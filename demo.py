import thipster
from thipster.auth import Google
from thipster.parser import ParserFactory
from thipster.parser.dsl_parser.exceptions import (
    DSLParserPathNotFound,
    DSLSyntaxException,
)
from thipster.repository import LocalRepo
from thipster.terraform import Terraform
from thipster.terraform.exceptions import CDKException


def demo():
    """Script to launch the sprint demo
    """
    file = input()
    engine = thipster.Engine(
        ParserFactory(), LocalRepo('/home/rcattin/THipster/tests/resources/e2e/models'),
        Google, Terraform(),
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
