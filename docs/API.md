# API

```powershell
python -m scriptengine.api.main    # http://127.0.0.1:8000
```

Local-bound by default. Override with `SCRIPTENGINE_API_HOST` /
`SCRIPTENGINE_API_PORT`.

## The endpoint that matters

### `POST /context`

Everything else is for inspection. This is what the script writer calls.

```jsonc
{
  "series": "jjk",
  "query": "Shibuya Incident",
  "mode": "auto",           // "auto" | "narrative" | "roster" | "qa"
  "token_budget": 24000,
  "top_k": 12,              // passages (qa) or beats (narrative)
  "words": 3000,            // target script length, stated in the served rules
  "intro": true,            // whether the script opens with a hook paragraph
  "rules": true,            // append the style/voice/annotation rules
  "as_prompt": true         // also return the bundle rendered as plain text
}
```

`mode` decides the shape of the answer, because the shape of a script topic
varies more than its subject does:

| Mode | Topic | Returns |
|---|---|---|
| `narrative` | an account: "Shibuya Incident" | beats in story order, across the subject's page and the pages it leans on |
| `roster` | a set: "Every Rank of Curse" | every member of the set the wiki declares, grouped and ordered |
| `qa` | a question | relevance-ranked passages after reranking |
| `auto` | either | reads the topic; falls back to `narrative` if a roster comes back empty |

Use `auto` unless you know better. The ordering *is* the value: a script written
from relevance-ranked fragments reads like a wiki summary.

#### A narrative bundle

```jsonc
{
  "series": "jjk",
  "mode": "narrative",
  "subject": "Shibuya Incident",           // the page the topic resolved to
  "beats": [
    {
      "order": 1,
      "title": "Prologue",
      "doc_title": "Shibuya Incident",
      "breadcrumb": "Prologue",
      "time": "7:00 PM",                   // when the heading carries a clock time
      "text": "...(Chapter 145, Episode 50) ...",
      "citations": ["(Chapter 145, Episode 50)", "(Chapter 10, Episode 5)"],
      "source_span": "Chapters 10-145, Episodes 5-50"
    }
  ],
  "participants": ["Satoru Gojo", "Kento Nanami"],
  "facts": [
    {"entity": "Shibuya Incident", "field": "Manga", "value": "Chapter 83 - 136", "citation": ""}
  ],
  "truncated": true,
  "beats_available": 61,
  "tokens_used": 23937
}
```

`source_span` is the tag the script puts at the end of that block. It is never
empty for prose the wiki cited: see "Sourcing" below.

#### A roster bundle

```jsonc
{
  "mode": "roster",
  "subject": "Cursed Spirit",
  "basis": "Cursed Spirits (class)",       // the set, and the field it is grouped by
  "kind": "category",                      // category | type | sections | declared
  "confidence": "declared",                // declared | exact | partial | weak
  "unmatched": [],                         // words in the set's name the topic never asked for
  "warning": "",                           // populated when confidence is partial or weak
  "candidates": 160,                       // what the wiki's set held before validation
  "scope": "canon",                        // canon | all
  "rejected": [                            // and why each one does not belong
    {"name": "Black Frieza", "reason": "not saiyan"},
    {"name": "Class-up", "reason": "outside the story (Game: Dragon Ball Heroes)"}
  ],
  "groups": ["Grade 2", "Special Grade"],
  "members": [
    {
      "name": "Jogo",
      "label": "character",
      "group": "Special Grade",
      "debut": "(Chapter 10, Episode 5)",
      "facts": [{"field": "Grade", "value": "Special Grade"}],
      "text": "...",
      "citations": ["(Chapter 10, Episode 5)"],
      "source_span": "Chapters 10-122, Episodes 5-42"
    }
  ],
  "members_available": 22,
  "tokens_used": 12887
}
```

`confidence` says how well the set the wiki gave back matches the set that was
asked for, because discovery cannot decline to answer. `declared` and `exact`
are trustworthy; `partial` means the set carries a word the topic never
mentioned. "Every Straw Hat Pirate" returns `Straw Hat Pirates' Creations`,
`partial` on *creations*, which is the crew's weapons rather than the crew, and
`weak` means nothing in the topic matched the set's name at all.

