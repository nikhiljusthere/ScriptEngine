**Day-1 order** (plain terminal first; nothing starts unattended before T0–T3 pass):
1. Preflight: `curl -m 2 http://127.0.0.1:18080/v1/models`; `cat /home/goblin/ninfer-work/qwen_mode.txt` (today: 135168, vision=on, api=cpu). Write `tools/pcloop/loop.py` from §5.2, plus a key-combo denylist (risk 3).
2. Bootstrap the four state files; seed `state.md §state` with next-unit=CSM-1 (per SWITCHPOINT), a_session/b_session empty; named-path commit.
3. **T0 — the single first end-to-end test**, before A, before any CSM work: B runs one trivial unit (`git log --oneline -1` → DONE line + one ESC into `§B updates`); A then writes the matching DEC and records a_session. Done = all three files show the B-append → A-decide round-trip inside ~10 min. This is the gate before T1–T3.
4. PC loop: `setsid`-launch `loop.py`, TASK = "new terminal tab; type `pcloop-ok`; Return; `done`". Done = `ps` shows it, ACT lines land in `work_log.md`, clean `done` exit.
5. T1→T3 in plan order. T1's switch is `ninfer-work/qwen-switch.sh 100k` (the plan's `./qwen-switch.sh` path is wrong; pass `--api` explicitly — current state is api=cpu).
6. First real unit CSM-1: stamp `questions/csm.json` via `tools/csm/stamp_revids.py`; standing gates; commit.

**Day-1 done:** T0–T3 green, CSM-1 committed, the loop completed one bounded session, `decisions.md` advancing (A alive).

**What breaks first / who pays:**
1. **§4.4's A-loop is Python but A is an LLM, not a daemon** — pi doesn't execute `while True` for days; each 60 s poll is a model turn, so A bloats on its own turns, then overflows itself or auto-compaction summarizes the strategy away (silently). Most likely day-2 failure — in A, not B. Fix day 1: event-driven A (wake on ESC/staleness) + a one-line tick in `state.md` per wake.
2. **B's `ls -1t *.jsonl | head -1` session discovery races** — two foreign pi sessions already live in that directory; a wrong `b_session` means A later resumes someone else's transcript after a death. B should log `$PI_SESSION_FILE` as its first `work_log` line; A reads that.
3. **`key` has no denylist** — a hallucinated `ctrl+alt+BackSpace` or `alt+F1` kills the X session or bounces a tty; `type` racing the owner's own keystrokes in an active terminal yields corrupted commands. Cost: session reset + owner attention. Day-1 mitigation: a dedicated window + the combo denylist.
4. **Silent HALTs** — T1's 30–60 s model-less window turns into 5 vision FAILs = no-op streak = HALT, visible only in a `work_log` line nobody is watching (A dead ⇒ quiet `decisions.md`). Money: zero (all local); attention: all of it.