#!/bin/bash
# lint_gold_fix.sh build | apply [--yes] [--allow-missing] -- M1-M6 on the reviewed gold audit (see lint_gold_fix.py)
cd /home/goblin/ScriptEngine/.claude/worktrees/big-review-flags
R=/home/goblin/ScriptEngine
BV2_SET=gold SCRIPTENGINE_ROOT=$R exec $R/scriptengine/.venv/bin/python plan/review_tools/lint_gold_fix.py "$@"
