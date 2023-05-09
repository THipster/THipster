import engine.Engine as eng
from parser.dsl_parser.DSLParser import DSLParser
from helpers import logger

from parser.dsl_parser.DSLParser import DSLParserPathNotFound
from parser.dsl_parser.TokenParser import DSLSyntaxException
from repository.GithubRepo import GithubRepo


class MockAuth(eng.I_Auth):
    """Mock of the Authentification module
    """
    @logger('- Authentifier')
    def run(self):
        pass


class MockTerraform(eng.I_Terraform):
    """Mock of the Terraform module
    """
    @logger('- Terraform')
    def run(self):
        pass


def demo():
    """Script to launch the sprint demo
    """
    file = input()
    engine = eng.Engine(
        DSLParser(), GithubRepo('Thipster/models'),
        MockAuth(), MockTerraform(),
    )

    try:
        engine.run(file)
    except DSLParserPathNotFound as e:
        print(e.message)
    except DSLSyntaxException as e:
        print(repr(e))


if __name__ == '__main__':
    demo()
