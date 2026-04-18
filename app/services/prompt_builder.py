"""
Prompt builder for constructing LLM prompts from review requests.
"""

from app.schemas.review import ReviewRequest


class PromptBuilder:
    """Builds prompts for the LLM from ReviewRequest payloads."""

    def build_review_prompt(self, payload: ReviewRequest) -> str:
        """
        Build a structured prompt for code review.
        
        Includes focus areas if specified and all target files with their content.
        """
        parts: list[str] = ["You are an expert code reviewer."]
        if payload.focus_areas:
            parts.append(f"Focus areas: {', '.join(payload.focus_areas)}.")
        for target in payload.targets:
            parts.append(f"\nFile: {target.filename} (lang={target.language})\n")
            parts.append(target.content)
        return "\n".join(parts)




