"""
GitHub service for repository and pull request analysis.

Coordinates with GithubClient to fetch PR/repo data and uses ReviewEngine for AI review.
Supports both open and merged pull requests, with fallback handling for various edge cases.
"""

from loguru import logger

from app.schemas.github import GithubPRRequest, GithubRepoRequest, GithubReviewResponse
from app.schemas.review import ReviewIssue, ReviewSummary, ReviewTarget
from app.services.github_client import GithubClient
from app.services.review_engine import ReviewEngine


class GithubService:
    """
    Service for analyzing GitHub repositories and pull requests.
    
    This service provides high-level operations for reviewing GitHub content:
    - Pull request review (open and merged states)
    - Repository file analysis
    - Language detection for code files
    
    It coordinates the GithubClient for API communication and ReviewEngine
    for AI-powered code analysis.
    
    Attributes:
        github_client: Client for interacting with GitHub REST API
    """

    def __init__(self, token: str | None = None):
        """
        Initialize the GitHub service.
        
        Args:
            token: Optional GitHub personal access token for authenticated requests.
                   If not provided, only public repository data can be accessed.
        """
        self.github_client = GithubClient(token=token)
        self.review_engine = ReviewEngine()

    async def review_pr(self, payload: GithubPRRequest) -> GithubReviewResponse:
        """
        Review a GitHub pull request.
        
        This is the main entry point for PR review. It determines the PR state
        (open or merged) and delegates to the appropriate handler.
        
        Args:
            payload: Request object containing:
                - owner: Repository owner (username or organization)
                - repo: Repository name
                - pr_number: Pull request number
                - pr_state: State of PR ("open" or "merged"), defaults to "open"
                - base_sha: Optional base commit SHA (defaults to PR's base)
                - head_sha: Optional head commit SHA (defaults to PR's head)
        
        Returns:
            GithubReviewResponse containing list of issues found and summary.
            Returns an error response if the review fails.
        
        Note:
            - For open PRs: Uses PR files API to get changes
            - For merged PRs: Uses commit comparison API to get all changes
            - Handles API failures gracefully with fallback strategies
        """
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
        """
        Review an open (unmerged) pull request.
        
        Fetches PR details to get base and head commit SHAs, then retrieves
        the list of changed files from the PR.
        
        Args:
            payload: The PR request with owner, repo, pr_number, and optional SHAs
        
        Returns:
            GithubReviewResponse with analyzed files and issues
        
        Process:
            1. Fetch PR details from GitHub API (base/head commit info)
            2. Determine base_sha (from payload or PR's base branch)
            3. Determine head_sha (from payload or PR's head branch)
            4. Fetch list of changed files from PR files API
            5. Process files through _process_files for review
        """
        logger.debug(f"Fetching PR details for {payload.owner}/{payload.repo}#{payload.pr_number}")
        pr_details = await self.github_client.get_pr_details(
            payload.owner, payload.repo, payload.pr_number
        )
        
        base_sha = payload.base_sha or pr_details.get("base", {}).get("sha")
        head_sha = payload.head_sha or pr_details.get("head", {}).get("sha")

        logger.debug(f"Using base_sha={base_sha}, head_sha={head_sha}")
        
        files_data = await self.github_client.get_pr_files(
            payload.owner, payload.repo, payload.pr_number
        )

        return await self._process_files(files_data, base_sha, head_sha, payload)

    async def _review_merged_pr(self, payload: GithubPRRequest) -> GithubReviewResponse:
        """
        Review a merged pull request.
        
        For merged PRs, we cannot use the PR files API directly as it may return
        incomplete data. Instead, we use the commit comparison API to get all
        changes between the base and the merge commit.
        
        Args:
            payload: The PR request with owner, repo, pr_number, and optional SHAs
        
        Returns:
            GithubReviewResponse with analyzed files and issues
        
        Process:
            1. Fetch PR details to get merge_commit_sha
            2. Determine base_sha and head_sha (use merge commit as head)
            3. Try commit comparison API first (most efficient)
            4. Fallback to commit files API if comparison fails
            5. Process files through _process_files for review
        
        Note:
            The fallback to commit files is necessary because:
            - Comparison API may fail for very large diffs
            - Some merged PRs may not have a clean merge commit
        """
        logger.debug(f"Reviewing merged PR {payload.owner}/{payload.repo}#{payload.pr_number}")
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
                logger.debug(f"Found {len(files_data)} files via compare API")
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
        """
        Process files from GitHub API and prepare them for AI review.
        
        Converts GitHub API file data into ReviewTarget objects, handling:
        - Skipping removed files
        - Using patch (diff) content when available
        - Fetching full file content when no patch exists
        - Language detection for each file
        
        Args:
            files_data: List of file objects from GitHub API, each containing:
                - filename: Path to the file
                - status: "added", "removed", "modified", or "renamed"
                - patch: Unified diff (only for text changes)
            base_sha: Base commit SHA used for comparison
            head_sha: Head commit SHA used for comparison
            payload: Original request for context (owner, repo, etc)
        
        Returns:
            GithubReviewResponse with issues found and summary
        
        Processing Logic:
            1. Iterate through all files from GitHub API
            2. Skip files with "removed" status (no longer exist)
            3. For each remaining file:
               - If patch exists: use patch content (shows only changed lines)
               - If no patch: fetch full file content at head_sha
            4. Detect language from file extension
            5. Create ReviewTarget for each valid file
            6. Send to ReviewEngine for AI analysis
            .
        """
        targets: list[ReviewTarget] = []
        issues: list[ReviewIssue] = []

        for file_info in files_data:
            filename = file_info.get("filename", "")
            status = file_info.get("status", "modified")

            if status == "removed":
                logger.debug(f"Skipping removed file: {filename}")
                continue

            patch = file_info.get("patch", "")
            if not patch:
                try:
                    content = await self.github_client.get_file_content(
                        payload.owner, payload.repo, filename, head_sha
                    )
                except Exception as e:
                    logger.warning(f"Failed to fetch content for {filename}: {e}")
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
        """
        Detect programming language from file extension.
        
        Maps common file extensions to their programming language.
        This is used to help the LLM provide language-specific suggestions.
        
        Args:
            filename: The file name or path (e.g., "src/utils/helper.py")
        
        Returns:
            Language string (e.g., "python", "javascript") or None if unknown
        
        """
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
        """
        Analyze a GitHub repository.
        
        This endpoint is intended for full repository analysis, but is
        not yet implemented. Returns an informative response.
        
        Args:
            payload: Request object containing:
                - owner: Repository owner
                - repo: Repository name
                - branch: Optional branch name (defaults to default branch)
                - path: Optional path to analyze (defaults to root)
        
        Returns:
            GithubReviewResponse with empty issues and "not implemented" summary
        
        TODO:
            - Implement repository traversal
            - Add support for branch selection
            - Add path filtering for specific directories
            - Handle large repositories with pagination
        """
        return GithubReviewResponse(issues=[], summary=ReviewSummary(summary="Repo review not implemented"))