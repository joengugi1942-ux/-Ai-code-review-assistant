from fastapi import APIRouter, Depends, UploadFile

from app.api.deps import get_current_api_key, get_review_engine
from app.schemas.review import ReviewRequest, ReviewResponse
from app.services.review_engine import ReviewEngine

router = APIRouter()


@router.post("/", response_model=ReviewResponse)
async def review_code(
    payload: ReviewRequest,
    _: str = Depends(get_current_api_key),
    engine: ReviewEngine = Depends(get_review_engine),
) -> ReviewResponse:
    return await engine.review_code(payload)


@router.post("/upload", response_model=ReviewResponse)
async def review_uploaded_file(
    file: UploadFile,
    _: str = Depends(get_current_api_key),
    engine: ReviewEngine = Depends(get_review_engine),
) -> ReviewResponse:
    return await engine.review_uploaded_file(file)
