"""Runtime configuration, read from the environment.

Secrets (WCL credentials) are read here and nowhere else, so it stays obvious that
they live server-side only — never in the frontend bundle.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()  # no-op in production where env vars are set by the platform

# Repo root = two levels up from this file (wowanalyze/config.py -> repo/).
REPO_ROOT = Path(__file__).resolve().parent.parent


class Settings:
    """Process-wide settings. Cheap enough to build on demand; cached below."""

    wcl_client_id: str | None = os.environ.get("WCL_CLIENT_ID")
    wcl_client_secret: str | None = os.environ.get("WCL_CLIENT_SECRET")

    wcl_token_url: str = "https://www.warcraftlogs.com/oauth/token"
    wcl_api_url: str = "https://www.warcraftlogs.com/api/v2/client"

    # Default reference population: top N Mythic kills by rDPS.
    top_parse_count: int = 100

    @property
    def reference_dir(self) -> Path:
        configured = os.environ.get("WOWANALYZE_REFERENCE_DIR", "data/reference")
        path = Path(configured)
        return path if path.is_absolute() else REPO_ROOT / path

    @property
    def has_wcl_credentials(self) -> bool:
        return bool(self.wcl_client_id and self.wcl_client_secret)


@lru_cache
def get_settings() -> Settings:
    return Settings()
