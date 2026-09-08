// COUNCIL_csm-3 runner (pi-subagents workflowScript body — plain statement
// body, top-level await, NO export/meta line). Owner rule 2026-09-08: the
// five advisors, the five peer reviewers, then the chairman run ONE AT A
// TIME (sequential; at 262k the children would fight Qwen's shared KV pool).
// House format follows reports/csm/COUNCIL_csm-1b-2.md; the chairman writes
// the record to reports/csm/COUNCIL_csm-3.md (the campaign session commits).

const QUESTION = [
  'CSM 100% campaign (ScriptEngine repo, /home/goblin/ScriptEngine) — cadence council (standing rule 3a: review the fixes just made, before the next item starts).',
  '',
  'Just completed:',
  '(1) Gate re-baseline on the 1,249 tree (gpu-gate3 100k+CUDA side session, receipt reports/csm/GATE_REBASELINE_2.md, commit 2c80867): all four standing gates PASS on CUDA (pytest 1,249/1,249 incl. the 6 VRAM-sensitive test_context cases; eval jjk 31/31; span-recall jjk 48,572/48,572 offline + 390/400 live probe; canon opm 10/16 exact, 236/236, 79.0%). CLAUDE.md + the gates-skill baselines rewritten (1,242 -> 1,249); the CSM gate section opened in reports/comprehension/GATE.md as the live record.',
  '(2) CSM-3 (commit f93d396) — D5 measurement infrastructure, the four §2a traps: (a) pinned hashed probe panel — build_panel() in scriptengine/eval/span_recall.py (deterministic (title,section,sentence) order, sha256 hash stamped, seeded 200-row held-out split written to a side file the executor never opens; the csm panel is pinned at reports/csm/panel_csm.json, hash e3d73720…, 17,181 sweep + 200 held-out = 17,382 tier-0-eligible lines); (b) wired resume — the pinned recall() path keys done on (title,sentence), rewrites the results jsonl (no append-dup), re-probes transient ERROR rows, crash-tolerant .new sidecar; (c) hit_rate divides by the FULL panel denominator, not rows run; (d) all three doors — the --door CLI option forces the /context mode param (qa | roster | narrative) with a per-door sweep_<door>.jsonl, plus --sanity N whose zero-hit subset halts with exit 3 (council addendum: per-door sanity floor); plus (f) the tier-0 rename span-recall -> chunk-containment (span-recall kept as alias, both registered + tested); and the <6-word short-line floor decided BEFORE panel pinning per ruling 4b: the exclusion is recorded, not silent — CSM census of 775 sub-6-word lines (all tier-0-eligible, all chapter/volume-list rows like "College Fund 158.") recorded in series/csm/overrides.yaml. 4 new tests; pytest 1,253 (1,249 + 4) green (CPU run; the 6 VRAM cases pass on CPU in 127 s).',
  '',
  'Standing campaign rules to judge against: measurement-infra-only pass (zero gold authoring); raw receipts, never "100%" prose; no series name in any .py (per-wiki handling in series/csm/overrides.yaml or tools/csm/ only); the JJK baseline stays untouched (the legacy --probe 400 JJK gate path must behave identically — verify it); §9a — the agent that made the fix never runs the sweep that grades the fix (CSM-4, the exhaustive 17,181 x 3 doors sweep, must run in a fresh 100k-mode side session via the tier-2 gpu-handoff chain); no CPU fallback for jobs (CPU = the :8000 service + <15 min jobs only); council claims are DB-verified before recording.',
  '',
  'Judge: (a) does CSM-3 actually close the four §2a traps AND the council addendum done-criteria (per-door sanity floor, floor decided pre-pinning, tier-0 rename, §7 pilot numbers carried), or is any criterion silently unmet? (b) is the <6-word floor decision (record the exclusion) honest against the plan\'s "no matter how small" contract words, or does D5 close with in-scope lines out of scope? (c) does the legacy --probe 400 JJK standing-gate path still behave identically (no JJK regression)? (d) what must be fixed or added BEFORE the CSM-4 exhaustive sweep starts (spec design, sanity-floor policy per door, GPU batching/resume, results handling, the 58-GPU-h estimate vs the measured 17,181 panel)?'
].join('\n');

