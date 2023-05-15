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


def __test_file(models: dict[str, str], file: str):
    __destroy_models = __setup_local(models)

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
        LocalRepo(os.getcwd()),
        MockAuth(),
        CDK(),
    )
    try:
        output = engine.run(path_input)
    except Exception as e:
        raise e
    finally:
        __destroy_dir()
        __destroy_models()

        if os.path.exists('cdktf.out'):
            shutil.rmtree('cdktf.out')

    return output


def __setup_local(models: dict[str, str]):
    path_input = 'test_models'
    return create_dir(
        path_input,
        models,
    )


def test_bucket():
    out = __test_file(
        models={
            'bucket.json':
            """
{
    "dependencies": {},
    "attributes":{
        "region": {
            "optional": true,
            "default": "euw",
            "cdk_key": "location"
        }
    },
    "cdk_name_key": "name",

    "cdk_provider":"cdktf_cdktf_provider_google",
    "cdk_module":"storage_bucket",
    "cdk_class":"StorageBucket"
}
""",
        },
        file="""
test_models/bucket my-bucket:
\tregion : euw
    """,
    )

    assert isinstance(out, list)
    assert len(out) == 1

    assert out[0] == 'cdktf.out/stacks/test_models--bucket--my-bucket'


def test_dep_with_full_options():
    out = __test_file(
        models={
            'dep_bucketParent.json':
            """
{
    "dependencies": {"bucketChild":"test_models/dep_bucketChild"},
    "attributes":{
        "region": {
            "optional": true,
            "default": "euw",
            "cdk_key": "location"
        }
    },
    "cdk_name_key": "name",

    "cdk_provider":"cdktf_cdktf_provider_google",
    "cdk_module":"storage_bucket",
    "cdk_class":"StorageBucket"
}
""",
            'dep_bucketChild.json':
            """
{
    "dependencies": {},
    "attributes":{
        "region": {
            "optional": true,
            "default": "euw",
            "cdk_key": "location"
        }
    },
    "cdk_name_key": "name",

    "cdk_provider":"cdktf_cdktf_provider_google",
    "cdk_module":"storage_bucket",
    "cdk_class":"StorageBucket"
}
""",
        },
        file="""
test_models/dep_bucketParent my-bucket:
\tregion : euw
    """,
    )

    assert isinstance(out, list)
    assert len(out) == 1

    assert out[0] == 'cdktf.out/stacks/test_models--dep_bucketParent--my-bucket'


def test_dep_with_no_options():
    with pytest.raises(CDKMissingAttributeInDependency):
        __test_file(
            models={
                'dep_bucketBadParent.json':
                """
{
    "dependencies": {"bucketBadChild":"test_models/dep_bucketBadChild"},
    "attributes":{
        "region": {
            "optional": true,
            "default": "euw",
            "cdk_key": "location"
        }
    },
    "cdk_name_key": "name",

    "cdk_provider":"cdktf_cdktf_provider_google",
    "cdk_module":"storage_bucket",
    "cdk_class":"StorageBucket"
}
""",
                'dep_bucketBadChild.json':
                """
{
    "dependencies": {},
    "attributes": {
        "region": {
            "optional": false,
            "cdk_key": "location"
        }
    },
    "cdk_name_key": "name",

    "cdk_provider":"cdktf_cdktf_provider_google",
    "cdk_module":"storage_bucket",
    "cdk_class":"StorageBucket"
}
""",
            },
            file="""
test_models/dep_bucketBadParent my-bucket:
\tregion : euw
        """,
        )


def test_cyclic_deps():
    with pytest.raises(CDKCyclicDependencies):
        __test_file(
            models={
                'dep_bucketBadParent.json':
                """
{
    "dependencies": {"bucketBadChild":"test_models/dep_bucketBadChild"},
    "attributes":{
        "region": {
            "optional": true,
            "default": "euw",
            "cdk_key": "location"
        }
    },
    "cdk_name_key": "name",

    "cdk_provider":"cdktf_cdktf_provider_google",
    "cdk_module":"storage_bucket",
    "cdk_class":"StorageBucket"
}
""",
                'dep_bucketBadChild.json':
                """
{
    "dependencies": {"bucketBadParent":"test_models/dep_bucketBadParent"},
    "attributes": {
        "region": {
            "optional": true,
            "default": "euw",
            "cdk_key": "location"
        }
    },
    "cdk_name_key": "name",

    "cdk_provider":"cdktf_cdktf_provider_google",
    "cdk_module":"storage_bucket",
    "cdk_class":"StorageBucket"
}
""",
            },
            file="""
test_models/dep_bucketBadParent my-bucket:
\tregion : euw
        """,
        )

    with pytest.raises(CDKCyclicDependencies):
        __test_file(
            models={
                'dep_cyclicModel.json':
                """
{
    "dependencies": {"bucketBadChild":"test_models/dep_cyclicModel"},
    "attributes":{
        "region": {
            "optional": true,
            "default": "euw",
            "cdk_key": "location"
        }
    },
    "cdk_name_key": "name",

    "cdk_provider":"cdktf_cdktf_provider_google",
    "cdk_module":"storage_bucket",
    "cdk_class":"StorageBucket"
}
""",
            },
            file="""
test_models/dep_cyclicModel my-bucket:
\tregion : euw
        """,
        )
