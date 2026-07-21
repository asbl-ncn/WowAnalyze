"""Async WarcraftLogs API v2 client.

OAuth **client-credentials** flow: exchange the client id/secret for a bearer token,
then POST GraphQL. The secret is read from settings (env) and stays server-side.

Points budget: every GraphQL call costs points by complexity. This client is where a
response cache and points accounting will live (see TODOs) so the rest of the engine
never worries about it.
"""

from __future__ import annotations

import time
from typing import Any

import httpx

from wowanalyze.config import Settings, get_settings


class WCLError(RuntimeError):
    """A GraphQL-level error or a missing-credentials error from WCL."""


class WCLClient:
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._token: str | None = None
        self._token_expiry: float = 0.0

    async def _get_token(self) -> str:
        if not self._settings.has_wcl_credentials:
            raise WCLError(
                "WCL credentials missing. Set WCL_CLIENT_ID and WCL_CLIENT_SECRET "
                "(see .env.example)."
            )
        # Refresh a minute early to avoid using a token that expires mid-request.
        if self._token and time.monotonic() < self._token_expiry - 60:
            return self._token

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                self._settings.wcl_token_url,
                data={"grant_type": "client_credentials"},
                auth=(self._settings.wcl_client_id, self._settings.wcl_client_secret),
            )
            resp.raise_for_status()
            payload = resp.json()

        self._token = payload["access_token"]
        self._token_expiry = time.monotonic() + float(payload.get("expires_in", 3600))
        return self._token

    async def query(
        self, query: str, variables: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Run a GraphQL query and return its `data` payload.

        TODO(points): add a keyed response cache (disk in precompute, in-memory in the
        serverless function) and record `rateLimitData` so we stay inside the budget.
        """
        token = await self._get_token()
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                self._settings.wcl_api_url,
                json={"query": query, "variables": variables or {}},
                headers={"Authorization": f"Bearer {token}"},
            )
            resp.raise_for_status()
            body = resp.json()

        if body.get("errors"):
            raise WCLError(str(body["errors"]))
        return body["data"]
