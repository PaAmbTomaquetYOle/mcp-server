import time
from typing import Any
from urllib.parse import urlencode

import jwt
from httpx2 import AsyncClient, HTTPStatusError

from mcp_server.application.ports import IBackendApiPort
from mcp_server.domain import BackendApiException

_BACKEND_JWT_AUDIENCE = "braintrust-backend"
_BACKEND_JWT_TTL_SECONDS = 300


class BackendApiAdapter(IBackendApiPort):
    """HTTP adapter for the BrainTrust backend API, used to look up offboarding dossiers."""

    __base_url: str
    __jwt_secret: str
    __jwt_issuer: str

    def __init__(self, base_url: str, jwt_secret: str, jwt_issuer: str) -> None:
        self.__base_url = base_url.rstrip("/")
        self.__jwt_secret = jwt_secret
        self.__jwt_issuer = jwt_issuer

    def _auth_headers(self) -> dict[str, str]:
        now = int(time.time())
        token = jwt.encode(
            {
                "iss": self.__jwt_issuer,
                "aud": _BACKEND_JWT_AUDIENCE,
                "iat": now,
                "exp": now + _BACKEND_JWT_TTL_SECONDS,
            },
            self.__jwt_secret,
            algorithm="HS256",
        )
        return {"Authorization": f"Bearer {token}"}

    async def get_dossier_by_process(self, process_id: str) -> dict:
        async with AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.__base_url}/offboarding/{process_id}/dossier",
                    headers=self._auth_headers(),
                )
                response.raise_for_status()
                return response.json()
            except HTTPStatusError as exc:
                raise BackendApiException(
                    f"Backend returned HTTP {exc.response.status_code} for process {process_id}",
                    status_code=exc.response.status_code,
                ) from exc
            except Exception as exc:
                raise BackendApiException(f"Failed to reach backend API: {exc}") from exc

    async def search_dossiers(
        self, employee_name: str | None = None, process_id: str | None = None
    ) -> list[dict]:
        params: dict[str, Any] = {}
        if employee_name is not None:
            params["employee_name"] = employee_name
        if process_id is not None:
            params["process_id"] = process_id

        async with AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.__base_url}/dossiers/search?{urlencode(params)}",
                    headers=self._auth_headers(),
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

        async with AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.__base_url}/sops?{urlencode(params, doseq=True)}",
                    headers=self._auth_headers(),
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
        async with AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.__base_url}/sops/{sop_id}",
                    headers=self._auth_headers(),
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
