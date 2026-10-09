# Big-window review: error and confirm patterns

> **OWNERSHIP (owner 2026-10-07): only Claude adds new rules, and only Claude edits this file and
> `tools/train/big_flags.py`.** The canonical make-and-verify method is `plan/WINDOW_METHOD.md`.

Companion to `plan/BIG_REVIEW_HANDOFF.md` (rulings R1-R25). Built from the corrections in
`series/universal/training/big/big_audit.jsonl` (b1-b131, 2026-10-07). `big_flags.py` turns
most of these into automatic FLAG / MISS? / DUP lines. **Flags are prompts, not verdicts: every
window is still read in full.** Measured on b7-b131: the row and window flags covered 113 of the
114 35B rows that had to change. MISS? cues fired in 62 of the 82 windows with a missed event,
and 13 of 98 rows marked OK still needed a change. Skipping full reads would therefore let
roughly one error in five through.

## A. Wrong-answer patterns (35B row -> correct answer)

| # | pattern (how it shows) | correct | rule | freq b7-b131 |
|---|---|---|---|---|
| A1 | missed event in a window that has other rows: rescues, escapes, "left the team", "found X", recruits, betrayal nouns ("Magik's betrayal"), attacks in passing ("having hurt Broo"), power/mind use ("brainwashed", "possessed", "manipulated by") | add the row | step 8.1, R8, R18 | most windows (82/125 needed additions) |
| A2 | group end ("Avengers", "X-Men", "the group") when the window ties named members to the event | one row per tied member, no group row | G.2, R19 | very common |
| A3 | met from joining/allying ("joined the team", "joining X and Y", "teamed up", "allied", "rejoined", "united with the Runaways" b941) | no met; fact: `joined` (or `allied_with`), actual | R4, R12 | common |
| A4 | two names for one person in the window (codename + real name, alias pairs, disguise reveals "revealed to be", "posing as", "was really", "unmasked") | the real / revealed name in every row | step 6, R10 | common |
| A5 | crowd, indefinite or species end ("several Avengers", "former Avengers", "a Kree armada", "the police", "a Space Phantom", "Skrulls", "Inhumans", "Builders") | drop the row (or the named member if one is tied) | step 6, R11 | common |
| A6 | confrontation with no stated attack written as fought ("confronted Whirlwind", "confronted the robot Computo") | met | R2 | occasional |
| A7 | trapped in a dimension / other world written as captured ("imprisoned in Limbo", "ensnared in Mojoverse", "pocket universe", "forced through a portal") | sealed | R3, R13, R20 | occasional |
| A8 | passive with no doer filled from context ("where he was defeated", "were freed", "Moira being rescued", "arrested due to his connection to Orchis") | no row | step 4, R17 | occasional |
| A9 | rank/title or short form as the name ("Captain Stacy", "Dr. Ellis", "Shaw" when "Sebastian Shaw" is in the window, "Gaunt", "Burch", "the Reaper", "The Crippler") | strip rank; fullest form; no article | step 6 | occasional |
| A10 | description used as a place ("Reavers' Australian base", "the mansion" when unnamed) or heading as arrival ("while taking ... back to") | no arrived/departed | table: arrived | occasional |
| A11 | hedged or prevented acts ("seemingly slew" -> defeated, "attack ... was prevented" -> no fought, "nearly kill" -> fought) | per hedge | step 3 | occasional |
| A12 | "helped X when ..." written as saved | no saved; fact: `helped` (or `assisted`), actual | R23 | rare |
| A13 | leaving/disbanding written as betrayed ("abandoned him to die", "the Avengers were disassembled by") | no betrayed (departed if a named place); fact: `left_group` when a named person leaves a named group, else `other_verb` with the passage's verb | R14, R24 | rare |
| A14 | wrong pronoun referent ("he had captured a Space Phantom" = Kang, not Immortus; "before he escaped the police" = Castle) | re-resolve by meaning | step 4 | rare, only reading catches it |
| A15 | broken end string ("X" for Professor X) | the full name | step 6 | rare |
| A16 | "<group> led by X" as doer | X | R21 | rare |
| A17 | self-directed death (suicide) | no row (gate refuses subject==object) | R16 | rare |
| A18 | two characters sharing a name merged ("the Variant" / "Variant Loki" ambushes while the TVA's Loki sits with B-15) | separate ends ("Variant" vs "Loki") | step 6 | rare, reading only |
| A19 | purpose clause as event ("traveled to NYC to meet with X", "planning to fight") | only the part that happened (arrived), no met/fought; the purpose clause is a fact: `planned`/`claimed` with `asserted_by` when both ends are nameable | step 3 | occasional |
| A21 | killing through a possessed body ("used his powers of body possession to cause Dolan to murder Craft") / a victim who "survived his own murder" | possessor fought the host and the victim; no killed when he survived | step 4, 3 | rare |
| A22 | "finishing off X" with no stated death written as killed | defeated | table: defeated | rare |
| A23 | deals and exchanges as events ("agreed to help in exchange for teleporting them all back") | no row for the promised act; the promise itself is a fact: `planned`/`claimed` with `asserted_by` | step 3 | rare |
| A24 | a vehicle as a place ("carried Pixie to the Blackbird") | no arrived/departed | table: arrived NO "the car" | rare |
| A25 | a pantheon or race as an end ("the Kami", "the Olympians", "Sentinels", "Quantumnauts") | no row | step 6 | occasional |
| A26 | a reported confirmation misread for its speaker ("Gao confirmed that she had fought beside him ... before her death and later rebirth": she = Elektra) | re-resolve by meaning | step 4 | rare, reading only |
| A27 | the Watcher "visited"/"went to" a version of someone (What If narration = observing a universe) | no met | table: met NO watching | rare |
| A28 | "X had A and B abduct Z" written only for A and B | X captured Z too (the one who had it done) | table: captured | rare |
| A29 | "sedated him" / "knocked him out" written as fought | defeated | table: defeated | occasional |
| A30 | "terminating X" about a file/record (X alive later in the window) written as killed | no row | step 3 | rare |
| A31 | a self-assigned task as an event ("joined Daredevil's side and worked to stop Fisk") | no row (R4 + purpose); facts: `joined` (actual) plus the task as `planned`/`ordered` with `asserted_by` | step 3 | occasional |
| A32 | an abilities/powers section narrating specific hits ("shake off a punch from Gladiator", "has taken multiple punches from Namor") left empty | fought rows (step 1: one specific occurrence is an event) | step 1 | occasional |
| A33 | "X revived him" written only as awakened | also X saved him (revived someone who would otherwise die) — only when the revival is for his sake (Merlyn); a corpse revived as a tool or a threat (the Mad Thinker's "living weapon", Cable reviving Apocalypse) is no saved | table: saved | occasional |
| A48 | "joined" disambiguation: joining a team/side/cause ("joined the X-Men", "joined Daredevil's side") vs joining specific people where they are ("Sif joined Coulson and May when they traveled", "joined Namor at Utopia", "joined by an arriving Spider-Man") | team/side -> no met (R4); people where they are -> met; team/side -> fact `joined`; people where they are -> `met` event AND `joined` fact | R4, table: met | common |
| A34 | a team member's own team as "met" target after rescuing/arriving ("arrived in time to save Daisy and May") missed | met each person reached + saved | table: met | occasional |
| A35 | a purpose clause that the next clause fulfils ("traveled to Genosha to confront Magneto ... In the resulting battle", "runs to save him ... stopping them both from falling") left out | write it (met/fought, saved): the PURPOSE flag is a prompt, check the following sentence | step 3 | occasional |
| A36 | "defended by X" in words (X told the accuser he was wrong) written as saved | no row; fact: `warned` or `persuaded`, actual | table: saved | rare |
| A37 | escorting a prisoner ("in charge of taking Venom to a helicarrier cell") left out | captured (brought as a prisoner) | table: captured | rare |
| A38 | "disposed of by X" / "dispatched" with no stated death written as killed | defeated | table: defeated | rare |
| A39 | a company or weapon as the killer ("killed by a Stark Industries missile") | no row (an item is never the doer; its user is unnamed) | step 4 | rare |
| A40 | "jumped into action" against X written as met | fought (an attack made) | table: fought | rare |
| A41 | a plural referent resolved to the wrong people ("the two young heroes" = Johnny and Bobby Drake, not Doris who was also on the cruise) | re-resolve by meaning (heroes = the ones with powers) | step 4 | rare, flagged as a prompt |
| A42 | "the ship was attacked by X" written as X fought the people aboard | no fought (an attack on a vehicle/building only) | table: fought NO | rare |
| A43 | a reunion phrased as feeling ("delight at seeing his dearest friends once again") left out | met | table: met | occasional |
| A44 | "X turned on them" (allies of the moment, e.g. after teaming up) left out or only fought | betrayed + fought (table: betrayed YES "turned on") | table: betrayed | rare |
| A45 | arrivals the other side cannot perceive (Reyes invisible to Mackenzie and May) written as met | no met; met only those who see him ("could see him") | table: met | rare |
| A46 | a later "they" that includes someone already out of the scene ("Hammerhead shot him point-blank" then "They were ambushed" written for Slyde) | only those still present | step 4 | rare, reading only |
| A47 | "were tied to a post" / "chained" / "locked" with no captor written for the last attacker | no captured (R17, example 9) | step 4 | occasional |
| A49 | an unnamed attacker/kidnapper ("their mysterious kidnapper") revealed later in the window ("their real aggressor, the Stranger") left without rows | rows with the revealed name (R10) | R10 | rare |
| A50 | escaped with a place object although the window names the captor ("cut herself free" from Dreykov's operation, written as escaped Red Room Academy) | the captor is the object; the place only when no captor is named | table: escaped | occasional |
| A51 | "A, B and C attended a meeting at <named place>" left out | each arrived + met per pair (a meeting held between them) | table: met/arrived | rare |
| A52 | "an assailant", "a lesser demon", "an impostor" as ends | no row (indefinite) | step 6 | occasional |
| A53 | "used his powers to kill it" where "it" is a symbiote/armor/item on a host who appears alive later ("Virus was arrested") written as the host killed; also "Thor destroyed Ultron's first body" while his consciousness escapes (b966) | fought the host; a body destroyed with the character surviving -> defeated | step 4 | rare, reading only |
| A54 | breaking an agreement ("abandoned his covenant with her and Xavier") | betrayed (broke faith) — unlike plain leaving (A13), which is no betrayal | table: betrayed | rare |
| A55 | "the trio stopped Egghead" written as captured | defeated (the fight ended; no capture stated) | table: defeated | occasional |
| A56 | "had thrown Loki and Thor out of the Bifrost" left out | defeated (thrown off ends the fight, as "pushed him off the truck") | table: defeated | rare |
| A57 | descriptive crowd groups ("the squad", "the rest of the Guardians") as ends | the named members the window ties to the act, else no row | step 6, R11 | occasional |
| A58 | "if not for the intervention of X" against a plot (no attack stated) written as fought; "Iron Man stopped Attuma's plot" written as defeated (b978) | met (an encounter that stops him) | table: met "stops X" | rare |
| A59 | composite end strings ("Dark Phoenix / Cyclops (Scott Summers)") | the real name only ("Scott Summers") | step 6 | rare |
| A60 | "X had his men attack the house, and in the following explosion, Y got killed" written as X killed Y | no killed (an ordered killing; the table excludes the order-giver); fact: `ordered` + `asserted_by` (order-giver and intended victim) | table: killed NO | rare |
| A61 | "managed to escape with the help of X" flagged as R23 'helped' | saved stays (helping an escape from captivity is a release, as b21 Carol Danvers); R23 covers only help with non-danger | R23 | occasional |
| A62 | "grabs Pangan for protection" / shielding someone written as fought | saved | table: saved | rare |
| A63 | "Rawlins' soldiers" / "X's men" attacking (possessive group with a named head) left out or as a crowd | X fought the targets (as "Luke Cage's team" -> Luke Cage) | G.2, R21 | occasional |
| A64 | "X sent Y to attack Z" written with the sender as the doer | Y fought Z (the sender only ordered it); fact: the sender `ordered` + `asserted_by` | table: killed NO ordering | occasional |
| A65 | an organisation as a place ("returned to the FBI", "joined S.H.I.E.L.D.") | no arrived (not a proper-named place); fact: `member_of` (or `joined`) when a named person joins it | table: arrived | rare |
| A66 | "became a mole infiltrated in <team>" left out | betrayed the team (a mole breaks faith with the team she is in) | table: betrayed | rare |
| A67 | a remote appearance ("joined the podcast remotely and greeted host X", a call, a hologram) written as met | no met; fact: `contacted` and/or `greeted` | table: met NO phone/video | rare |
| A68 | "The latter two ..." resolved to the wrong pair (Dracula and Miles instead of the last two named, Brielle and Miles) | the last two named | step 4 | rare, reading only |
| A69 | "destroyed Nimrod's bodies ... prevented him from transferring his consciousness" written as defeated | killed (a named robot/AI destroyed) | table: killed | rare |
| A70 | "trapped in an impenetrable energy dome created by X" left out | X sealed the named ones trapped (a barrier); deactivating it = saved | table: sealed | rare |
| A71 | training sparring between allies ("tasked with training Scott Lang ... he punched van Dyne") written as fought | no row (practice, not a conflict); fact: `trained`/`mentored` — a real punch inside the lesson still gets its `fought` event | table: fought NO playful/friendly contact | rare |
| A72 | "turned on both A and B" where B was already his enemy written as betrayed B | betrayed only the ally (A) | table: betrayed | rare |
| A73 | a battle/war/incident name as an arrived place ("joins the Battle of Wakanda, arriving with Groot and Rocket", b850) | no arrived (an event is not a place); arrived only when the named place itself is stated | table: arrived | rare |
| A74 | "forced Mordo to retreat" / "repelled" / "drove X off" / "force Pilgrim to escape the scene" (b1002) left out (b858) | defeated (the fight ended with X beaten, as A55 "stopped"); plus X escaped the one who forced it | table: defeated | occasional |
| A75 | "restrained the demon from attacking her" written only as fought (b869) | fought the attacker AND saved the one protected (an intercepted attack) | table: saved | rare |
| A76 | "firing wildly, Bishop missed Cable, instead managing to hit Professor Xavier" written as fought Xavier (b925) | fought the intended target (an attack made); no row for the ally hit by accident | table: fought NO accidental | rare |
| A77 | a numbered name with its word stripped as a rank ("Agent 33" -> "33", b912) | the whole name ("Agent 33") | step 6 | rare |
| A78 | a time as a place ("Earth-691's 31st Century", b932) | arrived the proper place only ("Earth-691") | table: arrived | rare |
| A79 | "they made it out into the streets of Hala" (escaping within Hala) written as arrived Hala (b955) | no arrived (not a new place reached) | table: arrived | rare |
| A80 | "the Mole Man was restored to human form" / "he got his powers back" (b1021) / "the Techno-Troid hatched" (b1034) written as awakened (b940) | no row (a form he already had) | table: awakened NO | rare |
| A81 | "learning how to psychically defeat Ahab for good" written as defeated (b971) | no row (knowledge of how, not the act) | step 3 | rare |
| A82 | "Faustus grabbed Peggy, threatening to break her spine if Cap came closer" written only as fought (b1003) | captured too (a hostage taken) | table: captured "hostage" | rare |
| A83 | "manhandled them and knocked them all aside" during an encounter written as defeated (b1029) | fought (+ met for the encounter); defeated only when the fight ends | table: defeated NO | occasional |
| A84 | "defeated all his opponents. The Chameleon ran away" written as defeated the Chameleon (b1021) | the one who ran: escaped, not defeated | table: escaped | rare |
| A85 | "Gideon manipulated her into betraying her friends" written as Gideon betrayed Karma (b1042) | the one manipulated is the betrayer (object = the friends; none if unnamed); the manipulator gets no betrayed | table: betrayed | rare |
| A86 | "scientists ... restore a Sentinel robot" written as the scientists awakened (b1042) | the restored machine is the awakened one; the restorers get no awakened | table: awakened (machine reactivated) | rare |
| A87 | "Stick fought with the Defenders as Elektra easily bested them all" written as Stick fought the Defenders (b1131) | "fought with X" next to a common enemy = alongside X: rows against the enemy, none between allies | table: fought | occasional |
| A20 | an unnamed relative resolved to a named one by outside knowledge ("saved by her father" -> Paxton, who is the stepfather) | the definite description ("Lang's father") | step 4/6 | rare, reading only |

> **FACT-LAYER ROUTES (2026-10-08, owner-authorised council).** When a ruling here says "no row",
> it means no **event** row. The sentence is still covered by v2: a `facts` row when both ends
> are nameable, otherwise a `tags` row from this closed set —
> `no_doer` (A8, A39, A47: passive with no 'by', item as doer, tied with no captor),
> `crowd_end` (A5, A25, A52, A57: crowd/species/indefinite/descriptive-group ends),
> `no_relation` (A17, A27, A30, A42, A45: stated, but no legal event AND no legal fact).
> An event-layer flag never justifies deleting a fact or tag row.

## B. Confirm patterns (35B usually right; one look suffices)

- quote literally states subject-verb-object: "Stark defeated Bullski", "Thanos kidnapped Nebula and Starfox" (OK lines in big_flags)
- "Back to <named place>" / "returned to <named place>" -> arrived
- "found X" / "was greeted by X" / "visited X" / "reunited with X" -> met
- "attacked by X" / "battled X" -> X fought the object
- "X was murdered by Y" / "Y slew X" -> killed
- lists, credits, trivia, dialogue windows -> empty (still skim for one narrated occurrence)
- **The commonest residual error on OK rows is A4 (alias / disguise names) and A2 (group expansion).** Check those two even on OK rows.

## C. Exact duplicates

The same text appears on several sections/pages (b8=b23, b2=b33, b62=b88), or cut at another offset
(b365 = b188's tail). big_flags prints `DUP of bK` (same opening) or `OVERLAP with bK (n/m sentences
shared)` with bK's final rows: reuse them for the shared part and read only the rest.
`tools/train/big_consistency.py` checks every reviewed overlapping pair for diverging rows
(b1-b371: 4 pairs, 0 inconsistent); run it before composing the training set.

## D. Gate quirks

- symmetric met/fought pairs are deduped by the gate; a correction with both "A met B" and
  "B met A" is refused with `dropped []` and `kept n-1/n`.
- "Rachel" and "Jude" are classed as places: refused as objects (R22).
- "Zemo" is classed as an episode page: every Zemo row is refused (both ends).
- "Donovan" is classed as a music page: refused as an end (b880).
- a place name containing "and" ("El Monte Junk and Salvage") is split by the gate like a comma place (refused as `kept n+1/n`); keep the first named part and drop the fragment (b1080).
- "the Other" (Chthon's demon) is refused as a class word ("Other"); no legal row (b1133).
- item pages are refused as ends even when they act like characters: "the Destroyer" (armor), Cerebro (AI).
- subject == object is refused (R16).
- a place with a comma ("Washington, D.C.") is split by the gate into two rows (refused as `kept n+1/n`);
  write the most specific part ("Washington", R1).

## E. Resume notes (2026-10-07 01:59)

- Cursor: see series/universal/training/big/review_cursor.txt (the live value; b7-b431+ reviewed 2026-10-07).
- Rulings R24/R25 (not yet in the handoff): "abandoned him to die" -> no betrayed; "<person> posing as <hero>"
  -> the impostor's name; "found themselves transported to <place> by X" -> X captured them + they arrived.
- Loop: `SCRIPTENGINE_ROOT=/home/goblin/ScriptEngine python tools/train/big_flags.py 15` (from this worktree),
  write compact edits, `python tools/train/big_mkfix.py edits.txt bfix.json`, then
  `/home/goblin/ScriptEngine/tools/train/big_review.py --fix bfix.json` and `--mark N`.

## F. Labeler recipe change (2026-10-07 ~04:50) — the 35B now gets these patterns

The owner asked to give the 35B the flagger and this catalog, not as a prompt dump. Done as:
- `--hints` (tools/train/label_hints.py): at most 5 one-line reminders whose trigger words occur in the
  window (mean 2.6; none on 13%), appended to the user turn; the procedure doc stays the cached prefix.
- `--repair`: big_flags.check() runs on the gated rows; only when flags fire, ONE follow-up turn lists
  them (max 8) and asks for the complete corrected JSON (fires on ~36% of windows).
- Measured on 96 hand-reviewed windows (eval_hints.py; gold = final reviewed rows), same server:
  base P .694 R .436 F1 .535 exact 38 | hints .707/.503/.588 37 | hints+repair .769/.532/.629 44.
  hints+repair vs base: +.093 F1, paired bootstrap 95% [-.008, +.196].
- The runner was paused (owner-approved, PID 471097 stopped at 5,206 labeled) and restarted with
  `--hints --repair` at ~04:48: PID 512679, launched from this worktree with
  SCRIPTENGINE_ROOT=/home/goblin/ScriptEngine (gate modules + data from the main checkout, so the
  gate is unchanged). Rows written from then on carry `"hinted": true`, `repair_note`, `first_rows`;
  the first 5,206 rows are the plain recipe (mixed provenance; every window is still reviewed).
- If the runner dies, resume with the same flags from this branch (label_single.py here has
  --hints/--repair; the main checkout's copy does not):
    cd .claude/worktrees/big-review-flags && SCRIPTENGINE_ROOT=/home/goblin/ScriptEngine \
    setsid nohup /home/goblin/ScriptEngine/scriptengine/.venv/bin/python tools/train/label_single.py \
      --in $R/series/marvel/training/labels/big_in.jsonl --in $R/series/mcu/training/labels/big_in.jsonl \
      --out $R/series/universal/training/big/labels.jsonl --workers 8 --shuffle --hints --repair \
      >> $R/series/universal/training/big/label_run.log 2>&1 < /dev/null &      (R=/home/goblin/ScriptEngine)

## G. Fact-layer gate quirks (big_review_v2, 2026-10-10) — fact_gate._end_ok bugs to fix in one tested change
- "President of the United States" is stripped as a rank prefix and refused (b4).
- "Guardians of the Galaxy" is refused as a crowd end (the crowd regex matches inside the name; b16).
- "Beast" is refused as a species/race end (b17).
Until fixed: drop the row and tag the sentence `no_relation` (a gate limit, not a ruling).