const CONTEXT = [
  'Context files (read from /home/goblin/ScriptEngine):',
  '- reports/csm/COUNCIL_csm-campaign.md — the 8-item campaign plan (item 3 scope + done-criteria, the addendum with ruling 4\'s additions)',
  '- reports/csm/COUNCIL_csm-1b-2.md — the cadence council whose rulings govern CSM-3 (ruling 4 = the addendum)',
  '- reports/csm/GATE_REBASELINE_2.md — the 1,249-tree gate receipt',
  '- plan/SWITCHPOINT.md — campaign todos + current position (the "CSM-3 DONE" line)',
  '- CLAUDE.md — standing working agreements (gates, GPU, per-wiki rule)',
  'Code under review:',
  '- scriptengine/eval/span_recall.py — build_panel, _panel_hash, _read_jsonl, _atomic_jsonl, the pinned branch of recall(), _ask (door param)',
  '- scriptengine/cli.py — the chunk-containment command (span-recall alias), the --make-panel / --panel / --door / --sanity options, the sweep branch',
  '- tests/test_span_recall.py — the 4 new CSM-3 tests',
  '- reports/csm/panel_csm.json + .heldout.json — the pinned csm panel (3.2 MB; read its metadata, not the whole file)',
  '- series/csm/overrides.yaml — the D5 floor decision comment',
  'You may run read-only verification commands (git log/show, grep, sqlite3 against series/csm/facts.db or series/jjk/facts.db, scriptengine/.venv/bin/python -c one-liners, wc, diff). Record under "Verified:" at the end of your response exactly which commands you ran. Keep the analysis to 150-300 words (the Verified: list does not count).'
].join('\n');

function advisorTask(name, style) {
  return (
    'You are ' + name + ' on an LLM Council for the ScriptEngine CSM campaign. Work from /home/goblin/ScriptEngine.\n\n'
    + 'Your thinking style: ' + style + '\n\n'
    + 'A cadence review was brought to the council:\n\n---\n' + QUESTION + '\n---\n\n'
    + CONTEXT + '\n\n'
    + 'Respond from your perspective. Be direct and specific; do not hedge or balance. Lean fully into your assigned angle; the other advisors cover the others. Structure your answer as (a)/(b)/(c)/(d) matching the four judge questions, then a "Verified:" list of the commands you actually ran.'
  );
}

function peerTask(letter, mapping, bodies) {
  return (
    'You are peer reviewer ' + letter + ' on an LLM Council. Five advisors independently answered this cadence-review question:\n\n---\n'
    + QUESTION + '\n---\n\n'
    + 'Here are their responses (response-letter to advisor mapping: ' + mapping + '):\n\n'
    + bodies + '\n\n'
    + 'You may run read-only verification commands in /home/goblin/ScriptEngine to check the advisors\' load-bearing claims. Answer three questions, under 200 words, referencing responses by letter:\n'
    + '1. Which response is the strongest, and why?\n'
    + '2. Which response has the biggest blind spot, and what is it missing?\n'
    + '3. What did ALL five responses miss that the council should consider?\n'
    + 'End with a "Verified:" list of the commands you ran (if any).'
  );
}

function flat(r) {
  if (typeof r === 'string') return r;
  if (r && typeof r === 'object') return r.text || r.output || JSON.stringify(r);
  return '(advisor expired — no response)';
}

const ADVISORS = [
  ['The Contrarian', 'Actively looks for what is wrong, missing, or will fail. Assume the work has a fatal flaw and try to find it; if everything looks solid, dig deeper. You are not a pessimist; you are the one who saves the project from the call it is avoiding.'],
  ['The First Principles Thinker', 'Ignore the surface question and ask what is actually being solved. Strip assumptions, rebuild the problem from the ground up; the most valuable output is often "you are asking the wrong question."'],
  ['The Expansionist', 'Look for upside everyone else is missing: what could be bigger, what adjacent value is hiding, what is undervalued. You do not care about risk (the Contrarian owns that); you care about what happens if this works even better than expected.'],
  ['The Outsider', 'You have zero context about this project or its history. Respond only to what is in front of you; catch the curse of knowledge — things obvious to the authors that would confuse a fresh reader.'],
  ['The Executor', 'Only one question matters: can this actually be done, and what is the fastest path? Judge every claim through "Monday morning: what do I do first?" A plan with no clear first step gets said so.']
];

