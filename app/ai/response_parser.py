"""
AI response parser for converting LLM responses to structured review data.
"""

from typing import Any

from app.schemas.review import ReviewIssue, ReviewResponse, ReviewSummary


VALID_SEVERITIES = {"critical", "high", "medium", "low", "info"}
SEVERITY_SCORES = {"critical": 20, "high": 10, "medium": 5, "low": 1, "info": 0}
SEVERITY_TEXT_MAP = {"high": 0.8, "medium": 0.6, "low": 0.4, "critical": 0.95, "info": 0.3}


class AIResponseParser:
    """Parses raw LLM responses into ReviewResponse objects."""

    def parse_review_response(self, raw: Any) -> ReviewResponse:
        """
        Parse LLM response into ReviewResponse.
        
        Expects a dict with 'issues' and 'summary' keys.
        Includes severity normalization, confidence handling, and scoring.
        """
        data = raw or {}
        issues_raw = data.get("issues", [])
        issues: list[ReviewIssue] = []
        
        for item in issues_raw:
            issue = self._parse_issue(item)
            issues.append(issue)
        
        summary = self._build_summary(issues, data.get("summary"))
        
        return ReviewResponse(issues=issues, summary=summary)

    def _parse_issue(self, item: dict[str, Any]) -> ReviewIssue:
        """Parse a single issue with normalization."""
        severity = self._normalize_severity(item.get("severity"))
        confidence = self._normalize_confidence(item.get("confidence"), severity)
        
        return ReviewIssue(
            file=item.get("file", ""),
            line=item.get("line"),
            severity=severity,
            message=item.get("message", ""),
            suggestion=item.get("suggestion"),
            category=item.get("category"),
            confidence=confidence,
            code_snippet=item.get("code_snippet"),
        )

    def _normalize_severity(self, severity: Any) -> str:
        """Normalize severity to valid level with fallback."""
        if severity is None:
            return "low"
        
        severity_str = str(severity).lower().strip()
        
        if severity_str in VALID_SEVERITIES:
            return severity_str
        
        keywords_critical = {"security", "injection", "xss", "sqli", "leak", "auth", "password", "secret", "crash", "deadlock"}
        keywords_high = {"bug", "error", "incorrect", "wrong", "exception", "unhandled"}
        
        if "critical" in severity_str:
            if any(kw in severity_str for kw in keywords_critical):
                return "critical"
            return "high"
        
        if "high" in severity_str or any(kw in severity_str for kw in keywords_high):
            return "high"
        
        if "medium" in severity_str:
            return "medium"
        
        if "low" in severity_str or "info" in severity_str:
            return severity_str if severity_str in VALID_SEVERITIES else "low"
        
        return "low"

    def _normalize_confidence(self, confidence: Any, severity: str) -> float | None:
        """Normalize confidence to 0-1 range."""
        if confidence is None:
            return SEVERITY_TEXT_MAP.get(severity, 0.5)
        
        if isinstance(confidence, str):
            return SEVERITY_TEXT_MAP.get(confidence.lower(), 0.5)
        
        try:
            conf = float(confidence)
            return round(min(max(conf, 0), 1), 2)
        except (ValueError, TypeError):
            return SEVERITY_TEXT_MAP.get(severity, 0.5)

    def _build_summary(self, issues: list[ReviewIssue], summary_raw: dict[str, Any] | None) -> ReviewSummary:
        """Build summary with scoring and issue counts."""
        issue_counts = self._count_by_severity(issues)
        score = self._calculate_score(issues)
        
        user_summary = summary_raw.get("summary") if summary_raw else None
        
        return ReviewSummary(
            score=score,
            summary=user_summary,
            issue_count_by_severity=issue_counts,
        )

    def _count_by_severity(self, issues: list[ReviewIssue]) -> dict[str, int]:
        """Count issues by severity level."""
        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
        for issue in issues:
            severity = issue.severity if issue.severity in counts else "low"
            counts[severity] += 1
        return counts

    def _calculate_score(self, issues: list[ReviewIssue]) -> float:
        """Calculate overall score (0-100)."""
        score = 100
        for issue in issues:
            severity = issue.severity if issue.severity in SEVERITY_SCORES else "low"
            score -= SEVERITY_SCORES.get(severity, 0)
        return max(0, score)