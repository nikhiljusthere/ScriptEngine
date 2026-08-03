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
    ("opm", "Every technique of Genos", [
        ("Incinerate", ["incineration cannon"]),
        ("Machine Gun Blows", ["machine gun punch"]),
        ("Jet Drive Arrow", []),
        ("Blazing Charge", []),
        ("Arms Gatling", []),
    ]),
    ("jjk", "How many 1v1 battles did Yuji Itadori have with named characters", [
        ("Yuji Itadori vs. Aoi Todo", ["yuji vs todo"]),
        ("Yuji Itadori vs. Junpei Yoshino", ["yuji vs junpei"]),
        ("Yuji Itadori vs. Mahito", ["yuji vs mahito"]),
        ("Yuji Itadori vs. Choso", ["yuji vs choso"]),
        ("Yuji Itadori vs. Sukuna", ["yuji vs sukuna"]),
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
    ("berserk", "Every armor of Guts", [
        ("Black Swordsman Armor", ["black swordsman"]),
        ("Berserker Armor", ["berserk armor"]),
    ]),
]


def norm(text: str) -> str:
    text = unicodedata.normalize("NFKD", text or "")
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower().replace("&", "and")
    text = re.sub(r"[^a-z0-9%]+", " ", text)
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
    print("\n" + "=" * 78)
    print(f"canon items recovered : {total_found}/{total_canon} "
          f"({total_found / total_canon:.1%})")
    print(f"members returned      : {total_returned}, of which "
          f"{total_found} are canon ({total_found / total_returned:.1%})")
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
