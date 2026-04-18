"""
GitHub integration schemas for PR and repository analysis.

Defines request and response models for GitHub API endpoints.
"""

from pydantic import BaseModel

from app.schemas.review import ReviewIssue, ReviewSummary


class GithubPRRequest(BaseModel):
    """Request to analyze a GitHub pull request."""

    owner: str
    repo: str
    pr_number: int
    pr_state: str | None = "open"  # "open" or "merged"
    base_sha: str | None = None  # optional custom base commit
    head_sha: str | None = None  # optional custom head commit


class GithubRepoRequest(BaseModel):
    """Request to analyze a GitHub repository."""

    owner: str
    repo: str
    branch: str | None = None
    path: str | None = None


class GithubReviewResponse(BaseModel):
    """Response for GitHub review requests."""

    issues: list[ReviewIssue]
    summary: ReviewSummary | None = None



