"""Score the character-scoped sheet against the online canon from Sheet 6.

Sheet 6 graded by eye. This asks the same live server and computes the number:
for each question, how many canon items came back (recall) and how many
returned members are canon at all (precision).

A canon item counts as found only when a returned member matches it or one of
its aliases after normalisation -- substring matching is deliberately not used,
because "Super Saiyan" is inside "Super Saiyan 2" and would score a miss as a
hit.
"""

import json
import re
import sys
import time
import unicodedata
import urllib.request

BASE = "http://127.0.0.1:8000"

# (series, question, [(canon item, [aliases])])
GOLD = [
    ("db", "Every form of Goku", [
        ("Base", []),
        ("Great Ape", ["oozaru"]),
        ("Kaio-ken", ["kaioken", "kaio ken"]),
        ("Super Saiyan", ["super saiyan 1", "ssj"]),
        ("Super Saiyan 2", ["super saiyan ii"]),
        ("Super Saiyan 3", ["super saiyan iii"]),
        ("Super Saiyan God", []),
        ("Super Saiyan Blue", ["super saiyan god super saiyan", "ssgss"]),
        ("Super Saiyan Blue Kaio-ken", ["super saiyan blue kaioken"]),
        ("Ultra Instinct -Sign-", ["ultra instinct sign"]),
        ("Mastered Ultra Instinct", ["perfected ultra instinct"]),
        ("True Ultra Instinct", []),
    ]),
    ("db", "Every form of Vegeta", [
        ("Base", []),
        ("Great Ape", ["oozaru"]),
        ("Super Saiyan", ["ssj"]),
        ("Super Saiyan Second Grade", ["super vegeta", "ascended super saiyan"]),
        ("Majin Vegeta", ["majin"]),
        ("Super Saiyan 2", []),
        ("Super Saiyan 3", []),
        ("Super Saiyan 4", []),
        ("Super Saiyan God", []),
        ("Super Saiyan Blue", ["ssgss"]),
        ("Super Saiyan Blue Evolution", ["perfected super saiyan blue", "super saiyan blue evolved"]),
        ("Ultra Ego", []),
    ]),
    ("db", "Every transformation of Frieza", [
        ("First Form", ["first form frieza"]),
        ("Second Form", ["second form frieza"]),
        ("Third Form", ["third form frieza"]),
        ("Final Form", ["true form", "fourth form"]),
        ("100% Full Power", ["full power frieza", "100% frieza", "full power"]),
        ("Mecha Frieza", ["cyborg frieza"]),
        ("Golden Frieza", ["true golden frieza", "fury golden frieza"]),
        ("Black Frieza", []),
    ]),
    ("db", "Every technique Goku uses", [
        ("Kamehameha", []),
        ("Spirit Bomb", ["genki dama", "super spirit bomb"]),
        ("Instant Transmission", ["shunkan ido"]),
        ("Kaio-ken", ["kaioken"]),
        ("Dragon Fist", ["dragon fist explosion"]),
        ("Solar Flare", ["taiyoken"]),
        ("Afterimage Strike", ["afterimage technique"]),
        ("Destructo Disc", []),
    ]),
    ("onepiece", "Every form of Luffy", [
        ("Gear Second", ["gear 2", "gear second"]),
        ("Gear Third", ["gear 3"]),
        ("Gear Fourth: Boundman", ["boundman", "gear 4 boundman"]),
        ("Gear Fourth: Snakeman", ["snakeman"]),
        ("Gear Fourth: Tankman", ["tankman"]),
        ("Gear Fifth", ["gear 5", "nika", "sun god nika"]),
    ]),
    ("onepiece", "Every Gear of Luffy", [
        ("Gear Second", ["gear 2"]),
        ("Gear Third", ["gear 3"]),
        ("Gear Fourth: Boundman", ["boundman", "gear 4"]),
        ("Gear Fourth: Snakeman", ["snakeman"]),
        ("Gear Fourth: Tankman", ["tankman"]),
        ("Gear Fifth", ["gear 5"]),
    ]),
    ("onepiece", "Every technique of Zoro", [
        ("Oni Giri", ["onigiri"]),
        ("Santoryu Ogi: Sanzen Sekai", ["sanzen sekai", "three thousand worlds"]),
        ("Tatsumaki", ["dragon twister"]),
        ("Shishi Sonson", []),
        ("Ashura", ["asura"]),
        ("Yakkodori", []),
        ("Toro Nagashi", []),
        ("King of Hell", ["enma"]),
    ]),
    ("opm", "Every Saitama technique", [
        ("Normal Punch", ["ordinary punch"]),
        ("Consecutive Normal Punches", ["normal punches"]),
        ("Serious Punch", ["serious series serious punch"]),
        ("Serious Sideways Jumps", ["sideways jumps"]),
        ("Serious Table Flip", ["table flip"]),
        ("Omnidirectional Serious Punch", ["omnidirectional punch"]),
        ("Killer Move: Serious Series", ["serious series"]),
    ]),
    # Corrected against the One-Punch Man wiki. `Blazing Charge` and `Arms
    # Gatling` were in this list and are not his — nor anyone's. The engine was
    # being marked down for not returning techniques that do not exist.
    ("opm", "Every technique of Genos", [
        ("Incineration Cannon", ["incinerate"]),
        ("Machinegun Blows", ["machine gun blows", "machine gun punch"]),
        ("Jet Drive Arrow", []),
        ("Rocket Punch", []),
        ("Rocket Stomp", []),
    ]),
    ("jjk", "How many 1v1 battles did Yuji Itadori have with named characters", [
        ("Yuji Itadori vs. Aoi Todo", ["yuji vs todo"]),
        ("Yuji Itadori vs. Junpei Yoshino", ["yuji vs junpei"]),
        ("Yuji Itadori vs. Mahito", ["yuji vs mahito"]),
        ("Yuji Itadori vs. Choso", ["yuji vs choso"]),
        # `Yuji Itadori vs. Sukuna` was here and is not a page on this wiki.
        # What exists is `Yuji, Maki & Hana vs. Sukuna` — three on one — and
        # `Jujutsu Sorcerers vs. Sukuna`, a group raid. Neither is a 1v1, which
        # is what this question asks for, so the item was never answerable.
        ("Yuji Itadori vs. Ko Guy", ["yuji vs ko guy"]),
        ("Yuji Itadori vs. Yuta Okkotsu", ["yuji vs yuta"]),
    ]),
    ("jjk", "Every cursed technique of Sukuna", [
        ("Shrine", ["cursed technique shrine"]),
        ("Dismantle", ["cleave dismantle"]),
        ("Cleave", []),
        ("Furnace", ["fuga"]),
        ("Malevolent Shrine", ["domain expansion malevolent shrine"]),
        ("Hollow Wicker Basket", []),
        ("Reverse Cursed Technique", []),
        ("Ten Shadows Technique", ["ten shadows"]),
    ]),
    ("bleach", "Every form of Ichigo Kurosaki", [
        ("Shikai", ["zangetsu shikai"]),
        ("Bankai", ["tensa zangetsu"]),
        ("Hollow Mask", ["visored", "hollowfication"]),
        ("Full Hollowfication", ["full hollow", "hollow ichigo"]),
        ("Vasto Lorde", []),
        ("Final Getsuga Tensho", ["dangai", "mugetsu"]),
        ("Fullbring", []),
        ("Fullbring Bankai", ["fullbring shikai"]),
        ("True Shikai", []),
        ("True Bankai", []),
        ("Quincy Form", ["blut vene", "quincy powers"]),
    ]),
    ("bleach", "Every technique of Ichigo Kurosaki", [
        ("Getsuga Tensho", ["getsuga tenshou"]),
        ("Bankai", []),
        ("Final Getsuga Tensho", ["mugetsu"]),
        ("Blut Vene", ["blut"]),
        ("Shunpo", ["flash step"]),
        ("Hollow Mask", []),
    ]),
    ("hxh", "Every Nen ability of Killua", [
        ("Lightning Palm", ["narukami"]),
        ("Thunderbolt", ["rhythm echo"]),
        ("Whirlwind", []),
        ("Speed of Lightning", ["kanmuru"]),
        ("Godspeed", ["kamikiri"]),
    ]),
    ("hxh", "Every Nen ability of Kurapika", [
        ("Chain Jail", []),
        ("Dowsing Chain", []),
        ("Holy Chain", []),
        ("Steal Chain", []),
        ("Judgement Chain", ["judgment chain"]),
        ("Emperor Time", []),
    ]),
    ("csm", "Every form of Denji", [
        ("Human", ["base", "denji"]),
        ("Chainsaw Man", ["chainsaw man hybrid", "hybrid form"]),
        ("Chainsaw Devil", ["pochita", "full devil form", "true chainsaw man"]),
    ]),
    # `Black Swordsman Armor` was here and is not a thing. "Black Swordsman" is
    # Guts' epithet, not the name of a suit; the Berserker Armor is the only
    # armour Berserk names. One item, and the engine already returns it.
    ("berserk", "Every armor of Guts", [
        ("Berserker Armor", ["berserk armor"]),
    ]),

    # ── Added 2026-08-04 ────────────────────────────────────────────────────
    # The seventeen questions above cover fourteen characters. Prose extraction
    # reads the top fifty of every series — about 350 characters — so the set
    # measured roughly four per cent of what the pipeline builds, and a number
    # computed over fourteen hand-picked characters is a number about those
    # fourteen. These twenty widen it to every series and to characters the
    # extraction demonstrably reached (each appears in its series' `abilities`
    # table). Canon was searched for this run; the source is named per block.
    #
    # They are expected to score *worse* than the original seventeen, which
    # were the questions the last two passes were tuned against. That is the
    # point of adding them.

    # dragonball.fandom.com/wiki/Beast + gamerant.com/dragon-ball-gohan-
    # transformations-explained
    ("db", "Every form of Gohan", [
        ("Base", []),
        ("Great Ape", ["oozaru"]),
        ("Super Saiyan", ["ssj"]),
        ("Super Saiyan 2", ["super saiyan ii"]),
        ("Ultimate", ["mystic", "potential unleashed", "ultimate gohan"]),
        ("Beast", ["gohan beast"]),
    ]),
    # cbr.com/dbz-cell-strongest-forms
    ("db", "Every form of Cell", [
        ("Imperfect Cell", ["imperfect"]),
        ("Semi-Perfect Cell", ["semi perfect", "semi-perfect"]),
        ("Perfect Cell", ["perfect"]),
        ("Super Perfect Cell", ["super perfect"]),
    ]),
    # cbr.com/dragon-ball-majin-buu-forms + gamerant.com/dragon-ball-all-of-
    # buus-transformations-explained
    ("db", "Every form of Majin Buu", [
        ("Innocent Buu", ["fat buu", "majin buu innocent"]),
        ("Evil Buu", []),
        ("Super Buu", []),
        ("Buutenks", ["super buu gotenks absorbed"]),
        ("Buuhan", ["super buu gohan absorbed"]),
        ("Kid Buu", ["pure buu"]),
        ("Good Buu", ["mr buu", "majin buu good"]),
    ]),
    # cbr.com/dragon-ball-trunks-transformations-ranked +
    # dragonball.fandom.com/wiki/Super_Saiyan_Rage
    ("db", "Every form of Trunks", [
        ("Super Saiyan", ["ssj"]),
        ("Super Saiyan Second Grade", ["ascended super saiyan", "super trunks"]),
        ("Super Saiyan Third Grade", ["ultra super saiyan"]),
        ("Super Saiyan 2", []),
        ("Super Saiyan Rage", []),
    ]),

    # onepiece.fandom.com/wiki/Sanji/Abilities_and_Powers +
    # onepiece.fandom.com/wiki/Black_Leg_Style/Ifrit_Jambe
    ("onepiece", "Every technique of Sanji", [
        ("Black Leg Style", ["black leg"]),
        ("Diable Jambe", []),
        ("Ifrit Jambe", []),
        ("Concasse", ["concasse"]),
        ("Joue Shoot", []),
    ]),
    # onepiece.fandom.com/wiki/Three_Sword_Style. Deliberately separate from
    # "Every technique of Zoro": Sheet 6 found the wiki names his *styles* in
    # the headings and buries the named attacks, so asking for the styles and
    # asking for the attacks should score very differently. If they do, the
    # miss is the corpus's shape and not the retriever's.
    ("onepiece", "Every sword style of Zoro", [
        ("Three Sword Style", ["santoryu", "three swords style"]),
        ("Two Sword Style", ["nitoryu", "two swords style"]),
        ("One Sword Style", ["ittoryu", "one sword style"]),
        ("Nine Sword Style", ["kyutoryu", "asura"]),
        ("King of Hell Three Sword Style", ["king of hell"]),
    ]),

    # cbr.com/jjk-gojo-every-cursed-technique +
    # jujutsu-kaisen.fandom.com/wiki/Limitless
    ("jjk", "Every cursed technique of Satoru Gojo", [
        ("Limitless", []),
        ("Infinity", ["muryokusho"]),
        ("Cursed Technique Lapse: Blue", ["blue", "lapse blue"]),
        ("Cursed Technique Reversal: Red", ["red", "reversal red"]),
        ("Hollow Purple", ["hollow technique purple", "purple"]),
        ("Unlimited Void", ["infinite void", "domain expansion unlimited void"]),
        ("Reverse Cursed Technique", []),
    ]),
    # cbr.com/megumi-jjk-ten-shadows-shikigami-ranked +
    # jujutsu-kaisen.fandom.com/wiki/Shikigami
    ("jjk", "Every shikigami of Megumi Fushiguro", [
        ("Divine Dogs", ["divine dog", "demon dogs", "divine dogs totality"]),
        ("Nue", []),
        ("Toad", ["gama"]),
        ("Great Serpent", ["orochi"]),
        ("Max Elephant", ["elephant"]),
        ("Rabbit Escape", ["rabbit"]),
        ("Round Deer", ["deer"]),
        ("Piercing Ox", ["ox", "bull"]),
        ("Mahoraga", ["eight handled sword divergent sila divine general mahoraga"]),
    ]),
    # cbr.com/yuta-okkotsu-cursed-techniques +
    # jujutsu-kaisen.fandom.com/wiki/Copy
    ("jjk", "Every cursed technique of Yuta Okkotsu", [
        ("Copy", ["copy technique"]),
        ("Rika", ["rika orimoto", "cursed spirit manifestation"]),
        ("Reverse Cursed Technique", []),
        ("Pure Love", ["pure love beam"]),
        ("Authentic Mutual Love", ["true and mutual love", "domain expansion authentic mutual love"]),
    ]),

    # hunterxhunter.fandom.com/wiki/Gon_Freecss +
    # gamerant.com/hunter-x-hunter-gon-jajanken-explained
    ("hxh", "Every Nen ability of Gon", [
        ("Jajanken", ["jan ken", "rock paper scissors"]),
        ("Rock", ["jajanken rock", "guu"]),
        ("Paper", ["jajanken paper", "paa"]),
        ("Scissors", ["jajanken scissors", "chi"]),
    ]),
    # vsbattles/hunterxhunter Meruem entries; abilities absorbed from the
    # Royal Guards after eating Pouf and Youpi.
    ("hxh", "Every Nen ability of Meruem", [
        ("Aura Synthesis", ["metamorphosis", "aura synthesis"]),
        ("Photon", ["spiritual message", "photons"]),
        ("Rage Blast", ["rage"]),
        ("En", []),
    ]),
    # gamerant.com/hunter-x-hunter-hxh-chrollo-skill-hunter +
    # hunterxhunter.fandom.com/wiki/Chrollo_Lucilfer
    ("hxh", "Every Nen ability of Chrollo", [
        ("Skill Hunter", ["bandit's secret", "bandits secret"]),
        ("Bookmark", []),
        ("Borrowed Time", []),
    ]),
    # hunterxhunter.fandom.com/wiki/Hisoka_Morow
    ("hxh", "Every Nen ability of Hisoka", [
        ("Bungee Gum", []),
        ("Texture Surprise", []),
    ]),

    # onepunchman.fandom.com/wiki/Garou +
    # fandomwire.com/one-punch-man-every-garou-ability-ranked
    ("opm", "Every technique of Garou", [
        ("Water Stream Rock Smashing Fist", ["water stream rock smashing"]),
        ("Whirlwind Iron Cutting Fist", ["whirlwind iron cutting"]),
        ("Exploding Heart Release Fist", ["exploding heart release"]),
        ("Roaring Aura Sky Ripping Fist", ["sky ripping fist"]),
        ("Cross Fang Dragon Slayer Fist", ["dragon slayer fist"]),
        ("Tiger Fang True Fist", ["tiger fang"]),
    ]),
    # onepunchman.fandom.com/wiki/Speed-o'-Sound_Sonic
    ("opm", "Every technique of Speed-o'-Sound Sonic", [
        ("Four Shadows Burial", ["four shadows"]),
        ("Ten Shadows Burial", ["ten shadows"]),
        ("Scattered Flash Slash", []),
        ("Wind Blade Kick", ["wind blade"]),
        ("Exploding Shuriken", ["explosive shuriken", "bakuretsu shuriken"]),
    ]),

    # bleach.fandom.com/wiki/Byakuya_Kuchiki + /wiki/Senkei +
    # /wiki/Shūkei:_Hakuteiken
    ("bleach", "Every technique of Byakuya Kuchiki", [
        ("Senbonzakura", []),
        ("Senbonzakura Kageyoshi", ["bankai senbonzakura kageyoshi"]),
        ("Senkei", ["senkei senbonzakura kageyoshi"]),
        ("Shukei: Hakuteiken", ["shukei hakuteiken", "hakuteiken"]),
        ("Gokei", ["gokei senbonzakura kageyoshi"]),
        ("Shunpo", ["flash step"]),
    ]),
    # bleach.fandom.com/wiki/Ulquiorra_Cifer + /wiki/Lanza_del_Relámpago
    ("bleach", "Every form of Ulquiorra Cifer", [
        ("Resurreccion", ["murcielago", "resurreccion murcielago"]),
        ("Resurreccion: Segunda Etapa", ["segunda etapa"]),
    ]),

    # chainsaw-man.fandom.com/wiki/Power + cbr.com/power-chainsaw-man
    ("csm", "Every ability of Power", [
        ("Blood Manipulation", ["blood control"]),
        ("Blood Weaponization", ["blood weapon", "blood weaponisation"]),
        ("Blood Spear", []),
        ("Blood Hammer", []),
        ("Blood Chainsaw", []),
        ("Thousand Tera Blood Rain", ["blood rain"]),
    ]),
    # chainsaw-man.fandom.com/wiki/Aki_Hayakawa + /wiki/Future_Devil
    ("csm", "Every devil contract of Aki Hayakawa", [
        ("Fox Devil", ["kon"]),
        ("Curse Devil", ["curse"]),
        ("Future Devil", ["future"]),
    ]),

    # berserk.fandom.com/wiki/Guts + /wiki/Cannon_Arm + /wiki/Dragon_Slayer.
    # Separate from "Every armor of Guts", which has one member and which the
    # engine already answers -- this asks for the equipment set instead.
    ("berserk", "Every weapon of Guts", [
        ("Dragon Slayer", ["dragonslayer"]),
        ("Cannon Arm", ["arm cannon"]),
        ("Repeater Crossbow", ["repeating crossbow", "crossbow"]),
        ("Throwing Knives", ["throwing knife"]),
        ("Berserker Armor", ["berserk armor"]),
    ]),
]

