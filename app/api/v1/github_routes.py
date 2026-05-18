from fastapi import APIRouter, Depends
from loguru import logger

from app.api.deps import get_current_api_key, get_github_service
from app.schemas.github import GithubPRRequest, GithubRepoRequest, GithubReviewResponse
from app.services.github_service import GithubService

router = APIRouter()


@router.post("/pr", response_model=GithubReviewResponse)
async def review_pull_request(
    payload: GithubPRRequest,
    _: str = Depends(get_current_api_key),
    service: GithubService = Depends(get_github_service),
) -> GithubReviewResponse:
    logger.info(f"[Route] POST /github/pr  {payload.owner}/{payload.repo}#{payload.pr_number} ({payload.pr_state})")
    result = await service.review_pr(payload)
    logger.info(f"[Route] POST /github/pr  → {len(result.issues)} issue(s), score={result.summary.score if result.summary else 'N/A'}")
    return result


@router.post("/repo", response_model=GithubReviewResponse)
async def review_repository(
    payload: GithubRepoRequest,
    _: str = Depends(get_current_api_key),
    service: GithubService = Depends(get_github_service),
) -> GithubReviewResponse:
    logger.info(f"[Route] POST /github/repo  {payload.owner}/{payload.repo} branch={payload.branch or 'default'}")
    result = await service.review_repo(payload)
    logger.info(f"[Route] POST /github/repo  → {len(result.issues)} issue(s), score={result.summary.score if result.summary else 'N/A'}")
    return result
