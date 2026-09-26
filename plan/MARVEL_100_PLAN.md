# MARVEL 100% — campaign plan (2026-09-25, opencode; owner-ordered)

# Reference shapes: plan/CSM_100_CLOSE.md (100% closure shape) and
# plan/Plan_to_perfection.md (D1–D6, supply tiers, standing rules).
# This plan is the owner's order: the entire Marvel fandom, from multiple
# sources, with speaker-labeled closed captions in the corpus, every
# character/comic/event mapped, to the JJK/CSM bar. Only the final council
# declares 100% (§D5).

Objective: Marvel reaches the CSM 100% bar — every in-scope question green,
content remainder 0, standing gates green at every change, the CC corpus
carries per-line speaker attribution (owner requirement 2026-09-25: visible
speaker names, not bare subtitle text), and every character, comic and event
is mapped across the whole Marvel surface.

Start state (2026-09-25):
- JEV stack verified live: 8017/8018/8020/8025/8026/8040/8041/8050 all UP
  (`jev-status`; 8018 fast lane answered a live systemone probe; 8040 is the
  group-D restored listener — owner to confirm).
- CSM closed state per plan/CSM_100_CLOSE.md (463/486, gates green): every
  engine change in this campaign must keep the four standing gates green
  (pytest / eval jjk / span-recall jjk / canon opm). JJK + CSM are baselines,
  never touched.
- No Marvel series on disk (`series/` = berserk, bleach, csm, db, doom, hxh,
  jjk, onepiece, opm) — greenfield, no phantom-work assumption.
- GPU: Qwen 30.4/32.6 GB resident; ~2.2 GB free — window discipline below.
- CPU: 32 cores, 30 GB RAM. No ffmpeg, no whisperx/pyannote/faster-whisper
  installed (install items, §B2).

## Denominator annex

Every exit below is read against these numbers. Re-measure each before its
phase; a number that disagrees with a fresh run wins and this document is
wrong.

| surface | number | measured 2026-09-25 | regenerate |
|---|---:|---|---|
| Marvel Database articles | 279,133 | same-day `allpages` enumeration 18:58 (the reconciliation run's fresh full enumeration — supersedes the siteinfo-statistics 279,440 per the fresh-run-wins rule; `series/marvel/manifest.json` `pages_enumerated` matches) | same, per wiki |
| MCU Wiki articles | 48,059 | same-day trusted sequential full-chain `allpages` enumeration ~20:01 (supersedes the siteinfo-statistics 48,025 and the 04:45 crawl-time count 48,026 — the +33 = wiki growth after the final crawl, recorded; `reports/marvel/receipts/mcu_all_pages_fresh_2026-09-25.jsonl`) | same, per wiki |
| Marvel DB `Template:` ns | 508 | `allpages` ns 10 full walk | same |
| Marvel DB project ns (`Marvel Database:`) | 162 pages, ~30 infobox templates | `allpages` ns 4 | same |
| MCU `Template:` ns | 489 | `allpages` ns 10 | same |
| marvel.com URLs | 22,676 (23 sub-sitemaps: characters 3,468 · articles 13,727 · watch 4,000 · teams 403 · videos 387 · tv-shows 108 · items 81 · movies 64 · games 39 · rest) | `sitemap.xml` index + per-sub-sitemap `<loc>` count | same |
| CC catalog | built in B0 (estimate 3,500–4,000 titles: ~35 MCU movies + ~45 animated films + ~2,000+ live-action episodes + ~1,000+ animated episodes) | `reports/marvel/cc_catalog.jsonl` row count | `wc -l` |
| CC text coverage | 100% of catalog, or named exclusion with cause | per-title `cc.db` presence | SQL §B gate |
| speaker-attributed coverage | measured, reported, with named floor (no floor may swallow a title that has an audio source) | SQL over `cc.db.speakers` | SQL §B gate |

## Standing rules

Verbatim copy of `plan/STANDING_RULES.md` (repeated deliberately so reading
only this document is sufficient).

**1. No user input. None, for the duration of this plan.** Every wall where
you would normally stop and ask — a design fork, an ambiguous result, a
blocked step, a judgement call — **run `llm-council` instead.** The council
decides; you act on its verdict and record it. The only stop is the halt path,
and that runs a council first. Council claims are DB-verified before recording;
one that cannot be verified did not happen.

**2. The GPU is available. Do not default to CPU.** Qwen's compute idles while
a shell command runs; ~7.4 GB free under Qwen at normal dial — enough for the
~5.3 GB retrieval stack. Check `nvidia-smi` first and size the job. A
sustained 27B extraction batch wants the card to itself (one OOM-crashed
co-located). Falling back to CPU needs a measured reason.

**3. Council cadence — three mandatory points.** (a) Every 2–3 completed
todos, a council reviewing the fixes just made. (b) At the end of every
sub-list, a council assessing completion before the return pointer fires. (c)
At every phase gate. Write each to `reports/marvel/COUNCIL_<subject>.md` and
commit it with the work it reviewed. If it is not on disk, it did not happen.

---

## 1. Source catalog (all verified 2026-09-25; raw receipts in
`reports/marvel/exploration_2026-09-25.md`)

| id | source | role | verified |
|---|---|---|---|
| S1 | **Marvel Database** — `marvel.fandom.com` (279,440 articles) | primary structured corpus: every character (Earth-designated), comic issue/series/volume, event, team, location, power | API live; 50-page batch fetch verified at **2,123 pages/min** (0.3 s sleep, zero 429 in a 500-page window); `expandtemplates` verified |
| S2 | **MCU Wiki** — `marvelcinematicuniverse.fandom.com` (48,025 articles) | live-action continuity: movies/episodes with `Plot`, `Cast`, `Appearances`, `Events` sections; the canonical cross-check set for CC speaker mapping | API live; **1,974 pages/min** verified |
| S3 | **Marvel.com** (`/explore`, characters, comics, movies, tv-shows, articles; 22,676 sitemap URLs) | official editorial descriptions (current continuity); sub-store, campaign-neutral | sitemap index + 23 sub-sitemaps fetched; character page server-rendered (JSON-LD + embedded state) |
| S4 | **Wikipedia** (publisher/imprint/corporate-history slice) | publisher history the fandom wikis omit | MediaWiki API (trivial); scope = decision D-4 (default: yes) |
| S5 | **YouTube official full-episode uploads** — `Marvel Animation \| Full Episodes` playlist + @MarvelHQ full-episode uploads | CC text for the animated library (90s–2020s) | `youtube-transcript-api` verified end-to-end: 1,711 timestamped caption snippets from one official full-episode video (auto-generated track present; **no speaker labels** — see §3 speaker layer) |
| S6 | **SDH/CC subtitle databases** — OpenSubtitles (v3, HI/"Hearing Impaired" flag), Subscene (SDH tag), Addic7ed (HI tag; reachable 200 from this host), Podnapisi (HI filter) | CC/SDH text for live-action + films: SDH adds non-verbal cues (`[MUSIC]`, `[SIREN]`, song lyrics) = `kind: sign` lines in the JJK transcript model | addic7ed reachable; subscene 403; podnapesi + opensubtitles-v3 unreachable from this host (000) — **reachability is a per-pilot measurement, not an assertion**; OpenSubtitles v3 needs a free API key (setup item) |
| S7 | **Disney+ official CC (and audio)** — owner-account downloaders | the only legal route to live-action CC + audio (movies/Disney+ series) | decision **D-1** (owner asset) |
| S8 | Comic Vine (issue-level credits) | candidate issue→creator mapping surface | deferred to C5; not in the download scope |

Detail-loss register (why "we don't lose details"):

