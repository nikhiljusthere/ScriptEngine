# Calibrating the precision filter against the canon bank (jev-calibrate)

`jev-calibrate` (smkrv) tunes a Jev question against labelled examples and gives
it a verdict: `gate`, `gate-above-confidence`, `ranker`, `unusable`. Here the
question is the index-time precision filter's `canon_member` noul, and the
labels come from two places the repo already trusts:

- **positives**: canon items in `questions/<series>.json`, the online-canon
  bank (every item verified against its cited page);
- **negatives**: intruders from `scriptengine/eval/diagnose_intruders.py`
  (`reports/*/canon_scores_intruders.json`), members a roster returned that
  the bank does not hold.

Caveat: an intruder is "not in the bank", and the bank can be incomplete, so
a few negatives may really be canon.

Everything runs against the local stack only (`~/tools/jev`): the gateway on
`:8018`, fast lane = decider-0.8b on CPU, deep lane = NInfer on `:18080`
(concurrency 1, refused while opencode runs). No cloud key is involved;
`TYPESAFE_API_KEY=local` is a dummy.

## Build the set

```bash
python tools/jev/build_calibration_set.py --limit 50            # 25 canon + 25 intruders
python tools/jev/build_calibration_set.py --series opm --limit 50
```

This writes `tools/jev/calibration/questions.json` and `examples.jsonl`. The
examples are grouped by bank question, so a question's items never straddle
tune and holdout.

## Run it (exact commands)

```bash
source ~/tools/jev/jev.env
J="node $HOME/tools/jev/src/jev-calibrate/dist/cli.js"     # or ~/tools/jev/bin/jev-calibrate

$J lint  --dir tools/jev/calibration
$J check --dir tools/jev/calibration --split tune \
         --base-url http://127.0.0.1:8018 --model jev-latest --concurrency 2
# edit criteria only, re-check, then:
$J compare --dir tools/jev/calibration
$J check --dir tools/jev/calibration --split holdout \
         --base-url http://127.0.0.1:8018 --model jev-latest --concurrency 2
```

The deep lane is selected by header, which jev-calibrate cannot set, so a
fast-vs-deep comparison goes through `--model deep` (the gateway maps the model
name `deep` to NInfer). Keep it to a handful of examples and never while an
opencode session is live.

## First run (2026-09-24, 50-item slice, fast lane, `--split all`)

```
split all, 1 run, typesafe, decider-0.8b-v1
50 examples checked, 0 not checked, 50 requests, 271.9 s
canon_member  [noul]  threshold 0.50
  verdict    unusable
             AUC 0.47 is below 0.85, and at 0.50 precision 0.50 and recall 0.08 miss the targets
  means      0.29 when true, 0.30 when false
  Brier      0.32
```

Reading: with only `{series, question, subject, item}` in the state, the 0.8B
fast-lane model cannot tell a canon technique from an intruder (AUC at
chance). That is the expected failure mode: the name alone does not carry the
evidence. The next revision has to put evidence in the state, i.e. the page
section the member came from (`section`, `bucket` source, the lead of the
item's page), which is what `tools/jev/precision_filter.py` builds. Re-run the
same commands after changing the state shape; `--split all` above was a look
around, and the ledger now marks those holdout examples as seen, so report only
a fresh holdout.

(`271.9 s` for 50 requests is CPU contention with other jobs on the fast lane,
not the model's normal latency.)
