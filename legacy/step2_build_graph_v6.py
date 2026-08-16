"""
Step 2 (v6): Build a cleaner, provenance-rich Neo4j graph from scraped JJK wiki text files.

What changed from the earlier builder:
- Removes the broad :Entity dependence for semantic nodes; primary labels are now
  Character / Location / Organization / Technique / Battle / Arc / Object.
- Adds universe tagging (canon / modulo).
- Adds provenance and confidence to semantic edges.
- Parses infoboxes and section lists so episode / arc / character pages produce
  structured facts instead of just raw mentions.
- Adds canonical alias handling before graph write, with a single canonical id
  per semantic node.
- Adds a dry-run mode so sample pages can be validated without Neo4j.
- Keeps chronology edges for chapter / episode / volume pages.
- Preserves traceability through Document nodes, but prevents them from dominating
  the graph.

Run:
    python step2_build_graph_v6.py --source <txt_folder> --dry-run
or:
    python -m pipeline.step2_build_graph_v6
"""

from __future__ import annotations

import argparse
import json
import logging
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import DefaultDict, Dict, Iterable, List, Optional, Sequence, Set, Tuple

try:
    from neo4j import GraphDatabase
except Exception:  # pragma: no cover - optional dependency
    GraphDatabase = None  # type: ignore

# Optional spaCy: used as a booster, not a dependency.
try:
    import spacy  # type: ignore
except Exception:  # pragma: no cover
    spacy = None  # type: ignore

# -----------------------------------------------------------------------------
# Config
# -----------------------------------------------------------------------------

TEXT_FILES_DIR = Path(r"E:\VS CODE\Midnight Render\Softwares\RAG\out\step_one_raw_scrapped_data\jjk")

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password"

CLEAR_EXISTING = True
MIN_DOC_FREQ = 2
MAX_TEXT_FOR_NLP = 120_000
SPACY_MODEL = "en_core_web_trf"
DRY_RUN_DEFAULT = False

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("jjk-graphbuilder-v6")

# -----------------------------------------------------------------------------
# Optional NLP
# -----------------------------------------------------------------------------

nlp = None
if spacy is not None:
    try:
        nlp = spacy.load(SPACY_MODEL)
        logger.info("Loaded spaCy model: %s", SPACY_MODEL)
    except Exception:
        try:
            nlp = spacy.load("en_core_web_sm")
            logger.warning("Falling back to en_core_web_sm")
        except Exception as e:
            logger.warning("spaCy unavailable; regex-only extraction will be used: %s", e)

# -----------------------------------------------------------------------------
# Canonical mappings and heuristics
# -----------------------------------------------------------------------------

ARC_ALIASES: Dict[str, str] = {
    "fearsome womb": "Fearsome Womb",
    "fearsome womb arc": "Fearsome Womb",
    "hidden inventory": "Hidden Inventory",
    "hidden inventory/premature death": "Hidden Inventory",
    "premature death": "Premature Death",
    "gojo's past": "Gojo's Past",
    "gojo's past arc": "Gojo's Past",
    "shibuya incident": "Shibuya Incident",
    "shibuya incident arc": "Shibuya Incident",
    "culling game": "Culling Game",
    "culling game arc": "Culling Game",
    "shinjuku showdown": "Shinjuku Showdown",
    "shinjuku showdown arc": "Shinjuku Showdown",
    "night parade of a hundred demons": "Night Parade of a Hundred Demons",
    "death painting": "Death Painting",
    "death painting arc": "Death Painting",
    "kyoto goodwill event": "Kyoto Goodwill Event",
    "kyoto goodwill event arc": "Kyoto Goodwill Event",
}

CHARACTER_ALIASES: Dict[str, str] = {
    "yuji": "Yuji Itadori",
    "itadori": "Yuji Itadori",
    "megumi": "Megumi Fushiguro",
    "fushiguro": "Megumi Fushiguro",
    "sukuna": "Ryomen Sukuna",
    "ryomen sukuna": "Ryomen Sukuna",
    "ryomen": "Ryomen Sukuna",
    "gojo": "Satoru Gojo",
    "satoru": "Satoru Gojo",
    "gojo sensei": "Satoru Gojo",
    "nobara": "Nobara Kugisaki",
    "kugisaki": "Nobara Kugisaki",
    "yuta": "Yuta Okkotsu",
    "okkotsu": "Yuta Okkotsu",
    "maki": "Maki Zenin",
    "zenin maki": "Maki Zenin",
    "toge": "Toge Inumaki",
    "inumaki": "Toge Inumaki",
    "panda": "Panda",
    "nanami": "Kento Nanami",
    "kento": "Kento Nanami",
    "todo": "Aoi Todo",
    "aoi": "Aoi Todo",
    "choso": "Choso",
    "kenjaku": "Kenjaku",
    "pseudo geto": "Kenjaku",
    "pseudo-geto": "Kenjaku",
    "geto": "Suguru Geto",
    "suguru": "Suguru Geto",
    "mahito": "Mahito",
    "hakari": "Kinji Hakari",
    "kashimo": "Hajime Kashimo",
    "yuki": "Yuki Tsukumo",
    "tsukumo": "Yuki Tsukumo",
    "ijichi": "Kiyotaka Ijichi",
    "shoko": "Shoko Ieiri",
    "ieiri": "Shoko Ieiri",
    "mei mei": "Mei Mei",
    "utahime": "Utahime Iori",
    "iori": "Utahime Iori",
    "uraume": "Uraume",
    "higuruma": "Hiromi Higuruma",
    "kusakabe": "Atsuya Kusakabe",
    "noritoshi": "Noritoshi Kamo",
    "toji": "Toji Fushiguro",
    "toji zenin": "Toji Fushiguro",
    "naobito": "Naobito Zenin",
    "naoya": "Naoya Zenin",
    "ogi": "Ogi Zenin",
    "jinichi": "Jinichi Zenin",
    "junpei": "Junpei Yoshino",
    "reggie": "Reggie Star",
    "mechamaru": "Kokichi Muta",
    "kokichi": "Kokichi Muta",
    "muta": "Kokichi Muta",
    "gakuganji": "Yoshinobu Gakuganji",
    "yaga": "Masamichi Yaga",
    "tengen": "Master Tengen",
    "angel": "Hana Kurusu",
    "hana": "Hana Kurusu",
    "kurusu": "Hana Kurusu",
    "remi": "Remi",
    "hanyu": "Hanyu",
    "haba": "Haba",
    "higuruma": "Hiromi Higuruma",
}

KNOWN_LOCATIONS: Set[str] = {
    "tokyo", "kyoto", "shibuya", "shinjuku", "sendai", "osaka", "aizu",
    "japan", "harajuku", "roppongi", "ikebukuro", "tochigi", "tokyo colony",
    "tokyo no. 1 colony", "tokyo no. 2 colony", "tokyo jujutsu high",
    "kyoto jujutsu high", "jujutsu high", "tokyo metropolitan curse technical college",
}

