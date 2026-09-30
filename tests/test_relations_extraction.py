"""The relationship extraction loop reads the index's sentence grid.

Windowing-100 council (2026-09-30): a passage is a whole-sentence grid
window, never a character slice. The loop's quote check runs against the
window's own text, so a quote the window states can be attributed to the
sentences that actually cover it.
"""

from __future__ import annotations

import json

from scriptengine.ingest import relations as R


class Probe:
    """Records every prompt; answers with one relation, quoted from the
    passage it was shown."""

    def __init__(self) -> None:
        self.prompts: list[str] = []

    def available(self) -> bool:
        return True

    def complete(self, prompt: str, system: str = "", temperature: float = 0.0,
                 max_tokens: int = 0, **_kwargs: object) -> str:
        self.prompts.append(prompt)
        passage = prompt.split("Passage:\n", 1)[1].split("\n\nAnswer", 1)[0]
        quote = passage[:40]  # first whole sentence of the window
        return json.dumps({
            "relations": [
                {"other": "Geto", "relation": "enemy", "era": "", "quote": quote}
            ]
        })


def _text() -> str:
    # Ten paragraphs, ~6,300 chars: the old 4,000-char slice read it in two
    # cuts; the grid reads one window per sub-topic.
    paragraphs = [
        f"Gojo and Geto met in year {i} of the school and sparred in the "
        f"training yard every morning for the rest of the term."
        for i in range(1, 11)
    ]
    return "\n\n".join(paragraphs)


def test_a_long_section_is_read_as_grid_windows() -> None:
    from scriptengine.ingest.windows import CURRENT_GEN, build_windows

    section, text = "History", _text()
    probe = Probe()
    found = R.extract_from_passages(
        probe, "jjk", "Gojo", [(section, text)], {}, {"geto": "Suguru Geto"}
    )
    expected = build_windows("Gojo", section, text, gen=CURRENT_GEN)
    assert len(probe.prompts) == len(expected)
    for prompt, window in zip(probe.prompts, expected):
        assert window.text in prompt
    # The quote was copied from the window read, so the window-level
    # check keeps the row.
    assert [entry["other"] for entry in found] == ["Suguru Geto"]


def test_a_quote_outside_every_window_is_dropped() -> None:
    """The window-level G1 at the caller: a quote no window carries is not
    attributed to sentences that do not cover it."""
    section, text = "History", _text()

    class OutsideProbe(Probe):
        def complete(self, prompt, system="", temperature=0.0,
                     max_tokens=0, **_kwargs):
            self.prompts.append(prompt)
            return json.dumps({
                "relations": [
                    {"other": "Geto", "relation": "enemy", "era": "",
                     "quote": "a sentence the wiki never wrote"}
                ]
            })

    probe = OutsideProbe()
    found = R.extract_from_passages(
        probe, "jjk", "Gojo", [(section, text)], {}, {"geto": "Suguru Geto"}
    )
    assert found == []