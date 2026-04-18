from pydantic import BaseModel

from app.schemas.review import ReviewIssue, ReviewSummary


class GithubPRRequest(BaseModel):
    owner: str
    repo: str
    pr_number: int
    pr_state: str | None = "open"  # "open" or "merged"
    base_sha: str | None = None  # optional custom base commit
    head_sha: str | None = None  # optional custom head commit


class GithubRepoRequest(BaseModel):
    owner: str
    repo: str
    branch: str | None = None
    path: str | None = None


class GithubReviewResponse(BaseModel):
    issues: list[ReviewIssue]
    summary: ReviewSummary | None = None



