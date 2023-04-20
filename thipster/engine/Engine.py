import engine.I_Parser as I_Parser
import engine.I_Repository as I_Repository
import engine.I_Auth as I_Auth
import engine.I_Terraform as I_Terraform


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
