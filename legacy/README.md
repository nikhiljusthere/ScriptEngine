# legacy/

The previous pipeline. Kept for reference until Phase 5 confirms the replacement
extracts at least as much as this did, then deleted.

**Nothing here is imported by ScriptEngine.** Several of these files cannot run
at all.

| File | Why it was retired |
|---|---|
| `step1_crawler_original.py` | Superseded, but the **best code in the old repo**. MediaWiki API over HTML scraping, `curl_cffi` browser impersonation, `allpages` enumeration, 10 async workers, 429/`Retry-After` handling. Its concurrency and retry design carries into `ingest/crawler.py`. |
| `step2_build_graph.py`, `_v2`, `_v3`, `_v6` | Four iterations, ~3,700 lines, rebuilding entities from prose with spaCy NER, regex relation patterns, and hardcoded JJK alias tables. The wikitext already contains this. `_v6`'s ideas survive as schema columns: provenance and confidence on edges, canon/modulo universe tagging, chronology edges. `_v3` and `_v6` also point at `E:\VS CODE\...` (with spaces), a path that does not exist. |
| `step3_chunk_and_embed.py` | Section detection matched a bare `appearance` against a corpus of `## Appearance`, so every document collapsed to one section. Citation stripping targeted `[1]` while the cleaner emitted full reference text. Entity tagging was substring matching over every entity × every chunk. |
| `step4_generation.py` | Imports `python.step3_retrieval`, which does not exist. References an undefined `FINAL_TOP_K`. Loaded Qwen2.5-7B in-process, competing for VRAM with the embedder and reranker. |
| `step5_retrieval.py` | The **retrieval architecture was right** — vector ∪ BM25 ∪ graph → RRF → cross-encoder → parent expansion — and is ported to `retrieve/hybrid.py`. The Cypher used `[r*1..$depth]`, which Neo4j rejects. BM25 rebuilt an in-memory index from a full Qdrant scroll on every process start. |
| `fandom_cleaner_fixed_v2.py` | HTML→text cleaner. Obsolete now that wikitext is parsed directly, but its navbox/gallery/ambox suppression lists and its `list_battles` / `list_episodes` extractors encode real knowledge about Fandom markup. |
| `clean_all_files.py` | In-place regex rewriter hardcoded to a path that no longer exists, applying JJK-specific capitalisation. |
| `config.py` | Declared Postgres, Redis, Elasticsearch, LangGraph, `bge-m3`, and a `qwen2.5-72b` Ollama model. No module imported it; every stage hardcoded its own conflicting values, including a different Neo4j password. |
| `cli_original.py`, `helper_original.py` | Thin argparse wrapper and a path helper. The wrapper wrote `test.txt` on every run — that file ended up in the scraped corpus. |

## The corpus

`out/step_one_raw_scrapped_data/` still holds the original crawl: 850 raw HTML
pages (61 MB) and 846 cleaned `.txt` (13 MB) from the Jujutsu Kaisen wiki. Both
are gitignored and stay untouched until Phase 5 verifies the new extraction
against them.

The cleaned set is not trustworthy as-is. Around 16 files are not wiki pages at
all — `LICENSES.chromium.txt`, `angular.txt`, `tslib.txt`, `docindex.txt` — from
a cleaner run pointed at a directory of Chromium and Angular documentation.
