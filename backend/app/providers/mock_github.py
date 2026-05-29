from app.schemas.github import ParsedPullRequest, PullRequestFile, PullRequestSnapshot


class MockGitHubProvider:
    async def get_pull_request(self, ref: ParsedPullRequest) -> PullRequestSnapshot:
        return PullRequestSnapshot(
            owner=ref.owner,
            repo=ref.repo,
            number=ref.number,
            title="Add async review task creation",
            author="demo-user",
            base_branch="main",
            head_branch="feature/review-task",
            changed_files=3,
            additions=128,
            deletions=24,
            commit_count=4,
            files=[
                PullRequestFile(
                    path="backend/app/api/reviews.py",
                    status="added",
                    additions=45,
                    deletions=0,
                    patch="@@ -0,0 +1,45 @@\n+@router.post('/reviews')\n+async def create_review(...)",
                ),
                PullRequestFile(
                    path="backend/app/services/review_service.py",
                    status="modified",
                    additions=63,
                    deletions=12,
                    patch="@@ -10,6 +10,57 @@\n+async def create_review_task(...)",
                ),
                PullRequestFile(
                    path="backend/tests/test_reviews.py",
                    status="added",
                    additions=20,
                    deletions=0,
                    patch="@@ -0,0 +1,20 @@\n+def test_create_review_task(...)",
                ),
            ],
        )
