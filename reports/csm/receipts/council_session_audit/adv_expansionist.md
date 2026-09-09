# Expansionist — CSM 100% campaign audit (2026-09-09 council)

**1. This is a corpus factory; CSM only pays the setup cost.** The census
tools take `--series`, JJK byte-identical; frozen sets generated fresh from
CSM (seeded, revid-stamped, on disk); the T0 pilot — 843 questions,
843/843 survival — runs through series-agnostic `page_gen.py`. Seven other
corpora are already crawled+indexed on disk (JJK, Bleach, OPM, Berserk,
Dragon Ball, One Piece, Hunterpedia), so their Phase-1
measurement shrinks to `overrides.yaml` + `census_doors --series X --regen` + a
dimension-map rerun. Left per corpus: Phase-2 GPU-hours — and D6
extraction only fires on a red census, so a green corpus skips it.
CSM is not corpus #2; it is the factory's amortization leg.

**2. R-5 is the campaign's biggest cross-corpus asset.** Verified
read-only against every `facts.db`: CSM's 11,261 edges are 96.7 %
cross-document; typed `relations` tables total 23,656 rows across the
eight corpora (JJK 821 → One Piece 14,527; CSM 748) over 1.05 M raw
`edges`. The router today has three modes; R-5's fourth, series-agnostic
`relations` mode (counseled) pays off in all eight — every future corpus
inherits it for free.

**3. Two ops assets nobody is counting.** (a) Transcript import:
`transcripts.db`'s 16,226 lines (verified) became 16,226 embedded points;
the Toji script shipped 21 verbatim `[E n mm:ss]` citations — the
strongest writer-facing differentiator (verbatim, timestamped grounding),
repeatable for any corpus with subtitles. (b) A/B bay + `csm-control.sh`
monitor (tmux-aware, logdir arg) + `ab-bay`/`terminal-pilot` skills: a
reusable supervision pattern — footprint invariants,
auto-kill of CPU work, the jsonl as judge.

**4. What CSM 100 % unlocks.** JJK's D6 is still open (P0–P5): CSM-8 will
be the *first* full D6 done-declaration, and its pilot memo becomes the
reusable acceptance template for everything after. A second,
different-genre corpus at D6 proves "nothing is hardcoded" — that is the
product claim; today it is a single data point.

*Verification: tools/census_*.py `--series` flags (grep), reports/csm/
census_*_csm.json + t0_pilot_csm.json (843 items) on disk,
series/<8>/facts.db read-only queries (relations: 821/748/359/617/651/5542/
14527/391; edges: 35,026/11,261/43,077/130,670/18,418/312,598/440,245/
62,066), series/jjk/transcripts.db line count = 16,226,
tools/master-work/csm-control.sh header (tmux/logdir),
~/.pi/agent/skills/{ab-bay,terminal-pilot}, router.py (no `relations`
mode yet), crosspage_census_csm.md (10,889/11,261 = 96.7 %).*