from mcp.server.fastmcp.prompts.base import Prompt, PromptArgument

from mcp_server.domain import CollaborationToolEnum
from mcp_server.infrastructure.controllers import BaseController


class ExtractTasksPromptController(BaseController):
    """Controller class that provides the MCP with prompts to extracts tasks from the collaboration tools."""

    __tool_map = {
        CollaborationToolEnum.JIRA: (
            "get_pending_jira_issues",
            "Call the `get_pending_jira_issues` tool with assignee='{assignee}' "
            "and your user_id to retrieve all pending Jira issues assigned to that user.",
        ),
        CollaborationToolEnum.TRELLO: (
            "get_pending_trello_cards",
            "Call the `get_pending_trello_cards` tool with assignee='{assignee}' "
            "and your user_id to retrieve all pending Trello cards assigned to that user.",
        ),
    }

    def register(self) -> None:
        self._server.add_prompt(
            Prompt(
                name="extract_pending_tasks",
                title="Extract Pending Tasks",
                description=("Extract pending tasks assigned to"
                             "a certain assignee from the specified collaboration tool."),
                fn=self.extract_pending_tasks,
                arguments=[
                    PromptArgument(
                        name="assignee",
                        description="Id of the pending tasks' assignee",
                        required=True
                    ),
                    PromptArgument(
                        name="collaboration_tool",
                        description="Collaboration tool to extract tasks from",
                        required=False
                    )
                ]
            )
        )

    async def extract_pending_tasks(
            self,
            assignee: str,
            collaboration_tool: CollaborationToolEnum = CollaborationToolEnum.JIRA
    ) -> str:
        """
        Prompt to give the agent context in order to extract tasks from the collaboration tool using the MCP tools.

        Args:
            assignee (str): Id of the assignee of the collaboration tool.
            collaboration_tool (CollaborationToolEnum): Id of the collaboration tool.

        Returns:
            str: The final prompt.
        """

        tool_name, tool_instruction = self.__tool_map[collaboration_tool]
        tool_instruction = tool_instruction.format(assignee=assignee)

        return (
            f"You are a task extraction assistant. Your goal is to retrieve all pending tasks "
            f"assigned to '{assignee}' from {collaboration_tool.value}.\n\n"
            f"Use the following MCP tool to fetch the data:\n"
            f"- Tool: `{tool_name}`\n"
            f"- {tool_instruction}\n\n"
            f"Once you have the results, present them clearly listing each task with its "
            f"id, title, status, and any other relevant fields available."
        )