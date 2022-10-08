from github import Github, Repository
from bot import app


class GithubService(Github):
    def __init__(self):
        super().__init__(app.config.get("github", "api_token"))

    @property
    def grace(self) -> Repository:
        return self.get_repo("code-society-lab/grace", lazy=True)
