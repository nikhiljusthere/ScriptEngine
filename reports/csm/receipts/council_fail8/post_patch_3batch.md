# Post-patch 3-batch receipt (the batches outside the closure8 sweep)

The remap's regression profile (decision (c) in the framed question) needed
three more batches that closure8 did not cover. Run this session against the
live :8000 (CUDA, server started 2026-09-17T14:24:38Z), working tree carrying
the full FAIL8 patch (Weapon Devils trimmed to 7 devils).

| batch | run folder | result |
|---|---|---|
| yoru | `csm-yoru-2026-09-17-1556` | **17/17** — sets exact 11/11, canon 98/98, facts 6/6 |
| asa_mitaka | `csm-asa_mitaka-2026-09-17-1556` | **16/16** — sets exact 10/10, canon 64/64, facts 6/6 |
| fourth_east_high_school | `csm-fourth_east_high_school-2026-09-17-1556` | **4/4** — facts 4/4 |

All rc=0 (page-run exit code 0 = 100%).

Note for decision (c): yoru's affiliation gold IS "Fourth East High School
(formerly)" — the reviewer-4 "not listed" claim was partly wrong (only yoru
carries the suffix; asa_mitaka/death_devil/fami list it plain; makima/nayuta
don't list Fourth East at all) — and the remap did not break it: 17/17 green.

GPU: Qwen 100k profile (PID 495401) alive before and after; sanctioned
co-located steady state preserved.