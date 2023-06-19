"""Demo script to launch the thipster package."""
from pathlib import Path

import thipster
from thipster.auth import Google
from thipster.engine import THipsterError
from thipster.parser import ParserFactory
from thipster.repository import LocalRepo
from thipster.terraform import Terraform


def demo():
    """Script to launch the sprint demo."""
    input_file_path = input()
    engine = thipster.Engine(
        ParserFactory(),
        LocalRepo(Path(Path.cwd(), '/tests/resources/e2e/models').as_posix()),
        Google, Terraform(),
    )

    try:
        print(engine.run(input_file_path))
    except THipsterError as e:
        print(e)
    except Exception as e:
        print('Unhandled Exception', e.args)


if __name__ == '__main__':
    demo()
