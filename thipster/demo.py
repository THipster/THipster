import engine.Engine as eng
from parser.ParserFactory import ParserFactory

from parser.dsl_parser.DSLParser import DSLParserPathNotFound
from parser.dsl_parser.TokenParser import DSLSyntaxException
from repository.LocalRepo import LocalRepo
from terraform.CDK import CDK, CDKException


class MockAuth(eng.I_Auth):
    """Mock of the Authentification module
    """

    def run(self):
        pass


class MockTerraform(eng.I_Terraform):
    """Mock of the Terraform module
    """

    def run(self):
        pass


def demo():
    """Script to launch the sprint demo
    """
    file = input()
    engine = eng.Engine(
        ParserFactory(), LocalRepo('/home/rcattin/THipster/tests/resources/e2e/models'),
        MockAuth(), CDK(),
    )

    try:
        print(engine.run(file))
    except DSLParserPathNotFound as e:
        print(e.message)
    except DSLSyntaxException as e:
        print(repr(e))
    except CDKException as e:
        print(e)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    demo()
