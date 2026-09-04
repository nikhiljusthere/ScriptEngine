# Scroll-box fix — reviewer findings to verify before applying

**These are claims to verify, not instructions to follow on trust.** Reproduce
each one yourself. If your results disagree with mine, **yours win — say so and
stop.** Nothing below authorises editing `scriptengine/`; the parser change stays
proposed until it is approved.

Your root-cause diagnosis is correct and your fix design is right. I patched a
**scratch copy** of the parser and diffed it against the live one over all 987
cached wikitext pages: 91 pages changed — your number exactly — 896 byte
identical, 979 lines added, 0 layout leaks. Three things came out of that review
that change what gets applied.

## Claim 1 — the diff in RESULTS does not compile

The list comprehension closes with `")]` and is then followed by a second `]`.
Applied verbatim it raises `SyntaxError: unmatched ']'` on import of
`scriptengine/ingest/wikitext.py`, which takes down the whole pipeline.

Test all three forms in context — no files touched:

```python
import textwrap
CTX = ("TRANSPARENT_TEMPLATES={'scroll box':'all'}\n"
       "TRANSPARENT_NAMED_PARAMS={'scroll box':{'content'}}\n"
       "lowered='scroll box'; positional=[]\n"
       "named={'content':'*[[A]]','height':'200px'}\n"
       "if False:\n    pass\n")

def try_form(label, body):
    ns = {}
    try:
        exec(CTX + textwrap.dedent(body).rstrip(), ns)
        print(f"{label:12s} -> candidates = {ns.get('candidates')}")
    except SyntaxError as e:
        print(f"{label:12s} -> SyntaxError line {e.lineno}: {e.msg}")

try_form("current", """
elif lowered in TRANSPARENT_TEMPLATES:
    candidates = [p for p in positional if p and not p.startswith("[[Category")]
""")
try_form("proposed", """
elif lowered in TRANSPARENT_TEMPLATES:
    named_prose = TRANSPARENT_NAMED_PARAMS.get(lowered, ())
    candidates = [p for p in positional if p and not p.startswith("[[Category")]
    candidates += [
        named[k] for k in sorted(named_prose & named.keys())
        if named[k] and not named[k].startswith("[[Category")]
    ]
""")
try_form("corrected", """
elif lowered in TRANSPARENT_TEMPLATES:
    named_prose = TRANSPARENT_NAMED_PARAMS.get(lowered, ())
    candidates = [p for p in positional if p and not p.startswith("[[Category")]
    candidates += [
        named[k] for k in sorted(named_prose & named.keys())
        if named[k] and not named[k].startswith("[[Category")
    ]
""")
```

Expected: `current -> []` (the bug), `proposed -> SyntaxError`, `corrected ->
['*[[A]]']` with `height` correctly absent. Apply the **corrected** form.

## Claim 2 — measure the blast radius without touching the ingest file

The technique matters more than my numbers: patch a scratch copy, import it
under a second name, diff both parsers over the whole corpus. This is how a
forbidden-file change gets evidence before approval.

