"""The verbatim-evidence predicate, shared by the extraction passes and the
store's remap.

A stored row is evidence only while its quote survives this check against the
section it was read from. The extraction passes run it before a row is stored
(`events`, `relations`), and `FactStore.remap_derived` re-runs the same check
when it re-keys a row onto a rebuilt section, so a row can never be attributed
to text that no longer says it: a section whose content shifted under a
parser fix fails the check, and the row is dropped for re-extraction instead
of silently misattributed. One predicate on both sides: if a pass ever
relaxes the check, the remap relaxes with it, and the store can never validate
stricter or looser than the extractor did.

Lives in its own module rather than `events` because the store layer needs
it and `events` already imports the store: a shared home keeps the import
graph acyclic.
"""

import re
import unicodedata


def fold(text: str) -> str:
    """Lowercase and fold diacritics the way the passage's words would."""
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(c for c in normalized if not unicodedata.combining(c)).lower()


def quoted_in(quote: str, passage: str) -> bool:
    """Whether the passage really contains the clause, word for word.

    Whitespace is normalised and diacritics folded, because a reflowed line
    is still the clause. Nothing else is relaxed: this is the check that
    stops a quote the section never says being stored as its evidence. Under
    12 characters is not a clause: it is too short to anchor a row to a
    passage, so it fails even when present.
    """
    if len(quote.strip()) < 12:
        return False
    tidy = lambda s: re.sub(r"\s+", " ", fold(s)).strip()
    return tidy(quote) in tidy(passage)