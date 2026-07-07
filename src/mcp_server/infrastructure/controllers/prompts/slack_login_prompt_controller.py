from mcp.server.fastmcp.prompts.base import Prompt

from mcp_server.infrastructure.controllers import BaseController


class SlackLoginPromptController(BaseController):
    """Prompt controller that guides an agent through the Slack OAuth 2.0 login flow."""

    def register(self) -> None:
        self._server.add_prompt(
            Prompt(
                name="slack_login",
                title="Slack Login",
                description="Guide the user through the Slack OAuth 2.0 authorization flow for workspace search.",
                fn=self.slack_login,
                arguments=[],
                context_kwarg=None,
            )
        )

    @staticmethod
    async def slack_login() -> str:
        return (
            "You are a Slack authentication assistant. Your goal is to help the user "
            "connect their Slack account via OAuth 2.0 so they can search their own workspace.\n\n"
            "Follow these steps:\n\n"
            "1. Call the `generate_slack_auth_url` tool (no arguments needed).\n"
            "2. Present the returned authorization URL to the user and ask them to open it in their browser.\n"
            "3. Tell the user they will be redirected to Slack to log in and grant search permissions.\n"
            "4. Once they authorize, the callback endpoint handles the token exchange automatically. "
            "The user will see a success page in their browser showing their Slack user ID.\n"
            "5. The Slack user ID shown is the user_id to use in `search_slack_workspace`.\n\n"
            "If the automatic callback fails (e.g. the user is on a different network), "
            "ask the user to copy the `code` parameter from the redirect URL and call "
            "`complete_slack_auth` with that code. It will return the Slack user ID to use.\n\n"
            "Important: the Slack user ID must be used consistently as user_id in all "
            "subsequent `search_slack_workspace` calls."
        )