KNOWN_ORGS: Set[str] = {
    "jujutsu high", "zenin clan", "gojo clan", "kamo clan", "the hei",
    "the kukuru unit", "cursed spirits", "jujutsu sorcerers",
    "curse users", "higher-ups", "the higher-ups", "master tengen",
    "jujutsu headquarters", "mahito group", "sun, moon and stars squad",
    "five empty generals", "the five empty generals",
}

TECHNIQUE_HINTS = {
    "technique", "domain expansion", "cursed technique", "limitless",
    "ten shadows", "projection sorcery", "idle transfiguration", "simple domain",
    "binding vow", "reverse cursed technique", "straw doll technique",
    "construction", "blood manipulation", "self-embodiment of perfection",
}

OBJECT_HINTS = {
    "tool", "weapon", "object", "finger", "realm", "spear", "katana", "rope",
    "chain", "cursed object", "cursed tool", "sword", "nail", "hammer",
}

ORG_HINTS = {
    "clan", "school", "unit", "group", "committee", "association", "family",
    "headquarters", "brigade", "squad", "vessel", "team", "college", "users",
    "spirits", "sorcerers", "higher-ups", "denizens",
}

LOC_HINTS = {
    "city", "ward", "colony", "prefecture", "region", "town", "island", "japan",
    "tokyo", "kyoto", "osaka", "shibuya", "shinjuku", "sendai", "harajuku",
}

DOC_PREFIX_RE = re.compile(r"^(chapter|episode|volume)\s+(\d+)(?:[-–](\d+))?$", re.I)
BATTLE_RE = re.compile(r"\bvs\.?\b|\bversus\b", re.I)

SECTION_IGNORE = {
    "music", "anime & manga differences", "anime and manga differences",
    "trivia", "references", "navigation", "gallery", "image gallery",
}

RELATION_WHITELIST = {
    "MENTIONED_IN",
    "ABOUT_ARC",
    "INVOLVES",
    "FIGHTS",
    "DEFEATS",
    "USES",
    "SUMMONS",
    "CREATES",
    "BELONGS_TO",
    "PROTECTS",
    "APPEARS_IN",
    "INTRODUCES",
    "ADAPTED_FROM",
    "FIRST_APPEARS_IN",
    "RELATES_TO",
}

DOC_RELATION_WHITELIST = {
    "NEXT_CHAPTER", "PREVIOUS_CHAPTER",
    "NEXT_EPISODE", "PREVIOUS_EPISODE",
    "NEXT_VOLUME", "PREVIOUS_VOLUME",
    "NEXT_ARC", "PREVIOUS_ARC",
}

KIND_PRIORITY = {
    "Character": 7,
    "Arc": 7,
    "Battle": 7,
    "Technique": 6,
    "Object": 6,
    "Organization": 5,
    "Location": 5,
    "Document": 1,
    "Entity": 0,
    "Junk": 0,
}

PRIMARY_LABELS = {
    "Character": "Character",
    "Arc": "Arc",
    "Battle": "Battle",
    "Technique": "Technique",
    "Location": "Location",
    "Organization": "Organization",
    "Object": "Object",
    "Document": "Document",
    "Entity": "Canonical",
}

# -----------------------------------------------------------------------------
# Dataclasses
# -----------------------------------------------------------------------------

@dataclass
class Section:
    heading: str
    lines: List[str] = field(default_factory=list)

    @property
    def text(self) -> str:
        return " ".join(x.strip() for x in self.lines if x.strip()).strip()


@dataclass
class DocumentRecord:
    title: str
    filepath: str
    kind: str
    doc_subtype: str
    universe: str
    raw_text: str
    infobox: Dict[str, List[str]] = field(default_factory=dict)
    sections: List[Section] = field(default_factory=list)


@dataclass
class NodeEvidence:
    name: str
    kind: str
    universes: Set[str] = field(default_factory=set)
    sources: Set[str] = field(default_factory=set)
    aliases: Set[str] = field(default_factory=set)
    evidence_docs: Set[str] = field(default_factory=set)
    doc_freq: int = 0
    confidence_sum: float = 0.0
    confidence_count: int = 0

    @property
    def confidence(self) -> float:
        if self.confidence_count == 0:
            return 0.0
        return round(self.confidence_sum / self.confidence_count, 4)


@dataclass
class RelationEvidence:
    source: str
    target: str
    relation: str
    source_kind: str
    target_kind: str
    in_document: str
    section: str
    universe: str
    confidence: float
    evidence: str = ""
    extractor: str = "regex"


@dataclass
class BuildResult:
    docs: int
    semantic_nodes: int
    mention_links: int
    semantic_rels: int
    chronology_rels: int
    skipped: int
    failed: List[Tuple[str, str]]
    node_counter: Counter
    relation_counter: Counter
    universe_counter: Counter
    sample_nodes: List[Tuple[str, str]]
    sample_relations: List[Tuple[str, str, str]]

# -----------------------------------------------------------------------------
# Generic helpers
# -----------------------------------------------------------------------------

def normalize_name(text: str) -> str:
    text = text.replace("_", " ").replace("\u2019", "'").replace("\u2018", "'")
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"^[\W_]+|[\W_]+$", "", text)
    text = re.sub(r"\s*\((?:flashback|voice only|mentioned|image gallery|alternate)\)\s*$", "", text, flags=re.I)
    text = re.sub(r"\s+[–-]\s+(?:flashback|voice only|mentioned)$", "", text, flags=re.I)
    text = re.sub(r"[’']s$", "", text, flags=re.I).strip()
    text = re.sub(r"[’']$", "", text).strip()
    return text


def key(text: str) -> str:
    return normalize_name(text).lower()


def _strip_leading_article(text: str) -> str:
    return re.sub(r"^(?:the|a|an)\s+", "", text, flags=re.I).strip()


def is_garbage_name(name: str) -> bool:
    k = key(name)
    if not k:
        return True
    if len(k) <= 2:
        return True
    if re.fullmatch(r"\d+", k):
        return True
    if re.search(r"\b(?:chapter|episode|volume|summary|synopsis|gallery|trivia|music|references)\b", k):
        return True
    if re.search(r"\d", k) and len(k) < 6:
        return True
    if k in {
        "jujutsu kaisen", "jjk", "anime", "manga", "wiki", "series",
        "profile", "summary", "synopsis", "description", "appearance",
        "personality", "abilities and powers", "profile", "infobox",
        "portrayal", "club", "furudate", "akutami", "shueisha", "viz",
        "voice", "opening song", "ending song", "episode guide",
    }:
        return True
    if re.match(r"^(?:while|after|before|during|battle|prologue|description|aftermath)\b", k):
        return True
    return False


