from urllib.parse import urlencode

from mcp_server.application.ports import ITrelloAuthPort, ITokenStoragePort
from mcp_server.domain.exceptions import TrelloTokenStorageException

TRELLO_AUTHORIZE_URL = "https://trello.com/1/authorize"


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

    async def generate_auth_url(self, user_id: str) -> str:
        params = {
            "key": self.__api_key,
            "name": self.__app_name,
            "scope": "read,write",
            "response_type": "token",
            "expiration": "never",
        }
        return f"{TRELLO_AUTHORIZE_URL}?{urlencode(params)}"

    async def store_tokens(self, user_id: str, token: str, token_secret: str) -> None:
        if not token or not token.strip():
            raise TrelloTokenStorageException(user_id, "token must not be empty")
        if not token_secret or not token_secret.strip():
            raise TrelloTokenStorageException(user_id, "token_secret must not be empty")

        await self.__token_storage.save_tokens(
            user_id=user_id,
            access_token=token,
            refresh_token=token_secret,
            expires_at=0,
        )
