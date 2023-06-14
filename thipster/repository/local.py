import os

from .exceptions import ModelNotFoundError
from .json import JSONRepo


class LocalRepo(JSONRepo):
    def __init__(self, path: str) -> None:
        super().__init__()
        self.__repo = path

    def get_json(self, name: str) -> str | bytes | bytearray:
        name += '.json'
        try:
            with open(os.path.join(self.__repo, name)) as file:
                return file.read()
        except Exception:
            raise ModelNotFoundError(name)
