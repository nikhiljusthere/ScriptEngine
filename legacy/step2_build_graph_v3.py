"""
Step 2 (robust): Build a cleaner Neo4j graph from scraped JJK wiki text files.

Goals:
- Skip junk pages and gallery/synopsis/noise pages
- Classify files by page type before extraction
- Use filename/title patterns + section headers + lightweight NLP
- Promote only meaningful entities into typed nodes
- Create explicit semantic relationships instead of only MENTIONED_IN
- Keep document nodes for traceability, but don't let them dominate the graph

Recommended usage:
    python -m pipeline.step2_build_graph_v3

Optional:
    set CLEAR_EXISTING = True for a clean rebuild

Fixes v4:
- Multi-label MERGE conflict fixed (MERGE on :Entity only, then SET label)
- Label pollution fixed: NER label only applied if title-kind is not already
  a more-specific non-Entity kind (prevents Tokyo→Character, etc.)
- Canonical alias map resolves first-name / full-name duplicates before write
- Possessive / fragment garbage filter added to normalize_name
- Entity+Document double-label fixed: Document nodes never promoted as Entity
- upsert_node uses a single label (most specific wins), never stacks labels
"""

from __future__ import annotations

import json
import logging
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set

from neo4j import GraphDatabase
from helper import get_scrapped_data_dir

# -----------------------------------------------------------------------------
# Config
# -----------------------------------------------------------------------------

TEXT_FILES_DIR = Path(
    r"E:\VS CODE\Midnight Render\Softwares\RAG\out\step_one_raw_scrapped_data\jjk"
)

NEO4J_URI      = "bolt://localhost:7687"
NEO4J_USER     = "neo4j"
NEO4J_PASSWORD = "password"

CLEAR_EXISTING    = True            # always wipe previous graph on startup
MIN_DOC_FREQ      = 2               # raise to 3 for stricter graphs
MAX_TEXT_FOR_NLP  = 120_000         # safety cap for huge pages
SPACY_MODEL       = "en_core_web_trf"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Optional spaCy
# -----------------------------------------------------------------------------

try:
    import spacy

    try:
        nlp = spacy.load(SPACY_MODEL)
        logger.info("Loaded spaCy model: %s", SPACY_MODEL)
    except Exception:
        nlp = spacy.load("en_core_web_sm")
        logger.warning("Falling back to en_core_web_sm")
except Exception as e:
    nlp = None
    logger.warning("spaCy unavailable; using regex/title logic only: %s", e)

# -----------------------------------------------------------------------------
# Page type heuristics
# -----------------------------------------------------------------------------


SKIP_PATTERNS = [
    "_image gallery", "_synopsis", "blu-ray", "original soundtrack",
    "soundtrack", "promotional videos", "popularity polls", "list of ",
    "story arcs", "volumes & chapters", "modulo", "wiki",
    "fanbook", "remember",
]

SKIP_EXACT = {
    "file_list", "jujutsu kaisen wiki", "rememeber",
    "list of characters", "list of episodes", "list of battles & events",
    "story arcs", "volumes & chapters",
    "ao no sumika", "kaikai kitan", "lost in paradise", "specialz",
    "vivid vice", "give it back", "more than words", "yoake no uta",
    "ichizu", "climax☆jumping!", "boost on", "frost calm",
    "stand in the darkness", "prayer song", "cutie honey",
    "jujutsu kaisen modulo",
}

ARC_ALIASES: Dict[str, str] = {
    "culling game":                        "Culling Game",
    "culling game arc":                    "Culling Game",
    "shibuya incident":                    "Shibuya Incident",
    "shibuya incident arc":                "Shibuya Incident",
    "the shibuya incident":                "Shibuya Incident",
    "shinjuku showdown":                   "Shinjuku Showdown",
    "shinjuku showdown arc":               "Shinjuku Showdown",
    "gojo's past":                         "Gojo's Past",
    "gojo's past arc":                     "Gojo's Past",
    "hidden inventory":                    "Hidden Inventory",
    "premature death":                     "Premature Death",
    "fearsome womb":                       "Fearsome Womb",
    "fearsome womb arc":                   "Fearsome Womb",
    "death painting":                      "Death Painting",
    "death painting arc":                  "Death Painting",
    "kyoto goodwill event":                "Kyoto Goodwill Event",
    "kyoto goodwill event arc":            "Kyoto Goodwill Event",
    "night parade of a hundred demons":    "Night Parade of a Hundred Demons",
}

# ---------------------------------------------------------------------------
# Canonical character alias map  (first-name / partial → full canonical name)
# Any name whose key matches a value here will be redirected before writing.
# ---------------------------------------------------------------------------

