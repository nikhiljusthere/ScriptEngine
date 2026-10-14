#!/bin/bash
# pre27.sh run LIST [--workers N] | show B..  -- 27B pre-review for the lint pass (see pre27.py)
cd /home/goblin/ScriptEngine/.claude/worktrees/big-review-flags
R=/home/goblin/ScriptEngine
SCRIPTENGINE_ROOT=$R exec $R/scriptengine/.venv/bin/python plan/review_tools/pre27.py "$@"
