import pytest

from app.schemas.review import ReviewRequest, ReviewTarget
from app.services.review_engine import ReviewEngine


@pytest.mark.asyncio
async def test_review_engine_basic() -> None:
    engine = ReviewEngine()
    payload = ReviewRequest(
        targets=[ReviewTarget(filename="example.py", language="python", content="print('hi')")]
    )
    response = await engine.review_code(payload)
    assert response.issues is not None



