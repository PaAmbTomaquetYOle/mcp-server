from mcp.server.fastmcp.prompts.base import Prompt

from mcp_server.infrastructure.controllers import BaseController


class TrelloLoginPromptController(BaseController):
    """Prompt controller that guides an agent through the Trello OAuth 1.0a login flow."""

    def register(self) -> None:
        self._server.add_prompt(
            Prompt(
                name="trello_login",
                title="Trello Login",
                description="Guide the user through the Trello OAuth 1.0a authorization flow.",
                fn=self.trello_login,
                arguments=[],
                context_kwarg=None,
            )
        )

    @staticmethod
    async def trello_login() -> str:
        return (
            "You are a Trello authentication assistant. Your goal is to help the user "
            "connect their Trello account via OAuth 1.0a.\n\n"
            "Follow these steps:\n\n"
            "1. Ask the user for their user_id (an identifier they want to use for Trello operations).\n"
            "2. Call the `generate_trello_auth_url` tool with the user_id.\n"
            "3. Present the returned authorization URL to the user and ask them to open it in their browser.\n"
            "4. Tell the user they will be redirected to Trello to log in and grant permissions.\n"
            "5. After authorizing, the user will receive an OAuth token. Ask the user to provide "
            "both the token and the token_secret.\n"
            "6. Call `complete_trello_auth` with the user_id, token, and token_secret to store "
            "the credentials.\n\n"
            "Important: the user_id provided must be used consistently in all subsequent Trello "
            "tool calls (e.g. `get_pending_trello_issues`, `get_trello_issue`)."
        )
