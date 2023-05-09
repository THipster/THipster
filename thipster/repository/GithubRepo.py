
from repository.JSONRepo import JSONRepo
import requests


class GithubRepo(JSONRepo):
    def __init__(self, repo: str) -> None:
        super().__init__()
        self.__repo = repo

    def get_json(self, name: str) -> str | bytes | bytearray:
        response = requests.get(
            f'https://raw.githubusercontent.com/{self.__repo}/main/{name}.json',
        )

        return response.content
