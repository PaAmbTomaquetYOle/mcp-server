from typing import Literal

from pydantic import BaseModel, Field


class DossierContact(BaseModel):
    name: str
    role: str
    email: str
    relationship: str


class DossierPendingTask(BaseModel):
    description: str
    priority: str
    deadline: str | None = None


class DossierKnowledgeArea(BaseModel):
    topic: str
    description: str
    expertise_level: str


class DossierSection(BaseModel):
    title: str
    section_type: Literal["responsibilities", "contacts", "pending_tasks", "knowledge_areas"]
    responsibilities: list[str] | None = None
    contacts: list[DossierContact] | None = None
    tasks: list[DossierPendingTask] | None = None
    areas: list[DossierKnowledgeArea] | None = None


class DossierSearchResult(BaseModel):
    id: str = Field(title="Dossier ID")
    process_id: str = Field(title="Process ID")
    state: str = Field(title="Dossier State")
    created_at: str = Field(title="Created At")
    summary: str | None = Field(default=None, title="Summary")
    sections: list[DossierSection] = Field(default_factory=list, title="Sections")
    employee_id: str = Field(title="Employee ID (Slack user ID)")
    manager_id: str = Field(title="Manager ID (Slack user ID)")
    employee_name: str | None = Field(default=None, title="Employee Name")
    manager_name: str | None = Field(default=None, title="Manager Name")


class GetDossierResponse(BaseModel):
    results: list[DossierSearchResult] = Field(
        default_factory=list,
        title="Matching Dossiers",
        description="Handover dossiers matching the search criteria.",
    )
    count: int = Field(title="Result Count")


class GenerateDossierResponse(BaseModel):
    summary: str | None = Field(default=None, title="Summary")
    sections: list[DossierSection] = Field(default_factory=list, title="Sections")
