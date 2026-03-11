"""Apollo.io API client with retry logic."""

from typing import Any

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.config import settings

APOLLO_BASE_URL = "https://api.apollo.io"


def _is_retryable(exc: BaseException) -> bool:
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code in (429, 500, 502, 503, 504)
    return isinstance(exc, (httpx.TimeoutException, httpx.ConnectError))


_retry_decorator = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.TimeoutException, httpx.ConnectError)),
    reraise=True,
)


class ApolloService:
    """Apollo.io API client with connection pooling and retry."""

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or settings.apollo_api_key
        self._client = httpx.AsyncClient(
            base_url=APOLLO_BASE_URL,
            timeout=30.0,
            headers={"Content-Type": "application/json"},
        )

    async def close(self) -> None:
        await self._client.aclose()

    @_retry_decorator
    async def search_people(self, filters: dict[str, Any]) -> dict:
        """Search for people matching ICP-derived filters.

        Filters may include: person_titles, person_locations,
        organization_industry_tag_ids, organization_num_employees_ranges, etc.
        """
        payload = {"api_key": self.api_key, **filters}
        resp = await self._client.post("/v1/mixed_people/search", json=payload)
        resp.raise_for_status()
        return resp.json()

    @_retry_decorator
    async def search_organizations(self, filters: dict[str, Any]) -> dict:
        """Search for organizations matching ICP criteria."""
        payload = {"api_key": self.api_key, **filters}
        resp = await self._client.post("/v1/organizations/search", json=payload)
        resp.raise_for_status()
        return resp.json()

    @_retry_decorator
    async def enrich_person(self, person_id: str) -> dict:
        """Enrich a person record by Apollo ID."""
        resp = await self._client.get(
            f"/v1/people/{person_id}",
            params={"api_key": self.api_key},
        )
        resp.raise_for_status()
        return resp.json()
