from repository.GithubRepo import GithubRepo
from engine.ResourceModel import ResourceModel


def test_get_bucket():
    resources = ['gcp/bucket']

    repo = GithubRepo('THipster/models')

    models = repo.get(resources)
    assert isinstance(models, dict)
    assert len(models) == 1

    assert 'gcp/bucket' in models.keys()
    assert isinstance(models['gcp/bucket'], ResourceModel)

    bucket = models['gcp/bucket']

    assert len(bucket.attributes) == 1
    assert len(bucket.dependencies) == 0
    assert bucket.type == 'gcp/bucket'


def test_get_vm():
    resources = ['gcp/vm']

    repo = GithubRepo('THipster/models')

    models = repo.get(resources)
    assert isinstance(models, dict)
    assert len(models) == 2

    assert 'gcp/vm' in models.keys()
    assert isinstance(models['gcp/vm'], ResourceModel)

    vm = models['gcp/vm']

    assert vm.type == 'gcp/vm'
    assert len(vm.attributes) == 2
    assert len(vm.dependencies) == 1

    assert 'gcp/network' in models.keys()
    assert isinstance(models['gcp/network'], ResourceModel)

    network = models['gcp/network']

    assert network.type == 'gcp/network'
    assert len(network.attributes) == 1
    assert len(network.dependencies) == 0
