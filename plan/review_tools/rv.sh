#!/bin/bash
# rv.sh view N | fix FILE | mark B   — big_review_v2 from the worktree with the main checkout's data
cd /home/goblin/ScriptEngine/.claude/worktrees/big-review-flags
R=/home/goblin/ScriptEngine
SCRIPTENGINE_ROOT=$R exec $R/scriptengine/.venv/bin/python tools/train/big_review_v2.py "$@"
