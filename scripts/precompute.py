"""Build Reference Profiles from Top Parses and write them under data/reference/.

Run offline by GitHub Actions (see .github/workflows/precompute.yml) and locally for
seeding. Encounter IDs are NOT hard-coded — discover the current tier with
`--list-zones`, then pass `--boss <id>`.

Examples
--------
    python -m scripts.precompute --list-zones
    python -m scripts.precompute --spec havoc --difficulty mythic --boss 3009
"""

from __future__ import annotations

import argparse
import asyncio
from datetime import datetime, timezone

from wowanalyze.config import get_settings
from wowanalyze.models import Difficulty
from wowanalyze.wcl import WCLClient
from wowanalyze.wcl.queries import LIST_ZONES

# WCL difficulty ids (Mythic raid = 5). Confirm against worldData if the API changes.
_DIFFICULTY_ID = {Difficulty.normal: 3, Difficulty.heroic: 4, Difficulty.mythic: 5}


async def list_zones() -> None:
    client = WCLClient()
    data = await client.query(LIST_ZONES)
    for zone in data["worldData"]["zones"]:
        print(f"\nZone {zone['id']}: {zone['name']}")
        for enc in zone.get("encounters", []):
            print(f"   encounter {enc['id']:>5}  {enc['name']}")


async def build_reference(spec: str, difficulty: Difficulty, boss_id: int) -> None:
    settings = get_settings()
    _ = WCLClient()
    patch = "TODO-detect-patch"
    generated_at = datetime.now(timezone.utc).isoformat()

    print(
        f"[precompute] spec={spec} difficulty={difficulty.value} boss={boss_id} "
        f"top={settings.top_parse_count} at {generated_at}"
    )
    # TODO(reference): the real pipeline —
    #   1. ENCOUNTER_RANKINGS -> top ~N Mythic kills for (spec, boss) by rDPS
    #   2. for each ranked parse: fetch ACTOR_TABLE, map -> ActorFightData + BuildCluster
    #   3. cluster_parses() -> aggregate_cluster() -> build_profile()
    #   4. save_profile() for each Build Cluster
    raise SystemExit(
        "Reference build not implemented yet — scaffold only. "
        "Wire the WCL rankings + table mapping (see builder.py TODOs)."
    )


async def build_seeds() -> None:
    """Build every (SEED_SPEC x CURRENT_TIER_ENCOUNTER) combination."""
    from scripts.seeds import (
        CURRENT_TIER_ENCOUNTERS,
        DEFAULT_DIFFICULTY,
        SEED_SPECS,
    )

    if not CURRENT_TIER_ENCOUNTERS:
        raise SystemExit(
            "No encounters configured for this tier. Run `--list-zones`, then fill in "
            "CURRENT_TIER_ENCOUNTERS in scripts/seeds.py."
        )
    for spec in SEED_SPECS:
        for boss_id in CURRENT_TIER_ENCOUNTERS:
            await build_reference(spec, DEFAULT_DIFFICULTY, boss_id)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build WowAnalyze Reference Profiles.")
    parser.add_argument(
        "--list-zones",
        action="store_true",
        help="Print current zones/encounters so you can find boss ids for this tier.",
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
    args = parser.parse_args()

    if args.list_zones:
        asyncio.run(list_zones())
        return

    if args.seeds:
        asyncio.run(build_seeds())
        return

    if not (args.spec and args.boss):
        parser.error("provide --spec and --boss, use --seeds, or use --list-zones")

    asyncio.run(build_reference(args.spec, args.difficulty, args.boss))


if __name__ == "__main__":
    main()
