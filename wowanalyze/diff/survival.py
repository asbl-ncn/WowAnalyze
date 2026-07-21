"""Dimension 4 — Survival & mechanics.

Defensive-cooldown usage on big hits, avoidable damage taken, and deaths — the stuff
that wipes raids. Diffs your damage-taken profile against players who survived.
"""

from __future__ import annotations

from wowanalyze.abilities import classify_ability
from wowanalyze.diff.base import ActorFightData, DiffDimension
from wowanalyze.models import Dimension, Finding, ReferenceProfile, Severity


class SurvivalDimension(DiffDimension):
    dimension = Dimension.survival

    def evaluate(
        self, data: ActorFightData, profile: ReferenceProfile
    ) -> list[Finding]:
        findings: list[Finding] = []

        # Defensives the top parses used but you didn't — correct framing (survival,
        # not throughput). Reads cast_count metrics regardless of their stored tag.
        for metric in profile.metrics:
            if not metric.key.startswith("cast_count:"):
                continue
            ability = metric.key.split(":", 1)[1]
            if classify_ability(ability) != "defensive":
                continue
            if metric.median <= 0:
                continue
            if data.cast_counts.get(ability, 0) == 0:
                findings.append(
                    Finding(
                        dimension=self.dimension,
                        severity=Severity.minor,
                        title=f"No {ability} used",
                        detail=(
                            f"Top parses used {ability} on this fight; you didn't cast "
                            f"it. Check whether a defensive was available for the big hits."
                        ),
                        your_value=0.0,
                        reference_value=None,
                        unit="count",
                        impact_score=2.0,
                    )
                )

        # A death is always worth surfacing — it's the most expensive mistake there is.
        if data.deaths > 0:
            findings.append(
                Finding(
                    dimension=self.dimension,
                    severity=Severity.critical,
                    title=f"Died {data.deaths}× this pull",
                    detail=(
                        "The Top Parses survived. Deaths cost far more than any rotation "
                        "gap. TODO: attribute each death to the killing ability and check "
                        "whether a defensive was available."
                    ),
                    your_value=float(data.deaths),
                    reference_value=0.0,
                    unit="count",
                    impact_score=100.0 * data.deaths,
                )
            )

        # TODO(survival): avoidable-damage-taken vs reference, and defensive-CD usage on
        # scripted big hits (needs the same phase/timeline data as cooldown timing).
        return findings
