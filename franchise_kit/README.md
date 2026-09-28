# Franchise kit: onboarding a new anime / fandom wiki to 100%

Everything needed to take a new franchise from "a wiki URL" to **a franchise brain**: every line understood, recallable and traceable, plus grounded reasoning over it (match-ups, hypotheticals, trajectories, with facts cited and assumptions labeled). It reuses the engine the earlier campaigns built. Distilled from JJK, CSM and Marvel/MCU (2026-09).

**Start with `RUNBOOK_100.md`.**

## What's here

| file | what it is |
|---|---|
| `RUNBOOK_100.md` | **The procedure**: the 100% = brain definition, roles (owner / Claude architect / opencode worker), GPU resource modes, the phases in order (acquire → survey and declare → understand → verify → declare), gates, and the time-saving rules |
| `DECISION_one_engine.md` | The structural decision: one shared engine; every wiki difference declared in `series/<name>/overrides.yaml`; new shapes become generic mechanisms + override keys (defaults inert); no per-franchise code |
| `OVERRIDES_REFERENCE.md` | Every `overrides.yaml` key: the code that reads it, its purpose, an example |
| `overrides.template.yaml` | An annotated starting `overrides.yaml` for a new wiki |
| `PLAN_TEMPLATE.md` | The campaign-plan skeleton (`plan/<NAME>_100_PLAN.md`) |
| `LESSONS.md` | Traps already paid for: the symptom, how to detect it in minutes, the fix |
| `CAMPAIGN_TOOLS.md` | Which `tools/marvel/*` scripts to reuse (promote to `tools/franchise/` with `--series`) and which are Marvel-only |
| `prompts/WORKER_PROMPT.template.md` | The opencode worker prompt skeleton |
| `tools/survey_wiki.py` | **Structure survey** (model-free, read-only, seconds): types, where the narrative lives, missed headings, placement types, time-axis signals, reality/partition, disambiguation hazards, speed indexes. Writes `reports/<series>/SURVEY.md` + suggested overrides |
| `tools/oc_status.py` | The worker's state from opencode's own session records (WORKING / STOPPED + last message) |
| `tools/oc_send.sh` | Type a reply into the worker's TUI (idle-only), then verify delivery in opencode.db |

## Quick start (new franchise `<name>`)

```bash
# Phase A: acquire (worker), then audit
python -m scriptengine.cli crawl --series <name> --start-url <any wiki page>
python -m scriptengine.cli audit --series <name>
# Phase S: survey and declare (architect)
python -m scriptengine.cli index --series <name> --no-embed
scriptengine/.venv/bin/python franchise_kit/tools/survey_wiki.py --series <name>
cp franchise_kit/overrides.template.yaml series/<name>/overrides.yaml   # then fill from SURVEY.md
python -m scriptengine.cli index --series <name>
python -m scriptengine.cli chunk-containment --series <name>            # must be 0 unreachable
# Phase C / D: follow RUNBOOK_100.md §3 steps 11–23
```

The engine code itself lives in `scriptengine/` and is versioned in git. This folder holds the method, the templates and the architect's tools, not a copy of the engine.
