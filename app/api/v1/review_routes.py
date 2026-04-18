"""
Review API endpoints for code analysis.

Provides endpoints to review code via:
- POST /: Review code sent in request body
- POST /upload: Upload and review a file
"""

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
    """
    Review code sent in the request body.
    
    Uses the ReviewEngine to analyze the code and return issues.
    """
    engine = ReviewEngine()
    return await engine.review_code(payload)


@router.post("/upload", response_model=ReviewResponse)
async def review_uploaded_file(
    file: UploadFile,
    api_key: str = Depends(get_current_api_key),
) -> ReviewResponse:
    """
    Upload and review a code file.
    
    Supports any text-based file. Performs security scanning and basic analysis.
    """
    engine = ReviewEngine()
    return await engine.review_uploaded_file(file)




