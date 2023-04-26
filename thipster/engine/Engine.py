from engine.I_Parser import I_Parser
from engine.I_Repository import I_Repository
from engine.I_Auth import I_Auth
from engine.I_Terraform import I_Terraform


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

        pass

    def run(self):
        res = 'Engine begin\n'
        if self.__parser.run():
            res += 'Parser OK' + '\n'
        if isinstance(self.__repository.run(), list):
            res += 'Repository OK' + '\n'
        res += self.__auth.run() + '\n'
        res += self.__terraform.run() + '\n'

        res += 'Engine end'
        return res
