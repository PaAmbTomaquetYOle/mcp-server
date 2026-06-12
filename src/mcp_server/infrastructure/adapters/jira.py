import asyncio
import time
from typing import Any

from httpx2 import AsyncClient, HTTPStatusError
from jira import JIRA, Issue
from jira.exceptions import JIRAError

from mcp_server.application.ports import (
    ICollaborationToolPort,
    ITokenStoragePort,
    TokenData,
)
from mcp_server.domain import (
    IssueNotFoundException,
    JiraApiException,
    JiraAuthenticationException,
    JiraTask,
    JiraUserNotFoundException,
    TokenRefreshException,
    UserTokensNotFoundException,
)

ATLASSIAN_TOKEN_URL = "https://auth.atlassian.com/oauth/token"


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

    async def _refresh_tokens(self, user_id: str, refresh_token: str) -> TokenData:
        """Exchange a refresh token for a new access token via Atlassian OAuth 2.0."""
        try:
            async with AsyncClient() as client:
                response = await client.post(
                    ATLASSIAN_TOKEN_URL,
                    json={
                        "grant_type": "refresh_token",
                        "client_id": self.__client_id,
                        "client_secret": self.__client_secret,
                        "refresh_token": refresh_token,
                    },
                )
                response.raise_for_status()
                data: dict[str, Any] = response.json()
        except HTTPStatusError as exc:
            if exc.response.status_code == 401:
                raise JiraAuthenticationException(user_id) from exc
            raise TokenRefreshException(user_id, str(exc)) from exc
        except Exception as exc:
            raise TokenRefreshException(user_id, str(exc)) from exc

        new_tokens: TokenData = {
            "access_token": str(data["access_token"]),
            "refresh_token": str(data.get("refresh_token", refresh_token)),
            "expires_at": int(time.time()) + int(data["expires_in"]),
        }
        await self.__token_storage.save_tokens(
            user_id,
            new_tokens["access_token"],
            new_tokens["refresh_token"],
            new_tokens["expires_at"],
        )
        return new_tokens

    def _build_client(self, access_token: str) -> JIRA:
        return JIRA(server=self.__server_url, token_auth=access_token)

    async def _get_client(self, user_id: str) -> JIRA:
        """Build a JIRA client, refreshing the token if expired."""
        tokens: TokenData | None = await self.__token_storage.get_tokens(user_id)
        if tokens is None:
            raise UserTokensNotFoundException(user_id)

        expires_at: int = tokens["expires_at"]
        access_token: str = tokens["access_token"]

        if expires_at <= int(time.time()) + 60:
            tokens = await self._refresh_tokens(user_id, tokens["refresh_token"])
            access_token = tokens["access_token"]

        try:
            return await asyncio.to_thread(self._build_client, access_token)
        except JIRAError as exc:
            if exc.status_code == 401:
                raise JiraAuthenticationException(user_id) from exc
            raise JiraApiException(str(exc), status_code=exc.status_code) from exc

    @staticmethod
    def __sanitize_jql_value(value: str) -> str:
        """Escape backslashes and double quotes to prevent JQL injection."""
        return value.replace("\\", "\\\\").replace('"', '\\"')

    def __issue_to_domain_model(self, issue: Issue) -> JiraTask:
        """Convert a JIRA Issue to a JiraTask domain model."""
        return JiraTask(
            task_id=issue.key,
            title=issue.fields.summary,
            description=issue.fields.description,
            url=f"{self.__server_url}/browse/{issue.key}",
            status=issue.fields.status.name,
            priority=issue.fields.priority.name if issue.fields.priority else None,
            project=issue.fields.project.name,
        )

    async def get_issue(self, issue_id: str, user_id: str) -> JiraTask:
        jira = await self._get_client(user_id)
        try:
            issue = await asyncio.to_thread(jira.issue, issue_id)
        except JIRAError as exc:
            if exc.status_code == 404:
                raise IssueNotFoundException(issue_id) from exc
            raise JiraApiException(str(exc), status_code=exc.status_code) from exc
        return self.__issue_to_domain_model(issue)

    async def get_pending_issues(self, user_id: str, assignee: str) -> tuple[JiraTask, ...]:
        jira = await self._get_client(user_id)
        jql = f'assignee = "{self.__sanitize_jql_value(assignee)}" AND status IN ("To Do", "In Progress")'
        try:
            issues = await asyncio.to_thread(jira.search_issues, jql)
        except JIRAError as exc:
            if "does not exist" in str(exc).lower() or exc.status_code == 400:
                raise JiraUserNotFoundException(assignee) from exc
            raise JiraApiException(str(exc), status_code=exc.status_code) from exc
        return tuple(self.__issue_to_domain_model(issue) for issue in issues)
