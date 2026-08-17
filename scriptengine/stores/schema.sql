-- ScriptEngine fact store.
--
-- One file per series holds the documents, the graph, the facts and the
-- full-text index. This replaces a Neo4j container plus an in-memory BM25 index
-- that was rebuilt from a full vector-store scroll on every process start.
--
-- Node labels are values in a column, never table names. Every series brings
-- different entity types. Jujutsu Kaisen has `technique` and `story_arcs`,
-- another wiki will have neither, so a new series must never require a schema
-- migration. This is the reason SQLite was chosen over an embedded graph engine
-- that wants a table per label.

PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

-- ── Documents ───────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS documents (
    id                INTEGER PRIMARY KEY,
    title             TEXT NOT NULL UNIQUE,
    url               TEXT,
    page_type         TEXT NOT NULL DEFAULT 'unknown',
    infobox_template  TEXT,
    lead              TEXT,
    word_count        INTEGER NOT NULL DEFAULT 0,
    revid             INTEGER,
    fetched_at        TEXT
);

CREATE INDEX IF NOT EXISTS idx_documents_type ON documents(page_type);

-- Sections keep `ordinal`, their position in the page. Narrative retrieval
-- depends on it: a script needs an arc in the order it happened, which is the
-- order the page tells it, not the order a similarity score returns.
CREATE TABLE IF NOT EXISTS sections (
    id            INTEGER PRIMARY KEY,
    document_id   INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    title         TEXT NOT NULL,
    breadcrumb    TEXT NOT NULL,
    level         INTEGER NOT NULL DEFAULT 2,
    ordinal       INTEGER NOT NULL DEFAULT 0,
    text          TEXT,
    word_count    INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_sections_document ON sections(document_id, ordinal);

-- Category membership, as the wiki publishes it. A category is a set an editor
-- assembled by hand ("Cursed Spirits", "Domain Expansions", "Curse Users")
-- which is what an enumeration script ("Every X") needs and what prose
-- retrieval cannot produce: ranking eight similar passages never yields a
-- complete set. Crawled all along on `WikiPage.categories`, never indexed.
CREATE TABLE IF NOT EXISTS categories (
    document_id  INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    category     TEXT NOT NULL,
    PRIMARY KEY (document_id, category)
);

CREATE INDEX IF NOT EXISTS idx_categories_name ON categories(category);

-- ── Graph ───────────────────────────────────────────────────────────────────

-- A node may exist without a document behind it: a page can link somewhere that
-- was never crawled. `is_resolved` records the difference so retrieval can
-- prefer entities it can actually say something about.
CREATE TABLE IF NOT EXISTS nodes (
    id           INTEGER PRIMARY KEY,
    name         TEXT NOT NULL UNIQUE,
    label        TEXT NOT NULL DEFAULT 'unknown',
    document_id  INTEGER REFERENCES documents(id) ON DELETE SET NULL,
    is_resolved  INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_nodes_label ON nodes(label);

-- Alias lookup is how a query mentioning "Todo" reaches the page "Aoi Todo".
-- Matching is done on whole words by the caller; storing aliases folded to
-- lower case keeps the lookup itself a plain index hit.
CREATE TABLE IF NOT EXISTS aliases (
    alias     TEXT NOT NULL,
    node_id   INTEGER NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
    PRIMARY KEY (alias, node_id)
);

CREATE INDEX IF NOT EXISTS idx_aliases_node ON aliases(node_id);

-- `confidence` separates an editor stating a fact in an infobox from a link
-- that merely appears in prose. Both are useful; conflating them is not.
CREATE TABLE IF NOT EXISTS edges (
    id          INTEGER PRIMARY KEY,
    source_id   INTEGER NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
    relation    TEXT NOT NULL,
    target_id   INTEGER NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
    confidence  REAL NOT NULL DEFAULT 1.0,
    provenance  TEXT,
    section     TEXT,
    UNIQUE (source_id, relation, target_id, section)
);

CREATE INDEX IF NOT EXISTS idx_edges_source ON edges(source_id, confidence);
CREATE INDEX IF NOT EXISTS idx_edges_target ON edges(target_id, confidence);

-- Infobox parameters, stored as data rather than flattened into prose. This is
-- what makes an entity lookup exact instead of retrieved-and-hoped-for.
CREATE TABLE IF NOT EXISTS facts (
    id         INTEGER PRIMARY KEY,
    node_id    INTEGER NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
    key        TEXT NOT NULL,
    label      TEXT,
    value      TEXT NOT NULL,
    citation   TEXT
);

CREATE INDEX IF NOT EXISTS idx_facts_node ON facts(node_id);
CREATE INDEX IF NOT EXISTS idx_facts_key ON facts(key);

-- ── Chunks ──────────────────────────────────────────────────────────────────

-- Three levels, as before, but built from the API's section tree rather than
-- guessed at:
--   0  a document card: title, type, infobox facts and lead, rendered compactly
--   1  a whole section, kept as the parent used to expand context
--   2  a passage, the primary retrieval unit
CREATE TABLE IF NOT EXISTS chunks (
    id           INTEGER PRIMARY KEY,
    document_id  INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    section_id   INTEGER REFERENCES sections(id) ON DELETE CASCADE,
    parent_id    INTEGER REFERENCES chunks(id) ON DELETE CASCADE,
    level        INTEGER NOT NULL,
    ordinal      INTEGER NOT NULL DEFAULT 0,
    doc_title    TEXT NOT NULL,
    breadcrumb   TEXT NOT NULL DEFAULT '',
    text         TEXT NOT NULL,
    word_count   INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_chunks_level ON chunks(level);
CREATE INDEX IF NOT EXISTS idx_chunks_document ON chunks(document_id, ordinal);
CREATE INDEX IF NOT EXISTS idx_chunks_parent ON chunks(parent_id);

-- Which entities a chunk mentions, for filtering retrieval by entity.
CREATE TABLE IF NOT EXISTS chunk_nodes (
    chunk_id  INTEGER NOT NULL REFERENCES chunks(id) ON DELETE CASCADE,
    node_id   INTEGER NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
    PRIMARY KEY (chunk_id, node_id)
);

CREATE INDEX IF NOT EXISTS idx_chunk_nodes_node ON chunk_nodes(node_id);

-- BM25 over the chunk text, on disk, maintained as an external-content index
-- against `chunks`. Lexical matching is not optional here: character and
-- technique names are exactly where dense retrieval is weakest.
CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
    text,
    breadcrumb,
    doc_title,
    content = 'chunks',
    content_rowid = 'id',
    -- Diacritic folding matters on an anime wiki, where "Tōdō" and "Todo" are
    -- the same name. Stemming is safe alongside it: proper nouns pass through
    -- unchanged, and the cross-encoder rerank downstream repairs any precision
    -- the looser matching costs.
    tokenize = "porter unicode61 remove_diacritics 2"
);

-- ── Metadata ────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS meta (
    key    TEXT PRIMARY KEY,
    value  TEXT
);

-- ── Semantic classification ─────────────────────────────────────────────────
--
-- What a page *is*, where the wiki's own fields cannot say. `Class =
-- Transformation` plus a `Saiyans` category describes Spirit Bomb Super Saiyan
-- and Great Ape identically, and only one of them is a form a Saiyan body
-- reaches. Separating them needs "stacked on another form" or "caused from
-- outside", which no wiki records. A local model decides that once, at index
-- time, and the answer is stored here so retrieval stays deterministic.
--
-- Deliberately **not** dropped by `FactStore.reset()`. Everything else in this
-- file is derived from the crawl and cheap to rebuild; this costs minutes of
-- local inference per wiki, and it is keyed on `revid`, so it stays valid until
-- the page itself changes.
CREATE TABLE IF NOT EXISTS semantics (
    title           TEXT PRIMARY KEY,
    revid           INTEGER,          -- what the classification was made from
    prompt_version  TEXT,             -- bump to invalidate every row
    semantic_type   TEXT,             -- the vocabulary in retrieve/semantics.py
    properties      TEXT,             -- JSON: race_exclusive, teachable, …
    reason          TEXT,             -- one line, so a bad call can be argued with
    model           TEXT,
    classified_at   TEXT
);

CREATE INDEX IF NOT EXISTS idx_semantics_type ON semantics(semantic_type);

-- What each page *names*, as against what it mentions.
--
-- A wiki bolds a thing it is naming and leaves a passing reference in plain
-- prose, and that distinction is the one an enumeration needs. Measured on
-- Sukuna's page: every real technique it lists is a bolded wikilink or a
-- bolded `{{Nihongo}}` argument, and none of the six names that were arriving
-- as his cursed techniques -- `Metamorphosis`, `Enchain`, `Totality`,
-- `Cursed Energy Reinforcement` among them -- is either.
--
-- Stored rather than derived on demand because `strip_markup` removes the
-- emphasis along with the rest of the markup, so a chunk cannot be asked. Also
-- not the same signal as "has a page of its own": `Cursed Technique Lapse -
-- Maximum Cursed Energy Output: Blue` has no page anywhere on the wiki and is
-- named in bold on Gojo's.
--
-- Rebuilt by `index` with the rest of the derived tables; it holds no
-- inference and costs nothing to recompute.
CREATE TABLE IF NOT EXISTS emphasis (
    document_id     INTEGER NOT NULL,
    name            TEXT    NOT NULL,
    PRIMARY KEY (document_id, name)
);

CREATE INDEX IF NOT EXISTS idx_emphasis_name ON emphasis(name COLLATE NOCASE);
