import json
from typing import Any

from groq import AsyncGroq
from loguru import logger

from app.core.config import settings
from app.schemas.review import ReviewRequest
from app.services.prompt_builder import PromptBuilder

_MODEL = "llama-3.3-70b-versatile"


class LLMClient:
    """Client for interacting with Groq LLM API for code review."""

    def __init__(self) -> None:
        self._client = AsyncGroq(api_key=settings.groq_api_key)
        self._prompt_builder = PromptBuilder()

    async def review_code(self, payload: ReviewRequest) -> dict[str, Any]:
        """Send code to LLM and return the raw JSON dict for the caller to parse."""
        prompt = self._prompt_builder.build_review_prompt(payload)
        chars = len(prompt)
        logger.debug(
            f"[LLMClient] Prompt built — {len(payload.targets)} file(s), "
            f"{chars} chars (~{chars // 4} tokens)"
        )

        logger.info(f"[LLMClient] Calling Groq ({_MODEL})...")
        completion = await self._client.chat.completions.create(
            model=_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert code reviewer. Respond with JSON only. "
                        "Return a dict with 'issues' (list of objects with keys: "
                        "'file' (str), 'line' (int or null), 'severity' (str: low/medium/high/critical), "
                        "'message' (str), 'suggestion' (str or null), 'category' (str or null), "
                        "'code_snippet' (str — the exact offending line(s) of code, required)) "
                        "and 'summary' (object with 'score' (float 0-100 or null) and 'summary' (str or null))."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=2048,
            response_format={"type": "json_object"},
        )

        content = completion.choices[0].message.content
        usage = completion.usage
        logger.info(
            f"[LLMClient] Response received — "
            f"{usage.prompt_tokens} prompt tokens, {usage.completion_tokens} completion tokens"
        )
        logger.debug(f"[LLMClient] Raw response: {len(content or '')} chars")

        return json.loads(content) if content else {}
