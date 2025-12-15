from pydantic import BaseModel

from app.schemas.review import ReviewIssue, ReviewSummary


class GithubPRRequest(BaseModel):
    owner: str
    repo: str
    pr_number: int


class GithubRepoRequest(BaseModel):
    owner: str
    repo: str
    branch: str | None = None
    path: str | None = None


class GithubReviewResponse(BaseModel):
    issues: list[ReviewIssue]
    summary: ReviewSummary | None = None



