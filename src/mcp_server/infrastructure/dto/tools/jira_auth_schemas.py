from pydantic import BaseModel, Field

class GenerateJiraAuthResponse(BaseModel):
    auth_url: str = Field(
        title="Jira Authorization URL",
        description="The URL for the Jira authorization page",
    )
    user_id: str = Field(
        title="User ID",
        description="The user ID for the Jira that is authenticated",
    )