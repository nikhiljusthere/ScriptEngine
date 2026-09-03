"""The MCP server: ScriptEngine's engine as tools an assistant can call.

    python -m scriptengine.mcp.server

Speaks the Model Context Protocol over stdio, so an agent host (opencode,
Claude Desktop, anything MCP-speaking) can register it and let the assistant
research a topic and verify a finished script through the same code the HTTP
API serves on :8000. There is no second implementation to drift: the tools
wrap `build_context`, `verify_script` and `script_destination` directly.

Three tools, sized for the script-writing workflow:

* `research`: the bundle for a topic, plus the rendered prompt with the house
  writing rules inside it. The assistant writes the script from that prompt.
* `verify_script`: check a script's chapter/episode tags against the raw
  crawl, the same gate `cli verify` runs.
* `script_path`: where a finished script should be saved, so the assistant
  does not invent a folder.

Deliberately no tool that writes files: the agent host has editors of its
own, and the engine's job is to serve research and judge tags, not to hold a
pen. `script_path` tells the assistant where to save; `verify_script` tells
it when it is done.
"""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from scriptengine.api.context import build_context, render_prompt
from scriptengine.config import get_settings, script_destination, series_paths
from scriptengine.eval.verify import verify_script as check_script
from scriptengine.script.writer import route_script

mcp = FastMCP("scriptengine")

# The same budget rule as the CLI: words times eight, clamped.
MIN_BUDGET = 6000
MAX_BUDGET = 60_000


def _budget_for(words: int) -> int:
    return max(MIN_BUDGET, min(words * 8, MAX_BUDGET))


@mcp.tool()
def research(
    subject: str,
    series: str = "jjk",
    mode: str = "auto",
    words: int = 6000,
    intro: bool = True,
    token_budget: int = 0,
) -> dict[str, Any]:
    """Research a script topic.

    Returns the ordered, cited context for `subject` (the same bundle
    `POST /context` serves) plus `prompt`, the bundle rendered as plain text
    with the house writing rules appended. Write the script from that prompt:
    it states the only chapter/episode numbers you may tag with.

    `mode` is auto (the engine reads the topic: "Every Rank of Curse" is a
    roster, anything else is a narrative), narrative, roster or qa. `words` is
    the target script length; the context budget is `words * 8` unless
    `token_budget` is given.
    """
    settings = get_settings()
    paths = series_paths(series, settings)
    if not paths.facts_db.exists():
        raise ValueError(
            f"Series {series!r} is not indexed. Run: "
            f"python -m scriptengine.cli index --series {series}"
        )

    asked = mode
    routed = None
    if mode == "auto":
        mode, routed = route_script(paths, subject, settings)

    budget = token_budget or _budget_for(words)
    bundle = build_context(
        paths, subject, mode=mode, token_budget=budget, top_k=12
    )
    if mode == "roster" and not bundle.get("members") and asked == "auto":
        bundle = build_context(
            paths, subject, mode="narrative", token_budget=budget, top_k=12
        )
    if routed is not None:
        bundle["routed"] = routed.as_dict()

    bundle["prompt"] = render_prompt(bundle, intro=intro, words=words, rules=True)
    return bundle


@mcp.tool()
def verify_script(text: str, series: str = "jjk") -> dict[str, Any]:
    """Check a finished script's chapter/episode tags against the wiki.

    Every tag is checked against the raw crawl, not the index: the page
    exists, a reference actually cites it, and a chapter paired with an
    episode agrees with the wiki's adaptation data. Returns
    `{"tags", "distinct", "findings", "passed"}`; `passed` is true only when
    every tag is real. Edit the script until `passed` is true.
    """
    paths = series_paths(series)
    return check_script(text, paths)


@mcp.tool()
def script_path(title: str) -> str:
    """Where a finished script should be saved.

    Finished scripts live in numbered video folders: `scripts output/Video N
    - <Title>/Script/<Title>.md`. Reuses the folder when one already carries
    this title, otherwise takes the next free number. Pass the script's title
    without the bold markers.
    """
    return str(script_destination(title))


if __name__ == "__main__":
    mcp.run()