CHARACTER_ALIASES: Dict[str, str] = {
    "yuji":             "Yuji Itadori",
    "itadori":          "Yuji Itadori",
    "megumi":           "Megumi Fushiguro",
    "fushiguro":        "Megumi Fushiguro",
    "gojo":             "Satoru Gojo",
    "satoru":           "Satoru Gojo",
    "gojo sensei":      "Satoru Gojo",
    "nobara":           "Nobara Kugisaki",
    "kugisaki":         "Nobara Kugisaki",
    "yuta":             "Yuta Okkotsu",
    "okkotsu":          "Yuta Okkotsu",
    "maki":             "Maki Zenin",
    "zenin maki":       "Maki Zenin",
    "toge":             "Toge Inumaki",
    "inumaki":          "Toge Inumaki",
    "panda":            "Panda",
    "nanami":           "Kento Nanami",
    "kento":            "Kento Nanami",
    "todo":             "Aoi Todo",
    "aoi":              "Aoi Todo",
    "choso":            "Choso",
    "kenjaku":          "Kenjaku",
    "pseudo geto":      "Kenjaku",
    "pseudo-geto":      "Kenjaku",
    "geto":             "Suguru Geto",
    "suguru":           "Suguru Geto",
    "mahito":           "Mahito",
    "sukuna":           "Ryomen Sukuna",
    "ryomen":           "Ryomen Sukuna",
    "ryomen sukuna":    "Ryomen Sukuna",
    "king of curses":   "Ryomen Sukuna",
    "the king of curses": "Ryomen Sukuna",
    "hakari":           "Kinji Hakari",
    "kashimo":          "Hajime Kashimo",
    "yuki":             "Yuki Tsukumo",
    "tsukumo":          "Yuki Tsukumo",
    "ijichi":           "Kiyotaka Ijichi",
    "shoko":            "Shoko Ieiri",
    "ieiri":            "Shoko Ieiri",
    "mei mei":          "Mei Mei",
    "utahime":          "Utahime Iori",
    "iori":             "Utahime Iori",
    "uraume":           "Uraume",
    "higuruma":         "Hiromi Higuruma",
    "kusakabe":         "Atsuya Kusakabe",
    "noritoshi":        "Noritoshi Kamo",
    "kamo":             "Noritoshi Kamo",
    "toji":             "Toji Fushiguro",
    "toji zenin":       "Toji Fushiguro",
    "naoya":            "Naoya Zenin",
    "junpei":           "Junpei Yoshino",
    "reggie":           "Reggie Star",
    "mechamaru":        "Kokichi Muta",
    "gakuganji":        "Yoshinobu Gakuganji",
    "yaga":             "Masamichi Yaga",
    "sorcerer killer":  "Toji Fushiguro",
    "the sorcerer killer": "Toji Fushiguro",
}

# Names that spaCy loves to tag as PERSON but are not characters

NER_PERSON_BLOCKLIST: Set[str] = {
    "jujutsu kaisen manga", "jujutsu kaisen manga and anime", "jujutsu kaisen",
    "anime", "manga", "wiki", "series", "chapter", "volume", "episode",
    "jump", "shonen jump", "viz media", "gege akutami", "gege akutami 's",
    "akutami", "shueisha", "crunchyroll", "funimation", "kanji", "rōmaji",
    "romaji", "kana", "japanese", "english", "alias", "popularity poll",
    "order of appearances", "flashback", "prologue", "references", "navigation",
    "trivia", "summary", "description", "appearance", "personality",
    "original soundtrack", "blu-ray", "dvd",
}

# Titles that are inherently locations — block spaCy from overriding to Character
KNOWN_LOCATIONS: Set[str] = {
    "tokyo", "kyoto", "shibuya", "shinjuku", "sendai", "osaka", "aizu",
    "japan", "jujutsu high", "tokyo jujutsu high", "kyoto jujutsu high",
    "tokyo metropolitan curse technical college",
}

# Titles that are inherently organizations
KNOWN_ORGS: Set[str] = {
    "jujutsu high", "tokyo jujutsu high", "kyoto jujutsu high",
    "zenin clan", "gojo clan", "kamo clan", "hei", "master denizen",
    "star plasma vessel", "time cell moon palace",
}

ORG_HINTS = {
    "clan", "headquarters", "high school", "college", "group",
    "unit", "association", "committee", "school", "family", "branch",
}

LOC_HINTS = {
    "city", "ward", "colony", "shibuya", "shinjuku", "sendai", "tokyo",
    "kyoto", "aizu", "japan",
}

TECHNIQUE_HINTS = {
    "technique", "domain expansion", "cursed technique", "shrine",
    "limitless", "black flash", "reverse cursed technique", "simple domain",
    "binding vow", "projection sorcery", "copy", "ten shadows",
    "idle transfiguration",
}

OBJECT_HINTS = {
    "tool", "weapon", "object", "finger", "realm", "spear", "katana",
    "rope", "chain", "cursed womb", "cursed object",
}

BATTLE_RE = re.compile(r"\bvs\.?\b", re.I)

SECTION_HEADERS = {
    "summary", "plot details", "prologue", "battle", "aftermath",
    "appearance", "personality", "abilities and powers", "abilities",
    "history", "description", "usage", "domain expansion",
    "locations", "characters in order of appearance",
    "character in order of appearances",
    "jutsu", "jutsu battles & events", "battles & events", "trivia",
    "navigation", "references", "setting", "members", "administration",
    "base of operations", "overview", "rules and security",
}

RELATION_PATTERNS = [
    (r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3})\s+(?:fights?|battles?|confronts?)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3})", "FIGHTS"),
    (r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3})\s+(?:kills?|defeats?|slashes?|exorcises?|beats?)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3})", "DEFEATS"),
    (r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3})\s+(?:uses?|wields?|activates?)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3}(?:\s+[A-Za-z]+){0,3})", "USES"),
    (r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3})\s+(?:summons?|conjures?|unleashes?)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3})", "SUMMONS"),
    (r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3})\s+(?:creates?|created)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3})", "CREATES"),
    (r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3})\s+(?:joins?|belongs to|is part of)\s+(?:the\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3})", "BELONGS_TO"),
    (r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3})\s+(?:protects?|guards?|saves?|rescues?)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3})", "PROTECTS"),
]