# Questions whose gold is a curated core list rather than the complete set the
# wiki keeps. Precision is meaningless on these and is not aggregated over
# them: `Every technique Goku uses` names eight, and the Dragon Ball wiki
# really does record 194 techniques with Goku as a user, so a correct answer
# scores about 4% precision. Recall still counts.
RECALL_ONLY = {
    "Every technique Goku uses",
}


def norm(text: str) -> str:
    text = unicodedata.normalize("NFKD", text or "")
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower().replace("&", "and")
    text = re.sub(r"[^a-z0-9%]+", " ", text)
    # A plural is not a different technique. The engine returned `Machine Gun
    # Blow` for the wiki's `Machinegun Blows` and was scored a miss for it.
    # Folded on both sides, so it can only ever merge a name with its own
    # plural -- this is not substring matching, which stays deliberately out:
    # `Super Saiyan` must not match `Super Saiyan 2`. Four-letter words and up,
    # so `gas`, `ren` and `nen` survive intact.
    text = re.sub(r"\b(\w{3,})s\b", r"\1", text)
    return " ".join(text.split())


def ask(series: str, query: str) -> dict:
    payload = json.dumps({"series": series, "query": query, "mode": "auto",
                          "token_budget": 60000}).encode()
    request = urllib.request.Request(
        f"{BASE}/context", data=payload,
        headers={"Content-Type": "application/json"})
    start = time.time()
    with urllib.request.urlopen(request, timeout=300) as response:
        body = json.loads(response.read())
    body["_seconds"] = round(time.time() - start, 2)
    return body


