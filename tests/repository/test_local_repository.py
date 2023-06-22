"""Local models repository tests."""
from pathlib import Path

import pytest

from tests.test_tools import create_dir
from thipster.engine.resource_model import ResourceModel
from thipster.repository import LocalRepo
from thipster.repository.exceptions import ModelNotFoundError

test_bucket = 'test/bucket'


def __setup_local(models: dict[str, str]):
    path_input = 'test'
    return create_dir(
        path_input,
        models,
    )


def test_get_bucket():
    """Test get bucket model."""
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
    resources = [test_bucket]
    repo = LocalRepo(Path.cwd().as_posix())

    models = repo.get(resources)
    _destroy_dir()

    assert isinstance(models, dict)
    assert len(models) == 1

    assert test_bucket in models
    assert isinstance(models[test_bucket], ResourceModel)

    bucket = models[test_bucket]

    assert len(bucket.attributes) == 1
    assert len(bucket.dependencies) == 0
    assert bucket.resource_type == test_bucket


def test_get_bucket_with_cors():
    """Test get bucket model with 'cors' internal object."""
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
    resources = [test_bucket]
    repo = LocalRepo(Path.cwd().as_posix())

    models = repo.get(resources)
    _destroy_dir()

    assert isinstance(models, dict)
    assert len(models) == 2

    assert test_bucket in models
    assert isinstance(models[test_bucket], ResourceModel)

    bucket = models[test_bucket]

    assert len(bucket.attributes) == 1
    assert len(bucket.dependencies) == 0
    assert len(bucket.internal_objects) == 1
    assert bucket.resource_type == test_bucket


def test_get_vm():
    """Test get vm model and its dependencies."""
    test_vm = 'test/vm'
    test_network = 'test/network'
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
    resources = [test_vm]

    repo = LocalRepo(Path.cwd().as_posix())

    models = repo.get(resources)
    _destroy_dir()

    assert isinstance(models, dict)
    assert len(models) == 2

    assert test_vm in models
    assert isinstance(models[test_vm], ResourceModel)

    vm = models[test_vm]

    assert vm.resource_type == test_vm
    assert len(vm.attributes) == 2
    assert len(vm.dependencies) == 1

    assert test_network in models
    assert isinstance(models[test_network], ResourceModel)

    network = models[test_network]

    assert network.resource_type == test_network
    assert len(network.attributes) == 1
    assert len(network.dependencies) == 0


def test_cyclic_import():
    """Test erroneous cyclic import."""
    test_cyclic = 'test/cyclic'
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
    resources = [test_cyclic]
    repo = LocalRepo(Path.cwd().as_posix())

    models = repo.get(resources)
    _destroy_dir()

    assert isinstance(models, dict)
    assert len(models) == 1

    assert test_cyclic in models
    assert isinstance(models[test_cyclic], ResourceModel)


def test_model_not_found():
    """Test non existing model."""
    resources = ['not_an_existing_model']

    repo = LocalRepo('THipster/models')

    with pytest.raises(ModelNotFoundError):
        repo.get(resources)
