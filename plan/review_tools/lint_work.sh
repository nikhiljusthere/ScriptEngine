#!/bin/bash
# lint_work.sh build | show B  -- reading lists for the lint pass (see lint_work.py)
cd /home/goblin/ScriptEngine/.claude/worktrees/big-review-flags
R=/home/goblin/ScriptEngine
SCRIPTENGINE_ROOT=$R exec $R/scriptengine/.venv/bin/python plan/review_tools/lint_work.py "$@"
