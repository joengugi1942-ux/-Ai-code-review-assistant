from pydantic import BaseModel


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


class ReviewSummary(BaseModel):
    score: float | None = None
    summary: str | None = None


class ReviewResponse(BaseModel):
    issues: list[ReviewIssue]
    summary: ReviewSummary | None = None



