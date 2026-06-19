"""HTTP route controllers.

Custom Starlette routes mounted alongside the MCP server. These are not MCP
tools — they handle plain HTTP requests (e.g. OAuth callbacks).
"""

from .oauth_callback_controller import OAuthCallbackController

__all__ = [
    "OAuthCallbackController",
]