def strip_descriptor_suffix(name: str) -> str:
    return re.sub(r"\s*\((?:flashback|voice only|mentioned|debut|child|adult)\)\s*$", "", name, flags=re.I).strip()


PROPER_STOPWORDS = {
    "the", "of", "and", "or", "vs", "vs.", "to", "in", "on", "at", "for", "with",
    "by", "from", "into", "over", "under", "after", "before", "during", "as", "a", "an",
}

def is_strong_name_candidate(text: str) -> bool:
    t = normalize_name(strip_descriptor_suffix(text))
    if is_garbage_name(t):
        return False
    if len(t) > 80:
        return False
    toks = [tok for tok in re.split(r"\s+", t) if tok]
    if not toks or len(toks) > 6:
        return False
    # allow canonical aliases / titles directly
    if key(t) in CHARACTER_ALIASES or key(t) in ARC_ALIASES or key(t) in KNOWN_LOCATIONS or key(t) in KNOWN_ORGS:
        return True
    good_tokens = 0
    for tok in toks:
        low = tok.lower()
        if low in PROPER_STOPWORDS:
            continue
        if re.fullmatch(r"[&/\-]", tok):
            continue
        if low in {"ii", "iii", "iv", "v", "x"}:
            continue
        if tok[:1].isupper() or tok.isupper():
            good_tokens += 1
            continue
        # allow romanized particles in names only if surrounded by capitals
        if low in {"no", "de", "da", "del", "la", "van", "von"}:
            continue
        return False
    return good_tokens >= 1

def infer_universe(title: str, raw_text: str, filepath: str) -> str:
    blob = " ".join([title, raw_text[:2000], filepath]).lower()
    return "modulo" if "modulo" in blob else "canon"


def best_kind(existing: str, candidate: str) -> str:
    return existing if KIND_PRIORITY.get(existing, 0) >= KIND_PRIORITY.get(candidate, 0) else candidate


def infer_doc_subtype(title: str) -> str:
    t = normalize_name(title).lower()
    m = DOC_PREFIX_RE.match(t)
    if not m:
        return "article"
    return m.group(1).lower()


def infer_kind_from_title(title: str) -> str:
    t = normalize_name(title)
    tl = t.lower()
    tl_no_article = _strip_leading_article(tl)

    if is_junk_title(t):
        return "Junk"
    if BATTLE_RE.search(t):
        return "Battle"
    if tl_no_article.endswith(" arc") or tl_no_article in ARC_ALIASES:
        return "Arc"
    if DOC_PREFIX_RE.match(tl_no_article):
        return "Document"
    if tl_no_article in KNOWN_LOCATIONS or any(h in tl_no_article for h in LOC_HINTS):
        return "Location"
    if tl_no_article in KNOWN_ORGS or any(h in tl_no_article for h in ORG_HINTS):
        return "Organization"
    if any(h in tl_no_article for h in TECHNIQUE_HINTS):
        return "Technique"
    if any(h in tl_no_article for h in OBJECT_HINTS):
        return "Object"
    return "Character"


def should_keep_title_as_node(title: str) -> bool:
    return infer_kind_from_title(title) not in {"Junk", "Document"}


def resolve_alias(name: str, kind: str) -> Tuple[str, str]:
    k = key(name)
    if k in ARC_ALIASES:
        return ARC_ALIASES[k], "Arc"
    if kind in {"Character", "Entity"} and k in CHARACTER_ALIASES:
        return CHARACTER_ALIASES[k], "Character"
    if k in KNOWN_LOCATIONS:
        return normalize_name(name), "Location"
    if k in KNOWN_ORGS:
        return normalize_name(name), "Organization"
    return normalize_name(name), kind


def classify_title_part(part: str) -> str:
    tl = key(part)
    tl_no_article = _strip_leading_article(tl)
    if tl_no_article in KNOWN_LOCATIONS or any(h in tl_no_article for h in LOC_HINTS):
        return "Location"
    if tl_no_article in KNOWN_ORGS or any(h in tl_no_article for h in ORG_HINTS):
        return "Organization"
    if any(h in tl_no_article for h in TECHNIQUE_HINTS):
        return "Technique"
    if any(h in tl_no_article for h in OBJECT_HINTS):
        return "Object"
    if tl_no_article in ARC_ALIASES or tl_no_article.endswith(" arc"):
        return "Arc"
    if BATTLE_RE.search(part):
        return "Battle"
    return "Character"


def is_junk_title(title: str) -> bool:
    t = key(title)
    skip_exact = {
        "file_list", "jujutsu kaisen wiki", "rememeber", "remember",
        "list of characters", "list of episodes", "list of battles & events",
        "story arcs", "volumes & chapters", "ao no sumika", "kaikai kitan",
        "lost in paradise", "specialz", "vivid vice", "give it back",
        "more than words", "yoake no uta", "ichizu", "climax☆jumping!",
        "boost on", "frost calm", "stand in the darkness", "prayer song",
        "cutie honey", "jujutsu kaisen modulo",
    }
    skip_patterns = [
        "_image gallery", "_synopsis", "blu-ray", "original soundtrack",
        "soundtrack", "promotional videos", "popularity polls", "list of ",
        "story arcs", "volumes & chapters", "wiki", "fanbook", "remember",
    ]
    if t in skip_exact:
        return True
    return any(p in t for p in skip_patterns)


def clean_text(raw: str) -> str:
    raw = re.sub(r"\[\d+\]", "", raw)
    raw = raw.replace("\r\n", "\n").replace("\r", "\n")
    return raw


def is_section_header(line: str) -> bool:
    s = line.strip()
    if not s:
        return False
    if not s.startswith("#"):
        return False
    return True


def section_name(line: str) -> str:
    return normalize_name(re.sub(r"^#+\s*", "", line).strip())


def parse_infobox(lines: Sequence[str]) -> Dict[str, List[str]]:
    out: DefaultDict[str, List[str]] = defaultdict(list)
    current_key: Optional[str] = None
    for raw in lines:
        line = raw.strip()
        if not line:
            current_key = None
            continue
        # bold mini-headings inside infobox, e.g. **Personal Description**
        if re.fullmatch(r"\*\*[^*]{1,80}\*\*", line):
            current_key = None
            continue
        # Ignore heading-like separators inside the infobox (e.g. "Professional Status")
        if re.match(r"^[A-Z][A-Za-z0-9 ,.'&\-]{1,60}$", line) and ":" not in line and not line.startswith(("-", "*", "•")):
            current_key = None
            continue
        m = re.match(r"^([A-Za-z0-9][A-Za-z0-9 \-/'&().,]+):\s*(.*)$", line)
        if m:
            current_key = normalize_name(m.group(1)).lower()
            value = normalize_name(m.group(2))
            if value:
                out[current_key].append(value)
            continue
        if current_key and line.startswith(("-", "*", "•")):
            value = normalize_name(re.sub(r"^[-*•]\s*", "", line))
            if value:
                out[current_key].append(value)
            continue
        if current_key and (line.startswith("  ") or line.startswith("\t")):
            value = normalize_name(line)
            if value:
                out[current_key].append(value)
            continue
        current_key = None
    return dict(out)


