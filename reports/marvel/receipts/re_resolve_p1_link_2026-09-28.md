# P1.3b receipt: link-aware re-resolve of the marvel store (2026-09-28)

`re_resolve_participants(series/marvel/facts.db)` -- the re-resolve from
`re_resolve_p1_2026-09-28.md`, now with the **link signal** (architect
2026-09-28): the wiki's own wikilinks, pre-resolved into per-page
`chunk_nodes` sets, break a same-reality ambiguity the reality signal
leaves. Exactly one linked candidate is the wiki's own answer; zero or
several linked members stay a counted ambiguity. Quotes kept, no
re-extraction; run once on the store repaired in place.

## Before / after

| measure | before | after |
|---|---:|---:|
| rows | 1221 | **1220** (one merge, see below) |
| on a disambiguation node | 0 | 0 |
| cross-reality | 618 | **635** (+17, all wiki-answered, see below) |
| filed explicitly ambiguous | 525 | **185** |
| participant ends moved | -- | 1234 |
| ends broken by the link signal alone | -- | 460 |
| ends no candidate set reaches (kept, counted) | -- | 11 |
| duplicates merged away | -- | 1 |

- **Ambiguous 525 -> 185**: 340 rows are the wiki's own answers -- the
  page's own links point at exactly one of the filed variants (e.g. a
  war page that listed `Wolverine (Earth-616) | Hellverine (Demon)
  (Earth-616)` links only the Hellverine). The 185 remaining are pages
  whose links break nothing (zero or several linked members, or no
  link): kept a counted ambiguity, names untouched, per P1.2 "never
  guess". The 340 match the read-only dry-run prediction exactly.
- **Cross-reality 618 -> 635**: the +17 are rows whose re-point landed
  on a variant of another reality than the page's. Every one of them is
  a link-rescued answer, not a guess: the page's own link names that
  variant (e.g. a page whose reality matches no variant of the codename
  falls to the base set, and the page's single link picks the
  cross-reality variant the wiki itself cited). 66 of the 635 rows'
  cross-reality ends are nodes the page links to; the rest stay the
  sole-variant class from the previous receipt (the wiki knows one
  variant, counted, never guessed).
- **Rows 1221 -> 1220, merged 1**: one event was filed twice on the same
  page -- once resolved and once ambiguous, the same wiki answer in two
  forms. The re-point lands the ambiguous row onto its duplicate and the
  pair merges (the store's own dedup rule: the wiki's answer, recorded
  once). The merge is its own counter, not silent.
- **unresolved_kept 11** unchanged: the same title-drift residue as the
  previous receipt, still owned by the alias-align / title-drift follow-up.

## Raw tallies

```json
{
  "before": {
    "rows": 1221,
    "on_disambiguation_node": 0,
    "cross_reality": 618,
    "ambiguous": 525
  },
  "after": {
    "rows": 1220,
    "on_disambiguation_node": 0,
    "cross_reality": 635,
    "ambiguous": 185,
    "moved": 1234,
    "ambiguous_new": 0,
    "unresolved_kept": 11,
    "link_broken": 460,
    "merged": 1
  }
}
```

## Notes

- Code: `pick_candidate` takes the page's linked set (exactly one linked
  candidate wins; the tie stays a counted ambiguity); the extraction
  path (`extract_from_sections` / `extract_events_series`) feeds the
  same per-page link set for new runs, so new extractions and the
  re-resolve agree. Committed before this store run
  (`6567f265`, `0c8f29f9`), per the process rule: commit, then the
  store mutates.
- The merge-on-collision behaviour (a re-point that would duplicate a
  stored row merges it away, counted) is pinned by
  `tests/test_events_link_resolution.py` (the Avengers case) and by the
  one merge above.
- `link_broken` (460) counts re-pointings the link signal achieved on
  top of the reality signal alone: the 340 rescued ambiguous rows plus
  the carried-node rows whose name pool the link broke. `ambiguous_new`
  is 0 -- the run files no *new* ambiguity it did not already have; it
  only repairs and counts.