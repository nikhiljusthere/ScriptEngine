"""
Step 1: Parse wiki text files → extract entities/relationships → build Neo4j graph
Focus: accuracy over speed
"""

import os
import re
import json
from pathlib import Path
from neo4j import GraphDatabase
from sentence_transformers import SentenceTransformer
import spacy
from helper import get_scrapped_data_dir

# ── Config ────────────────────────────────────────────────────────────────────
TEXT_FILES_DIR = get_scrapped_data_dir() / "jjk"

print("Selected Scrapped data folder :", TEXT_FILES_DIR)

NEO4J_URI      = "bolt://localhost:7687"
NEO4J_USER     = "neo4j"
NEO4J_PASSWORD = "password"

# ── Load spaCy for NER (used to extract entities from text) ───────────────────
# python -m spacy download en_core_web_trf  (transformer-based, most accurate)
nlp = spacy.load("en_core_web_trf")


# ─────────────────────────────────────────────────────────────────────────────
# 1A. Parse a single wiki text file into structured sections
# ─────────────────────────────────────────────────────────────────────────────

def parse_wiki_file(filepath: str) -> dict:
    """
    Parses a wiki text file into:
    {
        "title": str,
        "sections": [{"heading": str, "content": str}],
        "raw_text": str
    }
    """
    with open(filepath, "r", encoding="utf-8") as f:
        raw = f.read()

    # clean reference markers like [1], [2] etc
    raw_clean = re.sub(r'\[\d+\]', '', raw)

    # split into sections by headings
    # headings are lines that appear before content blocks
    sections = []
    current_heading = "Overview"
    current_content = []

    for line in raw_clean.splitlines():
        line = line.strip()
        if not line:
            continue

        # detect section headers (all caps, or known wiki section names)
        if is_section_header(line):
            if current_content:
                sections.append({
                    "heading": current_heading,
                    "content": " ".join(current_content).strip()
                })
            current_heading = line
            current_content = []
        else:
            current_content.append(line)

    # flush last section
    if current_content:
        sections.append({
            "heading": current_heading,
            "content": " ".join(current_content).strip()
        })

    # derive title from filename
    title = Path(filepath).stem.replace("_", " ").strip()

    return {
        "title": title,
        "filepath": filepath,
        "sections": sections,
        "raw_text": raw_clean
    }


def is_section_header(line: str) -> bool:
    """Detect if a line is a section header."""
    known_headers = {
        "history", "synopsis", "appearance", "personality",
        "abilities", "techniques", "relationships", "navigation",
        "references", "overview", "background", "plot"
    }
    # short lines that match known headers
    if line.lower() in known_headers:
        return True
    # arc names like "Shibuya Incident Arc", "Culling Game Arc"
    if re.match(r'^.{5,60} Arc$', line):
        return True
    return False


# ─────────────────────────────────────────────────────────────────────────────
# 1B. Extract entities and relationships from parsed file
# ─────────────────────────────────────────────────────────────────────────────

# Known relationship patterns; expand this list for your wiki
RELATIONSHIP_PATTERNS = [
    # (regex pattern, relationship label)
    (r'(\w[\w\s]+)\s+uses?\s+([\w\s:]+(?:technique|domain|style|slash|moon|palm|output))',
     "USES_TECHNIQUE"),
    (r'(\w[\w\s]+)\s+is\s+(?:a\s+)?(?:student|teacher|mentor)\s+of\s+([\w\s]+)',
     "STUDENT_OF"),
    (r'(\w[\w\s]+)\s+(?:fights?|battles?|confronts?)\s+([\w\s]+)',
     "FIGHTS"),
    (r'(\w[\w\s]+)\s+(?:kills?|defeats?|slashes?)\s+([\w\s]+)',
     "DEFEATS"),
    (r'(\w[\w\s]+)\s+(?:saves?|rescues?|protects?)\s+([\w\s]+)',
     "SAVES"),
    (r'(\w[\w\s]+)\s+is\s+(?:the\s+)?head\s+of\s+([\w\s]+)',
     "HEAD_OF"),
    (r'(\w[\w\s]+)\s+(?:participates?\s+in|appears?\s+in)\s+([\w\s]+\s+Arc)',
     "APPEARS_IN"),
]


