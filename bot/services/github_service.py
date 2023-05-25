from typing import Union, Optional
from github import Github, Organization
from github.Repository import Repository
from bot import app


class GithubService(Github):
    __token: Optional[Union[str, int, bool]] = app.config.get("github", "api_key")

    def __init__(self):
        if self.__token:
            super().__init__(self.__token, per_page=25)

    @classmethod
    def can_connect(cls):
        return cls.__token is not None and cls.__token != "".strip()

    def get_code_society_lab(self) -> Organization:
        return self.get_organization("code-society-lab")

    def get_code_society_lab_repo(self, name: str) -> Repository:
        return self.get_repo(f"code-society-lab/{name}", lazy=True)
