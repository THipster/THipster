import inspect
import json
import os
import shutil
import uuid

import pytest

from thipster.auth import Google
from thipster.engine.engine import Engine
from thipster.parser.parser_factory import ParserFactory
from thipster.repository.local import LocalRepo
from thipster.terraform import Terraform
from thipster.terraform.exceptions import (
    CDKCyclicDependencies,
    CDKDependencyNotDeclared,
    CDKMissingAttributeInDependency,
)

LOCAL_REPO = 'tests/resources/e2e/models'
REMOTE_REPO = 'THipster/models'


def create_dir(dirname: str, files: dict[str, str]):
    dirname = f'test/{dirname}'

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

    file = open(f'{dirname}/{filename}', 'w')
    file.write(content)
    file.close()


def __test_file(
        directory: str, file: str,
        local_repo: str = LOCAL_REPO, file_type: str = 'thips',
):
    if not os.path.isdir('test'):
        try:
            os.mkdir('test')
        except FileExistsError:
            pass

    __destroy_dir = create_dir(
        directory,
        {
            f'test_file.{file_type}':
            file,
        },
    )

    engine = Engine(
        ParserFactory(),
        LocalRepo(local_repo),
        Google,
        Terraform(),
    )
    try:
        engine.run(f'test/{directory}')
        shutil.move(
            os.path.join(os.getcwd(), 'thipster.tf.json'),
            os.path.join(os.getcwd(), f'test/{directory}', 'thipster.tf.json'),
        )
    except Exception as e:
        __destroy_dir()

        if os.path.exists('cdktf.out'):
            shutil.rmtree('cdktf.out')

        raise e

    def clean_up():
        __destroy_dir()

        if os.path.exists('cdktf.out'):
            shutil.rmtree('cdktf.out')

        if os.path.exists('test') and len(os.listdir('test')):
            shutil.rmtree('test')

    return clean_up


def get_output(test_name):
    with open(f'test/{test_name}/thipster.tf.json') as f:
        file_contents = json.load(f)
        f.close()
    return file_contents


def get_resource(output_path: str, resource_data: tuple):
    output = get_output(output_path)

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
    output = get_output(inspect.currentframe().f_back.f_code.co_name)
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
    output = get_output(inspect.currentframe().f_back.f_code.co_name)
    assert output.get('resource') is not None
    resources = output.get('resource')

    assert resources.get(resource_type) is not None
    assert len(resources.get(resource_type)) == amount


def assert_resource_parameters_are(resource_data: tuple, parameters: list[str]):
    resource = get_resource(
        inspect.currentframe().f_back.f_code.co_name, resource_data,
    )

    for parameter in parameters:
        assert parameter in resource.keys()


def get_resource_parameter(resource_data: tuple, parameter: str):
    resource = get_resource(
        inspect.currentframe().f_back.f_code.co_name, resource_data,
    )

    assert parameter in resource.keys()
    return resource.get(parameter)


def get_function_name():
    return inspect.currentframe().f_back.f_code.co_name


def get_go_function(function_name: str):
    return function_name.replace('_', ' ').title().replace(' ', '')


def test_bucket():
    function_name = get_function_name()

    bucket_name = f'test-bucket-{uuid.uuid4()}'
    clean_up = __test_file(
        directory=function_name,
        file=f"""
bucket {bucket_name}:
\tregion : europe-west1
    """,
    )

    # Assertions before Terratest
    assert_number_of_resource_type_is('google_storage_bucket', 1)
    bucket = assert_resource_created('google_storage_bucket', bucket_name)
    assert_resource_parameters_are(bucket, ['location'])

    # Terratest call

    clean_up()


