"""Index-time semantic classification, for what the wiki's fields cannot say.

Deterministic rules settle most of it. `Class = Power Up` separates Kaio-ken
from Super Saiyan; a `Frieza's race` category separates Black Frieza; a
`page_type` of `planet` keeps a world out of a list of soldiers. What they
cannot settle is the handful of pages that are *structurally identical* to the
ones that belong:

    Spirit Bomb Super Saiyan   Class = Transformation, filed under Saiyans
    Great Ape                  Class = Transformation, filed under Saiyans

One is a form a Saiyan body reaches; the other is Super Saiyan with a Spirit
Bomb absorbed into it. Telling them apart needs "stacked on another form",
"caused from outside", "an energy state" — concepts no wiki has a field for.

So a local model is asked, **once, at index time**, and the answer is stored.
Three rules keep that from costing anything at query time or in trust:

* **It never runs during a query.** Retrieval reads a table. The same question
  answers the same way twice, and the eval sets stay meaningful as a regression
  guard.
* **It is asked only where the rules are uncertain** — a few hundred ability
  pages per wiki, not all 23,656. A full-corpus pass is hours of inference for
  no extra benefit.
* **It may reject or annotate, never add.** A wrong property costs precision on
  one member; it can never invent one.

Every answer carries a one-line reason, stored beside it, so a classification
that looks wrong can be argued with rather than just overridden.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from typing import Any

from scriptengine.config import SeriesPaths, Settings, get_settings, load_overrides
from scriptengine.llm.client import LLMClient, LLMUnavailable
from scriptengine.retrieve import semantics as sem
from scriptengine.stores.facts import FactStore

logger = logging.getLogger(__name__)

# Bump to invalidate every stored classification. Anything that changes what the
# model is asked — the vocabulary, the properties, the wording — changes this.
PROMPT_VERSION = "2026-08-03.2"

# The properties a question can be validated against. Booleans rather than one
# label, because "Saiyan transformation" is a conjunction: a form, intrinsic to
# a race, not granted from outside.
PROPERTIES = (
    "race_exclusive",
    "biologically_intrinsic",
    "externally_granted",
    "teachable",
    "stackable",
    "temporary",
    "requires_artifact",
    "requires_fusion",
)

SYSTEM = (
    "You classify entities from a fiction wiki. You answer with JSON only — no "
    "prose, no code fences. You are precise about the difference between what a "
    "being *is* and what a being can be *given*."
)

_TEMPLATE = """Classify this entity from the {series} wiki.

Title: {title}
Wiki categories: {categories}
Wiki class field: {klass}
Known users: {users}
Inventor/creator: {inventor}

Description:
{lead}

Answer with JSON exactly in this shape:
{{"semantic_type": "...", "properties": {{{properties}}}, "reason": "one sentence"}}

`semantic_type` must be one of: {types}.

The properties mean:
- race_exclusive: only members of one species/race/clan can ever have this.
  A form that needs a trigger — a full moon, a ritual — is still race_exclusive
  if only that race responds to the trigger.
- biologically_intrinsic: it comes from what the being is. Latent potential
  that another character draws out of them is still intrinsic: the power was
  already theirs.
- externally_granted: the power itself comes from outside and would not exist
  in the being otherwise — an artifact, a wish, a parasite, a serum, absorbing
  another being's energy. A condition that merely *triggers* something the being
  already had is not an external grant.
- teachable: another being can learn it given training or instruction.
- stackable: it can be active at the same time as another form, amplifying it,
  rather than replacing it.
- temporary: it wears off on its own.
- requires_artifact: it needs an object to obtain or maintain.
- requires_fusion: it exists only because two or more beings merged.

