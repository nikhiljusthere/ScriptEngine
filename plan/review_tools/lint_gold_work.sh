#!/bin/bash
# lint_gold_work.sh build [--regate JSON] | show B -- gold v2 lint reading list (see lint_gold_work.py)
cd /home/goblin/ScriptEngine/.claude/worktrees/big-review-flags
R=/home/goblin/ScriptEngine
BV2_SET=gold SCRIPTENGINE_ROOT=$R exec $R/scriptengine/.venv/bin/python plan/review_tools/lint_gold_work.py "$@"