- **L1** — Marvel infoboxes are project-namespace templates (`Marvel Database:
  Character Template`, ~30 of them; MCU uses `Template:Character` / `Movie` /
  …). Crawl-time `build_ontology` only elects templates whose *name* contains
  "infobox", so without action every Marvel page would store as type
  `unknown` with zero infobox facts. Fix: `type_aliases:` in
  `series/marvel/overrides.yaml` + `series/mcu/overrides.yaml` (the §6
  mapping-file mechanism; no engine change). **Done pre-crawl (A0).**
- **L2** — Disambiguation pages (e.g. `Spider-Man`) carry the wiki's own
  alias graph (`main_articleN` lists) and the engine's default skip pattern
  drops them. Fix: `skip_patterns:` override hook + a small gap-fill pass
  over the disambiguation title list (A1b) so the alias data is on disk;
  `_aliases()` gains `currentalias` via `alias_fact_keys:` override.
- **L3** — Fandom's Portable Infobox schema on these wikis is **v5**
  (`parser_tag_version: 5`, a list of `{type,data}` rows with
  `source`/`label`); `learn_field_labels` only walks the legacy `sources`
  dict, so display labels are silently dropped. Fix: v5 walker branch
  (small engine change, gated; lands before Phase C indexing — re-extraction
  re-parses stored wikitext with the current parser, no re-crawl).
- **L4** — first-appearance data templates (`1st`, `1stChron`, `1stFull`, …)
  transclude curated lists; resolved by the existing `expandtemplates`
  pass, which the crawler already runs per template it cannot parse.
- **L5** — slash categories encode typed relations: `Avengers (Earth-616)/
  Members` (group membership), `Brian Michael Bendis/Creator` (credits),
  `A.X.E.: Judgment Day casualties` (event participation),
  `1962 Character Debuts` (era). The generic edge builder only emits
  wikilink mentions; the category grammar is declared per-wiki in
  `category_relations:` (C2, generic mechanism).
- **L6** — Lua-module rendering (what the *browser* sees) is out of scope by
  construction: the engine parses stored wikitext, and that is what the wiki
  is made of. Recorded so nobody later "fixes" a rendered-page mismatch.
- **L7** — character pages wrap the **entire narrative inside the
  infobox**: `{{Marvel Database:Character Template | ... | History = <the
  abridged-history note>` and the box only closes at page end, so every
  narrative section sits inside the template's parameter (measured on
  `Peter Parker (Earth-616)`: lead `{{`/`}}` 266/265, whole page
  1163/1163). Two generic parser gaps follow and are named, not discovered
  ad hoc: **F1** — `find_infobox` colon-fold mismatch
  (`Marvel Database: Character Template` vs the alias key) → character
  pages store `facts=0` while closed-box types (comic/event/film) extract
  fine; **F2** — the lead is the raw infobox parameter block instead of the
  `History` value. Both fixed in A1c (gated; re-extraction applies them to
  the stored corpus). Sections themselves are unaffected (headings are
  found in the raw text; 37 on that page).
- **L8** — the wiki publishes its own sample formats: every infobox's
  `/Documentation` (or `/doc`) page carries the full empty-syntax parameter
  list + per-field meaning (Marvel DB: 29 KB for the character template;
  `First`, `Powers`, `Abilities`, `Affiliation`, `Creators` among the
  fields). These are the per-archetype field specs for C1/C5 (tier 1),
  with the PIB v5 blob (tier 2) and observed keys (tier 3) where the wiki
  has no doc page (MCU: verified absent for `TV`/`Character`).

## 1a. Bot-protected source ladder (owner-approved 2026-09-25)

When a source is bot-protected — Subscene 403, Podnapisi / OpenSubtitles
000 today, any Fandom WAF 403 escalation mid-crawl, any new wall hit in a
pilot — climb the ladder, in order, and record which rung worked:

1. **API route** (default): plain curl / `curl_cffi` with the browser UA
   (verified on both Fandom APIs 2026-09-25; the crawler's WAF note — no
   `Accept: application/json` header — is the first fix before any ladder).
