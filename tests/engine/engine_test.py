import engine.Engine as eng
from engine.ParsedFile import ParsedFile


class MockException(Exception):
    def __init__(self, message):
        self.message = message


class MockAuth(eng.I_Auth.I_Auth):
    def run(self):
        return 'Auth OK'


class MockParser(eng.I_Parser.I_Parser):
    def run(self) -> ParsedFile:
        return ParsedFile()


class MockRepository(eng.I_Repository.I_Repository):
    def run(self):
        return 'Repository OK'


class MockTerraform(eng.I_Terraform.I_Terraform):
    def run(self):
        return 'Terraform OK'


def test_engine_run():
    parser = MockParser()
    repository = MockRepository()
    auth = MockAuth()
    terraform = MockTerraform()

    engine = eng.Engine(parser, repository, auth, terraform)
    res = engine.run()

    assert res == """Engine begin\n\
Parser OK
Repository OK
Auth OK
Terraform OK
Engine end"""


def test_parser_failure(mocker):
    def fail(self):
        raise MockException('Parser failed')

    mocker.patch(
        # Dataset is in slow.py, but imported to main.py
        'tests.engine.engine_test.MockParser.run',
        fail,
    )

    parser = MockParser()
    repository = MockRepository()
    auth = MockAuth()
    terraform = MockTerraform()

    try:
        engine = eng.Engine(parser, repository, auth, terraform)
        engine.run()
    except MockException as e:
        assert e.message == 'Parser failed'
