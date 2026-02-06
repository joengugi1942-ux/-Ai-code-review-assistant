from app.schemas.file import ParsedFile
from app.schemas.review import ReviewIssue


class SecurityScanner:
    def scan(self, parsed: ParsedFile) -> list[ReviewIssue]:
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




