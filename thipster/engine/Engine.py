"""_Engine.py module.
"""
import time

from engine.I_Parser import I_Parser
from engine.I_Repository import I_Repository
from engine.I_Auth import I_Auth
from engine.I_Terraform import I_Terraform
import engine.ParsedFile as pf


class Engine():
    """Class representing the engine of thipster

    The core of the application, it is used to call and link all
    interfaces together.

    Methods
    -------
    run(filename: str)
        Processes a fileName and creates the corresponding Cloud architecture plan

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

    def run(self, path: str):
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
        list[str]
            List of directories containing the terraform json files
        """
        start = time.time()
        # Parse files
        file = self.__parser.run(path)
        assert type(file) == pf.ParsedFile

        end = time.time()
        print("Parsed:", end - start)
        start = time.time()

        # Get needed models
        types = [r.type for r in file.resources]
        models = self.__repository.get(types)

        # self.__auth.run()

        # Generate Terraform files
        dirs = self.__terraform.generate(file, models)

        print(self.__terraform.init())
        print(self.__terraform.plan())

        return dirs
