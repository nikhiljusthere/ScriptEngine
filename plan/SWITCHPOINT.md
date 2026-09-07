# SWITCHPOINT — the resume file for Qwen mode switches

pi's model is the Qwen server: while the server is reloading the agent has no
model, and after reopening pi the *transcript* may be discarded (small
contexts compact fast). So everything needed to continue must live here, on
disk, **before** `qwen-switch.sh` runs. Fill the hand-written section before
every switch; `qwen-switch.sh` appends machine lines to the switch log — never
edit those.

## Current position (hand-written — fill BEFORE every switch)

- mode: 262k (current) → ____ (target)
- git: ____________ (sha of a clean commit)
- trunk/excursion address (drift_log §4): ____________
- work explanation (what's done, what's in flight, the exact next step):
  -
- open questions / risks:
  -
- first action on resume:
  -

## Switch log (machine-appended by qwen-switch.sh)

- (none yet)