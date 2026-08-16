"""Is the extraction model configured the way the run needs it?

Two failures this session were silent and cost hours, and both look identical
from the outside -- an idle GPU and a run producing nothing:

* **The model reverts when idle.** LM Studio reloads it with default settings,
  which means 262,144 context and thinking back on. A call that takes 3s
  configured takes 90s that way, and a long run simply stops progressing.
* **The API server holds the GPU.** Its embedder and a 27B do not fit on one
  32GB card together, and the endpoint answers 500 to everything.

A third was found on 2026-08-16, and it defeats a check on latency alone:

* **Thinking comes back on its own.** `lms load` has no preset flag, so every
  CLI reload restores it unless a per-model default config says otherwise. The
  model then answers correctly and in about 3.8s, passing every timing
  threshold, while spending 82 of 90 completion tokens on reasoning. It is
  visible only in `usage.completion_tokens_details.reasoning_tokens`.

So a run probes before it starts rather than discovering it in a log. Cheap:
one short completion, checked on time *and* on usage.
"""

from __future__ import annotations

import sys
import time

# Healthy is about 3s for a real extraction window. A trivial prompt is faster
# still, so anything past this means the context or the thinking setting came
# back -- not that the machine is busy.
SLOW_SECONDS = 30.0


def probe(timeout: float = 120.0) -> tuple[bool, str]:
    """`(healthy, why)` for the configured endpoint. Never raises."""
    from scriptengine.config import get_settings
    from scriptengine.llm.client import LLMClient

    settings = get_settings()
    client = LLMClient(settings)
    started = time.monotonic()
    try:
        answer, usage = client.complete_with_usage(
            "Reply with the single word OK.", system="", temperature=0.0,
            max_tokens=256,
        )
    except Exception as error:  # noqa: BLE001 - the reason is the whole point
        return False, f"{type(error).__name__}: {str(error)[:160]}"
    elapsed = time.monotonic() - started
    if not answer.strip():
        return False, f"empty answer after {elapsed:.1f}s"
    if elapsed > SLOW_SECONDS:
        return False, (
            f"{elapsed:.1f}s for a one-word answer, healthy is ~3s. The model has "
            "most likely reverted to its default context with thinking on -- "
            "reload it and re-probe."
        )

    # Latency alone does not catch this. A model reloaded with thinking on
    # answers a trivial prompt in about 3.8s -- inside every threshold above --
    # while spending 82 of 90 completion tokens on reasoning it was never asked
    # for. On 2026-08-16 this probe reported `ok: 3.8s` with thinking fully on,
    # and a long run went out under it. The usage is the only evidence.
    reasoning = (usage.get("completion_tokens_details") or {}).get(
        "reasoning_tokens"
    )
    if reasoning:
        return False, (
            f"{elapsed:.1f}s but {reasoning} reasoning tokens -- thinking is on. "
            "`lms load` has no preset flag, so it comes back on every CLI reload "
            "unless the per-model default config sets enableThinking false. See "
            "EXTRACTION_RUNBOOK.md."
        )
    return True, f"{elapsed:.1f}s, no thinking"


def main() -> int:
    healthy, why = probe()
    print(f"{'ok' if healthy else 'UNHEALTHY'}: {why}")
    return 0 if healthy else 1


if __name__ == "__main__":
    raise SystemExit(main())
