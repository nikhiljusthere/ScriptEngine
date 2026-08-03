"""Configuration for ScriptEngine.

Every value here is either read by running code or absent. The previous config
module described an infrastructure that no module imported — Postgres, Redis,
Elasticsearch, a different embedding model than the one actually loaded — while
each pipeline stage hardcoded its own conflicting values. Anything added below
must have a caller.

Settings load from environment variables (prefix ``SCRIPTENGINE_``) or a `.env`
file at the repo root, and fall back to the defaults defined here.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parent.parent

Device = Literal["auto", "cuda", "cpu"]


class Settings(BaseSettings):
    """Process-wide settings, overridable by env or `.env`."""

    model_config = SettingsConfigDict(
        env_prefix="SCRIPTENGINE_",
        env_file=REPO_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── Paths ────────────────────────────────────────────────────────────────
    series_root: Path = Field(default=REPO_ROOT / "series")

    # Where finished scripts land. Defaults inside the repo so a fresh clone
    # works; set `SCRIPTENGINE_SCRIPTS_ROOT` in `.env` to file them straight
    # into the production tree instead. The path is personal, so it lives in
    # `.env` (gitignored) rather than here.
    scripts_root: Path = Field(default=REPO_ROOT / "scripts output")

    # ── Crawler ──────────────────────────────────────────────────────────────
    # Ten workers, each requesting 50 pages at a time, is what pulled One
    # Piece's 7,937 pages in three minutes with no rate limiting. Raising these
    # does not help: Fandom limits per request, so more connections are served
    # more slowly rather than in parallel. Lowering them does not protect you
    # either — what triggers a 429 is the number of requests, and batching
    # already cut that by fifty.
    crawl_concurrency: int = 10
    crawl_delay_seconds: float = 0.25
    crawl_max_retries: int = 4
    crawl_timeout_seconds: int = 30
    user_agent: str = (
        "ScriptEngine/0.1 (wiki knowledge indexer; "
        "https://github.com/nikhiljusthere/ScriptEngine)"
    )

    # ── Embedding ────────────────────────────────────────────────────────────
    embed_model: str = "BAAI/bge-large-en-v1.5"
    embed_batch_size: int = 64
    embed_max_seq_length: int = 512

    # ── Reranking ────────────────────────────────────────────────────────────
    rerank_model: str = "BAAI/bge-reranker-v2-m3"
    rerank_max_length: int = 512

    # ── GPU sharing ──────────────────────────────────────────────────────────
    # ComfyUI and a resident LLM cannot share VRAM on this machine, so the
    # embedder and reranker (~3.5 GB combined) must not squat on the GPU while
    # ComfyUI renders. They load on first use and unload after idling.
    device: Device = "auto"
    model_idle_unload_seconds: int = 300

    # ── Chunking ─────────────────────────────────────────────────────────────
    # Sections come from the MediaWiki API with explicit levels, so chunking
    # splits *within* a known section rather than guessing where one starts.
    chunk_target_words: int = 350
    chunk_overlap_words: int = 60
    chunk_min_words: int = 20

    # ── Retrieval ────────────────────────────────────────────────────────────
    vector_top_k: int = 30
    lexical_top_k: int = 30
    graph_hop_depth: int = 2
    rrf_k: int = 60
    final_top_k: int = 8

    # ── LLM (optional: summarisation and eval judging only) ──────────────────
    # Script writing happens downstream in ComfyUI. ScriptEngine only needs a
    # model for corpus-side summarisation and for scoring the eval set.
    llm_base_url: str = "http://localhost:11434/v1"
    llm_model: str = "qwen3:8b"
    llm_api_key: str = "ollama"  # Ollama ignores this; kept for API compatibility.
    llm_timeout_seconds: int = 120

    # ── API ──────────────────────────────────────────────────────────────────
    api_host: str = "127.0.0.1"
    api_port: int = 8000

    def resolved_device(self) -> str:
        """Resolve ``auto`` to a concrete torch device without importing torch eagerly."""
        if self.device != "auto":
            return self.device
        try:
            import torch

            return "cuda" if torch.cuda.is_available() else "cpu"
        except Exception:
            return "cpu"


# ── Subject resolution ───────────────────────────────────────────────────────
#
# A script is about something that happens in the work, never about the work's
# packaging. Asked for "Every Rank of Curse in Jujutsu Kaisen", entity linking
# used to return the *series* page `Jujutsu Kaisen` — an exact alias match — and
# the timeline came back as one beat from `Volume 0`.
#
# These are page-type ids as `ontology.slugify_type` produces them, not series
# names, so a default is legitimate. Any wiki that disagrees overrides both
# lists in `series/<name>/overrides.yaml`.

# Types that package the work rather than appear in it. They can still be the
# subject when the query names one outright ("Volume 5", "Episode 19"); they
# just stop winning on an incidental mention.
SUBJECT_DEMOTE_TYPES: tuple[str, ...] = (
    "series", "anime", "manga", "novel", "game", "stage_play", "music",
    "blu_ray_dvd", "volume", "chapter", "episode", "simple_box",
)

# Which kind of page a script is most likely about, best first. This is what
# makes "Every Cursed Technique of Sukuna" resolve to `Sukuna` (a character)
# rather than to `Cursed Technique`, the generic concept page that matched the
# same query with a longer alias.
SUBJECT_TYPE_PRIORITY: tuple[str, ...] = (
    "character", "character_synopsis",
    "battle", "event", "story_arcs", "arc",
    "species", "organizations", "occupation", "location",
    "technique", "item",
)


def subject_ranking(overrides: dict | None = None) -> tuple[list[str], list[str]]:
    """``(demoted_types, type_priority)`` for this wiki."""
    overrides = overrides or {}
    demote = overrides.get("subject_demote_types")
    priority = overrides.get("subject_type_priority")
    return (
        [str(t) for t in demote] if demote else list(SUBJECT_DEMOTE_TYPES),
        [str(t) for t in priority] if priority else list(SUBJECT_TYPE_PRIORITY),
    )


@dataclass(frozen=True)
class SeriesPaths:
    """Filesystem layout for a single series.

    Each series is fully self-contained: delete the folder and the series is
    gone; copy it and the series moves. Nothing is shared between series except
    the code.
    """

    name: str
    root: Path

    @property
    def raw(self) -> Path:
        """Rendered HTML, as returned by ``action=parse``."""
        return self.root / "raw"

    @property
    def wikitext(self) -> Path:
        """Raw wikitext plus per-page API metadata, one JSON file per page."""
        return self.root / "wikitext"

    @property
    def facts_db(self) -> Path:
        """SQLite: documents, sections, nodes, edges, facts, and the FTS5 index."""
        return self.root / "facts.db"

    @property
    def vectors(self) -> Path:
        """Qdrant local-mode storage directory."""
        return self.root / "vectors"

    @property
    def manifest(self) -> Path:
        """What was crawled, when, and from which wiki. Small enough to commit."""
        return self.root / "manifest.json"

    @property
    def audit(self) -> Path:
        """Extraction audit reports."""
        return self.root / "audit"

    @property
    def overrides(self) -> Path:
        """Optional per-series YAML. Series-specific handling lives here, never in code."""
        return self.root / "overrides.yaml"

    def ensure(self) -> "SeriesPaths":
        """Create the directory tree for this series."""
        for path in (self.root, self.raw, self.wikitext, self.audit):
            path.mkdir(parents=True, exist_ok=True)
        return self


def load_overrides(paths: "SeriesPaths") -> dict:
    """Read `series/<name>/overrides.yaml`.

    The only place a wiki-specific rule may live. If a fix names a series and
    sits in a `.py` file, it is in the wrong place — the next wiki breaks.
    """
    if not paths.overrides.exists():
        return {}

    import yaml

    loaded = yaml.safe_load(paths.overrides.read_text(encoding="utf-8"))
    return loaded if isinstance(loaded, dict) else {}


# A finished script is one video's worth of work, and the production tree gives
# each video a numbered folder with the script's own title on it:
#
#     Video 1 - Every Fight Mahoraga Has Ever Been In/
#         Script/  Audio/  Images/  Prompt File/  storyboard/  ...
#
# Only `Script/` is this project's business; the sibling folders are filled in
# by the rest of the pipeline.
_VIDEO_FOLDER = re.compile(r"^Video\s+(\d+)\s*-\s*(.+)$", re.IGNORECASE)

# Characters Windows forbids in a folder name. A script title is a sentence, and
# "What It's Like to be Every Rank of Curse" is fine while a colon is not.
_UNSAFE = re.compile(r'[<>:"/\\|?*]')


def script_destination(
    title: str, settings: Settings | None = None, subfolder: str = "Script"
) -> Path:
    """Where a finished script goes, and under which video number.

    Reuses the existing folder when one already carries this title, so
    rewriting a script does not create `Video 4 - ...` beside `Video 1 - ...`.
    Otherwise it takes the next free number.
    """
    settings = settings or get_settings()
    root = settings.scripts_root
    clean = _UNSAFE.sub("", title).strip().rstrip(".")

    highest = 0
    if root.exists():
        for path in root.iterdir():
            match = _VIDEO_FOLDER.match(path.name) if path.is_dir() else None
            if not match:
                continue
            highest = max(highest, int(match.group(1)))
            if match.group(2).strip().lower() == clean.lower():
                return path / subfolder / f"{clean}.md"

    return root / f"Video {highest + 1} - {clean}" / subfolder / f"{clean}.md"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


def series_paths(name: str, settings: Settings | None = None) -> SeriesPaths:
    """Return the paths for ``name``, rejecting anything that could escape the root."""
    settings = settings or get_settings()
    safe = name.strip().lower()
    if not safe or safe != os.path.basename(safe) or safe in {".", ".."}:
        raise ValueError(f"Invalid series name: {name!r}")
    return SeriesPaths(name=safe, root=settings.series_root / safe)
