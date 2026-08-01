# API

> The service lands in Phase 4. This page records the intended contract so the
> ComfyUI side can be planned against it; the endpoints do not exist yet.

```powershell
python -m scriptengine.api.main    # http://127.0.0.1:8000
```

Local-bound by default. Override with `SCRIPTENGINE_API_HOST` /
`SCRIPTENGINE_API_PORT`.

## The endpoint that matters

### `POST /context`

Everything else is for inspection. This is what the script-writing model calls.

```jsonc
{
  "series": "jjk",
  "query": "the Shibuya Incident",
  "mode": "narrative",      // "narrative" | "qa"
  "token_budget": 6000
}
```

Returns passages **in narrative order** — not similarity order — with the
structured facts behind them and a citation per claim:

```jsonc
{
  "series": "jjk",
  "mode": "narrative",
  "beats": [
    {
      "order": 1,
      "title": "Shibuya Incident / Early Stages",
      "time": "7:00 P.M. - 8:31 P.M.",
      "participants": ["Satoru Gojo", "Suguru Geto"],
      "text": "...",
      "citations": [{"source": "Jujutsu Kaisen Manga", "volume": 10, "page": 26}],
      "doc": "Shibuya Incident",
      "section": "Event / Early Stages"
    }
  ],
  "facts": [
    {"entity": "Satoru Gojo", "key": "grade", "value": "Special Grade", "citation": {...}}
  ],
  "tokens_used": 5840
}
```

`mode: "narrative"` walks chronology edges and returns ordered beats.
`mode: "qa"` returns relevance-ranked passages after reranking. Use narrative for
scripts; the ordering *is* the value.

Citations are the point. A script whose claims cannot be traced back to the wiki
is a script you have to fact-check by hand.

## Inspection endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health` | Liveness, loaded models, resolved device |
| `GET` | `/series` | Series on disk and what has been built for each |
| `POST` | `/search` | Hybrid retrieval, ranked passages with scores |
| `GET` | `/facts/{entity}` | Exact structured facts — infobox-derived, not retrieved |
| `GET` | `/timeline/{arc}` | Ordered events within an arc |

`/facts/{entity}` is a lookup, not a search. Because infobox parameters are
stored as facts rather than flattened into prose, the answer is exact. Ask for a
character's grade or debut chapter here rather than hoping retrieval surfaces it.

## Wiring ComfyUI

The script-writing model needs one HTTP call. Sketch:

```python
import httpx

bundle = httpx.post("http://127.0.0.1:8000/context", json={
    "series": "jjk",
    "query": arc_name,
    "mode": "narrative",
    "token_budget": 6000,
}, timeout=60).json()

prompt = "\n\n".join(
    f"[{b['order']}] {b['title']}\n{b['text']}" for b in bundle["beats"]
)
```

Keep `token_budget` under what the model can hold alongside its instructions.
The service truncates at beat boundaries, never mid-beat, so a smaller budget
costs you later beats rather than a mangled one.

**On VRAM:** ScriptEngine holds ~3.5 GB of embedding and reranking models while
serving, and releases them after `SCRIPTENGINE_MODEL_IDLE_UNLOAD_SECONDS`. If
ComfyUI is rendering on the same GPU, either set `SCRIPTENGINE_DEVICE=cpu` or
call `/context` before the render starts.

## Errors

Standard codes. `404` for an unknown series or entity, `422` for a malformed
body, `503` when a series exists but has not been indexed — with the command to
fix it in the message body.
