import json
import os
import shutil
from cdktf_cdktf_provider_google.provider import GoogleProvider

from thipster.engine.Engine import Engine
from thipster.engine.I_Auth import I_Auth
from thipster.parser.ParserFactory import ParserFactory
import pytest
from thipster.repository.LocalRepo import LocalRepo
import thipster.terraform.CDK as cdk

LOCAL_REPO = 'tests/resources/e2e/models'
REMOTE_REPO = 'THipster/models'


class MockAuth(I_Auth):
    def authenticate(app):
        GoogleProvider(
            app, "default_google",
            project="project_id",
            credentials="credentials.token",
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


def __test_file(file: str, local_repo: str = LOCAL_REPO):

    path_input = 'test'
    __destroy_dir = create_dir(
        path_input,
        {
            'test_file.thips':
            file,
        },
    )

    engine = Engine(
        ParserFactory(),
        LocalRepo(local_repo),
        MockAuth,
        cdk.CDK(),
    )
    try:
        output = engine.run(path_input)
    except Exception as e:
        raise e
    finally:
        __destroy_dir()

        if os.path.exists('cdktf.out'):
            shutil.rmtree('cdktf.out')

    return output


def assert_resource_created(res_type: str, name: str):
    with open("thipster.tf.json") as f:
        output = json.load(f)
        f.close()

    assert output.get("resource") is not None
    resources = output.get("resource")

    assert resources.get(res_type) is not None

    names = [x.get("name") for _, x in resources.get(res_type).items()]
    assert name in names


def assert_number_of_resource_type_is(res_type: str, amount: str):
    with open("thipster.tf.json") as f:
        output = json.load(f)
        f.close()

    assert output.get("resource") is not None
    resources = output.get("resource")

    assert resources.get(res_type) is not None
    assert len(resources.get(res_type)) == amount


def test_bucket():
    __test_file(
        file="""
bucket my-bucket:
\tregion : euw
    """,
    )

    assert_number_of_resource_type_is("google_storage_bucket", 1)
    assert_resource_created("google_storage_bucket", "my-bucket")


def test_empty_bucket():
    __test_file(
        file="""
bucket dzvhvzarbazkhr:

    """,
    )

    assert_number_of_resource_type_is("google_storage_bucket", 1)
    assert_resource_created("google_storage_bucket", "dzvhvzarbazkhr")

    __test_file(
        file="""
bucket dzvhvzarbazkhr:

bucket ezezeaz:
    region: europe
    """,
    )

    assert_number_of_resource_type_is("google_storage_bucket", 2)
    assert_resource_created("google_storage_bucket", "dzvhvzarbazkhr")
    assert_resource_created("google_storage_bucket", "ezezeaz")


def test_dep_with_no_options():
    with pytest.raises(cdk.CDKMissingAttributeInDependency):
        __test_file(
            file="""
bucket_bad_dep_parent my-bucket:
\tregion : euw
        """,
        )


def test_cyclic_deps():
    with pytest.raises(cdk.CDKCyclicDependencies):
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
\tload_balancing_scheme: EXTERNAL
    """,
    )

    assert_number_of_resource_type_is("google_compute_network", 3)
    assert_resource_created("google_compute_network", "lb-net")

    assert_number_of_resource_type_is("google_compute_subnetwork", 1)
    assert_resource_created("google_compute_subnetwork", "lb-subnet")


def test_lb_single_file():
    __test_file(
        file="""
network lb-net:

subnetwork lb-subnet:
\tregion: europe-west1b
\tip_range: 10.0.1.0/24

loadbalancer my-lb:
\tload_balancing_scheme: EXTERNAL
    """,
    )


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


def test_bucket_cors():
    __test_file(
        file="""
bucket corsBucket:
    cors:
        origin:
            - "http://image-store.com"
        method:
            - "*"
        responseHeader:
            - "*"
        maxAge: 400
        """,
    )

    assert_number_of_resource_type_is("google_storage_bucket", 1)
    assert_resource_created("google_storage_bucket", "corsBucket")