# -----------------------------------------------------------------------------
# Utilities
# -----------------------------------------------------------------------------

# Trailing possessive / noise patterns to strip from names
_POSSESSIVE_RE   = re.compile(r"\s+'s?\s*$", re.I)
_LEADING_ART_RE  = re.compile(r"^(?:the|a|an)\s+", re.I)
# Single-token fragments that are likely NER noise (≤3 chars, or all-lowercase short word)
_FRAGMENT_RE     = re.compile(r"^[a-z]{1,3}$")



def normalize_name(text: str) -> str:
    text = text.replace("_", " ")
    text = text.replace("\u2019", "'")
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"^[\W_]+|[\W_]+$", "", text)
    text = re.sub(r"[’']s$", "", text, flags=re.I).strip()
    text = re.sub(r"[’']$", "", text).strip()
    return text


def key(text: str) -> str:
    return normalize_name(text).lower()


def is_garbage_name(name: str) -> bool:
    k = key(name)
    if not k:
        return True
    if _FRAGMENT_RE.match(k):
        return True
    if k in NER_PERSON_BLOCKLIST:
        return True
    if re.search(r"\d", k) and len(k) < 6:
        return True
    if len(name) <= 3 and name == name.lower():
        return True
    if re.match(r"^(?:while|after|before|during|battle|prologue|description|aftermath)\b", k):
        return True
    if re.search(r"\b(?:manga|anime|chapter|episode|volume|soundtrack|blu-?ray|dvd|popularity poll|order of appearances)\b", k):
        return True
    return False


def _strip_leading_article(text: str) -> str:
    return re.sub(r"^(?:the|a|an)\s+", "", text, flags=re.I).strip()


def _clean_battle_part(text: str) -> str:
    text = normalize_name(text)
    text = re.sub(r"\s+(?:first|second|third|final)\s+(?:fight|battle)$", "", text, flags=re.I).strip()
    text = re.sub(r"\s+rematch$", "", text, flags=re.I).strip()
    text = re.sub(r"\s+(?:part\s+\d+|round\s+\d+)$", "", text, flags=re.I).strip()
    return text


def _classify_title_part(part: str) -> str:
    tl = key(part)
    tl_no_article = _strip_leading_article(tl)
    if tl_no_article in KNOWN_ORGS or any(h in tl_no_article for h in ORG_HINTS) or any(x in tl_no_article for x in {"sorcerers", "curse users", "curse user", "group", "team", "unit"}):
        return "Organization"
    if tl_no_article in KNOWN_LOCATIONS or any(h in tl_no_article for h in LOC_HINTS):
        return "Location"
    if any(h in tl_no_article for h in TECHNIQUE_HINTS):
        return "Technique"
    if any(h in tl_no_article for h in OBJECT_HINTS):
        return "Object"
    return "Character"


def resolve_alias(name: str, kind: str) -> tuple[str, str]:
    """
    Resolve character first-name aliases to canonical full names.
    Also resolves arc aliases.
    Returns (canonical_name, kind).
    """
    k = key(name)

    # Arc alias check first
    if k in ARC_ALIASES:
        return ARC_ALIASES[k], "Arc"

    # Character alias only for Character/Entity kinds
    if kind in {"Character", "Entity"} and k in CHARACTER_ALIASES:
        return CHARACTER_ALIASES[k], "Character"

    return name, kind



def is_junk_title(title: str) -> bool:
    t = key(title)
    if t in SKIP_EXACT:
        return True
    return any(p in t for p in SKIP_PATTERNS)


def split_title_list(title: str) -> List[str]:
    """
    Splits titles like:
      - "Satoru Gojo vs. Ryomen Sukuna"
      - "Yuta Okkotsu vs. Takako Uro vs. Ryu Ishigori"
      - "Yuji Itadori & Aoi Todo vs. Mahito"
    """
    title = normalize_name(title)
    title = _clean_battle_part(title)
    parts = re.split(r"\s+vs\.?\s+", title, flags=re.I)
    out: List[str] = []

    for part in parts:
        subparts = re.split(r"\s*&\s*|\s+and\s+|,\s*", part, flags=re.I)
        for sp in subparts:
            sp = _clean_battle_part(sp)
            if 2 <= len(sp) <= 80:
                out.append(sp)

    seen: Set[str] = set()
    deduped: List[str] = []
    for p in out:
        k = key(p)
        if k not in seen:
            seen.add(k)
            deduped.append(p)
    return deduped


def infer_kind_from_title(title: str) -> str:
    t  = normalize_name(title)
    tl = t.lower()
    tl_no_article = _strip_leading_article(tl)

    if is_junk_title(t):
        return "Junk"
    if BATTLE_RE.search(t):
        return "Battle"
    if tl_no_article.endswith(" arc") or tl_no_article in ARC_ALIASES:
        return "Arc"
    if tl_no_article.startswith("chapter ") or tl_no_article.startswith("episode ") or tl_no_article.startswith("volume "):
        return "Document"
    if tl_no_article in KNOWN_LOCATIONS or any(h in tl_no_article for h in LOC_HINTS):
        return "Location"
    if tl_no_article in KNOWN_ORGS:
        return "Organization"
    if any(h in tl_no_article for h in TECHNIQUE_HINTS):
        return "Technique"
    if any(h in tl_no_article for h in ORG_HINTS):
        return "Organization"
    if any(h in tl_no_article for h in OBJECT_HINTS):
        return "Object"
    return "Entity"


def should_keep_title_as_node(title: str) -> bool:
    kind = infer_kind_from_title(title)
    return kind not in {"Junk", "Document"}


