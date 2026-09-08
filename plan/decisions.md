# decisions — A only; PREPEND (newest first). B never writes this file (hard rule 1).
# format: [ts] DEC <unit>-<seq>: APPROVE | VETO <rule> | REDO <rule> — re ESC <unit>-<seq>
#         [ts] NOTE <what>            <- wakes that touched §state without a pending ESC