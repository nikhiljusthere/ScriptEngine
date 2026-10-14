#!/bin/bash
# lint_fix.sh [--dry] -- mechanical rule-decided fixes of the final big-v2 rows (see lint_fix.py)
cd /home/goblin/ScriptEngine/.claude/worktrees/big-review-flags
R=/home/goblin/ScriptEngine
SCRIPTENGINE_ROOT=$R exec $R/scriptengine/.venv/bin/python plan/review_tools/lint_fix.py "$@"
