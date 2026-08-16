"""Models stay loaded between requests, and still come back to ComfyUI.

The GPU is shared with ComfyUI, so `release_models()` unloaded both models after
every single request. That made the idle timeout the file's own docstring
describes -- "load on first use, release the GPU after an idle period" --
unreachable: `unload_if_idle()` existed on both classes and had no caller
anywhere in the repo.

Measured cost on a warm CUDA server: two consecutive `qa` requests at 16.8s and
18.9s, no warm-up, against 0.07s for a roster request that touches no model.
"""

from __future__ import annotations

import time

from scriptengine.config import Settings
from scriptengine.index import embedder as E


class _FakeModel:
    def __init__(self) -> None:
        self.loads = 0


class _Counting(E.Embedder):
    """An Embedder that records loads instead of reading 1.3 GB off disk."""

    def __init__(self, settings: Settings) -> None:
        super().__init__(settings)
        self.loads = 0

    def load(self):  # type: ignore[override]
        with self._lock:
            if self._model is None:
                self._model = _FakeModel()
                self.loads += 1
            self._last_used = time.monotonic()
            return self._model


def test_a_second_request_does_not_reload_the_model():
    model = _Counting(Settings(model_idle_unload_seconds=300))
    model.load()
    model.load()
    model.load()
    assert model.loads == 1, "the model reloaded on a request that should reuse it"


def test_release_keeps_a_model_that_was_just_used():
    """`release_models()` after every request is what made queries slow."""
    model = _Counting(Settings(model_idle_unload_seconds=300))
    model.load()
    assert model.unload_if_idle() is False
    assert model._model is not None


def test_an_idle_model_is_released_for_comfyui():
    """The GPU still goes back, on a timer rather than per request.

    The clock is wound back rather than slept through: the setting is an int
    number of seconds, so the smallest honest timeout would make this test take
    a second for nothing.
    """
    model = _Counting(Settings(model_idle_unload_seconds=300))
    model.load()
    model._last_used = time.monotonic() - 301
    assert model.unload_if_idle() is True
    assert model._model is None


def test_a_zero_timeout_keeps_the_model_resident():
    """0 disables the sweep rather than unloading constantly."""
    model = _Counting(Settings(model_idle_unload_seconds=0))
    model.load()
    model._last_used = time.monotonic() - 10_000
    assert model.unload_if_idle() is False
    assert model._model is not None


def test_the_shared_instances_are_one_per_process():
    first, second = E.shared_embedder(), E.shared_embedder()
    assert first is second
    assert E.shared_reranker() is E.shared_reranker()
    assert first is not E.shared_reranker()


def test_sweep_reports_whether_it_freed_anything():
    """The API's timer thread calls this; it must never raise."""
    assert E.sweep_idle() in (True, False)
