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


def test_lb():
    out = __test_file(
        models={
            'loadbalancer.json':
            """
{
    "dependencies": {
        "ip_address":{
            "resource" : "test_models/global_address",
            "default" : {
            
            }
        },
        "target":{
            "resource" : "test_models/target_http_proxy",
            "default" : {
            
            }
        }
    },
    "internalObjects": {
        
    },
    "attributes":{
        "ip_protocol": {
            "optional": true,
            "default": "TCP",
            "cdk_key": "ip_protocol"
        },
        "port_range": {
            "optional": true,
            "default": "80",
            "cdk_key": "port_range"
        },
        "load_balancing_scheme": {
            "optional": true,
            "default": "EXTERNAL",
            "cdk_key": "load_balancing_scheme"
        }
        
    },
    "cdk_name_key": "name",

    "cdk_provider":"cdktf_cdktf_provider_google",
    "cdk_module":"compute_global_forwarding_rule",
    "cdk_class":"ComputeGlobalForwardingRule"
}
""",
            'global_address.json':
            """
{
    "dependencies": {
        "network" : {
            "resource" : "test_models/network",
            "default" : {
            
            }
        }
    },
    "internalObjects": {
        
    },
    "attributes":{
    
    },
    "cdk_name_key": "name",

    "cdk_provider":"cdktf_cdktf_provider_google",
    "cdk_module":"compute_global_address",
    "cdk_class":"ComputeGlobalAddress"
}
""",
            'target_http_proxy.json':
            """
{
    "dependencies": {
        "url_map":{
            "resource" : "test_models/url_map",
            "default" : {
            
            }
        } 
    },
    "internalObjects": {
        
    },
    "attributes":{
    
    },
    "cdk_name_key": "name",

    "cdk_provider":"cdktf_cdktf_provider_google",
    "cdk_module":"compute_target_http_proxy",
    "cdk_class":"ComputeTargetHttpProxy"
}
""",
            'url_map.json':
            """
{
    "dependencies": {
        "default_service":{
            "resource" : "test_models/backend_service",
            "default" : {
            
            }
        }
    },
    "internalObjects": {
        
    },
    "attributes":{
    
    },
    "cdk_name_key": "name",

    "cdk_provider":"cdktf_cdktf_provider_google",
    "cdk_module":"compute_url_map",
    "cdk_class":"ComputeUrlMap"
}
""",
            'backend_service.json':
            """
{
    "dependencies": {
        "":{
            "resource" : "test_models/firewall",
            "default" : {
            
            }
        }
    },
    "internalObjects": {
        "backend":{
            "resource" : "test_models/backend",
            "defaults" : []
        },
        "health_checks":{
            "resource" : "test_models/health_check",
            "default" : [{
            
            }]
        }
    },
    "attributes":{
        "protocol": {
            "optional": true,
            "default": "HTTP",
            "cdk_key": "protocol"
        },
        "port": {
            "optional": true,
            "default": "http",
            "cdk_key": "port_name"
        },
        "load_balancing_scheme": {
            "optional": true,
            "default": "EXTERNAL",
            "cdk_key": "load_balancing_scheme"
        },
        "timeout_sec": {
            "optional": true,
            "default": 10,
            "cdk_key": "timeout_sec"
        },
        "enable_cdn": {
            "optional": true,
            "default": true,
            "cdk_key": "enable_cdn"
        }
    
    },
    "cdk_name_key": "name",

    "cdk_provider":"cdktf_cdktf_provider_google",
    "cdk_module":"compute_backend_service",
    "cdk_class":"ComputeBackendService"
}
""",
            'backend.json':
            """
{
    "dependencies": {
        "group": {
            "resource" : "test_models/instance_group",
            "default" : {
            
            }
        }
    },
    "internalObjects": {
        
    },
    "attributes":{
        "balancing_mode": {
            "optional": true,
            "default": "UTILIZATION",
            "cdk_key": "balancing_mode"
        },
        "capacity_scaler": {
            "optional": true,
            "default": 1.0,
            "cdk_key": "capacity_scaler"
        }
    },
    "cdk_name_key": "name",

    "cdk_provider":"cdktf_cdktf_provider_google",
    "cdk_module":"compute_backend_service",
    "cdk_class":"ComputeBackendServiceBackend"
}
""",
            'health_check.json':
            """
{
    "dependencies": {
    
    },
    "internalObjects": {
        
    },
    "attributes":{
        "port": {
            "optional": true,
            "default": 80,
            "cdk_key": "port"
        }
    },
    "cdk_name_key": "name",

    "cdk_provider":"cdktf_cdktf_provider_google",
    "cdk_module":"compute_http_health_check",
    "cdk_class":"ComputeHttpHealthCheck"
}
""",
            'firewall.json':
            """
{
    "dependencies": {
        "network": {
            "resource" : "test_models/network",
            "default" : {
            
            }
        }
    },
    "internalObjects": {
        "allow": {
            "resource" : "test_models/firewallAllow",
            "defaults" : [
                {
                    "protocol" : "tcp"
                }
            ]
        }
    },
    "attributes":{
        "direction": {
            "optional": true,
            "default": "INGRESS",
            "cdk_key": "direction"
        },
        "source_ranges": {
            "optional": true,
            "default": [],
            "cdk_key": "source_ranges"
        }
    },
    "cdk_name_key": "name",

    "cdk_provider":"cdktf_cdktf_provider_google",
    "cdk_module":"compute_firewall",
    "cdk_class":"ComputeFirewall"
}
""",
            'firewallAllow.json':
            """
{
    "dependencies": {
    
    },
    "internalObjects": { 
    
    },
    "attributes":{
        "protocol": {
            "optional": false,
            "cdk_key": "protocol"
        }
    },

    "cdk_provider":"cdktf_cdktf_provider_google",
    "cdk_module":"compute_firewall",
    "cdk_class":"ComputeFirewallAllow"
}
""",
            'network.json':
            """
{
    "dependencies": {
    
    },
    "internalObjects": {
    
    },
    "attributes":{
        "auto_create_subnetworks": {
            "optional": true,
            "default": false,
            "cdk_key": "auto_create_subnetworks"
        }
    },
    "cdk_name_key": "name",

    "cdk_provider":"cdktf_cdktf_provider_google",
    "cdk_module":"compute_network",
    "cdk_class":"ComputeNetwork"
}
""",
            'subnetwork.json':
            """
{
    "dependencies": {
        "network" : {
            "resource" : "test_models/network",
            "default" : {
            
            }
        }
    },
    "internalObjects": {
        
    },
    "attributes": {
        "ip_range": {
            "optional": false,
            "cdk_key": "ip_cidr_range"
        },
        "region": {
            "optional": true,
            "default": "europe-west1b",
            "cdk_key": "region"
        }
    },
    "cdk_name_key": "name",

    "cdk_provider":"cdktf_cdktf_provider_google",
    "cdk_module":"compute_subnetwork",
    "cdk_class":"ComputeSubnetwork"
}
""",
            'instance_group.json':
            """
{
    "dependencies": {
        "instance_group_manager": {
            "resource" : "test_models/instance_group_manager",
            "default" : {
            
            }
        }
    },
    "internalObjects": {
        
    },
    "attributes":{
    
    },
    "cdk_name_key": "name",

    "cdk_provider":"cdktf_cdktf_provider_google",
    "cdk_module":"storage_bucket",
    "cdk_class":"StorageBucket"
}
""",
            'instance_group_manager.json':
            """
{
    "dependencies": {
        "instance_template": {
            "resource" : "test_models/instance_template",
            "default" : {
            
            }
        }
    },
    "internalObjects": {
        
    },
    "attributes":{
        "region": {
            "optional": true,
            "default": "euw",
            "cdk_key": "balancing_mode"
        }
    },
    "cdk_name_key": "name",

    "cdk_provider":"cdktf_cdktf_provider_google",
    "cdk_module":"storage_bucket",
    "cdk_class":"StorageBucket"
}
""",
            'instance_template.json':
            """
{
    "dependencies": {
    
    },
    "internalObjects": {
        
    },
    "attributes":{
        "machine_type": {
            "optional": true,
            "default": "e2-small",
            "cdk_key": "machine_type"
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
test_models/network lb-net:

test_models/subnetwork lb-subnet:
\tregion: europe-west1b
\tip_range: 10.0.1.0/24

test_models/loadbalancer my-lb:
\tload_balancing_scheme: EXTERNAL
    """,
    )

    assert isinstance(out, list)
    assert len(out) == 3

    assert 'cdktf.out/stacks/test_models--network--lb-net' in out
    assert 'cdktf.out/stacks/test_models--subnetwork--lb-subnet' in out
    assert 'cdktf.out/stacks/test_models--loadbalancer--my-lb' in out
