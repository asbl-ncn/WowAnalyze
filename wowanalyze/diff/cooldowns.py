"""Dimension 1 — Cooldowns (MVP centerpiece).

Did you get the expected number of major-cooldown casts, and (later) were they timed
like the Top Parses? This is the highest-signal, clearest "you did X wrong" dimension.
"""

from __future__ import annotations

from wowanalyze.abilities import classify_ability
from wowanalyze.diff.base import ActorFightData, DiffDimension
from wowanalyze.models import Dimension, Finding, ReferenceProfile, Severity


class CooldownDimension(DiffDimension):
    dimension = Dimension.cooldowns

    def evaluate(
        self, data: ActorFightData, profile: ReferenceProfile
    ) -> list[Finding]:
        findings: list[Finding] = []
        minutes = data.duration_ms / 60000 if data.duration_ms else 0.0
        if minutes <= 0:
            return findings

        for metric in profile.metrics:
            if metric.dimension is not Dimension.cooldowns:
                continue
            if not metric.key.startswith("cast_count:"):
                continue

            ability = metric.key.split(":", 1)[1]
            # Guardrail: skip utility/movement/consumables/racials and defensives
            # (defensives are handled by the Survival dimension).
            if classify_ability(ability) != "dps":
                continue

            your_count = float(data.cast_counts.get(ability, 0))
            your_rate = your_count / minutes
            ref_rate = metric.median  # casts per minute

            # Only flag when you're clearly low — below the top parses' 25th percentile,
            # not merely under the median where half the field sits by definition.
            low_bar = metric.p25 if metric.p25 is not None else ref_rate
            if your_rate >= low_bar:
                continue

            missed = (ref_rate - your_rate) * minutes  # extra casts at your pull length
            if missed < 1:
                continue

            severity = (
                Severity.critical
                if missed >= 3
                else Severity.major
                if missed >= 1.5
                else Severity.minor
            )
            findings.append(
                Finding(
                    dimension=self.dimension,
                    severity=severity,
                    title=f"Low {ability} usage",
                    detail=(
                        f"You cast {ability} at {your_rate:.1f}/min ({your_count:.0f}×); "
                        f"top parses average {ref_rate:.1f}/min — about {missed:.0f} more "
                        f"over your {minutes:.1f}-min pull."
                    ),
                    your_value=round(your_rate, 1),
                    reference_value=round(ref_rate, 1),
                    unit="per-min",
                    impact_score=missed,
                )
            )

        # TODO(cooldowns): timing analysis — compare cast timestamps against Top-Parse
        # windows (on pull, burst windows, add waves), which needs phase alignment.
        # TODO(cooldowns): tag true major cooldowns vs rotational fillers/spenders, so a
        # low Lava Burst rate reads differently from a missed Ascendance.
        return findings
