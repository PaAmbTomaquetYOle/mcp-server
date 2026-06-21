from urllib.parse import urlencode

from httpx2 import AsyncClient, HTTPStatusError

from mcp_server.application.ports import ITrelloAuthPort, ITokenStoragePort
from mcp_server.domain.exceptions import TrelloTokenStorageException

TRELLO_AUTHORIZE_URL = "https://trello.com/1/authorize"
TRELLO_MEMBERS_ME_URL = "https://api.trello.com/1/members/me"


class TrelloAuthAdapter(ITrelloAuthPort):

    __token_storage: ITokenStoragePort
    __api_key: str
    __app_name: str

    def __init__(
        self,
        token_storage_port: ITokenStoragePort,
        api_key: str,
        app_name: str,
    ) -> None:
        self.__token_storage = token_storage_port
        self.__api_key = api_key
        self.__app_name = app_name

    async def generate_auth_url(self) -> str:
        params = {
            "key": self.__api_key,
            "name": self.__app_name,
            "scope": "read,write",
            "response_type": "token",
            "expiration": "never",
        }
        return f"{TRELLO_AUTHORIZE_URL}?{urlencode(params)}"

    async def store_token(self, token: str) -> str:
        if not token or not token.strip():
            raise TrelloTokenStorageException("unknown", "token must not be empty")

        username = await self._resolve_username(token)

        await self.__token_storage.save_tokens(
            user_id=username,
            access_token=token,
            refresh_token="",
            expires_at=0,
        )
        return username

    async def _resolve_username(self, token: str) -> str:
        try:
            async with AsyncClient() as client:
                response = await client.get(
                    TRELLO_MEMBERS_ME_URL,
                    params={"key": self.__api_key, "token": token},
                )
                response.raise_for_status()
                return str(response.json()["username"])
        except HTTPStatusError as exc:
            raise TrelloTokenStorageException(
                "unknown",
                f"Failed to resolve Trello username: HTTP {exc.response.status_code}",
            ) from exc
        except Exception as exc:
            raise TrelloTokenStorageException(
                "unknown",
                f"Failed to resolve Trello username: {exc}",
            ) from exc
