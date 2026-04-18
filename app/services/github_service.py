from loguru import logger

from app.schemas.github import GithubPRRequest, GithubRepoRequest, GithubReviewResponse
from app.schemas.review import ReviewIssue, ReviewSummary, ReviewTarget
from app.services.github_client import GithubClient
from app.services.review_engine import ReviewEngine


class GithubService:
    def __init__(self, token: str | None = None):
        self.github_client = GithubClient(token=token)
        self.review_engine = ReviewEngine()

    async def review_pr(self, payload: GithubPRRequest) -> GithubReviewResponse:
        pr_state = (payload.pr_state or "open").lower()
        logger.info(f"Reviewing PR: {payload.owner}/{payload.repo}#{payload.pr_number} (state: {pr_state})")

        try:
            if pr_state == "merged":
                return await self._review_merged_pr(payload)
            else:
                return await self._review_open_pr(payload)
        except Exception as e:
            logger.error(f"Failed to review PR: {e}")
            return GithubReviewResponse(issues=[], summary=ReviewSummary(summary=f"Error: {str(e)}"))

    async def _review_open_pr(self, payload: GithubPRRequest) -> GithubReviewResponse:
        pr_details = await self.github_client.get_pr_details(
            payload.owner, payload.repo, payload.pr_number
        )
        base_sha = payload.base_sha or pr_details.get("base", {}).get("sha")
        head_sha = payload.head_sha or pr_details.get("head", {}).get("sha")

        files_data = await self.github_client.get_pr_files(
            payload.owner, payload.repo, payload.pr_number
        )

        return await self._process_files(files_data, base_sha, head_sha, payload)

    async def _review_merged_pr(self, payload: GithubPRRequest) -> GithubReviewResponse:
        pr_details = await self.github_client.get_pr_details(
            payload.owner, payload.repo, payload.pr_number
        )

        merge_sha = pr_details.get("merge_commit_sha")
        base_sha = payload.base_sha or pr_details.get("base", {}).get("sha")
        head_sha = payload.head_sha or merge_sha or pr_details.get("head", {}).get("sha")

        if not merge_sha:
            logger.warning(f"PR #{payload.pr_number} may not be merged, no merge commit SHA found")

        try:
            compare_result = await self.github_client.compare_commits(
                payload.owner, payload.repo, base_sha, head_sha
            )
            files_data = compare_result.get("files", [])
            if files_data:
                return await self._process_files(files_data, base_sha, head_sha, payload)
        except Exception as e:
            logger.warning(f"Compare API failed, falling back to commit files: {e}")

        files_data = await self.github_client.get_commit_files(
            payload.owner, payload.repo, head_sha
        )
        return await self._process_files(files_data, base_sha, head_sha, payload)

    async def _process_files(
        self, files_data: list[dict], base_sha: str, head_sha: str, payload: GithubPRRequest
    ) -> GithubReviewResponse:
        targets: list[ReviewTarget] = []
        issues: list[ReviewIssue] = []

        for file_info in files_data:
            filename = file_info.get("filename", "")
            status = file_info.get("status", "modified")

            if status == "removed":
                continue

            patch = file_info.get("patch", "")
            if not patch:
                try:
                    content = await self.github_client.get_file_content(
                        payload.owner, payload.repo, filename, head_sha
                    )
                except Exception:
                    content = ""
            else:
                content = patch

            if content:
                targets.append(
                    ReviewTarget(
                        filename=filename,
                        language=self._get_language(filename),
                        content=content,
                    )
                )

        if targets:
            from app.schemas.review import ReviewRequest

            review_request = ReviewRequest(targets=targets)
            review_response = await self.review_engine.review_code(review_request)
            issues = review_response.issues
            logger.info(f"Found {len(issues)} issues in {len(targets)} files")

        return GithubReviewResponse(
            issues=issues,
            summary=ReviewSummary(summary=f"Reviewed {len(targets)} files"),
        )

    def _get_language(self, filename: str) -> str | None:
        ext = filename.split(".")[-1] if "." in filename else ""
        lang_map = {
            "py": "python",
            "js": "javascript",
            "ts": "typescript",
            "jsx": "javascript",
            "tsx": "typescript",
            "go": "go",
            "rs": "rust",
            "java": "java",
            "kt": "kotlin",
            "rb": "ruby",
            "php": "php",
            "cs": "csharp",
            "cpp": "cpp",
            "c": "c",
            "h": "c",
            "swift": "swift",
            "yml": "yaml",
            "yaml": "yaml",
            "json": "json",
            "md": "markdown",
        }
        return lang_map.get(ext)

    async def review_repo(self, payload: GithubRepoRequest) -> GithubReviewResponse:
        return GithubReviewResponse(issues=[], summary=ReviewSummary(summary="Repo review not implemented"))