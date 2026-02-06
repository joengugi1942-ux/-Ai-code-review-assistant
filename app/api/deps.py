from fastapi import Depends

from app.core.security import get_api_key


def get_current_api_key(api_key: str = Depends(get_api_key)) -> str:
    return api_key




