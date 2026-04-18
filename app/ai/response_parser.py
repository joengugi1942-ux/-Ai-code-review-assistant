"""
AI response parser for converting LLM responses to structured review data.
"""

from typing import Any

from app.schemas.review import ReviewIssue, ReviewResponse, ReviewSummary


class AIResponseParser:
    """Parses raw LLM responses into ReviewResponse objects."""

    def parse_review_response(self, raw: Any) -> ReviewResponse:
        """
        Parse LLM response into ReviewResponse.
        
        Expects a dict with 'issues' and 'summary' keys.
        """
        data = raw or {}
        issues_raw = data.get("issues", [])
        issues: list[ReviewIssue] = []
        for item in issues_raw:
            issues.append(
                ReviewIssue(
                    file=item.get("file", ""),
                    line=item.get("line"),
                    severity=item.get("severity", "info"),
                    message=item.get("message", ""),
                    suggestion=item.get("suggestion"),
                    category=item.get("category"),
                )
            )
        summary_raw = data.get("summary") or {}
        summary = (
            ReviewSummary(
                score=summary_raw.get("score"),
                summary=summary_raw.get("summary"),
            )
            if summary_raw
            else None
        )
        return ReviewResponse(issues=issues, summary=summary)




