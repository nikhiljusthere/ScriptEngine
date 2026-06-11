"""
Step 2: Hierarchical chunking → embed → store in Qdrant
Each small chunk carries pointer to parent section and document.
Embedding model: bge-large-en-v1.5 (best accuracy for English wiki text)
"""

import os
import re
import json
import uuid
from pathlib import Path
from typing import List, Dict

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct,
    PayloadSchemaType
)
from sentence_transformers import SentenceTransformer
import torch
from python.helper import get_scrapped_data_dir


# ── Config ────────────────────────────────────────────────────────────────────
TEXT_FILES_DIR = get_scrapped_data_dir()  / "jjk"
QDRANT_HOST      = "localhost"
QDRANT_PORT      = 6333
COLLECTION_NAME  = "wiki_chunks"
EMBED_MODEL      = "BAAI/bge-large-en-v1.5"   # 1024-dim, best for accuracy
EMBED_BATCH_SIZE = 64                           # safe for 5090 24GB
CHUNK_SIZE       = 400                          # tokens approx (words * 1.3)
CHUNK_OVERLAP    = 60

# ─────────────────────────────────────────────────────────────────────────────
# 2A. Load embedding model on GPU
# ─────────────────────────────────────────────────────────────────────────────

def load_embedder():
    model = SentenceTransformer(EMBED_MODEL, device="cuda")
    model.max_seq_length = 512
    print(f"Loaded {EMBED_MODEL} on {next(model.parameters()).device}")
    return model


# ─────────────────────────────────────────────────────────────────────────────
# 2B. Re-use parser from step 1 (copy inline to keep files independent)
# ─────────────────────────────────────────────────────────────────────────────

def parse_wiki_file(filepath: str) -> dict:
    with open(filepath, "r", encoding="utf-8") as f:
        raw = f.read()

    raw_clean = re.sub(r'\[\d+\]', '', raw)

    sections = []
    current_heading = "Overview"
    current_content = []

    for line in raw_clean.splitlines():
        line = line.strip()
        if not line:
            continue
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

    if current_content:
        sections.append({
            "heading": current_heading,
            "content": " ".join(current_content).strip()
        })

    return {
        "title": Path(filepath).stem.replace("_", " ").strip(),
        "filepath": str(filepath),
        "sections": sections,
        "raw_text": raw_clean
    }


def is_section_header(line: str) -> bool:
    known = {
        "history", "synopsis", "appearance", "personality",
        "abilities", "techniques", "relationships", "navigation",
        "references", "overview", "background", "plot"
    }
    if line.lower() in known:
        return True
    if re.match(r'^.{5,60} Arc$', line):
        return True
    return False


# ─────────────────────────────────────────────────────────────────────────────
# 2C. Hierarchical chunker
# ─────────────────────────────────────────────────────────────────────────────

def word_count(text: str) -> int:
    return len(text.split())