Judge the entity itself, not the beings who happen to have used it."""


@dataclass(frozen=True)
class Classification:
    title: str
    semantic_type: str
    properties: dict[str, bool]
    reason: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "semantic_type": self.semantic_type,
            "properties": self.properties,
            "reason": self.reason,
        }


def needs_classifying(store: FactStore, overrides: dict | None = None) -> list[str]:
    """The pages worth spending inference on.

    Ability pages only, and only where the structural signals leave the question
    open. A page the wiki calls a power-up is already settled; a page in nobody's
    race category is already settled. What is left is the ambiguous middle, and
    on Dragon Ball that is a few hundred rather than nine thousand.
    """
    from scriptengine.retrieve.roster import race_vocabulary

    races = {word.rstrip("s") for word in race_vocabulary(store)}
    wanted: list[str] = []
    rows = store.connection.execute(
        "SELECT title, page_type FROM documents ORDER BY title"
    ).fetchall()
    for row in rows:
        semantic = sem.type_from_page_type(row["page_type"], overrides)
        if semantic not in sem.ABILITY_TYPES:
            continue
        # Already decided by the wiki's own field: a power-up is not a form.
        if sem.is_power_up_only(store, row["title"]):
            continue
        # An ability filed under no race at all never reaches a race-qualified
        # answer, so classifying it buys nothing. What is left is the middle
        # where structure says "Saiyan form" and may be wrong — 400 pages on
        # Dragon Ball rather than 2,500.
        if not any(
            category.lower().rstrip("s") in races
            for category in store.categories_of(row["title"])
        ):
            continue
        wanted.append(row["title"])
    return wanted


def _context(store: FactStore, title: str) -> dict[str, str]:
    row = store.connection.execute(
        "SELECT lead, revid FROM documents WHERE title = ? COLLATE NOCASE", (title,)
    ).fetchone()
    lead = (row["lead"] if row else "") or ""

    klass = ""
    for fact in store.facts_for(title):
        label = (fact["label"] or fact["key"] or "").strip().lower()
        if label in {"class", "type", "kind"} and fact["value"]:
            klass = fact["value"]
            break

    users = store.linked_from(title, ("user", "users", "wielder", "practitioner"))
    inventor = store.linked_from(title, ("inventor", "creator", "developer"))
    return {
        "lead": lead[:1200] or "(no description)",
        "klass": klass or "(none)",
        "categories": ", ".join(store.categories_of(title)[:10]) or "(none)",
        "users": ", ".join(users[:12]) or "(none recorded)",
        "inventor": ", ".join(inventor[:4]) or "(none recorded)",
        "revid": str(row["revid"] if row else "") or "",
    }


_JSON = re.compile(r"\{.*\}", re.S)


def parse_response(text: str) -> Classification | None:
    """Read the model's JSON, tolerating the fences it was told not to use."""
    match = _JSON.search(text or "")
    if not match:
        return None
    try:
        payload = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict):
        return None

    semantic = str(payload.get("semantic_type") or "").strip().lower()
    if semantic not in sem.ALL_TYPES:
        semantic = sem.UNKNOWN

    raw = payload.get("properties")
    properties = {
        name: bool(raw.get(name))
        for name in PROPERTIES
        if isinstance(raw, dict) and name in raw
    }
    return Classification(
        title="",
        semantic_type=semantic,
        properties=properties,
        reason=str(payload.get("reason") or "").strip()[:400],
    )


def classify_page(
    client: LLMClient, store: FactStore, series: str, title: str
) -> Classification | None:
    context = _context(store, title)
    prompt = _TEMPLATE.format(
        series=series,
        title=title,
        types=", ".join(sorted(sem.ALL_TYPES)),
        properties=", ".join(f'"{name}": true|false' for name in PROPERTIES),
        **{key: value for key, value in context.items() if key != "revid"},
    )
    answer = client.complete(prompt, system=SYSTEM, temperature=0.0, max_tokens=400)
    parsed = parse_response(answer)
    if parsed is None:
        logger.warning("Unparseable classification for %r", title)
        return None
    return Classification(
        title=title,
        semantic_type=parsed.semantic_type,
        properties=parsed.properties,
        reason=parsed.reason,
    )


def classify_series(
    paths: SeriesPaths,
    settings: Settings | None = None,
    limit: int | None = None,
    refresh: bool = False,
    progress: Any = None,
) -> dict[str, Any]:
    """Classify this series' ambiguous ability pages, skipping what is current.

    Cached on `revid` and `PROMPT_VERSION`: a page already classified from the
    same revision by the same prompt is left alone, so a second run costs
    nothing and a re-crawl only pays for what changed.
    """
    settings = settings or get_settings()
    overrides = load_overrides(paths)
    client = LLMClient(settings)
    if not client.available():
        raise LLMUnavailable(
            f"No model at {client.base_url}. Start Ollama, or set "
            "SCRIPTENGINE_LLM_BASE_URL."
        )

    report = {"considered": 0, "classified": 0, "cached": 0, "failed": 0, "types": {}}
    with FactStore(paths.facts_db) as store:
        store.ensure_semantics()
        titles = needs_classifying(store, overrides)
        report["considered"] = len(titles)

        for title in titles[:limit] if limit else titles:
            revid = _context(store, title)["revid"]
            stored = store.semantics_of(title)
            current = (
                stored
                and not refresh
                and stored["prompt_version"] == PROMPT_VERSION
                and str(stored["revid"] or "") == revid
            )
            if current:
                report["cached"] += 1
                continue

            try:
                result = classify_page(client, store, paths.name, title)
            except LLMUnavailable:
                raise
            except Exception as error:  # noqa: BLE001 - one page must not stop the run
                logger.warning("Classifying %r failed: %s", title, error)
                result = None

            if result is None:
                report["failed"] += 1
                continue

            store.save_semantics(
                title=title,
                revid=int(revid) if revid.isdigit() else None,
                prompt_version=PROMPT_VERSION,
                semantic_type=result.semantic_type,
                properties=result.properties,
                reason=result.reason,
                model=settings.llm_model,
            )
            report["classified"] += 1
            report["types"][result.semantic_type] = (
                report["types"].get(result.semantic_type, 0) + 1
            )
            if progress is not None:
                progress(title, result)
            if report["classified"] % 25 == 0:
                store.commit()
        store.commit()
    return report
