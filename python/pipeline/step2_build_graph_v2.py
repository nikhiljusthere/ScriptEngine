"""
Step 2: Build a cleaner Neo4j graph from scraped JJK wiki text files.

What this version does differently:
- Skips obvious junk pages (_Synopsis, _Image Gallery, Blu-ray, soundtrack, lists, etc.)
- Classifies nodes by kind: Character, Arc, Battle, Technique, Location, Organization, Object, Volume, Document
- Promotes only repeated / high-value entities into the graph
- Creates explicit Arc hubs like Culling Game, Shibuya Incident, Shinjuku Showdown
- Creates Battle nodes for pages like "X vs. Y"
- Keeps Document nodes for retrieval, but avoids letting them dominate the semantic graph
"""

from __future__ import annotations

import json
import logging
import re
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import spacy
from neo4j import GraphDatabase

from helper import get_scrapped_data_dir

# -----------------------------------------------------------------------------
# Config
# -----------------------------------------------------------------------------

TEXT_FILES_DIR = get_scrapped_data_dir() / "jjk"
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password"

MIN_DOC_FREQ = 2  # raise to 3 if you want a stricter graph

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

# Try transformer model first, then fall back to small model
try:
    nlp = spacy.load("en_core_web_trf")
except Exception:
    nlp = spacy.load("en_core_web_sm")
    logger.warning("Using en_core_web_sm fallback. en_core_web_trf not found.")

# -----------------------------------------------------------------------------
# Junk filters
# -----------------------------------------------------------------------------

SKIP_FILENAME_PATTERNS = [
    "_image gallery",
    "_synopsis",
    "blu-ray",
    "original soundtrack",
    "promotional videos",
    "popularity polls",
    "list of ",
    " wiki",
    "fanbook",
    "remember",
]

SKIP_EXACT_NAMES = {
    "file_list",
    "jujutsu kaisen wiki",
    "jujutsu kaisen original soundtrack",
    "jujutsu kaisen the movie original soundtrack",
    "jujutsu kaisen hidden inventory _ premature death original soundtrack",
    "jujutsu kaisen the culling game - part 1 original soundtrack",
    "jujutsu kaisen hidden inventory _ premature death, the shibuya incident original soundtrack",
}

# Pages that are useful as semantic nodes even if they are not characters
ARC_ALIASES = {
    "culling game": "Culling Game",
    "culling game arc": "Culling Game",
    "shibuya incident": "Shibuya Incident",
    "shibuya incident arc": "Shibuya Incident",
    "hidden inventory": "Hidden Inventory",
    "premature death": "Premature Death",
    "gojo's past": "Gojo's Past",
    "gojo's past arc": "Gojo's Past",
    "shinjuku showdown": "Shinjuku Showdown",
    "shinjuku showdown arc": "Shinjuku Showdown",
    "death painting": "Death Painting",
    "death painting arc": "Death Painting",
    "fearsome womb": "Fearsome Womb",
    "fearsome womb arc": "Fearsome Womb",
    "kyoto goodwill event": "Kyoto Goodwill Event",
    "kyoto goodwill event arc": "Kyoto Goodwill Event",
    "night parade of a hundred demons": "Night Parade of a Hundred Demons",
    "night parade of a hundred demons arc": "Night Parade of a Hundred Demons",
}

RELATIONSHIP_PATTERNS = [
    (r"(.{2,80}?)\s+(?:fights?|battles?|confronts?)\s+(.{2,80})", "FIGHTS"),
    (r"(.{2,80}?)\s+(?:kills?|defeats?|slashes?|exorcises?)\s+(.{2,80})", "DEFEATS"),
    (r"(.{2,80}?)\s+(?:uses?|wields?|employs?)\s+(.{2,80})", "USES"),
    (r"(.{2,80}?)\s+(?:creates?|made|created)\s+(.{2,80})", "CREATES"),
    (r"(.{2,80}?)\s+(?:joins?|belongs to|is part of)\s+(.{2,80})", "BELONGS_TO"),
    (r"(.{2,80}?)\s+(?:appears? in|participates? in)\s+(.{2,80})", "APPEARS_IN"),
]

