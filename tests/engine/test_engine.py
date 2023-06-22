"""Basic tests for the engine module functions."""

import pytest

import thipster.engine as eng
from thipster.engine.parsed_file import ParsedFile
from thipster.engine.resource_model import ResourceModel

test_file = 'test.file'


def logger(name: str):
    """Log the function calls in the console."""
    def wrapper(function):
        def internal_wrapper(*args, **kwargs):
            print(f'{name} starting')
            res = function(*args, **kwargs)
            print(f'{name} returned :\n{res!s}')
            return res
        return internal_wrapper
    return wrapper


class MockError(Exception):
    """Mock errors for testing purposes."""

    def __init__(self, message):
        self.message = message


class MockAuth(eng.AuthPort):
    """Mock engine authentification port."""

    @logger('- Authentifier')
    def authenticate(self):
        """Mock authentification method."""
        return (None, None)


class MockParser(eng.ParserPort):
    """Mock engine parser port."""

    @logger('- Parser')
    def run(self, filename) -> str:  # noqa: ARG002
        """Mock parser method."""
        return ParsedFile()


class MockRepository(eng.RepositoryPort):
    """Mock engine repository port."""

    @logger('- Repo')
    def get(
        self,
        resource_names: list[str],  # noqa: ARG002
    ) -> dict[str, ResourceModel]:
        """Mock the get models repository method."""
        return {}


class MockTerraform(eng.TerraformPort):
    """Mock engine terraform port."""

    @logger('- Terraform:apply')
    def apply(self, file):
        """Mock the terraform apply method."""
        pass

    @logger('- Terraform:generate')
    def generate(self, a, b, auth):
        """Mock the terraform generate method."""
        pass

    @logger('- Terraform:init')
    def init(self):
        """Mock the terraform init method."""
        pass

    @logger('- Terraform:plan')
    def plan(self, file):
        """Mock the terraform plan method."""
        pass


def test_engine_calls():
    """Test the engine calls."""
    parser = MockParser()
    repository = MockRepository()
    auth = MockAuth()
    terraform = MockTerraform()

    engine = eng.Engine(parser, repository, auth, terraform)
    res = engine.run(test_file)

    assert res is None


def test_parser_failure(mocker):
    """Test the parser failure."""

    def parser_fail(self, filename: str):  # noqa: ARG001
        msg = 'Parser failure'
        raise MockError(msg)

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
        engine.run(test_file)


def test_repository_failure(mocker):
    """Test the behavior of the repository when it fails."""

    def repository_fail(
        self,  # noqa: ARG001
        resource_names: list[str],  # noqa: ARG001
    ) -> dict[str, ResourceModel]:
        msg = 'Repository failure'
        raise MockError(msg)

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
        engine.run(test_file)