# ---------------------------------------------------------------------------
# Kind priority: higher number = more specific / wins in conflicts
# ---------------------------------------------------------------------------
KIND_PRIORITY = {
    "Character":    7,
    "Arc":          7,
    "Battle":       7,
    "Technique":    6,
    "Object":       6,
    "Organization": 5,
    "Location":     5,
    "Entity":       2,
    "Document":     1,
    "Junk":         0,
}


def best_kind(existing: str, candidate: str) -> str:
    """Return whichever kind has higher specificity priority."""
    return existing if KIND_PRIORITY.get(existing, 0) >= KIND_PRIORITY.get(candidate, 0) else candidate


def entity_kind_from_ner(label: str, name: str, title_kind: str) -> str:
    """
    Derive entity kind from spaCy NER label, but never let NER *downgrade*
    a kind that was already determined from the title/hints (e.g. Tokyo→Location
    must not become Character just because spaCy says PERSON).
    """
    tl = name.lower()

    # Hard overrides: known locations / orgs must not become Character
    if tl in KNOWN_LOCATIONS:
        return "Location"
    if tl in KNOWN_ORGS:
        return "Organization"

    ner_kind: str
    if label == "PERSON":
        ner_kind = "Character"
    elif label in {"GPE", "LOC"}:
        ner_kind = "Location"
    elif label == "ORG":
        ner_kind = "Organization"
    elif label in {"WORK_OF_ART", "EVENT"}:
        if "arc" in tl or tl in ARC_ALIASES:
            ner_kind = "Arc"
        elif "vs" in tl:
            ner_kind = "Battle"
        else:
            ner_kind = "Entity"
    else:
        ner_kind = "Entity"

    # If title-based kind is already specific, keep it
    return best_kind(title_kind, ner_kind)


def clean_text(raw: str) -> str:
    raw = re.sub(r"\[\d+\]", "", raw)
    raw = raw.replace("\r\n", "\n").replace("\r", "\n")
    return raw


def is_section_header(line: str) -> bool:
    s = line.strip().lower()
    if s in SECTION_HEADERS:
        return True
    if re.match(r"^.{5,80} arc$", s):
        return True
    if len(s) <= 60 and line.strip()[:1].isalpha():
        return s in SECTION_HEADERS
    return False


def parse_wiki_file(filepath: str) -> dict:
    path  = Path(filepath)
    title = normalize_name(path.stem)

    with open(filepath, "r", encoding="utf-8") as f:
        raw = f.read()

    raw_clean = clean_text(raw)

    sections: List[dict] = []
    current_heading = "Overview"
    current_content: List[str] = []

    for line in raw_clean.splitlines():
        line = line.strip()
        if not line:
            continue
        if line in {"Manga", "Anime", "Covers", "Extras"}:
            continue

        if is_section_header(line):
            if current_content:
                sections.append({
                    "heading": current_heading,
                    "content": " ".join(current_content).strip(),
                })
            current_heading = line
            current_content = []
        else:
            current_content.append(line)

    if current_content:
        sections.append({
            "heading": current_heading,
            "content": " ".join(current_content).strip(),
        })

    return {
        "title":    title,
        "filepath": filepath,
        "kind":     infer_kind_from_title(title),
        "sections": sections,
        "raw_text": raw_clean,
    }

# -----------------------------------------------------------------------------
# Extraction
# -----------------------------------------------------------------------------

@dataclass
class NodeEvidence:
    name:    str
    kind:    str
    sources: Set[str] = field(default_factory=set)


def find_arcs_in_text(text: str) -> Set[str]:
    arcs  = set()
    lower = text.lower()
    for alias, canon in ARC_ALIASES.items():
        if alias in lower:
            arcs.add(canon)
    return arcs


def _add_node(nodes: Dict[str, NodeEvidence], name: str, kind: str, source: str) -> None:
    """
    Safe helper: resolve alias, reject garbage, then upsert into `nodes` dict
    using kind priority (most specific kind wins).
    """
    if is_garbage_name(name):
        return

    # Resolve alias → canonical name + possibly upgraded kind
    name, kind = resolve_alias(name, kind)

    if is_garbage_name(name):   # re-check after alias resolution
        return

    ck = key(name)
    if ck not in nodes:
        nodes[ck] = NodeEvidence(name=name, kind=kind, sources={source})
    else:
        nodes[ck].kind = best_kind(nodes[ck].kind, kind)
        nodes[ck].sources.add(source)
        # Keep the most-canonical form of the name (prefer longer / title-cased)
        if len(name) > len(nodes[ck].name):
            nodes[ck].name = name


