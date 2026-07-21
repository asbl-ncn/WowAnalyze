"""FastAPI app, deployed as a Vercel Python serverless function.

This is the only always-on piece. It holds the WCL secret, browses reports for the
UI's pickers, and runs the live analysis. Heavy reference-building happens offline
(see scripts/precompute.py), so these handlers stay cheap.
"""

from __future__ import annotations

import sys
from pathlib import Path

# The shared engine lives at the repo root; make it importable inside the Vercel bundle.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, HTTPException  # noqa: E402
from pydantic import BaseModel  # noqa: E402

from wowanalyze.analyze import analyze_targets  # noqa: E402
from wowanalyze.config import get_settings  # noqa: E402
from wowanalyze.models import (  # noqa: E402
    AnalysisResult,
    Difficulty,
    ReportSummary,
    Target,
)
from wowanalyze.wcl import WCLClient, WCLError  # noqa: E402
from wowanalyze.wcl.actor import fetch_actor_fight_data  # noqa: E402
from wowanalyze.wcl.report import fetch_report_summary  # noqa: E402

app = FastAPI(title="WowAnalyze", version="0.1.0")


@app.get("/api/health")
async def health() -> dict[str, object]:
    return {
        "status": "ok",
        "wcl_credentials": get_settings().has_wcl_credentials,
    }


@app.get("/api/report/{code}", response_model=ReportSummary)
async def get_report(code: str) -> ReportSummary:
    """List a report's Pulls and Actors so the frontend can offer pickers."""
    try:
        return await fetch_report_summary(code, WCLClient())
    except ValueError as exc:
        # Report not found / not accessible.
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except WCLError as exc:
        # WCL rejected the query, or credentials are missing/invalid.
        raise HTTPException(status_code=502, detail=str(exc)) from exc


class AnalyzeRequest(BaseModel):
    targets: list[Target]
    difficulty: Difficulty = Difficulty.mythic


@app.post("/api/analyze", response_model=AnalysisResult)
async def analyze(req: AnalyzeRequest) -> AnalysisResult:
    """Analyze one or more Targets (solo, side-by-side, or raid-wide — same path)."""
    if not req.targets:
        raise HTTPException(status_code=400, detail="Provide at least one target.")

    client = WCLClient()

    async def fetch_actor_data(target: Target):
        # Casts wired now; buffs/debuffs/deaths follow as later Dimensions land.
        return await fetch_actor_fight_data(
            target.report_code, target.fight_id, target.actor_id, client
        )

    try:
        return await analyze_targets(
            req.targets,
            fetch_actor_data=fetch_actor_data,
            difficulty=req.difficulty,
        )
    except WCLError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
