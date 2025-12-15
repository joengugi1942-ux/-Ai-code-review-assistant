from app.schemas.github import GithubPRRequest, GithubRepoRequest, GithubReviewResponse


class GithubService:
    async def review_pr(self, payload: GithubPRRequest) -> GithubReviewResponse:
        # Placeholder implementation
        return GithubReviewResponse(issues=[], summary=None)

    async def review_repo(self, payload: GithubRepoRequest) -> GithubReviewResponse:
        # Placeholder implementation
        return GithubReviewResponse(issues=[], summary=None)



