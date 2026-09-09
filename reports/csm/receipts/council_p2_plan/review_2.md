# Review 2 (peer reviewer, anonymous) — council_p2_plan

**Q1 — Strongest: B.** Only response with double-verified load-bearing numbers: the plan prices 51 h off pre-pin 15,400; the pin is 17,181 rows (verified: `panel_csm.json`) → 57.3 h; csm-3 (d)(2) already ruled 4 s/probe "fiction" and mandated the sanity re-estimate; the only CSM rate on disk is 8.5 s/probe CPU@150k (verified: commit f81a1af) → ~122 h, 2.5× budget. B alone catches the null branch: P1.4 can close all 21 reds (verified 8/6/5/1/1 from the raw jsonl) → P2.3 no-ops, yet P2.5 signs 100 % with no comprehension layer; B makes it a voiding condition.

**Q2 — Shared blind spot:** none of A–E fights the sweep machinery csm-3 (d)(1) already mandated: no sweep spec or per-door floor policy exists on disk; roster/narrative are structurally low-yield, so the 51 h arm false-halts before it produces a number. Nobody gates P2.1 on that spec's existence.

**Q3 — Add:** the panel already hash-stamps and re-checks at load (Ruling 7; `panel_csm.json` stores `hash`; CLI recomputes from rows) and the held-out door is fixed — E's hash-stamp is a redundant spec. Per csm-3 (d)(4), record per-door raws + panel hash in GATE.md.