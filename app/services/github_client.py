"""
GitHub API client for fetching repository and pull request data.

Provides methods to interact with GitHub REST API for:
- Pull request details and files
- Commit comparisons
- Repository file contents
"""

import httpx
from loguru import logger


class GithubClient:
    """Client for interacting with GitHub REST API."""

    def __init__(self, token: str | None = None):
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if token:
            self.headers["Authorization"] = f"Bearer {token}"

    async def get_pr_details(self, owner: str, repo: str, pr_number: int) -> dict:
        """Fetch pull request details including base and head commits."""
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def get_pr_files(self, owner: str, repo: str, pr_number: int) -> list[dict]:
        """Fetch files changed in a pull request."""
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/files"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, params={"per_page": 100})
            response.raise_for_status()
            return response.json()

    async def compare_commits(self, owner: str, repo: str, base: str, head: str) -> dict:
        """Compare two commits and get file changes."""
        url = f"{self.base_url}/repos/{owner}/{repo}/compare/{base}...{head}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def get_commit_files(self, owner: str, repo: str, sha: str) -> list[dict]:
        """Fetch files changed in a specific commit."""
        url = f"{self.base_url}/repos/{owner}/{repo}/commits/{sha}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            return data.get("files", [])

    async def get_file_content(self, owner: str, repo: str, path: str, ref: str) -> str:
        """Fetch file content from a repository at a specific ref."""
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, params={"ref": ref})
            response.raise_for_status()
            data = response.json()
            if isinstance(data, dict) and data.get("content"):
                import base64
                return base64.b64decode(data["content"]).decode("utf-8")
            return ""