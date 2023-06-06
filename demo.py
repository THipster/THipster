from thipster.auth.google import GoogleAuth
import thipster.engine.engine as eng
from thipster.parser.parser_factory import ParserFactory

from thipster.parser.dsl_parser.parser import DSLParserPathNotFound
from thipster.parser.dsl_parser.token_parser import DSLSyntaxException
from thipster.repository.local import LocalRepo
from thipster.terraform.cdk import CDK, CDKException


def demo():
    """Script to launch the sprint demo
    """
    file = input()
    engine = eng.Engine(
        ParserFactory(), LocalRepo('/home/rcattin/THipster/tests/resources/e2e/models'),
        GoogleAuth, CDK(),
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
