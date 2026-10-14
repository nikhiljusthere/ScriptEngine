#!/bin/bash
# start the terminal Claude session that owns the lint pass + gold v2 + compose/train (2026-10-14)
cd /home/goblin/ScriptEngine/.claude/worktrees/big-review-flags
exec claude "Read plan/RESUME_HANDOFF_2026-10-14b.md fully and follow its reading order (owner rules in plan/RESUME_REVIEW_HANDOFF_2026-10-10.md section 1 first). You now own all remaining work: the lint reading pass over the 14k big v2 windows (27B pre-reviews, you review every 27B answer before submitting), the gold v2 backfill and review, then compose events+facts+tags and train the 9B. The owner wants the dataset flawless before training. Continue inline, no subagents; never push."
