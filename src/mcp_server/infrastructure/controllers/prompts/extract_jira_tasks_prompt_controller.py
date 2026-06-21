from mcp.server.fastmcp.prompts.base import Prompt, PromptArgument

from mcp_server.infrastructure.controllers import BaseController


class ExtractJiraTasksPromptController(BaseController):
    """Prompt controller that guides an agent through extracting pending Jira issues."""

    def register(self) -> None:
        self._server.add_prompt(
            Prompt(
                name="extract_pending_jira_tasks",
                title="Extract Pending Jira Tasks",
                description="Extract pending Jira issues assigned to a certain assignee.",
                fn=self.extract_pending_jira_tasks,
                arguments=[
                    PromptArgument(
                        name="assignee",
                        description="Id of the pending tasks' assignee",
                        required=True,
                    ),
                ],
            )
        )

    async def extract_pending_jira_tasks(self, assignee: str) -> str:
        return (
            f"You are a task extraction assistant. Your goal is to retrieve all pending tasks "
            f"assigned to '{assignee}' from JIRA.\n\n"
            f"Use the following MCP tool to fetch the data:\n"
            f"- Tool: `get_pending_jira_issues`\n"
            f"- Call the `get_pending_jira_issues` tool with assignee='{assignee}' "
            f"and your user_id to retrieve all pending Jira issues assigned to that user.\n\n"
            f"Once you have the results, present them clearly listing each task with its "
            f"id, title, status, and any other relevant fields available."
        )
