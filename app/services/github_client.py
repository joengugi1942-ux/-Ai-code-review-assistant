import httpx
from loguru import logger


class GithubClient:
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
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def get_pr_files(self, owner: str, repo: str, pr_number: int) -> list[dict]:
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/files"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, params={"per_page": 100})
            response.raise_for_status()
            return response.json()

    async def compare_commits(self, owner: str, repo: str, base: str, head: str) -> dict:
        url = f"{self.base_url}/repos/{owner}/{repo}/compare/{base}...{head}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def get_commit_files(self, owner: str, repo: str, sha: str) -> list[dict]:
        url = f"{self.base_url}/repos/{owner}/{repo}/commits/{sha}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            return data.get("files", [])

    async def get_file_content(self, owner: str, repo: str, path: str, ref: str) -> str:
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, params={"ref": ref})
            response.raise_for_status()
            data = response.json()
            if isinstance(data, dict) and data.get("content"):
                import base64
                return base64.b64decode(data["content"]).decode("utf-8")
            return ""