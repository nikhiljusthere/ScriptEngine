# decisions — A only; PREPEND (newest first). B never writes this file (hard rule 1).
# format: [ts] DEC <unit>-<seq>: APPROVE | VETO <rule> | REDO <rule> — re ESC <unit>-<seq>
#         [ts] NOTE <what>            <- wakes that touched §state without a pending ESC
[2026-09-08T11:17:27+05:30] DEC unit-t0-1: APPROVE — re ESC unit-t0-1
