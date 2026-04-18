"""
Review schemas for request and response models.

Defines data structures for:
- ReviewRequest: Input for code review
- ReviewResponse: Output with issues and summary
"""

from pydantic import BaseModel


class ReviewTarget(BaseModel):
    """A single file to be reviewed."""

    filename: str
    language: str | None = None
    content: str


class ReviewRequest(BaseModel):
    """Request payload for code review."""

    targets: list[ReviewTarget]
    focus_areas: list[str] | None = None


class ReviewIssue(BaseModel):
    """A single issue found during code review."""

    file: str
    line: int | None = None
    severity: str
    message: str
    suggestion: str | None = None
    category: str | None = None


class ReviewSummary(BaseModel):
    """Summary of the code review."""

    score: float | None = None
    summary: str | None = None


class ReviewResponse(BaseModel):
    """Response containing review issues and summary."""

    issues: list[ReviewIssue]
    summary: ReviewSummary | None = None