def extract_candidates(
    doc_data: dict,
    known_titles: Set[str],
    known_semantic_titles: Set[str],
) -> dict:
    title    = doc_data["title"]
    doc_kind = doc_data["kind"]

    # Skip Document-type titles from becoming Entity nodes entirely
    if doc_kind == "Document":
        return {"nodes": {}, "relations": [], "doc_arcs": set()}

    nodes: Dict[str, NodeEvidence] = {}
    relations: List[dict]          = []

    full_text = "\n".join(s["content"] for s in doc_data["sections"] if s["content"])
    if not full_text.strip():
        full_text = doc_data["raw_text"]
    full_text = full_text[:MAX_TEXT_FOR_NLP]

    # 1) Title-based semantic nodes
    if should_keep_title_as_node(title):
        kind = infer_kind_from_title(title)
        _add_node(nodes, title, kind, "title")

    # 2) Battle title participants
    if doc_kind == "Battle":
        for p in split_title_list(title):
            pkind = _classify_title_part(p)
            _add_node(nodes, p, pkind, "battle_title")

    # 3) Arc detection from title/body
    doc_arcs: Set[str] = set()
    if doc_kind == "Arc":
        doc_arcs.add(title)
    doc_arcs.update(find_arcs_in_text(title))
    doc_arcs.update(find_arcs_in_text(full_text))

    for arc in doc_arcs:
        _add_node(nodes, arc, "Arc", "arc_match")

    # 4) Relationship patterns per section  (require Title-Case subjects)
    for section in doc_data["sections"]:
        sec_text = section["content"]
        if not sec_text:
            continue

        for pattern, rel in RELATION_PATTERNS:
            for m in re.finditer(pattern, sec_text):
                src = normalize_name(m.group(1))
                tgt = normalize_name(m.group(2))

                # Strip trailing noise (articles, conjunctions)
                tgt = re.sub(r"\s+(?:and|or|but|with|for|in|on|at|to|a|an|the)\s.*$", "", tgt, flags=re.I).strip()

                if len(src) < 2 or len(tgt) < 2:
                    continue
                if is_garbage_name(src) or is_garbage_name(tgt):
                    continue

                src_r, _ = resolve_alias(src, "Character")
                tgt_r, _ = resolve_alias(tgt, "Character")

                relations.append({
                    "source":      src_r,
                    "target":      tgt_r,
                    "relation":    rel,
                    "section":     section["heading"],
                    "in_document": title,
                })

    # 5) Lightweight NER
    if nlp is not None and full_text.strip():
        try:
            spacy_doc = nlp(full_text)
            for ent in spacy_doc.ents:
                name = normalize_name(ent.text)

                if is_garbage_name(name):
                    continue
                if not (2 <= len(name) <= 80):
                    continue

                ck = key(name)

                # Only keep if it's a known title or a strong NER label
                if ck not in known_titles and ck not in known_semantic_titles \
                        and ent.label_ not in {"PERSON", "ORG", "GPE", "LOC", "WORK_OF_ART", "EVENT"}:
                    continue

                # Determine existing kind from title hints (don't let NER override)
                existing_kind = infer_kind_from_title(name)
                if existing_kind == "Junk":
                    continue

                kind = entity_kind_from_ner(ent.label_, name, existing_kind)
                _add_node(nodes, name, kind, f"ner:{ent.label_}")

        except Exception as e:
            logger.warning("spaCy extraction failed for %s: %s", title, e)

    # 6) Explicit arcs → doc->arc relation
    for arc in doc_arcs:
        relations.append({
            "source":      title,
            "target":      arc,
            "relation":    "ABOUT_ARC",
            "section":     "Document",
            "in_document": title,
        })

    # 7) Battle docs link to participants
    if doc_kind == "Battle":
        for p in split_title_list(title):
            p_r, _ = resolve_alias(p, "Character")
            relations.append({
                "source":      title,
                "target":      p_r,
                "relation":    "INVOLVES",
                "section":     "Title",
                "in_document": title,
            })

    return {"nodes": nodes, "relations": relations, "doc_arcs": doc_arcs}

# -----------------------------------------------------------------------------
# Neo4j writer
# -----------------------------------------------------------------------------

KIND_LABELS = {
    "Character":    "Character",
    "Arc":          "Arc",
    "Battle":       "Battle",
    "Technique":    "Technique",
    "Location":     "Location",
    "Organization": "Organization",
    "Object":       "Object",
    "Document":     "Document",
    "Entity":       "Entity",
}


RELATION_WHITELIST = {
    "FIGHTS", "DEFEATS", "USES", "SUMMONS", "CREATES",
    "BELONGS_TO", "APPEARS_IN", "ABOUT_ARC", "INVOLVES",
    "MENTIONED_IN", "PROTECTS", "RELATES_TO",
}

DOC_RELATION_WHITELIST = {
    "NEXT_CHAPTER", "PREVIOUS_CHAPTER",
    "NEXT_EPISODE", "PREVIOUS_EPISODE",
    "NEXT_VOLUME", "PREVIOUS_VOLUME",
}


