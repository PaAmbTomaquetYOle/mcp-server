from mcp_server.application.ports import ITrelloAuthPort
from mcp_server.application.service_interfaces import ITrelloAuthService


class TrelloAuthService(ITrelloAuthService):
    """Orchestrates the Trello OAuth 1.0a authentication flow."""

    __trello_auth_port: ITrelloAuthPort

    def __init__(self, trello_auth_port: ITrelloAuthPort) -> None:
        self.__trello_auth_port = trello_auth_port

    async def generate_auth_url(self, user_id: str) -> str:
        return await self.__trello_auth_port.generate_auth_url(user_id)

    async def store_tokens(self, user_id: str, token: str, token_secret: str) -> None:
        await self.__trello_auth_port.store_tokens(user_id, token, token_secret)