def split_into_sentences(text: str) -> List[str]:
    """Simple sentence splitter — accurate enough for wiki text."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def chunk_section(
    section_text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP
) -> List[str]:
    """
    Split a section into overlapping chunks.
    Uses sentences as atomic units to avoid mid-sentence cuts.
    """
    sentences = split_into_sentences(section_text)
    chunks = []
    current_words = []
    current_count = 0

    for sent in sentences:
        sent_words = sent.split()
        sent_count = len(sent_words)

        if current_count + sent_count > chunk_size and current_words:
            chunks.append(" ".join(current_words))
            # overlap: keep last N words
            overlap_words = current_words[-overlap:] if overlap else []
            current_words = overlap_words + sent_words
            current_count = len(current_words)
        else:
            current_words.extend(sent_words)
            current_count += sent_count

    if current_words:
        chunks.append(" ".join(current_words))

    return chunks


def build_hierarchical_chunks(doc_data: dict) -> List[Dict]:
    """
    Returns list of chunk dicts at 3 levels:
      level=0  →  full document summary (first 200 words)
      level=1  →  full section text
      level=2  →  paragraph-level chunks (what gets embedded for retrieval)
    """
    all_chunks = []
    doc_title = doc_data["title"]
    filepath  = doc_data["filepath"]

    # ── Level 0: document-level summary chunk ─────────────────────────────
    summary_text = doc_data["raw_text"][:1500]  # first ~1500 chars as summary
    all_chunks.append({
        "chunk_id":      str(uuid.uuid4()),
        "level":         0,
        "doc_title":     doc_title,
        "section":       "DOCUMENT_SUMMARY",
        "parent_id":     None,
        "text":          summary_text,
        "filepath":      filepath,
        "entities":      [],   # filled in step 3
    })

    doc_chunk_id = all_chunks[-1]["chunk_id"]

    for section in doc_data["sections"]:
        heading = section["heading"]
        content = section["content"]

        if not content or word_count(content) < 10:
            continue

        # ── Level 1: section-level chunk ─────────────────────────────────
        section_chunk = {
            "chunk_id":  str(uuid.uuid4()),
            "level":     1,
            "doc_title": doc_title,
            "section":   heading,
            "parent_id": doc_chunk_id,
            "text":      content,
            "filepath":  filepath,
            "entities":  [],
        }
        all_chunks.append(section_chunk)
        section_chunk_id = section_chunk["chunk_id"]

        # ── Level 2: paragraph chunks (primary retrieval units) ───────────
        if word_count(content) <= CHUNK_SIZE:
            # section is small enough — one chunk
            all_chunks.append({
                "chunk_id":  str(uuid.uuid4()),
                "level":     2,
                "doc_title": doc_title,
                "section":   heading,
                "parent_id": section_chunk_id,
                "text":      content,
                "filepath":  filepath,
                "entities":  [],
            })
        else:
            sub_chunks = chunk_section(content, CHUNK_SIZE, CHUNK_OVERLAP)
            for sub in sub_chunks:
                all_chunks.append({
                    "chunk_id":  str(uuid.uuid4()),
                    "level":     2,
                    "doc_title": doc_title,
                    "section":   heading,
                    "parent_id": section_chunk_id,
                    "text":      sub,
                    "filepath":  filepath,
                    "entities":  [],
                })

    return all_chunks


# ─────────────────────────────────────────────────────────────────────────────
# 2D. Entity tagging per chunk (lightweight — just string matching)
# ─────────────────────────────────────────────────────────────────────────────

def load_entity_list(neo4j_export_path: str = "entities.json") -> List[str]:
    """
    Load entity names exported from Neo4j.
    Run this in Neo4j to export:
      MATCH (e:Entity) RETURN e.name as name
    Save as entities.json: ["Kusakabe", "Sukuna", ...]
    """
    if not Path(neo4j_export_path).exists():
        print("Warning: entities.json not found. Skipping entity tagging.")
        return []
    with open(neo4j_export_path) as f:
        return json.load(f)


def tag_entities(chunk_text: str, entity_list: List[str]) -> List[str]:
    """Find which known entities are mentioned in this chunk."""
    found = []
    text_lower = chunk_text.lower()
    for entity in entity_list:
        if entity.lower() in text_lower:
            found.append(entity)
    return found


# ─────────────────────────────────────────────────────────────────────────────
# 2E. Qdrant setup
# ─────────────────────────────────────────────────────────────────────────────

def setup_qdrant(client: QdrantClient, vector_size: int):
    """Create collection if it doesn't exist."""
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME not in existing:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE
            )
        )
        # payload indexes for fast filtering
        client.create_payload_index(COLLECTION_NAME, "doc_title",   PayloadSchemaType.KEYWORD)
        client.create_payload_index(COLLECTION_NAME, "section",     PayloadSchemaType.KEYWORD)
        client.create_payload_index(COLLECTION_NAME, "level",       PayloadSchemaType.INTEGER)
        client.create_payload_index(COLLECTION_NAME, "entities",    PayloadSchemaType.KEYWORD)
        print(f"Created Qdrant collection '{COLLECTION_NAME}'")
    else:
        print(f"Collection '{COLLECTION_NAME}' already exists.")


