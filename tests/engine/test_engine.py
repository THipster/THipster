import os

import pytest

import thipster.engine as eng
from thipster.engine.parsed_file import ParsedFile
from thipster.engine.resource_model import ResourceModel


def logger(name: str):
    def wrapper(function):
        def internal_wrapper(*args, **kwargs):
            print(f'{name} starting')
            res = function(*args, **kwargs)
            print(f'{name} returned :\n{str(res)}')
            return res
        return internal_wrapper
    return wrapper


class MockError(Exception):
    def __init__(self, message):
        self.message = message


class MockAuth(eng.AuthPort):
    @logger('- Authentifier')
    def authenticate(self):
        return (None, None)


class MockParser(eng.ParserPort):
    @logger('- Parser')
    def run(self, filename) -> str:
        return ParsedFile()


class MockRepository(eng.RepositoryPort):
    @logger('- Repo')
    def get(self, resource_names: list[str]) -> dict[str, ResourceModel]:
        return []


class MockTerraform(eng.TerraformPort):
    @logger('- Terraform:apply')
    def apply(self):
        pass

    @logger('- Terraform:generate')
    def generate(self, a, b, auth):
        pass

    @logger('- Terraform:init')
    def init(self):
        pass

    @logger('- Terraform:plan')
    def plan(self):
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

    with open(f'{dirname}/{filename}', 'w') as f:
        f.write(content)


def test_engine_calls():
    parser = MockParser()
    repository = MockRepository()
    auth = MockAuth()
    terraform = MockTerraform()

    engine = eng.Engine(parser, repository, auth, terraform)
    res = engine.run('test.file')

    assert res is None


def test_parser_failure(mocker):
    def parser_fail(self, filename: str):
        raise MockError('Parser failure')

    mocker.patch(
        'tests.engine.test_engine.MockParser.run',
        parser_fail,
    )

    parser = MockParser()
    repository = MockRepository()
    auth = MockAuth()
    terraform = MockTerraform()

    with pytest.raises(MockError):
        engine = eng.Engine(parser, repository, auth, terraform)
        engine.run('test.file')


def test_repository_failure(mocker):
    def repository_fail(self, resource_names: list[str]) -> dict[str, ResourceModel]:
        raise MockError('Repository failure')

    mocker.patch(
        'tests.engine.test_engine.MockRepository.get',
        repository_fail,
    )

    parser = MockParser()
    repository = MockRepository()
    auth = MockAuth()
    terraform = MockTerraform()

    with pytest.raises(MockError):
        engine = eng.Engine(parser, repository, auth, terraform)
        engine.run('test.file')
