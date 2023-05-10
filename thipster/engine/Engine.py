"""_Engine.py module.
"""

from engine.I_Parser import I_Parser
from engine.I_Repository import I_Repository
from engine.I_Auth import I_Auth
from engine.I_Terraform import I_Terraform
from helpers import logger


class Engine():
    """Class representing the engine of thipster

    The core of the application, it is used to call and link all
    interfaces together.

    Methods
    -------
    run(filename: str)
        Processes a fileName and creates the corresponding Cloud architecture plan

    """

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

    @logger('Engine')
    def run(self, path: str):
        """Returns an AST from the input file name

        Calls the different run methods of the parser, repository,
        auth and terraform modules.
        Transforms the inputed filename into a Cloud architecture plan.

        Parameters
        ----------
        path : str
            The path of the files to be processed

        Returns
        -------
        list[ResourceModel]
            List of resource models
        """
        # Parse files
        file = self.__parser.run(path)

        # Get needed models
        types = [r.type for r in file.resources]
        models = self.__repository.get(types)

        self.__auth.run()
        self.__terraform.run()

        return models
