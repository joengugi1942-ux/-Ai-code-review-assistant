"""
Security scanner for detecting secrets and unsafe patterns in code.

Currently detects hard-coded AWS secret keys. Can be extended with more patterns.
"""

from app.schemas.file import ParsedFile
from app.schemas.review import ReviewIssue


class SecurityScanner:
    """Scanner for detecting security issues in code."""

    def scan(self, parsed: ParsedFile) -> list[ReviewIssue]:
        """
        Scan parsed file for security issues.
        
        Checks for hard-coded secrets, unsafe patterns, and other vulnerabilities.
        """
        issues: list[ReviewIssue] = []
        if "AWS_SECRET_ACCESS_KEY" in parsed.content:
            issues.append(
                ReviewIssue(
                    file=parsed.filename,
                    line=None,
                    severity="high",
                    message="Possible hard-coded AWS secret key detected.",
                    suggestion="Move secrets to a secure secret manager or environment variables.",
                    category="secrets",
                )
            )
        return issues