def main() -> None:
    rows = []
    detail = []
    for series, query, canon in GOLD:
        body = ask(series, query)
        members = [m if isinstance(m, str) else (m.get("name") or m.get("title") or "")
                   for m in (body.get("members") or [])]
        confidence = body.get("confidence") or "-"
        chosen = body.get("basis") or "-"
        available = body.get("members_available", len(members))
        seen = {norm(m) for m in members}

        found, missing, matched_members = [], [], set()
        for item, aliases in canon:
            keys = [norm(item)] + [norm(a) for a in aliases]
            hit = next((k for k in keys if k in seen), None)
            if hit:
                found.append(item)
                matched_members.add(hit)
            else:
                missing.append(item)

        recall = len(found) / len(canon) if canon else 0.0
        precision = len(matched_members) / len(members) if members else 0.0
        rows.append({
            "series": series, "query": query, "set": chosen,
            "confidence": confidence, "returned": len(members),
            "available": available,
            "canon": len(canon), "found": len(found),
            "recall": round(recall, 3), "precision": round(precision, 3),
            "recall_only": query in RECALL_ONLY,
        })
        detail.append({
            "query": query, "found": found, "missing": missing,
            "members": members,
        })
        print(f"{recall:5.0%} recall  {precision:5.0%} prec  "
              f"{len(found)}/{len(canon):<3} of canon  "
              f"n={len(members):<4} {confidence:9} {query[:46]}")

    exact_wrong = [r for r in rows
                   if r["confidence"] in {"exact", "declared"} and r["recall"] < 0.5]
    total_found = sum(r["found"] for r in rows)
    total_canon = sum(r["canon"] for r in rows)
    total_returned = sum(r["returned"] for r in rows)
    # Precision is aggregated only over the questions whose gold is a complete
    # set. Including the open-ended ones measures the wiki's breadth, not the
    # engine's aim.
    scored = [r for r in rows if not r["recall_only"]]
    scored_found = sum(r["found"] for r in scored)
    scored_returned = sum(r["returned"] for r in scored)

    print("\n" + "=" * 78)
    print(f"canon items recovered : {total_found}/{total_canon} "
          f"({total_found / total_canon:.1%})")
    print(f"members returned      : {total_returned}, of which "
          f"{total_found} are canon ({total_found / total_returned:.1%})")
    print(f"precision (closed sets): {scored_found}/{scored_returned} "
          f"({scored_found / scored_returned:.1%}) over "
          f"{len(scored)}/{len(rows)} questions")
    print(f"questions at recall=0 : {sum(1 for r in rows if r['found'] == 0)}/{len(rows)}")
    print(f"questions at recall>=0.8: {sum(1 for r in rows if r['recall'] >= 0.8)}/{len(rows)}")
    print(f"confident and wrong   : {len(exact_wrong)} "
          f"(confidence exact/declared, recall < 50%)")
    for r in exact_wrong:
        print(f"    {r['confidence']:9} recall {r['recall']:.0%}  {r['query']}")

    out = sys.argv[1] if len(sys.argv) > 1 else "canon_scores.json"
    with open(out, "w", encoding="utf-8") as handle:
        json.dump({"rows": rows, "detail": detail}, handle, indent=2)
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
