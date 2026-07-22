"""Test build detection from cast signatures."""

from __future__ import annotations

from wowanalyze.builds import detect_build


def test_elemental_stormbringer_from_tempest():
    assert detect_build("shaman-elemental", {"Tempest": 12, "Lava Burst": 30}) == "stormbringer"


def test_elemental_farseer_from_ancestors():
    assert (
        detect_build("shaman-elemental", {"Call of the Ancestors": 3, "Lava Burst": 30})
        == "farseer"
    )


def test_no_signature_falls_back_to_all():
    assert detect_build("shaman-elemental", {"Lava Burst": 30}) == "all"


def test_unknown_spec_falls_back_to_all():
    assert detect_build("warrior-arms", {"Mortal Strike": 20}) == "all"


def test_no_spec_falls_back_to_all():
    assert detect_build(None, {"Tempest": 5}) == "all"
