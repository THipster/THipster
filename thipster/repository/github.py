"""GithubRepo.py module."""

import requests

from .exceptions import ModelNotFoundError
from .json import JSONRepo


class GithubRepo(JSONRepo):
    """Represents a GitHub resources Repository.

    JSON Models of resources and services offered by supported cloud providers are
    stored in a repository.
    This class is used to access those models if they are located in a GitHub repo.
    """

    def __init__(self, repo: str, branch: str = 'main') -> None:
        """Represent a GitHub resources Repository.

        JSON Models of resources and services offered by supported cloud providers are
        stored in a repository.
        This class is used to access those models if they are located in a GitHub repo.

        Parameters
        ----------
        repo : str
            Name of the repository, for example : 'THipster/models'
        branch : str, optional
            Name of the branch, by default 'main'
        """
        super().__init__()
        self.__repo = repo
        self.__branch = branch

    def get_json(self, name: str) -> str | bytes | bytearray:
        """Get the json file from the GitHub repository.

        Parameters
        ----------
        name : str
            Name of the desired resource

        Returns
        -------
        str | bytes | bytearray
            Content of the JSON file defining the desired resource
        """
        response = requests.get(
            f'https://raw.githubusercontent.com/{self.__repo}/{self.__branch}/{name}.json',
        )

        if not response.ok:
            raise ModelNotFoundError(name)

        return response.content