def split_listish(text: str) -> List[str]:
    raw = normalize_name(text)
    raw = raw.replace(" / ", ", ")
    raw = raw.replace(" & ", ", ")
    raw = raw.replace(" and ", ", ")
    parts = [normalize_name(x) for x in re.split(r",|;|\n", raw)]
    out = []
    for part in parts:
        part = strip_descriptor_suffix(part)
        if part and not is_garbage_name(part):
            out.append(part)
    return out


def split_doc_refs(text: str) -> List[str]:
    raw = normalize_name(text)
    raw = raw.replace(" / ", ", ")
    raw = raw.replace(" & ", ", ")
    raw = raw.replace(" and ", ", ")
    parts = [strip_descriptor_suffix(normalize_name(x)) for x in re.split(r",|;|\n", raw)]
    out: List[str] = []
    for part in parts:
        if not part:
            continue
        if is_doc_like_title(part) or re.search(r"\bchapter\b|\bepisode\b|\bvolume\b", key(part)):
            out.append(part)
    return out


def extract_battle_parts(title: str) -> List[str]:
    t = normalize_name(title)
    pieces = re.split(r"\bvs\.?\b|\bversus\b", t, flags=re.I)
    out: List[str] = []
    for piece in pieces:
        for sub in split_listish(piece):
            if sub:
                out.append(sub)
    return out


def doc_type_from_title(title: str) -> Optional[str]:
    t = key(title)
    m = DOC_PREFIX_RE.match(t)
    if not m:
        return None
    return m.group(1).lower()


def is_doc_like_title(name: str) -> bool:
    return DOC_PREFIX_RE.match(key(name)) is not None


def next_rel_for_doc_type(doc_type: str) -> Tuple[str, str]:
    return {
        "chapter": ("NEXT_CHAPTER", "PREVIOUS_CHAPTER"),
        "episode": ("NEXT_EPISODE", "PREVIOUS_EPISODE"),
        "volume": ("NEXT_VOLUME", "PREVIOUS_VOLUME"),
    }.get(doc_type, ("NEXT_CHAPTER", "PREVIOUS_CHAPTER"))


def _section_kind(heading: str) -> str:
    h = key(heading)
    if "character" in h:
        return "Character"
    if "location" in h:
        return "Location"
    if "battle" in h:
        return "Battle"
    if "technique" in h or "jujutsu" in h:
        return "Technique"
    if "arc" in h:
        return "Arc"
    return "Entity"

# -----------------------------------------------------------------------------
# Parsing
# -----------------------------------------------------------------------------

def parse_wiki_file(filepath: str) -> DocumentRecord:
    path = Path(filepath)
    title = normalize_name(path.stem)
    with open(path, "r", encoding="utf-8") as f:
        raw = clean_text(f.read())

    lines = raw.splitlines()
    sections: List[Section] = []
    current = Section(heading="Preamble")
    infobox_lines: List[str] = []
    in_infobox = False

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        m = re.match(r"^(#+)\s*(.+)$", stripped)
        if m:
            level = len(m.group(1))
            heading = normalize_name(m.group(2))

            if in_infobox:
                # Only a level-2 heading ends the infobox; deeper headings are part of it.
                if level <= 2:
                    in_infobox = False
                else:
                    # ignore nested infobox title line like "### Sukuna"
                    continue

            if level == 2 and heading.lower() == "infobox":
                if current.lines or current.heading != "Preamble":
                    sections.append(current)
                current = Section(heading="Preamble")
                in_infobox = True
                continue

            if level >= 2:
                if current.lines or current.heading != "Preamble":
                    sections.append(current)
                current = Section(heading=heading)
                continue

        if in_infobox:
            infobox_lines.append(stripped)
        else:
            current.lines.append(stripped)

    if current.lines or current.heading != "Preamble":
        sections.append(current)

    infobox = parse_infobox(infobox_lines)
    universe = infer_universe(title, raw, filepath)
    kind = infer_kind_from_title(title)
    doc_subtype = infer_doc_subtype(title)

    return DocumentRecord(
        title=title,
        filepath=str(path),
        kind=kind,
        doc_subtype=doc_subtype,
        universe=universe,
        raw_text=raw,
        infobox=infobox,
        sections=sections,
    )
def add_node(nodes: Dict[str, NodeEvidence], name: str, kind: str, doc_title: str, universe: str, source: str, alias_of: Optional[str] = None, confidence: float = 1.0) -> None:
    name = strip_descriptor_suffix(normalize_name(name))
    if is_garbage_name(name) or not is_strong_name_candidate(name):
        return
    name, kind = resolve_alias(name, kind)
    if is_garbage_name(name):
        return
    ck = key(name)
    if ck not in nodes:
        nodes[ck] = NodeEvidence(name=name, kind=kind)
    nodes[ck].kind = best_kind(nodes[ck].kind, kind)
    nodes[ck].universes.add(universe)
    nodes[ck].sources.add(source)
    nodes[ck].evidence_docs.add(doc_title)
    nodes[ck].doc_freq += 1
    nodes[ck].confidence_sum += confidence
    nodes[ck].confidence_count += 1
    if alias_of:
        nodes[ck].aliases.add(alias_of)


def add_relation(rels: List[RelationEvidence], source: str, target: str, relation: str, source_kind: str, target_kind: str, doc_title: str, section: str, universe: str, confidence: float = 0.8, evidence: str = "", extractor: str = "regex") -> None:
    source = strip_descriptor_suffix(normalize_name(source))
    target = strip_descriptor_suffix(normalize_name(target))
    if (is_garbage_name(source) and not is_doc_like_title(source)) or (is_garbage_name(target) and not is_doc_like_title(target)):
        return
    src, source_kind = resolve_alias(source, source_kind)
    tgt, target_kind = resolve_alias(target, target_kind)
    rel = relation.upper().strip()
    if rel not in RELATION_WHITELIST and rel not in DOC_RELATION_WHITELIST:
        rel = "RELATES_TO"
    rels.append(
        RelationEvidence(
            source=src,
            target=tgt,
            relation=rel,
            source_kind=source_kind,
            target_kind=target_kind,
            in_document=doc_title,
            section=section,
            universe=universe,
            confidence=confidence,
            evidence=evidence[:240],
            extractor=extractor,
        )
    )

