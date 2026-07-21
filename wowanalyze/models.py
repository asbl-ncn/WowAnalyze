"""Core data model.

The load-bearing idea: **every analysis is a list of `Target`s**. One Target is single
-player coaching; two is a side-by-side diff; N is raid-wide. Nothing downstream cares
about the count. See CONTEXT.md for the vocabulary.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class Role(str, Enum):
    dps = "dps"
    healer = "healer"
    tank = "tank"


class Difficulty(str, Enum):
    normal = "normal"
    heroic = "heroic"
    mythic = "mythic"


class Dimension(str, Enum):
    """The four axes of analysis, in MVP priority order."""

    cooldowns = "cooldowns"
    rotation = "rotation"
    uptime = "uptime"
    survival = "survival"


class Severity(str, Enum):
    critical = "critical"
    major = "major"
    minor = "minor"
    info = "info"


# --- Inputs -----------------------------------------------------------------


class Target(BaseModel):
    """One `(Report, Fight, Actor)` — "this player, on this pull". The atomic unit."""

    report_code: str
    fight_id: int
    actor_id: int = Field(description="WCL `source id`, unique within the report")
    character_name: str | None = None
    spec: str | None = None


# --- Reference (derived, precomputed, committed as JSON) ---------------------


class BuildCluster(BaseModel):
    """A group of Top Parses that play the same way (hero tree + key talents)."""

    key: str = Field(description="stable id, e.g. 'havoc__aldrachi__single-target'")
    hero_talent: str
    label: str
    talent_hash: str | None = None
    sample_size: int = 0


class ReferenceMetric(BaseModel):
    """One expected value distilled from Top Parses, with spread for tolerance."""

    key: str = Field(description="e.g. 'cast_count:Eye Beam' or 'uptime:Immolation Aura'")
    dimension: Dimension
    label: str
    median: float
    p25: float | None = None
    p75: float | None = None
    unit: str = "count"


class ReferenceProfile(BaseModel):
    """Aggregated behavior of the Top Parses for one (Spec, Build, Boss, Difficulty)."""

    spec: str
    boss_id: int
    boss_name: str
    difficulty: Difficulty
    build: BuildCluster
    patch: str
    generated_at: str = Field(description="ISO timestamp; stamped by precompute")
    sample_size: int
    metrics: list[ReferenceMetric] = Field(default_factory=list)


# --- Outputs (Findings) ------------------------------------------------------


class Finding(BaseModel):
    """One detected gap between a Target and its Reference Profile, on one Dimension."""

    dimension: Dimension
    severity: Severity
    title: str
    detail: str
    your_value: float | None = None
    reference_value: float | None = None
    unit: str = "count"
    impact_score: float = Field(
        default=0.0,
        description="ranks Findings; later ranks players raid-wide",
    )


class TargetAnalysis(BaseModel):
    target: Target
    boss_name: str | None = None
    build: BuildCluster | None = None
    findings: list[Finding] = Field(default_factory=list)


class AnalysisResult(BaseModel):
    """The full result for a list of Targets — one TargetAnalysis each."""

    report_code: str
    analyses: list[TargetAnalysis] = Field(default_factory=list)


# --- Report browsing (for the UI pickers) -----------------------------------


class FightSummary(BaseModel):
    fight_id: int
    boss_id: int
    boss_name: str
    difficulty: Difficulty | None = None
    kill: bool
    duration_ms: int
    participant_ids: list[int] = Field(
        default_factory=list,
        description="source ids present in this fight; the UI filters actors by these",
    )


class ActorSummary(BaseModel):
    actor_id: int
    name: str
    class_name: str | None = None
    spec: str | None = None
    role: Role | None = None


class ReportSummary(BaseModel):
    """What `/api/report/{code}` returns so the frontend can offer Pull/Actor pickers."""

    report_code: str
    title: str | None = None
    fights: list[FightSummary] = Field(default_factory=list)
    actors: list[ActorSummary] = Field(default_factory=list)
