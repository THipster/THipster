from repository.JSONRepo import JSONRepo
import os


class LocalRepo(JSONRepo):
    def __init__(self, path: str) -> None:
        super().__init__()
        self.__repo = path

    def get_json(self, name: str) -> str | bytes | bytearray:
        name += '.json'
        with open(os.path.join(self.__repo, name), 'r') as file:
            return file.read()
