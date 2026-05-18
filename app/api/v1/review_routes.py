from fastapi import APIRouter, Depends, UploadFile
from loguru import logger

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
    logger.info(f"[Route] POST /review  files={len(payload.targets)}")
    result = await engine.review_code(payload)
    logger.info(f"[Route] POST /review  → {len(result.issues)} issue(s), score={result.summary.score if result.summary else 'N/A'}")
    return result


@router.post("/upload", response_model=ReviewResponse)
async def review_uploaded_file(
    file: UploadFile,
    _: str = Depends(get_current_api_key),
    engine: ReviewEngine = Depends(get_review_engine),
) -> ReviewResponse:
    logger.info(f"[Route] POST /review/upload  filename={file.filename}")
    result = await engine.review_uploaded_file(file)
    logger.info(f"[Route] POST /review/upload  → {len(result.issues)} issue(s)")
    return result
