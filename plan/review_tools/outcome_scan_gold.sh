#!/bin/bash
# outcome_scan_gold.sh [--class C] [--list OUT] [--quiet] | check FILE -- read-only outcome-ruling scan (see outcome_scan_gold.py)
cd /home/goblin/ScriptEngine/.claude/worktrees/big-review-flags
R=/home/goblin/ScriptEngine
BV2_SET=gold SCRIPTENGINE_ROOT=$R exec $R/scriptengine/.venv/bin/python plan/review_tools/outcome_scan_gold.py "$@"
