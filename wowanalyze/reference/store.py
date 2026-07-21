"""Read/write Reference Profiles as JSON under `data/reference/`.

The repo is the database. Layout is stable and human-browsable:

    data/reference/<spec>/<difficulty>/<bossId>__<buildKey>.json

The precompute writes these; the live API only reads them.
"""

from __future__ import annotations

from pathlib import Path

from wowanalyze.config import get_settings
from wowanalyze.models import Difficulty, ReferenceProfile


def profile_path(
    spec: str, difficulty: Difficulty, boss_id: int, build_key: str
) -> Path:
    root = get_settings().reference_dir
    safe_build = build_key.replace("/", "-")
    return root / spec / difficulty.value / f"{boss_id}__{safe_build}.json"


def save_profile(profile: ReferenceProfile) -> Path:
    path = profile_path(
        profile.spec, profile.difficulty, profile.boss_id, profile.build.key
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(profile.model_dump_json(indent=2), encoding="utf-8")
    return path


def load_profile(
    spec: str, difficulty: Difficulty, boss_id: int, build_key: str
) -> ReferenceProfile | None:
    path = profile_path(spec, difficulty, boss_id, build_key)
    if not path.exists():
        return None
    return ReferenceProfile.model_validate_json(path.read_text(encoding="utf-8"))
