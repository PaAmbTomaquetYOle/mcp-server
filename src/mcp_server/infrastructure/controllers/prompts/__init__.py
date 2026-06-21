"""MCP prompt controllers.

Defines and registers the server's MCP *prompts* (reusable prompt templates
that clients can request).

What to put here:
    - Prompt declarations and their handlers/builders, wiring each prompt to
      the relevant application use case when it needs data.

What NOT to put here:
    - Business logic: build the prompt and delegate any real work to an
      application service. No direct IO or SDK calls beyond the MCP framework.
"""

from .extract_jira_tasks_prompt_controller import ExtractJiraTasksPromptController
from .extract_trello_tasks_prompt_controller import ExtractTrelloTasksPromptController
from .jira_login_prompt_controller import JiraLoginPromptController
from .trello_login_prompt_controller import TrelloLoginPromptController

__all__ = [
    "ExtractJiraTasksPromptController",
    "ExtractTrelloTasksPromptController",
    "JiraLoginPromptController",
    "TrelloLoginPromptController",
]