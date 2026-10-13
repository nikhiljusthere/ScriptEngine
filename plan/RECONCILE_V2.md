# Reconcile overlapping big-v2 windows (started 2026-10-13)

Owner, verbatim: "Option 2, and share workload with terminal session, I want clean flawless data"
(option 2 = reconcile all conflicting overlap pairs by hand before composing the events+facts+tags set).

## Why
Windows that share >=2 sentences longer than 60 chars (the same passage cut at different offsets, or
repeated on several pages) must carry the same final rows for the shared part. Measured at the end of the
v2 pass (all 14,000 windows audited): 1,024 overlap pairs, **960 inconsistent** (events 491, facts 846,
tags 726; 1,768 windows). Cause: the two sides were reviewed far apart (628 pairs >50 windows apart)
under different rule generations, and the overlap check never ran during the v2 pass. The later side is
not reliably right (b153~b7384: the later side keeps fought next to defeated, A145).

## Split
`series/universal/training/big/recon/components.jsonl` (main checkout): the 960 pairs grouped into 838
connected components (a window in two conflicting pairs puts both pairs in one component; max 6 windows),
so no window is edited by both sessions. `owner` = `app` (the Claude-app session) or `term` (the
terminal session): 419 components / 884 windows each.

## Tools (`plan/review_tools/recon/`)
- `bash recon.sh view C` - the component's remaining diffs, then every window in it (full text, final
  rows, flags), exactly as `rv.sh view`.
- `bash recon.sh check C [C...]` - remaining diffs among all overlap pairs inside those components.
- `bash recon.sh check all` - the whole-corpus re-check (final gate).
- Edits go through the normal `bash plan/review_tools/rv.sh fix $PWD/FILE | grep -v ^FIXED` (gated,
  append-only, latest record wins). **Never run `mark`** during reconciliation (every window is already
  in the audit; a mark on a missing cursor sweeps from 0 - see the low2 incident in the catalog).

## Procedure per component
1. `recon.sh view C`.
2. Re-review EVERY window in the component in full under the current catalog (not only the shared
   sentences): the earlier side often predates A101/A125/A134/A145 etc.
3. Make the shared sentences carry identical rows on both sides: events (S, verb, O), facts
   (S, rel, O, modality, asserted_by), tags (kind + quote). Decide what is right; do not copy either side.
4. Only allowed difference: a person's name, when the window's OWN text supports a different single
   name (A4: one window gives the real name, the other only the codename). Record each such case as one
   line in `recon/exceptions.txt`: `C<c> b<a>~b<b> <name in a> / <name in b>: <reason>`.
5. Submit; `recon.sh check C` must report 0 inconsistent (apart from recorded exceptions); then append
   `C` to `recon/done_<owner>.txt`.
6. Catalog: new patterns go to `plan/BIG_REVIEW_PATTERNS.md` (measure before adding a rule, as always).

## Close
`recon.sh check all` -> 0 inconsistent outside `exceptions.txt`; then the terminal session commits
(data snapshot + this file + tools), and the compose step for events+facts+tags starts.
