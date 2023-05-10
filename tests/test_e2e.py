import os

from engine.Engine import Engine
from engine.I_Auth import I_Auth
from engine.I_Terraform import I_Terraform
from parser.ParserFactory import ParserFactory
from repository.LocalRepo import LocalRepo


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
        for content in os.listdir(dirname):
            os.remove(f'{dirname}/{content}')
        os.rmdir(dirname)

    return destroy_files


def create_file(filename: str, content: str, dirname: str = 'test'):
    if not os.path.isdir(dirname):
        os.mkdir(dirname)
    dirname = os.path.abspath(dirname)

    file = open(f'{dirname}/{filename}', 'w')
    file.write(content)
    file.close()


def __test_file(file: str):
    __destroy_models = __setup_local()

    path_input = 'test'
    _destroy_dir = create_dir(
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
        MockTerraform(),
    )
    try:
        output = engine.run(path_input)
    except Exception as e:
        raise e
    finally:
        _destroy_dir()
        __destroy_models()

    return output


def __setup_local():
    path_input = 'test_models'
    return create_dir(
        path_input,
        {
            'bucket.json':
            """
{
    "dependencies": {},
    "attributes":{
        "region": {
            "optional": true,
            "default": "euw",
            "cdk_key": "location"
        },
        "name": {
            "optional": false,
            "cdk_key": "name",
            "cdk_key": "location"
        }
    },
    "cdk_name_key": "name",

    "cdk_provider":"cdktf_cdktf_provider_google",
    "cdk_module":"storage_bucket",
    "cdk_class":"StorageBucket"
}
""",
            'network.json':
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

    "cdk_provider":"test_provider",
    "cdk_module":"test_module",
    "cdk_class":"bucket_class"
}
""",
            'vm.json':
            """
{
    "dependencies": {
        "network": "test/network"
    },
    "attributes":{
        "region": {
            "optional": true,
            "default": "euw",
            "cdk_key": "location"
        },
        "type": {
            "optional": false,
            "cdk_key": "location"
        }
    },
    "cdk_name_key": "name",

    "cdk_provider":"test_provider",
    "cdk_module":"test_module",
    "cdk_class":"vm_class"
}
""",
        },
    )


def test_bucket():
    out = __test_file(
        """
test_models/bucket my-bucket:
\tregion : euw
    """,
    )

    assert isinstance(out, list)
    assert len(out) == 1

    assert out[0] == 'cdktf.out/stacks/test_models--bucket--my-bucket'
