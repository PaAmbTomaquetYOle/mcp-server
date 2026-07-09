from mcp_server.application.ports import ISlackAuthPort
from mcp_server.application.ports.slack_auth import SlackAuthResult
from mcp_server.application.service_interfaces import ISlackAuthService


class SlackAuthService(ISlackAuthService):
    """Orchestrates the Slack OAuth 2.0 user authentication flow."""

    __slack_auth_port: ISlackAuthPort

    def __init__(self, slack_auth_port: ISlackAuthPort) -> None:
        self.__slack_auth_port = slack_auth_port

    async def generate_auth_url(self, state: str) -> str:
        return await self.__slack_auth_port.generate_auth_url(state)

    async def exchange_auth_code(self, code: str) -> SlackAuthResult:
        return await self.__slack_auth_port.exchange_auth_code(code)
