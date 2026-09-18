"""D6 closure flip analysis (offline): pre-486 (git HEAD) vs post-486 (worktree).

Prints: totals, red->green and green->red flips with ids, OOS200 post-vs-pre
delta, green30 flip count. Exit 2 if any green30 flip or OOS drop >= 3.
"""
import json
import subprocess
import sys

PRE_RAW = subprocess.run(
    ["git", "show", "HEAD:reports/csm/census_widened_csm_results.jsonl"],
    capture_output=True, text=True, cwd="/home/goblin/ScriptEngine",
    check=True).stdout
pre = {}
for line in PRE_RAW.splitlines():
    if line.strip():
        r = json.loads(line)
        pre[r["id"]] = r.get("verdict")

post = {}
with open("/home/goblin/ScriptEngine/reports/csm/census_widened_csm_results.jsonl") as f:
    for line in f:
        if line.strip():
            r = json.loads(line)
            post[r["id"]] = r.get("verdict")

assert set(pre) == set(post), "row id mismatch pre vs post"
g = lambda v: v == "MECH_GREEN"
pre_g = sum(1 for v in pre.values() if g(v))
post_g = sum(1 for v in post.values() if g(v))
r2g = sorted(i for i in pre if not g(pre[i]) and g(post[i]))
g2r = sorted(i for i in pre if g(pre[i]) and not g(post[i]))
print(f"pre {pre_g}/486 green, post {post_g}/486 green")
print(f"red->green ({len(r2g)}): {r2g}")
print(f"green->red ({len(g2r)}): {g2r}")

oos = [json.loads(l) for l in
       open("/home/goblin/ScriptEngine/reports/csm/D6_OOS_PRE.jsonl")
       if l.strip()]
oos_rows = [r for r in oos if r.get("set") == "oos200"]
grn_rows = [r for r in oos if r.get("set") == "green30"]
print(f"oos bank: {len(oos_rows)} oos200 + {len(grn_rows)} green30")

def post_verdict(rid):
    return post[rid]

oos_pre_g = sum(1 for r in oos_rows if g(r.get("verdict")))
oos_post_g = sum(1 for r in oos_rows if g(post_verdict(r["id"])))
print(f"oos200: pre {oos_pre_g}/{len(oos_rows)} -> post {oos_post_g}/{len(oos_rows)} "
      f"(delta {oos_post_g - oos_pre_g})")
grn_flips = [r["id"] for r in grn_rows
             if g(r.get("verdict")) and not g(post_verdict(r["id"]))]
print(f"green30 flips: {len(grn_flips)} {grn_flips}")

rc = 0
if grn_flips:
    print("VOID: green->red flip in frozen sample")
    rc = 2
if (oos_post_g - oos_pre_g) <= -3:
    print("VOID: oos drop >= 3")
    rc = 2
sys.exit(rc)
