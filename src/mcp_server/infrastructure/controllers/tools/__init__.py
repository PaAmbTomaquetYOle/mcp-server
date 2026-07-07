"""MCP tool controllers.

Defines and registers the server's MCP *tools* (callable actions the client can
invoke, with typed arguments and results).

What to put here:
    - Tool declarations, their argument schemas, and handlers that validate
      input and delegate execution to an application ``service_interface``.

What NOT to put here:
    - Business logic or use-case orchestration: the handler parses/validates the
      request and calls an application service; the real work happens there.
"""

from .extract_jira_tasks_controller import ExtractJiraTasksToolController
from .extract_trello_tasks_controller import ExtractTrelloTasksToolController
from .get_dossier_controller import GetDossierToolController
from .jira_auth_controller import JiraAuthToolController
from .ping_controller import PingToolController
from .search_connector_controller import SearchConnectorToolController
from .slack_auth_controller import SlackAuthToolController
from .slack_workspace_search_controller import SlackWorkspaceSearchToolController
from .trello_auth_controller import TrelloAuthToolController

__all__ = [
    "PingToolController",
    "ExtractJiraTasksToolController",
    "ExtractTrelloTasksToolController",
    "GetDossierToolController",
    "JiraAuthToolController",
    "SearchConnectorToolController",
    "SlackAuthToolController",
    "SlackWorkspaceSearchToolController",
    "TrelloAuthToolController",
]
