# Session org record (2026-09-08)

Goal: open pi, walk `/resume`, rename + delete unneeded sessions (owner-watched).

**Final state** (disk-verified; the /resume picker renders these names):
- kept + named: `CSM-stuck-RESUME-0907` (01a07cab — the paused-campaign resume point, protected),
  `B-T0-work-pane`, `A-T0-ESC-ruling`, `A-BSTALE-1..4`, `A-escalation-1142`; the active pi session (01a07f33) left unnamed/touched.
- trashed (reversible, `~/.local/share/Trash/files/`, via trash-cli): 01a07f38 (pi-update scratch),
  01a07c1b + 01a07c93 (yesterday's D6 campaign runs — outcomes in git), 2× `--tmp--` scratch.

**The incident (lesson):** the first pass was a *blind* xdotool key batch through the picker
(rename ×5, delete ×3, no per-op verification). pi's rename leaves the selection such that the
next `Down` lands one line short → names drifted onto the wrong sessions (double-concatenated
`A-BSTALE-3A-BSTALE-2` included) and one delete hit `a-1788846435` instead of L7.
Recovery: everything trashed came straight back from the trash sink; names were then fixed
*deterministically at disk level* (append a `session_info` record — same schema pi writes,
last record wins) instead of re-fighting the UI.
**Rule:** UI-driven key sequences get one screenshot + disk check *per operation*; when the
on-disk representation is a simple append-only record, fix state at that level and use the UI
for the visible pass only.

**Also found:** pi's `/delete` is permanent without the `trash` CLI — installed `trash-cli`
(apt, 1 pkg) so the UI delete path is reversible.
