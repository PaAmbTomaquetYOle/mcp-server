import asyncio
import time

from httpx2 import AsyncClient, HTTPStatusError

from mcp_server.application.ports import IBackendTokenProvider
from mcp_server.domain import BackendApiException

_TOKEN_PATH = "/auth/token"
_GRANT_TYPE = "client_credentials"
_REFRESH_SKEW_SECONDS = 60


class BackendTokenClient(IBackendTokenProvider):
    """
    Obtains and caches an access token for the backend API via the client-credentials grant.

    Requests a fresh token from `POST {base_url}/auth/token` the first time it is needed and
    whenever the cached token is within `_REFRESH_SKEW_SECONDS` of expiring, reusing it otherwise.
    Concurrent callers are serialized by a lock so only one refresh request is ever in flight.
    """

    __base_url: str
    __client_id: str
    __client_secret: str
    __client: AsyncClient
    __lock: asyncio.Lock
    __access_token: str | None
    __expires_at: float

    def __init__(self, base_url: str, client_id: str, client_secret: str, client: AsyncClient) -> None:
        self.__base_url = base_url.rstrip("/")
        self.__client_id = client_id
        self.__client_secret = client_secret
        self.__client = client
        self.__lock = asyncio.Lock()
        self.__access_token = None
        self.__expires_at = 0.0

    async def get_access_token(self) -> str:
        if self.__has_valid_token():
            return self.__access_token  # type: ignore[return-value]

        async with self.__lock:
            if self.__has_valid_token():
                return self.__access_token  # type: ignore[return-value]
            await self.__fetch_token()
            return self.__access_token  # type: ignore[return-value]

    def __has_valid_token(self) -> bool:
        return self.__access_token is not None and time.monotonic() < self.__expires_at - _REFRESH_SKEW_SECONDS

    async def __fetch_token(self) -> None:
        try:
            response = await self.__client.post(
                f"{self.__base_url}{_TOKEN_PATH}",
                json={
                    "grant_type": _GRANT_TYPE,
                    "client_id": self.__client_id,
                    "client_secret": self.__client_secret,
                },
            )
            response.raise_for_status()
            data = response.json()
        except HTTPStatusError as exc:
            raise BackendApiException(
                f"Backend returned HTTP {exc.response.status_code} for token request",
                status_code=exc.response.status_code,
            ) from exc
        except Exception as exc:
            raise BackendApiException(f"Failed to reach backend API: {exc}") from exc

        self.__access_token = data["access_token"]
        self.__expires_at = time.monotonic() + data["expires_in"]