def is_list_section(heading: str) -> bool:
    h = key(heading)
    return any(tok in h for tok in (
        "character", "location", "battle", "jujutsu", "arc guide",
        "episode guide", "new character", "adapted from", "cursed tool",
        "technique", "members", "locations", "battles & events",
    ))


def list_items(section: Section) -> List[str]:
    items: List[str] = []
    for line in section.lines:
        s = line.strip()
        if not s:
            continue
        if s.startswith("- "):
            item = normalize_name(s[2:])
            if item:
                items.append(item)
            continue
        if ":" in s:
            left, right = s.split(":", 1)
            left_n = key(left)
            if any(tok in left_n for tok in (
                "character", "location", "battle", "arc", "adapted from",
                "new character", "episode guide", "arc guide", "cursed tool",
                "technique", "adapted", "opening song", "ending song",
            )):
                for item in split_listish(right):
                    items.append(item)
                continue
    return items
def infer_section_kind(heading: str) -> str:
    h = key(heading)
    if "character" in h:
        return "Character"
    if "location" in h:
        return "Location"
    if "battle" in h:
        return "Battle"
    if "arc" in h:
        return "Arc"
    if "technique" in h or "jujutsu" in h:
        return "Technique"
    if "object" in h or "tool" in h:
        return "Object"
    return "Entity"

# -----------------------------------------------------------------------------
# Extraction
# -----------------------------------------------------------------------------

def extract_candidates(doc: DocumentRecord, known_titles: Set[str], known_semantic_titles: Set[str]) -> Tuple[Dict[str, NodeEvidence], List[RelationEvidence]]:
    nodes: Dict[str, NodeEvidence] = {}
    rels: List[RelationEvidence] = []

    full_text = doc.raw_text[:MAX_TEXT_FOR_NLP]
    title = doc.title
    universe = doc.universe

    # Title node (not for Document pages)
    if doc.kind not in {"Document", "Junk"} and should_keep_title_as_node(title):
        add_node(nodes, title, doc.kind, title, universe, "title", confidence=1.0)

    # Battle title participants
    if doc.kind == "Battle":
        add_node(nodes, title, "Battle", title, universe, "battle_title", confidence=1.0)
        parts = extract_battle_parts(title)
        for part in parts:
            add_node(nodes, part, classify_title_part(part), title, universe, "battle_part", confidence=0.95)
            add_relation(
                rels, title, part, "INVOLVES", "Battle", classify_title_part(part),
                title, "Title", universe, confidence=0.98,
                evidence=f"battle title: {title}", extractor="title",
            )

    # Arc title node
    if doc.kind == "Arc":
        add_node(nodes, title, "Arc", title, universe, "arc_title", confidence=1.0)

    # Arc matches
    doc_arcs: Set[str] = set()
    if doc.kind == "Arc":
        doc_arcs.add(title)
    for alias, canon in ARC_ALIASES.items():
        if alias in key(title) or alias in full_text.lower():
            doc_arcs.add(canon)
    for arc in doc_arcs:
        add_node(nodes, arc, "Arc", title, universe, "arc_match", confidence=0.95)
        src_canon, src_kind = resolve_alias(title, "Document" if doc.kind == "Document" else doc.kind)
        if not (doc.kind == "Arc" and key(arc) == key(title)) and key(arc) != key(src_canon):
            add_relation(
                rels, title, arc, "ABOUT_ARC", src_kind, "Arc",
                title, "Document", universe, confidence=0.92, evidence="arc reference", extractor="alias"
            )

    # Infobox-driven facts
    for k, vals in doc.infobox.items():
        for val in vals:
            if not val:
                continue
            key_l = k.lower()
            if "alias" in key_l:
                for alias in split_listish(val):
                    # alias is stored on the canonical title node if possible
                    if doc.kind not in {"Document", "Junk"}:
                        add_node(nodes, title, doc.kind, title, universe, "infobox_alias", alias_of=alias, confidence=0.9)
            elif key_l in {"arc(s)", "arc", "arc guide"}:
                for arc in split_listish(val):
                    arc_name, _ = resolve_alias(arc, "Arc")
                    add_node(nodes, arc_name, "Arc", title, universe, "infobox_arc", confidence=0.95)
                    rel = "ABOUT_ARC" if doc.kind != "Arc" else "RELATES_TO"
                    add_relation(rels, title, arc_name, rel, doc.kind, "Arc", title, "Infobox", universe, confidence=0.93, evidence=f"{k}: {val}", extractor="infobox")
            elif key_l in {"adapted from"}:
                for item in split_doc_refs(val):
                    add_relation(rels, title, item, "ADAPTED_FROM", doc.kind, "Document", title, "Infobox", universe, confidence=0.91, evidence=f"{k}: {val}", extractor="infobox")
            elif key_l in {"new character(s)", "new character", "characters", "character(s)"}:
                for item in split_listish(val):
                    item_name, item_kind = resolve_alias(strip_descriptor_suffix(item), "Character")
                    add_node(nodes, item_name, item_kind, title, universe, "infobox_character", confidence=0.92)
                    add_relation(rels, title, item_name, "INTRODUCES", doc.kind, item_kind, title, "Infobox", universe, confidence=0.88, evidence=f"{k}: {val}", extractor="infobox")
            elif key_l in {"previous", "next", "previous arc", "next arc"}:
                for item in split_listish(val):
                    item_kind = "Arc" if "arc" in key_l else "Document"
                    add_node(nodes, item, item_kind, title, universe, "infobox_sequence", confidence=0.8)
            elif key_l in {"manga debut", "anime debut", "first appearance"}:
                for item in split_doc_refs(val):
                    add_relation(rels, title, item, "FIRST_APPEARS_IN", doc.kind, "Document", title, "Infobox", universe, confidence=0.9, evidence=f"{k}: {val}", extractor="infobox")
            elif any(tok in key_l for tok in ("occupation", "species", "grade", "relatives")):
                # keep as properties / aliases, not graph nodes
                continue
            elif any(tok in key_l for tok in ("opening song", "ending song")):
                continue

    # Section-list driven extraction
    for section in doc.sections:
        heading = section.heading
        if key(heading) in SECTION_IGNORE or not is_list_section(heading):
            continue
        section_kind = infer_section_kind(heading)
        items = list_items(section)
        if not items:
            continue

        for item in items:
            item = strip_descriptor_suffix(item)
            if not is_strong_name_candidate(item):
                continue
            item_kind = section_kind
            if section_kind == "Technique":
                if any(tok in key(item) for tok in ("tool", "sword", "blade", "katana", "nail", "hammer", "rope", "finger", "shield", "gun")):
                    item_kind = "Object"
                elif any(tok in key(item) for tok in ("domain", "technique", "manipulation", "transfiguration", "shrine", "construction", "limitless")):
                    item_kind = "Technique"
                else:
                    item_kind = "Technique"
            add_node(nodes, item, item_kind, title, universe, f"section:{heading}", confidence=0.82)
            rel_name = "APPEARS_IN" if section_kind in {"Character", "Location", "Battle"} else "RELATES_TO"
            add_relation(
                rels, title, item, rel_name, doc.kind, item_kind,
                title, heading, universe,
                confidence=0.76,
                evidence=section.text[:240],
                extractor="section_list",
            )

    # Text-level explicit relation patterns
    relation_patterns = [
        (re.compile(r"([A-Z][A-Za-z0-9'’\-]+(?:\s+[A-Z][A-Za-z0-9'’\-]+){0,4})\s+(?:fights?|battles?|confronts?)\s+([A-Z][A-Za-z0-9'’\-]+(?:\s+[A-Z][A-Za-z0-9'’\-]+){0,4})", re.I), "FIGHTS", 0.9),
        (re.compile(r"([A-Z][A-Za-z0-9'’\-]+(?:\s+[A-Z][A-Za-z0-9'’\-]+){0,4})\s+(?:kills?|defeats?|slashes?|exorcises?|beats?)\s+([A-Z][A-Za-z0-9'’\-]+(?:\s+[A-Z][A-Za-z0-9'’\-]+){0,4})", re.I), "DEFEATS", 0.86),
        (re.compile(r"([A-Z][A-Za-z0-9'’\-]+(?:\s+[A-Z][A-Za-z0-9'’\-]+){0,4})\s+(?:uses?|wields?|activates?|deploys?)\s+([A-Z][A-Za-z0-9'’\-]+(?:\s+[A-Z][A-Za-z0-9'’\-]+){0,4})", re.I), "USES", 0.84),
        (re.compile(r"([A-Z][A-Za-z0-9'’\-]+(?:\s+[A-Z][A-Za-z0-9'’\-]+){0,4})\s+(?:summons?|conjures?|unleashes?)\s+([A-Z][A-Za-z0-9'’\-]+(?:\s+[A-Z][A-Za-z0-9'’\-]+){0,4})", re.I), "SUMMONS", 0.82),
        (re.compile(r"([A-Z][A-Za-z0-9'’\-]+(?:\s+[A-Z][A-Za-z0-9'’\-]+){0,4})\s+(?:joins?|belongs to|is part of)\s+(?:the\s+)?([A-Z][A-Za-z0-9'’\-]+(?:\s+[A-Z][A-Za-z0-9'’\-]+){0,4})", re.I), "BELONGS_TO", 0.8),
        (re.compile(r"([A-Z][A-Za-z0-9'’\-]+(?:\s+[A-Z][A-Za-z0-9'’\-]+){0,4})\s+(?:protects?|guards?|saves?|rescues?)\s+([A-Z][A-Za-z0-9'’\-]+(?:\s+[A-Z][A-Za-z0-9'’\-]+){0,4})", re.I), "PROTECTS", 0.8),
    ]
    for sec in doc.sections:
        if not sec.text:
            continue
        for pattern, rel_name, confidence in relation_patterns:
            for m in pattern.finditer(sec.text):
                src = strip_descriptor_suffix(normalize_name(m.group(1)))
                tgt = strip_descriptor_suffix(normalize_name(m.group(2)))
                if not is_strong_name_candidate(src) or not is_strong_name_candidate(tgt):
                    continue
                src_kind = classify_title_part(src)
                tgt_kind = classify_title_part(tgt)
                add_node(nodes, src, src_kind, title, universe, f"regex:{rel_name}", confidence=confidence)
                add_node(nodes, tgt, tgt_kind, title, universe, f"regex:{rel_name}", confidence=confidence)
                evidence = sec.text[max(0, m.start() - 60): min(len(sec.text), m.end() + 60)]
                add_relation(rels, src, tgt, rel_name, src_kind, tgt_kind, title, sec.heading, universe, confidence=confidence, evidence=evidence, extractor="regex")

    # Lightweight NER booster
    if nlp is not None and full_text.strip():
        try:
            spacy_doc = nlp(full_text)
            for ent in spacy_doc.ents:
                name = strip_descriptor_suffix(normalize_name(ent.text))
                if is_garbage_name(name) or len(name) > 80:
                    continue
                ent_kind = "Entity"
                if ent.label_ == "PERSON":
                    ent_kind = "Character"
                elif ent.label_ in {"GPE", "LOC"}:
                    ent_kind = "Location"
                elif ent.label_ == "ORG":
                    ent_kind = "Organization"
                elif ent.label_ in {"WORK_OF_ART", "EVENT"}:
                    if "arc" in key(name) or key(name) in ARC_ALIASES:
                        ent_kind = "Arc"
                    elif "vs" in key(name):
                        ent_kind = "Battle"
                    else:
                        ent_kind = "Entity"
                else:
                    continue
                # do not let NER override strong title kind
                inferred = infer_kind_from_title(name)
                if inferred != "Entity":
                    ent_kind = best_kind(inferred, ent_kind)
                add_node(nodes, name, ent_kind, title, universe, f"ner:{ent.label_}", confidence=0.6)
        except Exception as e:
            logger.warning("spaCy extraction failed for %s: %s", title, e)

    # Explicit chronology / sequence relations for doc pages
    if doc.kind == "Document":
        pass

    return nodes, rels

