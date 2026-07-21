"""Smoke tests for the diff engine — no network, hand-built fixtures.

Reference cast metrics are stored as casts-per-minute; the cooldown dimension compares
your rate against the top parses' 25th percentile and skips guardrail-classified
abilities (utility/consumable/defensive).
"""

from __future__ import annotations

from wowanalyze.diff import ALL_DIMENSIONS
from wowanalyze.diff.base import ActorFightData
from wowanalyze.diff.cooldowns import CooldownDimension
from wowanalyze.models import (
    BuildCluster,
    Difficulty,
    Dimension,
    ReferenceMetric,
    ReferenceProfile,
)


def _profile(metrics: list[ReferenceMetric]) -> ReferenceProfile:
    return ReferenceProfile(
        spec="shaman-elemental",
        boss_id=1,
        boss_name="Test Boss",
        difficulty=Difficulty.mythic,
        build=BuildCluster(key="all", hero_talent="mixed", label="all"),
        patch="test",
        generated_at="2026-01-01T00:00:00+00:00",
        sample_size=100,
        metrics=metrics,
    )


def _metric(ability: str, median: float, p25: float) -> ReferenceMetric:
    return ReferenceMetric(
        key=f"cast_count:{ability}",
        dimension=Dimension.cooldowns,
        label=ability,
        median=median,
        p25=p25,
        unit="per-min",
    )


def test_all_dimensions_are_priority_ordered():
    assert [d.dimension for d in ALL_DIMENSIONS] == [
        Dimension.cooldowns,
        Dimension.rotation,
        Dimension.uptime,
        Dimension.survival,
    ]


def test_low_cast_rate_produces_a_finding():
    profile = _profile([_metric("Lava Burst", median=10.0, p25=9.0)])
    # 20 casts over 5 min = 4/min, well below the 9/min p25.
    data = ActorFightData(duration_ms=300_000, cast_counts={"Lava Burst": 20})

    findings = CooldownDimension().evaluate(data, profile)

    assert len(findings) == 1
    assert findings[0].reference_value == 10.0
    assert findings[0].your_value == 4.0


def test_on_pace_is_clean():
    profile = _profile([_metric("Lava Burst", median=10.0, p25=9.0)])
    # 50 casts over 5 min = 10/min, right on the median.
    data = ActorFightData(duration_ms=300_000, cast_counts={"Lava Burst": 50})

    assert CooldownDimension().evaluate(data, profile) == []


def test_guardrail_ability_is_never_flagged():
    # Spiritwalker's Grace is utility — must not produce a cooldown finding even at 0.
    profile = _profile([_metric("Spiritwalker's Grace", median=1.0, p25=1.0)])
    data = ActorFightData(duration_ms=300_000, cast_counts={})

    assert CooldownDimension().evaluate(data, profile) == []
