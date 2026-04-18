"""
GitHub API endpoints for repository and pull request analysis.

Provides endpoints to:
- POST /pr: Analyze a GitHub pull request
- POST /repo: Analyze a GitHub repository

Requires X-API-Key header for authentication.
"""

from fastapi import APIRouter, Depends

from app.api.deps import get_current_api_key
from app.core.config import settings
from app.schemas.github import GithubPRRequest, GithubRepoRequest, GithubReviewResponse
from app.services.github_service import GithubService

router = APIRouter()


@router.post("/pr", response_model=GithubReviewResponse)
async def review_pull_request(
    payload: GithubPRRequest,
    api_key: str = Depends(get_current_api_key),
) -> GithubReviewResponse:
    """
    Analyze a GitHub pull request.
    
    Fetches PR diff and files, then runs AI code review on the changes.
    """
    service = GithubService(token=settings.github_token)
    return await service.review_pr(payload)


@router.post("/repo", response_model=GithubReviewResponse)
async def review_repository(
    payload: GithubRepoRequest,
    api_key: str = Depends(get_current_api_key),
) -> GithubReviewResponse:
    """
    Analyze a GitHub repository.
    
    Fetches repository files and runs AI code review on them.
    """
    service = GithubService(token=settings.github_token)
    return await service.review_repo(payload)




