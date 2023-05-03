import engine.Engine as eng
from engine.ParsedFile import ParsedFile
from engine.ResourceModel import ResourceModel
from helpers import logger

import pytest
import os


class MockException(Exception):
    def __init__(self, message):
        self.message = message


class MockAuth(eng.I_Auth):
    @logger('- Authentifier')
    def run(self):
        pass


class MockParser(eng.I_Parser):
    @logger('- Parser')
    def run(self, filename) -> str:
        return ParsedFile()


class MockRepository(eng.I_Repository):
    @logger('- Repo')
    def get(self, resourceNames: list[str]) -> list[ResourceModel]:
        return []


class MockTerraform(eng.I_Terraform):
    @logger('- Terraform')
    def run(self):
        pass


def create_dir(dirname: str, files: dict[str, str]):
    if not os.path.isdir(dirname):
        os.mkdir(dirname)

    dirname = os.path.abspath(dirname)
    for name, content in files.items():
        create_file(name, content, dirname)

    def destroy_files():
        for content in os.listdir(dirname):
            os.remove(f'{dirname}/{content}')
        os.rmdir(dirname)

    return destroy_files


def create_file(filename: str, content: str, dirname: str = 'test'):
    if not os.path.isdir(dirname):
        os.mkdir(dirname)
    dirname = os.path.abspath(dirname)

    file = open(f'{dirname}/{filename}', 'w')
    file.write(content)
    file.close()


def test_engine_calls():
    parser = MockParser()
    repository = MockRepository()
    auth = MockAuth()
    terraform = MockTerraform()

    engine = eng.Engine(parser, repository, auth, terraform)
    res = engine.run('test.file')

    assert res == []


def test_parser_failure(mocker):
    def parserFail(self, filename: str):
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
        engine.run('test.file')


def test_repository_failure(mocker):
    def repositoryFail(self, resourceNames: list[str]):
        raise MockException('Repository failure')

    mocker.patch(
        'tests.engine.test_engine.MockRepository.get',
        repositoryFail,
    )

    parser = MockParser()
    repository = MockRepository()
    auth = MockAuth()
    terraform = MockTerraform()

    with pytest.raises(MockException):
        engine = eng.Engine(parser, repository, auth, terraform)
        engine.run('test.file')
