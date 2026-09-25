# SWITCHPOINT — the resume file for Qwen mode switches

pi's model is the Qwen server: while the server is reloading the agent has no
model, and after reopening pi the *transcript* may be discarded (small
contexts compact fast). So everything needed to continue must live here, on
disk, **before** `qwen-switch.sh` runs. Fill the hand-written section before
every switch; `qwen-switch.sh` appends machine lines to the switch log — never
edit those.

## Current position (hand-written — fill BEFORE every switch)
- **2026-09-25 (opencode session `ses_f2b28e47dffefAHhFTSIFM4XKj` — Marvel 100% campaign; owner stopped the work, declared the VPN fixed, and ordered the stall→switch policy; THIS ENTRY IS THE NEW-SESSION PROMPT — paste it into the fresh session, it is self-contained):**
  - **Campaign:** Marvel 100% per `plan/MARVEL_100_PLAN.md` (source of truth — read it first: standing rules, §1a bot-wall ladder + the new throttle→egress-IP-rotation policy, phases A–D, GPU discipline §6). JJK + CSM are baselines, never touched; the four standing gates (pytest / eval jjk / span-recall jjk / canon opm) stay green at every change; no user input at runtime — councils instead, records in `reports/marvel/COUNCIL_*.md`; receipts on disk ("a claim that is not on disk did not happen"); commits by named paths.
  - **Position:** A0 DONE (type_aliases verified for `series/marvel/` + `series/mcu/`, receipts in `reports/marvel/exploration_2026-09-25.md`); A1 NOT run — 0 pages on disk for both wikis (the MCU crawl was killed, the Marvel crawl never completed; all resumable from disk, so a fresh run is the restart).
  - **Landed + committed this session:** (1) crawler stall watchdog — zero completed pages for `crawl_stall_seconds` (300 s, `SCRIPTENGINE_CRAWL_STALL_SECONDS`) while titles are still outstanding → `CrawlStalled` → CLI exit **42** + `stalled`/`stall_remaining` marker rows in the manifest; per-page fetch timeout = `crawl_timeout_seconds` (30 s, `SCRIPTENGINE_CRAWL_TIMEOUT_SECONDS`); (2) plan §1a throttle policy (owner 2026-09-25): when a connection throttles, change the NordVPN server/country for a fresh egress IP before escalating — never blind-retry the same IP; (3) 2 new tests in `tests/test_crawler_stall.py` (passing; full-suite + the other three gates are GATE A items — known delta: pytest pin 1,331 + 2 = 1,333 expected, no mid-campaign gate re-run per the known-delta rule).
  - **VPN state (owner verdict: fixed 2026-09-25):** the ISP blackholes public TCP/53+UDP/53 and outbound UDP/443 (QUIC), so all resolver traffic rides the local DoH-backed DNS stack — `nordvpn-dnsfwd` (127.0.0.1:5353 + 127.0.0.55:53), `nordvpn-dnsfix` (DNAT/REJECT iptables), `nordvpn-conntrack-flush.timer` (60 s), static `/etc/resolv.conf` → `127.0.0.55`. All four must stay enabled or `nordvpn` 15-seconds again. Account OAuth may still be pending (`nordvpn login` → browser / `--callback`); if it reports "You're not logged in", record it and keep going — the crawl runs on the direct ISP egress until rotation is needed.
  - **FIRST ACTION ON RESUME (in order):** (1) read `plan/MARVEL_100_PLAN.md`; (2) verify the egress stack: `systemctl is-enabled nordvpn-dnsfwd nordvpn-dnsfix nordvpn-conntrack-flush.timer`, `nordvpn status`, and record the direct-egress baseline `curl -s -m 5 https://api.ipify.org`; (3) start the Marvel production crawl detached: `setsid nohup scriptengine/.venv/bin/python -m scriptengine.cli crawl --series marvel --start-url "https://marvel.fandom.com/wiki/Marvel_Database" > reports/marvel/receipts/crawl_marvel.log 2>&1 < /dev/null &` (~2.2–2.5 h; 10 workers default — do NOT raise them, 20 was measured slower); (4) start MCU too (separate host, separate 429 pool; ~30–60 min, may run in parallel — watch both logs): same shape, `--series mcu --start-url "https://marvelcinematicuniverse.fandom.com/wiki/Marvel_Cinematic_Universe_Wiki"`, log `reports/marvel/receipts/crawl_mcu.log`.
  - **Throttle protocol while the crawl runs (the new policy, plan §1a):** on CLI exit **42** (`CrawlStalled`) or a sustained 429 pause-loop → `nordvpn connect --country <a different country/server>` (fresh egress IP) → verify `curl -s https://api.ipify.org` changed → re-run the same command (it resumes from disk). Keep rotating servers while throttling persists.
  - **During/after the crawl (plan §2):** A1c parser fixes — F1 (colon-fold template-name normalisation in `find_infobox`/`infobox_candidates`) + F2 (unclosed-lead infobox branch in `split_sections`), site `scriptengine/ingest/wikitext.py` (L7/L8 of the detail-loss register); the branch fires only on the unclosed shape so JJK/CSM are pinned by the existing suite; four standing gates green before that commit. Then A1b (`skip_patterns:` + `alias_fact_keys:` hook + disambiguation gap-fill), A2 (marvel.com sub-store), and GATE A council checkpoint → Phase B (CC corpus; speaker names visible per line is a hard owner requirement; `SPEAKER n` no-guess fallback).
  - **Open owner decisions (raise at the next wall, never at runtime):** D-1 (Disney+ account for live-action CC/audio), D-2 (scope boundary: Fox-era X-Men / MIB / 3rd-party licensed). B2 prereqs not installed (ffmpeg, faster-whisper, pyannote; ~35 GB free → streaming audio, drop audio after processing); OpenSubtitles v3 needs a free API key; agent-reach: youtube ok (yt-dlp), OpenCLI extension not connected (D-5 owner setup). GPU: Qwen resident (262k per the 09-25T00:33 switch line) — any ASR/diarization/27B batch needs a dial-down window (ab-bay); no CPU job >15 min in-campaign.
  - **Git:** campaign plan + this checkpoint + the stall work are committed by named paths in this session; `reports/marvel/` (receipts) stays untracked; the owner's CSM-window files (`tools/csm/d7_gates.sh`, `tools/master-work/switch_restart3_oc.sh`) remain uncommitted per the 09-24 note.
  - **RESUMED 2026-09-25 ~03:5x (new opencode session `ses_f2a7d1dedffeGfA0C5UDhWbNiL`; this sub-block supersedes the "Position" line above where they differ):**
    - **Egress verified + deviation recorded:** baseline direct-egress IP `103.124.15.71`; `nordvpn status` = Disconnected (logged in, not connected, responsive — no 15-second stall). DEVIATION from this entry's VPN-state line: the three `nordvpn-dns*` units are **not-found** (5353 is avahi-daemon; `resolv.conf` = systemd-resolved stub → ISP 192.168.1.1; `nordvpnd` active) — the owner's post-plan fix does not use that unit set; DNS + egress function. Receipt: `reports/marvel/receipts/egress_verification_2026-09-25.md` + plan §1a addendum.
    - **Both crawls launched detached 03:53** (10 workers, per the do-not-raise rule): Marvel pid 9982 → `reports/marvel/receipts/crawl_marvel.log` (~2.2–2.5 h); MCU pid 10039 → `crawl_mcu.log` (14 page types discovered; ~30–60 min). Throttle protocol: exit 42 / sustained 429 loop → `nordvpn connect` to a different country/server → verify IP ≠ `103.124.15.71` → re-run the same command (disk resume). Watch both logs; the MCU finishes first.
    - **Position change:** the working tree ALREADY carries A1c (wikitext F1 `fold_template_colons` in `find_infobox`/`infobox_candidates` + F2 `_unclosed_lead_prose` in `split_sections`; 9 new tests in `tests/test_wikitext.py`) and A1b (`alias_fact_keys:`/`skip_patterns:` hooks in `ontology.py` + `crawler.py`; 5 new tests in `tests/test_ontology.py`; `series/marvel/overrides.yaml` already declares both keys) — landed in the previous session, **uncommitted and ungated**. **Sequence (revised this session — one commit, not two):** the "A1c-only" gate run was RED, because `tests/test_crawler_aliases.py` (3 tests) is untracked and survived the pathspec stash on disk, so an A1c-only pytest could never have been green; a true A1c-only would have been green (base `1adb0d42` = 1,333). Therefore: 4 standing gates on the **union tree (A1c+A1b)** → ONE gate-covered commit by named paths (the L2/L7 package: `scriptengine/ingest/{wikitext,ontology,crawler}.py`, the 3 test files, `series/marvel/overrides.yaml` + `series/mcu/overrides.yaml` (A0 scaffolding joins — its `alias_fact_keys`/`skip_patterns` declarations are A1b), CLAUDE.md pin) → docs commit (`plan/MARVEL_100_PLAN.md` + `plan/SWITCHPOINT.md`, never the two owner CSM-window files) → cadence council (`reports/marvel/COUNCIL_a1c_a1b_landed.md`) → A2 (marvel.com sub-store: inspect the previous session's untracked `tools/marvel/export_fetch.py` + `reconcile.py` first) → the disambiguation gap-fill rides the next crawl re-run (disk-driven) → GATE A council.
    - **Pytest pin:** committed base 1,331 (CLAUDE.md) + 2 stall tests (`1adb0d42`, known delta, un-stamped) = 1,333; union tree = 1,333 + 9 (A1c `test_wikitext`) + 5 (A1b `test_ontology`) + 3 (`test_crawler_aliases`) = **1,350** (expect 1,347 passed + 2 xpassed, with the 3 documented `:8000`-down `test_mcp_server.py` env failures — council #25 class, record-don't-chase). Stamp CLAUDE.md at the union commit with the measured number + the `:8000`-down caveat.
    - **GPU (owner directive 2026-09-25, recorded in plan §6):** Qwen 153600 dial (switch line 2026-09-25T03:50:38, 5,464 MiB free) — the ~5 GB is the campaign's working VRAM; ALL model-bearing tasks run GPU-only; the one exception is JEV systemone when it processes faster than the GPU (never CPU).
    - **Open owner decisions (unchanged; raise at the next wall):** D-1 Disney+ account, D-2 scope boundary (Fox-era X-Men / MIB / 3rd-party licensed).
    - **EGRESS ROTATIONS #1 + #2 (this session, ~04:0x–04:2x, per plan §1a throttle protocol):** both crawls throttled on the baseline ISP IP `103.124.15.71` — Marvel run 1 (pid 9982) hit the stall watchdog (`CrawlStalled`, CLI exit 42) after enumerating 42,692 of ~279k titles with zero completions in the stall window; MCU run 1 (pid 10039, 10,968 titles outstanding, ~37k fetched) CrawlStalled at 04:05:44. Response per protocol: `nordvpn connect us` → **us13908.nordvpn.com**, egress verified `187.14.224.72` (≠ baseline), both crawl commands re-run (disk resume; logs rewritten per run; Marvel setsid wrapper 17630, MCU 17966). **Rotation #2 (~04:23):** the US exit IP throttled on the MCU host within minutes (124 `rate limited` hits; marvel.fandom.com stayed clean on the same egress — the 429 pools are per-host, as the plan expects), the MCU run 2 CrawlStalled at 04:23 before the switch could take effect → `nordvpn connect de` → **de1507.nordvpn.com**, egress verified `187.40.55.180`, MCU re-run (setsid wrapper 27977; fresh log: 0 429s at ~04:25, re-enumerating). Marvel keeps its run-2 process through rotation #2 (disk-resume-safe; its log shows 0 429s on the de egress). 10 workers kept (do-not-raise rule). If a 429 pause-loop or exit-42 recurs, rotate to a DIFFERENT country/server again — never blind-retry the same IP; receipt trail stays in the two crawl logs.
    - **EGRESS ROTATION #3 (this session ~04:36, per plan §1a + council hardening #6):** MCU run 2 on the DE egress (`187.40.55.180`) hit a sustained 429 pause-loop on the MCU host (04:31–04:36) → `CrawlStalled` at 04:35:47 (zero completions in 300 s, 4,867 titles outstanding, 35,209/48,026 on disk) → `nordvpn connect nl` → **nl1260.nordvpn.com** (third country — us/de already used), egress verified `186.247.163.23`, DE stall log archived to `reports/marvel/receipts/crawl_mcu_run2_de_stalled.log` BEFORE the per-run log rewrite, MCU re-run from disk (setsid wrapper 37211; 0 429s on the fresh log 3+ min). The Marvel run-2 process (pid 17631 — healthy on DE, 0 429s, still enumerating ~182k/279k at 04:40) rides the NL egress into its fetch phase: the council-flagged per-host-pool risk (rotating both crawls can trade a clean IP for a dirty one) is LIVE — the Marvel log is the monitor; a Marvel-side 429 loop on NL triggers rotation #4 (OWNER WALL per council hardening #6: rotation #4+ needs owner budget sign-off — three consumed: us, de, nl).
    - **FOUR STANDING GATES GREEN on the union tree (~04:1x–04:4x, receipts `reports/marvel/receipts/gates_2026-09-25_union/`):** pytest **1,345 passed + 2 xpassed + 3 failed** (1,350 total = 1,333 base + 17 A1c/A1b tests; the 3 failures are exactly the documented `:8000`-down `test_mcp_server.py` env trio — record, don't chase); `eval --series jjk` **31/31**; `span-recall --series jjk` **48,572/48,572 rc=0** + live probe **398/400 (99.5%)** — the probe needed `:8000`, started on CUDA as a short bounded co-location (skill device rule; 5,462 MiB free, Qwen quiet window: crawls are network+disk only), health-checked, then STOPPED (steady state restored: port free, 5,462 MiB free); `canon-run --series opm` **10/16 exact · 236/236 · 79.0%** (also behind a bounded `:8000` window, same procedure). All four match/beat baseline.
    - **COMMITTED `6a1f6ceb` (named paths only, 9 files):** `scriptengine/ingest/{wikitext,ontology,crawler}.py` + `tests/{test_wikitext,test_ontology,test_crawler_aliases}.py` + `series/{marvel,mcu}/overrides.yaml` (the `.gitignore` `!series/*/overrides.yaml` rule makes those the only tracked series files — the 35k MCU wikitext snapshots + manifest stay untracked campaign artifacts) + `CLAUDE.md` (pin stamped 1,331 → **1,350** with the `:8000`-down caveat). The owner's `tools/csm/d7_gates.sh` + `tools/master-work/switch_restart3_oc.sh` remain `M`, uncommitted.
    - **Docs commit (this session, after the code commit):** `plan/MARVEL_100_PLAN.md` + `plan/SWITCHPOINT.md` (the plan's §1a rotation records + §6 GPU directive + this checkpoint). Machine lines the switcher appends to the switch log stay OUT of the docs commit.
    - **COUNCIL (cadence, this session ~04:4x — `reports/marvel/COUNCIL_a1c_a1b_landed.md`):** `llm-council` 5 advisors (Contrarian / First-Principles / Expansionist / Outsider / Executor) + 5 peer reviews (anonymized A–E; run SEQUENTIALLY per owner constraint "1 subagent at a time") + chairman synthesis (de-anonymized). **Verdict: (Q1) one-commit SOUND — misframed question (the missing thing is the Marvel gate, not bisection); (Q2) gap-fill ride-along = PHANTOM dependency (the disambiguation skip fires at index time in `load_extracted`, not crawl time — don't stall Phase C on it); (Q3) egress rotation is a bet, not a fix (per-(host,IP)-vs-global budget undecidable from current evidence; shared VPN exits are dirty; rotating both crawls can trade a clean IP for a dirty one); (Q4) A2 = **NO-GO** (zero Marvel extraction signal; marvel.com ToS unchecked — owner item), GATE A = **CONDITIONAL-GO** (convene only after gate list 1–6 pass; the checkpoint must bless the Marvel validation, not just the four JJK/CSM gates).** Gate list: **1 cheap (DONE this session)** resume-skip proof (run-2 log: `resuming: 35209 of 48026 already on disk / crawling 12817` — exact, no re-fetch; on-disk count unchanged across the run 2→3 restart) + egress hygiene (exit IP logged for rotations #1–#3); **2 cheap (DONE)** snapshot completeness → `reports/marvel/receipts/snapshot_completeness_2026-09-25.md` (MCU **35,209/48,026** on disk, 12,817 outstanding, run 3 on NL; Marvel **0/~279k** — fetch phase not started, the "~330k stored" was a projection, not a count; truncation spot-check folded into gate 4); **3 cheap (DONE)** base `1adb0d42` patch export → `reports/marvel/base_1adb0d42/` (`wikitext/ontology/crawler.py` — both `overrides.yaml` ABSENT at base = pure campaign additions; one-command attribution) + the 3 `:8000` env failures codified in the gate definition (`scriptengine-gates` skill pytest line + plan §D1: GREEN = exactly 1,345 passed + 2 xpassed + 3 failed, the 3 = the documented `:8000`-down `tests/test_mcp_server.py` trio, never deselected; any other failure = RED); **4 medium** Marvel baseline diff: run the **base** parser on ~200 pages FIRST to create the baseline (the corpus was never extracted — the diff as originally stated was vacuous; MCU 35.2k set now, Marvel set post-fetch), then new parser + hooks; **stop condition: fact-count delta >10% on sample or any systematic content rewrite → A2 stays blocked**; **5 medium** hand-validate 20–50 character pages (`currentalias` resolves, colon-template infoboxes parse) + 10 disambiguation pages (zero facts), recall tolerance ≥99.5% (398/400 baseline); **6 medium** full `load_extracted` dry-run with error isolation (quarantine bad pages, don't crash the index) + per-series fact-count diff; **7 defer** per-(host,IP)-vs-global 429 probe + client-side throttling as primary control; **8 defer** parser-version stamp in stored JSON + re-parse idempotency/rollback. **NEW owner-wall items (raise at the next wall, never at runtime):** (a) marvel.com ToS/robots compliance (A2 precondition); (b) disambiguation zero-facts policy — disambiguation lists are a writer-research signal, is "no facts" right for a script-research corpus? (corpus-design call); (c) rotation #4+ budget (three consumed: us, de, nl); (d) formal exclusion of the 3 env failures from the gate definition (codified this session; ratify at the wall).
    - **MEDIUM GATES 4–6 GREEN ON THE FINAL MCU CORPUS (~04:4x–05:0x, receipts `reports/marvel/receipts/gates_4_6_mcu_2026-09-25.md` + `parse_diff_mcu_report.md` + `gate5_mcu_sheet.md` + the two extract JSONLs):** MCU crawl run 3 **completed 04:45:59** (`crawl complete: 0 written, 12817 skipped, 0 failed`, stalled=False — the 12,817 outstanding were all default-policy category skips (Galleries/stubs/no-image/Disambiguations); **35,209 is the final MCU set**). Gate 4 (base-vs-new parser diff, `tools/marvel/parse_diff.py` over the official `load_extracted` path; BASE = worktree `/tmp/se_base_1adb0d42` via PYTHONPATH + manifest ontology, no overrides — faithful to 1adb0d42; NEW = HEAD + current overrides): **stable fact-count delta +0.00%, 0/35,209 pages with any fact-count or key change** → PROCEED (the A2 stop condition is NOT triggered); the single difference is type-id renames `tv*`→`tv_series*` (225 pages, 0.6%, label-level only — downstream note for GATE A). Gate 5: 40/40 sampled character pages typed `character` with faithful values (spot-graded from the sheet), the 1 stored disambiguation page (`TVA (disambiguation)`) = type unknown + **0 facts → PASS**; the 10-page disambiguation sample is owed to the Marvel set post-fetch; cosmetic note: inline `<ref>` content can survive into fact values (value-cleaning gap, logged, not a gate failure). Gate 6: full `load_extracted` dry-run, 35,209 pages, **both trees 0 exceptions / 0 quarantined** (~96 s each, 365 pages/s); review-5 truncation characterization (synthetic 60% and 15% cuts, stored corpus untouched): **never garbage facts** — worst case is the unclosed template's raw parameter text in `lead` (the F2 branch, cosmetic) plus reduced/zero facts (severed infobox). Marvel fetch in progress on NL (1,889/279,111 at 04:58, ~1,200/min → ETA ~09:00; **zero real 429s** in its log; egress still `186.247.163.23`). A2 tooling inspected (previous session's, untracked, read-only per plan): `tools/marvel/export_fetch.py` (source B = per-title `Special:Export/<title>`, resumable enumeration + 429-aware workers, writes `series/<s>/export/` + RECEIPT.json) + `tools/marvel/reconcile.py` (S0 sourcing receipt: page-for-page witnessed/drift/conflict, `sourcing_100` verdict) — both sound; **sequencing constraint for GATE A: source B doubles egress on the same host → serialize it AFTER the source-A fetch, or run at very low worker count.**
    - **MARVEL 429-LOOP + HARDENING RESOLUTION (~06:25–06:40, no rotation, owner wall NOT triggered):** the NL egress started 429-looping at ~06:25 (46 rate-limit lines by 06:28; progress degraded 2,400/min → ~12/min; 46→96 lines 06:28→06:31). Per council hardening (client-side throttling primary, rotation last resort): archived the log to `reports/marvel/receipts/crawl_marvel_nl_429loop_2026-09-25.log` (106 rate-limit lines), killed the crawl, 8-minute cooldown, restarted with `SCRIPTENGINE_CRAWL_CONCURRENCY=3` (the `crawl` CLI has no `--workers`; pydantic env override of `Settings.crawl_concurrency`, default 10) at 06:39:37 — **worked**: only 2 rate-limit lines (startup residuals), clean enumeration by 06:44 (20k/279k in ~1 min), fetch phase resumes from disk (213,718 on disk, 65,400 outstanding, ETA ~08:20–08:40 at ~600–700/min). This is a hardening event, NOT rotation #4 — rotation #4+ (a new country ≠ us/de/nl) remains owner-gated and was NOT consumed.
    - **MARVEL C3 FETCH STALL + KILL (07:24–07:35, no rotation):** the concurrency-3 run re-enumerated cleanly (06:44–07:24, zero new 429s on the `allpages` path) and resumed the fetch 07:24:24 (`resuming: 213721 of 279112; crawling 65391`), but the fetch endpoint (`prop=revisions` batches) was still hard-throttled → 429 loop from 07:26, 0 completions, CrawlStalled logged 07:29:24. **Ops correction (recorded):** under a hard lockout the process does NOT exit cleanly — in-flight batches keep retrying inside `_get` (each 429 extends the shared throttle window), so workers never reach the top-of-loop `stalled` check, `gather` never completes, the stalled manifest is never written, and the retry traffic *keeps the IP penalty window alive*. Operator killed pid 91969 at 07:35 (SIGTERM); the kill also stops the penalty-feeding traffic. Stall evidence: `reports/marvel/receipts/crawl_marvel_c3_stalled_2026-09-25.log` (archived — CrawlStalled line + full 429 timeline); `series/marvel/manifest.json` absent (killed before the end-of-run write; the manifest is only written at run end). Next step per the protocol ladder (same-egress hardening before rotation): **45-minute cooldown → restart at `SCRIPTENGINE_CRAWL_CONCURRENCY=2`**, with single-request fetch-endpoint probes at ~+15 min and ~+30 min (a clean probe allows starting early; probes run from the same NL IP, one request each, negligible load). If the c2 run stalls again (CrawlStalled within ~10 min of fetch-phase start) → same-egress hardening exhausted → **rotation #4 = OWNER WALL** (budget sign-off, country ≠ us/de/nl): record the evidence and wait — do NOT rotate without the owner.
    - **MARVEL C2 FETCH STALL → OWNER WALL TRIGGERED (08:29–08:40; rotation #4 now pending the owner):** after the 45-min cooldown plan, the +15-min single-request probe at 07:49 came back clean (HTTP 200 on the fetch endpoint — one-off requests pass the limiter), so c2 launched early at 07:50:20 (pid 113427). Enumeration clean again (all 279,112, zero 429s); fetch phase resumed 08:29:28 (`resuming: 213721 of 279112; crawling 65391`) → **hard-throttled again immediately: 7 rate-limit lines, 0 completions, CrawlStalled 08:34:28, killed ~08:40** (same hung-process behaviour — the kill stops the penalty-feeding retry traffic). Log archived: `reports/marvel/receipts/crawl_marvel_c2_stalled_2026-09-25.log`. **Evidence chain for owner-wall item (c) rotation #4+:** c10 429 loop 06:25 (106 lines) → c3 after 8-min cooldown: fetch stall (07:29 CrawlStalled) → c2 after 45-min cooldown + clean single-request probe: fetch stall (08:34 CrawlStalled). Interpretation: the NL egress (`186.247.163.23`) carries a **long hard penalty on the batched `prop=revisions` endpoint** (the ~06:25 c10 burst, plus each hung process's 429-retry attempts during its drain, keep extending it); single light requests pass, sustained batch traffic is rejected. Same-egress hardening (client-side throttling, 8-min/45-min cooldowns, c10→c3→c2) is **exhausted**. **Last in-authority step (no new budget):** keep the egress fully quiet (crawl stopped; at most one light probe) for ~3 h → retry **once** at c2 ≈ 11:30; if CrawlStalled again → **HARD STOP: the campaign waits at the owner wall** (rotation #4 = a new country ≠ us/de/nl requires owner budget sign-off). No rotation, no further restarts beyond that single retry. Owner-wall briefing: `reports/marvel/OWNER_WALL_2026-09-25.md`.
    - **MARVEL C2-RETRY STALL → HARD STOP IN EFFECT (11:30–12:33; no further in-authority crawl actions):** the last in-authority c2 retry launched 11:30:00 (pid 171756, after the ~3 h quiet egress; receipt `reports/marvel/receipts/c2_retry_receipt.txt`). Enumeration clean again (all 279,116 enumerated, zero 429s on the `allpages` path); fetch phase resumed 12:14:15 (`resuming: 213721 of 279116; crawling 65395`) → **429-loop again: 52 rate-limit lines, 0 completions, CrawlStalled 12:19:15**. **Ops correction (to the c3/c2 entries):** this time the drain COMPLETED — the in-flight batches finished, the post-loop code wrote the stalled manifest to disk (`series/marvel/manifest.json`: `stalled: true`, `stall_remaining: 64091`, `pages_written: 0`), and only then did the process hang on shutdown (killed 12:33:30). Under a hard lockout the outcome is run-specific: killed-mid-drain runs (c3, c2) leave no manifest; a completed drain leaves the documented stalled manifest, and the process may still hang after it. Log archived: `reports/marvel/receipts/crawl_marvel_c2retry_stalled_2026-09-25.log` (52 rate-limit lines). **The committed condition is met → HARD STOP: no further crawl attempts, no rotation — the campaign now waits at the owner wall** (all four items raised in `reports/marvel/OWNER_WALL_2026-09-25.md`; rotation #4+ is item 3, TRIGGERED with the full evidence chain: c10 06:25 → c3 07:29 → c2 08:34 → c2-retry 12:19, every one on the NL egress `186.247.163.23`). Agent posture while waiting: single light probes at most ~hourly, logged to `reports/marvel/receipts/nl_probe_log.txt` (caveat recorded: the 07:49 single-request 200 preceded a fetch stall — a light 200 is NOT a readiness signal; only a sustained c2 crawl is), and the campaign state stays resumable from this file.
    - **MARVEL ROTATION #4 (owner-approved ~14:52; NL → CA) — hard stop lifted, c3 fetch run in progress:** the owner ruled at the wall ("use the VPN to download the remaining pages") → rotation #4 sign-off (country ≠ us/de/nl; budget = VPN connection time until the crawl finishes). `nordvpn connect canada` → **Canada #1980 (ca1980.nordvpn.com, Toronto)**, egress verified `187.15.140.90` (fresh IP; the locked NL egress `186.247.163.23` is now unused). Single light fetch probe from CA: HTTP 200 (14:54:46, logged). c3 launched 14:54:46 (pid 221627; `SCRIPTENGINE_CRAWL_CONCURRENCY=3` — deliberately gentle: ~15 req/min vs the ~48 req/min that triggered the NL lockout; 65,395 outstanding → ETA ~1.5–2 h in the fetch phase). Health judge for the fetch phase (~15:35, after the ~40-min re-enumeration): >100 completions and <10 rate-limit lines in the first ~15 min = healthy → 15-min watch cycles to completion; CrawlStalled on CA = this exit is dirty too → record evidence, kill, rotation #5 = owner wall (no further unapproved rotation).
    - **FETCH PIVOT (owner ruling ~15:2x, 2026-09-25): single machine, c8, rotation pre-authorized for speed — c8 full-list fetcher in flight (pid 242771):** owner ordered: do it all here, not on a 2nd PC (the 2nd-device/"Sun 6 606" plan + the home-line second-egress idea are RETIRED — the home line is a diagnosed dead end: wired netns `se_shard2` + macvlan `mv2` @ static 192.168.1.203 gets L3 reachability, but the router does not NAT static/non-DHCP source IPs, cannot receive the DHCP broadcast over Wi-Fi (macvlan-on-wireless L2 limitation), and ignores unicast DHCP — a real cable/dongle would be needed); try more workers or anything; start right now; switch the VPN to download faster (rotations are now pre-authorized as a SPEED tool — country open, egress still logged on every connect + 15-min health judge after any relaunch). Executed 15:23: (1) the stale c2 manifest's complete `all_titles` (279,112, enumerated 08:48 today) reused as the page list → `reports/marvel/receipts/marvel_all_pages.jsonl` — NO network enumeration; (2) `tools/marvel/make_shards.py --shards 1` → `tools/marvel/shard_a.jsonl` = 65,391 outstanding (213,721 on disk); (3) in-flight c3 (pid 221627) killed 15:23:03 (still enumerating, 165,303/279,112 — zero fetch progress lost); (4) `tools/marvel/shard_fetch.py --series marvel --shard-file tools/marvel/shard_a.jsonl --shard-id full` launched 15:23:08 (pid 242771, nohup → `reports/marvel/receipts/shard_full.log`, `SCRIPTENGINE_CRAWL_CONCURRENCY=8`): ShardCrawler feeds the fixed list in place of re-enumeration (no 45-min sequential enumeration), per-run manifest `series/marvel/manifest.shard_full.json`, canonical `manifest.json` untouched. Egress CA Canada #1980, outbound re-verified `187.15.140.90` via ipify (the `.11` in `nordvpn status` is the client's internal view, not the outbound IP). Pages added after the c2 08:48 enumeration are caught by the final reconciliation (fresh full enumeration + catch-up fetch of the delta; canonical manifest rebuilt there). Health judge on the c8 fetch phase (~15:41, after template enumeration): >100 completions AND <10 rate-limit lines in the first ~15 min = healthy → 15-min watch cycles to completion; RED → step down c5/c3, and if still RED rotate to a faster country (pre-authorized; egress logged + re-judged).
    - **C8 BURST → ROTATIONS #5/#6 (15:23–15:35) — c3 + 60-s timeout on SG in flight (pid 249443):** c8 burst-looped on CA within 115 s (16 rate-limit lines, 0 completions; `receipts/crawl_marvel_c8_429burst_2026-09-25.log`), killed 15:25:09 → c3 step-down on CA 429'd within 4 s even on the light path (the c8 burst left the CA egress hot; `crawl_marvel_c3_ca_hot_2026-09-25.log`), killed 15:25:4x → **rotation #5 (speed tool, pre-authorized) Japan #1295**, egress `187.15.136.110` (ipify) 15:26:4x: 0 429s but ~2 s RTT — heavy 50-page batches hit the 30-s fetch timeout (3 retry loops, 0 completions; `crawl_marvel_c3_jp_timeouts_2026-09-25.log`) → relaunched 15:31 with `SCRIPTENGINE_CRAWL_TIMEOUT_SECONDS=60` (pid 247612). **Rotation #6 (owner: "use a closer VPN", ~15:33) Singapore #646** — SG is the closest NordVPN exit to this host: JP run killed 15:33 (0 completions, zero progress lost; `crawl_marvel_c3_jp_60s_2026-09-25.log`); egress `187.15.101.107` (ipify); Fandom probes 1.2–1.5 s with 1/3 a 15-s timeout (route watch item); c3 + 60-s timeout relaunched 15:35 (pid 249443, `receipts/shard_full.log`, egress note on the run). 15-min judge ~15:50: >100 completions + <10 rate-limit lines + low timeout rate → 15-min watch cycles to completion; RED → next rotation (pre-authorized: UK / other closer-exit candidates; egress logged + re-judged each time). **Rotation #7 (~15:38) United Kingdom #2640 (London)** — the SG run CrawlStalled at 300 s (14 rate-limit lines, 0 completions; light path clean but the heavy 50-page batch endpoint 429-looped within 4 min on a fresh exit; `crawl_marvel_c3_sg_429loop_2026-09-25.log`; 1,200 titles dropped out under the storm are re-tried by disk-resume, no loss). UK exits sit on a different Nord range (`194.88.x` vs `187.15.x`) — the discriminator for "is the 187.15 range batch-limited, or the batch endpoint across all Nord exits": clean UK batch path → range-level; UK also loops → client-side fix (slimmer batch / reduced rate) is the next council/wall item. Egress `194.88.96.77` (ipify; probes 200 in 2.0–2.5 s). First c3 + 60-s attempt ~15:40 (pid 255764) CrawlStalled at 300 s with **0 rate-limit lines** (one six-0-s batch timeout, 0 completions): a transient SG→UK tunnel degradation, NOT throttling — `crawl_marvel_c3_uk_stall_transient_2026-09-25.log` (reconstructed from the session transcript after the live log was truncated for the relaunch). Discriminator answer so far: the 187.15 exits' 429 loops were egress-specific (burned/dirty), not a range/ASN-level batch limit — the 194.88 exit is 429-clean. Direct 50-title batch probe from the same UK egress ~15:58: 200 in 1.64 s, 50/50 pages (endpoint healthy from UK). Relaunched c3 + 60-s on the SAME UK egress (no new rotation; pid 264208, ~16:00); 15-min judge ~16:15: >100 completions + <10 rate-limit lines + low timeout rate → 15-min watch cycles to completion; RED → next rotation (pre-authorized; egress logged + re-judged). Health monitor restarted ~16:02.
    - **UK/DE 429-loops + OWNER RULING + ROTATION #9 FR c2 (~16:00–16:20):** the UK relaunch (pid 264208) 429-looped within 3 min (20 rate-limit lines, 0 completions — single-request probes pass, sustained c3 trips the limit; `crawl_marvel_c3_uk_429loop_2026-09-25.log`). **Owner ruling (~16:0x): "why are you waiting 15 min? just download it, if it doesnt start, use new VPN"** → the 15-min judge is RETIRED: quick check (2–4 min) after every relaunch; not starting / 429-looping → rotate immediately (pre-authorization stands; egress logged each time). Rotation #8 Germany #1544 (~16:04, egress `187.40.54.176` — the proven MCU-crawl 187.40 range): attempt 1 (c3, ~16:05) hung on stale pooled connections (2 failed first-attempts at the 60-s cap, 0 RLs; direct batch probe 50/50 in 1.92 s; `crawl_marvel_c3_de_stall_1_2026-09-25.log`); restart #2 (c3, ~16:11) 429-looped (6 RLs, 0 completions; `crawl_marvel_c3_de_429loop_2026-09-25.log`). **Pattern: every egress tried today (CA, SG, UK, DE) 429-loops on sustained c3 batch traffic within minutes while single-request probes always pass** → consistent with a sustained-rate limit on VPN ranges for the heavy batch query, not egress-specific dirt. Rotation #9 France #1136 (~16:18, egress `187.14.107.20`; slow route — light 3.2–10 s, batch 50/50 in 14.5 s, no 429s): launched **c2** (half the c3 request rate; env-var lever, no gate) + 60-s timeout (pid 273739, ~16:20). Quick check ~16:24: completions flowing → 15-min watch cycles to completion (c2 on the slow route ≈ 3–4 h for 65,391); 429-loop = the FIFTH egress → decisive evidence for the sustained-rate limit → escalate to council (client-side slimmer batch = gate-covered code change; per-page parse fallback; or a cooldown) — no sixth blind rotation.
    - **CH/ES c2 silent stalls + WAF UA finding + ROOT CAUSE + patch (16:28–17:23; rotations #10/#11/#12):** rotation #10 **CH #383** (~16:28, egress `89.37.173.228` — ipify UNKNOWN, range only): c2 attempt 1 (pid 281296, ~16:29) **silently CrawlStalled** at 300 s (0 completions/0 RLs/0 failures; the earlier "quick check ~16:33: completions flowing" line was WRONG — ondisk never left 213,721 all afternoon; `crawl_marvel_c2_ch_stall_1_2026-09-25.log`); c3 429-looped (killed, `crawl_marvel_c3_ch_429loop`); c2-diag EnumerationFailed (hot state); c2 + browser-UA silent stall (`crawl_marvel_c2_ch_stall_2_browserua`); c3 + browser-UA 429-loop (18 RLs/3 min, killed, `crawl_marvel_c3_ch_429loop_browserua`). **WAF UA-discrimination probe (16:44, `tools/marvel/batch_probe_ua.py`, exact chrome136 session replica):** same session/egress — crawler UA `ScriptEngine/0.1` → **429 + "Just a moment…" HTML in 1.1 s**; browser UA → **200 JSON 50/50 in 0.51 s** → the c3 429 loops were Cloudflare WAF **UA challenges**, not Fandom's limiter (state escalated through the afternoon; CH challenged the browser UA by 16:50) → the "sustained-rate limit on VPN ranges" theory is RETIRED for the c3 loops; every launch now carries the chrome136 browser UA. Rotation #11 **ES #175** (~16:52, egress `187.13.187.62` ifconfig.co): route healthy (light 1.8–2.5 s; batch 50/50 in 2.0 s browser UA); full-list c2 + browser-UA attempts 1+2 both silent CrawlStalled (`crawl_marvel_c2_es_stall_1/_2`). **c2 silent stall = six straight (FR, CH×2, CH-browserUA, ES×2), on every egress, UA-independent; c3 runs were never silent.** py-spy on the hung c2: MainThread idle in `select`, zero worker OS threads → hung `await` invisible to py-spy (SIGUSR1 `Task.print_stack` via `tools/marvel/c2_diag.py` is the tool). **Repro #1 (17:05, ES, head-200) INVALID** — clean exit 0 fetched/0 failed: the first ~1,200–1,300 shard titles are already on disk (the pre-stall c2 crawl wrote the head: 65,391 − 64,091 ≈ 1,300) → no real batch request was ever issued. **Repro #2 (17:10, ES, TAIL-200 off-disk titles): c2 + browser UA fetched 160/200 clean in ~3 min (ondisk 213,721 → 213,881, 0 failures)** — the c2 batch path works. **A/B + instrumented full run (17:15–17:20, ES):** full c2 + browser UA (`shard_fetch.py` pid 298524) same silent signature at 3 min → killed + archived (`crawl_marvel_c2_es_stall_3_fullrun`); `c2_diag.py --limit-titles 0` (pid 299943): 2× "rate limited; pausing all workers for 30 s" within 5 s, and the **SIGUSR1 task dump shows BOTH workers suspended at `crawler.py:708` → `await self._learn_labels(...)`** (`crawl_marvel_c2_es_learn429_taskdump_2026-09-25.log`). **ROOT CAUSE (RESOLVED):** `_learn_labels` — one `action=parse&prop=properties` request per new page type, issued **between the batch fetch and the page write** — 429-loops/hangs in hot WAF state (`_get` 4 retries + 30–120 s global throttle pauses), pinning both workers before any page write → 300 s/0 writes → CrawlStalled with the batch endpoint healthy the whole time (the 200-tail run only passed because the WAF state was clean then). Secondary defect: a type with no PI schema (or a failed learn) is never marked learned → re-fetched on every page of the type. **Fix patched into `scriptengine/ingest/crawler.py` (`_learn_labels`): bounded (`asyncio.wait_for(crawl_timeout_seconds + 30 s)`) + failure-tolerant (timeout/failure → default labels; type recorded with an empty label set so it is never re-fetched).** Output unchanged on a healthy egress. **GATED: the four standing gates (pytest running; eval jjk / span-recall jjk / canon-run opm) before the patch is used/committed.** **Rotation #12 (17:23, pre-authorized speed tool): Finland #214 (fi214.nordvpn.com), egress verified `187.40.62.59` (ipify + ifconfig.co + ip.sb agree).**
    - **GATES GREEN + PATCH COMMITTED + FULL c2 FETCH COMPLETE + RECONCILIATION IN FLIGHT (17:27–18:0x; rotation #12 FI egress `187.40.62.59`):** (1) **Four standing gates GREEN on the `_learn_labels` patch** (receipts `reports/marvel/receipts/gates_learn_patch_2026-09-25/`): pytest **1,345 passed + 2 xpassed + 3 failed** (exactly the documented `:8000`-down trio; the 17:24 first run flaked one rank-dependent `test_context` case while the rotation + FI probes ran concurrently — clean 206-s re-run green, not patch-attributable); eval jjk **31/31** (CPU — Qwen holds the card, `SCRIPTENGINE_DEVICE=cpu`); span-recall jjk **48,572/48,572 rc=0 + live probe 398/400 (99.5%)** (bounded `:8000` CUDA window at the morning margin 5,462 MiB free, health-checked, STOPPED — steady state restored: port free, 5,462 MiB, Qwen 7676 alive); canon opm **10/16 exact · 236/236 · 79.0%**. (2) **Committed `e78e1f62`** (named paths: `scriptengine/ingest/crawler.py` + `plan/SWITCHPOINT.md` + `plan/MARVEL_100_PLAN.md`; owner files still `M`; `reports/marvel/` + `tools/marvel/` still untracked). (3) **Full-list c2 fetch COMPLETE 17:45:55–18:00 (pid 314745, FI egress, chrome136 UA, 60-s timeout): all 65,231 outstanding titles accounted for — 22,701 written (in ~15 min, rl=0 / to=0 / learn-warn=0: the patch held, zero WAF escalation) + 42,530 skipped (no-content / skippable-category / duplicate pageid — the enumeration's tail is stubs, redirects and galleries) + 1 failed ("Elizabeth Tyne")** (22,701+42,530+1 = 65,232 ✓); corpus now **236,580 on disk**; receipts `crawl_marvel_c2_fi_full_done_2026-09-25.log` + `series/marvel/manifest.shard_full.json` (its `field_labels` shows the patch's explicit `{}` marks on the no-PI types — marked attempted, never re-fetched). The earlier "2.5–3.5 h" was a title-count estimate, not a fetch estimate. (4) **Reconciliation COMPLETE 19:06:58 (pid 320221, FI egress, launched
18:06:31 — egress re-verified + batch probe 50/50 @ 1.77 s first;
quick check 18:09: chrome136 impersonate session confirmed, enumeration
in flight, 0 RLs): canonical `crawl --series marvel` = fresh full
sequential enumeration (18:06–18:58, **279,133** — the wiki grew +21
since the 15:21 list; 279,133 is the new ground-truth denominator,
superseding 279,116) + on-disk resume-skip + catch-up fetch 19:01–19:06
(**48 written + 42,504 re-verified skips + 0 failed**; the 42,552
non-on-disk queue = the shard run's no-content/skippable tail,
re-proven by the pipeline itself so the canonical manifest stands on the
pipeline's own accounting — including the shard run's one failed page,
now `pages_failed: 0`). **Canonical `series/marvel/manifest.json`
REBUILT CLEAN** (no `stalled` marker; `pages_enumerated 279,133` /
`pages_on_disk 236,628` / `pages_written 48` / `pages_skipped 42,504` /
`pages_failed 0`; accounting closes exactly: resume line
`236581 of 279133 already on disk` (2 titles share one filename →
236,580 files pre-run) + 48 + 42,504 + 0 = 279,133 — **every enumerated
title accounted as on-disk ∪ skipped ∪ failed**; the `stalled: true` /
`stall_remaining: 64091` manifest is obsolete). Whole run rl=0 / to=0 /
learn-warn=0. Log: `reports/marvel/receipts/recon_canonical.log` →
archived as `receipts/crawl_marvel_recon_done_2026-09-25.log`.
**Marvel fetch phase = 100% COMPLETE (236,628 on disk, 0 failed,
279,133/279,133 enumerated accounted). Kill-on-429-loop / hung-drain
rules stand for any later network phase (Phase B); rotate pre-authorized
(next unused range = Italy; egress logged each time).**
    - **Next (in order):** (1) Marvel-set gates 4–6 on the final corpus (same harness as the MCU run: base extract `PYTHONPATH=/tmp/se_base_1adb0d42 … --no-overrides`; new extract `PYTHONPATH=/home/goblin/ScriptEngine … --values`; `parse_diff.py` >10%/systematic-rewrite stop; gate 5 Marvel = 20–50 character pages asserting `currentalias` extraction + the 10-page disambiguation zero-facts sample; `revid_spotcheck.py --series marvel`; the `_learn_labels`-wedge regression test is a POST-CAMPAIGN/council item — NOT this cycle, the 1,345 baseline is pinned) → (2) GATE A council (sequential subagents, one at a time; must bless the *Marvel* validation, not just the four JJK/CSM gates; wall items 1/2/4 still open: ToS/robots ruling, disambiguation zero-facts policy, gate-definition ratification) → (3) Phase B (CC corpus; `SPEAKER n` no-guess fallback). While gates/council run: no CPU job >15 min (extract passes ~10–12 min each — run as separate jobs); `:8000` stays down (3 `test_mcp_server.py` env failures = the documented trio); commits by named paths only (the owner's `tools/csm/d7_gates.sh` + `tools/master-work/switch_restart3_oc.sh` stay `M`; `reports/marvel/` + `tools/marvel/` stay untracked). A2 stays NO-GO until 4–6 pass AND the owner ToS/robots wall call (tooling already inspected). The A1b disambiguation gap-fill stays index-time (disk-driven in `load_extracted` — do NOT stall anything on it, per the council).
- **2026-09-24 ~05:4x (opencode session `ses_f2f7bfe8cffegkgz0l6AQllWeV` — CSM P2-scope checkpoint complete; the GPU window is owner-triggered, design-locked):**
  - **Campaign ledger (disk-verified):** product state (flag-OFF) = **469/486, 17 reds** (ref `d7_window/snapshots/census_head_469.jsonl`); campaign grade (TIERED ON) = **473/486** (13 reds = 11 retrieval-gated dim rows + 2 width-class {pool-140, pool-358}, per D7-CLOSE #37). The on-disk `census_widened_csm_results.jsonl` is the LEG B census (pool-140/358 green / pool-149/252 counter-flipped red) — a trap; the product reference is the snapshot. FLOOR16 = the 17 product reds − org-03.
  - **COUNCIL #38 (P2-scope lock) — verdict: LOCKED WITH 8 AMENDMENTS** (receipts `reports/csm/receipts/council_p2_scope/`, record `chairman.md`; ledger #38 + backfilled #37 in `reports/comprehension/COUNCIL_HISTORY.md`; GATE.md D37 section): (Q1) extraction ≠ the qa-floor flip lever (all 16 FLOOR16 rows are retrieval-config gaps; D6: 333 events, 0 flips) → leg (c) is the **pre-registered STRETCH leg** (narrative-door event layer + Q4 coverage; owner word + first-10-pages rate probe); (Q2) window commits to **minimum-viable (a)gates+(b)sweep+(d)width-instrument+(e)re-grade ≈ 5 h**, no commits in-window, zero-regression receipts + JJK diff + span/coverage re-proof in (e), 1.2–2× shrink band; (Q3) width instrument stands + **beyond-class counter-flip bound = 0** (violation ⇒ class-scoped hunk only); (Q4) **(d) before (c)** (same-index arms; a leg-(c) OOM can never grade (d) on a partial index); (Q5) TIERED flip = **its own gated owner-word window** (unanimous). Close = ledger closure (green OR voided with named defect+leg+retest); lever path caps at **475**; a guaranteed 486/486 is never claimed.
  - **JEV measurement receipt (amend #38-7, `JEV_MEASUREMENT.md`):** council #38 = 175 req / 10.46M prompt / 336k output / **67.76% prefix-cache hit** (vs R-5 baseline 3.76M/110k/6.1%); pruner logs 0 `hook_error` (bash pruner: 61 `no_scoring_capacity` fail-open events 23:05–00:06 UTC, by design).
  - **Window-killer pre-checks (verified ~05:3x, re-run at window start):** (1) `mountpoint /mnt/PROJECTS` — up (root-owned fuseblk, touched 00:27 today); (2) `/mnt/PROJECTS/ninfer-transfer/models/qwen3_8_27b_nvfp4.ninfer` (18.3 GB) present; (3) the owner's UNCOMMITTED `tools/csm/d7_gates.sh` restore argv (line 36) resolves — authoritative, stays uncommitted; (4) detached chain writes STATE+RECEIPT sentinels; (5) owner-alert rule on RED/missing-sentinel/restore-failure.
  - **GPU window checklist (owner-triggered; Qwen :18080 down for the window — pid 4332 @ 262k, :8000 down; legs detached):** (a) `setsid nohup bash tools/csm/d7_gates.sh` → (b) `setsid nohup bash tools/csm/p21_sweep.sh` → (d) `tools/csm/widthclass_run.py` → (e) `setsid nohup bash tools/csm/p23_handoff.sh`; **stretch (c)** only on owner word + rate probe (dry-run first, re-verify 230/406 @ the window's HEAD): `scriptengine/.venv/bin/python -m scriptengine.cli events-extract --series csm --scope corpus --pages reports/csm/p2_keep_pages.txt --workers 2`. Standing guards on every regrade: 0 counter-flips / green30 30/30 / OOS200 drop <3 (floor 166) / blind 19/19 / 4 gates green / JJK diff = gate artifacts only.
  - **Owed CPU-side BEFORE the owner calls the window:** (1) `tools/csm/widthclass_run.py` (the pre-registered instrument vehicle, per `WIDTHCLASS_PREDICT.md`); (2) a fresh `reports/csm/receipts/p2_extract/RECEIPT` writer for leg (c); (3) the D7a 37-row retest (id-pinned roster now in `D7A_NUMERIC_COLLISION.md`) rides leg (e).
  - **NEVER commit the owner's dirty files:** `plan/SWITCHPOINT.md`, `tools/csm/d7_gates.sh`, `tools/master-work/switch_restart3_oc.sh`. /mnt/PROJECTS is add-only (no commits there — not a git repo, root-owned fuseblk).
  - **Next:** owner calls the window (or orders the two pre-window artifacts first). On resume of this session: verify `qwen_mode.txt` + `/tmp/switch_restart3_oc.log` if a switch happened, confirm session `ses_f2f7bfe8cffegkgz0l6AQllWeV`, then continue from the "Owed CPU-side" list.
- **2026-09-20 ~00:2x (pi session `01a0bb30`, owner-directed 262k → 135k + terminal relaunch; no campaign work in flight):**
  - **Mode: 262k (ctx 262144) → 135k (ctx 138240, raw-dial; `ninfer-work/serve_ctx_138240.sh` auto-generated by the switcher).** Pre-switch card: qwen pid 3895 @ 262k, 30,367 MiB used / 1,744 free, `:8000` OFF, no extraction in flight. Post-switch prediction: free ≈ 7–8 GiB → helper places `:8000` on CUDA (≥6 GiB headroom rule).
  - **JSON sync is done by `qwen-switch.sh` part 2 (no manual edits):** pi `~/.pi/agent/models.json` contextWindow→138240, repo `opencode.json` limit.context (ninfer-27b)→138240, global `~/.config/opencode/opencode.jsonc`→138240. (Same session fixed the global jsonc's invalid `external_directory` array → object map, backup `~/.config/opencode/opencode.jsonc.bak-extdir`, and the repo opencode.json permission block — both verified parse-clean.)
  - **Terminal flow (owner: "close current terminals, reopen both"; one detached shell = 3-part helper + opencode relaunch):** `switch_restart3.sh 138240 <session_file> 24658 24567` — part 1 unload → part 2 load + json sync + `:8000` placement → part 3 internal LLM call → `relaunch_term.sh`: new gnome-terminal `pi --session <file>`, old pi 24658 + shell 24567 killed (my window closes). Then the same detached shell closes the opencode window (TERM 24978 → verify → KILL -9; TERM 24836 → verify → KILL -9) and reopens `opencode -c` (resumes last opencode session) in a new window. oc-watch (pid 5274) idle-polls and re-engages automatically.
  - **UNCOMMITTED → now committed** (D59 never-lose): D7 snapshot at `4a8616bd` (context.py TIERED + ABILWIDTH legs, d7/d6-probe receipts, report jsonls); skill frontmatter fix at `55f41208`. Switch log line appended by the switcher below.
  - **First action on resume (post-flight, then STOP):** (1) status line shows /135k; (2) `cat /home/goblin/ninfer-work/qwen_mode.txt` (expect ctx=138240, free ≈ 7–8 GiB, api=cuda|cpu); (3) `tail /tmp/switch_restart3.log` (part3 answered, new pi pid, old pi gone, relaunch done); (4) opencode window up (`pgrep -x opencode`, new pid ≠ 24978); (5) report one line to owner, no work until owner speaks.
  - **Campaign position (unchanged by this ops switch):** CSM Phase 1, per `plan/drift_log.md` §4 (D22); D7 uncommitted-leg question (narrow-legs-singly vs focus-resolution spike) remains open for the council — see the 2026-09-18 entry below.
- **2026-09-18 ~16:5x (opencode session — CSM D7 re-score council resume;
  prior muse-spark session `ses_f503d5a0` (1,647 msgs) hit its model limit
  at 16:24 mid-plan):**
  - **CSM position: D7 post-deriv-leg.** HEAD `20d6da4e` = derivation leg
    (verbatim-first + possessive-deferral) committed after the D61 owner-word;
    post-commit gate window `/tmp/d7_gates` (15:46–15:59) ALL PASS (pytest
    1,329+2x / eval jjk 31/31 / span 48,572+probe / canon baseline / p23 469
    w/ 4 flips + 0 counter). D6 CLOSED (A20, `9ef7082e`). Remaining reds
    **23** = 7 D7 holdouts (chap-01, org-03/05/06, vol-10, pool-140/358) +
    16 Phase-2 floor.
  - **UNCOMMITTED (D59 rule — never lose; stash-surgical, snapshot grade
    files before overwriting):** 44-line narrow legs in
    `scriptengine/api/context.py` — **TIERED** (env-flagged
    `SCRIPTENGINE_TIERED_RECALL=1`; second top_k=30 search; tier-2 novel
    chunks appended after beam+floor, rendered only from leftover budget;
    flag off = byte-identical) + **ABILWIDTH** (possessive query +
    `_owner_attribute_hit` declared (character, ability-prefix) pair →
    top_k=30; NOT flagged; targets pool-140/358 width holdouts, gold ranks
    12–47 cut at 8) + 3 report jsonl (`census_widened_csm_results.jsonl`,
    `reports/index.md`, `recall_verbatim.jsonl`). D59 measured tiered at
    **473** (+4: arcn-02/10, org-03, state-08; 0 counter); ABILWIDTH
    unmeasured. Queue per D61: width (tiered, chair-ordered) → depth
    (arcn-03/04, state-03, vol-10-class) → official suite → VOID formal →
    CLOSE.
  - **Open wall for the council:** ranking probe **RED** (arcb-05 "What
    happens in the Katana Man arc?", gold 4988 never shortlisted — defect is
    UPSTREAM of ranking; the D7 limit is still unproven; GATE's last line:
    "follow-up is a focus-resolution spike, then the D7 leg proper"). Ruling
    needed: narrow-legs-singly (pre-register → run → grade) vs
    focus-resolution spike first, the GPU path, and the one-subagent task.
  - **Live GPU (re-verified 16:4x):** Qwen **135k owner-manual** (pid
    1137321, launched 16:31 via `serve_ctx_135168.sh` — open in the owner's
    editor; `--max-context 135168 --kv-capacity 143360`; 26,962 used /
    5,142 free MiB) → the ~5.3 GB in-process CUDA stack does NOT fit;
    `:8000` DOWN; `qwen_mode.txt` STALE (says mode=off @16:30:50);
    `tools/csm/d7_gates.sh` restore STALE (hardcoded 65k argv). Full 135k
    restore argv captured in the 16:4x ps output (this entry's session
    record). This opencode session runs ON Qwen :18080 — a mode switch kills
    the in-flight turn (owner resumes `opencode -c`); fill THIS section
    first, per the file's rule.
  - **Prep subagents (read-only, 2 in parallel per owner 16:4x):** state
    compaction (task `ses_f4bd05f4`) + re-score staging (task
    `ses_f4bd05f3`: launch commands, preflight, wall-clocks; corrections =
    confirm legs ALREADY ran D61, `qwen_mode.txt` stale, `d7_gates.sh` 65k
    stale, two-OOS-instruments clobber warning on `D6_OOS_PRE.jsonl`).
  - **COUNCIL #36 COMPLETE (D7 re-score; sequential 11 members, all finals +
    the verdict restored verbatim from opencode.db):** record
    `reports/csm/COUNCIL_csm_d7_rescore.md` + receipts
    `reports/csm/receipts/council_d7_rescore/{framed_question,advisors,
    reviews,chairman}.md`; ledger #36; drift D63. **Verdict:
    LEGS-FIRST-FLAGGED** (Q3 (b) 4–1): (Q1) grade the two narrow legs
    SINGLY in one detached kill-window (A: TIERED=1/ABILWIDTH=0 → B:
    TIERED=0/ABILWIDTH=1 → C: both); the focus-resolution spike runs AFTER,
    GPU-free, in the live session (GATE's "spike first" line ruled stale —
    it predates D59, which already flipped D7 row org-03); (Q2) ABILWIDTH
    behind the new flag `SCRIPTENGINE_ABILWIDTH_RECALL` (default OFF,
    3-line mirror of `_tiered_enabled`; ruled against the 3-advisor as-is
    majority — its JJK no-op is data-dependent, not by-construction); (Q3)
    stop owner-manual 135k → grade legs + four standing gates (both flags
    default-OFF) on the whole card → restore 135k from the freshly captured
    + verified argv — as ONE `setsid nohup` chain
    `tools/csm/d7_window_chain.sh` (every post-kill step is shell; this
    session runs on the server being killed), issued as the subagent's
    final act; (Q4) ONE subagent task: 6 pre-staging steps (D59 receipts
    gate — chairman verified ABILWIDTH ∉ D59's 473 tree, so the full-bank
    grade genuinely remains unbought; 17/6/23 arithmetic re-statement; OOS
    floor authority = `d6_flip.py` exit-2 + `D6_OOS_PRE.jsonl` backed up;
    TIERED flag-off inertness by read; argv capture + verification to
    `/tmp/d7_qwen_{pid,argv,cwd}.txt`; snapshots + the 3-line flag edit +
    per-leg `PREDICT.md` (A: W ≥ 469, flips ⊇ {arcn-02, arcn-10, org-03,
    state-08}; B: W ≥ 469, flips ⊇ {pool-140, pool-358}; C: the union;
    each 0 counter-flips, blind 19/19, `d6_flip.py` rc=0; + the 16-row
    floor re-count — TIERED's +4 flipped floor rows arcn-02/10, state-08)
    + `check_targets.py` + the SWITCHPOINT governance commit (engine code
    stays uncommitted) → then the chain. **Pass bar** = all three legs +
    the four standing gates (pytest 1,331 pin / eval jjk 31/31 / span jjk
    48,572 + 400-probe / canon opm ≥ 10/16 · 236/236 · 79.0%); **stop
    conditions** = first RED leg (halt the rest; gates still run for the
    record; Qwen restored; receipt = RED + that leg's kill clause — no
    ex-post retuning, D59) / OOM or restore failure (receipt + owner
    relaunches 135k by hand from the captured argv) / **no engine-code
    commit without owner word**. **Post-commit flag config (R5 gap
    closed):** both flags default-OFF in the commit; the CSM `p23_grader`
    grade runs flag-ON; the four standing gates run default-OFF (the
    committed tree = the structural JJK no-op proof); the default-flip
    (shipping CSM default-ON) + its 4-gate rerun + GATE.md record =
    DEFERRED, a separate owner decision.
  - **NEXT ACTION:** launch the ONE subagent task per the chair's Q4 spec
    (full spec + the chain script's verbatim body in `chairman.md`). After
    the chain: owner resumes `opencode -c`, reads `reports/csm/receipts/
    d7_window/RECEIPT_DONE` + `/tmp/d7_gpu_chain.log` (no sentinel within
    the hour ⇒ card in known-bad state ⇒ relaunch 135k by hand from the
    captured argv); commit the engine diff only on all-green + owner word.
- **2026-09-18 (opencode session — D6 dedicated-GPU window checkpoint,
  council #35 D39 lock @ `2ee7edc`):**
  - **NO Qwen mode switch in this window** — Qwen is already at the 100k
    profile (pid 495401, `--kv-capacity 102400`, port 18080); the locked
    "checkpoint (switchpoint)" is resumability-only (this file + git), so
    no `qwen-switch.sh` line is appended.
  - **CSM position: D6 extraction window** (campaign todo 6, P2.3 D6
    extraction leg). Locked scope (council #35): additive `events-extract
    --pages <frozen-list>` flag (NOT a `--scope` change), 30-row green
    sample (N=5/dim × 6 dims, seeded, disjoint from the 200-row held-out
    OOS), P/T/A triage on the 134 setrel + 6 abl rows, A20 stamp. Full
    record: `reports/csm/COUNCIL_csm_d6.md` + `GATE.md` D6 block +
    `plan/drift_log.md` D39.
  - **`--pages` flag IMPLEMENTED + proven this session** (JJK zero-regression
    gates A byte-identical + B scope-plan identity, CSM corpus = 235 pages
    / 412 sections; native `--scope corpus` untouched, remains the
    fallback): receipt `reports/csm/D6_PAGES_FLAG_RECEIPT.md`, code in
    `scriptengine/cli.py` + `scriptengine/ingest/events.py` (committed
    `aa410c0`).
- **GPU window order (locked §4, model-unloaded first):** (1) pre-window
     chain — targeted re-crawl Yoru + Asa Mitaka → CSM re-index with
     zero-regression receipt → frozen P/T/A triage + the CSM `--pages`
     frozen list → freeze 30-row green + 200-row OOS sets (seeded,
     disjoint) → pre-extraction OOS + 134 page-run baselines. **(1)
     COMPLETE 2026-09-18:** `D6_OOS_PRE.jsonl` (230 rows, 0 errors:
     green30 30/30 MECH_GREEN; oos200 168G/32R — matches the offline freeze
     mix) + 134/134 page-run rc=0 all 100% (417 set + 665 fact questions;
     receipts in `reports/csm/receipts/d6_page134_pre/`, 2.4 MB) — the
     setrel class is closed pre-extraction (D36 cross-check: 136 rc=2 rows
     = 134 setrel slugs + 2 sweep reports). (2)
     `nvidia-smi` pre-check → stop `:8000` (pid 788943, re-verified at
     launch; 745658 was the pre-re-crawl pid) → `events-extract --series
     csm --scope corpus --pages reports/csm/D6_PAGES_FROZEN.txt --workers 2`
     (dry-run receipt already @ `95337f4`; per-page atomic resume; abort →
     resume with workers 1) → index rebuild → restore `:8000` to CUDA. (3)
     model-unloaded side session: re-grade + JJK 4 standing
     gates → closure council → A20 stamp.
- **Steady-state GPU on disk now (re-verified 2026-09-18 pre-window):**
     Qwen 100k pid 495401 (25,543 MiB) + `:8000` CUDA pid 788943 (log
     `/tmp/scriptengine_api_cuda.log`), 29,275/2,829 MiB used/free of
     32 GB. Window flips the inversion of W1: Qwen model-only + ~7 GB free
     during extraction.
  - **P6 §7 addendum due 2026-09-25** (method seed only; 7-wiki rollout is
    a separate future owner decision): `plan/Plan_to_perfection.md` §7.
- **FIRST ACTION ON RESUME:** the D6 GPU window (item 2): `nvidia-smi`
     pre-check → stop `:8000` (pid 788943) → confirm Qwen model-only +
     ~7 GB free → launch `events-extract --series csm --scope corpus
     --pages reports/csm/D6_PAGES_FROZEN.txt --workers 2` detached
     (`setsid nohup`, log `/tmp/d6_events_extract.log`) → poll → index
     rebuild → restore `:8000` (CUDA) → model-unloaded side session
     (486 re-grade + 134 page-run re-run + 4 standing gates) → closure
     council → A20 stamp. Item 1 is COMPLETE (receipts above). Read
     `reports/csm/GATE.md` D6 block + `COUNCIL_csm_d6.md` first if context
     is lost.
- **2026-09-17 (opencode session — post-P2.1-sweep council #31; P2.3+P2.2
  graded via the Claude model-unloaded handoff):**
  - **CSM position: post-sweep close, P2.3+P2.2 DONE, pre-P2.4.** Council #31
    verdict + pre-registrations P-1…P-5 on disk (`reports/csm/
    COUNCIL_p21_post_sweep.md` + `GATE.md` + `plan/flow.md` + drift D27,
    commits `3a1af4f` + `f1619d4`). The P23 handoff fired in the Claude
    session: widened 486 (qa) = 417 MECH_GREEN (85.8%, 69 reds), bar audit
    qa 11/26 (pre-fix control arm, P-2) + auto 14/26 (R-9 supplement),
    0/538 probe errors — results + receipt `3d43a21`, red triage + P-3
    pre-analysis in `reports/csm/p23_red_triage.md` (37 box-class wrong-page
    ranking, 27 width/enumeration, 5 state-over-time content, 0 judge
    artifacts; **R-9 is not the lever for these reds**). Drift D28.
    Qwen left DOWN (mode=off); CPU `:8000` untouched.
  - **FIRST ACTION ON RESUME (owner, Qwen up):** P2.4 writer leg (one
    `script-gen` + `cli verify` on CSM) → the R-9-vs-writer-bar evidence
    call (input: `p23_red_triage.md` + the P2.4 output) → residual triage
    sign-off (P-4, all logs on disk) → `PHASE_B_COMPLETE`.
  - **P2.4 FIRED 2026-09-17 (opencode session, Qwen up @ 174080 pid 286402,
    no switch needed):** `script-gen "Denji" --series csm --words 6000
    --mode auto`, writer via `SCRIPTENGINE_WRITER_BACKEND=opencode`
    (opencode → Qwen `:18080`), research in-process on
    `SCRIPTENGINE_DEVICE=cpu` (4.4 GB free < 5.3 GB; Qwen owns the GPU —
    hard rule). Essence (owner-rule pick, stated not asked): quiet heavy
    opening (Tokyo alley, the boy with nothing to lose), slow anime pacing,
    resolution = "love is the power that keeps a heart moving" (a reading),
    tragedies worked: debt, the abusive father, agency lost to Public
    Safety. Also fixed: `.env` SCRIPTS_ROOT was a stale Windows path — the
    two JJK video folders moved into `scripts output/`. If this session dies
    mid-run: poll `/tmp/p24_writer_leg.log`; a re-fire reuses the video
    folder (idempotent subject+title).
- **2026-09-17 ~09:50 (Claude session C — owner-directed switch 262k → 170k, ctx 174080):**
  - **Switch:** `qwen-switch.sh 174080 --force` (owner correction: 170k, not
    full context; same dead 09-12 pi transcript trips the fit guard). Configs
    to 174080: pi `models.json` + repo `opencode.json` (the main one, by the
    script) + global `~/.config/opencode/opencode.jsonc` (by hand, back to its
    pre-09:38 value). `:8000` device follows the 174080 headroom; if the
    script leaves it down (same-device restart defect, work_log 09:27), it is
    restarted by hand.
  - **CSM position unchanged:** P2.1 measured
    (`reports/csm/p21_sweep_2026-09-17/REPORT.md`), tree clean at `5117740`.
- **2026-09-17 ~09:40 (Claude session C — owner-directed switch 100k → 262k full context):**
  - **Switch:** `qwen-switch.sh 262k --force` (the fit guard reads the dead
    2026-09-12 pi transcript, ≈264k > 262,144; no pi process alive). At 262k
    `:8000` runs on CPU (≈3.5 GiB headroom). Configs synced to 262144: pi
    `~/.pi/agent/models.json` + repo `opencode.json` (by the script) + global
    `~/.config/opencode/opencode.jsonc` (by hand — the script does not sync it;
    it was stale at 174080). A running opencode session keeps its start-time
    limit until reopened.
  - **CSM position unchanged since the entry below:** P2.1 measured
    (`reports/csm/p21_sweep_2026-09-17/REPORT.md`), tree clean at `fb20145`.
    FIRST ACTION ON RESUME: the REPORT.md "Owed / for A" list.
- **2026-09-17 ~09:35 (Claude GPU session C — post-sweep switch off → 100k, plan A19):**
  - **Switch:** Qwen `off` → `100k` (`qwen-switch.sh 100k --force`). The fit
    guard refused on the newest pi transcript (2026-09-12 session, ≈264k
    tokens) — no pi/opencode process is alive, so that transcript is dead;
    **the next pi/opencode session must start FRESH** (resume from this entry +
    `reports/master-work/work_log.md` newest lines). `:8000` is restarted by
    the switch on CUDA if the 100k headroom allows (≥ 6 GiB), else CPU.
  - **CSM position: Phase 2 P2.1 MEASURED.** R-8 gate window green @`4b60043`
    (pytest 1,331 / eval jjk 31/31 / span-recall jjk 48,572 + 398/400 / canon
    opm 236/236; `GATE_LEDGER.json` last_green = R-8). P2.1 sweep runner exit
    0: **qa 98.48 %** (≥ 97.5 % bar, 261-row miss file), narrative 10.74 %,
    roster 0.77 %, **auto 15.43 % — fails the bar** (heldout 14.00 %); R-8
    moved 0/100 auto routes — the second misroute sends 89 % of line lookups
    to narrative. Report: `reports/csm/p21_sweep_2026-09-17/REPORT.md`.
    Widened census bank (Q1/Q2): `reports/csm/census_widened_csm.json`.
  - **Clean commit sha:** `93043d6` (sweep + census) → this checkpoint commit.
  - **FIRST ACTION ON RESUME:** read the REPORT.md "Owed / for A" list —
    (1) the second-misroute decision, (2) qa miss-file triage, (3) narrative /
    roster residual triage, (4) P2.2 bar audit never graded (A7 open),
    (5) A14 / P2.3 grader for the widened bank, (6) GATE.md + CLAUDE.md pin
    stamps (1,321 → 1,331).
- **2026-09-16 ~22:5x (opencode session — CSM coding-only; GPU work handed to Claude, no Qwen switch in this session):**
  - **No mode switch happened** — this is a coding-only opencode session on
    tree `852916e`. Mode/dial state is whatever the last recorded switch left
    (120k ctx=122880 per the 09-14 entry). Qwen (27B, `:18080`) resident on
    the card; `:8000` down.
  - **CSM position: Phase 1 CLOSED (extraction-gated floor, marker
    `407c016`); Phase 2 (P2.1 sweep) pre-baked, GPU leg unstarted.** All
    detail on disk: `plan/COMPACTION_PROOF.md` (newest dated note 2026-09-16
    ~22:50 — READ THIS FIRST on resume) + `reports/master-work/work_log.md`
    (newest line, R-8 gate-debt window) + `reports/csm/GATE.md` (R-8 landed
    section at the bottom).
  - **What landed this session (all committed):** (1) the P2.1 sweep runner
    `tools/csm/p21_sweep.sh` — pre-checks (frozen A26 hashes / row counts /
    `:8000` /health / Qwen-down → exit 10/11/12), stamp-based A18 pre-wipe
    (HEAD-stamped rows resume; pre-R-8 `f2a611d` sanity ledgers wipe), qa →
    narrative → roster → auto + 200-row auto-heldout, 30 s watchdog, halt
    codes exit 4/5/20+rc/30, receipts under `reports/master-work/`; (2) the
    env-mc test fix (`test_research_bare_character_name_is_qa`, count-neutral);
    (3) GATE.md / work_log / COMPACTION_PROOF stamps.
  - **Owed GPU work (Claude session, Qwen DOWN, whole 32 GB for `:8000`):**
    (1) R-8 gate window: 4 standing gates + `eval --series jjk` 31/31 at the
    post-R-8 pin **1,331** (the 407c016 window is pre-R-8; `GATE_LEDGER.json`
    `last_green` still R-7 `60e568f`); (2) launch the sweep:
    `setsid nohup bash tools/csm/p21_sweep.sh > /dev/null 2>&1 < /dev/null &`
    (wall ≈ 2.7 h + ~4 min heldout; poll `p21_sweep_<stamp>_run.log` +
    `nvidia-smi`); (3) on GREEN receipt: P2.3 widened census authoring (Q1–Q4
    rulings, `tools/census_dimensions.py`) + D6 extraction (Qwen owns the
    card) → completion declaration + pilot memo (A24 receipt).
  - **Clean commit sha:** below (this checkpoint).
  - **FIRST ACTION ON RESUME:** (1) `cat plan/COMPACTION_PROOF.md` (newest
    note) + `reports/master-work/work_log.md` tail; (2) `git log --oneline
    407c016..HEAD` (expect `aada154` + this checkpoint only); (3)
    `nvidia-smi` (Qwen only on the card, `:8000` down); (4) run the R-8 gate
    window, then the sweep.
- **2026-09-14 ~03:3x (owner-directed: 174k → 120k, PI session — Creator Research campaign; CSM parked):**
  - **Mode: 174k (ctx 174080) → 120k (ctx 122880, raw-token dial-down).** Pre-switch
    card state: `qwen_mode.txt` = `mode=174080 ctx=174080 qwen_pid=42381
    ts=2026-09-14T03:11:11+05:30 api=off free_mib=4293`; `:8000` off, no
    extraction in flight. Expected headroom ≈ 6.2–6.3 GB (measured 6,303 MiB
    at 122880 on 2026-09-12). `:8000` stays off (no `--api`).
  - **This is a PI session** — the agent runs the switch as ONE blocking bash
    call (`cd /home/goblin/ninfer-work && ./qwen-switch.sh 122880`,
    timeout 300 s; the autonomous protocol, QWEN_MODES.md §3). The model is
    back on the turn after the reload; this session's transcript (≈10–15k
    tokens) fits 122880, fit guard passes without `--force`.
  - **Owner directive: update BOTH json configs** — `qwen-switch.sh` does both
    automatically: `~/.pi/agent/models.json` (ninfer-27b `contextWindow` →
    122880) + `/home/goblin/ScriptEngine/opencode.json` (ninfer-27b
    `limit.context` → 122880). The ninfer-35b provider (229376) is untouched.
    VERIFY both files after the switch.
  - **Campaign state unchanged: Creator Research (opencode, outside the repo)
    — full resume state in `/home/goblin/Creator Research/HANDOFF.md`** (§6:
    finish the candidate analysis w/ india-free keywords + 12-worker capped
    parallel scan). CSM parked (Phase 1 at the extraction-gated floor, D23
    `407c016`; JJK baseline 100%).
  - **Clean commit sha:** below (this checkpoint).
  - **FIRST ACTION ON RESUME / POST-FLIGHT:** (1) `cat
    /home/goblin/ninfer-work/qwen_mode.txt` (expect mode=122880 ctx=122880,
    api=off, free ≈ 6.2 GB); (2) `nvidia-smi` (Qwen only on the card); (3)
    verify BOTH json files now read 122880 (models.json ninfer-27b +
    opencode.json ninfer-27b); (4) continue whatever work the owner points at
    (Creator Research HANDOFF §6 if none).
- **2026-09-13 ~15:3x (owner-directed: 262k → 170k, NEW opencode session — Creator Research campaign continues; CSM parked):**
  - **Mode: 262k (ctx 262144) → 170k (ctx 174080, raw-token dial-down).** Pre-switch
    card state: `qwen_mode.txt` = `mode=262k ctx=262144 qwen_pid=65114 api=off
    free_mib=1613`; `:8000` off, no extraction in flight. The 170k profile is
    auto-generated (`serve_ctx_174080.sh` from the serve.sh template, kv=174080,
    expected headroom ≈ 5 GiB). Switch: `qwen-switch.sh 174080 --force`
    (fit guard trips on the stale 09-13 pi transcript ≈293k tokens > 174080;
    force is safe — this commit is the full checkpoint).
  - **This is an OPENCODE session, not pi** — the in-flight turn dies
    mid-reload (expected). The owner continues in a **NEW opencode session**
    (owner directive 15:3x: "continue this experiment in a new session").
  - **Campaign: Creator Research (outside the repo) — full resume state in
    `/home/goblin/Creator Research/HANDOFF.md` (§6, updated this session).**
    CSM parked (Phase 1 at the extraction-gated floor; JJK baseline 100%).
  - **Done in this opencode session (all on disk, none in the transcript):**
    (1) 262-creator mapping analyzed (online `Analysis_262` tab);
    (2) 15-day reel+brand research: all 218 IG creators (905 in-window reels,
    371 brand rows) + 44 YT-only creators (47 uploads) — online campaign
    sheet `1JScUInkANwXKZTEXhbnzh2taafraTXRiz-0Wud3_59Y`;
    (3) expansion discovery wave 1: 8 accepted creators; new sheet
    **"Expansion Creators Reels 15D & Brands (2026-09-13)"**
    (`1dk6VUjeYW49kp3Y_SUAEhN4usM6l65KVTJlWXoK2Lgw`, Creator folder) with 21
    in-window reels / 2 brand rows / per-creator summary;
    (4) parallel-worker experiment: `reel_parallel.py` (per-reel CDP workers,
    1 persistent tab each; 16-worker wall ~29 s; 32-worker runs degrade IG
    hydration → data-quality recipe = 12 workers × up to 3 passes with a 24 s
    hydration poll; **hard cap MAX_TABS=12 + end-of-job tab cleanup** per
    owner rules "reduce the limit / PC is lagging").
  - **EXACT NEXT STEPS (new session, in order):** (1) read
    `/home/goblin/Creator Research/HANDOFF.md` §6; (2) launch Brave (CDP
    `--remote-debugging-port=9222 --remote-allow-origins=*`, wipe session-
    restore files first to avoid window duplication); (3) **finish the
    candidate analysis of the mapping sheet**: discovery with `india` removed
    from the search keywords (owner rule 15:0x — "don't search india, it will
    most probably show you indian shorts already"), 4-worker discovery
    (expand_driver.py, per-worker state files), then `reel_parallel.py` scan
    of all accepted expansion creators (12-tab cap), merge + sheet
    consolidation; (4) report the final per-category coverage
    (targets: Tech 16, C&E 30, H&B 31, Business 38, Other 41, Entertainment 48
    still short of 50).
  - **Open risks:** IG checkpoint wall (abort → owner re-login in Brave);
    OpenCLI bridge drops when the daemon restarts (restart Brave to
    reconnect); Brave session-restore respawns stale windows (wipe
    `Sessions/` while stopped).
  - **Clean commit sha:** below (this checkpoint).
- **2026-09-13 ~04:5x (owner-directed: 100k → 262k full-context switch, OPENCODE session — Creator Research work; CSM parked):**
  - **Mode: 100k (ctx 102400) → 262k (ctx 262144), "full context".** Pre-switch
    card state: Qwen 100k pid 108527 (up ~7 min, **serving this opencode
    session**), `:8000` on CUDA pid 53671 (up ~91 min), GPU 25,783/32,607 MiB
    used @100 % util. `qwen_mode.txt` was STALE (`mode=off` @04:46:42); the
    03:23 100k switch's bash script (pid 53669) sat stuck in `do_wait` 91 min
    @0 % CPU — killed before this switch (its :8000 child is in its own
    session and survived).
  - **This is an OPENCODE session, not pi** — the in-flight opencode turn dies
    mid-reload (expected; same as the 03:4x entry). The opencode process
    survives; the owner resumes with `opencode -c` (or `-s <id>`). Fit guard:
    262k is the max ctx and the opencode session is not a pi session; if the
    newest pi transcript still trips the guard, `--force` is safe (this commit
    is a full checkpoint; the opencode session auto-compacts on
    context_length_exceeded).
  - **Campaign: PARKED, nothing pending.** CSM Phase 1 §9a closure loop DONE
    (halted at the extraction-gated floor, D23 `407c016`); JJK baseline 100 %.
  - **Active work (opencode session, outside the repo):** the online
    Google-sheet reorg — state + re-run recipe in
    `/home/goblin/Creator Research/HANDOFF.md` §5 (Instagram values written;
    `mergeCells` 400 fix pending: drop the `"fields"` key; the other 5 tabs
    untouched; scans in `/tmp/scan_<tab>.json`).
  - **Clean commit sha:** below (this checkpoint). Switch: `qwen-switch.sh 262k
    --api` (262k exploratory: ~3.4 GiB headroom → `:8000` lands on CPU;
    `--force` only if the fit guard trips).
  - **FIRST ACTION ON RESUME (opencode -c):** (1) `cat
    ~/ninfer-work/qwen_mode.txt` (expect mode=262k ctx=262144, api=cpu, free
    ≈ 3.4 GB); (2) `nvidia-smi` (Qwen only on the card); (3) `curl -s
    localhost:8000/health` (expect device=cpu); (4) tail this file's switch log
    for the machine line; (5) HANDOFF.md §5 → finish the sheet reorg.
- **2026-09-13 ~03:4x (owner-directed: 262k → 100k, OPENCODE session — Creator Research work; CSM parked):**
  - **Mode: 262k (ctx 262144) → 100k (ctx 102400).** Pre-switch card state: qwen
    pid 23351, 30,673 MiB used / 1,430 MiB free; `:8000` up on CPU (pid 23419);
    no extraction in flight (the script refuses anyway while an
    events-extract batch holds the card).
  - **This is an OPENCODE session, not pi** — opencode runs on this same Qwen
    server, so the in-flight turn dies mid-reload (expected; the script header
    says never switch inside an agent session). The opencode process survives;
    the owner resumes with `opencode -c` (or `-s <id>`). If the fit guard
    refuses on a stale pi session file (the 09-13 02:33 pi transcript, ~150k
    est. tokens), `--force` is safe: this commit is a full checkpoint and the
    opencode session auto-compacts to 100k on overflow.
  - **Campaign: PARKED, nothing pending.** CSM Phase 1 §9a closure loop DONE
    (halted at the extraction-gated floor, D23 `407c016`); Phase 2 unstarted;
    JJK baseline at 100%. HEAD `aada154` + this checkpoint commit.
  - **Active work (opencode session, outside the repo) — read
    `/home/goblin/Creator Research/HANDOFF.md` first:** §2 a–c fixed (Tech-sheet
    second/third tables, dedupe pop bug + min-7 1-to-1 prefix rule) and
    `Creator_Mapping.xlsx` formatted (262 creators, 8 categories, colored
    headers, content-based widths, zebra, tab colors); §3 WriterAgent 0.8.75
    installed (`~/.config/libreoffice/4/user/`), Qwen endpoint pre-configured in
    `writeragent.json` (`mcp.mcp_enabled=true`, :18765); opencode MCP entry
    `writeragent` in `~/.config/opencode/opencode.jsonc`.
  - **OPEN ISSUE at switch time:** the WriterAgent MCP server never bound
    :18765 under the LO 26.8 deb build (`~/Applications/LibreOffice`, python
    bootstrap warning "Could not find platform independent libraries" → the
    extension's Python never bootstrapped, no writeragent_debug.log). Next step
    queued: try the system LO 24.2 (`/usr/bin/soffice`) with the xlsx open and
    poll :18765; if it still doesn't bind, check LO's python loader next.
  - **Clean commit sha:** below (this checkpoint). Switch: `qwen-switch.sh 100k
    --api` (100k service profile: ~7-8 GiB headroom → `:8000` co-locates on
    CUDA; `--force` only if the fit guard trips on the stale pi transcript).
  - **FIRST ACTION ON RESUME (opencode -c):** (1) `cat
    ~/ninfer-work/qwen_mode.txt` (expect mode=100k ctx=102400, api=cuda, free
    ≈ 7 GB); (2) `nvidia-smi` (Qwen only on the card); (3) `curl -s
    localhost:8000/health` (expect device=cuda); (4) tail this file's switch log
    for the machine line; (5) continue the open MCP issue above.
- **2026-09-13 ~02:5x (owner-directed: 100k → 262k full-context switch, then Creator Research work):**
  - **Mode: 100k (ctx 102400) → 262k (ctx 262144).** Pre-switch card state: qwen
    pid 7760, 6,996 MiB free, `:8000` off, no extraction in flight
    (`pgrep events[-_]extract` empty).
  - **Fit guard: PASSES without FORCE.** Session file 600,029 B ≈ 150,007 est.
    tokens (bytes/4, conservative) < 262144 target.
  - **Processes (verified live):** pi **5378** (serves this session 01a09753)
    ← bash **5364** ← gnome-terminal-server **3432** ⇒ helper args
    old_pi=5378, old_shell=5364. Single pi on the machine.
  - **In-tree before switch:** R-8 fix-class landed + committed at `aada154`
    (wants_chronology_set in chronology.py, router split: set-in-order → roster,
    one-subject order → narrative; 152 router tests green).
  - **Owner directive for after the switch (Creator Research, non-campaign work
    — todos #1–#5 in the session's todo panel):** (1) make a "Creator Research"
    working folder OUTSIDE the ScriptEngine repo; (2) map creators by
    niche/category from three sources — Google sheet 1 (id
    `1-zkuoTRLIEfkDJk1SWfW2WfOwlt15nZTD6aSLDMgupc`, public, already fetched to
    `/tmp/sheet1.xlsx`), Google sheet 2 (id `19G2vQFv6tV0oUQ4F6CSRcIZUXBm4bCM5xcW0WgRBOHs`,
    behind Google sign-in → fetch through the OpenCLI browser bridge on the
    user's Brave session, profile `m4e85p8v`; opencli `download` step forwards
    browser cookies to the `/export?format=xlsx` URL), and the local
    `/home/goblin/Downloads/Finnet Media Exclusive Roster .xlsx`;
    (3) build one new Excel sheet of the category mapping (LibreOffice already
    installed at /usr/bin/libreoffice; openpyxl in venv /tmp/xlsxenv). The
    opencli instagram `user` adapter is locally overridden (works via rendered-
    grid fallback; `~/.opencli/clis/instagram/user.js`, undo = rm the dir).
  - **Clean commit sha:** `aada154` (this checkpoint).
  - **FIRST ACTION ON RESUME (new pi, same session):** post-flight — (1) status
    line shows the new window (`/262k`); (2) `cat
    /home/goblin/ninfer-work/qwen_mode.txt` (expect ctx=262144, api=off, free
    ≈1.5 GiB); (3) `tail /tmp/switch_restart3.log` (part3 answered, new pi pid,
    old pi gone, relaunch_term done); (4) `pgrep -P 3432` — only the new pi's
    window remains. THEN, per owner directive, proceed straight into Creator
    Research todos #1–#5 (do not stop and wait).
- **2026-09-12 02:4x (owner-directed: 262k → 120k mode switch — switchpoint BEFORE the 3-part flow):**
  - **Mode: 262k → 120k (ctx 122880).** Pre-switch card state: ninfer pid 7190 on the
    262k profile (30,344 MiB used / 1,533 MiB free), `:8000` off. `qwen-switch.sh
    122880 --api` generates `serve_ctx_122880.sh` from the `serve.sh` template
    (kv=ctx, no --vision). Expected headroom ≈ 6.3 GB → `:8000` should land on
    CUDA (the --api headroom rule decides; 100k-era precedent = CUDA).
  - **Fit guard: PASSES without FORCE.** This session file 77,336 B ≈ 19.3k est.
    tokens (conservative bytes/4) << 122880 target. No extraction in flight
    (`pgrep events[-_]extract` empty).
  - **Processes (verified live, 02:4x):** single pi = **7263** (serves this
    session 01a09247, started under 262k). Window chain: gnome-terminal-server
    3394 → bash **3406** → pi 7263 ⇒ helper args old_pi=7263, old_shell=3406.
  - **Campaign position UNCHANGED by this switch** (work parked since the
    2026-09-10 power loss): CSM Phase 1 after P1.2 — R-5 closed + committed
    (`ec60587`/`35c16c9`/`3ee6bd0`), census v2 authored + committed
    (`60e568f`), **R-7 in-tree but UNGATED** (owes gates + stamps + its own
    commit), miss queue 38 open / 20 closed of 58. R-6/P1.3/P1.4/Phase 2
    unstarted. Restart ritual unchanged: READ
    `reports/master-work/POWER_CHECKPOINT.md` FIRST, then
    `reports/master-work/HANDOFF_STATE.md`.
  - **Clean commit sha:** below (this checkpoint). Switch helper (agent's last
    act, detached): `setsid nohup bash tools/master-work/switch_restart3.sh
    122880 <session_file> 7263 3406 … &`; log `/tmp/switch_restart3.log`;
    `qwen-switch.sh` appends the machine line to the switch log below.
  - **FIRST ACTION ON RESUME (new pi, same session, post-flight per the
    qwen-switch skill):** (1) status line shows the new window (≈ `/120k` —
    this pi is freshly spawned, so its window is trustworthy); (2) `cat
    /home/goblin/ninfer-work/qwen_mode.txt` (expect ctx=122880, free ≈ 6.3 GB,
    api=cuda); (3) `tail /tmp/switch_restart3.log` — part3 LLM answered, new
    pi pid, old pi gone, relaunch_term done; (4) report ONE line + **STOP**.
    Then resume the CSM parked ritual (POWER_CHECKPOINT + HANDOFF_STATE) when
    the owner speaks. Note: any OTHER pi alive before this switch holds a
    stale window snapshot — `exit` + `pi -c` it (none known 2026-09-12).
- **2026-09-10 POWER LOSS — work stopped mid-run. READ
  `reports/master-work/POWER_CHECKPOINT.md` FIRST, then
  `reports/master-work/HANDOFF_STATE.md`.** Phase 1, after P1.2.
  R-5 closed + committed (`ec60587`/`35c16c9`/`3ee6bd0`); miss queue 38 open /
  20 closed. Census v2 authored + committed (`60e568f`) = close-council Q1's
  artifact. **R-7 is in the tree but UNGATED** (same commit, gates not run,
  no queue stamps) — it owes gates + stamps before it counts. R-6, P1.3, P1.4,
  Phase 2 unstarted. Restart ritual: single terminal (A/B bay retired), fresh
  `pi`, read ONLY those two files (lean boot = 23.8% context vs 61.3% verbose),
  rebuild the 8-item todo panel. Qwen + `:8000` will both need restarting —
  verify, never trust the recorded pids.
- **2026-09-09 (CSM Phase 1 under the A/B bay — 262k→100k switch now; drift D20):**
  - **00:5x addendum (directing session pi 53523):** the bay was opened 00:38–00:39
    (tmux `control` = A, `work` = B + `csm-control.sh` monitor) and terminated on
    owner direction — the visible pilot windows would not scroll (tmux `mouse off`
    → the wheel fell through to pi; wheel-up showed the previous prompt in the
    entry field). Fixed at the root: `~/.tmux.conf` `set -g mouse on` (live
    server set as well) + rule lines in the terminal-pilot / ab-bay skills;
    wheel = tmux copy-mode scrollback, `Esc` = live pane. Owner then directed:
    demo 262k→100k switch pair (both inline; session fit 85k est < 102k), then
    re-launch A/B per ab-bay step 5 with the fixed windows.
  - **Owner mandate 2026-09-10 (supersedes the 2026-09-08 "never ask the
    owner to restart" convention):** EVERY context switch = exit the pi
    agent, then relaunch into the same session — the agent never chats
    across a model recycle (the 00:5x inline 100k switch died mid-reload;
    the owner restored 262k by hand, then restarted it). The qwen-switch
    skill made this MANDATORY (commit 8f3b0c5: "the agent always exits, the
    owner relaunches"); `switch_restart.sh` is the only sanctioned path.
    The 262k→100k demo therefore runs: `switch_restart.sh 100k
    /tmp/resume_msg.txt 53523` (my pid; the owner's pi 53686 untouched),
    resume line = stop-and-wait.
  - **Owner directive (this session, 2026-09-09 night):** (1) switch to the
    100k context by reloading ninfer (qwen-switch skill); (2) close this pi
    agent + session as ninfer restarts (pi_restart.sh, grace ≤10 s — the
    owner convention: the agent never asks the owner to restart); (3) come
    back to this session; (4) from here launch the A/B bay — A continuously
    watches every shell B launches, B works. **Phase A is GPU-only for
    shells (owner 2026-09-09 night):** every model-bearing shell runs on
    CUDA; if B's shell is caught on CPU, A stops it immediately and sends
    the standard instruction ("Control A killed your shell (pid …). Re-run
    on GPU: …") — B auto-reruns on CUDA (the 2026-09-07 convention, now
    documented in the ab-bay skill §"The CPU-kill → auto-rerun
    convention"). B works **Phase 1 only** (plan v2.2 P1.1–P1.4).
  - **Phase-boundary gate (owner: "prepare a checking/reviewer that will
    check the phase 1's end, then only will move to phase 2"):**
    `reports/master-work/PHASE1_CLOSE_REVIEW.md` — a fresh-context
    reviewer re-runs the four standing gates on the committed tree +
    verifies every P1.4 close condition + the marker-at-floor; **Phase 2
    starts only on its PASS + the owner's go.** B never starts Phase 2 on
    its own.
  - **State at handoff:** Qwen 262k (pid 3584, ~30.5 GB / ~1.6 GB free),
    `:8000` down, no tmux bay (the 150k-era bay is gone with the reboot).
    CSM = plan `plan/CSM_2PHASE_PLAN.md` **v2.2** (P1 council 14 amendments
    + P2 council 13, ledger #25/#26) is the working plan; the 9-file
    R-2/R-3 package is on disk, uncommitted (its gate legs = P1.1 step 3);
    `/tmp/csm_iter1_records` was lost in the reboot → P1.1 step 1
    (model-free rebuild). Miss queue 58 rows (33 fixable / 22 floors / 3
    stamped); census 39/60 (21 red, extraction-gated floor).
  - **This session's sequence (2026-09-09 night → 09-10 00:3x):** (a)
    ab-bay skill updated with the CPU-kill → auto-rerun convention; (b)
    `reports/master-work/PHASE1_JOB.md` (B's spec) +
    `reports/master-work/PHASE1_CLOSE_REVIEW.md` (the close gate) on disk
    (commit `958ce93`); (c) **the 100k switch was run INLINE from this
    ~400k session (00:1x) and STRANDED it** — the reloaded 100k model
    could not serve it (242k prepared prompt > 102k cap; the auto-compact
    itself did not fit), the turn died, and the restart helper never
    launched. **The owner restored 262k by hand at 00:30**
    (`ninfer-start-262k --force`; qwen pid 53071, free 1607 MiB, `:8000` on
    CPU — current state). Root cause + the fix: the safe order is kill pi
    FIRST, then switch, then relaunch pi — one detached helper
    (`tools/master-work/switch_restart.sh`, new, repo-committed); both
    skills updated (ab-bay step 2; qwen-switch "the switch" + "overflow"
    sections + Never list).
  - **NEXT (this session's final act, scripted):** launch the helper
    detached — `setsid nohup bash tools/master-work/switch_restart.sh 100k
    /tmp/resume_msg.txt $(pgrep -x pi | head -1) < /dev/null > /dev/null
    2>&1 &`. It: kills this pi (grace 5 s) → `qwen-switch.sh 100k --api
    --force` (30–60 s; `:8000` lands on CUDA at 100k per the headroom
    rule) → launches `pi` in tmux `pi-csm` → types the resume line from
    `/tmp/resume_msg.txt` → verifies via capture-pane (log
    `/tmp/switch_restart.log`). The new pi (attach: `DISPLAY=:0 setsid
    gnome-terminal -- tmux attach -t pi-csm`) reads THIS section and opens
    the bay per the ab-bay skill: A boot line (tmux `control`,
    `csm-control.sh` monitor on B's pid, the GPU-only-shell rule, the
    standard kill message), B boot line (tmux `work`,
    `reports/master-work/PHASE1_JOB.md`); the directing session (the new
    pi) stands down and relays.
  - **Next (the new session, in order):** boot A + B per ab-bay step 5 (A
    boot line carries the live-verified state snapshot + the monitor
    launch; B boot line carries the job spec + the contract). B's first
    units: P1.1 step 0 (zero-GPU baseline re-verify) + step 1 (model-free
    rebuild) → A brings `:8000` to CUDA → the four gate legs → C1/C2/C3
    (path-limited adds, `git add .` banned) → P1.2 R-5 wave (council per
    the kept trigger) → P1.3 halt meter (33 fixable only) → P1.4 close +
    marker (floor only) → **the phase-close reviewer gate** → owner go →
    Phase 2 (P2.1 step 0 sanity-100 first — the 51-GPU-h number is
    unmeasured and must not be spent before it).
- **2026-09-09 (Gojo script v2 — ESSENCE-driven; machine powers off at end of that session):**
- **2026-09-09 (Gojo script v2 — ESSENCE-driven; machine powers off at end of this session):**
  - **Gojo script rewritten per owner essence** (`E:\Personal\Plot Works\Video 2 - Gojo\Script\Gojo.md`,
    3,780 w tagged / 3,126 w clean, 56 tags / 30 distinct, verify-clean): dark open
    (the morning the world learns Gojo is sealed — E34 "Pandemonium" facts, no
    fabricated "19 days" number: the corpus's only 19-day fact is the Culling
    Game inactivity rule, Ch 158, used as the slow "days" beat); slow pacing;
    the bad things in between (Toji, Geto's break/kill, Jogo, Shibuya);
    resolution close per owner: "even the strongest, you were overpowered —
    the King beat the title, not the man" (thematic, not literal, per owner's
    "don't take this literally"). Clean companion regenerated.
  - **Standing rule (owner 2026-09-09): for ALL future scripts, ask the owner
    for the ESSENCE before drafting** (opening, pacing, resolution, the
    tragedies in between); offer options when asked; anime scripts pace slowly.
    Implemented in the engine: `scriptengine/api/rules.py` `ESSENCE_RULES`
    (folded into `writing_rules()` → travels with `script-gen` + `/context`),
    + CLAUDE.md working agreement.
  - **Toji script state (owner-directed):** `Toji.md` = the 6,520-word
    Gojo-quote-open version (the one that opened on "since he has no cursed
    energy, I can't read his presence" [E27 14:17]); the "I'm glad." rewrite
    (6,530 w) and all backups deleted on owner instruction — the Script dir
    holds only `Toji.md` + `Toji-clean.md` (5,658 w).
  - Next on the owner's list: nothing pending — **the owner powers the
    machine off at the end of this session** (Qwen 262k + :8000 CPU API die
    with it; the CSM campaign todos below stay parked until the next session).
- **2026-09-08 (Toji script rewrite COMPLETE, owner-directed — drift D14):**
- **2026-09-08 (Toji script rewrite COMPLETE, owner-directed — drift D14):**
  - The owner-directed autonomous rewrite of the Toji Fushiguro script
    (`E:\Personal\Plot Works\Video 1 - Toji\Script\Toji.md`) is done and
    **verify-clean: 104 tags / 29 distinct, every tag checks out against the
    raw wiki** (`cli verify --series jjk`), 6,037 words (was 4,044 / 91 tags;
    ~46 min at 132 wpm — the owner's ~45-min target).
    Method: `humanscope` Mode A structure sheet before drafting, Mode B
    30-feature audit before/after, citation discipline (one tag per
    (chapter, episode) run, tag every sentence on source change), `cli verify`
    before calling it done. Cut the explaining closing (theme-restate
    “in one breath …” paragraph deleted; ending now lands on the
    unexplained afterlife image); removed “not X, it is Y” reframes /
    rule-of-three / -ing-tail / weasel wording; kept plain emotion words.
    Added verbatim citation clusters from the D13 transcript store, then
    expanded to the ~45-min target with sourced material (not padding): a
    full Arsenal section (Split Soul Katana, Inverted Spear of Heaven,
    Chain of a Thousand Miles, the inventory curse, Playful Cloud, the
    broadsword/knives/handgun), a How-he-hunts/tactics section (bounty
    design, the boat-race/Shiu beat, the infiltration, the read-and-counter
    method), deeper mechanics (Physically Gifted, footprint/odor tracking,
    long-fight endurance), the Naobito Dagon beat, and more Geto/Gojo
    dialogue. The 5 key citation clusters: Gojo
    “since he has no cursed energy, I can't read his presence” (cold-open,
    Ch 71/E27); Dagon-fight narrator VO “he had become a murder machine, his
    fangs constantly directed toward the strongest” (Ch 110/E39); Gojo
    “any last words?” (Ch 75/E28); Gojo-to-Megumi “the ultimate card that
    his dad kept on hand against the Zen'in clan” (Ch 79/E29); plus the
    already-woven Toji verbatim lines. Original backed up as
    `Toji.md.orig-20260908-2343` (alongside the file, untracked).
  - **Timestamps added (same session):** all 21 verbatim quotes now carry a
    `[E<n> mm:ss]` timestamp (exact `ts` pulled from `transcripts.db`), so
    the editor can find each line's footage. The JJK0 movie (M1) was already
    imported + embedded with timestamps (D12/D13), but **Toji does not
    appear in it (0 mentions)**, so there are no movie quotes in this script
    (the movie's timestamps are ready for a Yuta/Okkotsu video). No new
    fixing run was needed, so no council (owner fallback). `cli verify`
    still clean (104 tags / 29 distinct); 6,082 words.
- **2026-09-08 (transcript Phase 2 + bay closed + dial-back, owner-directed):**
  - JJK transcript Phase 2 COMPLETE (drift D13, commit `f86ed7a`): all
    **16,226 lines embedded** (separate `series/jjk/qdrant-transcripts/` dir,
    CUDA, BAAI/bge-large-en-v1.5 1024-d, `embed_meta.json` staleness
    marker); CLI doors `transcripts-embed` + `transcript-search` (episode
    filter, stale warnings); `(Movie <name>)` verify branch + 3 tests; plan
    + drift D13. Read doors: `transcript` (time-window) / `dialogue`
    (per-character FTS) / `transcript-search` (semantic).
  - A/B bay CLOSED (~23:3x): machine monitor (csm-control.sh, generalized @
    `c81be85`) + tmux `control` (A) + tmux `work` (B) all killed; visible
    windows gone. Skills: `ab-bay` (new) + `terminal-pilot` (user-level,
    outside repo); `qwen-switch` use-case-3 committed with this checkpoint.
  - Owner directive (this switch): Qwen **100k → 262k** (full context);
    `:8000` → **CPU** (262k steady state, ~3.5 GiB headroom).
- **Next task (owner-authorized):** CSM (Chainsaw Man) campaign — the next
  owner-authorized work after the JJK campaign closed (D11). Live state: see
  the “Campaign todos” section below + `reports/csm/`. (The Toji rewrite
  above was the owner-directed intermission; it is now complete, D14.)
- **Resume / post-switch steps (a fresh session executes these in order):**
  1. `cat /home/goblin/ninfer-work/qwen_mode.txt` (expect mode=262k) +
     `nvidia-smi` (Qwen only on the card, ~25 GB used) +
     `curl -s -m 3 localhost:8000/health` (expect device=cpu).
  2. The owner's pi (this session) is restarted by the owner: fresh `pi` in
     /home/goblin/ScriptEngine, then *Read plan/SWITCHPOINT.md and
     continue from there*.
  3. Read `plan/drift_log.md` §4 (current position) + this file. The Toji
     rewrite is done (D14, verify-clean). Next owner-authorized work is the
     CSM campaign — pick up from the “Campaign todos” section below (Wave-2
     pre-step + the two parallel Wave-2 subs, or whichever the owner points
     at).
- git: the Toji script is untracked (`E:\...` dir is intentionally outside
  git); the plan checkpoint for this session (SWITCHPOINT + drift_log D14)
  is committed. (Previous head before this session: `998c673`.)
- Campaign state: JJK campaign CLOSED (D11, 2026-09-07). CSM campaign =
  next owner-authorized work (CSM-1/1b/2 + councils done; CSM-3 is the next
  unit — see the "Campaign todos" section below + `reports/csm/`).
  Transcript work is campaign-neutral (D12/D13).
- Toji script (D14 addendum 5, same session): the owner corrected the
  cast-list range to cite **Toji's appearance** in each arc (not the arc's
  full span). The inline `[range:]` notes + end-glossary are gone; the
  passage pass is now a **`[covers X-Y]` block after every 3 passages**
  (9 blocks: after passages 3, 6, 9, …, 24, and the lone 25th), each citing
  the distinct events/battles + ch/ep ranges those 3 passages draw on. Toji
  in Gojo's Past = Ch 66-75/Ep 25-28; Toji in Shibuya = Ch 95-113/Ep 35-40.
  `Toji-clean.md` (5,589 words, pure narrative; strips the `[covers X-Y]`
  + `·` lines). Ranges sourced from the wiki's `anime episode` edges in
  `series/jjk/facts.db`, never invented. `cli verify --series jjk` still clean
  (104 tags; the `[covers X-Y]` blocks are a new human-curated format, not
  verify-checked).
- Toji conventions made **permanent in the pipeline** (D15, same session):
  `rules.py` `ANNOTATION_RULES` now states all four conventions (timestamps,
  `[covers X-Y]` after every 3 passages, words-only companion, cite-the-thing
  not-the-arc); `writer.py` always writes `<title>-clean.md` and a
  `ensure_covers_blocks` backstop rebuilds the `[covers]` lines from the tags
  if the model omits them; `docs/SCRIPT_STYLE.md` §6 + a `CLAUDE.md`
  working-agreement quote the rules. 6 new script-gen tests (47 green).

## gpu-gate3 handoff (2026-09-08 — A=01a08064 (fresh CSM session; retargeted from the retired 01a07ff0) → chain → C on 100k → A resume)

**DONE 15:30 local — chain complete (state=done, no STALLED, typed RESUME
15:30:08; C transcript trashed after the report was read; `:8000` back on CPU
via the 262k switch-back, pid 80967, /health device=cpu).** All 4 gates PASS
on CUDA on the 1,249 tree (receipts `reports/csm/GATE_REBASELINE_2.md`):
pytest **1,249/1,249** (the 6 OOM cases pass on GPU) · eval jjk **31/31** ·
span-recall jjk **48,572/48,572** offline + **390/400 (97.5%)** probe · canon
opm **10/16 exact, 236/236, 79.0%**. CLAUDE.md + gates-skill baselines
re-baselined 1,242 → 1,249; the 1,242 `GATE_REBASELINE.md` record is
superseded; the CSM gate section is now open in
`reports/comprehension/GATE.md` as the live record.

**Gate re-baseline, round 2 (council blocker, COUNCIL_csm-1b-2).** The
GATE_REBASELINE record (1,242, git `9e13815`) predates CSM-2's +7 tests
(`42aa296` → suite 1,249): the "JJK baseline" is no longer reproducible and
CSM-3's gate re-verification would start broken. Same tier-2 chain as
gpu-live2: `gpu-handoff.sh --tier2 plan/gpu_gate3.spec` flips 262k→100k,
opens C (visible terminal, fresh 100k pi) which runs the four standing gates
**on CUDA on the 1,249 tree** per `plan/gpu_gate3_task.md` (pytest full —
the 6 VRAM-sensitive `test_context` cases must pass; eval jjk; span-recall
jjk offline + --probe 400 on a CUDA `:8000`; canon opm --skip-eval) →
`reports/csm/GATE_REBASELINE_2.md`, flips back 262k, typed RESUME into A's
window (51286464).

**On resume (the typed RESUME line is my next user message):**
1. Read `reports/csm/GATE_REBASELINE_2.md` (C's 1,249-tree re-baseline).
2. Restore `:8000` to CPU (C leaves it on CUDA; 262k co-location rule).
3. Check chain state: `reports/master-work/gpu_handoff_state/gpu_gate3.
{log,stalled,typed}` + `/tmp/gpu_gate3_chain.log`; a `STALLED` flag =
   inspect, then replay the same setsid line (gates are idempotent).
4. Trash C's transcript (`…/gpu_handoff_state/c_session`) — only AFTER
   reading the report.
5. Rewrite the CLAUDE.md + gates-skill baselines (1,242 → 1,249 + run
   timestamps; the record's 1,242 line is superseded), open the CSM gate
   section in `reports/comprehension/GATE.md` as the live record (council
   peer-C finding: the campaign's designated live gate record did not exist),
   commit — then start **CSM-3** (item 3 scope + the addendum in
   `reports/csm/COUNCIL_csm-campaign.md`).

## gpu-live2 handoff (2026-09-08 — A=01a07ff0 → chain → C on 100k → A resume)

**DONE 13:57 local — chain complete (state=done, no STALLED; C transcript
trashed after the report was read; `:8000` back on CPU, pid 62983).** All 4
gates PASS on CUDA (receipts `reports/csm/GATE_REBASELINE.md`):
pytest **1,242/1,242** (the 6 OOM cases pass on GPU) · eval jjk **31/31** ·
span-recall jjk **48,572/48,572** offline + **390/400 (97.5%)** probe ·
canon opm **10/16 exact, 236/236, 79.0%**. CLAUDE.md + the gates skill
baseline updated with these numbers + run timestamps (the 1,239-vs-1,242
stale pair is resolved: the suite is 1,242).

Second live run of the gpu-handoff chain (docs/ops/PC_GPU_HANDOFF.md):
`gpu-handoff.sh --tier2 plan/gpu_live2.spec` flips 262k→100k, opens C
(visible terminal `GPU-gpu_live2`, fresh 100k pi) which runs the
**standing-gates re-baseline** per `plan/gpu_live2_task.md` (pytest full on
CUDA incl. the 6 OOM cases, eval jjk, span-recall jjk offline + --probe 400
on a CUDA :8000, canon opm --skip-eval) → `reports/csm/GATE_REBASELINE.md`,
flips back 262k, and the gated typer types the resume line into A's window
(51768426). A sits idle at its prompt meanwhile (frozen context, zero cost).
Context: CSM-1b (owner directive 2026-09-08) is DONE + committed — bank
validation + 4 in-place gold fixes + relations runner + 4 numbered engine
gaps (G-CSM-1..4); the gate re-baseline moved to this side session (owner
correction: 262k holds the card → 100k+CUDA, never CPU fallback).

**On resume (the typed RESUME line is my next user message):**
1. Read `reports/csm/GATE_REBASELINE.md` (C's re-baseline).
2. Restore `:8000` to CPU (C left it on CUDA; 262k co-location rule —
   headroom 1,604 MiB < 6 GiB).
3. Check chain state: `reports/master-work/gpu_handoff_state/gpu_live2.{log,stalled,typed}`
   + `/tmp/gpu_live2_chain.log`. A `STALLED` flag = inspect, then replay:
   `setsid nohup bash tools/master-work/gpu-handoff.sh --tier2 plan/gpu_live2.spec >/dev/null 2>&1 &`
   (gates are idempotent).
4. Trash C's transcript (`reports/master-work/gpu_handoff_state/c_session`)
   — only AFTER reading the report (deleting it earlier poisons the
   switch-back fit guard).
5. Update CLAUDE.md's stale gate values with the re-baselined numbers + run
   timestamps (the 1,239 vs 1,242 self-contradiction), commit, then resume
   **CSM-2** (scoreboard/classification, council item 2 — its grounding data
   is in `plan/SWITCHPOINT.md`'s CSM-1b todo note / `reports/csm/`).

## gpu-live1 handoff (2026-09-08 — A=01a07f33 → chain → C on 100k → A resume)

First LIVE run of the gpu-handoff chain (docs/ops/PC_GPU_HANDOFF.md):
`gpu-handoff.sh --tier2 plan/gpu_live1.spec` flips 262k→100k, opens C
(visible terminal `GPU-gpu_live1`, fresh 100k pi) which runs the JJK gate
baseline per `plan/gpu_live1_task.md` (→ `reports/master-work/GPU_LIVE1_REPORT.md`),
flips back 262k, and a gated plain-shell typer types the resume line into A's
window (50331658). A sits idle at its prompt meanwhile (frozen context, zero
cost). Engine was untouched by today's MASTER_WORK deploy, so the baseline
should hold (eval 31/31, span-recall 100%); a deviation is a real signal.

**On resume (the typed RESUME line is my next user message):**
1. Read `reports/master-work/GPU_LIVE1_REPORT.md` (C's baseline).
2. Restore `:8000` to CPU (C left it on CUDA; 262k co-location rule —
   headroom 3.5 GiB < 6 GiB).
3. Check chain state: `reports/master-work/gpu_handoff_state/gpu_live1.{log,stalled,typed}`
   + `/tmp/gpu_live1_chain.log`. A `STALLED` flag = inspect, then replay:
   `setsid nohup bash tools/master-work/gpu-handoff.sh --tier2 plan/gpu_live1.spec >/dev/null 2>&1 &`
   (gates are idempotent).
4. Trash C's transcript (`reports/master-work/gpu_handoff_state/c_session`)
   — only AFTER reading the report (deleting it earlier poisons the
   switch-back fit guard).
5. CSM resume remains on hold (owner-paused; the stuck session 01a07cab
   resumption is a separate, later flip).

## Campaign todos (live list — every CSM session rebuilds its todo panel from this section and syncs it back after each status change; the panel is per-session volatile state, disk is the tiebreaker)

- [x] 0. Wave-0 tier-0 reachability — 439→0 unreachable, span-recall csm rc=0 (record only; 6-word floor note in the audit)
- [x] 1. Seed-bank inventory + revid-stamp (CSM-1 — `064093e`)
- [x] 2. Classify every CSM page type + generalize the scoreboard (CSM-2 — `42aa296`; 14 unknowns resolved, JJK output byte-identical)
- [x] Standing-gate re-baselining ×2 — gpu-live2 (`GATE_REBASELINE.md`, 1,242) + gpu-gate3 (`GATE_REBASELINE_2.md`, 1,249; CLAUDE.md + gates-skill baselines updated, `2c80867`)
- [x] 3. D5 measurement infrastructure (CSM-3 — `f93d396`: pinned hashed panel + held-out split, csm panel pinned hash e3d73720… (17,181 + 200); wired (title,sentence) resume, jsonl rewritten; full-denominator hit_rate; three doors + --sanity dead-door halt; tier-0 rename `chunk-containment` (alias kept); <6-word floor recorded (775-line census, exclusion stands); pytest 1,253)
- [x] 3b. CSM-3b post-council (COUNCIL_csm-3 Rulings 1/7): roster-door fix (`served_text` flattens members/passages; member names = returned docs; roster-shaped test) + panel-hash recompute/enforce (exit 1) + bare-list held-out load + named consumer (`tools/csm/panel_heldout.py`) — `bc73795` (close-out: exit-code recheck + JJK tier-0 unchanged + commit, wave 1 fresh 100k B session 2026-09-08); standing gates + 39-question seed bank receipt (worker 2 gates, worker 3 close-out): `reports/csm/CSM3B_GATES.md` @ `78b5cf3`
- [ ] 4. D5 exhaustive tier-1 × 3 doors (**PHASE 2 — extraction**; GPU-h pending measured s/probe — sanity runs measure it first, COUNCIL_csm-3 Ruling 4; batched via the gpu-handoff chain in Qwen quiet windows, smaller dial if VRAM demands; standing 400-probe gate stays)
- [x] 5. Phase-0 remainder (**PHASE 1 — Wave 2, sub 4 — DONE** `waveB_csm5_remainder.md`: 5.3 CSM fixtures / 5.5 no-LLM-judge generator-sliced gold + held-out declaration / 5.4 door-first pre-check (zero GPU; the 34 s one-copy 5.4 re-adjudication ran at the P1.4 close, `reports/csm/receipts/census_5_4_readjudication_p14.md` — 21/21 reds identical to 09-09, 0 closed, no de-scope) / §13 awareness line / the twenty-failures set (`waveA_twenty_failures_author.md`))
- [x] 6. D6 oracle + bounded instrument (**PHASE 1 — instrument half DONE** `waveB_csm6_instrument.md` + census authoring (`3dbc3ef` v2 50-item; v1 60-item bank): CSM dimension map, frozen census sets (seeded + revid-stamped, D4 fresh-context authored), T0 pilot 843/843, cross-page census 10,889/11,261; **PHASE 2 — extraction half** pending: P2.3 D6 extraction, only on the 21 red dimensions (floor stands post 5.4 re-adjudication))
- [x] 7. §9a closure loop (D1–D6; **PHASE 1 iteration 1 DONE** — one class per fix, never reword to pass: R-1 router / R-2 passage-leg / R-3 roster-scoping / R-5 relations / R-6 subject_aliases / R-7 identity_fields all green; halt-meter converged `407c016` (D23: 35 open = 22 floor + 13b + 0c; halt condition met, no regression / no no-reduction iterations fired))
- [ ] 8. Done-declaration + pilot memo (**PHASE 2**; pasted raw output + the four pilot numbers; JJK baseline diff-empty; halt before P6)
- Standing items (whole campaign): council every 2–3 todos — **one agent at a time** (owner rule 2026-09-08); raw receipts, never "100%" prose; `coverage_report` regenerated after every commit; the four standing gates before any pass is declared done; per-wiki handling in `series/csm/overrides.yaml` / `tools/csm/` only; JJK baseline untouched; **Phase 1 (owner rule 2026-09-08): all model/GPU work on CUDA at the 100k dial (live CSM dial since the P1.1 boundary; the 150k draft was superseded per council #24/#25), no CPU shell command >15 s, 2-subagent waves; the gpu-handoff switching plan is Phase 2 only**.

## Switch log (machine-appended by qwen-switch.sh)

- (none yet)- 2026-09-07T22:05:09+05:30 qwen-switch: ctx=102400 (mode 100k), api=off, free=8988MiB
- 2026-09-07T22:17:58+05:30 qwen-switch: ctx=102400 (mode 100k), api=cuda, free=8986MiB
- 2026-09-07T22:19:34+05:30 qwen-switch: ctx=102400 (mode 100k), api=cuda, free=8986MiB
- 2026-09-07T22:53:45+05:30 qwen-switch: ctx=262144 (mode 262k), api=cpu, free=3513MiB
- 2026-09-07T23:32:51+05:30 qwen-switch: ctx=102400 (mode 100k), api=cuda, free=9002MiB
- 2026-09-08T10:14:37+05:30 qwen-switch: ctx=135168 (owner manual +--vision; profile = serve_ctx_135168.sh), api=cpu, free=5575MiB
- 2026-09-08T12:51:22+05:30 qwen-switch: ctx=102400 (mode 100k), api=cuda, free=7072MiB
- 2026-09-08T12:56:08+05:30 qwen-switch: ctx=262144 (mode 262k), api=cpu, free=1604MiB
- 2026-09-08T13:47:15+05:30 qwen-switch: ctx=102400 (mode 100k), api=cuda, free=6932MiB
- 2026-09-08T13:56:00+05:30 qwen-switch: ctx=262144 (mode 262k), api=cpu, free=1488MiB
- 2026-09-08T15:18:32+05:30 qwen-switch: ctx=102400 (mode 100k), api=cuda, free=6699MiB
- 2026-09-08T15:29:18+05:30 qwen-switch: ctx=262144 (mode 262k), api=cpu, free=1202MiB
- 2026-09-08T16:50:27+05:30 qwen-switch: ctx=150000 (mode 150000), api=cpu, free=5182MiB
- 2026-09-08T17:37:25+05:30 qwen-switch: ctx=102400 (mode 100k), api=off, free=6820MiB
- 2026-09-08T18:30:37+05:30 manual (worker 3): CSM-3b gate cycle complete — worker 2 (gates-bank-cuda) froze at 18:20, worker 3 close-out @ `78b5cf3`; 4 standing gates = 15:22–15:26 re-baseline (pytest 1,254 / eval jjk 31/31 / span-recall jjk 48,572+390/400 / canon opm 10/16·236/236·79.0%); seed bank no new FAILs (G-CSM-1/G-CSM-2 persist); heldout sanity-4 4/4 HIT (Ruling-7 green); F-CSM-3b-1 (ledger sidecar shared per series, not per panel) recorded for the council
- 2026-09-08T19:05:00+05:30 manual (orchestrator): council CSM-3b complete (workflow 5dcd56b8, 11 sequential agents, one-agent-at-a-time per owner rule) — record `reports/csm/COUNCIL_csm-3b.md` + artifacts `reports/csm/council_csm-3b/` @ `ccd4523`; **verdict: RATIFY the CSM-3b close**; rulings R-CSM3B-1..7 on disk; ledger row #20 in `reports/comprehension/COUNCIL_HISTORY.md`; GATE.md Phase-2 pre-flight lines (R-CSM3B-6) + self-contained receipt header (R-CSM3B-7) same commit; next = Wave 2 pre-step (R-CSM3B-2 F1 ledger fix + R-CSM3B-3 live roster probe, sequential, orchestrator-graded) → the two parallel Wave-2 subs (CSM-6 instrument + CSM-5 remainder) → §9a closure loop iteration 1
- 2026-09-08T19:45:00+05:30 manual (orchestrator): Wave-2 pre-step GRADED PASS (live interleaved 2-panel survival: pinned 168->172 + heldout 9->13, both keyed ledgers retain their own rows, all stamped cuda+commit+panel_hash; log /tmp/prestep_grade.log) + pre-step committed; F1 (R-CSM3B-2) and roster probe (R-CSM3B-3: 31/88 members, 16,231 chars, 0 pre-fix) closed; next = deploy the 2 parallel Wave-2 subs (CSM-6 instrument + CSM-5 remainder + R-CSM3B-4 pre-checks) -> §9a closure loop iteration 1
- 2026-09-08T21:47:43+05:30 qwen-switch: ctx=262144 (mode 262k), api=cpu, free=1464MiB
- 2026-09-08T22:41:06+05:30 qwen-switch: ctx=102400 (mode 100k), api=cuda, free=6967MiB
- 2026-09-08T23:35:06+05:30 qwen-switch: ctx=262144 (mode 262k), api=cpu, free=1486MiB
- 2026-09-09T01:53:56+05:30 qwen-switch: ctx=150000 (mode 150000), api=off, free=5397MiB
- 2026-09-09T22:03:52+05:30 qwen-switch: ctx=262144 (mode 262k), api=off, free=1563MiB
- 2026-09-09T23:29:19+05:30 qwen-switch: ctx=262144 (mode 262k), api=off, free=1606MiB
- 2026-09-10T00:29:26+05:30 qwen-switch: ctx=102400 (mode 100k), api=cuda, free=7077MiB
- 2026-09-10T00:30:38+05:30 qwen-switch: ctx=262144 (mode 262k), api=cpu, free=1607MiB
- 2026-09-10T00:37:25+05:30 qwen-switch: ctx=102400 (mode 100k), api=cuda, free=7084MiB
- 2026-09-10T00:52:47+05:30 qwen-switch: ctx=262144 (mode 262k), api=cpu, free=1610MiB
- 2026-09-10T00:54:16+05:30 qwen-switch: ctx=262144 (mode 262k), api=off, free=1610MiB
- 2026-09-10T00:58:08+05:30 qwen-switch: ctx=102400 (mode 100k), api=cuda, free=7080MiB
  - **01:0x (owner-directed):** 100k→262k return switch via the same
    `switch_restart.sh` helper (resume line = report 262k state to the owner,
    then stop). Helper bug fixed + committed (new-pi detection was `head -1`
    = oldest surviving pi → typed into the owner's pi; now `sort -n | tail -1`
    = newest = the spawned one).
- 2026-09-10T01:01:47+05:30 qwen-switch: ctx=262144 (mode 262k), api=cpu, free=1610MiB
  - **01:0x (helper hardening, commit pending→done):** two latent defects
    found via the 01:01 262k run — (a) the "new pi pid" log label raced the
    pane's spawn (pgrep before exec) and printed the owner's pi 53686;
    (b) the fixed 12 s pre-type sleep lost the TUI race both times, so the
    typed resume line was swallowed and the owner had to type the first
    message that landed. Fix: label from the pane pid (wait comm=pi) + poll
    for the TUI status line (model name) before typing. Next switch's
    resume line should land unassisted.
  - **01:1x (owner ruled the 262k return FAILED — "context is still 102k"):** root cause — the /102k the owner saw was the owner's OWN terminal pi (53686, started 00:38:31 in the 100k era), not the helper-restarted pane pi. pi snapshots the model's contextWindow at startup and never re-reads `models.json`, so any pi alive before a switch keeps the old window in memory (status line + auto-compact threshold). The pane pi (restarted 01:01:47) had shown /262k all along (capture-pane proof 01:02:07: `8.1%/262k`). Fixes (all committed): (1) `switch_restart.sh` now prints `WARNING: stale pi(s) on the pre-switch window` (pgrep diff — every pi that survived the switch holds the old window and needs a manual `exit` + `pi -c`); (2) qwen-switch skill: new "The window is per pi-process" section + a Never item; (3) per the owner's order ("fix this issue, update your skill, then restart") the helper flow was re-run (262k re-switch, same session, fully self-contained). The owner's 53686 stays a manual owner step: `exit` + `pi -c` in the project dir.
- 2026-09-10T01:11:16+05:30 qwen-switch: ctx=262144 (mode 262k), api=cpu, free=1608MiB
  - **01:2x (owner's new idea — the model-driven switch flow, TRIED this turn):** "when you switch and see the model loaded, send a call to the llm through that shell; that call tells the model to terminate this shell and restart the pi agent." Implemented as `tools/master-work/switch_restart2.sh <mode> <old_pi_pid>` + `tools/master-work/relaunch_pi.sh <old_pid> <resume_msg>`: (1) the detached switch shell switches Qwen and waits for the model to load — the pi agent STAYS ALIVE through the switch (requires the session to fit the target context; a not-fitting down-switch stays on the legacy kill-first `switch_restart.sh`); (2) the shell types an LLM call into the directing pane (tmux send-keys) instructing the model to (a) pkill the switch shell, (b) launch `relaunch_pi.sh` (grace-kill self → tmux relaunch → TUI-ready poll → typed resume line → capture-pane proof); (3) the model executes the call with its own tools and ends its turn — it dies at the grace by design; (4) the switch shell waits bounded (600 s) for the pkill, else self-exits. The model (not a blind bash loop) does the restart. First live try: 262k re-switch, directing pid 56461, launched ~01:2x.
- 2026-09-10T01:18:01+05:30 qwen-switch: ctx=262144 (mode 262k), api=cpu, free=1609MiB
  - **01:2x (owner: "model reloads in 3-7 s, why wait this long — show a perfect 100k"):** tightened relaunch_pi.sh (GRACE 5->2 s, TUI poll 2 s->1 s, post-resume blind sleep 8 s->2 s — the slow parts were my sleeps, not the model) + made the LLM-call text mode-agnostic. Re-running the model-driven flow for a REAL mode change 262k->100k (:8000 lands on CUDA per the headroom rule), directing pid 56926 (session ~4k tokens, fits 100k). Target: whole switch ~10-20 s wall, verified by capture-pane, zero owner input.
- 2026-09-10T01:21:08+05:30 qwen-switch: ctx=102400 (mode 100k), api=cuda, free=7081MiB
- 2026-09-10T01:36:52+05:30 qwen-switch: ctx=262144 (mode 262k), api=cpu, free=1610MiB
- 2026-09-10T01:42:55+05:30 qwen-switch: ctx=102400 (mode 100k), api=cuda, free=7060MiB
- 2026-09-12T02:29:15+05:30 qwen-switch: ctx=262144 (mode 262k), api=off, free=1535MiB
- 2026-09-12T02:34:50+05:30 qwen-switch: ctx=122880 (mode 122880), api=cuda, free=6303MiB
- 2026-09-13T02:00:23+05:30 qwen-switch: ctx=102400 (mode 100k), api=off, free=6996MiB
- 2026-09-13T02:34:53+05:30 qwen-switch: ctx=262144 (mode 262k), api=cpu, free=1437MiB
- 2026-09-13T03:23:02+05:30 qwen-switch: ctx=102400 (mode 100k), api=cuda, free=6902MiB
- 2026-09-13T04:57:03+05:30 qwen-switch: ctx=262144 (mode 262k), api=cpu, free=847MiB
- 2026-09-13T14:15:33+05:30 qwen-switch: ctx=262144 (mode 262k), api=off, free=1534MiB
- 2026-09-13T15:15:08+05:30 qwen-switch: ctx=262144 (mode 262k), api=off, free=1613MiB
- 2026-09-13T15:31:47+05:30 qwen-switch: ctx=174080 (mode 174080), api=off, free=4539MiB
- 2026-09-14T03:11:11+05:30 qwen-switch: ctx=174080 (mode 174080), api=off, free=4293MiB
- 2026-09-16T22:26:58+05:30 qwen-switch: ctx=122880 (mode 122880), api=off, free=6279MiB
- 2026-09-17T09:25:43+05:30 qwen-switch: ctx=102400 (mode 100k), api=cuda, free=6928MiB
- 2026-09-17T09:38:40+05:30 qwen-switch: ctx=262144 (mode 262k), api=cpu, free=1477MiB
- 2026-09-17T09:39:53+05:30 qwen-switch: ctx=174080 (mode 174080), api=cpu, free=4503MiB
- 2026-09-17T09:41:12+05:30 manual: :8000 restarted on cpu after qwen-switch left it down (same-device restart defect)
- 2026-09-17T10:37:49+05:30 qwen-switch: ctx=174080 (mode 174080), api=cpu, free=4393MiB
- 2026-09-17T11:05:22+05:30 qwen-switch: ctx=174080 (mode 174080), api=cpu (restarted by hand after), free=4493MiB
- 2026-09-17T18:29:08+05:30 qwen-switch: ctx=174080 (mode 174080), api=cpu (restarted by hand after; Qwen had been down since ~13:30, a 14:16 170k-window start failed on VRAM), free=4508MiB
- 2026-09-17T19:54:24+05:30 qwen-switch: ctx=102400 (mode 100k), api=cuda, free=6974MiB
- 2026-09-18T22:28:45+05:30 qwen-switch: ctx=262144 (mode 262k), api=off, free=1746MiB
- 2026-09-19T11:23:23+05:30 qwen-switch: ctx=262144 (mode 262k), api=off, free=1746MiB
- 2026-09-19T16:12:24+05:30 qwen-switch: ctx=262144 (mode 262k), api=off, free=1746MiB
- 2026-09-19T23:33:29+05:30 qwen-switch: ctx=262144 (mode 262k), api=off, free=1746MiB
- 2026-09-20T00:10:30+05:30 qwen-switch: ctx=262144 (mode 262k), api=off, free=1746MiB
- 2026-09-20T01:20:31+05:30 qwen-switch: ctx=138240 (mode 138240), api=cpu, free=5988MiB
- 2026-09-20T11:34:24+05:30 qwen-switch: ctx=262144 (mode 262k), api=cpu, free=1746MiB
- 2026-09-21T07:53:47+05:30 qwen-switch: ctx=262144 (mode 262k), api=off, free=1746MiB
- 2026-09-21T02:29:08+05:30 qwen-switch: ctx=225280 (mode 225280), api=cpu, free=3008MiB
- 2026-09-22T16:08:52+05:30 qwen-switch: ctx=262144 (mode 262k), api=off, free=1746MiB
- 2026-09-23T02:09:33+05:30 qwen-switch: ctx=262144 (mode 262k), api=off, free=1746MiB
- 2026-09-23T05:11:39+05:30 qwen-switch: ctx=262144 (mode 262k), api=off, free=1746MiB
- 2026-09-23T05:47:08+05:30 qwen-switch: ctx=262144 (mode 262k), api=off, free=1746MiB
- 2026-09-24T01:54:48+05:30 qwen-switch: ctx=262144 (mode 262k), api=off, free=1746MiB
- 2026-09-24T18:56:10+05:30 qwen-switch: ctx=262144 (mode 262k), api=off, free=1746MiB
- 2026-09-25T00:33:56+05:30 qwen-switch: ctx=262144 (mode 262k), api=off, free=1746MiB
- 2026-09-25T03:50:38+05:30 qwen-switch: ctx=153600 (mode 153600), api=off, free=5464MiB
