from fastapi import APIRouter, Depends

from app.api.deps import get_current_api_key
from app.schemas.github import GithubPRRequest, GithubRepoRequest, GithubReviewResponse
from app.services.github_service import GithubService

router = APIRouter()


@router.post("/pr", response_model=GithubReviewResponse)
async def review_pull_request(
    payload: GithubPRRequest,
    api_key: str = Depends(get_current_api_key),
) -> GithubReviewResponse:
    service = GithubService()
    return await service.review_pr(payload)


@router.post("/repo", response_model=GithubReviewResponse)
async def review_repository(
    payload: GithubRepoRequest,
    api_key: str = Depends(get_current_api_key),
) -> GithubReviewResponse:
    service = GithubService()
    return await service.review_repo(payload)




