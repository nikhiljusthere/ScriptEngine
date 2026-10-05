"""Wiki evidence for one event row, read from the series store (the same card
tools/train/verify_row_wiki.py gives the Q6 verifier). For annotators working
outside the engine (opencode models), so every row is checked against the wiki's
own data: which page each end is, its page type, infobox status and race, and
battle pages whose sides name both ends, with the outcome.

    scriptengine/.venv/bin/python tools/train/wiki_card.py "Subject" "verb" "Object"
    scriptengine/.venv/bin/python tools/train/wiki_card.py "Yuji" awakened ""
    scriptengine/.venv/bin/python tools/train/wiki_card.py --series opm "Saitama" defeated "Boros"
(--series defaults to jjk; the universal pools pass their own wiki.)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_row_wiki import ROOT, Wiki  # noqa: E402


def main():
    args = sys.argv[1:]
    series = "jjk"
    if len(args) >= 2 and args[0] == "--series":
        series, args = args[1], args[2:]
    if len(args) != 3:
        print(__doc__)
        return 2
    s, v, o = args[0], args[1], args[2] or None
    card, flags = Wiki(ROOT / "series" / series / "facts.db").card({"subject": s, "verb": v, "object": o})
    print(card)
    print("WIKI FLAGS: " + ("; ".join(flags) if flags else "none"))
    print("(a species page is a class, never an end; a technique page can be a named shikigami,"
          " which IS allowed, but an attack, technique or domain is not)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
