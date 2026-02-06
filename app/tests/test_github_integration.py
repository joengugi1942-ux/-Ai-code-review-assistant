import pytest

from app.schemas.github import GithubPRRequest
from app.services.github_service import GithubService


@pytest.mark.asyncio
async def test_github_service_pr_stub() -> None:
    service = GithubService()
    payload = GithubPRRequest(owner="o", repo="r", pr_number=1)
    response = await service.review_pr(payload)
    assert response.issues == []




