"""Build Reference Profiles from Top Parses and write them under data/reference/.

Run offline by GitHub Actions (see .github/workflows/precompute.yml) and locally for
seeding. Encounter IDs are NOT hard-coded in the engine — seeds live in scripts/seeds.py
(discover new ones with `--list-zones`).

Examples
--------
    python -m scripts.precompute --list-zones
    python -m scripts.precompute --dump-rankings --spec elemental --boss 3177
    python -m scripts.precompute --spec elemental --boss 3177 --top 20
    python -m scripts.precompute --seeds --top 20
"""

from __future__ import annotations

import argparse
import asyncio
import json
from datetime import datetime, timezone

from wowanalyze.builds import build_label, detect_build
from wowanalyze.models import BuildCluster, Difficulty
from wowanalyze.reference.builder import build_profile
from wowanalyze.reference.store import PROVISIONAL_BUILD_KEY, save_profile
from wowanalyze.wcl import WCLClient
from wowanalyze.wcl.actor import map_actor_casts
from wowanalyze.wcl.queries import (
    ACTOR_CASTS,
    ENCOUNTER_RANKINGS,
    LIST_ZONES,
    REPORT_ACTORS,
)

# WCL difficulty ids (Mythic raid = 5). Confirm against worldData if the API changes.
_DIFFICULTY_ID = {Difficulty.normal: 3, Difficulty.heroic: 4, Difficulty.mythic: 5}

# Minimum parses to trust a per-build cluster on its own.
_MIN_CLUSTER = 5


def _resolve_spec(spec: str) -> tuple[str, str]:
    from scripts.seeds import SPEC_TO_CLASS

    if spec not in SPEC_TO_CLASS:
        raise SystemExit(
            f"Unknown spec slug {spec!r}. Add it to SPEC_TO_CLASS in scripts/seeds.py."
        )
    return SPEC_TO_CLASS[spec]


async def list_zones() -> None:
    client = WCLClient()
    data = await client.query(LIST_ZONES)
    for zone in data["worldData"]["zones"]:
        print(f"\nZone {zone['id']}: {zone['name']}")
        for enc in zone.get("encounters", []):
            print(f"   encounter {enc['id']:>5}  {enc['name']}")


async def _fetch_rankings(
    client: WCLClient,
    boss_id: int,
    difficulty: Difficulty,
    class_name: str,
    spec_name: str,
    top: int,
) -> tuple[str | None, list[dict]]:
    """Page through characterRankings until we have `top` entries."""
    rankings: list[dict] = []
    encounter_name: str | None = None
    page = 1
    while len(rankings) < top:
        data = await client.query(
            ENCOUNTER_RANKINGS,
            {
                "encounterId": boss_id,
                "difficulty": _DIFFICULTY_ID[difficulty],
                "className": class_name,
                "specName": spec_name,
                "page": page,
            },
        )
        enc = (data.get("worldData") or {}).get("encounter") or {}
        encounter_name = enc.get("name") or encounter_name
        cr = enc.get("characterRankings") or {}
        page_rankings = cr.get("rankings") or []
        if not page_rankings:
            break
        rankings.extend(page_rankings)
        if not cr.get("hasMorePages"):
            break
        page += 1
    return encounter_name, rankings[:top]


async def dump_rankings(spec: str, difficulty: Difficulty, boss_id: int) -> None:
    """Print the raw shape of page 1 of rankings — used to confirm the JSON layout."""
    class_name, spec_name = _resolve_spec(spec)
    client = WCLClient()
    data = await client.query(
        ENCOUNTER_RANKINGS,
        {
            "encounterId": boss_id,
            "difficulty": _DIFFICULTY_ID[difficulty],
            "className": class_name,
            "specName": spec_name,
            "page": 1,
        },
    )
    enc = (data.get("worldData") or {}).get("encounter") or {}
    cr = enc.get("characterRankings") or {}
    print(f"encounter: {enc.get('name')}")
    print(f"characterRankings keys: {list(cr.keys())}")
    rankings = cr.get("rankings") or []
    print(f"rankings on page 1: {len(rankings)}")
    if rankings:
        print("--- first ranking entry ---")
        print(json.dumps(rankings[0], indent=2)[:2000])


