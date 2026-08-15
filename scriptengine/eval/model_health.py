"""Is the extraction model configured the way the run needs it?

Two failures this session were silent and cost hours, and both look identical
from the outside -- an idle GPU and a run producing nothing:

* **The model reverts when idle.** LM Studio reloads it with default settings,
  which means 262,144 context and thinking back on. A call that takes 3s
  configured takes 90s that way, and a long run simply stops progressing.
* **The API server holds the GPU.** Its embedder and a 27B do not fit on one
  32GB card together, and the endpoint answers 500 to everything.

So a run probes before it starts rather than discovering it in a log. Cheap:
one short completion.
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
        answer = client.complete(
            "Reply with the single word OK.", system="", temperature=0.0,
            max_tokens=16,
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
            "reload it with the `No thinking 27b` preset."
        )
    return True, f"{elapsed:.1f}s"


def main() -> int:
    healthy, why = probe()
    print(f"{'ok' if healthy else 'UNHEALTHY'}: {why}")
    return 0 if healthy else 1


if __name__ == "__main__":
    raise SystemExit(main())
