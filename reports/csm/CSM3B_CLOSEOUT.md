# CSM-3b close-out receipt (exit-code recheck raw + commit trail)

2026-09-08, Terminal B (fresh 100k session), worker 1 (Wave 1). Offline-only
run: no `:8000` contact, no in-process model loads, no full pytest (a sibling
worker owned the GPU cycle in parallel). Raw output below.

## Exit-code recheck (all offline, CPU, each <2 s)

- **(a)** `python -m scriptengine.cli chunk-containment --series csm` → **rc=0**
  - sections 2373 · sentences 17,382 · present in a chunk 17,382 · unreachable 0 · coverage 100.0000%
  - "11 sentences in link-list boilerplate excluded"
- **(b)** `python -m scriptengine.cli span-recall --series csm` (alias) → **rc=0**, identical counts (17,382/17,382, 0 unreachable)
- **(c)** `python -m scriptengine.cli chunk-containment --series jjk` → **rc=0** — JJK-unchanged check
  - sections 5,507 · sentences 48,572 · present in a chunk 48,572 · unreachable 0 · coverage 100.0000% (the re-baseline numbers)
- **(d)** tampered pin → **rc=1** (expected). Copied `reports/csm/panel_csm.json` to `/tmp/pin_tampered.json`, removed one row (17,181 → 17,180), kept the stored hash `e3d737205cd07245…`. `span-recall --series csm --panel /tmp/pin_tampered.json` printed:
  ```
  panel hash mismatch: the pin stamps e3d737205cd07245… but the rows load as
  aa37229f1af264ec… -- the panel was edited after stamping; re-pin before
  sweeping.
  ```
  The check fired in the `--panel` branch before `recall()` — no probe progress lines, no model load, no `:8000` contact (the tier-0 table is the command's offline pre-stage output).
- **(e)** bare-list load (Ruling 7, offline part): `json.load` of `reports/csm/panel_csm.json.heldout.json` = bare list, **200 rows**; `_panel_hash([list(r) for r in rows])` = **ec15e0d8772b8b54…** without exception. (The 4-probe LIVE version was delegated to worker 2 in the `:8000`-up window.)
- **(f)** `python -m pytest tests/test_span_recall.py -q` → **rc=0, 13 passed in 0.70 s** (model-free — the tests monkeypatch `_ask`; covers the roster-shaped HIT, door forwarding, and sanity logic)

## Coverage (standing rule: regenerate after every commit)

- after commit A: `python tools/coverage_report.py` rc=0 — jjk 893/987 pages (90.5%), 29,819 questions, in-scope content remainder 0, orphans 2; `COVERAGE.md` **unchanged** (no diff → nothing to commit)
- after the sync commit: rc=0, `COVERAGE.md` unchanged again

## Commit trail

- **A `bc73795`** — "csm: CSM-3b landed (Rulings 1/7) — roster door (served_text flattens members/passages; member names = returned docs; roster-shaped test), panel-hash recompute+enforce (exit 1) + bare-list held-out load + named consumer tools/csm/panel_heldout.py; COUNCIL_csm-3 record + floor census; stray 0956 receipts + 1200-s partial sidecar; suite 1,254" (CSM-area paths only; the master-work paths `plan/decisions.md`, `plan/state.md`, `reports/master-work/*`, `plan/AB_DEPLOYMENT.md` left untouched)
- **B `4d576d1`** — "csm: campaign-todos sync (CSM-3b done @ bc73795)"

## Deviations

None in checks a–f (all matched expectations). One task-text note: the git-add
line referenced `reports/2026-09-09-0956`; the actual receipts directory on
disk is `reports/2026-09-08-0956` — the correct one was committed.