class GraphBuilder:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)
        )

    def close(self):
        self.driver.close()

    def clear_graph(self):
        logger.info("Clearing existing graph — deleting all nodes and relationships...")
        with self.driver.session() as session:
            result = session.run("MATCH (n) RETURN count(n) AS total")
            total  = result.single()["total"]
            logger.info("  Found %d existing nodes to delete", total)
            session.run("MATCH (n) DETACH DELETE n")
        logger.info("  Graph cleared successfully")

    def create_constraints(self):
        logger.info("Creating uniqueness constraints...")
        constraints = [
            ("entity_name",    "CREATE CONSTRAINT entity_name    IF NOT EXISTS FOR (e:Entity)       REQUIRE e.name  IS UNIQUE"),
            ("document_title", "CREATE CONSTRAINT document_title IF NOT EXISTS FOR (d:Document)     REQUIRE d.title IS UNIQUE"),
            ("arc_name",       "CREATE CONSTRAINT arc_name       IF NOT EXISTS FOR (a:Arc)          REQUIRE a.name  IS UNIQUE"),
            ("battle_name",    "CREATE CONSTRAINT battle_name    IF NOT EXISTS FOR (b:Battle)       REQUIRE b.name  IS UNIQUE"),
            ("char_name",      "CREATE CONSTRAINT character_name IF NOT EXISTS FOR (c:Character)    REQUIRE c.name  IS UNIQUE"),
            ("tech_name",      "CREATE CONSTRAINT technique_name IF NOT EXISTS FOR (t:Technique)    REQUIRE t.name  IS UNIQUE"),
            ("loc_name",       "CREATE CONSTRAINT location_name  IF NOT EXISTS FOR (l:Location)     REQUIRE l.name  IS UNIQUE"),
            ("org_name",       "CREATE CONSTRAINT org_name       IF NOT EXISTS FOR (o:Organization) REQUIRE o.name  IS UNIQUE"),
            ("obj_name",       "CREATE CONSTRAINT object_name    IF NOT EXISTS FOR (x:Object)       REQUIRE x.name  IS UNIQUE"),
        ]
        with self.driver.session() as session:
            for _, cypher in constraints:
                session.run(cypher)
        logger.info("  Constraints ready")

    def upsert_document(self, doc: dict):
        with self.driver.session() as session:
            session.run(
                """
                MERGE (d:Document {title: $title})
                SET d.filepath   = $filepath,
                    d.kind       = $kind,
                    d.updated_at = datetime(),
                    d.raw_text   = $raw_text
                """,
                title=doc["title"],
                filepath=doc["filepath"],
                kind=doc["kind"],
                raw_text=doc["raw_text"][:8000],
            )

    def upsert_node(
        self,
        name:     str,
        kind:     str,
        doc_freq: int,
        sources:  Optional[List[str]] = None,
    ):
        """
        MERGE on base :Entity label only (avoids ConstraintValidationFailed
        when the node already exists with a different label set).
        Then SET the specific label as an additive operation.
        Document nodes are NEVER written here — they go through upsert_document.
        """
        if kind == "Document":
            return

        label   = KIND_LABELS.get(kind, "Entity")
        sources = sources or []

        with self.driver.session() as session:
            session.run(
                f"""
                MERGE (n:Entity {{name: $name}})
                SET n:{label},
                    n.kind       = $kind,
                    n.doc_freq   = $doc_freq,
                    n.updated_at = datetime()
                WITH n
                SET n.sources = reduce(
                    acc = [],
                    s IN coalesce(n.sources, []) + coalesce($sources, []) |
                    CASE WHEN s IN acc THEN acc ELSE acc + s END
                )
                """,
                name=name,
                kind=kind,
                doc_freq=doc_freq,
                sources=sources,
            )

    def upsert_document_link(
        self,
        entity_name: str,
        doc_title:   str,
        rel:         str = "MENTIONED_IN",
    ):
        rel = rel.upper().strip()
        if rel not in RELATION_WHITELIST:
            rel = "MENTIONED_IN"

        with self.driver.session() as session:
            session.run(
                f"""
                MERGE (e:Entity  {{name:  $entity_name}})
                MERGE (d:Document {{title: $doc_title}})
                MERGE (e)-[r:{rel}]->(d)
                ON CREATE SET r.weight = 1
                ON MATCH  SET r.weight = coalesce(r.weight, 0) + 1
                """,
                entity_name=entity_name,
                doc_title=doc_title,
            )

    def upsert_document_relation(
        self,
        src_title: str,
        tgt_title: str,
        rel: str,
        props: Optional[dict] = None,
    ):
        rel = rel.upper().strip()
        if rel not in DOC_RELATION_WHITELIST:
            rel = "NEXT_CHAPTER"
        props = props or {}

        with self.driver.session() as session:
            session.run(
                f"""
                MERGE (a:Document {{title: $src_title}})
                MERGE (b:Document {{title: $tgt_title}})
                MERGE (a)-[r:{rel}]->(b)
                ON CREATE SET r.weight = 1
                ON MATCH  SET r.weight = coalesce(r.weight, 0) + 1
                SET r += $props
                """,
                src_title=src_title,
                tgt_title=tgt_title,
                props=props,
            )

    def upsert_relation(
        self,
        src:      str,
        tgt:      str,
        rel:      str,
        src_kind: str,
        tgt_kind: str,
        props:    Optional[dict] = None,
    ):
        rel = rel.upper().strip()
        if rel not in RELATION_WHITELIST:
            rel = "RELATES_TO"

        src_label = KIND_LABELS.get(src_kind, "Entity")
        tgt_label = KIND_LABELS.get(tgt_kind, "Entity")
        props     = props or {}

        with self.driver.session() as session:
            session.run(
                f"""
                MERGE (a:Entity {{name: $src}})
                SET a:{src_label}
                WITH a
                MERGE (b:Entity {{name: $tgt}})
                SET b:{tgt_label}
                WITH a, b
                MERGE (a)-[r:{rel}]->(b)
                ON CREATE SET r.weight = 1
                ON MATCH  SET r.weight = coalesce(r.weight, 0) + 1
                SET r += $props
                """,
                src=src,
                tgt=tgt,
                props=props,
            )

    def fix_entity_document_overlap(self):
        """
        Remove :Entity label from nodes that are also :Document.
        Happens when a document title was accidentally promoted as an entity.
        """
        logger.info("  Cleaning up Entity+Document label overlap...")
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (n:Entity:Document)
                REMOVE n:Entity
                RETURN count(n) AS fixed
                """
            )
            fixed = result.single()["fixed"]
        logger.info("    Removed :Entity label from %d Document nodes", fixed)

# -----------------------------------------------------------------------------
# Main build
# -----------------------------------------------------------------------------

def build_graph(files_dir: Path, clear_existing: bool = False):
    logger.info("=" * 60)
    logger.info("JJK Graph Build — START")
    logger.info("  Source dir : %s", files_dir)
    logger.info("  Clear existing graph: %s", clear_existing)
    logger.info("  Min doc frequency   : %d", MIN_DOC_FREQ)
    logger.info("  NLP model           : %s", SPACY_MODEL if nlp else "disabled")
    logger.info("=" * 60)

    # -------------------------------------------------------------------------
    # Phase 1: Discover files
    # -------------------------------------------------------------------------
    logger.info("[Phase 1/5] Discovering .txt files in %s ...", files_dir)
    all_text_files = sorted(files_dir.rglob("*.txt"))
    text_files = [p for p in all_text_files if not is_junk_title(p.stem)]
    logger.info("  Found %d txt files (%d skipped junk)", len(text_files), len(all_text_files) - len(text_files))

    known_titles = {key(p.stem) for p in text_files}
    known_semantic_titles = {
        key(p.stem)
        for p in text_files
        if should_keep_title_as_node(p.stem)
    }
    logger.info("  Total title keys          : %d", len(known_titles))
    logger.info("  Semantic title candidates : %d", len(known_semantic_titles))

    # -------------------------------------------------------------------------
    # Phase 2: Parse docs and extract candidates
    # -------------------------------------------------------------------------
    logger.info("[Phase 2/5] Parsing documents and extracting candidates...")

    parsed_docs: List[dict]           = []
    skipped                           = 0
    failed: List[tuple]               = []
    doc_entity_counter: Counter[str]  = Counter()
    entity_kind_by_key: Dict[str,str] = {}
    entity_name_by_key: Dict[str,str] = {}
    entity_sources: Dict[str,Set[str]]= defaultdict(set)
    doc_payloads: List[tuple]         = []

    total_files = len(text_files)
    for idx, fp in enumerate(text_files, start=1):
        if idx % 100 == 0 or idx == total_files:
            logger.info("  Parsing file %d/%d ...", idx, total_files)

        try:
            doc = parse_wiki_file(str(fp))

            if is_junk_title(doc["title"]) or not doc["raw_text"].strip():
                logger.debug("  [SKIP] %s (junk or empty)", doc["title"])
                skipped += 1
                continue

            extracted = extract_candidates(doc, known_titles, known_semantic_titles)
            parsed_docs.append(doc)
            doc_payloads.append((doc, extracted))

            seen_in_doc: Set[str] = set()
            for ck, node in extracted["nodes"].items():
                if ck in seen_in_doc:
                    continue
                seen_in_doc.add(ck)
                doc_entity_counter[ck] += 1
                # Use best_kind to accumulate the most specific kind across docs
                prev_kind = entity_kind_by_key.get(ck, "Entity")
                entity_kind_by_key[ck] = best_kind(prev_kind, node.kind)
                # Keep longest / most canonical name form
                prev_name = entity_name_by_key.get(ck, node.name)
                entity_name_by_key[ck] = node.name if len(node.name) >= len(prev_name) else prev_name
                entity_sources[ck].update(node.sources)

        except Exception as e:
            logger.warning("  [ERROR] Failed to parse %s: %s", fp.name, e)
            failed.append((str(fp), str(e)))

    logger.info("  Parsed    : %d docs", len(parsed_docs))
    logger.info("  Skipped   : %d docs (junk/empty)", skipped)
    logger.info("  Failed    : %d docs", len(failed))
    logger.info("  Raw candidate entity keys: %d", len(doc_entity_counter))

    # -------------------------------------------------------------------------
    # Phase 3: Decide which nodes to promote
    # -------------------------------------------------------------------------
    logger.info("[Phase 3/5] Filtering candidate nodes (MIN_DOC_FREQ=%d) ...", MIN_DOC_FREQ)

    keep_keys: Set[str]       = set()
    kind_counts: Counter[str] = Counter()

    for ck, freq in doc_entity_counter.items():
        kind = entity_kind_by_key.get(ck, "Entity")
        if kind in {"Document", "Junk"}:
            continue
        if freq >= MIN_DOC_FREQ:
            keep_keys.add(ck)
            kind_counts[kind] += 1
        elif kind in {"Arc", "Battle", "Character", "Technique", "Location", "Organization", "Object"}:
            keep_keys.add(ck)
            kind_counts[kind] += 1
        elif ck in known_semantic_titles:
            keep_keys.add(ck)
            kind_counts[kind] += 1

    logger.info("  Keeping %d semantic nodes", len(keep_keys))
    for kind, count in sorted(kind_counts.items(), key=lambda x: -x[1]):
        logger.info("    %-20s : %d", kind, count)

    # -------------------------------------------------------------------------
    # Phase 4: Connect to Neo4j and write graph
    # -------------------------------------------------------------------------
    logger.info("[Phase 4/5] Connecting to Neo4j at %s ...", NEO4J_URI)
    graph = GraphBuilder()
    graph.create_constraints()

    if clear_existing:
        graph.clear_graph()

    chronology_written = 0

    try:
        # --- Write document nodes ---
        logger.info("  Writing %d document nodes ...", len(doc_payloads))
        for i, (doc, _) in enumerate(doc_payloads, start=1):
            graph.upsert_document(doc)
            if i % 200 == 0 or i == len(doc_payloads):
                logger.info("    Documents written: %d/%d", i, len(doc_payloads))


        # --- Write chronology edges between sequential documents ---
        def seq_key(title: str):
            t = normalize_name(title)
            m = re.match(r"^(chapter|episode|volume)\s+(\d+)(?:-(\d+))?$", t, flags=re.I)
            if not m:
                return None
            kind = m.group(1).lower()
            major = int(m.group(2))
            minor = int(m.group(3) or 0)
            return kind, (major, minor)

        grouped_docs: Dict[str, List[str]] = defaultdict(list)
        for doc, _ in doc_payloads:
            sk = seq_key(doc["title"])
            if sk is None:
                continue
            grouped_docs[sk[0]].append(doc["title"])

        for seq_kind, titles in grouped_docs.items():
            def sort_key(tt: str):
                _, pair = seq_key(tt)
                return pair
            titles = sorted(titles, key=sort_key)
            rel_name = {
                "chapter": "NEXT_CHAPTER",
                "episode": "NEXT_EPISODE",
                "volume": "NEXT_VOLUME",
            }.get(seq_kind)
            if not rel_name or len(titles) < 2:
                continue
            for a, b in zip(titles, titles[1:]):
                graph.upsert_document_relation(a, b, rel_name, props={"source_kind": seq_kind})
                chronology_written += 1

        # --- Write entity nodes and relationships ---
        logger.info("  Writing entity nodes and relationships (%d docs) ...", len(doc_payloads))

        total_nodes_written = 0
        total_links_written = 0
        total_rels_written  = 0

        for i, (doc, extracted) in enumerate(doc_payloads, start=1):
            title           = doc["title"]
            doc_nodes_written = 0
            doc_rels_written  = 0

            # promoted nodes
            for ck, node in extracted["nodes"].items():
                if ck not in keep_keys:
                    continue
                # Use the globally-accumulated best kind and canonical name
                best_name = entity_name_by_key.get(ck, node.name)
                best_k    = entity_kind_by_key.get(ck, node.kind)
                if best_k in {"Document", "Junk"}:
                    continue

                graph.upsert_node(
                    name=best_name,
                    kind=best_k,
                    doc_freq=doc_entity_counter.get(ck, 1),
                    sources=sorted(entity_sources.get(ck, set())),
                )
                graph.upsert_document_link(best_name, title, rel="MENTIONED_IN")
                doc_nodes_written  += 1
                total_nodes_written += 1
                total_links_written += 1

            # semantic relations
            for rel in extracted["relations"]:
                src = normalize_name(rel["source"])
                tgt = normalize_name(rel["target"])

                if is_garbage_name(src) or is_garbage_name(tgt):
                    continue

                src, _ = resolve_alias(src, "Character")
                tgt, _ = resolve_alias(tgt, "Character")

                src_ck = key(src)
                tgt_ck = key(tgt)

                src_kind = entity_kind_by_key.get(src_ck, infer_kind_from_title(src))
                tgt_kind = entity_kind_by_key.get(tgt_ck, infer_kind_from_title(tgt))

                if src_kind == "Entity":
                    src_kind = _classify_title_part(src)
                if tgt_kind == "Entity":
                    tgt_kind = _classify_title_part(tgt)

                if src_kind in {"Document", "Junk"} or tgt_kind in {"Document", "Junk"}:
                    continue

                rel_type = rel["relation"].upper().strip()
                if rel_type not in RELATION_WHITELIST:
                    rel_type = "RELATES_TO"

                should_keep = (
                    src_ck in keep_keys
                    or tgt_ck in keep_keys
                    or rel_type in {"ABOUT_ARC", "INVOLVES"}
                )
                if not should_keep:
                    continue

                graph.upsert_relation(
                    src=src,
                    tgt=tgt,
                    rel=rel_type,
                    src_kind=src_kind,
                    tgt_kind=tgt_kind,
                    props={
                        "section":    rel.get("section", ""),
                        "source_doc": rel.get("in_document", ""),
                    },
                )
                doc_rels_written   += 1
                total_rels_written += 1

            if i % 100 == 0 or i == len(doc_payloads):
                logger.info(
                    "    [%d/%d] %-50s | +%d nodes  +%d rels  (total nodes=%d, rels=%d)",
                    i, len(doc_payloads), title[:50],
                    doc_nodes_written, doc_rels_written,
                    total_nodes_written, total_rels_written,
                )

        # --- Post-processing: remove Entity+Document overlap ---
        graph.fix_entity_document_overlap()

    finally:
        graph.close()
        logger.info("  Neo4j connection closed")

    # -------------------------------------------------------------------------
    # Phase 5: Summary
    # -------------------------------------------------------------------------
    logger.info("[Phase 5/5] Build summary")
    logger.info("  Documents written        : %d", len(doc_payloads))
    logger.info("  Entity node upserts      : %d", total_nodes_written)
    logger.info("  MENTIONED_IN link upserts: %d", total_links_written)
    logger.info("  Semantic rel upserts     : %d", total_rels_written)
    logger.info("  Chronology rel upserts   : %d", chronology_written)
    logger.info("  Skipped (junk/empty)     : %d", skipped)
    logger.info("  Parse failures           : %d", len(failed))

    if failed:
        with open("failed_files.json", "w", encoding="utf-8") as f:
            json.dump(failed, f, indent=2, ensure_ascii=False)
        logger.warning("  Failed files saved to failed_files.json")

    logger.info("=" * 60)
    logger.info("Graph build COMPLETE")
    logger.info("=" * 60)


if __name__ == "__main__":
    build_graph(TEXT_FILES_DIR, clear_existing=CLEAR_EXISTING)