"""
Prompt builder for constructing LLM prompts from review requests.
"""

from pathlib import Path
from typing import Any

from app.schemas.review import ReviewRequest


class PromptBuilder:
    """Builds prompts for the LLM from ReviewRequest payloads."""

    def __init__(self) -> None:
        self._prompt_cache: dict[str, str] = {}

    def build_review_prompt(self, payload: ReviewRequest) -> str:
        """
        Build a structured prompt for code review.
        
        Includes focus areas, prompt template, and all target files with their content.
        """
        parts: list[str] = []
        
        parts.append(self._get_base_prompt())
        
        if payload.focus_areas:
            parts.append(f"\n## Focus Areas\n{', '.join(payload.focus_areas)}.")
        
        parts.append("\n## Files to Review\n")
        for target in payload.targets:
            parts.append(f"### File: {target.filename}")
            if target.language:
                parts.append(f"Language: {target.language}")
            parts.append("\n```")
            parts.append(target.content)
            parts.append("\n```\n")
        
        return "\n".join(parts)

    def _get_base_prompt(self) -> str:
        """Get base prompt from file or use default."""
        prompt_file = Path(__file__).parent.parent / "ai" / "prompts" / "code_review.md"
        
        if prompt_file.exists():
            try:
                return prompt_file.read_text(encoding="utf-8")
            except Exception:
                pass
        
        return self._default_prompt()

    def _default_prompt(self) -> str:
        """Default prompt if file not found."""
        return """You are an expert software engineer performing a thorough code review.

Output JSON with:
- issues: list of {file, line, severity, category, message, suggestion, confidence}
- summary: {score, summary}

Severity (STRICT):
- critical: security, data loss, crashes (-20)
- high: logic bugs, runtime errors (-10)
- medium: performance, maintainability (-5)
- low: minor issues (-1)
- info: suggestions only (0)

Scoring: 100 - deductions (min 0)

DO NOT return generic advice. All suggestions must be specific and actionable."""

    def extract_snippet(self, content: str, line: int | None, context: int = 5) -> str | None:
        """
        Extract focused snippet around the issue line.
        
        Args:
            content: Full file content
            line: Line number of the issue (1-indexed)
            context: Number of lines before/after to include (default 5)
        
        Returns:
            Extracted snippet or None if line not available
        """
        if line is None:
            return self._extract_fallback_snippet(content)
        
        lines = content.split("\n")
        
        start = max(0, line - context - 1)
        end = min(len(lines), line + context)
        
        snippet_lines = lines[start:end]
        return "\n".join(snippet_lines)

    def _extract_fallback_snippet(self, content: str) -> str | None:
        """Extract first lines as fallback when no line number."""
        lines = content.split("\n")
        if not lines:
            return None
        
        first_lines = lines[:15]
        return "\n".join(first_lines)