# -----------------------------------------------------------------------------
# Normalization / classification
# -----------------------------------------------------------------------------

def normalize_name(text: str) -> str:
    text = text.replace("_", " ")
    text = text.replace("’", "'")
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"^[\W_]+|[\W_]+$", "", text)
    return text


def canonical_key(text: str) -> str:
    return normalize_name(text).lower()


def is_junk_title(title: str) -> bool:
    t = canonical_key(title)
    if t in SKIP_EXACT_NAMES:
        return True
    return any(p in t for p in SKIP_FILENAME_PATTERNS)


def infer_kind_from_title(title: str) -> str:
    t = normalize_name(title)
    tl = t.lower()

    if is_junk_title(t):
        return "Junk"

    if re.search(r"\bvs\.?\b", t, flags=re.I):
        return "Battle"

    if tl.endswith(" arc") or tl in ARC_ALIASES:
        return "Arc"

    if tl.startswith("chapter ") or tl.startswith("modulo chapter "):
        return "Document"

    if tl.startswith("episode "):
        return "Document"

    if tl.startswith("volume ") or tl.startswith("modulo volume "):
        return "Volume"

    if "colony" in tl:
        return "Location"

    if "technique" in tl or "domain expansion" in tl or "shrine" in tl:
        return "Technique"

    if any(k in tl for k in ["clan", "college", "high", "headquarters", "association", "group", "unit"]):
        return "Organization"

    if any(k in tl for k in ["realm", "realm", "object", "tool", "weapon", "finger", "realm"]):
        return "Object"

    return "Entity"


def is_semantic_page(title: str) -> bool:
    kind = infer_kind_from_title(title)
    return kind not in {"Junk", "Document"}

# -----------------------------------------------------------------------------
# Parse wiki text files
# -----------------------------------------------------------------------------

def parse_wiki_file(filepath: str) -> dict:
    with open(filepath, "r", encoding="utf-8") as f:
        raw = f.read()

    raw_clean = re.sub(r"\[\d+\]", "", raw)

    sections = []
    current_heading = "Overview"
    current_content = []

    for line in raw_clean.splitlines():
        line = line.strip()
        if not line:
            continue

        if is_section_header(line):
            if current_content:
                sections.append(
                    {
                        "heading": current_heading,
                        "content": " ".join(current_content).strip(),
                    }
                )
            current_heading = line
            current_content = []
        else:
            current_content.append(line)

    if current_content:
        sections.append(
            {
                "heading": current_heading,
                "content": " ".join(current_content).strip(),
            }
        )

    title = Path(filepath).stem.replace("_", " ").strip()

    return {
        "title": normalize_name(title),
        "filepath": filepath,
        "sections": sections,
        "raw_text": raw_clean,
        "kind": infer_kind_from_title(title),
    }


def is_section_header(line: str) -> bool:
    known_headers = {
        "history", "synopsis", "appearance", "personality",
        "abilities", "techniques", "relationships", "navigation",
        "references", "overview", "background", "plot",
    }
    if line.lower() in known_headers:
        return True
    if re.match(r"^.{5,60} Arc$", line):
        return True
    return False

# -----------------------------------------------------------------------------
# Build title universe first so we can filter one-off junk
# -----------------------------------------------------------------------------

def gather_titles(files_dir: Path) -> List[Path]:
    return sorted(files_dir.rglob("*.txt"))


def build_title_sets(filepaths: List[Path]) -> Tuple[Set[str], Set[str]]:
    all_titles: Set[str] = set()
    semantic_titles: Set[str] = set()

    for p in filepaths:
        title = normalize_name(p.stem)
        all_titles.add(canonical_key(title))
        if is_semantic_page(title):
            semantic_titles.add(canonical_key(title))

    return all_titles, semantic_titles

