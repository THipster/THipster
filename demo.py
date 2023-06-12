import thipster
from thipster.auth import Google
from thipster.engine import THipsterException
from thipster.parser import ParserFactory
from thipster.repository import LocalRepo
from thipster.terraform import Terraform


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
    except THipsterException as e:
        print(e)
    except Exception as e:
        print('Unhandled Exception', e.args)


if __name__ == '__main__':
    demo()
