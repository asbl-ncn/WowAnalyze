"""Orchestration: a list of Targets -> an AnalysisResult.

This is the single entry point the API calls. It is deliberately count-agnostic: one
Target (solo coaching), two (side-by-side), or N (raid-wide) all flow through the same
loop. That is the whole point of the Target model.
"""

from __future__ import annotations

from wowanalyze.diff import ALL_DIMENSIONS
from wowanalyze.diff.base import ActorFightData
from wowanalyze.models import (
    AnalysisResult,
    Difficulty,
    Finding,
    ObservedPlay,
    ReferenceProfile,
    Target,
    TargetAnalysis,
)
from wowanalyze.reference.store import PROVISIONAL_BUILD_KEY, load_profile

# WCL raid difficulty ids.
_DIFFICULTY_BY_ID = {3: Difficulty.normal, 4: Difficulty.heroic, 5: Difficulty.mythic}


def analyze_actor_data(
    data: ActorFightData, profile: ReferenceProfile
) -> list[Finding]:
    """Run every Dimension over one Target's data and return ranked Findings."""
    findings: list[Finding] = []
    for dimension in ALL_DIMENSIONS:
        findings.extend(dimension.evaluate(data, profile))

    # TODO(guardrails): pass findings through the guardrail layer here to drop/adjust
    # misleading ones (add-padding, proc-window sanity) before ranking.

    findings.sort(key=lambda f: f.impact_score, reverse=True)
    return findings


async def analyze_targets(
    targets: list[Target],
    *,
    fetch_actor_data,  # async (Target) -> ActorFightData  (injected: WCL client)
    difficulty: Difficulty = Difficulty.mythic,
) -> AnalysisResult:
    """Analyze each Target against its matching Reference Profile.

    `fetch_actor_data` is injected so the engine never imports the WCL client directly
    and stays unit-testable with fixtures.
    """
    if not targets:
        raise ValueError("analyze_targets requires at least one Target")

    report_code = targets[0].report_code
    result = AnalysisResult(report_code=report_code)

    for target in targets:
        data = await fetch_actor_data(target)

        profile = None
        if target.spec and data.boss_id:
            profile = load_profile(
                spec=target.spec,
                difficulty=_DIFFICULTY_BY_ID.get(data.difficulty_id) or difficulty,
                boss_id=data.boss_id,
                build_key=PROVISIONAL_BUILD_KEY,
            )

        analysis = TargetAnalysis(target=target)
        # Always surface what the player actually did, reference or not.
        analysis.observed = ObservedPlay(
            duration_ms=data.duration_ms, cast_counts=data.cast_counts
        )
        if profile is None:
            # No reference yet (spec/boss/build not precomputed) — say so, don't guess.
            analysis.findings = []
            analysis.boss_name = None
        else:
            analysis.boss_name = profile.boss_name
            analysis.build = profile.build
            analysis.findings = analyze_actor_data(data, profile)

        result.analyses.append(analysis)

    return result
