import engine.Engine as eng
from engine.ParsedFile import ParsedFile
from engine.ResourceModel import ResourceModel

import pytest


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
    def run(self) -> list[ResourceModel]:
        return []


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
    def parserFail(self):
        raise MockException('Parser failure')

    mocker.patch(
        'tests.engine.test_engine.MockParser.run',
        parserFail,
    )

    parser = MockParser()
    repository = MockRepository()
    auth = MockAuth()
    terraform = MockTerraform()

    with pytest.raises(MockException):
        engine = eng.Engine(parser, repository, auth, terraform)
        engine.run()


def test_repository_failure(mocker):
    def repositoryFail(self):
        raise MockException('Repository failure')

    mocker.patch(
        'tests.engine.test_engine.MockRepository.run',
        repositoryFail,
    )

    parser = MockParser()
    repository = MockRepository()
    auth = MockAuth()
    terraform = MockTerraform()

    with pytest.raises(MockException):
        engine = eng.Engine(parser, repository, auth, terraform)
        engine.run()
