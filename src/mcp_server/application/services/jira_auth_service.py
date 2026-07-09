from mcp_server.application.ports import IJiraAuthPort
from mcp_server.application.ports.token_storage import AuthResult
from mcp_server.application.service_interfaces import IJiraAuthService


class JiraAuthService(IJiraAuthService):
    """Orchestrates the Jira OAuth 2.0 authentication flow."""

    __jira_auth_port: IJiraAuthPort

    def __init__(self, jira_auth_port: IJiraAuthPort) -> None:
        self.__jira_auth_port = jira_auth_port

    async def generate_auth_url(self, state: str) -> str:
        return await self.__jira_auth_port.generate_auth_url(state)

    async def exchange_auth_code(self, code: str) -> AuthResult:
        return await self.__jira_auth_port.exchange_auth_code(code)
