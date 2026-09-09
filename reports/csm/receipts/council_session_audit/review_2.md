# Peer review 2

**Q1 — Strongest:** A. Its load-bearing claims all verify on disk (recall_verbatim.jsonl holds exactly 685 ERROR rows; /tmp/csm_iter1_records is absent; R-2/R-3 still uncommitted). It correctly names the critical path — gated state living outside git, one reboot erasing two work-days — and quantifies the governance churn (133 commits, only 4 CSM engine commits). D is a close second (doc contradictions are real), but its CI alternative is a rhetorical straw man.

**Q2 — Shared blind spot:** all five take JJK D6's done-state on faith. A and C say "open (P0–P5)"; B and D cite DONE_DECLARATION.md (09-07). Verified: the file exists and declares D1–D10 closed. Two of five confidently assert the opposite of disk; the unverified-claim pattern the audit's own CORRECTION lines flag runs through all five.

**Q3 — What I'd add:** a single machine-readable ledger-of-record, committed to git (done/gated/uncommitted/next-action; one file; updated at each gate close). A diagnoses the fragility but only prescribes "commit now"; nothing makes the state machine-readable, which is what would make reboots cost zero and the 2-hour re-verification councils obsolete.