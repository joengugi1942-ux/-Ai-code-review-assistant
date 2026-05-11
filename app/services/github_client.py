import base64

import httpx
from loguru import logger


class GithubClient:
    """Client for interacting with GitHub REST API with connection pooling."""

    def __init__(self, token: str | None = None):
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        self._client = httpx.AsyncClient(
            base_url="https://api.github.com",
            headers=headers,
            timeout=30.0,
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    async def get_pr_details(self, owner: str, repo: str, pr_number: int) -> dict:
        response = await self._client.get(f"/repos/{owner}/{repo}/pulls/{pr_number}")
        response.raise_for_status()
        return response.json()

    async def get_pr_files(self, owner: str, repo: str, pr_number: int) -> list[dict]:
        response = await self._client.get(
            f"/repos/{owner}/{repo}/pulls/{pr_number}/files",
            params={"per_page": 100},
        )
        response.raise_for_status()
        return response.json()

    async def compare_commits(self, owner: str, repo: str, base: str, head: str) -> dict:
        response = await self._client.get(f"/repos/{owner}/{repo}/compare/{base}...{head}")
        response.raise_for_status()
        return response.json()

    async def get_commit_files(self, owner: str, repo: str, sha: str) -> list[dict]:
        response = await self._client.get(f"/repos/{owner}/{repo}/commits/{sha}")
        response.raise_for_status()
        return response.json().get("files", [])

    async def get_file_content(self, owner: str, repo: str, path: str, ref: str) -> str:
        response = await self._client.get(
            f"/repos/{owner}/{repo}/contents/{path}",
            params={"ref": ref},
        )
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict) and data.get("content"):
            return base64.b64decode(data["content"]).decode("utf-8")
        return ""
