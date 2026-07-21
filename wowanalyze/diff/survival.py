"""Dimension 4 — Survival & mechanics.

Defensive-cooldown usage on big hits, avoidable damage taken, and deaths — the stuff
that wipes raids. Diffs your damage-taken profile against players who survived.
"""

from __future__ import annotations

from wowanalyze.diff.base import ActorFightData, DiffDimension
from wowanalyze.models import Dimension, Finding, ReferenceProfile, Severity


class SurvivalDimension(DiffDimension):
    dimension = Dimension.survival

    def evaluate(
        self, data: ActorFightData, profile: ReferenceProfile
    ) -> list[Finding]:
        findings: list[Finding] = []

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
