from mcp.server.fastmcp.prompts.base import Prompt

from mcp_server.infrastructure.controllers import BaseController


class JiraLoginPromptController(BaseController):
    """Prompt controller that guides an agent through the Jira OAuth 2.0 login flow."""

    def register(self) -> None:
        self._server.add_prompt(
            Prompt(
                name="jira_login",
                title="Jira Login",
                description="Guide the user through the Jira OAuth 2.0 authorization flow.",
                fn=self.jira_login,
                arguments=[],
            )
        )

    async def jira_login(self) -> str:
        return (
            "You are a Jira authentication assistant. Your goal is to help the user "
            "connect their Jira account via OAuth 2.0.\n\n"
            "Follow these steps:\n\n"
            "1. Call the `generate_jira_auth_url` tool (no arguments needed).\n"
            "2. Present the returned authorization URL to the user and ask them to open it in their browser.\n"
            "3. Tell the user they will be redirected to Atlassian to log in and grant permissions.\n"
            "4. Once they authorize, the callback endpoint handles the token exchange automatically. "
            "The user will see a success page in their browser showing their Atlassian email.\n"
            "5. The email shown is the user_id to use in all future Jira tool calls "
            "(e.g. `get_pending_jira_issues`, `get_jira_issue`).\n\n"
            "If the automatic callback fails (e.g. the user is on a different network), "
            "ask the user to copy the `code` parameter from the redirect URL and call "
            "`complete_jira_auth` with that code. It will return the email to use as user_id.\n\n"
            "Important: the user's Atlassian email is resolved automatically from the OAuth token. "
            "It must be used consistently as user_id in all subsequent Jira tool calls."
        )
