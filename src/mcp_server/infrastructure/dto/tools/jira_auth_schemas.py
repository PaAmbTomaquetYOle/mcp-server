from pydantic import BaseModel, Field


class GenerateJiraAuthResponse(BaseModel):
    auth_url: str = Field(
        title="Jira Authorization URL",
        description="The URL for the Jira authorization page",
    )
    user_id: str = Field(
        title="User ID",
        description="The user ID for Jira that is authenticated",
    )

class CompleteJiraAuthResponse(BaseModel):
    success: bool = Field(
        title="Success",
        description="Whether the Jira authorization was successful",
    )
    user_id: str = Field(
        title="User ID",
        description="The user ID for Jira that is authenticated",
    )
    message: str = Field(
        title="Message",
        description="A message describing the authorization status",
    )