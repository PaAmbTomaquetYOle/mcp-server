from pydantic import BaseModel, Field


class PersonInfo(BaseModel):
    person_id: str = Field(title="Person ID")
    name: str = Field(title="Name")
    department: str | None = Field(default=None, title="Department")


class TopicInfo(BaseModel):
    name: str = Field(title="Topic Name")
    description: str | None = Field(default=None, title="Topic Description")


class DocumentInfo(BaseModel):
    document_id: str = Field(title="Document ID")
    title: str = Field(title="Title")
    url: str | None = Field(default=None, title="URL")
    source: str | None = Field(default=None, title="Source")


class ExpertResult(BaseModel):
    person: PersonInfo = Field(title="Person")
    topic: str = Field(title="Topic")
    score: float = Field(title="Expertise Score")


class QueryExpertsResponse(BaseModel):
    topic: str = Field(title="Queried Topic")
    experts: list[ExpertResult] = Field(default_factory=list, title="Matching Experts")
    count: int = Field(title="Result Count")


class AddInteractionResponse(BaseModel):
    event_id: str = Field(title="Event ID")
    status: str = Field(title="Publish Status")


class KnowledgeMapResponse(BaseModel):
    person: PersonInfo = Field(title="Person")
    topics: list[TopicInfo] = Field(default_factory=list, title="Known Topics")
    documents: list[DocumentInfo] = Field(default_factory=list, title="Related Documents")
