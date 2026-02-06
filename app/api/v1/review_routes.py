from fastapi import APIRouter, Depends, UploadFile

from app.api.deps import get_current_api_key
from app.schemas.review import ReviewRequest, ReviewResponse
from app.services.review_engine import ReviewEngine

router = APIRouter()


@router.post("/", response_model=ReviewResponse)
async def review_code(
    payload: ReviewRequest,
    api_key: str = Depends(get_current_api_key),
) -> ReviewResponse:
    engine = ReviewEngine()
    return await engine.review_code(payload)


@router.post("/upload", response_model=ReviewResponse)
async def review_uploaded_file(
    file: UploadFile,
    api_key: str = Depends(get_current_api_key),
) -> ReviewResponse:
    engine = ReviewEngine()
    return await engine.review_uploaded_file(file)