def extract_entities(doc_data: dict) -> dict:
    """
    Extract:
    - Named entities (characters, techniques, locations, arcs)
    - Relationships between entities
    """
    entities = set()
    relationships = []

    for section in doc_data["sections"]:
        text = section["content"]
        if not text:
            continue

        # spaCy NER for named entities
        spacy_doc = nlp(text[:100000])  # spaCy limit guard
        for ent in spacy_doc.ents:
            if ent.label_ in ("PERSON", "ORG", "GPE", "WORK_OF_ART", "EVENT"):
                entities.add(ent.text.strip())

        # pattern-based relationship extraction
        text_lower = text
        for pattern, rel_label in RELATIONSHIP_PATTERNS:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                src = match[0].strip()
                tgt = match[1].strip()
                # filter noise: must be reasonable length
                if 2 < len(src) < 60 and 2 < len(tgt) < 60:
                    relationships.append({
                        "source": src,
                        "target": tgt,
                        "relation": rel_label,
                        "section": section["heading"],
                        "in_document": doc_data["title"]
                    })

    # always add the document title itself as a primary entity
    entities.add(doc_data["title"])

    return {
        "primary_entity": doc_data["title"],
        "entities": list(entities),
        "relationships": relationships
    }


# ─────────────────────────────────────────────────────────────────────────────
# 1C. Write everything to Neo4j
# ─────────────────────────────────────────────────────────────────────────────

class GraphBuilder:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)
        )

    def close(self):
        self.driver.close()

    def create_indexes(self):
        """Run once; creates indexes for fast lookup."""
        with self.driver.session() as session:
            session.run("CREATE INDEX entity_name IF NOT EXISTS FOR (e:Entity) ON (e.name)")
            session.run("CREATE INDEX doc_title IF NOT EXISTS FOR (d:Document) ON (d.title)")
        print("Indexes created.")

    def upsert_document(self, doc_data: dict):
        """Create or update a Document node."""
        with self.driver.session() as session:
            session.run("""
                MERGE (d:Document {title: $title})
                SET d.filepath = $filepath,
                    d.raw_text = $raw_text
            """, title=doc_data["title"],
                 filepath=doc_data["filepath"],
                 raw_text=doc_data["raw_text"][:5000])  # store preview only

    def upsert_entity(self, name: str, entity_type: str = "Unknown"):
        """Create or update an Entity node."""
        with self.driver.session() as session:
            session.run("""
                MERGE (e:Entity {name: $name})
                SET e.type = $entity_type
            """, name=name, entity_type=entity_type)

    def upsert_relationship(self, src: str, tgt: str, rel: str, props: dict = {}):
        """Create a relationship between two Entity nodes."""
        with self.driver.session() as session:
            session.run(f"""
                MERGE (a:Entity {{name: $src}})
                MERGE (b:Entity {{name: $tgt}})
                MERGE (a)-[r:{rel}]->(b)
                SET r += $props
            """, src=src, tgt=tgt, props=props)

    def link_entity_to_document(self, entity_name: str, doc_title: str):
        """Link an entity to the document it appears in."""
        with self.driver.session() as session:
            session.run("""
                MERGE (e:Entity {name: $entity_name})
                MERGE (d:Document {title: $doc_title})
                MERGE (e)-[:MENTIONED_IN]->(d)
            """, entity_name=entity_name, doc_title=doc_title)


# ─────────────────────────────────────────────────────────────────────────────
# 1D. Main ingestion loop
# ─────────────────────────────────────────────────────────────────────────────

def build_graph(files_dir: str):
    graph = GraphBuilder()
    graph.create_indexes()

    text_files = list(Path(files_dir).rglob("*.txt"))
    print(f"Found {len(text_files)} files. Building graph...")

    failed = []

    for i, filepath in enumerate(text_files):
        try:
            # parse
            doc_data = parse_wiki_file(str(filepath))

            # skip empty files
            if not doc_data["raw_text"].strip():
                continue

            # write document node
            graph.upsert_document(doc_data)

            # extract entities + relationships
            extracted = extract_entities(doc_data)

            # write entity nodes
            for entity in extracted["entities"]:
                graph.upsert_entity(entity)
                graph.link_entity_to_document(entity, doc_data["title"])

            # write relationships
            for rel in extracted["relationships"]:
                graph.upsert_relationship(
                    src=rel["source"],
                    tgt=rel["target"],
                    rel=rel["relation"],
                    props={"section": rel["section"], "source_doc": rel["in_document"]}
                )

            if (i + 1) % 100 == 0:
                print(f"  Processed {i+1}/{len(text_files)}")

        except Exception as e:
            failed.append((str(filepath), str(e)))
            continue

    graph.close()

    # save failed files for inspection
    if failed:
        with open("failed_files.json", "w") as f:
            json.dump(failed, f, indent=2)
        print(f"Failed on {len(failed)} files. See failed_files.json")

    print("Graph build complete.")


if __name__ == "__main__":
    build_graph(TEXT_FILES_DIR)
