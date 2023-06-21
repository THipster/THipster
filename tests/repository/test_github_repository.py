"""Github models repository tests."""
import pytest

from thipster.engine.resource_model import ResourceModel
from thipster.repository import GithubRepo
from thipster.repository.exceptions import ModelNotFoundError

repository = 'THipster/models'


def test_get_bucket():
    """Test get bucket model."""
    gcp_bucket = 'gcp/bucket'
    resources = [gcp_bucket]

    repo = GithubRepo(repository)

    models = repo.get(resources)
    assert isinstance(models, dict)
    assert len(models) == 2

    assert gcp_bucket in models
    assert isinstance(models[gcp_bucket], ResourceModel)

    bucket = models[gcp_bucket]

    assert len(bucket.attributes) == 1
    assert len(bucket.dependencies) == 0
    assert bucket.resource_type == gcp_bucket


def test_get_vm():
    """Test get vm model and its dependencies."""
    gcp_network = 'gcp/network'
    gcp_vm = 'gcp/vm'
    resources = [gcp_vm]

    repo = GithubRepo(repository)

    models = repo.get(resources)
    assert isinstance(models, dict)
    assert len(models) == 2

    assert gcp_vm in models
    assert isinstance(models[gcp_vm], ResourceModel)

    vm = models[gcp_vm]

    assert vm.resource_type == gcp_vm
    assert len(vm.attributes) == 2
    assert len(vm.dependencies) == 1

    assert gcp_network in models
    assert isinstance(models[gcp_network], ResourceModel)

    network = models[gcp_network]

    assert network.resource_type == gcp_network
    assert len(network.attributes) == 1
    assert len(network.dependencies) == 0


def test_model_not_found():
    """Test get non-existant model."""
    resources = ['not_an_existing_model']

    repo = GithubRepo(repository)

    with pytest.raises(ModelNotFoundError):
        repo.get(resources)
