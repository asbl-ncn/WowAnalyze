"""Seed configuration — which specs get Reference Profiles built first.

Kept in one small file so updating each patch is a one-file edit. Boss/encounter ids
are tier-specific: discover them with `python -m scripts.precompute --list-zones`, then
fill in CURRENT_TIER_ENCOUNTERS. Never hard-code a tier deeper in the code.
"""

from __future__ import annotations

from wowanalyze.models import Difficulty

# Specs to cover first (the maintainer's mains), by WCL spec slug.
SEED_SPECS: list[str] = [
    "elemental",  # Elemental Shaman
    "shadow",     # Shadow Priest
]

# Encounter ids for the current raid tier. Populate from `--list-zones` each patch.
CURRENT_TIER_ENCOUNTERS: list[int] = []

DEFAULT_DIFFICULTY = Difficulty.mythic

# A real report used to eyeball-validate the engine (Elemental Shaman Mythic kills).
VALIDATION_REPORT = "1rcWf3xnAbVC9QwB"
