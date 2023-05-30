from thipster.repository.LocalRepo import LocalRepo
from thipster.engine.ResourceModel import ResourceModel
import os


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


def __setup_local(models: dict[str, str]):
    path_input = 'test'
    return create_dir(
        path_input,
        models,
    )


def test_get_bucket():
    _destroy_dir = __setup_local({
        'bucket.json':
            """
{
    "dependencies": {},
    "internalObjects": {},
    "attributes":{
        "region": {
            "optional": true,
            "default": "euw",
            "cdk_key": "region",
            "var_type": "str"
        }
    },
    "cdk_name_key": "name",

    "cdk_provider":"cdktf_cdktf_provider_google",
    "cdk_module":"storage_bucket",
    "cdk_class":"StorageBucket"
}
""",
    })
    resources = ['test/bucket']
    repo = LocalRepo(os.getcwd())

    models = repo.get(resources)
    _destroy_dir()

    assert isinstance(models, dict)
    assert len(models) == 1

    assert 'test/bucket' in models.keys()
    assert isinstance(models['test/bucket'], ResourceModel)

    bucket = models['test/bucket']

    assert len(bucket.attributes) == 1
    assert len(bucket.dependencies) == 0
    assert bucket.type == 'test/bucket'


def test_get_bucket_with_cors():
    _destroy_dir = __setup_local({
        'bucket.json':
            """
{
    "dependencies": {},
    "internalObjects": {
        "cors": {
            "resource" : "test/bucket_cors",
            "var_type": "list[StorageBucketCors]",
            "default": {}
        }
    },
    "attributes":{
        "region": {
            "optional": true,
            "default": "euw",
            "cdk_key": "region",
            "var_type": "str"
        }
    },
    "cdk_name_key": "name",

    "cdk_provider":"cdktf_cdktf_provider_google",
    "cdk_module":"storage_bucket",
    "cdk_class":"StorageBucket"
}
""",
        'bucket_cors.json':
            """
{
    "dependencies": {},
    "internalObjects": {},
    "attributes":{
        "origin": {
            "optional": true,
            "cdk_key": "origin",
            "var_type": "list[str]"
        },
        "method": {
            "optional": true,
            "cdk_key": "method",
            "var_type": "list[str]"
        },
        "responseHeader": {
            "optional": true,
            "cdk_key": "response_header",
            "var_type": "list[str]"
        },
        "maxAge": {
            "optional": true,
            "cdk_key": "max_age_seconds",
            "var_type": "int"
        }
    },

    "cdk_provider":"cdktf_cdktf_provider_google",
    "cdk_module":"storage_bucket",
    "cdk_class":"StorageBucketCors"
}
""",
    })
    resources = ['test/bucket']
    repo = LocalRepo(os.getcwd())

    models = repo.get(resources)
    _destroy_dir()

    assert isinstance(models, dict)
    assert len(models) == 2

    assert 'test/bucket' in models.keys()
    assert isinstance(models['test/bucket'], ResourceModel)

    bucket = models['test/bucket']

    assert len(bucket.attributes) == 1
    assert len(bucket.dependencies) == 0
    assert len(bucket.internalObjects) == 1
    assert bucket.type == 'test/bucket'


def test_get_vm():
    _destroy_dir = __setup_local({
        'network.json':
            """
{
    "dependencies": {},
    "internalObjects": {},
    "attributes":{
        "region": {
            "optional": true,
            "default": "euw",
            "cdk_key": "region",
            "var_type": "str"
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
        "network": {
            "resource": "test/network",
            "default": {}
        }
    },
    "internalObjects": {},
    "attributes":{
        "region": {
            "optional": true,
            "default": "euw",
            "cdk_key": "region",
            "var_type": "str"
        },
        "type": {
            "optional": false,
            "cdk_key": "type"
        }
    },
    "cdk_name_key": "name",
    
    "cdk_provider":"test_provider",
    "cdk_module":"test_module",
    "cdk_class":"vm_class"
}
""",
    })
    resources = ['test/vm']

    repo = LocalRepo(os.getcwd())

    models = repo.get(resources)
    _destroy_dir()

    assert isinstance(models, dict)
    assert len(models) == 2

    assert 'test/vm' in models.keys()
    assert isinstance(models['test/vm'], ResourceModel)

    vm = models['test/vm']

    assert vm.type == 'test/vm'
    assert len(vm.attributes) == 2
    assert len(vm.dependencies) == 1

    assert 'test/network' in models.keys()
    assert isinstance(models['test/network'], ResourceModel)

    network = models['test/network']

    assert network.type == 'test/network'
    assert len(network.attributes) == 1
    assert len(network.dependencies) == 0


def test_cyclic_import():
    _destroy_dir = __setup_local({
        'cyclic.json':
            """
{
    "dependencies": {
        "network": {
            "resource": "test/cyclic",
            "default": {}
        }
    },
    "internalObjects": {},
    "attributes":{
        "region": {
            "optional": true,
            "default": "euw",
            "cdk_key": "region"
        }
    },
    "cdk_name_key": "name",
    
    "cdk_provider":"test_provider",
    "cdk_module":"test_module",
    "cdk_class":"vm_class"
}
""",
    })
    resources = ['test/cyclic']
    repo = LocalRepo(os.getcwd())

    models = repo.get(resources)
    _destroy_dir()

    assert isinstance(models, dict)
    assert len(models) == 1

    assert 'test/cyclic' in models.keys()
    assert isinstance(models['test/cyclic'], ResourceModel)