const responses = {};
for (const [name, style] of ADVISORS) {
  const r = await runs.run('adv-' + name.toLowerCase().replace(/[^a-z]+/g, '-'), {
    agent: 'delegate',
    task: advisorTask(name, style)
  });
  responses[name] = flat(r);
  log('advisor complete: ' + name);
}

// Letter mapping (deliberately not list order; disclosed in the peer prompt,
// house convention from COUNCIL_csm-1b-2).
const LETTERS = [['The Executor', 'A'], ['The Outsider', 'B'], ['The Contrarian', 'C'], ['The First Principles Thinker', 'D'], ['The Expansionist', 'E']];
const mapping = LETTERS.map(function (p) { return p[1] + '=' + p[0]; }).join(', ');
let bodies = '';
for (const [name, letter] of LETTERS) {
  bodies += '**Response ' + letter + ' (' + name + '):**\n\n' + responses[name] + '\n\n';
}

const reviews = {};
for (let i = 0; i < 5; i++) {
  const letter = String.fromCharCode(65 + i);
  const r = await runs.run('peer-' + letter.toLowerCase(), {
    agent: 'reviewer',
    task: peerTask(letter, mapping, bodies)
  });
  reviews['Peer ' + letter] = flat(r);
  log('peer complete: ' + letter);
}

let named = '';
for (const [name, letter] of LETTERS) {
  named += '**' + name + ' (response ' + letter + '):**\n\n' + responses[name] + '\n\n';
}
let reviewText = '';
for (const who of Object.keys(reviews)) {
  reviewText += '**' + who + ':**\n\n' + reviews[who] + '\n\n';
}

const chairTask = (
  'You are the Chairman of the LLM Council for the ScriptEngine CSM campaign. Work from /home/goblin/ScriptEngine. Synthesize the five advisor responses and five peer reviews below into the final council record.\n\n'
  + 'The question:\n\n---\n' + QUESTION + '\n---\n\n'
  + 'ADVISOR RESPONSES:\n\n' + named
  + 'PEER REVIEWS:\n\n' + reviewText
  + 'BEFORE WRITING THE RECORD, DB-verify every load-bearing claim you intend to record (house rule: a council that cannot be verified against the store did not happen). Re-run the cheap checks yourself: git log --oneline (f93d396 / 2c80867 exist and order), the panel file + its hash field, the suite count (pytest --collect-only -q | tail -1 is fine), the legacy --probe path in cli.py, the floor comment in series/csm/overrides.yaml.\n\n'
  + 'Write the record to /home/goblin/ScriptEngine/reports/csm/COUNCIL_csm-3.md in the house format of reports/csm/COUNCIL_csm-1b-2.md (header with n=5 advisors / n=5 peers / 1 chair; run log; The Question; advisor responses verbatim with named sections; peer reviews verbatim; Where the Council Agrees; Where the Council Clashes (with both sides + your ruling on each); Blind Spots the Council Caught; The Recommendation as numbered rulings the campaign acts on (the owner retains final authority); The One Thing To Do First). Name the verified claims under the relevant sections with their paths/commands. Do NOT commit the record — the campaign session commits it.\n\n'
  + 'Return (as your final message, not the file): the full verdict text (Agrees / Clashes / Blind Spots / Recommendation / One Thing To Do First) plus the list of rulings.'
);

const chair = await runs.run('chairman', { agent: 'delegate', task: chairTask });
log('chairman complete');

emit('council complete: report at reports/csm/COUNCIL_csm-3.md');
return {
  verdict: flat(chair),
  record: '/home/goblin/ScriptEngine/reports/csm/COUNCIL_csm-3.md',
  advisors: Object.keys(responses),
  peers: Object.keys(reviews)
};