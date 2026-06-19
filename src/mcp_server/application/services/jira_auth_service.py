from mcp_server.application.ports import IJiraAuthPort
from mcp_server.application.ports.token_storage import TokenData
from mcp_server.application.service_interfaces import IJiraAuthService


class JiraAuthService(IJiraAuthService):
    """Orchestrates the Jira OAuth 2.0 authentication flow."""

    __jira_auth_port: IJiraAuthPort

    def __init__(self, jira_auth_port: IJiraAuthPort) -> None:
        self.__jira_auth_port = jira_auth_port

    async def generate_auth_url(self, user_id: str) -> str:
        return await self.__jira_auth_port.generate_auth_url(user_id)

    async def exchange_auth_code(self, user_id: str, code: str) -> TokenData:
        return await self.__jira_auth_port.exchange_auth_code(user_id, code)
