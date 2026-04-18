"""
LLM client for AI-powered code review using Groq.

Uses the Llama model to analyze code and detect issues.
"""

from typing import Any

from groq import AsyncGroq

from app.ai.response_parser import AIResponseParser
from app.core.config import settings
from app.schemas.review import ReviewRequest
from app.services.prompt_builder import PromptBuilder


class LLMClient:
    """Client for interacting with Groq LLM API for code review."""

    def __init__(self) -> None:
        self._client = AsyncGroq(api_key=settings.groq_api_key)
        self._prompt_builder = PromptBuilder()
        self._parser = AIResponseParser()

    async def review_code(self, payload: ReviewRequest) -> dict[str, Any]:
        """
        Send code to LLM for review.
        
        Builds a prompt, sends to Groq Llama model, and returns parsed response.
        """
        prompt = self._prompt_builder.build_review_prompt(payload)
        
        completion = await self._client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert code reviewer. Respond with JSON only. "
                        "Return a dict with 'issues' (list of objects with keys: "
                        "'file' (str), 'line' (int or null), 'severity' (str: low/medium/high), "
                        "'message' (str), 'suggestion' (str or null), 'category' (str or null)) "
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
        import json
        
        data = json.loads(content) if content else {}
        return self._parser.parse_review_response(data).model_dump()
