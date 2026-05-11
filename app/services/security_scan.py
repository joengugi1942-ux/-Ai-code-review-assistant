import re

from app.schemas.file import ParsedFile
from app.schemas.review import ReviewIssue

# (pattern, label, severity, suggestion)
_PATTERNS: list[tuple[str, str, str, str]] = [
    (
        r"AKIA[0-9A-Z]{16}",
        "AWS Access Key ID",
        "critical",
        "Remove the key and rotate it immediately. Use IAM roles or a secrets manager.",
    ),
    (
        r"(?i)aws.{0,20}secret.{0,20}['\"][0-9a-zA-Z/+]{40}['\"]",
        "AWS Secret Access Key",
        "critical",
        "Remove the key and rotate it immediately. Store in AWS Secrets Manager or SSM.",
    ),
    (
        r"ghp_[A-Za-z0-9]{36}",
        "GitHub Personal Access Token",
        "critical",
        "Revoke the token on GitHub and use environment variables or a vault.",
    ),
    (
        r"ghs_[A-Za-z0-9]{36}",
        "GitHub App Installation Token",
        "critical",
        "Revoke immediately. These tokens should be generated at runtime, not stored.",
    ),
    (
        r"sk-[A-Za-z0-9]{32,}",
        "OpenAI / Groq API Key",
        "critical",
        "Revoke and regenerate the key. Load it from environment variables.",
    ),
    (
        r"-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----",
        "Private Key",
        "critical",
        "Never commit private keys. Remove from repo history and rotate the key pair.",
    ),
    (
        r"(?i)(password|passwd|pwd)\s*=\s*['\"][^'\"]{8,}['\"]",
        "Hard-coded password",
        "high",
        "Move the password to environment variables or a secrets manager.",
    ),
    (
        r"(?i)(secret_?key|signing_?key)\s*=\s*['\"][^'\"]{8,}['\"]",
        "Hard-coded secret key",
        "high",
        "Move the secret to environment variables. Never commit secrets to source control.",
    ),
    (
        r"(?i)(api_?key|apikey)\s*=\s*['\"][A-Za-z0-9_\-]{20,}['\"]",
        "Hard-coded API key",
        "high",
        "Load the key from environment variables or a secrets vault.",
    ),
    (
        r"(?i)Authorization\s*:\s*Bearer\s+[A-Za-z0-9\-_\.]{20,}",
        "Hard-coded Bearer token",
        "high",
        "Do not hard-code authorization tokens. Use runtime token injection.",
    ),
    (
        r"(?i)mongodb(\+srv)?://[^:]+:[^@]+@",
        "MongoDB connection string with credentials",
        "high",
        "Store the connection string in environment variables, not in source code.",
    ),
    (
        r"(?i)(mysql|postgresql|postgres)://[^:]+:[^@]+@",
        "Database connection string with credentials",
        "high",
        "Store the database URL in environment variables, not in source code.",
    ),
    (
        r"(?i)redis://(:[^@]+@)",
        "Redis connection string with password",
        "medium",
        "Store the Redis URL in environment variables.",
    ),
    (
        r"(?i)eval\s*\(",
        "Use of eval()",
        "medium",
        "Avoid eval() — it can execute arbitrary code. Use safe alternatives.",
    ),
    (
        r"(?i)subprocess\.call\(.*shell\s*=\s*True",
        "Shell injection risk",
        "high",
        "Do not use shell=True with user-controlled input. Pass arguments as a list.",
    ),
    (
        r"(?i)os\.system\(",
        "os.system() usage",
        "medium",
        "Prefer subprocess with a list of arguments to avoid shell injection.",
    ),
]

_COMPILED = [(re.compile(pat), label, sev, sugg) for pat, label, sev, sugg in _PATTERNS]


class SecurityScanner:
    """Scanner for detecting security issues and secret leaks in code."""

    def scan(self, parsed: ParsedFile) -> list[ReviewIssue]:
        issues: list[ReviewIssue] = []
        lines = parsed.content.splitlines()

        for pattern, label, severity, suggestion in _COMPILED:
            for lineno, line in enumerate(lines, start=1):
                if pattern.search(line):
                    issues.append(
                        ReviewIssue(
                            file=parsed.filename,
                            line=lineno,
                            severity=severity,
                            message=f"{label} detected.",
                            suggestion=suggestion,
                            category="security",
                        )
                    )

        return issues