2. **agent-reach + OpenCLI (browser-grade; the owner's "brave app" channel):**
   `agent-reach` (installed; `agent-reach doctor --json` verified 2026-09-25)
   routes platforms through OpenCLI / per-platform CLIs. OpenCLI's browser
   backend drives a real browser session, which is what gets past bot walls
   that block headless fetches. Precondition: a browser with the OpenCLI
   extension connected (doctor today: extension not connected — one-time
   owner setup, recorded when done). YouTube already resolves via its
   `yt-dlp` backend (doctor: ok).
3. **JEV triage of what the rung found:** `~/tools/jev/bin/jev-search-
   triage.py --query "<title> <SDH|subtitles>"` (or `--input results.jsonl`)
   ranks the candidate URLs/files with the local decider (survivors
   p ≥ 0.3, unjudged kept + flagged); the agent researches only survivors —
   manual research stays cheap because the 27B never sees the raw candidate
   pile.
4. **Record it:** every bot-protected fetch goes to
   `reports/marvel/receipts/<phase>/` — source, ladder rung, tool, output
   sha256. A claim that is not on disk did not happen.

Where the ladder applies: B0/B1 tier-source failures (T-SC Subscene,
T-PN Podnapisi, T-OS OpenSubtitles v3), Fandom 429→403 escalation during A1
(run the ladder, then resume the crawl — never blind-retry), and any D4
blind-set source verification. A source the whole ladder cannot reach is
not silently dropped: it becomes a named row in the CC catalog with cause
`bot-protected: all rungs failed <date>` + retest trigger (the wall may be
temporary; a retest is one `doctor` + one rung probe).

**Throttle → egress-IP rotation (owner policy 2026-09-25).** Fandom
throttles per IP, and a throttled IP stays throttled for the whole run.
When a crawl connection throttles — a sustained 429 pause-loop, or the
stall watchdog firing (`CrawlStalled`, CLI exit **42**: zero completed
pages for `crawl_stall_seconds`, default 300 s, while titles were still
outstanding) — the response is to **change the egress IP before
escalating anything**: `nordvpn connect` to a *different* country/server
(a fresh exit IP), verify the egress actually changed
(`curl -s https://api.ipify.org` ≠ the pre-switch IP), then re-run the
same crawl command (resumable from disk: already-fetched pages are
skipped, `all_titles` is re-enumerated, the partial manifest's `stalled`
marker is replaced). Keep rotating servers while throttling persists; a
stalled path is never blind-retried on the same IP. The VPN switch is the
rate-limit escape hatch, not a rung of the bot-wall ladder above (that
ladder is for walls; this is for limits).

Egress state of this host (2026-09-25 — the stack must stay true or the
VPN is useless): the ISP blackholes public TCP/53 + UDP/53 and outbound
UDP/443 (QUIC), so all resolver traffic rides the local DoH-backed DNS
stack: `nordvpn-dnsfwd` (127.0.0.1:5353 + 127.0.0.55:53),
`nordvpn-dnsfix` (DNAT/REJECT iptables), `nordvpn-conntrack-flush.timer`
(60 s), static `/etc/resolv.conf` → `127.0.0.55`. If `nordvpn` starts
15-seconding again, the first suspect is one of those four units having
died, not the account. Account: the owner's OAuth login may still be
pending (`nordvpn login` → browser flow, headless fallback
`--callback`); a session reporting "You're not logged in" cannot
`connect` — record it, do not stop the run on it (the crawl runs on the
direct ISP egress until rotation is needed).

**2026-09-25 addendum (verified on resume):** the three `nordvpn-dns*`
units named above no longer exist on this host (`systemctl is-enabled` →
not-found; 5353 is held by avahi-daemon; `resolv.conf` rides the
systemd-resolved stub → ISP `192.168.1.1`; `nordvpnd` active; `nordvpn
status` responsive, no 15-second stall). The owner's fix — the VPN was
declared fixed after this section was written — does not use that unit set.
Baseline direct-egress IP at resume: `103.124.15.71`. The rotation
protocol above applies unchanged; if a rotation 15-seconds again, the first
suspect is the live DNS chain (systemd-resolved → ISP resolver), not the
absent units. Receipt:
`reports/marvel/receipts/egress_verification_2026-09-25.md`.

**2026-09-25 rotations #1 + #2 (executed ~04:0x / ~04:2x):** both crawls
throttled on the baseline ISP egress — the Marvel run 1 hit `CrawlStalled`
(exit 42) after enumerating 42,692 titles; the MCU run 1 `CrawlStalled` at
04:05:44 with 10,968 titles outstanding (~37k fetched). Per the protocol
above: rotation #1 `nordvpn connect us` → us13908, egress verified
`187.14.224.72` (≠ `103.124.15.71`), both crawl commands re-run (disk
resume; the per-run logs are the receipts). The US exit then throttled on
the MCU host only (marvel.fandom.com stayed clean on the same egress —
429 pools are per-host), MCU run 2 `CrawlStalled` at 04:23 → rotation #2
`nordvpn connect de` → de1507, egress verified `187.40.55.180`, MCU
re-run (0 429s on the fresh log). If throttling recurs, rotate to a
different country/server — a fresh exit IP every time; 10 workers
unchanged.

**2026-09-25 rotation #3 (executed ~04:36):** the DE egress throttled the
MCU host within ~5 min of the re-run (sustained `rate limited` pause-loop,
04:31–04:36) → MCU run 2 `CrawlStalled` at 04:35:47 (zero completed pages
for 300 s, 4,867 titles outstanding; 35,209/48,026 on disk). Per protocol:
`nordvpn connect nl` → **nl1260.nordvpn.com** (third country — us/de already
used; rotation #4+ needs owner budget sign-off, council hardening #6), egress
verified `186.247.163.23` (≠ de1507's `187.40.55.180`), DE stall log
archived to `reports/marvel/receipts/crawl_mcu_run2_de_stalled.log` before
the per-run log rewrite, MCU re-run from disk (setsid wrapper 37211; 0 429s
on the fresh log for 3+ min). The Marvel crawl (run 2, pid 17631 — healthy
on the DE egress, 0 429s, still enumerating ~182k/279k at 04:40) rides the
NL egress into its fetch phase: the council-flagged per-host-pool risk
(rotating both crawls can trade a clean IP for a dirty one) is live — the
Marvel log is the monitor; a Marvel-side 429 loop on NL is the trigger for
rotation #4 (owner wall, per hardening #6). 10 workers unchanged.

**Rotation protocol hardening (council A1c/A1b ruling, 2026-09-25 —
`reports/marvel/COUNCIL_a1c_a1b_landed.md`):** (1) record the egress IP
(`curl -s https://api.ipify.org`) after every connect and verify it changed
(done for rotations #1–#3; VPN pools churn — the "DE server" that worked is
not guaranteed at resume time); (2) rotate per-host, not per-country, where
the per-host pools allow — keep a clean host's crawl running, switch only the
throttled one; (3) resume at reduced concurrency for a cooldown window before
returning to 10 workers (the do-not-raise rule caps at 10); (4) a wall-clock
no-progress alarm must trigger rotation — a hung backoff loop never fires
exit 42 by itself (the 300 s stall watchdog is the catch-all); (5)
client-side 429 limiting (honor Retry-After, backoff, jitter) is the primary
control; rotation is the last resort; (6) rotation #4+ requires owner budget
sign-off (three consumed: us, de, nl). The US/DE evidence proves host-scoping
but NOT per-(host,IP) vs a per-host-global budget — if global, rotation is a
placebo and only time clears a budget; NordVPN exit IPs are shared and often
dirty, so "changed country" ≠ "clean IP".

**2026-09-25 rotations #4–#12 + the c2 root cause (executed 14:54–17:23;
full episode record in `plan/SWITCHPOINT.md` +
`reports/marvel/OWNER_WALL_2026-09-25.md`):** after the owner's "single
machine, rotate for speed" ruling (wall item 5, RESOLVED), the Marvel
fetch (65,391 outstanding; `tools/marvel/shard_fetch.py` full shard) ran:
#4 CA #1980 (`187.15.140.90`; c3, then c8 burst 429-loop), #5 JP #1295
(`187.15.136.110`; 60-s fetch timeouts), #6 SG #646 (`187.15.101.107`; c3
429-loop), #7 UK #2640 (`194.88.96.77`; c3 429-loop ×2 + one transient
post-switch tunnel stall), #8 DE #1544 (`187.40.54.176`; c3 429-loop),
#9 FR #1136 (`187.14.107.20`; c2 silent stall), #10 CH #383
(`89.37.173.228`; c2 silent stall + c3 429-loop), #11 ES #175
(`187.13.187.62`; c2 silent stall ×2 + the 17:10 tail-200 repro that added
160 pages), #12 FI #214 (`187.40.62.59` — current egress). **Two findings
close the afternoon's stalls:** (1) the c3 429 loops were Cloudflare **WAF
UA challenges**, not Fandom's rate limiter — proven 16:44 on CH (crawler
UA `ScriptEngine/0.1` → 429 "Just a moment…" HTML in 1.1 s; browser UA
→ 200 JSON 50/50 in 0.51 s, same session/egress;
`tools/marvel/batch_probe_ua.py`); the sustained-rate-limit theory is
retired for those loops, and every launch now carries the chrome136
browser UA. (2) The c2 **silent stalls (300 s, 0 completions, 0 RLs, 0
failures, on every egress, UA-independent) are a client-side bug —
RESOLVED by the SIGUSR1 task dump** (`tools/marvel/c2_diag.py`,
`crawl_marvel_c2_es_learn429_taskdump_2026-09-25.log`): both workers
suspended in `_learn_labels` (`crawler.py:708`) — the per-new-type
`action=parse` label fetch sits between the batch fetch and the page write
and 429-loops/hangs in hot WAF state, pinning the crawl while the batch
endpoint stays healthy. **Patch (gated on the four standing gates before
use/commit):** the learn fetch is bounded (`asyncio.wait_for(crawl_
timeout_seconds + 30 s)`) + failure-tolerant, and a type with no PI schema
(or a failed attempt) is recorded once with an empty label set so it is
never re-fetched; output is unchanged on a healthy egress. **CLOSED
17:27–18:0x (rotation #12 FI egress `187.40.62.59`):** the four standing
gates went GREEN on the patch (pytest 1,345+2+3 exactly the documented
`:8000`-down trio; eval jjk 31/31 CPU; span-recall jjk 48,572 rc=0 + probe
398/400 behind a bounded `:8000` window; canon opm 10/16 · 236/236 · 79.0% —
receipts `reports/marvel/receipts/gates_learn_patch_2026-09-25/`) and were
committed as `e78e1f62` (named paths: `crawler.py` + both plan files).
**Full-list c2 fetch COMPLETE 17:45:55–18:00 (pid 314745, chrome136 UA,
60-s timeout, rl=0 / to=0 / learn-warn=0): all 65,231 outstanding titles
accounted for — 22,701 written + 42,530 skipped (no-content / skippable-
category / duplicate pageid: the enumeration's tail is stubs, redirects and
galleries) + 1 failed ("Elizabeth Tyne")**; corpus now 236,580 on disk
(`crawl_marvel_c2_fi_full_done_2026-09-25.log` + `manifest.shard_full.json`).
**Reconciliation COMPLETE 19:06:58 (pid 320221, same egress, launched
18:06; receipt `crawl_marvel_recon_done_2026-09-25.log`): canonical
`crawl --series marvel` = fresh full sequential enumeration to
**279,133** (the wiki grew +21 since the 15:21 list — 279,133 is the new
ground-truth denominator, superseding 279,116) + on-disk resume-skip +
catch-up fetch: **48 written + 42,504 re-verified skips + 0 failed**
(the 42,552 non-on-disk queue was the shard run's no-content/skippable
tail, re-proven by the pipeline itself, including the shard run's one
failed page). Canonical `series/marvel/manifest.json` REBUILT CLEAN
(`stalled` marker gone; accounting closes exactly: `resuming: 236581 of
279133 already on disk` (2 titles share one filename) + 48 + 42,504 + 0
= 279,133 — every enumerated title on-disk ∪ skipped ∪ failed).
**Marvel fetch phase = 100% COMPLETE (236,628 on disk, 0 failed).**
Then: Marvel-set gates 4–6 → GATE A council (sequential; must bless the
*Marvel* validation).**

## 2. Phase A — Download (no model, no GPU; resumable, hash-pinned)

**A0 — series scaffolding + overrides. (EXECUTED at plan time.)**
- `series/marvel/`, `series/mcu/` trees + `overrides.yaml` each
  (`type_aliases` per L1; minimal `skip_categories`; `citation_params`
  `r → comic` for Marvel DB's `{{r|Amazing Spider-Man Vol 1 15}}` reference
  grammar — verified on character pages; refine in C1).
- PREMISE: `type_aliases` keys match the normalized template names the
  crawler sees. VERIFY: one 50-title batch fetch; assert a `Peter Parker
  (Earth-616)`-shaped page types as `character` with `facts > 0`
  (`reextract` + inspect). IF REFUTED: log deviation, fix the alias spelling
  (the `Marvel Database:` prefix normalisation), re-verify.

**A1 — full crawl, S1 + S2.**
- `python -m scriptengine.cli crawl --series marvel --start-url
  https://marvel.fandom.com/wiki/Marvel_Database` (279,440 titles ≈ 3–4 h at
  the measured rate; crawler resumes by on-disk title set).
- `crawl --series mcu --start-url
  https://marvelcinematicuniverse.fandom.com/wiki/Marvel_Cinematic_Universe_Wiki`
  (48,025 ≈ 30–60 min; separate host, may run in parallel — 429 pools are
  per-host; watch both logs).
- Manifest pins: `revid` per page (gold-pinning per Plan_to_perfection §5.2),
  `all_titles` (the audit resolves links against the full enumeration),
  `crawled_at`, failed/skipped lists.
- **Crawl ops (owner 2026-09-25):** per-page fetch timeout =
  `crawl_timeout_seconds` (30 s, `SCRIPTENGINE_CRAWL_TIMEOUT_SECONDS`) — a
  page that does not answer in 30 s is abandoned, retried, then failed, so
  one dead route can never hold a worker; stall watchdog =
  `crawl_stall_seconds` (300 s, `SCRIPTENGINE_CRAWL_STALL_SECONDS`) →
  `CrawlStalled` → CLI exit **42** + a `stalled` marker row in the
  manifest → **switch the VPN server/country for a fresh egress IP,
  re-run the same command** (the §1a throttle policy; the resume is
  disk-driven, nothing is lost). Each run's log is a receipt:
  `reports/marvel/receipts/crawl_marvel.log` / `crawl_mcu.log` (rewritten
  per run).

**A1b — hook + gap-fill (L2).** `skip_patterns:` override hook +
`alias_fact_keys:` (both small, four gates green) + targeted crawl of the
disambiguation title list (from `list=search`/category walk) + re-extract.

**A1c — parser shape fixes F1 + F2 (L7), during the crawl.** Generic,
gated: (F1) colon-fold template-name normalisation in `find_infobox` /
`infobox_candidates` (one helper, both sides); (F2) when the lead's first
top-level template is unclosed inside the lead (parameter-wrapped
narrative, L7), the lead is the `History`-value pre-heading portion, not
the raw parameter block — the branch fires only on the unclosed shape, so
JJK/CSM pages are untouched (pinned by the existing suite). Four standing
gates green before the change is committed. No re-crawl: `load_extracted`
re-parses stored wikitext with the current parser at index time
(documented crawler architecture), so the stored JSON snapshots are
corrected without refetching. The MCU `TV` alias (found in A0) is already
in `series/mcu/overrides.yaml`.

**A-status (2026-09-25 ~05:0x; SWITCHPOINT + receipts carry the detail):**
A1 MCU crawl **complete** (run 3, 04:45:59 — `0 written, 12817 skipped
(category policy), 0 failed`; 35,209 is the final MCU set). Marvel fetch
in progress on the NL egress (279,111 enumerated; ~1,200/min at 04:58 →
ETA ~09:00; zero 429s at that time). At ~06:25 the NL egress 429-looped at
concurrency 10 (~12/min); resolved per council hardening (client-side
throttling primary, rotation last resort): 8-minute cooldown + restart at
`SCRIPTENGINE_CRAWL_CONCURRENCY=3` (06:39:37) — enumeration was clean,
but the fetch endpoint was still hard-throttled and stalled at 07:24
(CrawlStalled 07:29:24; under a hard lockout the process does not exit
cleanly and its 429-retry traffic keeps the IP penalty alive, so the
operator killed it at 07:35; logs archived:
`crawl_marvel_nl_429loop_2026-09-25.log` +
`crawl_marvel_c3_stalled_2026-09-25.log`), 213,718 on disk at 06:44.
Now: c2 (07:50, after the clean 07:49 single-request probe) also stalled
immediately on the fetch endpoint (CrawlStalled 08:34:28, 0 completions —
`crawl_marvel_c2_stalled_2026-09-25.log`); same-egress hardening exhausted,
owner wall TRIGGERED for rotation #4+. The last in-authority attempt — a
c2 retry at 11:30 after a ~3 h fully-quiet egress — also stalled:
CrawlStalled 12:19:15, 0 completions, 52 rate-limit lines
(`crawl_marvel_c2retry_stalled_2026-09-25.log`; this run left the stalled
manifest on disk: `stalled: true`, `stall_remaining: 64091`). **HARD STOP
in effect: no further in-authority crawl actions**; the campaign now waits
at the owner wall (briefing `reports/marvel/OWNER_WALL_2026-09-25.md`).
**Owner ruling at the wall (~14:52): "use the VPN to download the
remaining pages"** → rotation #4 approved (country ≠ us/de/nl; budget = VPN
connection time until the crawl finishes). Executed: `nordvpn connect
canada` → Canada #1980, egress `187.15.140.90` (fresh IP; the locked NL
egress `186.247.163.23` now unused); single light probe HTTP 200; c3 run
launched 14:54:46 (pid 221627; ~15 req/min vs the ~48 req/min that
triggered the NL lockout; 65,395 outstanding, ETA ~1.5–2 h into the fetch
phase). Hard stop lifted; the fetch phase (~15:35) is judged with the
15-min health judge (>100 completions, <10 rate-limit lines); CrawlStalled
on CA = this exit is dirty too → record + kill + rotation #5 = owner wall.
**Fetch-strategy pivot (owner ruling ~15:2x, 2026-09-25): single machine,
higher concurrency, rotation pre-authorized as a speed tool.** The owner
ruled: do it all on this machine (the 2nd-device / multi-IP plan and the
home-line second-egress idea are retired — the home line is a diagnosed
dead end: a wired macvlan netns gets L3 reachability, but the router
does not NAT static source IPs, cannot receive the DHCP broadcast over
Wi-Fi, and ignores unicast DHCP), try more workers or anything, start
right now, switch the VPN to download faster (rotations are now
pre-authorized as a *speed* tool — any rotation still gets its egress
logged on connect and a 15-min health judge after relaunch). Executed
15:23: the stale c2 manifest's complete `all_titles` (279,112,
enumerated 08:48 today) was reused as the page list (no network
enumeration) → `tools/marvel/make_shards.py --shards 1` →
`tools/marvel/shard_a.jsonl` (65,391 outstanding, 213,721 on disk);
the in-flight c3 run (pid 221627) was killed at 15:23:03 (still
enumerating — zero fetch progress lost); `tools/marvel/shard_fetch.py
--shard-id full` (ShardCrawler feeds the fixed list in place of the
45-min re-enumeration; per-run manifest `manifest.shard_full.json`, the
canonical manifest is rebuilt by the reconciliation run after the
fetch) launched 15:23:08 (pid 242771) at
`SCRIPTENGINE_CRAWL_CONCURRENCY=8` on CA egress `187.15.140.90`
(ipify-verified). 15-min health judge on the c8 fetch phase: >100
completions and <10 rate-limit lines → 15-min watch cycles to
completion; RED → step down c5/c3, then rotate for speed (pre-authorized).
Pages added after the c2 08:48 enumeration are caught by the final
reconciliation (fresh full enumeration + catch-up fetch of the delta).
**Episode 15:23–15:40 (recorded):** c8 burst-looped on CA within 115 s
(16 rate-limit lines, 0 completions — `receipts/
crawl_marvel_c8_429burst_2026-09-25.log`); c3 step-down on CA 429'd
within 4 s (the c8 burst left the CA egress hot even on the light path —
`crawl_marvel_c3_ca_hot_2026-09-25.log`) → rotation #5 (pre-authorized
speed tool) Japan #1295, egress `187.15.136.110`: clean of 429s but
~2 s RTT — heavy 50-page batches hit the 30-s fetch timeout
(`crawl_marvel_c3_jp_timeouts_2026-09-25.log`) → relaunched with
`SCRIPTENGINE_CRAWL_TIMEOUT_SECONDS=60`; rotation #6 (owner: "use a
closer VPN") Singapore #646, egress `187.15.101.107`, c3 + 60-s timeout
relaunched ~15:32 — CrawlStalled at 300 s (14 rate-limit lines, 0
completions; light path clean but the heavy 50-page batch endpoint
429-looped within 4 min on a fresh exit — `crawl_marvel_c3_sg_429loop_2026-09-25.log`;
1,200 titles dropped out under the storm are re-tried by disk-resume,
no loss). Rotation #7 (~15:38) United Kingdom #2640 (London), egress
`194.88.96.77` — a **different Nord range** (`194.88.x` vs `187.15.x`
for CA/JP/SG), the discriminator: clean UK batch path ⇒ the 187.15
range is what is batch-limited; UK also loops ⇒ the batch endpoint is
limited across NordVPN exits (range/ASN level) and the fix is
client-side (slimmer batch / reduced rate), not another rotation. c3 +
60-s attempt ~15:40 (pid 255764) CrawlStalled at 300 s with **0 rate-
limit lines** (one six-0-s batch timeout, 0 completions): a transient
SG→UK tunnel degradation, NOT throttling — `crawl_marvel_c3_uk_stall_transient_2026-09-25.log`
(reconstructed from the session transcript). Discriminator answer so
far: the 187.15 exits' 429 loops were egress-specific (burned/dirty),
not a range/ASN-level batch limit — the 194.88 exit is 429-clean.
Direct 50-title batch probe from the same UK egress ~15:58: HTTP 200 in
1.64 s, 50/50 pages (endpoint healthy from UK). Relaunched c3 + 60-s on
the SAME UK egress (no new rotation; pid 264208, ~16:00). **The UK
relaunch 429-looped within 3 min** (20 rate-limit lines, 0 completions,
CrawlStalled fired — `crawl_marvel_c3_uk_429loop_2026-09-25.log`;
single-request probes pass but sustained c3 trips the limit). **Owner
ruling (~16:0x): "why are you waiting 15 min? just download it, if it
doesnt start, use new VPN"** — the 15-min health judge is RETIRED:
quick check (2–4 min) after every relaunch; not starting / 429-looping
→ rotate immediately (pre-authorization stands; egress logged each
time). **Rotation #8 Germany #1544 (~16:04, egress `187.40.54.176` —
the proven MCU-crawl 187.40 range):** attempt 1 (c3, ~16:05) hung with
2 failed first-attempts at the 60-s cap and 0 RLs (stale pooled
connections from the post-switch window; direct batch probe 50/50 in
1.92 s — `crawl_marvel_c3_de_stall_1_2026-09-25.log`) → restart #2
(c3, ~16:11) 429-looped (6 RLs, 0 completions —
`crawl_marvel_c3_de_429loop_2026-09-25.log`). **Pattern: every egress
tried today (CA, SG, UK, DE) 429-loops on sustained c3 batch traffic
within minutes while single-request probes always pass** → consistent
with a sustained-rate limit on VPN ranges for the heavy batch query,
not egress-specific dirt. **Rotation #9 France #1136 (~16:18, egress
`187.14.107.20`; slow route — light 3.2–10 s, batch 50/50 in 14.5 s,
no 429s):** launched **c2** (half the c3 request rate; env-var lever,
no gate needed) + 60-s timeout (pid 273739, ~16:20, `receipts/shard_full.log`).
Quick check ~16:24: completions flowing (ondisk delta from 213,721) →
15-min watch cycles to completion (c2 on the slow FR route ≈ 3–4 h for
65,391); 429-loop = the FIFTH egress → decisive evidence for the
sustained-rate limit → escalate to the council (client-side slimmer
batch = gate-covered code change; per-page parse fallback; or a
cooldown) — no sixth blind rotation.
A1c + A1b landed as the one gate-covered commit
`6a1f6ceb` (four standing gates green on the union tree). Council medium
gates 4–6 on the final MCU corpus: **GREEN** — base-vs-new parser diff
(stable delta +0.00%, 0/35,209 pages changed → PROCEED; the only
difference is the label-level `tv*`→`tv_series*` rename on 225 pages);
hand-validation 40/40 character pages faithful + the 1 stored
disambiguation page at zero facts; full `load_extracted` dry-run
0 exceptions / 0 quarantined per tree; the truncation characterization
shows the F2 unclosed-lead branch never fabricates facts. Receipts:
`reports/marvel/receipts/gates_4_6_mcu_2026-09-25.md`,
`parse_diff_mcu_report.md`, `gate5_mcu_sheet.md`. The Marvel-set gate
run (same diff + `currentalias`/colon-template assertions + a 10-page
disambiguation zero-facts sample) runs after the fetch completes.

