"""
Review engine for AI-powered code analysis.

Coordinates code parsing, security scanning, and LLM-based review.
"""

from fastapi import UploadFile
from loguru import logger

from app.ai.llm_client import LLMClient
from app.ai.response_parser import AIResponseParser
from app.schemas.file import ParsedFile
from app.schemas.review import ReviewRequest, ReviewResponse
from app.services.code_parser import CodeParser
from app.services.security_scan import SecurityScanner


class ReviewEngine:
    """Main engine for reviewing code using AI and security scanning."""

    def __init__(self) -> None:
        self.llm = LLMClient()
        self.parser = CodeParser()
        self.security_scanner = SecurityScanner()
        self.response_parser = AIResponseParser()

    async def review_code(self, payload: ReviewRequest) -> ReviewResponse:
        """
        Review code from a ReviewRequest payload.

        Runs both pattern-based security scanning and LLM analysis on every
        target, then merges the results into a single scored response.
        """
        logger.info(f"[ReviewEngine] Starting review: {len(payload.targets)} file(s)")

        # Pattern-based security scan (fast, runs on every path)
        security_issues = []
        for target in payload.targets:
            parsed = ParsedFile(
                filename=target.filename,
                language=target.language or "unknown",
                content=target.content,
            )
            found = self.security_scanner.scan(parsed)
            if found:
                logger.debug(f"[SecurityScanner] {target.filename}: {len(found)} pattern match(es)")
            security_issues.extend(found)

        if security_issues:
            logger.info(f"[SecurityScanner] Total: {len(security_issues)} issue(s) across all files")

        # LLM deep review
        logger.debug("[ReviewEngine] Sending to LLM for deep review")
        ai_raw = await self.llm.review_code(payload)
        response = self.response_parser.parse_review_response(ai_raw)

        # Merge: security issues first so they surface at the top
        if security_issues:
            response.issues = security_issues + response.issues
            response.summary = self.response_parser._build_summary(response.issues, None)

        logger.info(
            f"[ReviewEngine] Done — {len(response.issues)} total issue(s), "
            f"score={response.summary.score if response.summary else 'N/A'}"
        )
        return response

    async def review_uploaded_file(self, file: UploadFile) -> ReviewResponse:
        """
        Review an uploaded file.

        Parses the file, runs security scanning, and returns results.
        """
        logger.info(f"[ReviewEngine] Reviewing uploaded file: {file.filename}")
        content = (await file.read()).decode("utf-8", errors="ignore")
        parsed = self.parser.parse(file.filename, content)
        logger.debug(f"[ReviewEngine] Parsed {file.filename}: {len(content)} chars")
        security_issues = self.security_scanner.scan(parsed)
        logger.info(f"[ReviewEngine] Upload scan complete: {len(security_issues)} issue(s)")
        return ReviewResponse(issues=security_issues, summary=None)
