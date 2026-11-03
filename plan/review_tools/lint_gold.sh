#!/bin/bash
# lint_gold.sh [--regate] [--show CHECK] [--json OUT] -- read-only lint of the gold v2 audit (see lint_gold.py)
cd /home/goblin/ScriptEngine/.claude/worktrees/big-review-flags
R=/home/goblin/ScriptEngine
BV2_SET=gold SCRIPTENGINE_ROOT=$R exec $R/scriptengine/.venv/bin/python plan/review_tools/lint_gold.py "$@"
