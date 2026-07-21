"""Test the guardrail ability classifier."""

from __future__ import annotations

from wowanalyze.abilities import classify_ability


def test_rotational_abilities_are_dps():
    assert classify_ability("Lava Burst") == "dps"
    assert classify_ability("Lightning Bolt") == "dps"
    assert classify_ability("Stormkeeper") == "dps"


def test_utility_and_consumables_ignored():
    assert classify_ability("Spiritwalker's Grace") == "ignore"
    assert classify_ability("Ghost Wolf") == "ignore"
    assert classify_ability("Silvermoon Health Potion") == "ignore"  # matches "Potion"
    assert classify_ability("Algari Mana Potion") == "ignore"


def test_racials_ignored():
    assert classify_ability("Blood Fury") == "ignore"
    assert classify_ability("Berserking") == "ignore"


def test_defensives_routed():
    assert classify_ability("Astral Shift") == "defensive"
    assert classify_ability("Barkskin") == "defensive"
