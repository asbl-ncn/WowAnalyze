"""Seed configuration — which specs get Reference Profiles built first.

Kept in one small file so updating each patch is a one-file edit. Boss/encounter ids
are tier-specific: discover them with `python -m scripts.precompute --list-zones`, then
fill in CURRENT_TIER_ENCOUNTERS. Never hard-code a tier deeper in the code.
"""

from __future__ import annotations

from wowanalyze.models import Difficulty

# Specs to cover first (the maintainer's mains). Slugs are class-qualified
# ("<class>-<spec>", lowercased) so e.g. Resto Druid and Resto Shaman never collide.
SEED_SPECS: list[str] = [
    "shaman-elemental",  # Elemental Shaman
    "priest-shadow",     # Shadow Priest
]

# WCL rankings need the exact className + specName. Slug -> (className, specName).
# The slug is what the reference JSON is filed under and what the UI sends.
SPEC_TO_CLASS: dict[str, tuple[str, str]] = {
    "shaman-elemental": ("Shaman", "Elemental"),
    "priest-shadow": ("Priest", "Shadow"),
}

# Encounter ids for the current raid tier (Manaforge Omega, Mythic), taken from a
# real report. Refresh each tier via `python -m scripts.precompute --list-zones`.
CURRENT_TIER_ENCOUNTERS: list[int] = [
    3176,  # Imperator Averzian
    3177,  # Vorasius
    3178,  # Vaelgor & Ezzorak
    3179,  # Fallen-King Salhadaar
    3180,  # Lightblinded Vanguard
    3181,  # Crown of the Cosmos
]

DEFAULT_DIFFICULTY = Difficulty.mythic

# A real report used to eyeball-validate the engine (Elemental Shaman Mythic kills).
VALIDATION_REPORT = "1rcWf3xnAbVC9QwB"
