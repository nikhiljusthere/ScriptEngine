import json
D="/home/goblin/ScriptEngine/.claude/worktrees/9b-model-extraction-analysis-a7e9c9/docs/train_audit_2026-11-14/adj/"
V={
98:("gold_ok","The Band of the Falcon names no member in the window, so the group row stands (step 6 groups); the second reader adds nothing."),
223:("gold_ok","Same killed row as the second reader; names differ only by page title."),
166:("fix","Eriza flees with the heart from Guts, who was following her: escaped table YES 'fled', object = the named pursuer (A50); not recorded by any row."),
82:("gold_ok","No event in the window; facts match."),
185:("unsure","Two open points: 'the Falcon members are surrounded by a mercenary troop led by Adon himself' (met Adon-Guts/Casca or A145/A63?) and 'Casca's platoon ... infiltrated the fortress' (arrived Doldrey via 'the fortress'?). Other second-reader rows are crowd/group rows (A5, A2)."),
30:("gold_ok","Guts|fought|Bazuso is subsumed by defeated (A145); Corkus's attack is a purpose clause and its outcome is already defeated + escaped (A74)."),
92:("gold_ok","Daka are a race/crowd (step 6), so no fought row; the arrival is already recorded."),
245:("gold_ok","A145: the blast that dematerialises the Kundalini is one act, defeated only."),
97:("unsure","'the party is met by the villagers and priest': step 6 allows a definite description of one individual ('the priest') as an end, but the reviewer and A112 treat an unnamed person as no end; owner should rule."),
137:("gold_ok","Same met row as the second reader (Count / The Count is a name-form difference)."),
131:("gold_ok","Second-reader rows are group rows; gold writes the named disciples (A2); restraining in a fight is fought, not captured (table)."),
99:("fix","Zepek's bolt stops Guts' killing attack on Rosine: an intercepted attack is fought AND saved (A75; Addendum 3 'intercepting a killing blow on a named person = saved'); gold has only the fought row."),
248:("fix","Guts arrives in time as the trolls surround the women and covers them while they escape: A34 met + saved; saved table YES 'protected from harm'. The protected facts are the event's twins (section B)."),
105:("fix","Being turned into pseudo-apostles is a first new form: awakened table YES 'gained a new power or form for the FIRST time' (A126), so the transformed_into twins go (section B); the Crow's separately stated attack on Guts is fought beside the defeated (step 5 verb rules, A145)."),
181:("gold_ok","No event in the window."),
169:("fix","Ganishka 'assuming a divine state' is a first new form: awakened (table, A126); the transformed_into twin goes (section B). Killing 'Kushan soldiers' is a crowd (no row)."),
69:("fix","The Count transforms Zondark into a pseudo-apostle, a first new form: Zondark awakened (table, A126); the transformed_into twin goes (section B)."),
83:("fix","'When the group reaches Elfhelm, Schierke's experience with magic helps the party navigate' ties Schierke to the group that reached the named place: Schierke arrived Elfhelm (A57). The friendship with Kukka is no stated meeting."),
66:("unsure","'Griffith stabs the Kushan leader in the eye': step 6 makes a definite description of one individual an end, but the reviewer and A112 leave an unnamed person without a row; owner should rule. Sonia freeing her hands has no captor or named place (A117)."),
183:("gold_ok","Trolls are a species cut down 'in droves' (step 6 crowd/species): no killed row."),
18:("gold_ok","'Tudor is forced to seek peace' has no 'by' doer and the recapture is of a place (A110, A42): no defeated row."),
46:("gold_ok","Gold met row matches; the second reader omitted it."),
452:("gold_ok","A manga/anime comparison in Anime Notes is production (A98)."),
387:("gold_ok","The shot is known only from a question and an affirmation, a report (A113); healing with no stated danger of death is no saved (table)."),
356:("gold_ok","Same fought pair as the second reader; name forms differ only."),
302:("gold_ok","Second reader adds nothing; gold met and fought rows on separate pairs (A145)."),
447:("fix","'As Shinji is wounded by the explosion, Bambietta explains that ... she simply has to explode everything around her' names the owner of the explosion: A120 the owner of the power is the doer, so Bambietta fought Shinji. Komamura awakened is not stated (A126)."),
497:("gold_ok","A145: Ichigo's attack that severs Zabimaru is the one act that ends the fight, defeated only."),
339:("gold_ok","Same killed row as the second reader; name forms differ only."),
274:("gold_ok","Same fought row as the second reader; name forms differ only."),
444:("gold_ok","Same met row as the second reader; name forms differ only."),
}
out=[]
for l in open(D+"A02_adj_input.jsonl"):
    d=json.loads(l)
    v,r=V[d["b"]]
    out.append(json.dumps({"b":d["b"],"id":d["id"],"verdict":v,"reason":r},ensure_ascii=False))
open(D+"A02_verdicts.jsonl","w").write("\n".join(out)+"\n")
from collections import Counter
print(Counter(V[json.loads(l)["b"]][0] for l in open(D+"A02_adj_input.jsonl")), len(out))
