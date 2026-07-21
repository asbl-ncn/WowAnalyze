"""Test the REPORT_SUMMARY -> ReportSummary mapping with a canned WCL response.

No network: `map_report_summary` is a pure function, so we feed it a realistic
GraphQL payload and assert the shape the frontend pickers rely on.
"""

from __future__ import annotations

import pytest

from wowanalyze.models import Difficulty
from wowanalyze.wcl.report import map_report_summary

_SAMPLE = {
    "reportData": {
        "report": {
            "title": "Guild Raid Night",
            "fights": [
                {
                    "id": 1,
                    "encounterID": 3009,
                    "name": "Test Boss",
                    "difficulty": 5,
                    "kill": False,
                    "startTime": 1000,
                    "endTime": 121000,
                },
                {
                    "id": 2,
                    "encounterID": 3009,
                    "name": "Test Boss",
                    "difficulty": 5,
                    "kill": True,
                    "startTime": 200000,
                    "endTime": 380000,
                },
            ],
            "masterData": {
                "actors": [
                    {"id": 11, "name": "Zaphod", "subType": "Shaman"},
                    {"id": 12, "name": "Trillian", "subType": "Priest"},
                ]
            },
        }
    }
}


def test_maps_fights_and_actors():
    summary = map_report_summary("abc123", _SAMPLE)

    assert summary.report_code == "abc123"
    assert summary.title == "Guild Raid Night"
    assert len(summary.fights) == 2
    assert len(summary.actors) == 2

    wipe, kill = summary.fights
    assert wipe.kill is False
    assert kill.kill is True
    assert kill.boss_id == 3009
    assert kill.difficulty is Difficulty.mythic
    assert kill.duration_ms == 180000  # 380000 - 200000

    assert summary.actors[0].name == "Zaphod"
    assert summary.actors[0].actor_id == 11


def test_missing_report_raises():
    with pytest.raises(ValueError, match="not found"):
        map_report_summary("nope", {"reportData": {"report": None}})


def test_unknown_difficulty_is_none():
    payload = {
        "reportData": {
            "report": {
                "title": "x",
                "fights": [
                    {
                        "id": 1,
                        "encounterID": 1,
                        "name": "B",
                        "difficulty": 99,
                        "kill": True,
                        "startTime": 0,
                        "endTime": 1000,
                    }
                ],
                "masterData": {"actors": []},
            }
        }
    }
    summary = map_report_summary("x", payload)
    assert summary.fights[0].difficulty is None
