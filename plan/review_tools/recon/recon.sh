#!/bin/bash
# recon.sh build | check C... | check all | view C  -- reconcile overlapping big-v2 windows
# view C: the component's diffs, then every window in it (full text + final rows + flags)
D=/home/goblin/ScriptEngine/.claude/worktrees/big-review-flags/plan/review_tools/recon
R=/home/goblin/ScriptEngine
P=$R/scriptengine/.venv/bin/python
cd $D
case "$1" in
  build) SCRIPTENGINE_ROOT=$R $P recon_build.py ;;
  check) shift; SCRIPTENGINE_ROOT=$R $P recon_check.py "$@" ;;
  view)
    SCRIPTENGINE_ROOT=$R $P recon_check.py $2
    for b in $($P -c "import json;[print(*c['windows']) for c in map(json.loads,open('$R/series/universal/training/big/recon/components.jsonl')) if c['c']==$2]"); do
      bash $R/.claude/worktrees/big-review-flags/plan/review_tools/rv.sh view 1 --from $((b-1)) | grep -v '^\[printed' | grep -v '^ EVENTS\|^ FACTS\|^ TAGS\|^ DROPPED'
    done
    SCRIPTENGINE_ROOT=$R $P recon_rows.py $($P -c "import json;[print(*c['windows']) for c in map(json.loads,open('$R/series/universal/training/big/recon/components.jsonl')) if c['c']==$2]") ;;
  *) echo "usage: recon.sh build | check C...|all | view C" ;;
esac