# -----------------------------------------------------------------------------
# Extraction
# -----------------------------------------------------------------------------

def extract_participants_from_battle_title(title: str) -> List[str]:
    t = normalize_name(title)
    if " vs. " not in t.lower() and " vs " not in t.lower():
        return []

    parts = re.split(r"\s+vs\.?\s+", t, flags=re.I)
    participants: List[str] = []

    for part in parts:
        subparts = re.split(r"\s*&\s*|\s+and\s+|,", part, flags=re.I)
        for sp in subparts:
            s = normalize_name(sp)
            if 2 < len(s) < 80:
                participants.append(s)

    # dedupe preserving order
    seen = set()
    out = []
    for p in participants:
        ck = canonical_key(p)
        if ck not in seen:
            seen.add(ck)
            out.append(p)
    return out


def find_arcs_in_text(text: str) -> List[str]:
    arcs = []
    lower = text.lower()
    for alias, canonical in ARC_ALIASES.items():
        if alias in lower:
            arcs.append(canonical)
    # dedupe
    out = []
    seen = set()
    for arc in arcs:
        ck = canonical_key(arc)
        if ck not in seen:
            seen.add(ck)
            out.append(arc)
    return out


def should_keep_entity(name: str, doc_freq: int, known_semantic_titles: Set[str]) -> bool:
    ck = canonical_key(name)
    if ck in known_semantic_titles:
        return True
    if doc_freq >= MIN_DOC_FREQ:
        return True
    # allow obvious important-looking named entities
    if re.fullmatch(r"[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3}", name):
        return True
    return False


def spacy_type_to_kind(label: str, text: str) -> str:
    t = text.lower()
    if label == "PERSON":
        return "Character"
    if label in {"GPE", "LOC"}:
        return "Location"
    if label in {"ORG"}:
        return "Organization"
    if label in {"WORK_OF_ART", "EVENT"}:
        if "arc" in t or t in ARC_ALIASES:
            return "Arc"
        if "vs." in t or " vs " in t:
            return "Battle"
        return "Entity"
    return "Entity"


