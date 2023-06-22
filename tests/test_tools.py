"""Test utils and helper functions."""
import inspect
import json
import os
import shutil
from pathlib import Path

from cdktf_cdktf_provider_google.provider import GoogleProvider

from thipster import Engine
from thipster.auth import Google
from thipster.engine import AuthPort
from thipster.parser import ParserFactory
from thipster.repository import LocalRepo
from thipster.terraform import Terraform

LOCAL_REPO = 'tests/resources/e2e/models'
REMOTE_REPO = 'THipster/models'


class MockAuth(AuthPort):
    """Mock auth class."""

    def authenticate(self, app):
        """Authenticate to GCP."""
        GoogleProvider(
            app, 'default_google',
            project='project_id',
            credentials='credentials.token',
        )


def create_dir(dirname: str, files: dict[str, str]):
    """Create a directory with files.

    Parameters
    ----------
    dirname : str
        The name of the directory to create.
    files : dict[str, str]
        A dictionary of file names and contents.
    """
    if not Path(dirname).is_dir():
        Path(dirname).mkdir()

    dirname = Path(dirname).resolve().as_posix()
    for name, content in files.items():
        create_file(name, content, dirname)

    def destroy_files():
        for content in os.listdir(dirname):
            if not (Path(dirname)/content).is_dir():
                (Path(dirname)/content).unlink()
            else:
                shutil.rmtree(Path(dirname)/content)
        Path(dirname).rmdir()

    return destroy_files


def create_file(filename: str, content: str, dirname: str = 'test'):
    """Create a file with content in the designated directory.

    Parameters
    ----------
    filename : str
        The name of the file to create.
    content : str
        The content of the file to create.
    dirname : str
        The name of the directory in which to create the file.
    """
    if not Path(dirname).is_dir():
        Path(dirname).mkdir()
    dirname = Path(dirname).resolve().as_posix()

    with Path(f'{dirname}/{filename}').open('w') as f:
        f.write(content)


def process_file(
        directory: str, file: str,
        local_repo: str = LOCAL_REPO, file_type: str = 'thips',
        mock_auth=False,
):
    """Handle the file creation, engine run and clean up for the test.

    Parameters
    ----------
    directory : str
        The name of the directory to create.
    file : str
        The content of the file to create.
    local_repo : str
        The path to the local repository.
    file_type : str
        The type of file to create (thips or yaml). Defaults to 'thips'.
    mock_auth : bool
        Whether to mock the authentication to GCP. Defaults to False.
    """
    if not Path('test').is_dir():
        Path('test').mkdir()

    __destroy_dir = create_dir(
        f'test/{directory}',
        {
            f'test_file.{file_type}':
            file,
        },
    )

    def clean_up():
        __destroy_dir()

        if Path('cdktf.out').exists():
            shutil.rmtree('cdktf.out')

        if Path('test').exists() and len(os.listdir('test')) == 0:
            shutil.rmtree('test')

    engine = Engine(
        ParserFactory(),
        LocalRepo(local_repo),
        Google() if not mock_auth else MockAuth(),
        Terraform(),
    )
    try:
        engine.run(f'test/{directory}')
        shutil.move(
            Path(Path.cwd(), 'thipster.tf.json'),
            Path(Path.cwd(), f'test/{directory}', 'thipster.tf.json'),
        )
    except Exception as e:
        clean_up()
        raise e

    return clean_up


def __get_output(test_name):
    with Path(f'test/{test_name}/thipster.tf.json').open() as f:
        file_contents = json.load(f)
        f.close()
    return file_contents


def __get_resource(output_path: str, resource_data: tuple):
    output = __get_output(output_path)

    resources_of_type = output.get('resource').get(resource_data[0])
    resource = None
    for r in resources_of_type.values():
        if r.get('name') == resource_data[1]:
            resource = r

    assert resource is not None

    return resource


def assert_resource_created(
    resource_type: str,
    resource_name: str,
):
    """Assert that a resource was created.

    Parameters
    ----------
    resource_type : str
        The type of resource to check for.
    resource_name : str
        The name of the resource to check for.
    """
    output = __get_output(inspect.currentframe().f_back.f_code.co_name)
    assert output.get('resource') is not None
    resources = output.get('resource')

    assert resources.get(resource_type) is not None

    names = [x.get('name') for _, x in resources.get(resource_type).items()]
    assert resource_name in names

    return (resource_type, resource_name)


def assert_number_of_resource_type_is(
    resource_type: str,
    amount: str,
):
    """Assert that a type of resource was created the right number of times.

    Parameters
    ----------
    resource_type : str
        The type of resource to check for.
    amount : str
        The number of resources to check for.
    """
    output = __get_output(inspect.currentframe().f_back.f_code.co_name)
    assert output.get('resource') is not None
    resources = output.get('resource')

    assert resources.get(resource_type) is not None
    assert len(resources.get(resource_type)) == amount


def assert_resource_parameters_are(resource_data: tuple, parameters: list[str]):
    """Assert that a resource has the right parameters.

    Parameters
    ----------
    resource_data : tuple
        The type and name of the resource to check for.
    parameters : list[str]
        The parameters to check for.
    """
    resource = __get_resource(
        inspect.currentframe().f_back.f_code.co_name, resource_data,
    )

    for parameter in parameters:
        assert parameter in resource


def get_resource_parameter(resource_data: tuple, parameter: str):
    """Get a resource parameter.

    Parameters
    ----------
    resource_data : tuple
        The type and name of the resource to check for.
    parameter : str
        The parameter to get.
    """
    resource = __get_resource(
        inspect.currentframe().f_back.f_code.co_name, resource_data,
    )

    assert parameter in resource
    return resource.get(parameter)


def get_function_name():
    """Get the name of the function that called this function."""
    return inspect.currentframe().f_back.f_code.co_name
