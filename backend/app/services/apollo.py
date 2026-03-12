"""Apollo.io API client with retry logic.

Free-tier compatible: uses /v1/contacts/search with X-Api-Key header auth.
"""

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
            headers={
                "Content-Type": "application/json",
                "X-Api-Key": self.api_key,
            },
        )

    async def close(self) -> None:
        await self._client.aclose()

    @_retry_decorator
    async def search_people(self, filters: dict[str, Any]) -> dict:
        """Search for contacts matching ICP-derived filters.

        Uses /v1/contacts/search (available on free tier).
        Response is normalized to a consistent shape with 'people' key.
        """
        resp = await self._client.post("/v1/contacts/search", json=filters)
        resp.raise_for_status()
        data = resp.json()
        return self._normalize_contacts_response(data)

    @_retry_decorator
    async def search_organizations(self, filters: dict[str, Any]) -> dict:
        """Search for organizations matching ICP criteria."""
        resp = await self._client.post("/v1/organizations/search", json=filters)
        resp.raise_for_status()
        return resp.json()

    @_retry_decorator
    async def enrich_person(self, person_id: str) -> dict:
        """Enrich a person record by Apollo ID."""
        resp = await self._client.get(f"/v1/people/{person_id}")
        resp.raise_for_status()
        return resp.json()

    @staticmethod
    def _normalize_contacts_response(data: dict) -> dict:
        """Normalize contacts/search response to match people/search shape.

        contacts/search returns {contacts: [...]} where each contact has
        an 'account' sub-object. We normalize to {people: [...]} where
        each person has an 'organization' sub-object.
        """
        contacts = data.get("contacts", [])
        people = []
        for contact in contacts:
            person = dict(contact)
            # Rename 'account' → 'organization' for consistency
            account = person.pop("account", None) or {}
            person["organization"] = account
            people.append(person)

        return {
            "people": people,
            "pagination": data.get("pagination", {}),
        }
