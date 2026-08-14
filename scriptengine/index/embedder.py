"""Embedding, with the GPU treated as a shared resource.

ComfyUI and a resident model cannot share VRAM on this machine, and ComfyUI is
what ultimately writes the scripts. So ScriptEngine's models are guests: they
load on first use, release the GPU after an idle period, and fall back to CPU
rather than failing when CUDA is unavailable.

The previous code hardcoded ``device="cuda"`` in five places against a CPU-only
torch build, so the first embed would have raised immediately.
"""

from __future__ import annotations

import logging
import threading
import time
from typing import Sequence

from scriptengine.config import Settings, get_settings

logger = logging.getLogger(__name__)

# BGE models are trained with an instruction prefix and lose accuracy without
# it. Passages and queries take different prefixes; using one for both collapses
# the asymmetry the model was trained to exploit.
QUERY_PREFIX = "Represent this question for searching relevant passages: "
PASSAGE_PREFIX = "Represent this passage: "

# One of each model per process, so a second request reuses the first one's
# weights instead of reading 3.6 GB off disk again.
#
# The policy this file's docstring describes -- "load on first use, release the
# GPU after an idle period" -- was only half built. `unload_if_idle()` existed
# on both classes and had no callers anywhere in the repo, and every retrieval
# entry point instead called `release_models()`, which unloads unconditionally
# the moment a request finishes. So each query paid the full load again:
# measured on a warm CUDA server, two consecutive `qa` requests took 16.8s and
# 18.9s, with no warm-up between them.
#
# Sharing the instances is what makes the idle timeout mean anything. Freeing
# the GPU for ComfyUI is still the point -- `sweep_idle()` below does it on a
# timer rather than after every single request.
_SHARED_LOCK = threading.RLock()
_SHARED: dict[str, object] = {}


def shared_embedder(settings: Settings | None = None) -> "Embedder":
    with _SHARED_LOCK:
        found = _SHARED.get("embedder")
        if found is None:
            found = Embedder(settings)
            _SHARED["embedder"] = found
        return found  # type: ignore[return-value]


def shared_reranker(settings: Settings | None = None) -> "Reranker":
    with _SHARED_LOCK:
        found = _SHARED.get("reranker")
        if found is None:
            found = Reranker(settings)
            _SHARED["reranker"] = found
        return found  # type: ignore[return-value]


def sweep_idle() -> bool:
    """Unload whichever shared model has gone idle. Returns whether any did.

    Called on a timer by the API so the GPU comes back to ComfyUI without a
    request having to arrive to trigger it.
    """
    freed = False
    with _SHARED_LOCK:
        for model in _SHARED.values():
            if model.unload_if_idle():  # type: ignore[attr-defined]
                freed = True
    return freed


class Embedder:
    """Lazily-loaded sentence-transformer with an idle timeout."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._model = None
        self._device: str | None = None
        self._last_used = 0.0
        self._lock = threading.RLock()

    # ── lifecycle ────────────────────────────────────────────────────────────

    @property
    def device(self) -> str:
        if self._device is None:
            self._device = self.settings.resolved_device()
        return self._device

    def load(self):
        with self._lock:
            if self._model is None:
                from sentence_transformers import SentenceTransformer

                logger.info(
                    "loading %s on %s", self.settings.embed_model, self.device
                )
                started = time.monotonic()
                self._model = SentenceTransformer(
                    self.settings.embed_model, device=self.device
                )
                self._model.max_seq_length = self.settings.embed_max_seq_length
                logger.info("loaded in %.1fs", time.monotonic() - started)
            self._last_used = time.monotonic()
            return self._model

    def unload(self) -> bool:
        """Release the model and its VRAM. Returns whether anything was freed."""
        with self._lock:
            if self._model is None:
                return False
            self._model = None
            if self.device == "cuda":
                try:
                    import torch

                    torch.cuda.empty_cache()
                except Exception:  # pragma: no cover - best effort
                    pass
            logger.info("unloaded %s", self.settings.embed_model)
            return True

    def unload_if_idle(self) -> bool:
        """Free the GPU if nothing has used the model recently."""
        timeout = self.settings.model_idle_unload_seconds
        if not timeout or self._model is None:
            return False
        if time.monotonic() - self._last_used < timeout:
            return False
        return self.unload()

    @property
    def dimensions(self) -> int:
        model = self.load()
        # Renamed in sentence-transformers 5; the old name still works but warns.
        getter = getattr(model, "get_embedding_dimension", None) or (
            model.get_sentence_embedding_dimension
        )
        return int(getter())

    # ── encoding ─────────────────────────────────────────────────────────────

    def encode_passages(
        self, texts: Sequence[str], show_progress: bool = False
    ) -> list[list[float]]:
        return self._encode(texts, PASSAGE_PREFIX, show_progress)

    def encode_query(self, text: str) -> list[float]:
        return self._encode([text], QUERY_PREFIX, False)[0]

    def _encode(
        self, texts: Sequence[str], prefix: str, show_progress: bool
    ) -> list[list[float]]:
        if not texts:
            return []
        model = self.load()
        vectors = model.encode(
            [prefix + text for text in texts],
            batch_size=self.settings.embed_batch_size,
            show_progress_bar=show_progress,
            normalize_embeddings=True,   # required for cosine similarity
            convert_to_numpy=True,
        )
        self._last_used = time.monotonic()
        return [vector.tolist() for vector in vectors]


class Reranker:
    """Cross-encoder rerank, under the same load/unload discipline."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._model = None
        self._last_used = 0.0
        self._lock = threading.RLock()

    @property
    def device(self) -> str:
        return self.settings.resolved_device()

    def load(self):
        with self._lock:
            if self._model is None:
                from sentence_transformers import CrossEncoder

                logger.info(
                    "loading %s on %s", self.settings.rerank_model, self.device
                )
                self._model = CrossEncoder(
                    self.settings.rerank_model,
                    device=self.device,
                    max_length=self.settings.rerank_max_length,
                )
            self._last_used = time.monotonic()
            return self._model

    def unload(self) -> bool:
        with self._lock:
            if self._model is None:
                return False
            self._model = None
            if self.device == "cuda":
                try:
                    import torch

                    torch.cuda.empty_cache()
                except Exception:  # pragma: no cover - best effort
                    pass
            return True

    def unload_if_idle(self) -> bool:
        timeout = self.settings.model_idle_unload_seconds
        if not timeout or self._model is None:
            return False
        if time.monotonic() - self._last_used < timeout:
            return False
        return self.unload()

    def score(self, query: str, passages: Sequence[str]) -> list[float]:
        """Score each passage against the query.

        A cross-encoder reads the query and the passage together, which is why
        it outranks the bi-encoder that retrieved them — and why it is only ever
        run over a shortlist.
        """
        if not passages:
            return []
        model = self.load()
        # Long passages are truncated anyway; trimming first keeps batches even.
        pairs = [(query, passage[:2000]) for passage in passages]
        scores = model.predict(pairs, batch_size=32, show_progress_bar=False)
        self._last_used = time.monotonic()
        return [float(score) for score in scores]
