"""Smoke tests for the diff engine — no network, hand-built fixtures.

These lock in the shape of the pipeline: a Dimension takes ActorFightData + a
ReferenceProfile and returns Findings. They should keep passing as the real logic
fills in behind the same interface.
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
        spec="havoc",
        boss_id=1,
        boss_name="Test Boss",
        difficulty=Difficulty.mythic,
        build=BuildCluster(key="havoc__test", hero_talent="test", label="Test"),
        patch="test",
        generated_at="2026-01-01T00:00:00+00:00",
        sample_size=100,
        metrics=metrics,
    )


def test_all_dimensions_are_priority_ordered():
    assert [d.dimension for d in ALL_DIMENSIONS] == [
        Dimension.cooldowns,
        Dimension.rotation,
        Dimension.uptime,
        Dimension.survival,
    ]


def test_missed_cooldown_produces_a_finding():
    profile = _profile(
        [
            ReferenceMetric(
                key="cast_count:Metamorphosis",
                dimension=Dimension.cooldowns,
                label="Metamorphosis casts",
                median=2.0,
            )
        ]
    )
    data = ActorFightData(duration_ms=300_000, cast_counts={"Metamorphosis": 1})

    findings = CooldownDimension().evaluate(data, profile)

    assert len(findings) == 1
    assert findings[0].dimension is Dimension.cooldowns
    assert findings[0].your_value == 1
    assert findings[0].reference_value == 2.0


def test_matching_cooldown_usage_is_clean():
    profile = _profile(
        [
            ReferenceMetric(
                key="cast_count:Metamorphosis",
                dimension=Dimension.cooldowns,
                label="Metamorphosis casts",
                median=2.0,
            )
        ]
    )
    data = ActorFightData(duration_ms=300_000, cast_counts={"Metamorphosis": 2})

    assert CooldownDimension().evaluate(data, profile) == []
