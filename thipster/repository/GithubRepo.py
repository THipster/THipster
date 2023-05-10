"""GithubRepo.py module
"""

from repository.JSONRepo import JSONRepo
import requests


class GithubRepo(JSONRepo):
    """Class representing a GitHub resources Repository

    JSON Models of resources and services offered by supported cloud providers are
    stored in a repository.
    This class is used to access those models if they are located in a GitHub repo.
    """

    def __init__(self, repo: str) -> None:
        """
        Parameters
        ----------
        repo : str
            Name of the repository, for example : 'THipster/models'
        """
        super().__init__()
        self.__repo = repo

    def get_json(self, name: str) -> str | bytes | bytearray:
        """Method to get the json file from the GitHub repository

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
            f'https://raw.githubusercontent.com/{self.__repo}/main/{name}.json',
        )

        return response.content