**A2 — marvel.com sub-store (S3).** Crawl the 22,676 sitemap URLs →
`series/marvel/web/` (raw HTML + extracted JSON: name/description/cast-ish
fields), `manifest.json` with per-URL sha256 + fetched_at. Campaign-neutral:
outside the `facts.db` denominator (JJK-transcripts precedent; drift-log
entry required).

**A3 — Wikipedia slice (S4, if D-4 yes).** Publisher/imprint/history pages →
`series/marvel/wiki/`, same sub-store shape.

**GATE A — DOWNLOAD (council checkpoint).**
Exit evidence, emitted: (1) manifest `pages_enumerated` == denominator annex
for both wikis (re-measured same day); (2) on-disk page count == enumerated −
skipped − failed, with the skipped/failed lists archived and every non-empty
failed list re-run to zero or named; (3) `revid` spot-check: 10 random pages,
stored `revid` == live API `revid` (or an explicit diff = wiki edited between
crawl and check, recorded); (4) type histogram: `unknown`-type share < 5% of
pages with infoboxes (L1 proof); (5) L4 expand spot-check on 5 pages;
(6) four standing gates green (crawl touches no gated code — the gate run
proves it); (7) council verdict recorded in
`reports/marvel/COUNCIL_gate_A_download.md`.
GATE A is a precondition on Phase B/C advancement, not a hand-off.
Council hardening (2026-09-25, `reports/marvel/COUNCIL_a1c_a1b_landed.md`):
GATE A convenes **only after the council gate list 1–6 pass** (1–3 done
2026-09-25; 4–6 MCU done, Marvel set after its fetch) and the checkpoint
blesses the *Marvel* validation, not just the four JJK/CSM gates.
Source B (`tools/marvel/export_fetch.py` + `reconcile.py`, inspected
2026-09-25) is serialized AFTER the source-A fetch (same host, shared
429 pool) and its `reconcile.py` S0 receipt (`sourcing_100`) joins the
exit evidence.

