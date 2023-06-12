import uuid

import pytest
import tftest

from .test_tools import (
    assert_number_of_resource_type_is,
    assert_resource_created,
    assert_resource_parameters_are,
    get_function_name,
    process_file,
)


@pytest.fixture
def apply_output():
    def _apply_output(function_name):
        tf = tftest.TerraformTest(
            tfdir='.',
            basedir=f'test/{function_name}',
        )

        tf.setup()
        try:
            tf.apply()
            yield tf.output()
        except Exception as e:
            raise e

        finally:
            tf.destroy()

    return _apply_output


def test_bucket(apply_output):
    function_name = get_function_name()

    bucket_name = f'test-bucket-{uuid.uuid4()}'
    clean_up = process_file(
        directory=function_name,
        file=f"""
bucket {bucket_name}:
\tregion : europe-west1
    """,
    )

    try:
        # Assertions on plan
        assert_number_of_resource_type_is('google_storage_bucket', 1)
        bucket = assert_resource_created('google_storage_bucket', bucket_name)
        assert_resource_parameters_are(bucket, ['location'])

        # Test apply
        _ = [o for o in apply_output(function_name)]

    except Exception as e:
        raise e
    finally:
        clean_up()


def test_lb(apply_output):
    function_name = get_function_name()

    clean_up = process_file(
        directory=function_name,
        file="""
network lb-net:

subnetwork lb-subnet:
\tnetwork: lb-net
\tregion: europe-west1
\tip_range: 10.0.1.0/24

loadbalancer my-lb:
\tnetwork: lb-net
\tload_balancing_scheme: EXTERNAL
    """,
    )

    try:
        # Assertions on plan
        assert_number_of_resource_type_is('google_compute_network', 1)
        assert_resource_created('google_compute_network', 'lb-net')

        assert_number_of_resource_type_is('google_compute_subnetwork', 1)
        assert_resource_created('google_compute_subnetwork', 'lb-subnet')

        # Test apply
        _ = [o for o in apply_output(function_name)]

    except Exception as e:
        raise e
    finally:
        clean_up()
