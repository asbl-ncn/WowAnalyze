"""The guardrail layer: classify abilities so the diff doesn't treat everything as a
DPS cooldown.

This is deliberately a *thin*, cross-spec list — utility/movement/consumables/racials
that should never be a throughput finding, plus defensives that belong in Survival, not
Cooldowns. It is NOT per-spec rotation logic. Add entries as new noise shows up; keep it
small. Everything not listed defaults to "dps" and stays data-driven.
"""

from __future__ import annotations

# Cast, but never a throughput finding: movement, utility, buffs, totems you drop once.
IGNORE: frozenset[str] = frozenset(
    {
        # Shaman utility / movement / buffs
        "Ghost Wolf",
        "Gust of Wind",
        "Spiritwalker's Grace",
        "Nature's Swiftness",
        "Skyfury",
        "Wind Rush Totem",
        "Tremor Totem",
        "Earthbind Totem",
        "Capacitor Totem",
        "Wind Shear",
        "Purge",
        "Hex",
        "Cleanse Spirit",
        "Far Sight",
        "Astral Recall",
        # Seen in-log as trinket/encounter proc casts (not player rotation)
        "Nullsight",
        "Light's Potential",
    }
)

# Substrings that mark a consumable / non-rotational cast regardless of spec.
IGNORE_PATTERNS: tuple[str, ...] = (
    "Potion",
    "Healthstone",
    "Flask",
    "Bandage",
    "Drums of",
    "Rune of",
)

# Race abilities — race varies across the reference population, so never flag "missed".
RACIALS: frozenset[str] = frozenset(
    {
        "Blood Fury",
        "Berserking",
        "Fireblood",
        "Ancestral Call",
        "Arcane Torrent",
        "Stoneform",
        "Bag of Tricks",
        "Gift of the Naaru",
        "Shadowmeld",
        "Light's Judgment",
        "Rocket Barrage",
        "Will to Survive",
    }
)

# Defensives — route to Survival ("did you use it?"), never a throughput finding.
DEFENSIVES: frozenset[str] = frozenset(
    {
        "Astral Shift",  # Shaman
        "Barkskin",
        "Survival Instincts",
        "Dispersion",
        "Desperate Prayer",
        "Fade",
        "Cloak of Shadows",
        "Evasion",
        "Feint",
        "Icebound Fortitude",
        "Anti-Magic Shell",
        "Vampiric Blood",
        "Divine Shield",
        "Divine Protection",
        "Shield Wall",
        "Die by the Sword",
        "Ice Block",
        "Ice Barrier",
        "Blur",
        "Darkness",
        "Netherwalk",
        "Fortifying Brew",
        "Dampen Harm",
        "Diffuse Magic",
        "Aspect of the Turtle",
        "Exhilaration",
    }
)


def classify_ability(name: str) -> str:
    """Return "defensive", "ignore", or "dps"."""
    if name in DEFENSIVES:
        return "defensive"
    if name in IGNORE or name in RACIALS:
        return "ignore"
    if any(pattern in name for pattern in IGNORE_PATTERNS):
        return "ignore"
    return "dps"
