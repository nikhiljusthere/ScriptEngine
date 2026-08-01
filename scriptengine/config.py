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

    # ── Crawler ──────────────────────────────────────────────────────────────
    # Concurrency and pacing carried over from the original crawler, which ran
    # ~850 pages against Fandom without tripping rate limits.
    crawl_concurrency: int = 10
    crawl_delay_seconds: float = 0.2
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
