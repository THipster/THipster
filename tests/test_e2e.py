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


def test_bucket():
    out = __test_file(
        file="""
bucket my-bucket:
\tregion : euw
    """,
    )

    assert isinstance(out, list)
    assert len(out) == 1

    assert out[0] == 'cdktf.out/stacks/thipster_infrastructure'


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
    out = __test_file(
        file="""
network lb-net:

subnetwork lb-subnet:
\tregion: europe-west1b
\tip_range: 10.0.1.0/24

loadbalancer my-lb:
\tload_balancing_scheme: EXTERNAL
    """,
    )

    assert isinstance(out, list)
    assert len(out) == 1

    assert 'cdktf.out/stacks/thipster_infrastructure' in out


def test_lb_single_file():
    out = __test_file(
        file="""
network lb-net:

subnetwork lb-subnet:
\tregion: europe-west1b
\tip_range: 10.0.1.0/24

loadbalancer my-lb:
\tload_balancing_scheme: EXTERNAL
    """,
    )

    assert isinstance(out, list)
    assert len(out) == 1

    assert 'cdktf.out/stacks/thipster_infrastructure' in out


def test_internal_object():
    out = __test_file(
        file="""
firewall testParent:
\tdirection: EGRESS
        """,
    )
    assert 'cdktf.out/stacks/thipster_infrastructure' in out

    out = __test_file(
        file="""
firewall testParent:
\tdirection: EGRESS

\tallow:
\t\tprotocol: http
        """,
    )
    assert 'cdktf.out/stacks/thipster_infrastructure' in out


def test_bucket_cors():
    out = __test_file(
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
    assert 'cdktf.out/stacks/thipster_infrastructure' in out
