import engine.Engine as eng
from parser.dsl_parser.DSLParser import DSLParser
from engine.ResourceModel import ResourceModel
from helpers import logger

from parser.dsl_parser.DSLParser import DSLParserPathNotFound
from parser.dsl_parser.TokenParser import DSLSyntaxException


class MockAuth(eng.I_Auth):
    @logger('- Authentifier')
    def run(self):
        pass


class MockRepository(eng.I_Repository):
    @logger('- Repo')
    def run(self) -> list[ResourceModel]:
        pass


class MockTerraform(eng.I_Terraform):
    @logger('- Terraform')
    def run(self):
        pass


def demo():
    file = input()
    engine = eng.Engine(
        DSLParser(), MockRepository(),
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
