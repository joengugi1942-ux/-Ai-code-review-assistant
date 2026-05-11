from functools import lru_cache

from fastapi import Depends

from app.core.security import get_api_key


def get_current_api_key(api_key: str = Depends(get_api_key)) -> str:
    return api_key


@lru_cache(maxsize=1)
def get_review_engine():
    from app.services.review_engine import ReviewEngine
    return ReviewEngine()


@lru_cache(maxsize=1)
def get_github_service():
    from app.services.github_service import GithubService
    from app.core.config import settings
    return GithubService(token=settings.github_token)