# -----------------------------------------------------------------------------
# Neo4j writer
# -----------------------------------------------------------------------------

class GraphStore:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run or GraphDatabase is None
        self.driver = None
        if not self.dry_run:
            self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    def close(self) -> None:
        if self.driver is not None:
            self.driver.close()

    def clear_graph(self) -> None:
        if self.dry_run or self.driver is None:
            return
        logger.info("Clearing existing graph...")
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")

    def create_constraints(self) -> None:
        if self.dry_run or self.driver is None:
            return
        cyphers = [
            "CREATE CONSTRAINT canonical_name IF NOT EXISTS FOR (n:Canonical) REQUIRE n.name IS UNIQUE",
            "CREATE CONSTRAINT document_title IF NOT EXISTS FOR (d:Document) REQUIRE d.title IS UNIQUE",
        ]
        with self.driver.session() as session:
            for cypher in cyphers:
                session.run(cypher)

    def upsert_document(self, doc: DocumentRecord) -> None:
        if self.dry_run or self.driver is None:
            return
        with self.driver.session() as session:
            session.run(
                """
                MERGE (d:Document {title: $title})
                SET d.filepath = $filepath,
                    d.kind = $kind,
                    d.doc_subtype = $doc_subtype,
                    d.universe = $universe,
                    d.updated_at = datetime(),
                    d.raw_text = $raw_text
                """,
                title=doc.title,
                filepath=doc.filepath,
                kind=doc.kind,
                doc_subtype=doc.doc_subtype,
                universe=doc.universe,
                raw_text=doc.raw_text[:8000],
            )

    def upsert_node(self, node: NodeEvidence) -> None:
        if node.kind == "Document":
            return
        label = PRIMARY_LABELS.get(node.kind, "Canonical")
        if self.dry_run or self.driver is None:
            return
        with self.driver.session() as session:
            session.run(
                f"""
                MERGE (n:Canonical {{name: $name}})
                SET n:{label},
                    n.kind = $kind,
                    n.doc_freq = $doc_freq,
                    n.confidence = $confidence,
                    n.universe = CASE
                        WHEN n.universe IS NULL OR n.universe = '' THEN $universes
                        ELSE n.universe
                    END,
                    n.updated_at = datetime()
                WITH n
                SET n.universes = reduce(acc = [], u IN coalesce(n.universes, []) + $universes |
                    CASE WHEN u IN acc THEN acc ELSE acc + u END),
                    n.sources = reduce(acc = [], s IN coalesce(n.sources, []) + $sources |
                    CASE WHEN s IN acc THEN acc ELSE acc + s END),
                    n.aliases = reduce(acc = [], a IN coalesce(n.aliases, []) + $aliases |
                    CASE WHEN a IN acc THEN acc ELSE acc + a END),
                    n.evidence_docs = reduce(acc = [], d IN coalesce(n.evidence_docs, []) + $evidence_docs |
                    CASE WHEN d IN acc THEN acc ELSE acc + d END)
                """,
                name=node.name,
                kind=node.kind,
                doc_freq=node.doc_freq,
                confidence=node.confidence,
                universes=sorted(node.universes) or ["canon"],
                sources=sorted(node.sources),
                aliases=sorted(node.aliases),
                evidence_docs=sorted(node.evidence_docs),
            )

    def upsert_document_link(self, entity_name: str, doc_title: str, rel: str = "MENTIONED_IN", props: Optional[dict] = None) -> None:
        if self.dry_run or self.driver is None:
            return
        rel = rel.upper().strip()
        if rel not in RELATION_WHITELIST:
            rel = "MENTIONED_IN"
        props = props or {}
        with self.driver.session() as session:
            session.run(
                f"""
                MERGE (e:Canonical {{name: $entity_name}})
                MERGE (d:Document {{title: $doc_title}})
                MERGE (e)-[r:{rel}]->(d)
                ON CREATE SET r.weight = 1
                ON MATCH SET r.weight = coalesce(r.weight, 0) + 1
                SET r += $props
                """,
                entity_name=entity_name,
                doc_title=doc_title,
                props=props,
            )

    def upsert_document_relation(self, src_title: str, tgt_title: str, rel: str, props: Optional[dict] = None) -> None:
        if self.dry_run or self.driver is None:
            return
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
                ON MATCH SET r.weight = coalesce(r.weight, 0) + 1
                SET r += $props
                """,
                src_title=src_title,
                tgt_title=tgt_title,
                props=props,
            )

    def upsert_relation(self, rel: RelationEvidence) -> None:
        if self.dry_run or self.driver is None:
            return
        rel_name = rel.relation if rel.relation in RELATION_WHITELIST else "RELATES_TO"
        src_label = PRIMARY_LABELS.get(rel.source_kind, "Canonical")
        tgt_label = PRIMARY_LABELS.get(rel.target_kind, "Canonical")
        with self.driver.session() as session:
            session.run(
                f"""
                MERGE (a:Canonical {{name: $src}})
                SET a:{src_label},
                    a.kind = coalesce(a.kind, $src_kind)
                WITH a
                MERGE (b:Canonical {{name: $tgt}})
                SET b:{tgt_label},
                    b.kind = coalesce(b.kind, $tgt_kind)
                WITH a, b
                MERGE (a)-[r:{rel_name}]->(b)
                ON CREATE SET r.weight = 1
                ON MATCH SET r.weight = coalesce(r.weight, 0) + 1
                SET r.confidence = coalesce(r.confidence, 0) + $confidence,
                    r.evidence = CASE WHEN $evidence = '' THEN coalesce(r.evidence, '') ELSE $evidence END,
                    r.extractor = $extractor,
                    r.in_document = $in_document,
                    r.section = $section,
                    r.universe = $universe
                """,
                src=rel.source,
                tgt=rel.target,
                src_kind=rel.source_kind,
                tgt_kind=rel.target_kind,
                confidence=rel.confidence,
                evidence=rel.evidence,
                extractor=rel.extractor,
                in_document=rel.in_document,
                section=rel.section,
                universe=rel.universe,
            )

# -----------------------------------------------------------------------------
# Build
# -----------------------------------------------------------------------------

def chronology_key(title: str) -> Optional[Tuple[str, Tuple[int, int]]]:
    t = normalize_name(title)
    m = DOC_PREFIX_RE.match(t)
    if not m:
        return None
    kind = m.group(1).lower()
    major = int(m.group(2))
    minor = int(m.group(3) or 0)
    return kind, (major, minor)

def build_graph(files_dir: Path, clear_existing: bool = False, dry_run: bool = False) -> BuildResult:
    logger.info("=" * 72)
    logger.info("JJK Graph Build v6: START")
    logger.info("  Source dir : %s", files_dir)
    logger.info("  Clear graph: %s", clear_existing)
    logger.info("  Dry run    : %s", dry_run or GraphDatabase is None)
    logger.info("  Min doc freq: %d", MIN_DOC_FREQ)
    logger.info("  NLP model  : %s", SPACY_MODEL if nlp else "disabled")
    logger.info("=" * 72)

    all_text_files = sorted(files_dir.rglob("*.txt"))
    text_files = [p for p in all_text_files if not is_junk_title(p.stem)]
    logger.info("Found %d text files (%d skipped junk)", len(text_files), len(all_text_files) - len(text_files))

    parsed_docs: List[DocumentRecord] = []
    doc_payloads: List[Tuple[DocumentRecord, Dict[str, NodeEvidence], List[RelationEvidence]]] = []
    skipped = 0
    failed: List[Tuple[str, str]] = []
    doc_entity_counter: Counter[str] = Counter()
    entity_by_key: Dict[str, NodeEvidence] = {}

    known_titles = {key(p.stem) for p in text_files}
    known_semantic_titles = {key(p.stem) for p in text_files if should_keep_title_as_node(p.stem)}

    logger.info("Parsing documents and extracting candidates...")
    for idx, fp in enumerate(text_files, start=1):
        if idx % 25 == 0 or idx == len(text_files):
            logger.info("  parsing %d/%d", idx, len(text_files))
        try:
            doc = parse_wiki_file(str(fp))
            if is_junk_title(doc.title) or not doc.raw_text.strip():
                skipped += 1
                continue
            nodes, rels = extract_candidates(doc, known_titles, known_semantic_titles)
            parsed_docs.append(doc)
            doc_payloads.append((doc, nodes, rels))
            seen: Set[str] = set()
            for ck, node in nodes.items():
                if ck in seen:
                    continue
                seen.add(ck)
                doc_entity_counter[ck] += 1
                if ck not in entity_by_key:
                    entity_by_key[ck] = NodeEvidence(name=node.name, kind=node.kind)
                entity_by_key[ck].name = node.name if len(node.name) >= len(entity_by_key[ck].name) else entity_by_key[ck].name
                entity_by_key[ck].kind = best_kind(entity_by_key[ck].kind, node.kind)
                entity_by_key[ck].universes.update(node.universes)
                entity_by_key[ck].sources.update(node.sources)
                entity_by_key[ck].aliases.update(node.aliases)
                entity_by_key[ck].evidence_docs.update(node.evidence_docs)
                entity_by_key[ck].doc_freq += 1
                entity_by_key[ck].confidence_sum += node.confidence
                entity_by_key[ck].confidence_count += 1
        except Exception as e:
            logger.warning("Failed to parse %s: %s", fp.name, e)
            failed.append((str(fp), str(e)))

    keep_keys: Set[str] = set()
    for ck, freq in doc_entity_counter.items():
        node = entity_by_key[ck]
        if node.kind in {"Document", "Junk"}:
            continue
        if freq >= MIN_DOC_FREQ or node.kind in {"Character", "Arc", "Battle", "Technique", "Location", "Organization", "Object"}:
            keep_keys.add(ck)

    logger.info("Kept %d semantic nodes after filtering", len(keep_keys))
    kind_counter = Counter(entity_by_key[k].kind for k in keep_keys)
    for kind, count in sorted(kind_counter.items(), key=lambda kv: (-kv[1], kv[0])):
        logger.info("  %-14s : %d", kind, count)

    store = GraphStore(dry_run=dry_run)
    if not store.dry_run:
        store.create_constraints()
        if clear_existing:
            store.clear_graph()

    chronology_rels = 0
    mention_links = 0
    semantic_rels = 0
    relation_counter: Counter[str] = Counter()
    universe_counter: Counter[str] = Counter()

    try:
        for doc in parsed_docs:
            universe_counter[doc.universe] += 1
            store.upsert_document(doc)

        # chronology edges
        grouped: DefaultDict[str, List[DocumentRecord]] = defaultdict(list)
        for doc in parsed_docs:
            ck = chronology_key(doc.title)
            if ck:
                grouped[ck[0]].append(doc)
        for doc_type, docs in grouped.items():
            docs = sorted(docs, key=lambda d: chronology_key(d.title)[1])  # type: ignore[index]
            next_rel, prev_rel = next_rel_for_doc_type(doc_type)
            for a, b in zip(docs, docs[1:]):
                store.upsert_document_relation(a.title, b.title, next_rel, {"source_kind": doc_type})
                chronology_rels += 1
            # store reverse links too for traversal
            for a, b in zip(docs[1:], docs[:-1]):
                store.upsert_document_relation(a.title, b.title, prev_rel, {"source_kind": doc_type})
                chronology_rels += 1

        # semantic graph
        for idx, (doc, nodes, rels) in enumerate(doc_payloads, start=1):
            for ck, node in nodes.items():
                if ck not in keep_keys:
                    continue
                store.upsert_node(node)
                store.upsert_document_link(node.name, doc.title, "MENTIONED_IN", {"universe": doc.universe})
                mention_links += 1

            for rel in rels:
                src_key = key(rel.source)
                tgt_key = key(rel.target)
                if src_key not in keep_keys and tgt_key not in keep_keys:
                    # still keep strong doc-driven relations even if nodes are singletons
                    if rel.relation not in {"ABOUT_ARC", "INVOLVES", "ADAPTED_FROM", "FIRST_APPEARS_IN", "INTRODUCES"}:
                        continue
                if rel.relation in RELATION_WHITELIST or rel.relation in DOC_RELATION_WHITELIST:
                    store.upsert_relation(rel)
                    semantic_rels += 1
                    relation_counter[rel.relation] += 1
            if idx % 25 == 0 or idx == len(doc_payloads):
                logger.info("  written %d/%d docs", idx, len(doc_payloads))
    finally:
        store.close()

    sample_nodes = [(entity_by_key[k].name, entity_by_key[k].kind) for k in list(keep_keys)[:15]]
    sample_relations = [(r.source, r.relation, r.target) for _, _, rels in doc_payloads[:5] for r in rels[:10]][:25]

    result = BuildResult(
        docs=len(parsed_docs),
        semantic_nodes=len(keep_keys),
        mention_links=mention_links,
        semantic_rels=semantic_rels,
        chronology_rels=chronology_rels,
        skipped=skipped,
        failed=failed,
        node_counter=kind_counter,
        relation_counter=relation_counter,
        universe_counter=universe_counter,
        sample_nodes=sample_nodes,
        sample_relations=sample_relations,
    )

    logger.info("=" * 72)
    logger.info("Documents written      : %d", result.docs)
    logger.info("Semantic nodes promoted: %d", result.semantic_nodes)
    logger.info("MENTIONED_IN links     : %d", result.mention_links)
    logger.info("Semantic rels          : %d", result.semantic_rels)
    logger.info("Chronology rels        : %d", result.chronology_rels)
    logger.info("Skipped                : %d", result.skipped)
    logger.info("Failed                 : %d", len(result.failed))
    logger.info("Universe mix           : %s", dict(result.universe_counter))
    logger.info("Relation mix           : %s", dict(result.relation_counter))
    logger.info("=" * 72)
    return result

# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=str, default=str(TEXT_FILES_DIR))
    parser.add_argument("--clear", action="store_true", default=CLEAR_EXISTING)
    parser.add_argument("--dry-run", action="store_true", default=DRY_RUN_DEFAULT)
    parser.add_argument("--report", type=str, default="")
    args = parser.parse_args()

    result = build_graph(Path(args.source), clear_existing=args.clear, dry_run=args.dry_run)
    if args.report:
        report_path = Path(args.report)
        report_path.write_text(
            json.dumps(
                {
                    "docs": result.docs,
                    "semantic_nodes": result.semantic_nodes,
                    "mention_links": result.mention_links,
                    "semantic_rels": result.semantic_rels,
                    "chronology_rels": result.chronology_rels,
                    "skipped": result.skipped,
                    "failed": result.failed,
                    "node_counter": dict(result.node_counter),
                    "relation_counter": dict(result.relation_counter),
                    "universe_counter": dict(result.universe_counter),
                    "sample_nodes": result.sample_nodes,
                    "sample_relations": result.sample_relations,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        logger.info("Wrote report to %s", report_path)

if __name__ == "__main__":
    main()
