from engine.I_Parser import I_Parser
from engine.I_Repository import I_Repository
from engine.I_Auth import I_Auth
from engine.I_Terraform import I_Terraform
from helpers import logger


class Engine():

    def __init__(
            self, parser: I_Parser,
            repository: I_Repository,
            auth: I_Auth,
            terraform:  I_Terraform,
    ):
        self.__parser = parser
        self.__repository = repository
        self.__auth = auth
        self.__terraform = terraform

    @logger('Engine')
    def run(self, path: str):
        # Parse files
        file = self.__parser.run(path)

        # Get needed models
        types = [r.type for r in file.resources]
        models = self.__repository.get(types)

        self.__auth.run()
        self.__terraform.run()

        return models
