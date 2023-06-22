"""Local repository implementation."""
from pathlib import Path

from .exceptions import ModelNotFoundError
from .json import JSONRepo


class LocalRepo(JSONRepo):
    """Represents a local resources Repository.

    JSON Models of resources and services offered by supported cloud providers are
    stored in a repository.
    This class is used to access those models if they are stored locally.
    """

    def __init__(self, path: str) -> None:
        """Represent a local resources Repository.

        JSON Models of resources and services offered by supported cloud providers are
        stored in a repository.
        This class is used to access those models if they are stored locally.
        """
        super().__init__()
        self.__repo = path

    def get_json(self, name: str) -> str | bytes | bytearray:
        """Get the json file from the local repository."""
        name += '.json'
        try:
            with (Path(self.__repo)/name).open() as file:
                return file.read()
        except Exception:
            raise ModelNotFoundError(name)
