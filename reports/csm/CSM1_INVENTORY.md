# CSM-1 INVENTORY — the CSM seed bank (2026-09-08)

Council item 1 (`reports/csm/COUNCIL_csm-campaign.md`): inventory + revid-stamp the
existing CSM seed bank; zero new questions. Raw receipts only.

## Files

| artifact | contents |
|---|---|
| `questions/csm.json` | 39 active questions + 1 retired; wiki `https://chainsaw-man.fandom.com`; bank `updated: 2026-08-15` |
| `questions/_csm_relations.json` | 11 relation-set questions |
| `series/csm/overrides.yaml` | 20 declared rosters (11 with explicit members, 9 category-style with none) |

## Revid stamps (fetched 2026-09-08, `tools/csm/stamp_revids.py`)

- `questions/csm.json`: 39/40 entries stamped `source_revid`
  (all 39 active questions stamped; the 1 retired entry has no `sources` key -> `source_revid: null`, correct, nothing to pin)
- `questions/_csm_relations.json`: 11/11 stamped
- 18 distinct wiki source pages pinned, 0 unpinnable. Per-title map in each file under `revids`:

| page | revid | last edit |
|---|---|---|
| Aki Hayakawa | 44532 | 2026-07-27T08:43:32Z |
| Asa Mitaka | 44657 | 2026-09-04T05:25:07Z |
| Chocolate | 40844 | 2025-12-02T16:01:06Z |
| Death Devil | 44650 | 2026-08-31T05:32:37Z |
| Denji | 43187 | 2026-03-25T19:02:48Z |
| Devil | 44646 | 2026-08-28T19:47:08Z |
| Famine Devil | 44656 | 2026-09-04T05:23:35Z |
| Four Horsemen | 44644 | 2026-08-27T11:24:52Z |
| Future Devil | 44404 | 2026-07-07T11:39:40Z |
| Himeno | 44498 | 2026-07-24T07:08:02Z |
| Hybrid | 44379 | 2026-07-05T08:33:14Z |
| Makima | 44595 | 2026-08-05T20:12:58Z |
| Meowy | 43176 | 2026-03-25T18:25:06Z |
| Pochita | 43189 | 2026-03-25T19:08:40Z |
| Power | 44435 | 2026-07-11T20:27:21Z |
| Tokyo Special Division 4 | 43635 | 2026-05-20T20:04:03Z |
| Weapon Devils | 43348 | 2026-04-06T08:02:46Z |
| Yoru | 44649 | 2026-08-30T06:47:37Z |

Non-wiki sources (left unpinned, no revid possible):

- `csm-set-02`: `https://www.cbr.com/power-chainsaw-man/` (its first wiki source is pinned; the cbr URL is corroboration only)

## Declared rosters (`series/csm/overrides.yaml`, 20)

| roster | members |
|---|---|
| The Public Safety special divisions | 5 |
| Every devil contract Denji has made | 3 |
| Every blood weapon Power can create | 7 |
| Every devil Aki Hayakawa contracted with | 4 |
| Every devil whose power Makima can channel through her control ability | 6 |
| Every division Himeno was affiliated with in Public Safety | 1 |
| How many members are in the Four Horsemen | 4 |
| Tokyo Special Division 4 | 14 |
| Weapon Devils | 7 |
| Aki Hayakawa's devil contracts | 3 |
| Himeno's abilities | 2 |
| Devils | 0 (category-style) |
| Devil Hunters | 0 (category-style) |
| Hybrids | 0 (category-style) |
| Fiends | 0 (category-style) |
| Humans | 0 (category-style) |
| Four Horsemen | 0 (category-style) |
| Primal Fear Devils | 0 (category-style) |
| Devil Tiers | 0 (category-style) |
| Groups | 0 (category-style) |

## Verification (this run)

```
questions/csm.json: 39 q + 1 retired, stamped=39/40, revids_map=18
questions/_csm_relations.json: 11 q + 0 retired, stamped=11/11, revids_map=18
```

## Incident (raw receipt)

First run of `tools/csm/stamp_revids.py` (committed `6a87479`) **wiped the questions
lists**: a tuple-unpack swap (`prev_maps[f] = (prev, data)` stored, `data, prev =`
unpacked reversed) wrote the empty *prev* revid map instead of the full file dict.
Both files restored from git (`git checkout --`), the unpack fixed in-tool with a
comment naming the bug, and the stamp re-run is the one recorded above.