def test_empty_bucket():
    function_name = get_function_name()

    clean_up = __test_file(
        directory=function_name,
        file="""
bucket dzvhvzarbazkhr:

    """,
    )

    assert_number_of_resource_type_is('google_storage_bucket', 1)
    assert_resource_created('google_storage_bucket', 'dzvhvzarbazkhr')

    clean_up()

    clean_up = __test_file(
        directory=function_name,
        file="""
bucket dzvhvzarbazkhr:

bucket ezezeaz:
    region: europe
    """,
    )

    assert_number_of_resource_type_is('google_storage_bucket', 2)
    assert_resource_created('google_storage_bucket', 'dzvhvzarbazkhr')
    assert_resource_created('google_storage_bucket', 'ezezeaz')

    clean_up()


def test_dep_with_no_options():
    function_name = get_function_name()

    with pytest.raises(CDKMissingAttributeInDependency):
        clean_up = __test_file(
            directory=function_name,
            file="""
bucket_bad_dep_parent my-bucket:
\tregion : euw
        """,
        )

        clean_up()


def test_cyclic_deps():
    function_name = get_function_name()

    with pytest.raises(CDKCyclicDependencies):
        clean_up = __test_file(
            directory=function_name,
            file="""
bucket_bad_dep_cyclic my-bucket:
\tregion : euw
        """,
        )

        clean_up()


def test_lb():
    function_name = get_function_name()

    clean_up = __test_file(
        directory=function_name,
        file="""
network lb-net:

subnetwork lb-subnet:
\tnetwork: lb-net
\tregion: europe-west1b
\tip_range: 10.0.1.0/24

loadbalancer my-lb:
\tnetwork: lb-net
\tload_balancing_scheme: EXTERNAL
    """,
    )

    assert_number_of_resource_type_is('google_compute_network', 1)
    assert_resource_created('google_compute_network', 'lb-net')

    assert_number_of_resource_type_is('google_compute_subnetwork', 1)
    assert_resource_created('google_compute_subnetwork', 'lb-subnet')

    # Terratest call
    clean_up()


def test_internal_object():
    function_name = get_function_name()

    clean_up = __test_file(
        directory=function_name,
        file="""
firewall testParent:
\tdirection: EGRESS
        """,
    )

    clean_up()

    clean_up = __test_file(
        directory=function_name,
        file="""
firewall testParent:
\tdirection: EGRESS

\tallow:
\t\tprotocol: http
        """,
    )

    clean_up()


def test_missing_explicit_dependency():
    function_name = get_function_name()

    with pytest.raises(CDKDependencyNotDeclared):
        clean_up = __test_file(
            directory=function_name,
            file="""
subnetwork lb-subnet:
\tnetwork: lb-net
\tregion: europe-west1b
\tip_range: 10.0.1.0/24
            """,
        )

        clean_up()


def test_explicit_dependency():
    function_name = get_function_name()

    clean_up = __test_file(
        directory=function_name,
        file="""
network lb-net:

subnetwork lb-subnet:
\tnetwork: lb-net
\tregion: europe-west1b
\tip_range: 10.0.1.0/24
        """,
    )

    clean_up()


def test_bucket_cors():
    function_name = get_function_name()

    clean_up = __test_file(
        directory=function_name,
        file="""
bucket corsBucket:
    cors:
        origin:
            - "http://example.com"
        method:
            - "*"
        responseHeader:
            - "*"
        maxAge: 400
        """,
    )

    assert_number_of_resource_type_is('google_storage_bucket', 1)
    assert_resource_created('google_storage_bucket', 'corsBucket')

    clean_up()


def test_bucket_two_cors():
    function_name = get_function_name()

    clean_up = __test_file(
        directory=function_name,
        file="""
bucket:
  name: corsBucket
  cors:
    - origin:
      - "http://example.com"
      method:
      - "*"
      responseHeader:
      - "*"
      maxAge: 400
    - origin:
      - "http://example.com/other"
      method:
      - "*"
      responseHeader:
      - "*"
      maxAge: 600
""",
        file_type='yaml',
    )

    assert_number_of_resource_type_is('google_storage_bucket', 1)
    bucket = assert_resource_created('google_storage_bucket', 'corsBucket')
    cors_block = get_resource_parameter(bucket, 'cors')

    assert len(cors_block) == 2

    clean_up()