```python
import json, glob, os, sys, tempfile, importlib.util, difflib
import scriptengine.ingest.wikitext as cur

# 1. scratch copy, patched (do NOT write into scriptengine/)
src = open('scriptengine/ingest/wikitext.py', encoding='utf-8').read()
src = src.replace(
    'TRANSPARENT_TEMPLATES: dict[str, str] = {',
    'TRANSPARENT_NAMED_PARAMS: dict[str, set[str]] = {\n'
    '    "scroll box": {"content"},\n}\n\n'
    'TRANSPARENT_TEMPLATES: dict[str, str] = {', 1)
old = ('        elif lowered in TRANSPARENT_TEMPLATES:\n'
       '            candidates = [p for p in positional '
       'if p and not p.startswith("[[Category")]\n')
new = ('        elif lowered in TRANSPARENT_TEMPLATES:\n'
       '            named_prose = TRANSPARENT_NAMED_PARAMS.get(lowered, ())\n'
       '            candidates = [p for p in positional '
       'if p and not p.startswith("[[Category")]\n'
       '            candidates += [\n'
       '                named[k] for k in sorted(named_prose & named.keys())\n'
       '                if named[k] and not named[k].startswith("[[Category")\n'
       '            ]\n')
assert src.count(old) == 1
src = src.replace(old, new, 1)
tmp = tempfile.mkdtemp() + '/wikitext_fixed.py'
open(tmp, 'w', encoding='utf-8').write(src)

# 2. import the patched copy alongside the real one
spec = importlib.util.spec_from_file_location("wikitext_fixed", tmp)
fix = importlib.util.module_from_spec(spec)
sys.modules["wikitext_fixed"] = spec.name and fix   # must be registered first
spec.loader.exec_module(fix)

# 3. diff both parsers over every cached page
changed = added = removed = leaks = 0
for f in sorted(glob.glob('series/jjk/wikitext/*.json')):
    d = json.load(open(f, encoding='utf-8'))
    txt = d if isinstance(d, str) else (d.get('wikitext') or d.get('text') or '')
    a, b = cur.strip_markup(txt), fix.strip_markup(txt)
    if a == b:
        continue
    changed += 1
    for l in difflib.unified_diff(a.splitlines(), b.splitlines(), lineterm='', n=0):
        if l.startswith('+') and not l.startswith('+++'):
            added += 1
            if any(t in l.lower() for t in ('height=', 'width=', 'px;', 'background:')):
                leaks += 1
        elif l.startswith('-') and not l.startswith('---'):
            removed += 1
print(f'changed={changed} added={added} removed={removed} leaks={leaks}')
```

Expected: `changed=91 added=979 removed=1 leaks=0`. The single removal is an
**empty string** on `Chapter 57` — a blank line replaced by six character names,
not content loss. Confirm that yourself before accepting it; a nonzero removal
count is exactly the kind of number that should not be waved through.

Recovery is not chapter-only: `Aizo` gains 47 character names and `Ao no Sumika`
13, alongside the 83 chapter OOA sections.

## Claim 3 — re-index, do not re-crawl

Your plan says "re-crawl/re-index chapter pages". A re-crawl pulls whatever the
wiki says *today*, which can move content underneath ~55k existing gold answers
for reasons that have nothing to do with this fix. `index` parses the **stored**
wikitext — that is the stated premise of `resolve-templates` — and the 91-page
delta above was measured against that same cache, so a re-index alone reproduces
exactly this change and nothing else. If you think a re-crawl is needed, make it
a separate proposal with its own gate.

(`resolve-templates` was considered as a lower-risk alternative and does not
apply: it splices in `Template:`-namespace pages the crawler skips, whereas this
content is already inline in the page's own wikitext. Confirm that reading if
you disagree.)

## Suggested: pin the defect with a test

The campaign's pattern is that a defect found once gets a test so it cannot
silently return. No existing test pins this behaviour — `tests/test_templates.py:54`
only asserts that bare `{{Scroll box}}` with no params is furniture, which stays
true under the fix. Consider adding, in the same style:

- named `|content=` list is kept (the bug, pinned);
- positional list still kept (no regression);
- `height`/`width` never reach prose (the scoping);
- bare `{{Scroll box}}` still yields nothing (the existing contract).

## On approval, in this order

1. Apply the **corrected** diff to `scriptengine/ingest/wikitext.py`.
2. `index --series jjk` — **no re-crawl**.
3. `span-recall --series jjk` — expect only the two known
   `Chapter 239 / References` misses. Anything else means the re-index moved
   something and you stop and report.
4. `pytest tests/ -q` and `eval --series jjk`. Additive text cannot invalidate a
   verbatim gold, but it can shift chunk boundaries on the 91 changed pages, so
   confirm rather than assume.
5. Only then the Hybrid roster build (~550 `overrides.yaml` entries — also
   propose-and-approve, not autonomous).

## Standing rules, unchanged

- Verbatim substrings only; **never reword a question to dodge a failure** —
  diagnose it as a gold error or an engine gap.
- `scriptengine/`, `overrides.yaml`, and batch files outside the page in hand
  stay forbidden to the execution tier: propose and stop.
- The 5 standing opens stay out of scope. The uncommitted router `against` fix
  stays uncommitted. Nothing gets committed unless explicitly asked.

Full detail, including the param census and the test-compile results, is in
`reports/page-campaign/CHAPTER_TRANCHE_ROSTER_CHECK.md` under "Reviewer
verification of the proposed parser fix".
