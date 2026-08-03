"""The model backend, spoken through opencode.

ScriptEngine does not need a model to retrieve. This client exists for the two
index-time passes — `ingest/classify.py` and `ingest/abilities.py` — and for
nothing on the query path.

It used to POST to an OpenAI-compatible endpoint, which in practice meant a
local Ollama on `localhost:11434`. That path is gone: opencode is the backend
now, driven as a subprocess.

    opencode run --format json -m <provider/model> --dir <workdir> <message>

Two consequences of it being an *agent* rather than a completion endpoint, both
handled here rather than left to callers:

* **It runs somewhere.** An agent can read and write files in its working
  directory, and an index-time pass has no business touching the repository, so
  every call is pinned to a scratch directory with `--dir`.
* **It reports as a stream.** Output is newline-delimited JSON events, and the
  answer is the `text` parts among them:

      {"type":"step_start", ...}
      {"type":"text", "part":{"type":"text","text":"{\\"abilities\\": [...]}"}}
      {"type":"step_finish","part":{"reason":"stop","tokens":{...}}}

Rate limiting gets its own exception. A free-tier model over a few hundred
calls is exactly the case that throttles, and a batch that logs three hundred
failures and finishes "successfully" is worse than one that stops on the first
and says so.
"""

from __future__ import annotations

import json
import logging
import os
import re
import shutil
import subprocess
import tempfile

from scriptengine.config import Settings, get_settings

logger = logging.getLogger(__name__)

# What a throttled response looks like, matched generously because the exact
# wording belongs to whichever provider opencode routed to.
_RATE_LIMITED = (
    "rate limit",
    "rate_limit",
    "ratelimit",
    "429",
    "too many requests",
    "quota",
    "overloaded",
    "capacity",
)


class LLMUnavailable(RuntimeError):
    """No model answered. Callers should degrade, not crash."""


class LLMRateLimited(LLMUnavailable):
    """The provider throttled us.

    Separate from `LLMUnavailable` so a batch can stop on the first one and
    report it, rather than recording every remaining page as a failure and
    presenting the run as complete.
    """


class LLMClient:
    def __init__(self, settings: Settings | None = None, workdir: str = "") -> None:
        self.settings = settings or get_settings()
        # An agent will happily edit whatever is around it. Nothing here needs a
        # repository, so it is given an empty directory and cannot reach one.
        self.workdir = workdir or os.path.join(
            tempfile.gettempdir(), "scriptengine-opencode"
        )
        os.makedirs(self.workdir, exist_ok=True)

    @property
    def executable(self) -> str:
        return shutil.which("opencode") or ""

    def available(self) -> bool:
        """Whether opencode is installed. Never raises."""
        return bool(self.executable)

    def models(self) -> list[str]:
        if not self.available():
            return []
        try:
            done = subprocess.run(
                [self.executable, "models"],
                capture_output=True, text=True, timeout=60,
            )
            return [line.strip() for line in done.stdout.splitlines() if line.strip()]
        except Exception:
            return []

    def complete(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> str:
        """One turn, one answer.

        `temperature` and `max_tokens` are accepted and ignored: `opencode run`
        exposes neither. They stay in the signature so the two ingest passes and
        their tests are untouched by the change of backend.
        """
        if not self.available():
            raise LLMUnavailable(
                "opencode is not on PATH. Install it, or set SCRIPTENGINE_LLM_MODEL "
                "and provide another backend."
            )

        message = _flatten(f"{system}\n\n{prompt}" if system else prompt)
        command = [
            self.executable, "run",
            "--format", "json",
            "-m", self.settings.llm_model,
            "--dir", self.workdir,
            message,
        ]
        try:
            done = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=self.settings.llm_timeout_seconds,
            )
        except subprocess.TimeoutExpired as error:
            raise LLMUnavailable(
                f"opencode timed out after {self.settings.llm_timeout_seconds}s"
            ) from error
        except Exception as error:  # noqa: BLE001 - surfaced as one failure mode
            raise LLMUnavailable(f"Could not run opencode ({error})") from error

        # Throttling is only ever looked for in a *failure*. Scanning the whole
        # output caught the model's own words instead: an ability described as
        # "beyond human capacity" tripped the check and stopped a batch that
        # was working, on the first page, twice.
        failed = done.returncode != 0 or _error_event(done.stdout)
        if failed:
            trouble = f"{_error_event(done.stdout)}\n{done.stderr}"
            if _looks_throttled(trouble):
                raise LLMRateLimited(
                    f"{self.settings.llm_model} is rate limited. "
                    "Stopping so the run is not filled with failures."
                )
            raise LLMUnavailable(
                f"opencode exited {done.returncode}: "
                f"{(trouble.strip() or 'no detail')[:300]}"
            )

        answer = _text_of(done.stdout)
        if not answer:
            raise LLMUnavailable(f"No text in opencode output: {done.stdout[:300]}")
        return answer


def _flatten(message: str) -> str:
    """One line, because `opencode run` silently drops everything after the first.

    `run [message..]` is variadic and joins its arguments with spaces. A newline
    inside a single argument truncates the message there, and the model answers
    the fragment it was given — which is why the first extraction attempt
    returned "Provide the passage and I'll return the named abilities as JSON"
    for every page: it had received the instructions and none of the passage.

    Measured: a 4,000-character single-line argument arrives intact; the same
    text with newlines does not. Paragraph breaks become ` | ` so a sentence
    ending one paragraph does not run into the next.
    """
    text = (message or "").replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n\s*\n+", " | ", text)
    text = text.replace("\n", " ")
    return re.sub(r"[ \t]+", " ", text).strip()


def _error_event(stdout: str) -> str:
    """What opencode reported as an error, if anything.

    A run can exit 0 and still have failed — the failure arrives as an event in
    the stream like everything else.
    """
    trouble: list[str] = []
    for line in (stdout or "").splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        kind = str(event.get("type") or "")
        if "error" not in kind.lower():
            continue
        trouble.append(json.dumps(event.get("part") or event))
    return "\n".join(trouble)


def _looks_throttled(output: str) -> bool:
    """Whether a *failure* was a throttle.

    Only ever called on stderr and on error events. Called on the whole output
    it matches the assistant's own prose — "beyond human capacity" is an
    ability description, not a rate limit.
    """
    lowered = (output or "").lower()
    return any(marker in lowered for marker in _RATE_LIMITED)


def _text_of(stdout: str) -> str:
    """The assistant's words, out of the event stream.

    Every line is its own JSON object and only some carry text; a line that does
    not parse is a log line rather than a failure, so it is skipped instead of
    raising.
    """
    parts: list[str] = []
    for line in (stdout or "").splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") != "text":
            continue
        part = event.get("part") or {}
        text = part.get("text")
        if isinstance(text, str) and text.strip():
            parts.append(text)
    return "\n".join(parts).strip()
