from fastapi import UploadFile

from app.ai.llm_client import LLMClient
from app.ai.response_parser import AIResponseParser
from app.schemas.review import ReviewRequest, ReviewResponse
from app.services.code_parser import CodeParser
from app.services.security_scan import SecurityScanner


class ReviewEngine:
    def __init__(self) -> None:
        self.llm = LLMClient()
        self.parser = CodeParser()
        self.security_scanner = SecurityScanner()
        self.response_parser = AIResponseParser()

    async def review_code(self, payload: ReviewRequest) -> ReviewResponse:
        # Placeholder basic flow: delegate to LLM and parse the response
        ai_raw = await self.llm.review_code(payload)
        return self.response_parser.parse_review_response(ai_raw)

    async def review_uploaded_file(self, file: UploadFile) -> ReviewResponse:
        content = (await file.read()).decode("utf-8", errors="ignore")
        parsed = self.parser.parse(file.filename, content)
        security_issues = self.security_scanner.scan(parsed)
        # Minimal combination of security issues with empty AI review
        return ReviewResponse(issues=security_issues, summary=None)




