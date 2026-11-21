import json
D='/home/goblin/ScriptEngine/.claude/worktrees/9b-model-extraction-analysis-a7e9c9/docs/train_audit_2026-11-14/adj/'
rows=[json.loads(l) for l in open(D+'A03_adj_input.jsonl')]
V={
264:("gold_ok","SR fought Shunsui-Kusaka is the gold row under the window's names; 'wakes up' is ordinary sleep (A106)."),
320:("gold_ok","SR fought Koga-Ichigo is already a gold row (name form only)."),
396:("gold_ok","No event disagreement; doer-less passive tagged."),
441:("fix","Gerard's attacks that Byakuya repels are a separately stated attack: fought YES 'any attack made, even if blocked'; A145 fought too when stated separately from the defeat."),
348:("gold_ok","fought is one row per pair (step 5); Driscoll fought Sasakibe already present."),
357:("unsure","Gold treats 'the Arrancar' as an unnamed creature; step 6 allows a definite description of one individual ('the monster'), which would give Tōshirō defeated and Shōta/Rangiku killed rows."),
310:("gold_ok","'the Arrancar clone' is one of many clones, indefinite in effect (A52); fought direction is the same pair anyway."),
266:("gold_ok","Being inside the Study Chamber is located_at, not an arrival (A151); met already present."),
281:("unsure","Same open question as b357: 'the Hollow' read as unnamed creature; under step 6 definite description Renji defeated it ('defeating him'). Renji catching Chad is a purpose infinitive, saved not clearly stated."),
313:("gold_ok","The three female Arrancar are unnamed in the window (A8/A130); no doer stated for their fall."),
334:("gold_ok","Yamamoto and Aizen are already in conversation: landing in front of him is no new meeting (met NO 'talking inside a meeting already under way')."),
379:("gold_ok","No second-reader difference beyond name form."),
458:("fix","Algora shielding Nikita from the arrows Ichibe'e sends back is an intercepted attack: saved (table 'protected from harm', A75); the protected fact for Nikita goes (section B, A89). Other SR rows are the same pairs."),
487:("gold_ok","The window does not state a first-time power gain for Ichigo's shroud; awakened needs FIRST time (step 5, A80)."),
298:("gold_ok","No second-reader-only event."),
340:("fix","Ichigo slashing Dordoni away in time from his attack on Nel is an intercepted attack: fought AND saved the one protected (A75)."),
484:("gold_ok","SR met is the gold row under name form."),
308:("gold_ok","No second-reader-only event."),
404:("gold_ok","SR fought is the gold row under name form."),
431:("gold_ok","Anime/manga censorship note is production (A98)."),
378:("gold_ok","'were called to the Sōkyoku Hill' does not state arrival (A109)."),
423:("gold_ok","Komamura is not named in the window (A8, A130)."),
412:("unsure","Two open points: 'fled Soul Society to escape their sentences' may be escaped (table 'fled', A150) instead of departed; 'was able to awaken his powers' may be awakened (first power) though the note rules it out."),
297:("gold_ok","No event disagreement."),
454:("gold_ok","Renji not in window (A8); Cang shattering ice is an attack on an object (A42); Bambietta-Komamura is one pair."),
480:("gold_ok","Casting away his own sword spirit is no betrayal of an ally (A13 plain leaving)."),
305:("gold_ok","SR rows are gold rows under name form."),
353:("gold_ok","fought is one row per pair; reversed SR rows duplicate gold pairs."),
364:("gold_ok","An argument states no coming-together; no met narrated (table met NO)."),
370:("gold_ok","SR saved is the gold row."),
312:("gold_ok","No event disagreement."),
457:("gold_ok","Anime/manga censorship note is production (A98)."),
500:("gold_ok","A friendship that began is not a narrated meeting; companions."),
288:("fix","Lille fires Trompete after telling Nanao and Shunsui to perish: an attack made on Shunsui (fought YES); met stays since they talk first (as gold lint b264)."),
435:("gold_ok","Anime/manga note is production (A98)."),
316:("gold_ok","killed over defeated (A145); waking from sleep is no awakened (A106)."),
508:("gold_ok","Ripping Mimihagi off and absorbing it is no capture; Pernida fought Yoruichi already present."),
}
FIX={
441:"""@441 gold: 2026-11-14 audit, step 5 fought / A145 -- Gerard's attacks repelled by Byakuya are a separately stated attack
keep
+ Gerard Valkyrie|fought|Byakuya|even repel attacks from a titanic Gerard in his very last incarnation""",
458:"""@458 gold: 2026-11-14 audit, A75 / saved table -- Algora shields Nikita from the returned arrows: saved, not a protected fact
keep
+ Algora Lallau|saved|Nikita Deslock|she and the rest of the Schutzstaffel were shielded by Algora Lallau
f- Algora Lallau|protected|Nikita Deslock""",
340:"""@340 gold: 2026-11-14 audit, A75 -- Ichigo slashes Dordoni away from Nel in time: intercepted attack, saved
keep
+ Ichigo|saved|Nel|Ichigo barely manages to slash him away in time""",
288:"""@288 gold: 2026-11-14 audit, step 5 fought -- Lille fires Trompete at Nanao and Shunsui after telling them to perish
keep
+ Lille|fought|Shunsui|as Lille fires Trompete""",
}
assert set(V)=={r['b'] for r in rows}
with open(D+'A03_verdicts.jsonl','w') as f:
    for r in rows:
        v,why=V[r['b']]
        f.write(json.dumps({"b":r['b'],"id":r['id'],"verdict":v,"reason":why},ensure_ascii=False)+"\n")
with open(D+'A03_fix.txt','w') as f:
    f.write("\n\n".join(FIX[r['b']] for r in rows if r['b'] in FIX)+"\n")
from collections import Counter
print(Counter(v for v,_ in V.values()))
