from typing import Any
from urllib.parse import urlencode

from httpx2 import AsyncClient, HTTPStatusError

from mcp_server.application.ports import IBackendApiPort, IBackendTokenProvider
from mcp_server.domain import BackendApiException


class BackendApiAdapter(IBackendApiPort):
    """HTTP adapter for the OffBoardMe backend API, used to look up offboarding dossiers and SOPs."""

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

    async def search_dossiers(
        self, employee_name: str | None = None, process_id: str | None = None
    ) -> list[dict]:
        params: dict[str, Any] = {}
        if employee_name is not None:
            params["employee_name"] = employee_name
        if process_id is not None:
            params["process_id"] = process_id

        try:
            response = await self.__client.get(
                f"{self.__base_url}/dossiers/search?{urlencode(params)}",
                headers=await self._auth_headers(),
            )
            response.raise_for_status()
            data = response.json()
            return list(data.get("items", []))
        except HTTPStatusError as exc:
            raise BackendApiException(
                f"Backend returned HTTP {exc.response.status_code} for dossier search",
                status_code=exc.response.status_code,
            ) from exc
        except Exception as exc:
            raise BackendApiException(f"Failed to reach backend API: {exc}") from exc

    async def search_sops(
        self,
        text: str | None = None,
        tags: list[str] | None = None,
        page: int = 1,
        size: int = 20,
    ) -> dict:
        params: dict[str, Any] = {"page": page, "size": size}
        if text is not None:
            params["q"] = text
        if tags:
            params["tags"] = tags

        try:
            response = await self.__client.get(
                f"{self.__base_url}/sops?{urlencode(params, doseq=True)}",
                headers=await self._auth_headers(),
            )
            response.raise_for_status()
            return response.json()
        except HTTPStatusError as exc:
            raise BackendApiException(
                f"Backend returned HTTP {exc.response.status_code} for SOP search",
                status_code=exc.response.status_code,
            ) from exc
        except Exception as exc:
            raise BackendApiException(f"Failed to reach backend API: {exc}") from exc

    async def get_sop(self, sop_id: str) -> dict:
        try:
            response = await self.__client.get(
                f"{self.__base_url}/sops/{sop_id}",
                headers=await self._auth_headers(),
            )
            response.raise_for_status()
            return response.json()
        except HTTPStatusError as exc:
            raise BackendApiException(
                f"Backend returned HTTP {exc.response.status_code} for SOP {sop_id}",
                status_code=exc.response.status_code,
            ) from exc
        except Exception as exc:
            raise BackendApiException(f"Failed to reach backend API: {exc}") from exc
