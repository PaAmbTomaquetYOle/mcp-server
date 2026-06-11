from jira import JIRA, Issue

from mcp_server.application.ports import ICollaborationToolPort, ITokenStoragePort
from mcp_server.domain import JiraTask


class JiraAdapter(ICollaborationToolPort):

    __token_storage: ITokenStoragePort
    __server_url: str
    __client_id: str
    __client_secret: str

    def __init__(
        self,
        token_storage_port: ITokenStoragePort,
        server_url: str,
        client_id: str,
        client_secret: str,
    ) -> None:
        """
        Initializes the JiraAdapter with necessary configuration and token storage.

        Args:
            token_storage_port (ITokenStoragePort): Port for storing and retrieving OAuth tokens.
            server_url (str): Base URL of the Jira server.
            client_id (str): OAuth 2.0 client ID for Jira integration.
            client_secret (str): OAuth 2.0 client secret for Jira integration.
        """
        self.__token_storage = token_storage_port
        self.__server_url = server_url
        self.__client_id = client_id
        self.__client_secret = client_secret

    async def _get_client(self, user_id: str) -> JIRA:
        """Build a JIRA client with the user's OAuth 2.0 access token."""
        tokens = await self.__token_storage.get_tokens(user_id)
        if tokens is None:
            raise ValueError(f"No tokens found for user: {user_id}")
        return JIRA(server=self.__server_url, token_auth=tokens["access_token"])
    
    def __issue_to_domain_model(self, issue: Issue) -> JiraTask:
        """Convert a JIRA Issue to a JiraTask domain model."""
        return JiraTask(
            task_id=issue.key,
            title=issue.fields.summary,
            description=issue.fields.description,
            url=f"{self.__server_url}/browse/{issue.key}",
            status=issue.fields.status.name,
            priority=issue.fields.priority.name if issue.fields.priority else None,
        )

    async def get_issue(self, issue_id: str, user_id: str):
        jira = await self._get_client(user_id)
        issue = jira.issue(issue_id)
        return self.__issue_to_domain_model(issue)