Council verdict (2026-09-25, `reports/marvel/COUNCIL_gate_A_download.md` —
GATE A item 7, recorded): **GATE A = PASS (conditional)** — 5/5 advisors +
5 peer reviews unanimous; the Marvel download validation is blessed;
Phase B unblocked now; Phase C gated on the entry checklist below.
Finding dispositions F1–F7 + the F1 root cause (the gated `fetch_batch`
sends `rvprop=content` @ `scriptengine/ingest/crawler.py:334`, which
filters the API revision object to content-only, so stored `revid` is
always 0; fix = `rvprop=ids|content` — a one-word **gated** change:
+ four standing gates + commit by named paths, landing before the Phase B
top-up crawls; interim = campaign-tooling revid backfill or explicit
waiver; latent second gap recorded: the per-page `action=parse` path
reads a key Fandom's parse response never returns) are in the council
doc.
- **Phase C entry checklist (ordered; council):** 1. F1 gated fix
  (before the top-up crawls — new files stamp natively); 2. F1 backfill
  (campaign tooling: `action=query`, `rvprop=ids`, 50-title batches ≈ 4,733
  Marvel + ≈ 962 MCU requests) or an explicit waiver on record; 3. F3:
  zero-egress inspection of the 2 folded collision files + 1 orphan, then
  re-crawl the 4 collision titles under disambiguated filenames (after #1);
  4. F5: 33-page MCU top-up (bundled with #3's egress); 5. F7:
  grep-quantify the stray-`'` blast radius (zero egress); if material,
  patch the value cleaner + re-emit + O*N*E regression fixture (the fixture
  lands either way); 6. F2: record the title drift in
  `reports/marvel/receipts/known_diffs_2026-09-25.md` — the "46-title
  rename map" is NOT reproducible (zero-egress audit: no metric yields
  46); actual drift = 1 orphan file `Elizabeth Tyne (Earth-33263)` + 23
  net-new titles (enum 279,112→279,133, net +21), wired into the
  re-validation plan (the next revid spot-check must include the orphan
  + the net-new titles); 7. F6: owner ruling at the wall (item 2, costed: revert =
  612-file rework; interim default = typed + fact-free, no edges — C does
  not wait on it); 8. **delta re-gate** (S5): after #1–#6 mutate the
  corpus — G4-style diff on changed/added files, G5 sample on them, G6
  full dry-run on the mutated corpus, re-archived accounting lists →
  receipt; Phase C start = after this receipt; 9. GATE A (3) explicit-diff
  branch quoted verbatim in the record (done in the council doc).
- **Standing rules adopted (campaign-level, S1–S7):** S1 revid-stamp at
  crawl time (every future franchise + Marvel backfill/waiver); S2
  title-normalization collision check in crawl tooling (a 4-titles→2-files
  fold flags at crawl time, not reconciliation); S3 same-day pre-gate
  re-enumeration standing and non-optional (it caught the MCU +33); S4
  synthetic truncation probe (60%×5 + 15%×6) per corpus; S5
  freeze-and-verify — no post-green corpus mutation without a delta
  re-gate + re-archived accounting lists, logged to a receipt; S6
  value-cleaner regression fixtures (O*N*E class) + the shared-defect
  blind spot recorded in the gate-4 spec (a base-vs-new diff cancels
  defects shared by both parsers); S7 franchise-gate template — the GATE A
  receipt + the G4 diff report + this gate list are the reusable template
  for the next franchise (DC, Star Wars, any fandom wiki).
- **A2 unlock conditions (council union; A2 stays NO-GO until all):**
  1. owner ToS/robots ruling + written clearance (wall item 1;
  Disney-owned, non-CC, no official API/feed); 2. a marvel.com enumeration
  source (the 22,676-URL sitemap index exists) demonstrated to close
  enumerated−skipped−failed accounting; 3. a marvel.com-specific extractor
  + type mapping dry-run-verified with its OWN stop conditions (the
  Fandom gate apparatus does not transfer); 4. egress/rate budget
  demonstrated, with no risk to the closed fandom corpus; 5. the template
  completes Phase C end-to-end on a wiki corpus first (template before
  extension).

## 3. Phase B — CC corpus (speaker attribution is a hard requirement)

Owner requirement (2026-09-25, both messages): closed captions — **speaker
names visible**, not bare subtitle text. Architecture (JJK-transcript
precedent, extended): per-title documents with lines
`{t, speaker, text, kind: line|sign}`, `sign` = SDH non-verbal cue
(`[MUSIC]`, `[SIREN]`, song lyric) — the JJK `SIGN` line class.

Storage: `series/marvel/cc/` — raw caption files + `manifest.json` (url,
sha256, source, credits, fetched_at) + `cc.db` (SQLite FTS5, separate from
`facts.db`) + `qdrant-cc/` (own VectorStore dir, JJK Phase-2 shape).
Campaign-neutral w.r.t. the wiki gates; drift-log entry required.

**B0 — catalog (no model).** Build `reports/marvel/cc_catalog.jsonl` from the
wikis themselves, not from a hardcoded list (JJK-lesson: structure is the
source of truth):
- MCU movies/series: MCU Wiki categories (`Released Movies`, `Phase N Movies`,
  per-series nav templates) → title, year, episode_count.
- Animated library: Marvel DB `Series Template`/`Episode Template` pages +
  the YouTube official playlist inventory (S5) → title, season, episodes,
  `audio_source: youtube:<id>` when present.
- Live-action (Netflix/ABC era): MCU Wiki + Marvel DB series pages; cross-
  check against S6 catalog availability.
Each row: `{title, class: movie|series|animated, source_tier, audio_source,
cc_source, episode_count, status}`. **Completeness is measured, not
asserted**: every released title in S2's movie/series pages must have a row,
or be named-excluded with a one-line cause (D1 discipline).

**B1 — text layer (no model).** Per row, fetch CC/SDH text via the tier
order, per-title first hit wins, recorded:
`T-OS` (OpenSubtitles v3,
`hearing_impaired` flag preferred, fallback any) → `T-SC` (Subscene, SDH
tag) → `T-A7` (Addic7ed, HI tag) → `T-PN` (Podnapisi, HI filter) →
`T-DP` (S7, if D-1 yes). **Owner decision 2026-09-27: websites first —
`T-YT` (S5) dropped from the tier order** (YouTube auto-captions carry no
speaker labels; the owner requirement is character names with dialogue,
which only tagged SDH/subtitle files provide; S5 survives as D-1/owner
fallback for legal live-action audio). **Pilot re-measure 2026-09-27
(egress FI #214):** T-A7 reachable + anonymous download works (no login),
HI files are per-file siblings of normal files (row flag `HI`); T-A7
catalog = Disney+ era only (WandaVision 8219, Loki 8435 = S2 only,
Agatha 9912, Secret Invasion 9464, …) — Netflix-era shows (Punisher,
Iron Fist, Daredevil, Jessica Jones, Loki S1, …) and films absent →
T-OS (free owner API key) or T-SC (ladder); T-OS unkeyed API answers
`kong-user-agent-block` / "cannot consume this service" (re-measured
09-27); T-SC 403, T-PN 000. **Label-density measurement (pilot #2,
09-27, 6 Disney+-era episodes, HI files):** speaker labels present on
only 0–8% of dialogue lines (real character names when present) — the
B1 text layer satisfies timing + verbatim text + SDH `sign` cues, and
the hard names-on-every-line requirement is closed in B2
(diarization vs named characters), unless the owner requires a
fully-labeled source first (GATE B1 decision item). A tier whose fetch is bot-protected climbs the
§1a ladder (agent-reach + OpenCLI browser-grade rung, JEV-triaged) before
the tier is marked failed; reachability is re-measured at run time per
source (addic7ed 200 / subscene 403 / others 000 from this host today —
the catalog records what actually served each title, not what was intended).
Parse to `{t, speaker, text, kind}` — SDH cue lines become `kind: sign`
(verbatim, JJK lossless rule: every cue line lands, zero loss).
Licensing (JJK blind spot #8, carried): personal local KB only; source +
upload/sub-team credits in the manifest; any derived product carries the
credit tag.

**GATE B1 (council checkpoint).** Catalog completeness == denominator
annex CC row (every released title present or named-excluded); zero parse
failures (assert every timestamped line carries text; `sign` lines counted,
not dropped); per-title manifest sha256 pinned; four gates unchanged.
Exit evidence emitted, archived in `reports/marvel/receipts/b1/`.

**B2 — speaker-attribution pilot (10 titles, all tiers; GPU window).**
This is the CSM "pilot's job" pattern: 10 titles end-to-end, measured cost,
council sets the scale budget. Nothing scales before the pilot numbers exist.
1. **Install (prereq):** ffmpeg (static or apt), `faster-whisper` (ASR,
   large-v3), `pyannote.audio` (diarization 3.1 — needs a free HF token,
   terms acceptance). Streaming audio: one title in flight, process → keep
   text/JSON, drop audio (35 GB free on /home; the full library would be
   ~250 GB — disk math recorded in the pilot receipt).
2. **Per title:** audio (T-YT: yt-dlp `--audio-only`; T-DP: downloader
   media) → faster-whisper ASR (forced-alignment timestamps) + pyannote
   diarization (per-line speaker cluster) → **deterministic mapping,
   closed-set, no-guess** (the JJK alias-table discipline):
   - candidate set for each title = the episode/movie's wiki
     `Appearances`/`Cast` list (S2 has both; Marvel DB animated shows carry
     voice-cast data) — a mapped speaker MUST be in that set (FK gate);
   - live-action: cluster → actor via per-scene cast where the scene is a
     closed set; otherwise the 27B mapping pass (GPU card-to-itself window)
     proposes character assignments, each stamped `confidence` + evidence
     quote; `confidence < 0.8` → `SPEAKER n (unmapped)`;
   - animation: recurring-voice consistency across episodes is the extra
     check (a character's cluster must be stable across the series;
     violations → re-cluster, not re-guess).
3. **Pilot exit (council):** measured per-episode cost (ASR min, diarization
   min, mapping calls, wall-clock), mapping gate violation count (target 0),
   and the budget ruling: full scale in GPU windows (ab-bay discipline: Qwen
   dial-down window, ~200–300 GPU-h estimated for the priority ~400 titles)
   vs CPU batch (32 cores; measured at pilot, ~5–8× GPU time — abort/shrink
   rule per CSM-P2 precedent: over budget → shrink to T1 priority titles,
   long tail keeps B1 text with `speaker: none` + named floor).
   **Named floor (pre-registered):** a title may end at text-only only if it
   has **no audio source at all** (no T-YT, no S7, no legal audio) — cause +
   retest trigger recorded. "Audio exists but mapping was expensive" is
   not a floor; it is budget, and budget goes to the council.

**B3 — scale (tiered).** T1: MCU movies (35) + flagship Disney+ series +
flagship animated series. T2: Netflix/ABC live-action. T3: animated long
tail. Each tier closes with the B-gate checks below + a council checkpoint.

**GATE B (council checkpoint, per tier and final).**
(1) CC text coverage of catalog = 100% or named floor (SQL: catalog rows
without a cc.db doc, cause column populated). (2) Speaker coverage: per-tier
`attributed / total lines`, reported with the named floor — the number, not
the phrase "done". (3) Mapping gate violations = 0 (FK: every mapped
speaker resolves to a wiki character node; closed-set: mapped speaker ∈
title's Appearances/Cast; verbatim: line text == source caption text, no
rewording — the JJK "never reword to pass" rule, mechanical here); (4)
temporal sanity: no speaker active at two overlapping timestamps (diarization
invariant, checked on stored rows); (5) four standing gates unchanged.
Council verdict per tier.

## 4. Phase C — Extraction & the full map ("every character, comic, event")

**C1 — T0 structured generation (free).** `page_gen` is series-agnostic
(Plan_to_perfection §4): point it at `marvel` + `mcu` `facts.db`; identity
fields declared in overrides (`Name`, `CurrentAlias`, `Title`, `Image`…
Marvel's infobox params are already human-readable keys, so the
`identity_fields:` map is short). Measure field coverage per wiki (the
readiness metric); a low number here buys a mapping-file entry, not a
campaign. Field specs come from the three-tier source (L8): the wiki's own
`/Documentation` page where it exists (Marvel DB — parse the empty-syntax
`<pre>` block + per-field meaning into a per-archetype spec), else the PIB
v5 `infoboxes` blob (after the L3 walker fix), else observed parameter keys.
A field in the spec but absent on a page is an empty fact, not an error;
a field *not* in the spec is kept and flagged (no silent drop — the detail
rule).

**C2 — category → relation edges (L5).** `category_relations:` override
grammar, generic mechanism: `{pattern: "*/Members", relation: member_of}`,
`{pattern: "*/Creator", relation: created_by}`, `{pattern: "*/casualties",
relation: event_participant, kind: casualty}`, `{pattern: "(\\d{4}) Character
Debuts", relation: debuted_year}`. Edges carry provenance
`category:<name>` + confidence. Gate: sampled against the infobox's own
affiliation/creator fields — a category edge contradicting the page's
infobox is a finding, not a keep.

**C3 — alias & universe alignment (deterministic).**
- Within-wiki: disambiguation `main_articleN` graph (A1b) + infobox
  `Name`/`CurrentAlias` (L2 hook) → canonical entity per (name, Earth-XXXX).
- Cross-corpus: `marvel` (Earth-616 canon) ↔ `mcu` (Earth-199999) ↔
  `marvel.com` ↔ `cc.db` speakers, via explicit alias tables in
  `overrides.yaml` (`subject_aliases:` shape) — never LLM-guessed; the
  MCU-wiki `Appearances` lists are the cross-check (a CC speaker mapped to
  "Iron Man" must appear in that movie's MCU-wiki Appearances list).

**C4 — events (D6 shape).** `ingest/events.py` precedent (JJK Phase 2):
two passes — (3a) placement set on `event`/`conflict`/`story_arc` types
(Marvel DB) + MCU movie/episode `Plot`/`Events` sections (cheap, gate-
proven first), then (3b) widen to character narrative sections (the
"Ragnarok Cycle / Civil War (Event) / One More Day" headings — event-named
sections, the JJK arc-heading finding: placement is structural where the
wiki files it under a heading). Event rows: `(subject, verb, object,
placement_key, section, quote, temporal)`, three-check gate (verbatim quote,
FK participants, placement exists **or** `temporal=false`), plus cross-page
agreement (the Civil War fight on Peter Parker's page, the event page, and
the CC episode must agree). **CC-derived events**: per-episode beat rows
from B2/B3 (episode = placement container; the MCU timeline spine).

**C5 — dimension map (JJK §12 shape; nothing scheduled without its
consumer + failing test).**
| dimension | source | consumer (the query it buys) |
|---|---|---|
| character → abilities/powers | `Power Template` pages + `Abilities` sections | "what can X do" |
| character → affiliations over time | `*/Members` categories + team pages | "who was in the Avengers in 1964" (state-over-time) |
| character → event history | C4 events + event-named sections | "what happened to X, in order" |
| comic issue → credits | `Comic Template` (writers/artists) + C8 if adopted | "who wrote Amazing Spider-Man #300" |
| comic issue → events/plots | `Comic Template` plot fields + episode/issue `Plot` | issue-level beat support for scripts |
| character → filmography | MCU wiki `Appearances`/`Cast` + CC speaker rows | "every MCU movie X is in, with what they did" |
| character → voice/dialogue | `cc.db` per-character dialogue (JJK `dialogue` door) | the character's actual lines — voice dataset |
Each row schedules only when the consumer names a real query and the
acceptance column names a test that can fail (the §12 rule, verbatim).

**C6 — question bank + census (CSM method seed).** `page-gen` T0 batch →
census (CSM v1 schema: class/subject/q/expect/hits/verdict, mechanical
term-count judge) + 200-row OOS protocol (seeded draw from the whole
population, no leak exclusion) + named-limit register. The bank is the
regression suite; the OOS is the anti-theater arm (the executing agent runs
it, never edits it).

**GATE C (council checkpoint).** D1 (every page covered or excluded in
writing — the exclusion file committed), D2 (archetype depth floors:
character/comic/event/film/series/episode/location, measured against
populated sections), D3 (zero unfiled engine gaps; red list not empty),
C-gate evidence: census baseline + OOS pre-score + `unknown`-type residue
report + four standing gates + `chunk-containment` (tier 0) for both wikis
at 0 unreachable (the JJK D5 class: chunker-skip vs oracle-content
divergence is checked before any prose work — the wave-0 pre-pass,
Plan_to_perfection §7).

## 5. Phase D — 100% declaration

**D1 — standing gates (per change, no exceptions).**
Four unchanged (pytest pin from CLAUDE.md, eval jjk, span-recall jjk,
canon opm) + Marvel set: pytest full, `eval --series marvel`,
**pytest GREEN definition (codified 2026-09-25, council A1c/A1b ruling):**
1,350 total = 1,345 passed + 2 xpassed + 3 failed, and the 3 failures must
be exactly the documented `:8000`-down `tests/test_mcp_server.py` env trio
(steady state = `:8000` down; the trio passes when it is up — never
deselect). Any other failure, or a trio failure on a non-env cause, is
RED; "ALL GREEN" while three fail is a definition error, not prose.
`chunk-containment --series marvel`, `eval --series mcu`,
`chunk-containment --series mcu`, census OOS re-score (floor per CSM
annex: OOS post ≥ pre − 2; a drop of 3+ voids), CC mapping-gate SQL
(§B gate 3) after any cc.db change.
Standing guards: 0 green→red counter-flips (a counter-flip rolls back its
mechanism alone); blind-set accuracy must not trail bank movement.

**D2 — blind fresh set (CSM Step 0 shape).** ~24 fresh Marvel questions
(named limit classes: universe-variant characters, event enumeration,
issue-level facts, state-over-time), corpus-verified expect terms, frozen
to `reports/marvel/blind_fresh.jsonl`, scored against the frozen build.
Fixes that move only the bank fail against it.

**D3 — D5 reachability exhaustive.** Pinned panel (hashed, not
`random.Random(7)` — the §2a trap), held-out split the executing agent
never sees, full tier-1 sweep (the real D5: the served bundle contains the
line) across qa/roster/narrative doors, miss file to zero (or a
documented floor with cause + retest).

**D4 — D6 consistency.** Event placement + cross-page agreement + CC-episode
agreement checks (§2b gates: one event in two placements, era-less event
rows, beat ordering contradicting an episode number, cross-page fact
disagreement) → zero violations.

**D5 — declaration (final council).** Only when: bank 100% green +
blind set at declared threshold + D3 miss file empty (or documented floor)
+ D4 zero violations + CC text coverage 100%/named floor + speaker
coverage number on the record + final four-gate green run +
`PHASE_MARVEL_100.md` declaration record. Remainder rows close by flip or by
explicit void-set criteria (cause + defect + retest pointer, council-
decided — never by phrasing). **That council, not this plan, declares
100%.**

## 6. GPU & resource discipline (carried from CSM_100_CLOSE)

- Steady state: Qwen at working dial, `:8000` down. Whole-card windows
  (Qwen dial-down, trap-restored to the exact argv) REQUIRED whenever the
  retrieval stack must co-locate or a 27B extraction batch runs — triple
  residency peaks above the 32 GB card.
- **Steady state re-measured 2026-09-25 (Qwen 153600 dial, owner switch line
  2026-09-25T03:50:38):** 5,462 MiB free of 32,607 MiB (nvidia-smi) — the
  owner's ~5 GB is the campaign's working VRAM.
- **GPU-only rule (owner directive 2026-09-25):** every model-bearing
  campaign task runs on the GPU (CUDA); the CPU is never a default. The one
  exception: the JEV systemone fast lane (local decision model, `~/tools/jev`)
  may take any task it can process faster than the GPU (triage, ranking,
  keep/drop, claim checks, voice lint) — JEV over CPU, never CPU. A CPU
  fallback requires a measured reason, recorded to the council.
- Gate runs (eval / span-recall / canon-run) co-locate the retrieval stack
  on CUDA within the ~5 GB (CSM precedent: gate stacks co-located at ~2.8 GB
  free under a 100k dial). 27B batches (B2 pilot, C4 extraction) still need
  the ab-bay whole-card window — a 27B does not fit 5 GB.
- B2 pilot + C4 extraction = 27B card-to-itself windows (ab-bay discipline;
  the invoking session directs only).
- CC audio processing (ASR + diarization): pilot measures it; GPU windows
  vs CPU batch is the B2 council ruling (budget in hours, abort/shrink
  rules, CPU-fallback number — a CPU fallback is a decision with a measured
  reason, never a default).
- Disk: 35 GB free — streaming audio (one title in flight), text/JSON
  retained, audio dropped; the pilot receipt records the disk math.
- State survival: commit BEFORE gates; never gate an uncommitted tree
  twice; re-crawls are hash/resume-driven (manifest sha256), never blind.

## 7. Halt, step semantics, councils

- Every step carries **PREMISE / VERIFY (exact command, exact tree) /
  IF HOLDS / IF REFUTED** (flow.md §14). A refuted premise halts the step,
  logs to `plan/deviation_reasons.md` with the raw output that refuted it,
  and surfaces. Refusal authority, not substitution authority.
- Halt conditions suspend the phase, not the run; the halt path runs a
  council first; a halt the council finds unresolvable inside the plan as
  written stops the run.
- Councils: GATE A, GATE B1, B2 pilot (budget), GATE B (per tier + final),
  GATE C, D5 final — plus cadence (a)/(b)/(c). All to
  `reports/marvel/COUNCIL_*.md`, committed with the work, DB-verified
  before recording.
- Drift-log entries: CC layer, marvel.com sub-store, Wikipedia sub-store
  (campaign-neutral additions, JJK-transcript precedent).

## 8. Open decisions (owner assets / scope — recorded, not asked at runtime)

- **D-1** Disney+ account for S7 (live-action CC + audio). Without it:
  live-action audio comes from S5/S6 where legal, and the B-gate named
  floor swallows the residue with causes. Owner can supply at any time;
  the catalog's `source_tier` picks it up without rework.
- **D-2** Scope boundary: Fox-era X-Men / Men in Black / 3rd-party
  licensed shows (e.g. Sony's Spider-Man 2017). Default: **in when
  Marvel-owned or Marvel-licensed** (the fandom wikis' own categories
  decide, not this plan); otherwise named-excluded with cause.
- **D-3** CC long-tail budget cap (B2 council sets the number; this plan
  pre-registers the abort/shrink shape only).
- **D-4** Wikipedia slice (S4). Default: yes (cheap; publisher history the
  fandom wikis omit).
- **D-5** OpenCLI browser-extension connection (one-time owner setup;
  precondition for the §1a rung-2 browser-grade fetches). Until it is done,
  rung 2 degrades to the per-platform CLI backends agent-reach has healthy
  (youtube: yt-dlp, ok today).