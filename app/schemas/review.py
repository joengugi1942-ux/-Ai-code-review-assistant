from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ReviewTarget(BaseModel):
    filename: str
    language: str | None = None
    content: str


class ReviewRequest(BaseModel):
    targets: list[ReviewTarget]
    focus_areas: list[str] | None = None


class ReviewIssue(BaseModel):
    file: str
    line: int | None = None
    severity: str
    message: str
    suggestion: str | None = None
    category: str | None = None
    confidence: float | None = None
    code_snippet: str | None = None


class ReviewSummary(BaseModel):
    score: float | None = None
    summary: str | None = None
    issue_count_by_severity: dict[str, int] | None = None


class ReviewResponse(BaseModel):
    issues: list[ReviewIssue]
    summary: ReviewSummary | None = None


class ConversationCreate(BaseModel):
    title: str | None = None


class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class MessageCreate(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    conversation_id: UUID
    role: str
    content: str
    created_at: datetime
