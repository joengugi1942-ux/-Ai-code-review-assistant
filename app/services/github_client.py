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
        logger.debug(f"[GithubClient] GET /repos/{owner}/{repo}/pulls/{pr_number}")
        response = await self._client.get(f"/repos/{owner}/{repo}/pulls/{pr_number}")
        response.raise_for_status()
        return response.json()

    async def get_pr_files(self, owner: str, repo: str, pr_number: int) -> list[dict]:
        logger.debug(f"[GithubClient] GET /repos/{owner}/{repo}/pulls/{pr_number}/files")
        response = await self._client.get(
            f"/repos/{owner}/{repo}/pulls/{pr_number}/files",
            params={"per_page": 100},
        )
        response.raise_for_status()
        files = response.json()
        logger.debug(f"[GithubClient] PR #{pr_number} has {len(files)} file(s)")
        return files

    async def compare_commits(self, owner: str, repo: str, base: str, head: str) -> dict:
        logger.debug(f"[GithubClient] GET compare {base[:7]}...{head[:7]}")
        response = await self._client.get(f"/repos/{owner}/{repo}/compare/{base}...{head}")
        response.raise_for_status()
        return response.json()

    async def get_commit_files(self, owner: str, repo: str, sha: str) -> list[dict]:
        logger.debug(f"[GithubClient] GET commit files for {sha[:7]}")
        response = await self._client.get(f"/repos/{owner}/{repo}/commits/{sha}")
        response.raise_for_status()
        files = response.json().get("files", [])
        logger.debug(f"[GithubClient] Commit {sha[:7]} has {len(files)} file(s)")
        return files

    async def get_file_content(self, owner: str, repo: str, path: str, ref: str) -> str:
        logger.debug(f"[GithubClient] GET contents/{path} @{ref[:7] if len(ref) >= 7 else ref}")
        response = await self._client.get(
            f"/repos/{owner}/{repo}/contents/{path}",
            params={"ref": ref},
        )
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict) and data.get("content"):
            return base64.b64decode(data["content"]).decode("utf-8")
        return ""

    async def get_default_branch(self, owner: str, repo: str) -> str:
        logger.debug(f"[GithubClient] GET /repos/{owner}/{repo} (default branch)")
        response = await self._client.get(f"/repos/{owner}/{repo}")
        response.raise_for_status()
        branch = response.json().get("default_branch", "main")
        logger.debug(f"[GithubClient] Default branch: {branch}")
        return branch

    async def get_branch_tree_sha(self, owner: str, repo: str, branch: str) -> tuple[str, str]:
        """Returns (commit_sha, tree_sha) for the tip of a branch."""
        logger.debug(f"[GithubClient] GET /repos/{owner}/{repo}/branches/{branch}")
        response = await self._client.get(f"/repos/{owner}/{repo}/branches/{branch}")
        response.raise_for_status()
        data = response.json()
        commit_sha = data["commit"]["sha"]
        tree_sha = data["commit"]["commit"]["tree"]["sha"]
        logger.debug(f"[GithubClient] Branch {branch}: commit={commit_sha[:7]}, tree={tree_sha[:7]}")
        return commit_sha, tree_sha

    async def get_tree(self, owner: str, repo: str, tree_sha: str) -> list[dict]:
        """Fetch the full recursive file tree for a given tree SHA."""
        logger.debug(f"[GithubClient] GET git/trees/{tree_sha[:7]}?recursive=1")
        response = await self._client.get(
            f"/repos/{owner}/{repo}/git/trees/{tree_sha}",
            params={"recursive": "1"},
        )
        response.raise_for_status()
        tree = response.json().get("tree", [])
        blobs = sum(1 for item in tree if item.get("type") == "blob")
        logger.debug(f"[GithubClient] Tree has {len(tree)} entries ({blobs} files)")
        return tree