def extract_from_document(
    doc_data: dict,
    known_titles: Set[str],
    known_semantic_titles: Set[str],
) -> dict:
    entities: Dict[str, dict] = {}
    relations: List[dict] = []
    doc_title = doc_data["title"]
    doc_kind = doc_data["kind"]

    # pull text from all sections
    full_text = "\n".join(section["content"] for section in doc_data["sections"] if section["content"])
    if not full_text.strip():
        full_text = doc_data["raw_text"]

    # battle pages should contribute their participants even if spaCy misses them
    if doc_kind == "Battle":
        for p in extract_participants_from_battle_title(doc_title):
            entities[canonical_key(p)] = {"name": p, "kind": "Character", "evidence": "battle_title"}

    # explicit arc links from title or body
    arcs_found = set()
    if doc_kind == "Arc":
        arcs_found.add(doc_title)
    arcs_found.update(find_arcs_in_text(full_text))
    arcs_found.update(find_arcs_in_text(doc_title))

    for arc in arcs_found:
        ck = canonical_key(arc)
        entities[ck] = {"name": arc, "kind": "Arc", "evidence": "arc_match"}

    # NER over text
    text = full_text[:120000]
    try:
        spacy_doc = nlp(text)
    except Exception as e:
        logger.warning("spaCy failed on %s: %s", doc_title, e)
        spacy_doc = None

    if spacy_doc is not None:
        for ent in spacy_doc.ents:
            name = normalize_name(ent.text)
            if len(name) < 2 or len(name) > 80:
                continue

            ck = canonical_key(name)

            # hard reject very generic junk
            if ck in {"jujutsu kaisen", "anime", "manga", "wiki", "series", "episode", "chapter"}:
                continue

            if ck not in known_titles and ck not in known_semantic_titles:
                # keep only if it looks like a meaningful proper name
                if ent.label_ not in {"PERSON", "GPE", "LOC", "ORG", "WORK_OF_ART", "EVENT"}:
                    continue

            kind = spacy_type_to_kind(ent.label_, name)

            if ck in ARC_ALIASES:
                kind = "Arc"
                name = ARC_ALIASES[ck]

            # prefer title-based kind if we know it
            if ck in known_semantic_titles:
                kind = infer_kind_from_title(name)

            prev = entities.get(ck)
            if prev is None:
                entities[ck] = {"name": name, "kind": kind, "evidence": f"ner:{ent.label_}"}
            else:
                # keep the more specific kind when possible
                if prev["kind"] == "Entity" and kind != "Entity":
                    prev["kind"] = kind

    # relation patterns
    for section in doc_data["sections"]:
        sec_text = section["content"]
        if not sec_text:
            continue

        for pattern, rel_label in RELATIONSHIP_PATTERNS:
            for m in re.finditer(pattern, sec_text, flags=re.I):
                src = normalize_name(m.group(1))
                tgt = normalize_name(m.group(2))

                if len(src) < 2 or len(tgt) < 2:
                    continue

                relations.append(
                    {
                        "source": src,
                        "target": tgt,
                        "relation": rel_label,
                        "section": section["heading"],
                        "in_document": doc_title,
                    }
                )

    # attach doc-level arc info
    for arc in arcs_found:
        relations.append(
            {
                "source": doc_title,
                "target": arc,
                "relation": "ABOUT_ARC",
                "section": "Document",
                "in_document": doc_title,
            }
        )

    # battle page -> participants
    if doc_kind == "Battle":
        participants = extract_participants_from_battle_title(doc_title)
        for p in participants:
            relations.append(
                {
                    "source": doc_title,
                    "target": p,
                    "relation": "INVOLVES",
                    "section": "Title",
                    "in_document": doc_title,
                }
            )

    return {
        "title": doc_title,
        "kind": doc_kind,
        "filepath": doc_data["filepath"],
        "raw_text": doc_data["raw_text"],
        "entities": list(entities.values()),
        "relations": relations,
        "arcs_found": list(arcs_found),
    }

# -----------------------------------------------------------------------------
# Neo4j writer
# -----------------------------------------------------------------------------

KIND_TO_LABEL = {
    "Character": "Character",
    "Arc": "Arc",
    "Battle": "Battle",
    "Technique": "Technique",
    "Location": "Location",
    "Organization": "Organization",
    "Object": "Object",
    "Volume": "Volume",
    "Entity": "Entity",
    "Document": "Document",
}

RELATION_WHITELIST = {
    "FIGHTS",
    "DEFEATS",
    "USES",
    "CREATES",
    "BELONGS_TO",
    "APPEARS_IN",
    "ABOUT_ARC",
    "INVOLVES",
    "MENTIONED_IN",
    "RELATES_TO",
}


