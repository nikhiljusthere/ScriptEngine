# Big review v2, half2 notes (b12068–b14000)

Reviewer: the app-side Claude session, cursor `BV2_CURSOR=half2`. Rows were appended to
`big_audit_v2.jsonl` only. Nothing was committed and no code was changed. The proposals below
are for the peer to measure and adopt or reject.

## Scope
- 1,933 windows, b12068–b14000, all marked (cursor `review_cursor_v2_half2.txt` = 14000).
- Edit files e041–e098, plus the fix files e046b, e049b, e052b, e062fix and e078b.

## Tool behaviour worth documenting
- `f-` matches S|rel|O whatever the modality and removes every matching row. `f- S|rel|-` matches a None object.
- The fact dedupe key is (subject, relation, object, modality). An `f+` that differs only by modality adds a second row.
- `r` renames the subject, the object and asserted_by. A later `f-` in the same block must use the new name, or it prints UNMATCHED. UNMATCHED lines do not carry the FIXED prefix.
- When an alias subject is renamed, the alias row breaks. Use `-`/`+` for that block instead of `r`.
- A REFUSED block is not stored at all. Resubmit the whole block.
- The base shown is the latest audit state, so a second edit file builds on the first.

## Ends the gate refuses (observed)
- Race pages used as event ends: Chitauri, Soul Eaters. Use a crowd_end tag.
- Ordinal places ("29th Precinct"), "X and Y" places ("Nelson and Murdock Law Office"), and possessive descriptions ("Wilson's former Sargent").
- Quotes under 12 characters.

## Frequent base errors (each seen in many windows; not yet measured)
1. asserted_by is set on actual rows. The usual case is "stated"/"replied" carrying `claimed/X`.
2. "tried"/"attempted"/"trying" is used as other_verb (A134 violations).
3. `discovered <clause object>` should be `learned|-`. This is very common.
4. `X|other_verb|<Name>`: a name is used as the verb (A125). Adjectives and copulas also appear ("was", "became", "stunned", "attracted", "unnoticed").
5. Reversed `wounded` and `parent_of` rows. A spouse was also given as a parent (Doris Toomes).
6. Mind projections and illusions are given fought/defeated (A124).
7. Quote pages and list pages are given facts (B.9).
8. Rank prefixes split one person ("Captain Carter"), as do bare first names (Kang, Janet, Cassie).
9. A confrontation that becomes the fight still gets a `met`, and `fought` still sits next to a `defeated`/`killed` (A145).

## Measured
- Of the 1,271 approved `X|ordered|Y` facts, 576 carry the `ordered` modality. Per the rules, an order is actual. **Proposal:** a gate flag for `ordered` relation + non-actual modality.

## Corrections made by me
- A97: I had briefly changed `gave` objects to items. I reverted all of them to the recipient in e062fix.
