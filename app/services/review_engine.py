"""
Review engine for AI-powered code analysis.

Coordinates code parsing, security scanning, and LLM-based review.
"""

from fastapi import UploadFile

from app.ai.llm_client import LLMClient
from app.ai.response_parser import AIResponseParser
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
        
        Sends code to LLM for analysis and returns parsed review response.
        """
        ai_raw = await self.llm.review_code(payload)
        return self.response_parser.parse_review_response(ai_raw)

    async def review_uploaded_file(self, file: UploadFile) -> ReviewResponse:
        """
        Review an uploaded file.
        
        Parses the file, runs security scanning, and returns results.
        """
        content = (await file.read()).decode("utf-8", errors="ignore")
        parsed = self.parser.parse(file.filename, content)
        security_issues = self.security_scanner.scan(parsed)
        return ReviewResponse(issues=security_issues, summary=None)




