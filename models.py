"""Public input/output contracts shared by REST, CLI and business functions."""
from datetime import date, datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

Question = Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=2000)]


class Message(BaseModel):
    model_config = ConfigDict(extra="allow", strict=True)
    id: str = Field(min_length=1)
    sim_ts: str
    channel: str = Field(min_length=1)
    author: str = Field(min_length=1)
    text: str

    @field_validator("sim_ts")
    @classmethod
    def timestamp(cls, value):
        datetime.fromisoformat(value)
        return value


class Task(BaseModel):
    model_config = ConfigDict(extra="forbid")
    task: str = Field(min_length=1)
    owner: str | None = None
    due: date | None = None
    priority: Literal["high", "medium", "low"]


class Alert(BaseModel):
    message_id: str
    severity: Literal["high", "medium"]
    channel: str
    matched: list[str]
    text: str


class Answer(BaseModel):
    question: str
    answer: str
    sources: list[str]
    top_score: float = Field(ge=0, le=1)
    refused: bool
    mode: str


class Digest(BaseModel):
    message_count: int = Field(ge=0)
    alerts: list[Alert]
    summaries: dict[str, str]
    tasks: list[Task]
    faq: list[Answer]
    mode: str


class AskRequest(BaseModel):
    question: Question
    k: int = Field(default=2, ge=1, le=5)


class SummarizeRequest(BaseModel):
    channel: str = Field(default="#incidents", min_length=1, max_length=100)

    @field_validator("channel")
    @classmethod
    def normalize(cls, value):
        value = value.strip()
        if not value.strip("#"):
            raise ValueError("channel cannot be blank")
        return value if value.startswith("#") else "#" + value


class DigestRequest(BaseModel):
    faq_queries: list[Question] = Field(default_factory=list, max_length=10)


class Health(BaseModel):
    status: Literal["ok"] = "ok"
    version: str


class Ready(BaseModel):
    status: Literal["ready"] = "ready"
    messages: int
    kb_chunks: int


class Alerts(BaseModel):
    alerts: list[Alert]


class Tasks(BaseModel):
    tasks: list[Task]


class Summary(BaseModel):
    channel: str
    summary: str
    mode: str
