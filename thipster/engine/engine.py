"""_Engine.py module.
"""

import thipster.engine.parsed_file as pf

from .i_auth import AuthPort
from .i_parser import ParserPort
from .i_repository import RepositoryPort
from .i_terraform import TerraformPort
from .resource_model import ResourceModel


class Engine():
    """The engine of thipster

    The core of the application, it is used to call and link all
    interfaces together.
    """

    def __init__(
            self, parser: ParserPort,
            repository: RepositoryPort,
            auth: AuthPort,
            terraform:  TerraformPort,
    ):
        """
        Parameters
        ----------
        parser : ParserPort
            Instance of a Parser class
        repository : RepositoryPort
            Instance of a Respository class
        auth : AuthPort
            Instance of an Auth class
        terraform : TerraformPort
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
        if not isinstance(value, ParserPort):
            raise Exception()

        self.__parser = value

    @property
    def repository(self):
        return self.__repository

    @repository.setter
    def repository(self, value):
        if not isinstance(value, RepositoryPort):
            raise Exception()

        self.__repository = value

    @property
    def auth(self):
        return self.__auth

    @auth.setter
    def auth(self, value):
        if not isinstance(value, AuthPort):
            raise Exception()

        self.__auth = value

    @property
    def terraform(self):
        return self.__terraform

    @terraform.setter
    def terraform(self, value):
        if not isinstance(value, TerraformPort):
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
        parsed_file = self._parse_files(path)

        # Get needed models
        models = self._get_models(parsed_file)

        # Generate Terraform files
        self._generate_tf_files(parsed_file, models)

        self.__terraform.init()

        return self.__terraform.plan()

    def _parse_files(self, path: str) -> pf.ParsedFile:
        """Parse the input file or directory

        Parameters
        ----------
        path : str
            The path of the files to be processed

        Returns
        -------
        pf.ParsedFile
            The ParsedFile object containing the resources defined in the input file
        """
        parsed_file = self.__parser.run(path)
        assert type(parsed_file) == pf.ParsedFile

        return parsed_file

    def _get_models(
        self, file: pf.ParsedFile,
    ) -> dict[str, ResourceModel]:
        """Get the models from the repository

        Parameters
        ----------
        file : pf.ParsedFile
            The ParsedFile object containing the resources defined in the input file

        Returns
        -------
        dict[str, ResourceModel]
            The dictionary of models
        """
        types = [r.resource_type for r in file.resources]
        models = self.__repository.get(types)

        return models

    def _generate_tf_files(
        self, file: pf.ParsedFile, models: dict[str, ResourceModel],
    ) -> list[str]:
        """Generate Terraform files

        Parameters
        ----------
        file : pf.ParsedFile
            The ParsedFile object containing the resources defined in the input file
        models : dict[str, ResourceModel]
            The dictionary of models

        Returns
        -------
        list[str]
            A list of directories containing the Terraform json files
        """
        self.__terraform.generate(file, models, self.__auth)

    def _init_terraform(self) -> None:
        """Initialize Terraform
        """
        self.__terraform.init()

    def _plan_terraform(self) -> str:
        """Plan Terraform

        Returns
        -------
        str
            The results of the Terraform plan
        """
        results = self.__terraform.plan()

        return results

    def _apply_terraform(self) -> str:
        """Apply Terraform

        Returns
        -------
        str
            The results of the Terraform apply
        """
        results = self.__terraform.apply()

        return results
