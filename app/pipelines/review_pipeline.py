from app.schemas.review import ReviewRequest, ReviewResponse
from app.services.review_engine import ReviewEngine


class ReviewPipeline:
    def __init__(self) -> None:
        self.engine = ReviewEngine()

    async def run(self, payload: ReviewRequest) -> ReviewResponse:
        return await self.engine.review_code(payload)



