import os
import shutil

from engine.Engine import Engine
from engine.I_Auth import I_Auth
from engine.I_Terraform import I_Terraform
from parser.ParserFactory import ParserFactory
import pytest
from repository.LocalRepo import LocalRepo
from terraform.CDK import CDK, CDKCyclicDependencies, CDKMissingAttributeInDependency


class MockAuth(I_Auth):
    def run(self):
        pass


class MockTerraform(I_Terraform):
    def run(self):
        pass


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


def __test_file(file: str):

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
        LocalRepo('tests/resources/e2e/models'),
        MockAuth(),
        CDK(),
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

    assert out[0] == 'cdktf.out/stacks/bucket--my-bucket'


def test_dep_with_full_options():
    out = __test_file(
        file="""
bucket_dep_parent my-bucket:
\tregion : euw
    """,
    )

    assert isinstance(out, list)
    assert len(out) == 1

    assert out[0] == 'cdktf.out/stacks/bucket_dep_parent--my-bucket'


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
bucket_bad_dep_parent my-bucket:
\tregion : euw
        """,
        )

    with pytest.raises(CDKCyclicDependencies):
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
    assert len(out) == 3

    assert 'cdktf.out/stacks/network--lb-net' in out
    assert 'cdktf.out/stacks/subnetwork--lb-subnet' in out
    assert 'cdktf.out/stacks/loadbalancer--my-lb' in out


def test_internal_object():
    out = __test_file(
        file="""
firewall testParent:
\tdirection: EGRESS
        """,
    )
    assert 'cdktf.out/stacks/firewall--testParent' in out

    out = __test_file(
        file="""
firewall testParent:
\tdirection: EGRESS

\tallow:
\t\tprotocol: http
        """,
    )
    assert 'cdktf.out/stacks/firewall--testParent' in out