# ─────────────────────────────────────────────────────────────────────────────
# 2F. Embed with BGE prefix (important for bge-large accuracy)
# ─────────────────────────────────────────────────────────────────────────────

def embed_chunks(
    chunks: List[Dict],
    model: SentenceTransformer,
    is_query: bool = False
) -> list:
    """
    BGE models require a prefix for accurate embeddings:
    - Documents: no prefix (or "Represent this sentence: ")
    - Queries:   "Represent this question for searching relevant passages: "
    """
    texts = [c["text"] for c in chunks]

    # BGE document prefix
    if not is_query:
        texts = ["Represent this passage: " + t for t in texts]

    embeddings = model.encode(
        texts,
        batch_size=EMBED_BATCH_SIZE,
        show_progress_bar=True,
        normalize_embeddings=True,   # required for cosine similarity
        convert_to_numpy=True
    )
    return embeddings


# ─────────────────────────────────────────────────────────────────────────────
# 2G. Main ingestion loop
# ─────────────────────────────────────────────────────────────────────────────

def ingest_all(files_dir: str):
    model   = load_embedder()
    client  = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    entity_list = load_entity_list("entities.json")

    # get embedding dim from a test encode
    test_vec = model.encode(["test"], normalize_embeddings=True)
    vec_dim  = test_vec.shape[1]
    setup_qdrant(client, vec_dim)

    text_files = list(Path(files_dir).rglob("*.txt"))
    print(f"Ingesting {len(text_files)} files...")

    # process in file batches to avoid OOM
    UPLOAD_BATCH = 500   # chunks per Qdrant upload call

    pending_chunks  = []
    pending_vectors = []
    total_chunks    = 0

    for i, filepath in enumerate(text_files):
        try:
            doc_data = parse_wiki_file(str(filepath))
            if not doc_data["raw_text"].strip():
                continue

            chunks = build_hierarchical_chunks(doc_data)

            # tag entities
            for chunk in chunks:
                chunk["entities"] = tag_entities(chunk["text"], entity_list)

            # only embed level-2 chunks (retrieval units)
            # level 0/1 are stored as payload for context expansion
            l2_chunks = [c for c in chunks if c["level"] == 2]

            if not l2_chunks:
                continue

            embeddings = embed_chunks(l2_chunks, model)

            for chunk, vec in zip(l2_chunks, embeddings):
                pending_chunks.append(chunk)
                pending_vectors.append(vec.tolist())

            # flush to Qdrant
            if len(pending_chunks) >= UPLOAD_BATCH:
                upload_to_qdrant(client, pending_chunks, pending_vectors)
                total_chunks += len(pending_chunks)
                pending_chunks  = []
                pending_vectors = []

            if (i + 1) % 200 == 0:
                print(f"  Files: {i+1}/{len(text_files)} | Chunks uploaded: {total_chunks}")

        except Exception as e:
            print(f"Error on {filepath}: {e}")
            continue

    # final flush
    if pending_chunks:
        upload_to_qdrant(client, pending_chunks, pending_vectors)
        total_chunks += len(pending_chunks)

    print(f"\nDone. Total chunks in Qdrant: {total_chunks}")


def upload_to_qdrant(
    client: QdrantClient,
    chunks: List[Dict],
    vectors: List[list]
):
    points = []
    for chunk, vec in zip(chunks, vectors):
        points.append(PointStruct(
            id=chunk["chunk_id"],
            vector=vec,
            payload={
                "doc_title":  chunk["doc_title"],
                "section":    chunk["section"],
                "level":      chunk["level"],
                "parent_id":  chunk["parent_id"],
                "text":       chunk["text"],
                "filepath":   chunk["filepath"],
                "entities":   chunk["entities"],
            }
        ))
    client.upsert(collection_name=COLLECTION_NAME, points=points)


if __name__ == "__main__":
    ingest_all(TEXT_FILES_DIR)
