"""D7 window per-leg target check (council #36, Q4).

Usage: check_targets.py <leg>      leg in {A, B, C}

Bars, one per leg (all must hold for PASS):
  W >= 469            greens in THIS leg's p23 census
  flips superset      every registered flip row is MECH_GREEN in this leg
  0 counter-flips     no 469-era (git-HEAD) green row is red in this leg
  blind 19/19         all 19 blind rows MECH_GREEN
  d6_flip rc == 0     OOS floor: no green30 flip, no oos200 drop >= 3

Counter-flip baseline is the 469-era census captured at pre-stage
(snapshots/census_head_469.jsonl == `git show HEAD:...`), the same reference
d6_flip diffs against. The leg census / blind file are the ones just rewritten
by this leg's p23_grader / blind_score.

Prints one verdict line (`PASS <leg>` or `RED <leg>: <reasons>`) then one
info line (`FLOOR <leg>: ...`) that never starts with RED. The chain greps
`^RED`, so exit code is always 0.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SNAP = ROOT / "reports/csm/receipts/d7_window/snapshots"

BASELINE = SNAP / "census_head_469.jsonl"          # 469-era git-HEAD census
CENSUS = ROOT / "reports/csm/census_widened_csm_results.jsonl"  # this leg
BLIND = ROOT / "reports/csm/blind_fresh_d7_results.jsonl"      # this leg
D6FLIP = ROOT / "tools/csm/d6_flip.py"

# registered flips per leg (Q4): rows that must be MECH_GREEN in the leg census
FLIPS = {
    "A": ["csm-dim-arcn-02", "csm-dim-arcn-10", "csm-dim-org-03", "csm-dim-state-08"],
    "B": ["csm-abl-pool-140", "csm-abl-pool-358"],
}
FLIPS["C"] = FLIPS["A"] + FLIPS["B"]

# 16 Phase-2 floor rows = the 17 git-HEAD p23 reds minus the org-03 D7 holdout
FLOOR16 = [
    "csm-abl-pool-140", "csm-abl-pool-358",
    "csm-dim-abl-01", "csm-dim-abl-02", "csm-dim-abl-09",
    "csm-dim-arcn-02", "csm-dim-arcn-03", "csm-dim-arcn-04",
    "csm-dim-arcn-06", "csm-dim-arcn-08", "csm-dim-arcn-10",
    "csm-dim-caus-03",
    "csm-dim-state-02", "csm-dim-state-03", "csm-dim-state-08", "csm-dim-state-09",
]


def greens(path: Path) -> set:
    return {json.loads(l)["id"] for l in path.read_text().splitlines()
            if l.strip() and json.loads(l).get("verdict") == "MECH_GREEN"}


def blind_rows(path: Path):
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


def main() -> None:
    leg = sys.argv[1] if len(sys.argv) > 1 else "?"
    if leg not in FLIPS:
        print(f"RED {leg}: unknown leg (want A, B or C)")
        return

    base_g = greens(BASELINE)
    leg_g = greens(CENSUS)
    brows = blind_rows(BLIND)
    blind_g = {r["id"] for r in brows if r.get("verdict") == "MECH_GREEN"}

    reasons = []
    W = len(leg_g)
    if W < 469:
        reasons.append(f"W={W}<469")

    missing = sorted(set(FLIPS[leg]) - leg_g)
    if missing:
        reasons.append("missing flips: " + ", ".join(missing))

    counter = sorted(base_g - leg_g)
    if counter:
        reasons.append(f"{len(counter)} counter-flips: " + ", ".join(counter))

    if len(brows) != 19 or len(blind_g) != 19:
        bad = sorted({r["id"] for r in brows} - blind_g)
        reasons.append(f"blind {len(blind_g)}/19 (rows={len(brows)}; "
                       f"not-green={bad or 'n/a'})")

    d6 = subprocess.run([sys.executable, str(D6FLIP)],
                        capture_output=True, text=True)
    if d6.returncode != 0:
        tail = " ".join(d6.stdout.split())[-160:]
        reasons.append(f"d6_flip rc={d6.returncode} ({tail})")

    if reasons:
        print(f"RED {leg}: " + "; ".join(reasons))
    else:
        print(f"PASS {leg}")

    flipped = [r for r in FLOOR16 if r in leg_g]
    print(f"FLOOR {leg}: {len(flipped)}/16 flipped: "
          f"{', '.join(flipped) if flipped else '-'}")


if __name__ == "__main__":
    main()