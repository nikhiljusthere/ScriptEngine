"""The MCP server: ScriptEngine's engine as tools an assistant can call.

    python -m scriptengine.mcp.server

Speaks the Model Context Protocol over stdio, so an agent host (pi, opencode,
Claude Desktop, anything MCP-speaking) can register it and let the assistant
research a topic and verify a finished script through the same code the HTTP
API serves on :8000. There is no second implementation to drift: `research`
delegates to that running service, and the other two tools wrap
`verify_script` and `script_destination` directly.

`research` goes over HTTP rather than calling `build_context` in this process
because the embedder and reranker must live in exactly one place: loading
them here cost 30-60 s on the first call and took VRAM the extraction model
needs (the one-copy rule). So this module never imports the retrieval stack —
the service it talks to owns the models, and a session that only calls
`script_path` or `verify_script` pays nothing.

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

import httpx
from fastmcp import FastMCP

from scriptengine.config import get_settings, script_destination, series_paths
from scriptengine.eval.verify import verify_script as check_script

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

    Needs the API up: `python -m scriptengine.api.main`.
    """
    settings = get_settings()
    url = f"http://{settings.api_host}:{settings.api_port}/context"
    payload = {
        "series": series,
        "query": subject,
        "mode": mode,
        "token_budget": token_budget or _budget_for(words),
        "top_k": 12,
        "as_prompt": True,
        "words": words,
        "intro": intro,
        "rules": True,
    }
    try:
        # Generous: a service that has not answered since it started loads the
        # embedder and reranker on this first call.
        response = httpx.post(url, json=payload, timeout=180.0)
    except httpx.ConnectError as error:
        raise ValueError(
            f"The ScriptEngine API is not answering on {url}. Start it with: "
            "python -m scriptengine.api.main"
        ) from error

    if response.status_code != 200:
        raise ValueError(f"POST /context returned {response.status_code}: {response.text}")
    return response.json()


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