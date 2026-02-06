from typing import Any

import httpx

from app.core.config import settings
from app.schemas.review import ReviewRequest
from app.services.prompt_builder import PromptBuilder


class LLMClient:
    def __init__(self) -> None:
        self._prompt_builder = PromptBuilder()

    async def review_code(self, payload: ReviewRequest) -> Any:
        # This is a stub; wire to OpenAI or other LLM provider later.
        prompt = self._prompt_builder.build_review_prompt(payload)
        _ = prompt  # avoid unused variable for now
        async with httpx.AsyncClient() as client:
            _ = client  # placeholder
        return {"issues": [], "summary": {}}




