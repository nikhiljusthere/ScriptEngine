# LLM Council — correct-and-verify loop + Granite student training (2026-09-29)

Sequential council (5 advisors, 5 anonymized peer reviews, chairman), owner-requested.

## Framed question
DECISION: Design (1) the most efficient and robust correct-and-verify loop to make ~3,000 training windows as close to 100% correct as possible, (2) the best way to train a small student model on them, (3) how long to train, and (4) how to push the student's extraction toward ~100% precision and accuracy — because the student will then run unsupervised over 300,000+ Marvel/MCU wiki pages.

TASK: Event extraction from Fandom wiki passages (Jujutsu Kaisen now, Marvel next). Input = one passage window (a wiki section chunk, up to ~4k chars). Output = JSON list of events {quote (verbatim clause from the passage), subject, verb, object}. 12 verbs only: fought, defeated, killed, captured, escaped, saved, betrayed, sealed, awakened, met, arrived, departed. A written annotation guideline (~180 lines) defines each verb with explicit yes/no columns and precedent rulings (e.g. "met" only when two come together, not people already talking; "killed" needs a stated death; generic classes/techniques/items are never ends; fought/met symmetric = one row per pair; attempts/plans are not events; precision first — ambiguous rows are left out). ~43% of windows correctly contain no events. Rare verbs (betrayed, departed, captured) appear a handful of times per 400 windows.

HARDWARE / MODELS: one RTX 5090 (32 GB). Student = IBM Granite-4.2-3B, LoRA r=64 all-linear, prompt/completion SFT (loss on completion only), thinking off, bf16; ~150 optimizer steps (400 windows × 3 epochs, batch 8) takes ~10 minutes. Labeller = Qwen3.8-27B Q6 GGUF on llama.cpp with MTP speculative decoding, thinking on: ~53 tok/s per request, ~350–400 tok/s aggregate with 6 slots, ~2,200 generated tokens per window (mostly thinking), ~4–7 windows/min. Only one of {Q6 server, Granite training, Open-Jev-9B} fits on the GPU at a time. The production "teacher" (Qwen3.8-27B uncensored NVFP4, thinking off, short prompt) produced the 8,491 rows already stored for JJK. Claude (the orchestrating agent) adjudicates by reading passages; it did 400 windows at roughly 150 windows per 10 minutes of its time. Free cloud models (Space Bunny, MiMo-V2.6-Flash, Nemotron 3 Ultra via opencode) are drafting 500 windows each with an extract + wiki-check + self-verify prompt.

MEASURED SO FAR (blind 100-window test gold, 180 core events, annotated from the passage only):
- Q6 extractor (thinking): recall 77.2%, precision 77.1%.
- Production teacher target: 62.8% / 73.0%.
- Granite zero-shot: 8.4% / 37.0%.
- Granite trained on 205 verified windows: 46.1% / 53.9%. On 400 verified windows: 53.9% / 56.7% (learning curve still steep: +7.8 recall per doubling).
- Granite-400 errors: killed 1 hit / 16 missed / 9 false; saved 5 / 15 missed; fought 43 false positives; met 33 false positives; 22 false positives in windows with no events; 22 duplicate rows; once invented a verb ("released").
- Space Bunny (cloud) on its first 10 hidden verified windows: 55.6% / 62.5%.
- Open-Jev-9B (a one-step yes/no decision model) as a row verifier: AUC 0.47 plain, 0.671 with rules in the question — passes 67% of wrong rows. Rejected.
- Q6 row-by-row verifier with a "wiki evidence card" (each name resolved to its wiki page, page type, alive/deceased status, battle pages with outcomes): on 163 already-verified windows it disagreed with Claude's labels on 25 windows; on re-reading, Q6 was right on 12 (Claude had missed a copy-not-the-person case, "fatally wounded" counted as a kill, a purpose clause counted as a kill, subject/object direction) and Claude right on 10 (including Q6 accepting "Gojo killed Jogo" because the wiki says Jogo is dead — but Sukuna killed him). Two design bugs found and fixed: both twins of a symmetric pair rejected themselves as duplicates; partial names resolved to battle pages.

