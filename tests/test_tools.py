import inspect
import json
import os
import shutil

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
    def authenticate(self, app):
        GoogleProvider(
            app, 'default_google',
            project='project_id',
            credentials='credentials.token',
        )


def create_dir(dirname: str, files: dict[str, str]):
    if not os.path.isdir(dirname):
        os.mkdir(dirname)

    dirname = os.path.abspath(dirname)
    for name, content in files.items():
        create_file(name, content, dirname)

    def destroy_files():
        shutil.rmtree(dirname)

    return destroy_files


def create_file(filename: str, content: str, dirname: str = 'test'):
    if not os.path.isdir(dirname):
        os.mkdir(dirname)
    dirname = os.path.abspath(dirname)

    with open(f'{dirname}/{filename}', 'w') as f:
        f.write(content)


def process_file(
        directory: str, file: str,
        local_repo: str = LOCAL_REPO, file_type: str = 'thips',
        mock_auth=False,
):
    if not os.path.isdir('test'):
        os.mkdir('test')

    __destroy_dir = create_dir(
        f'test/{directory}',
        {
            f'test_file.{file_type}':
            file,
        },
    )

    def clean_up():
        __destroy_dir()

        if os.path.exists('cdktf.out'):
            shutil.rmtree('cdktf.out')

        if os.path.exists('test') and len(os.listdir('test')) == 0:
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
            os.path.join(os.getcwd(), 'thipster.tf.json'),
            os.path.join(os.getcwd(), f'test/{directory}', 'thipster.tf.json'),
        )
    except Exception as e:
        clean_up()
        raise e

    return clean_up


def __get_output(test_name):
    with open(f'test/{test_name}/thipster.tf.json') as f:
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
    output = __get_output(inspect.currentframe().f_back.f_code.co_name)
    assert output.get('resource') is not None
    resources = output.get('resource')

    assert resources.get(resource_type) is not None
    assert len(resources.get(resource_type)) == amount


def assert_resource_parameters_are(resource_data: tuple, parameters: list[str]):
    resource = __get_resource(
        inspect.currentframe().f_back.f_code.co_name, resource_data,
    )

    for parameter in parameters:
        assert parameter in resource.keys()


def get_resource_parameter(resource_data: tuple, parameter: str):
    resource = __get_resource(
        inspect.currentframe().f_back.f_code.co_name, resource_data,
    )

    assert parameter in resource.keys()
    return resource.get(parameter)


def get_function_name():
    return inspect.currentframe().f_back.f_code.co_name