It does not detect an *incomplete* set: `Grand Line Islands` reports `exact` and
returns four members where the wiki has hundreds of islands filed elsewhere. Use
`members_available` against the size you expect.

`candidates` and `rejected` are membership validation. A category is what the
wiki keeps, not what the topic asked for: `Transformations` holds Black Frieza
because it is one, and only the topic knows that "Saiyan" was the point. Each
candidate is checked against the topic's constraints (ownership, race, media)
and what fails is reported rather than dropped quietly.

`scope` is `canon` by default: film, manga and anime material only. Game and
spin-off entries stay in the store and come back when the topic asks for them
("every transformation **ever**", "**including games**"), which sets
`scope: "all"`.

Members are paid for out of an equal share of the budget, so a long biography at
the top of the list cannot spend what the tail needed.

#### `as_prompt`

Adds a `prompt` field: the bundle as plain text, followed by the house style,
voice and annotation rules from `scriptengine/api/rules.py`. Two things are
deliberately absent from it: bare `[n]` order markers, which the house rules
forbid in a script, and a repeated `source:` line under every beat.

## Sourcing

Every beat and member carries the chapters and episodes its prose comes from.
Two lookups produce them, in `scriptengine/retrieve/citations.py`:

- **A `{{Ref}}` covers the sentences before it**, back to the previous
  reference, which is what putting it there means. Without this, 12.8% of the
  sentences in a Shibuya Incident bundle carried a locator and 60 of its 128
  beats carried none; with it the page reaches 99.6%.
- **A chapter resolves to its episode through the graph**, via
  `Chapter N -anime episode-> Episode M` and `Episode M -adapted from-> Chapter N`.
  Half the corpus's references name a chapter and no episode. A chapter the
  anime never adapted resolves to nothing and stays `(Chapter N)`.

Nothing is inferred beyond that. `python -m scriptengine.cli audit --series jjk`
reports the resulting coverage and fails a check when citations stop reaching
the prose.

## Inspection endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health` | Liveness, loaded models, resolved device, series on disk |
| `GET` | `/series` | Series and what has been built for each |
| `POST` | `/search` | Hybrid retrieval, ranked passages with scores |
| `GET` | `/facts/{series}/{entity}` | Exact structured facts, infobox-derived rather than retrieved |
| `GET` | `/abilities/{series}/{entity}` | Every ability a character uses, walked from the graph |
| `GET` | `/timeline/{series}/{subject}` | An event as ordered beats |

`/facts/{series}/{entity}` is a lookup, not a search. Because infobox parameters
are stored as facts rather than flattened into prose, the answer is exact. Ask
for a character's grade or debut chapter here rather than hoping retrieval
surfaces it.

`/abilities/{series}/{entity}` exists because prose retrieval cannot answer
"every ability of X" reliably: a multi-entity question ranks battle pages above
ability pages. The graph does not care: `Black Flash -user-> Yuji Itadori` is an
edge.

## Budget

Keep `token_budget` under what the writer can hold alongside its instructions.
The service truncates at beat boundaries, never mid-beat, so a smaller budget
costs you later beats rather than a mangled one. Oversized beats are split at
sentence boundaries and each part is re-sourced, so no part loses the citation
that covers it.

**On VRAM:** ScriptEngine holds ~3.5 GB of embedding and reranking models while
serving `qa` mode, and releases them after
`SCRIPTENGINE_MODEL_IDLE_UNLOAD_SECONDS`. `narrative` and `roster` need neither
model. If ComfyUI is rendering on the same GPU, either set
`SCRIPTENGINE_DEVICE=cpu` or call `/context` before the render starts.

## Errors

Standard codes. `404` for an unknown entity or an event with no narrative, `422`
for a malformed body or an invalid series name, `503` when a series exists but
has not been indexed, with the command to fix it in the message body.