class GraphBuilder:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)
        )

    def close(self):
        self.driver.close()

    def create_indexes(self):
        with self.driver.session() as session:
            session.run(
                "CREATE CONSTRAINT entity_name IF NOT EXISTS "
                "FOR (e:Entity) REQUIRE e.name IS UNIQUE"
            )
            session.run(
                "CREATE CONSTRAINT document_title IF NOT EXISTS "
                "FOR (d:Document) REQUIRE d.title IS UNIQUE"
            )
            session.run(
                "CREATE CONSTRAINT arc_name IF NOT EXISTS "
                "FOR (a:Arc) REQUIRE a.name IS UNIQUE"
            )
            session.run(
                "CREATE CONSTRAINT battle_name IF NOT EXISTS "
                "FOR (b:Battle) REQUIRE b.name IS UNIQUE"
            )
        print("Indexes/constraints created.")

    def clear_graph(self):
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        print("Graph cleared.")

    def upsert_document(self, doc_data: dict):
        with self.driver.session() as session:
            session.run(
                """
                MERGE (d:Document {title: $title})
                SET d.filepath = $filepath,
                    d.kind = $kind,
                    d.raw_text = $raw_text,
                    d.updated_at = datetime()
                """,
                title=doc_data["title"],
                filepath=doc_data["filepath"],
                kind=doc_data["kind"],
                raw_text=doc_data["raw_text"][:8000],
            )

    def upsert_semantic_node(self, name: str, kind: str, doc_freq: int):
        label = KIND_TO_LABEL.get(kind, "Entity")
        with self.driver.session() as session:
            session.run(
                f"""
                MERGE (n:Entity:{label} {{name: $name}})
                SET n.kind = $kind,
                    n.doc_freq = $doc_freq,
                    n.updated_at = datetime()
                """,
                name=name,
                kind=kind,
                doc_freq=doc_freq,
            )

    def upsert_relation(
        self,
        src: str,
        tgt: str,
        rel: str,
        props: Optional[dict] = None,
        src_kind: str = "Entity",
        tgt_kind: str = "Entity",
    ):
        rel = rel.upper().strip()
        if rel not in RELATION_WHITELIST:
            rel = "RELATES_TO"

        src_label = KIND_TO_LABEL.get(src_kind, "Entity")
        tgt_label = KIND_TO_LABEL.get(tgt_kind, "Entity")

        props = props or {}
        with self.driver.session() as session:
            session.run(
                f"""
                MERGE (a:Entity:{src_label} {{name: $src}})
                MERGE (b:Entity:{tgt_label} {{name: $tgt}})
                MERGE (a)-[r:{rel}]->(b)
                ON CREATE SET r.weight = 1
                ON MATCH SET r.weight = coalesce(r.weight, 0) + 1
                SET r += $props
                """,
                src=src,
                tgt=tgt,
                props=props,
            )

    def link_entity_to_document(self, entity_name: str, doc_title: str, rel: str = "MENTIONED_IN"):
        rel = rel.upper().strip()
        if rel not in RELATION_WHITELIST:
            rel = "MENTIONED_IN"

        with self.driver.session() as session:
            session.run(
                f"""
                MERGE (e:Entity {{name: $entity_name}})
                MERGE (d:Document {{title: $doc_title}})
                MERGE (e)-[r:{rel}]->(d)
                ON CREATE SET r.weight = 1
                ON MATCH SET r.weight = coalesce(r.weight, 0) + 1
                """,
                entity_name=entity_name,
                doc_title=doc_title,
            )

# -----------------------------------------------------------------------------
# Main build
# -----------------------------------------------------------------------------

