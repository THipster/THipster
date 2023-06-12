import json
import os
import shutil

import pytest
from cdktf_cdktf_provider_google.provider import GoogleProvider

from thipster.engine.engine import Engine
from thipster.engine.i_auth import I_Auth
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


class MockAuth(I_Auth):
    def authenticate(app):
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

    file = open(f'{dirname}/{filename}', 'w')
    file.write(content)
    file.close()


def __test_file(file: str, local_repo: str = LOCAL_REPO, file_type: str = 'thips'):
    path_input = 'test'
    __destroy_dir = create_dir(
        path_input,
        {
            f'test_file.{file_type}':
            file,
        },
    )

    engine = Engine(
        ParserFactory(),
        LocalRepo(local_repo),
        MockAuth,
        Terraform(),
    )
    try:
        engine.run(path_input)
    except Exception as e:
        raise e
    finally:
        __destroy_dir()

        if os.path.exists('cdktf.out'):
            shutil.rmtree('cdktf.out')


def get_output():
    with open('thipster.tf.json') as f:
        file_contents = json.load(f)
        f.close()
    return file_contents


def get_resource(resource_data: tuple):
    output = get_output()

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
    output = get_output()
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
    output = get_output()
    assert output.get('resource') is not None
    resources = output.get('resource')

    assert resources.get(resource_type) is not None
    assert len(resources.get(resource_type)) == amount


def assert_resource_parameters_are(resource_data: tuple, parameters: list[str]):
    resource = get_resource(resource_data)

    for parameter in parameters:
        assert parameter in resource.keys()


def get_resource_parameter(resource_data: tuple, parameter: str):
    resource = get_resource(resource_data)

    assert parameter in resource.keys()
    return resource.get(parameter)


def test_bucket():
    __test_file(
        file="""
bucket my-bucket:
\tregion : euw
    """,
    )

    assert_number_of_resource_type_is('google_storage_bucket', 1)
    bucket = assert_resource_created('google_storage_bucket', 'my-bucket')
    assert_resource_parameters_are(bucket, ['location'])


def test_empty_bucket():
    __test_file(
        file="""
bucket dzvhvzarbazkhr:

    """,
    )

    assert_number_of_resource_type_is('google_storage_bucket', 1)
    assert_resource_created('google_storage_bucket', 'dzvhvzarbazkhr')

    __test_file(
        file="""
bucket dzvhvzarbazkhr:

bucket ezezeaz:
    region: europe
    """,
    )

    assert_number_of_resource_type_is('google_storage_bucket', 2)
    assert_resource_created('google_storage_bucket', 'dzvhvzarbazkhr')
    assert_resource_created('google_storage_bucket', 'ezezeaz')


def test_dep_with_no_options():
    with pytest.raises(CDKMissingAttributeInDependency):
        __test_file(
            file="""
bucket_bad_dep_parent my-bucket:
\tregion : euw
        """,
        )


def test_cyclic_deps():
    with pytest.raises(CDKCyclicDependencies):
        __test_file(
            file="""
bucket_bad_dep_cyclic my-bucket:
\tregion : euw
        """,
        )


def test_lb():
    __test_file(
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


def test_internal_object():
    __test_file(
        file="""
firewall testParent:
\tdirection: EGRESS
        """,
    )

    __test_file(
        file="""
firewall testParent:
\tdirection: EGRESS

\tallow:
\t\tprotocol: http
        """,
    )


def test_missing_explicit_dependency():
    with pytest.raises(CDKDependencyNotDeclared):
        __test_file(
            file="""
subnetwork lb-subnet:
\tnetwork: lb-net
\tregion: europe-west1b
\tip_range: 10.0.1.0/24
            """,
        )


def test_explicit_dependency():
    __test_file(
        file="""
network lb-net:

subnetwork lb-subnet:
\tnetwork: lb-net
\tregion: europe-west1b
\tip_range: 10.0.1.0/24
        """,
    )


def test_bucket_cors():
    __test_file(
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


def test_bucket_two_cors():
    __test_file(
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