CURRENT PIPELINE (running overnight): 1,000 windows (400 verified pilot + 600 selected for rare verbs / event-rich pages / no-event windows): Q6 extracts → Q6 row-by-row wiki check → Claude reviews every window. Then 1,500 opencode windows + 500 windows with teacher drafts: Q6 per-window corrector (judges each draft row, adds missed events) → Q6 row-by-row wiki check → Claude reviews every window. Target ~3,000 windows, ETA tomorrow afternoon. Test split is by page; the 100-window blind test gold is never trained on.

OWNER CONSTRAINTS: every training entry should be ~100% correct; no quality degradation from shortcuts; the student must extract "perfectly" because it runs unsupervised at 300k-page scale; time matters (the owner wanted to avoid 24h of prep); GPU-only for model work; the owner is not an ML expert and wants a clear decision.

QUESTION FOR THE COUNCIL: What is the best loop (who drafts, who checks, in what order, where Claude's review goes, how disagreements are settled, how residual error is measured), what is the best training recipe for the 3B student (data mix, epochs/steps, LoRA vs full, hyperparameters, curriculum, negatives, constrained decoding, self-consistency or post-filters), how long should it train, and what realistically gets the student to ~100% extraction accuracy — or what is the honest ceiling and how to design around it?

## Advisor: Contrarian
The fatal flaw is that you are chasing "~100%" with a measuring stick that is itself only about 90% accurate. Look at your own numbers. On 163 windows Claude had already verified, the Q6 checker's disagreements showed Claude wrong on 12 and Q6 wrong on 10. That puts Claude's window-level error somewhere around 7%, and Claude alone wrote the 100-window blind gold, so the gold carries that noise too. Until the test gold is double-annotated and every disagreement is settled, every student number you report is limited by that noise. You cannot prove 95% with a ruler good to 93%.

Second, the loop only catches wrong rows, not missing ones. The row-by-row check judges rows that exist. When a draft misses an event, nothing downstream shows it to anyone. Claude reviewing a draft is anchored to it, and at about 4 seconds a window (150 per 10 minutes) Claude is skimming. The student inherits every miss as a "correct" negative, and with 43% empty windows it learns to stay quiet. Your worst verbs, killed (1 of 17 found) and saved (5 of 20), are exactly the kind that get missed quietly.

Third, the wiki evidence card leaks outside knowledge. "Gojo killed Jogo" slipped through because the card said Jogo was dead. On Marvel, with its alternate Earths, variants and retcons, that card gets far noisier, not cleaner.

Fourth, a JJK blind test says nothing about Marvel. Wiki prose that summarizes comic issues differs from JJK's episode prose. With no Marvel gold, the 300k-page run is unmeasured.

Fifth, the realistic ceiling. At +7.8 recall points per doubling, 400 to 3,200 windows is three doublings, which lands the student near 77%, about the level of its Q6 labeller. A distilled 3B model rarely beats the data it learned from.

What to do instead:
- Accept that recall will stay far from 100% and make precision the target.
- Add deterministic filters: constrained decoding to the 12 verbs, an exact-substring check on every quote, dedup of symmetric pairs, and a precision-tuned rejection threshold.
- Build a small, double-annotated Marvel gold set now.
- Once the full run starts, sample-audit about 1% of its output every week.

## Advisor: First-Principles
You're asking how to make a 3B student extract "perfectly". The real question is whether anything can extract perfectly with no supervision. The numbers say no. Your best labeller, Q6 with thinking, reaches 77/77 on blind gold. Claude, adjudicating by hand, was wrong on about 12 of 25 disputed windows against a verifier with wiki evidence. So even your "100% correct" gold is not 100%. A student trained on 3,000 windows will land below its teachers, realistically 70–80%. Doubling the data from here gives diminishing returns, not a jump to 100.

So stop treating precision as a property of the student. Make it a property of the system. The student is a candidate generator. The guarantees come from checks it cannot talk its way past:

1. Mechanical post-filters, not learned ones. The quote must be a verbatim substring. The verb must be one of the 12 (use constrained decoding). Subject and object must resolve to wiki pages of the right type. Symmetric pairs get deduplicated. That removes the invented verbs, the duplicates and the generic ends for free.
2. Structural checks where the wiki already knows the answer. A "killed" row needs a deceased status on the object, and the killer must match the battle page or death section. This is the project's own founding idea: the wiki publishes its structure, so use it as the verifier. Your Gojo/Jogo case is exactly this check, done right.
3. Abstain by design. Ship only rows that pass every gate. Flag the rest as unverified instead of storing them as fact. At 300k pages, a missed event costs little. A false "killed" in a script is the failure that matters.
4. Measure residual error on Marvel, not JJK. Your blind gold is all JJK. Marvel's prose, aliases (Earth-616 variants) and verb distribution differ. Before you trust any number at scale, build 100–200 gold Marvel windows.

On training: ~3 epochs on the 3,000, with no-event windows kept at their natural 43% and rare verbs upsampled. Past that, stop tuning. The honest ceiling for the student is about 80%. Getting close to 100% precision comes from the gates and from abstaining, not from the model.

## Advisor: Expansionist
The council is aiming too low. The real asset here is not the 3B student. It is the verification machinery you have already built. The Q6 wiki-evidence-card verifier beat Claude on 12 of 25 disagreements. That means the wiki's own structure (death status, battle outcomes, page types) can act as a free, scalable oracle. Put it at the centre of the design, not the edges.

Where the upside is:

1. Make the student a drafter, not the final answer. Don't chase 100% from a 3B model; the ceiling tops out well short of that. Run Granite for recall-heavy drafting over 300k pages, then run a cheap structural post-filter built from the evidence card. It checks that verbs are closed-set, the quote is verbatim, the symmetric pair is deduped, "killed" only fires on a stated death, and that both ends resolve to character pages rather than technique pages. Most of Granite-400's errors are mechanical: 22 duplicates, an invented verb, generic ends. Deterministic code removes them at zero GPU cost. Precision comes from that architecture, not from training time.

2. Marvel feeds itself. Every Marvel page Granite processes and the filter accepts, plus a small sample confirmed by Q6 agreement, becomes new training data. Self-training rounds of 3k -> 10k -> 30k windows keep the steep curve going (+7.8 recall per doubling). Four more doublings is where the gain is, not more epochs.

3. Disagreement is a free labelling signal. When Granite, Q6 and a cloud model all agree, auto-accept. Send only the three-way splits to Claude. That cuts Claude's review load by about 60% and focuses it on the rare verbs (betrayed, captured, departed), where the gold is thinnest.

4. The bigger prize. Verified events plus wiki battle outcomes give you a contradiction detector: an event claims X, the infobox says Y. That feeds straight into the franchise brain's "grounded reasoning" goal, because match-ups and trajectories are built from exactly these rows. Treat the extraction corpus as the reasoning layer's substrate, not a side product.

Recipe: LoRA r=64 is fine. Train 3–4 epochs on 3k, oversample rare verbs 3–5x, and keep the 43% negatives. Constrain decoding with a JSON grammar that allows only the 12-verb enum. That kills invented verbs outright.

## Advisor: Outsider
Reading this cold, the thing that jumps out is that "~100% correct" has no ruler. Your gold standard is Claude reading passages. Yet in your own check, Q6 caught Claude wrong on 12 of 163 windows, about 7% window-level error in data you already called "verified." And the 100-window blind test was presumably annotated the same way. So every number here (77%, 54%) is measured against a reference that is itself wrong a noticeable fraction of the time. Before anyone promises 100%, get two independent annotations on those 100 test windows and measure how often they agree. That agreement rate is your real ceiling. No student can beat the people or models grading it.

Second, run the arithmetic you already have. You gain about +7.8 recall per doubling. From 400 to 3,000 windows is roughly 2.9 doublings, which lands the student around 75–80%. That is about where your best labeller (Q6, 77%) sits, and a student rarely beats its teacher. So "near 100% unsupervised" isn't a training-recipe problem. It isn't on the table at all.

Third, "precision and accuracy" are two different targets, and you have to pick one. Your own rules say precision first. Precision near 100% is reachable if you let the student stay silent. Hard filters help there: the quote must appear verbatim in the passage, only the 12 allowed verbs get through, and names must resolve to wiki pages. You can also keep only rows that several sampled runs agree on. Recall near 100% is not reachable. Tell the owner plainly that the system will miss events, and that this is the price of not inventing them.

Fourth, and the one that worries me most: every measurement is on JJK, but the unsupervised run is on Marvel. Different wiki, different writing, far more characters. Nothing here measures transfer. Before the 300k run, build a small blind Marvel test set (100 windows is enough) and require the student to pass it. Otherwise the 300k-page run is an unmeasured bet.

## Advisor: Executor
The student will not reach 100% by training longer. It is being distilled from a Q6 labeller that scores 77/77, so it will level off below that. What's left in the plan, and what can actually ship, is precision you enforce outside the model. Here is what I'd do Monday morning.

1. Write the post-filter today (about 2 hours of code, no GPU). These are deterministic rejects, applied in this order:
- verb must be in the 12-verb enum;
- quote must be a verbatim substring of the window;
- subject and object must resolve to a wiki page of a character or group type (this kills generic classes, techniques and items);
- "killed" requires a death word inside the quote;
- symmetric pairs are canonicalized, then duplicates are removed.
That fixes the invented verb and the 22 duplicates outright, and a large share of the fought/met false positives. Add a verb-enum JSON grammar (GBNF in llama.cpp) at decode time.

2. Use self-consistency as the precision knob. Decode 3 times at temperature 0.7 and keep a row only if at least 2 of the 3 decodes produce it. That costs 3x inference on a 3B model, which is affordable even at 300k pages. Measure it on the blind 100 tonight.

3. Don't wait for 3,000 windows. Train at 1,000 (about 25 minutes) as soon as the overnight batch lands, then again at 2,000 and 3,000. That gives three points on the learning curve for about 2.5 GPU-hours in total. If going from 2,000 to 3,000 adds less than 3 points, stop labelling.

Recipe:
- LoRA r=64 as it is now; full fine-tuning of a 3B model won't fit beside AdamW on 32 GB without tricks, so it isn't worth it.
- 3 epochs, lr 1e-4, cosine schedule.
- Oversample rare-verb windows 3–4x.
- Keep the no-event windows at their natural 43%.

4. Fix the measurement before trusting any number. 180 events in 100 windows means "killed" is judged on 17 examples, which is noise. Grow the blind gold to 300 windows, stratified by verb. Also hand-check 100 Marvel windows before the 300k launch, because JJK precision is not Marvel precision.

5. The ship rule. Launch unsupervised at 300k only when the filtered student reaches at least 90% precision on the Marvel sample. Recall is whatever it turns out to be. Missed events are recoverable later; wrong rows spread across 300k pages are not.

Time check: 3,000 windows at 4–7 per minute is 7–12 hours of Q6, and Claude's review is about 3.5 hours. Tomorrow afternoon is realistic.

Anonymization for reviews: A=Executor, B=Contrarian, C=Outsider, D=Expansionist, E=First Principles.

## Peer review 1
1. Strongest: E. It treats precision as a property of the whole system, not of the model. The student only proposes rows. Checks it cannot talk past decide what ships: mechanical filters, then structural checks against the wiki, then abstaining when unsure. Its "killed" check (the object must be dead and the killer must match the battle page) is the right fix for the Gojo/Jogo leak. That check is the project's founding idea used as the verifier. One flaw: E says Claude was wrong on "12 of 25" windows. The real figure is 12 disagreements out of 163 windows. A is the most actionable, with learning-curve checkpoints at 1k/2k/3k and an explicit ship rule.
2. Biggest blind spot: D. It proposes self-training on Marvel output that passed its filter. That feeds the student's own errors back as labels and adds confirmation bias. It also leans on the evidence card as an "oracle" even though the Gojo/Jogo case shows the card leaks. And auto-accepting three-way agreement conflicts with the owner's "~100% correct entries" rule, because correlated models agree on the same mistakes.
3. What all five missed: Is the 3B student worth it at all? Nobody costed running Q6 plus filters directly on 300k pages against the student's quality gap. No one said how to measure how often the filters wrongly reject correct rows. Events that span two windows, and pronoun subjects, can only be resolved with context outside the window. The 8,491 stored teacher rows, at 73% precision, must stay out of the training mix.

## Peer review 2
1. Strongest: A. It is the only response that turns the analysis into a schedule you can check. It puts the filters in a fixed order. It trains at 1k, 2k and 3k windows with a stop rule of less than 3 points gained. It uses 2-of-3 self-consistency as a precision dial. It points out that "killed" rests on only 17 gold examples. And it sets a hard ship gate: at least 90% precision on a Marvel sample. E is close behind, and its "the wiki is the verifier" framing is the best conceptual point.
2. Biggest blind spot: D. Self-training on Marvel output the filter accepted feeds the student's own misses and systematic errors back in as truth. That is confirmation bias at 300k scale. D also treats the wiki evidence card as an oracle, though the Gojo/Jogo case already shows it leaking. It says nothing about noise in the gold labels or about measuring on Marvel.
3. What all five missed: The student is not distilled from raw Q6. Its labels are Q6 output corrected by Claude and wiki-checked, so "it can't beat its 77% teacher" (A, C, E) is the wrong ceiling. The real ceilings are how often gold annotators agree and what a 3B model can hold. The post-filters were never measured for the recall they destroy on gold. "Killed needs a death word" could remove true kills. Nobody did the rare-verb arithmetic. About 3,000 windows gives roughly 20 "betrayed" examples, too few whatever the oversampling. Nobody costed a 7–9B student against the 300k-page time budget.

## Peer review 3
1. Strongest: A. It is the only response that turns the shared insight (precision comes from gates outside the model, not from training) into things you can do and check: an ordered filter list, 2-of-3 self-consistency tested on the blind gold, learning-curve checkpoints at 1k/2k/3k with a stop rule, a verb-stratified gold of 300 windows, and a numeric ship rule (>=90% filtered precision on Marvel). E comes close but gives no stop rule.
2. Biggest blind spot: D. Self-training on Marvel output the student's own filter accepted is circular. It strengthens exactly the misses B points out, and it uses the wiki evidence card as an oracle even though the Gojo/Jogo case shows the card leaks outside knowledge. D also never measures Marvel before scaling.
3. What all five missed: Nobody asked for a per-verb ship decision. killed (1/17) and saved (5/20) could be dropped or routed to Q6 at scale, while fought and met ship from the student. Nobody considered running Q6 itself on the 300k pages. At ~5 windows/min it is slow, but it is a real baseline to cost against the student. Nobody checked that the post-filter doesn't strip true rows. Its rejection rate needs measuring on gold, not just its precision. Wiki-structure gates like "killed needs deceased status" can't be carried over to Marvel as-is, because characters there come back to life and exist in variants.

## Peer review 4
1. Strongest: A. It is the only response that turns the analysis into a schedule you can check. It trains at 1k, 2k and 3k windows so the learning curve decides when to stop labelling, and it names a rule for when to stop. It grows the blind gold to 300 windows stratified by verb, since "killed" judged on 17 examples is noise. Its ship rule is at least 90% filtered precision on a hand-checked Marvel sample. B, C and E are right about the ruler-noise problem, but they stop at diagnosis.
2. Biggest blind spot: D. Self-training on the filter's own accepted Marvel output reinforces the student's errors, because the filters only catch mechanical faults. Auto-accepting three-way agreement assumes the errors are independent, but all three models share prompts and wiki cards. D also treats the evidence card as an oracle, when that card is what produced the Gojo/Jogo error.
3. What all five missed: The worst errors are about meaning, not format. Missed "killed" (16 of 17) and missed "saved" (15 of 20), plus 43 wrong "fought" rows and 33 wrong "met" rows, are judgement errors. Filters and grammars cannot recover missed rows or fix those. The student is trained on answers alone. Q6 wins with about 2,000 tokens of thinking per window, but the student learns only its final answer with thinking off. Distilling brief reasoning, or a two-stage detect-then-classify design, might close the gap. Nobody ran the throughput numbers. No one estimated how many windows 300k pages make, or compared the student's speed against Q6 plus filters running the job directly.

## Peer review 5
1. Strongest: A. It is the only response that turns the consensus into a schedule someone can follow. It puts deterministic rejects in order, uses 2-of-3 self-consistency as a precision knob it can measure, trains at 1k/2k/3k with an explicit stop rule (under 3 points gained, stop labelling), grows the gold to 300 windows stratified by verb, and ships only on filtered precision of at least 90% on Marvel. E has the clearest framing (precision belongs to the system, not the model) but is less operational.
2. Biggest blind spot: D. Self-training on Marvel rows that its own filter accepted, plus auto-accepting three-way agreement, amplifies correlated errors. Models that share a bias agree confidently. D also puts the wiki evidence card at the centre, even though that card produced the Gojo/Jogo leak (B flagged this). E's "deceased status" check carries the same risk. A dead object does not identify the killer.
3. What all five missed: The labels don't match the test. Training rows are adjudicated with wiki-evidence knowledge, but the blind gold is annotated from the passage alone. The student learns a different target than the one it is scored on. Throughput is never checked. Nobody computed the windows per page on Marvel or the student's decode rate, including 3x self-consistency, against 300k pages. The guideline doesn't cover Marvel. Publication-history sections, alternate realities, what-ifs and retcons are not addressed. These are guideline gaps, not model gaps. Events split across windows. Pronouns and events that cross chunk boundaries go uncounted in both recall and precision.

## Chairman verdict
**Agrees:** training alone will not reach 100% (~+7.8 recall per doubling → high 70s–low 80s at 3k); precision must come from the system (decode grammar for the 12 verbs, verbatim-quote check, ends resolve to right page type, symmetric dedup); choose precision over recall and say so; the ruler (single-annotator blind gold, 17 "killed" examples) is too noisy to tell 90% from 95%; a Marvel test set (100–200 windows) is required before the 300k run; recipe LoRA r=64, ~3 epochs, natural ~43% no-event windows, rare verbs upsampled 3–5x.

**Clashes → rulings:** ceiling ≈80% recall (corrected labels lift it above raw Q6's 77%, arithmetic still caps it); the wiki card may FLAG a row, never add or confirm one the passage does not state; no self-training on filter-approved Marvel output and no auto-accept on model agreement (correlated errors); death-status/death-word rules for "killed" only after measuring how many true kills they remove.

**Blind spots:** score every filter for the correct rows it rejects; training disputes settled passage-only (to match the passage-only test gold); the worst errors are meaning errors (missed killed 16/17, saved 15/20, fought/met false positives) — next lever if it plateaus is distilled short reasoning or detect-then-classify; per-verb ship decisions; rare verbs need targeted mining, not just upsampling; 300k pages ≈ ~1M windows → Q6 alone takes months, so the student is necessary; keep the 8,491 teacher rows out of training; Marvel guideline additions (publication history, alternate realities, what-ifs, retcons, resurrection, variants) before Marvel gold; cross-window events and pronouns are uncounted.

**Recommendation:** loop = two independent drafts per window (only way to catch missed rows) → Q6 row+wiki check as a FLAGGER → Claude reviews every window reading the passage first, with a deliberate "what did both drafts miss" pass on disagreements and empty windows → disputes settled by the guideline from the passage alone → a blind re-annotation of a random 5% of training windows measures the training set's own error. Training = Granite-4.2-3B, LoRA r=64 all-linear, lr 1e-4 cosine, batch 8, bf16, completion-only loss, verified windows only, 12-verb decode grammar, checkpoints at 1k/2k/3k with stop rule (<3 recall points 2k→3k → switch to targeted rare-verb mining), 3 epochs (~1,100 steps, ~75 min at 3k). Path to ~100%: recall ~80% (say so); near-100% precision on shipped rows via scored filters + 2-of-3 self-consistency (if timing allows) + per-verb ship gate on a Marvel test set (≥95% for killed/betrayed/captured, ≥90% for others; failing verbs held back or routed to Q6); ~1% weekly audit after launch.

**First thing:** second independent annotation of the 100-window blind test gold, disagreements settled by the guideline, grown toward 300 windows stratified by verb.
