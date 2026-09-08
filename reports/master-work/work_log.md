# work log — B only, APPEND at EOF (never rewrite; the pcloop appends its own ACT/FAIL/HALT lines).
# format: [ts] KIND <unit>: detail    KIND ∈ DONE/ACT/FAIL/HALT
# B's first line after boot: [ts] ACT boot: b_session=$PI_SESSION_FILE (its own env var — never `ls` the session dir)