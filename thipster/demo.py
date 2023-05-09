import engine.Engine as eng
from parser.ParserFactory import ParserFactory
from helpers import logger

from parser.dsl_parser.DSLParser import DSLParserPathNotFound
from parser.dsl_parser.TokenParser import DSLSyntaxException
from repository.LocalRepo import LocalRepo


class MockAuth(eng.I_Auth):
    @logger('- Authentifier')
    def run(self):
        pass


class MockTerraform(eng.I_Terraform):
    @logger('- Terraform')
    def run(self):
        pass


def demo():
    file = input()
    engine = eng.Engine(
        ParserFactory(), LocalRepo('/home/rcattin/models'),
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
