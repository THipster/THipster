"""_Engine.py module.
"""
import time

from thipster.engine.i_parser import I_Parser
from thipster.engine.i_repository import I_Repository
from thipster.engine.i_auth import I_Auth
from thipster.engine.i_terraform import I_Terraform
import thipster.engine.parsed_file as pf
from thipster.engine.resource_model import ResourceModel


class Engine():
    """The engine of thipster

    The core of the application, it is used to call and link all
    interfaces together.
    """

    importedPackages = []

    def __init__(
            self, parser: I_Parser,
            repository: I_Repository,
            auth: I_Auth,
            terraform:  I_Terraform,
    ):
        """
        Parameters
        ----------
        parser : I_Parser
            Instance of a Parser class
        repository : I_Repository
            Instance of a Respository class
        auth : I_Auth
            Instance of an Auth class
        terraform : I_Terraform
            Instance of a Terraform class

        """
        self.__parser = parser
        self.__repository = repository
        self.__auth = auth
        self.__terraform = terraform

    @property
    def parser(self):
        return self.__parser

    @parser.setter
    def parser(self, value):
        if not isinstance(value, I_Parser):
            raise Exception()

        self.__parser = value

    @property
    def repository(self):
        return self.__repository

    @repository.setter
    def repository(self, value):
        if not isinstance(value, I_Repository):
            raise Exception()

        self.__repository = value

    @property
    def auth(self):
        return self.__auth

    @auth.setter
    def auth(self, value):
        if not isinstance(value, I_Auth):
            raise Exception()

        self.__auth = value

    @property
    def terraform(self):
        return self.__terraform

    @terraform.setter
    def terraform(self, value):
        if not isinstance(value, I_Terraform):
            raise Exception()

        self.__terraform = value

    def run(self, path: str) -> tuple[list[str], str]:
        """Returns json Terraform files from the input file name

        Calls the different run methods of the parser, repository,
        auth and terraform modules.
        Transforms the inputed filename into a Cloud architecture plan.

        Parameters
        ----------
        path : str
            The path of the files to be processed

        Returns
        -------
        tuple[list[str], str]
            A tuple made up of the list of directories containing the Terraform json 
            files and a string with the results of the Terraform plan
        """
        # Parse file or directory
        file = self._parse_files(path)[0]

        # Get needed models
        models = self._get_models(file)[0]

        # Generate Terraform files
        dirs = self.__terraform.generate(file, models, self.__auth)

        self.__terraform.init()

        return dirs, self.__terraform.plan()

    def _parse_files(self, path: str) -> tuple[pf.ParsedFile, float]:
        """Parse the input file or directory

        Parameters
        ----------
        path : str
            The path of the files to be processed

        Returns
        -------
        tuple[pf.ParsedFile, float]
            A tuple made up of the ParsedFile object and the time it took to parse it
        """
        start = time.time()

        file = self.__parser.run(path)
        assert type(file) == pf.ParsedFile

        end = time.time()
        return file, end - start

    def _get_models(
        self, file: pf.ParsedFile,
    ) -> tuple[dict[str, ResourceModel], float]:
        """Get the models from the repository

        Parameters
        ----------
        file : pf.ParsedFile
            The ParsedFile object containing the resources defined in the input file

        Returns
        -------
        tuple[dict[str, ResourceModel], float]
            A tuple made up of the dictionary of models and the time it took to get them
        """
        start = time.time()
        types = [r.type for r in file.resources]
        models = self.__repository.get(types)
        end = time.time()

        return models, end - start
