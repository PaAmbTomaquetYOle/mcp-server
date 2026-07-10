from typing import Any
from urllib.parse import urlencode

from httpx2 import AsyncClient, HTTPStatusError

from mcp_server.application.ports import IBackendTokenProvider, IKnowledgeGraphPort
from mcp_server.domain import KnowledgeGraphApiException, PersonNotFoundException


class KnowledgeGraphApiAdapter(IKnowledgeGraphPort):
    """HTTP adapter for the OffBoardMe backend's Knowledge Graph REST endpoints."""

    __base_url: str
    __token_provider: IBackendTokenProvider
    __client: AsyncClient

    def __init__(self, base_url: str, token_provider: IBackendTokenProvider, client: AsyncClient) -> None:
        self.__base_url = base_url.rstrip("/")
        self.__token_provider = token_provider
        self.__client = client

    async def _auth_headers(self) -> dict[str, str]:
        token = await self.__token_provider.get_access_token()
        return {"Authorization": f"Bearer {token}"}

    async def search_experts(self, topic: str, limit: int = 10) -> list[dict]:
        params: dict[str, Any] = {"topic": topic, "limit": limit}
        try:
            response = await self.__client.get(
                f"{self.__base_url}/knowledge-graph/experts?{urlencode(params)}",
                headers=await self._auth_headers(),
            )
            response.raise_for_status()
            return list(response.json())
        except HTTPStatusError as exc:
            raise KnowledgeGraphApiException(
                f"Backend returned HTTP {exc.response.status_code} for expert search",
                status_code=exc.response.status_code,
            ) from exc
        except Exception as exc:
            raise KnowledgeGraphApiException(f"Failed to reach Knowledge Graph API: {exc}") from exc

    async def get_person_knowledge(self, person_id: str) -> dict:
        try:
            response = await self.__client.get(
                f"{self.__base_url}/knowledge-graph/persons/{person_id}",
                headers=await self._auth_headers(),
            )
            response.raise_for_status()
            return response.json()
        except HTTPStatusError as exc:
            if exc.response.status_code == 404:
                raise PersonNotFoundException(person_id) from exc
            raise KnowledgeGraphApiException(
                f"Backend returned HTTP {exc.response.status_code} for person {person_id}",
                status_code=exc.response.status_code,
            ) from exc
        except Exception as exc:
            raise KnowledgeGraphApiException(f"Failed to reach Knowledge Graph API: {exc}") from exc
