"""Detect a parse's Build Cluster from its casts — no talent decoder needed.

Each hero tree has a handful of *signature* abilities that only that build casts
(e.g. Elemental Shaman's Stormbringer casts Tempest). We detect the build from which
signatures appear, cluster the top parses accordingly, and compare you only against
parses on your build. This is the same thin-curation spirit as abilities.py: a small
per-spec table, not a full talent model.

Specs without a table (or parses with no signature match) fall back to the blended
"all" cluster, so nothing breaks — it just isn't segmented yet.
"""

from __future__ import annotations

from wowanalyze.reference.store import PROVISIONAL_BUILD_KEY

# spec slug -> { build_key: signature abilities (any one present => that build) }.
# Order matters: the first build whose signature is present wins.
BUILD_SIGNATURES: dict[str, dict[str, set[str]]] = {
    "shaman-elemental": {
        "stormbringer": {"Tempest"},
        "farseer": {"Call of the Ancestors", "Ancestral Swiftness"},
    },
    "priest-shadow": {
        "voidweaver": {"Void Blast", "Entropic Rift"},
        "archon": {"Halo", "Perfected Form"},
    },
}

BUILD_LABELS: dict[str, str] = {
    "stormbringer": "Stormbringer",
    "farseer": "Farseer",
    "voidweaver": "Voidweaver",
    "archon": "Archon",
    PROVISIONAL_BUILD_KEY: "All builds",
}


def detect_build(spec: str | None, cast_counts: dict[str, int]) -> str:
    """Return the build key for this spec+casts, or the blended key if unknown."""
    if not spec:
        return PROVISIONAL_BUILD_KEY
    signatures = BUILD_SIGNATURES.get(spec)
    if not signatures:
        return PROVISIONAL_BUILD_KEY
    cast = set(cast_counts)
    for build_key, signature in signatures.items():
        if cast & signature:
            return build_key
    return PROVISIONAL_BUILD_KEY


def build_label(build_key: str) -> str:
    return BUILD_LABELS.get(build_key, build_key)