def build_graph(files_dir: Path, clear_existing: bool = False):
    filepaths = gather_titles(files_dir)
    known_titles, known_semantic_titles = build_title_sets(filepaths)

    logger.info("Found %d txt files", len(filepaths))
    logger.info("Semantic title candidates: %d", len(known_semantic_titles))

    # First pass: parse and extract candidates
    parsed_docs = []
    entity_doc_counter: Counter[str] = Counter()
    entity_kind_hint: Dict[str, str] = {}

    failed = []
    skipped = 0

    for filepath in filepaths:
        try:
            doc_data = parse_wiki_file(str(filepath))

            if is_junk_title(doc_data["title"]):
                skipped += 1
                continue

            if not doc_data["raw_text"].strip():
                skipped += 1
                continue

            extracted = extract_from_document(
                doc_data,
                known_titles=known_titles,
                known_semantic_titles=known_semantic_titles,
            )

            parsed_docs.append(extracted)

            seen_in_this_doc = set()
            for ent in extracted["entities"]:
                name = normalize_name(ent["name"])
                ck = canonical_key(name)

                if ck in seen_in_this_doc:
                    continue
                seen_in_this_doc.add(ck)

                entity_doc_counter[ck] += 1
                entity_kind_hint.setdefault(ck, ent.get("kind", "Entity"))

        except Exception as e:
            failed.append((str(filepath), str(e)))

    logger.info("Parsed docs: %d", len(parsed_docs))
    logger.info("Skipped junk/empty docs: %d", skipped)
    logger.info("Failed docs: %d", len(failed))

    # Decide which entities to keep
    keep_entities: Set[str] = set()
    for ck, freq in entity_doc_counter.items():
        kind = entity_kind_hint.get(ck, "Entity")
        if freq >= MIN_DOC_FREQ:
            keep_entities.add(ck)
        elif kind in {"Arc", "Battle", "Character", "Technique", "Location", "Organization", "Object", "Volume"}:
            keep_entities.add(ck)
        elif ck in known_semantic_titles:
            keep_entities.add(ck)

    logger.info("Keeping %d semantic entities", len(keep_entities))

    graph = GraphBuilder()
    graph.create_indexes()
    if clear_existing:
        graph.clear_graph()

    try:
        # Create document nodes first
        for doc in parsed_docs:
            graph.upsert_document(doc)

        # Second pass: write only promoted entities and cleaner relations
        for i, doc in enumerate(parsed_docs, start=1):
            doc_title = doc["title"]
            doc_kind = doc["kind"]

            # keep an arc mapping for this document
            doc_arcs = [a for a in doc.get("arcs_found", [])]

            # write semantic entities
            for ent in doc["entities"]:
                name = normalize_name(ent["name"])
                ck = canonical_key(name)
                kind = ent.get("kind", "Entity")

                if ck not in keep_entities:
                    continue

                graph.upsert_semantic_node(
                    name=name,
                    kind=kind,
                    doc_freq=entity_doc_counter.get(ck, 1),
                )
                graph.link_entity_to_document(name, doc_title, rel="MENTIONED_IN")

            # write relationships, but only if endpoints are kept or meaningful
            for rel in doc["relations"]:
                src = normalize_name(rel["source"])
                tgt = normalize_name(rel["target"])
                src_ck = canonical_key(src)
                tgt_ck = canonical_key(tgt)

                # allow document/arc/battle relationships even if one side is not yet promoted
                src_kind = entity_kind_hint.get(src_ck, infer_kind_from_title(src))
                tgt_kind = entity_kind_hint.get(tgt_ck, infer_kind_from_title(tgt))

                if src_kind == "Junk" or tgt_kind == "Junk":
                    continue

                # Keep relation if at least one endpoint is a promoted semantic node,
                # or if it is a doc->arc / battle->participant edge
                rel_type = rel["relation"].upper().strip()
                if rel_type not in RELATION_WHITELIST:
                    rel_type = "RELATES_TO"

                should_keep = (
                    src_ck in keep_entities
                    or tgt_ck in keep_entities
                    or rel_type in {"ABOUT_ARC", "INVOLVES"}
                    or src_kind == "Document"
                    or tgt_kind == "Document"
                )

                if not should_keep:
                    continue

                graph.upsert_relation(
                    src=src,
                    tgt=tgt,
                    rel=rel_type,
                    props={
                        "section": rel.get("section", ""),
                        "source_doc": rel.get("in_document", ""),
                    },
                    src_kind=src_kind,
                    tgt_kind=tgt_kind,
                )

                # Extra hub: connect all semantic entities found in a doc to the arc of that doc
                if doc_arcs and src_ck in keep_entities and tgt_ck in keep_entities:
                    for arc in doc_arcs:
                        graph.upsert_relation(
                            src=src,
                            tgt=arc,
                            rel="APPEARS_IN",
                            props={"source_doc": doc_title},
                            src_kind=src_kind,
                            tgt_kind="Arc",
                        )

            if i % 100 == 0:
                logger.info("Processed %d/%d docs", i, len(parsed_docs))

    finally:
        graph.close()

    if failed:
        with open("failed_files.json", "w", encoding="utf-8") as f:
            json.dump(failed, f, indent=2, ensure_ascii=False)
        logger.warning("Failed on %d files. See failed_files.json", len(failed))

    logger.info("Graph build complete.")


if __name__ == "__main__":
    build_graph(TEXT_FILES_DIR, clear_existing=False)