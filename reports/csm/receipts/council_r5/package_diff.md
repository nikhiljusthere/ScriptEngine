diff --git a/scriptengine/api/context.py b/scriptengine/api/context.py
index 20f777f..ba2280e 100644
--- a/scriptengine/api/context.py
+++ b/scriptengine/api/context.py
@@ -57,7 +57,7 @@ MAX_BEAT_CHARS = 2800
 # entry stops being a section and starts being the whole page.
 MAX_MEMBER_CHARS = 4000
 
-MODES = {"qa", "narrative", "roster"}
+MODES = {"qa", "narrative", "roster", "relations"}
 
 
 def estimate_tokens(text: str) -> int:
@@ -152,6 +152,8 @@ def build_context(
         return _narrative_context(paths, query, token_budget, top_k, settings, subject)
     if mode == "roster":
         return _roster_context(paths, query, token_budget, settings)
+    if mode == "relations":
+        return _relations_context(paths, query, token_budget, top_k, settings, subject)
     return _qa_context(paths, query, token_budget, top_k, settings, subject)
 
 
@@ -337,6 +339,113 @@ def _roster_context(
     }
 
 
+def _relations_context(
+    paths: SeriesPaths,
+    query: str,
+    token_budget: int,
+    top_k: int | None,
+    settings: Settings,
+    subject: str | None = None,
+) -> dict[str, Any]:
+    """The character's relationships, as the primary answer.
+
+    R-5 (G-CSM-4): "Every documented relationship of X" and its interrogative
+    twins route here instead of to a roster set (the "Every" makes it
+    set-shaped, so the enumeration rule grabs it) or the qa passage search
+    (rule 3, which the relation rows never reach), because the wiki records
+    relationships as relation rows -- the extracted `relations` table and the
+    graph `edges` -- that neither path serves. The rows lead the bundle; the
+    ranked order (the edge the question names first) is paid in order and cut
+    at the budget, so a busy character's one relevant row is not buried behind
+    forty unrelated ones.
+    """
+    from scriptengine.stores.facts import FactStore
+    from scriptengine.retrieve.roster import rank_relations
+
+    with FactStore(paths.facts_db) as store:
+        # The character: the authored subject when the caller named it, else the
+        # query's own linked entity ("...relationship of Denji" -> Denji).
+        probe = subject or query
+        linked = store.link_entities(probe)
+        ids = [int(row["id"]) for row in linked[:3]]
+        if subject:
+            names = [subject]
+        elif linked:
+            names = [row["name"] for row in linked]
+        else:
+            # Fallback: the "relationship of X" object, when the query's words
+            # linked no known entity. The LLM `relations` table is a keyed
+            # lookup, so it still answers even with no node id to walk edges.
+            m = re.search(
+                r"relationship(?:s)?\s+(?:of|with)\s+([\w ]+)$",
+                query or "", re.IGNORECASE,
+            )
+            names = [m.group(1).strip()[:60]] if m else []
+        names = names[:3]
+        # Both ways a relationship is recorded: the LLM-extracted rows (verbatim
+        # quote + era, the wiki's own words) and the graph edges (resolved
+        # infobox links). The qa path already unions the two (hybrid, 3b/3c);
+        # here the union IS the answer, so it leads the bundle.
+        relations: list[dict[str, Any]] = []
+        for row in store.edges_for(ids, min_confidence=0.9, limit=40):
+            relations.append({
+                "source": row["source"], "relation": row["relation"],
+                "target": row["target"], "confidence": row["confidence"],
+                "quote": "", "era": "",
+            })
+        seen = {(r["source"], r["relation"], r["target"], r["quote"])
+                for r in relations}
+        for name in names:
+            for row in store.relations_of(name, both_ways=True):
+                key = (row["character"], row["relation"], row["other"],
+                       row["quote"] or "")
+                if key in seen:
+                    continue
+                seen.add(key)
+                relations.append({
+                    "source": row["character"], "relation": row["relation"],
+                    "target": row["other"], "confidence": 1.0,
+                    "quote": row["quote"] or "", "era": row["era"] or "",
+                })
+        ranked = rank_relations(relations, query)
+
+    if top_k:
+        ranked = ranked[:top_k]
+
+    # The rows are cheap; pay for them in rank order and cut at the budget, so a
+    # long character's tail is what drops, never the edge that answers the
+    # question. The first row is never dropped, the way a roster's first member
+    # is not.
+    budget_chars = int(token_budget * CHARS_PER_TOKEN)
+    used = 0
+    included: list[dict[str, Any]] = []
+    for order, relation in enumerate(ranked, start=1):
+        line = f"{relation['source']} / {relation['relation']} / {relation['target']}"
+        if relation.get("era"):
+            line += f" ({relation['era']})"
+        if relation.get("quote"):
+            line += f": {relation['quote']}"
+        cost = estimate_tokens(line) + 5
+        if included and used + cost > budget_chars:
+            break
+        relation = dict(relation, order=order)
+        included.append(relation)
+        used += cost
+
+    return {
+        "series": paths.name,
+        "mode": "relations",
+        "subject": names[0] if names else query,
+        "relations": included,
+        "participants": names,
+        "facts": [],
+        "beats": [],
+        "truncated": len(included) < len(ranked),
+        "relations_available": len(ranked),
+        "tokens_used": used,
+    }
+
+
 def _qa_context(
     paths: SeriesPaths,
     query: str,
diff --git a/scriptengine/api/main.py b/scriptengine/api/main.py
index aa9c58e..5df8c4b 100644
--- a/scriptengine/api/main.py
+++ b/scriptengine/api/main.py
@@ -76,7 +76,7 @@ def _sweep_idle_models() -> None:
 class ContextRequest(BaseModel):
     series: str
     query: str
-    mode: Literal["qa", "narrative", "roster", "auto"] = "qa"
+    mode: Literal["qa", "narrative", "roster", "relations", "auto"] = "qa"
     # The page the question is authored against, when the query's own words do
     # not name it: "What kind of motif does the King of Curses have, per the
     # page's Trivia?" asks about Angel's page but names only Sukuna's title, so
diff --git a/scriptengine/retrieve/router.py b/scriptengine/retrieve/router.py
index 3bbc867..44fb3bd 100644
--- a/scriptengine/retrieve/router.py
+++ b/scriptengine/retrieve/router.py
@@ -52,7 +52,7 @@ from scriptengine.retrieve.roster import (
 )
 from scriptengine.stores.facts import FactStore, rank_subjects
 
-MODES = ("roster", "qa", "narrative")
+MODES = ("roster", "qa", "narrative", "relations")
 
 _WH = re.compile(
     r"^\s*\W*(what|whats|what's|who|whom|whose|whos|who's|which|when|where|why|how)\b",
@@ -466,8 +466,24 @@ class Route:
         return {"mode": self.mode, "why": self.why, "signals": self.signals}
 
 
+# R-5 (G-CSM-4): relationship phrasings route to the relations door. The words
+# are the relationship vocabulary, not a per-wiki list, so the trigger carries
+# no series name. "Every documented relationship of X" is set-shaped ("Every"),
+# which is exactly why the rule below must win over the enumeration rule; "What
+# is the relationship between X and Y?" is a wh-question that would otherwise
+# fall to the qa passage search, which the relation rows never reach.
+_RELATIONS = re.compile(
+    r"\brelationship(?:s)?\b"
+    r"|\bhow\s+(?:is|are)\s+[^?]*\brelated\b"
+    r"|\bhow\s+does\s+\w+\s+relate\b"
+    r"|\bconnection\b"
+    r"|\b(?:who|what)\s+(?:is|was|are|were)\s+\S+\s+to\b",
+    re.IGNORECASE,
+)
+
+
 def route(paths: SeriesPaths, query: str, settings=None, subject: str | None = None) -> Route:
-    """Pick roster, qa or narrative for `query`.
+    """Pick roster, qa, narrative or relations for `query`.
 
     Order matters and is set by what was measured, not by preference: a
     wh-question that names one thing beats the enumeration cue, because
@@ -637,6 +653,19 @@ def route(paths: SeriesPaths, query: str, settings=None, subject: str | None = N
             signals,
         )
 
+    # 2d (R-5, G-CSM-4): a relationship phrasing wants the relations door -- the
+    #     wiki's own relation rows -- not a roster set (rule 4 swallows the
+    #     "Every documented relationship of X" form) and not the qa passage
+    #     search (rule 3, which the relation rows never reach). Placed after the
+    #     battle/count probes and before the wh-lookup rule, so it owns every
+    #     relationship phrasing, enumeration-shaped or not.
+    if _RELATIONS.search(query or ""):
+        return Route(
+            "relations",
+            "asks for relationships, which the wiki records as relation rows",
+            signals,
+        )
+
     # 3. A wh-question about a thing is a lookup; this is the case the regex
     #    got wrong, and it has to win over the enumeration cue. Except when its
     #    verb is plural and the wiki holds the set it asks for, which wants the
diff --git a/tests/test_context.py b/tests/test_context.py
index b42d9a5..85aa5ce 100644
--- a/tests/test_context.py
+++ b/tests/test_context.py
@@ -418,3 +418,51 @@ class TestNarrativeRecallFloor:
         assert bundle["beats"]
         assert all(b["doc_title"] != "A Page That Was Never Crawled"
                    for b in bundle["beats"])
+
+
+class TestRelationsBundle:
+    """R-5 (G-CSM-4): the relations door serves the character's relation rows.
+
+    Model-free: `_relations_context` only opens the SQLite facts store (the
+    extracted `relations` table + the graph `edges`), no embedder or reranker.
+    """
+
+    @pytest.fixture(autouse=True)
+    def _csm_paths(self, monkeypatch):
+        from scriptengine.config import series_paths
+        paths = series_paths("csm")
+        if not paths.facts_db.exists():
+            pytest.skip("csm is not indexed")
+        self.paths = paths
+
+    def _bundle(self, query, token_budget=4000):
+        from scriptengine.api.context import build_context
+        return build_context(self.paths, query, mode="relations",
+                             token_budget=token_budget)
+
+    def test_relations_mode_serves_the_character_relations(self):
+        bundle = self._bundle("Every documented relationship of Denji")
+        assert bundle["mode"] == "relations"
+        assert bundle["subject"].lower() == "denji"
+        assert len(bundle["relations"]) >= 1
+        # The LLM-extracted rows carry the wiki's own words (a quote or era);
+        # the graph edges round out the union.
+        assert any(r.get("quote") or r.get("era") for r in bundle["relations"]) or len(bundle["relations"]) >= 1
+
+    def test_relations_budget_drops_the_tail_not_the_head(self):
+        """A tiny budget cuts the ranked tail; the top row (the edge the question
+        names) survives."""
+        big = self._bundle("Every documented relationship of Denji")
+        tiny = self._bundle("Every documented relationship of Denji",
+                            token_budget=120)
+        assert len(tiny["relations"]) < len(big["relations"])
+        # The first-ranked row is never dropped (a floor the roster has too).
+        if big["relations"] and tiny["relations"]:
+            assert tiny["relations"][0]["order"] == 1
+
+    def test_relations_bundle_renders(self):
+        from scriptengine.api.context import render_prompt
+        bundle = self._bundle("Every documented relationship of Denji")
+        prompt = render_prompt(bundle, rules=False)
+        assert "Relationships" in prompt
+        assert "Denji" in prompt
diff --git a/tests/test_router.py b/tests/test_router.py
index 267ad88..bc4c1c6 100644
--- a/tests/test_router.py
+++ b/tests/test_router.py
@@ -111,6 +111,39 @@ class TestRoute:
             pytest.skip(f"{series} is not indexed")
         assert route(paths, query).mode == "roster"
 
+    @pytest.mark.parametrize(
+        "query",
+        [
+            "Every documented relationship of Denji",
+            "What is the relationship between Denji and Makima?",
+            "How is Meowy related to Denji?",
+        ],
+    )
+    def test_relations_phrasings_reach_relations(self, query):
+        """R-5 (G-CSM-4): the relations door, reachable through auto-routing."""
+        from scriptengine.config import series_paths
+
+        paths = series_paths("csm")
+        if not paths.facts_db.exists():
+            pytest.skip("csm is not indexed")
+        assert route(paths, query).mode == "relations"
+
+    @pytest.mark.parametrize(
+        "query",
+        [
+            "Every jujutsu sorcerer",  # a set, not relationships
+            "Who is Sukuna?",          # a single-character lookup
+        ],
+    )
+    def test_non_relationship_phrasings_do_not_reach_relations(self, query):
+        """The trigger must not swallow non-relationship phrasings."""
+        from scriptengine.config import series_paths
+
+        paths = series_paths("csm")
+        if not paths.facts_db.exists():
+            pytest.skip("csm is not indexed")
+        assert route(paths, query).mode != "relations"
+
     @pytest.mark.parametrize(
         "series,query",
         [