async def build_reference(
    spec: str, difficulty: Difficulty, boss_id: int, top: int = 20
) -> None:
    class_name, spec_name = _resolve_spec(spec)
    client = WCLClient()
    generated_at = datetime.now(timezone.utc).isoformat()
    print(
        f"[precompute] {spec} @ boss {boss_id} ({difficulty.value}) — "
        f"top {top} {spec_name} {class_name} parses"
    )

    encounter_name, rankings = await _fetch_rankings(
        client, boss_id, difficulty, class_name, spec_name, top
    )
    if not rankings:
        print(f"  no rankings for boss {boss_id}; skipping")
        return

    actors_cache: dict[str, dict[str, int]] = {}
    cluster_data = []
    for i, r in enumerate(rankings, 1):
        report = r.get("report") or {}
        code = report.get("code")
        fight_id = report.get("fightID")
        name = r.get("name")
        if not (code and fight_id and name):
            continue

        if code not in actors_cache:
            adata = await client.query(REPORT_ACTORS, {"code": code})
            master = (
                ((adata.get("reportData") or {}).get("report") or {}).get("masterData")
                or {}
            )
            actors_cache[code] = {
                a.get("name"): a.get("id") for a in (master.get("actors") or [])
            }
        source_id = actors_cache[code].get(name)
        if not source_id:
            print(f"  [{i}/{len(rankings)}] {name}: could not resolve sourceID, skip")
            continue

        cdata = await client.query(
            ACTOR_CASTS, {"code": code, "fightId": fight_id, "sourceId": source_id}
        )
        cluster_data.append(map_actor_casts(cdata))
        print(f"  [{i}/{len(rankings)}] {name} ({code}#{fight_id})")

    if not cluster_data:
        print("  resolved 0 parses; skipping")
        return

    def _save(build_key: str, data_list: list) -> None:
        build = BuildCluster(
            key=build_key, hero_talent=build_key, label=build_label(build_key)
        )
        profile = build_profile(
            spec=spec,
            boss_id=boss_id,
            boss_name=encounter_name or f"Boss {boss_id}",
            difficulty=difficulty,
            build=build,
            patch="unknown",
            generated_at=generated_at,
            cluster_data=data_list,
        )
        path = save_profile(profile)
        print(
            f"  saved [{build_key}] {len(data_list)} parses, "
            f"{len(profile.metrics)} metrics -> {path}"
        )

    # Always the blended fallback, then per-build clusters that are big enough.
    _save(PROVISIONAL_BUILD_KEY, cluster_data)

    groups: dict[str, list] = {}
    for d in cluster_data:
        groups.setdefault(detect_build(spec, d.cast_counts), []).append(d)
    for build_key, ds in groups.items():
        if build_key == PROVISIONAL_BUILD_KEY:
            continue
        if len(ds) < _MIN_CLUSTER:
            print(f"  [{build_key}] only {len(ds)} parses (<{_MIN_CLUSTER}), skipped")
            continue
        _save(build_key, ds)


async def build_seeds(top: int) -> None:
    """Build every (SEED_SPEC x CURRENT_TIER_ENCOUNTER) combination."""
    from scripts.seeds import (
        CURRENT_TIER_ENCOUNTERS,
        DEFAULT_DIFFICULTY,
        SEED_SPECS,
    )

    if not CURRENT_TIER_ENCOUNTERS:
        raise SystemExit(
            "No encounters configured. Run `--list-zones`, then fill in "
            "CURRENT_TIER_ENCOUNTERS in scripts/seeds.py."
        )
    for spec in SEED_SPECS:
        for boss_id in CURRENT_TIER_ENCOUNTERS:
            await build_reference(spec, DEFAULT_DIFFICULTY, boss_id, top=top)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build WowAnalyze Reference Profiles.")
    parser.add_argument(
        "--list-zones",
        action="store_true",
        help="Print current zones/encounters so you can find boss ids for this tier.",
    )
    parser.add_argument(
        "--dump-rankings",
        action="store_true",
        help="Print the raw shape of page 1 of rankings for --spec/--boss and exit.",
    )
    parser.add_argument(
        "--seeds",
        action="store_true",
        help="Build the configured seed set (scripts/seeds.py). Used by CI.",
    )
    parser.add_argument("--spec", help="Spec slug, e.g. 'elemental'.")
    parser.add_argument(
        "--difficulty",
        type=Difficulty,
        default=Difficulty.mythic,
        choices=list(Difficulty),
    )
    parser.add_argument("--boss", type=int, help="Encounter id (from --list-zones).")
    parser.add_argument(
        "--top", type=int, default=20, help="How many top parses to aggregate (default 20)."
    )
    args = parser.parse_args()

    if args.list_zones:
        asyncio.run(list_zones())
        return

    if args.dump_rankings:
        if not (args.spec and args.boss):
            parser.error("--dump-rankings needs --spec and --boss")
        asyncio.run(dump_rankings(args.spec, args.difficulty, args.boss))
        return

    if args.seeds:
        asyncio.run(build_seeds(args.top))
        return

    if not (args.spec and args.boss):
        parser.error("provide --spec and --boss, use --seeds, or use --list-zones")

    asyncio.run(build_reference(args.spec, args.difficulty, args.boss, top=args.top))


if __name__ == "__main__":
    main()
