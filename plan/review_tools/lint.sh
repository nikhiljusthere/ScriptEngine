#!/bin/bash
# lint.sh [--regate] [--show CHECK] [--json OUT] -- corpus-wide lint of the final big-v2 rows
cd /home/goblin/ScriptEngine/.claude/worktrees/big-review-flags
R=/home/goblin/ScriptEngine
SCRIPTENGINE_ROOT=$R exec $R/scriptengine/.venv/bin/python plan/review_tools/lint_v2.py "$@"
