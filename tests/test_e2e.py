"""End to end tests for the thipster tool.

Starts from a .thips or .yaml file and tests the creation of the resources on GCP.
"""
import os
import random
import uuid
from pathlib import Path

import pytest
import tftest

from .test_tools import (
    assert_number_of_resource_type_is,
    assert_resource_created,
    assert_resource_parameters_are,
    get_function_name,
    process_file,
)

AUTH_FILE_PATH = Path(Path.cwd(), 'tests/credentials.json')


@pytest.fixture
def apply_output():
    """Apply terraform and return output."""
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


@pytest.fixture
def authentication():
    """Authenticate to GCP."""
    delete_credentials = False
    if (
        not Path(
            os.getenv('HOME'),
            '.config/gcloud/application_default_credentials.json',
        ).exists()
        and (
            os.getenv('GOOGLE_APPLICATION_CREDENTIALS') is not None
            or os.getenv('GOOGLE_APPLICATION_CREDENTIALS') != ''
        )
    ):

        delete_credentials = True
        if os.getenv('GOOGLE_APPLICATION_CREDENTIALS_CONTENT') is None:
            msg = 'No credentials available'
            raise Exception(msg)

        with Path(AUTH_FILE_PATH).open('w') as auth_file:
            auth_file.write(
                os.environ['GOOGLE_APPLICATION_CREDENTIALS_CONTENT'],
            )
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = AUTH_FILE_PATH.as_posix()

    yield

    if delete_credentials:
        Path(AUTH_FILE_PATH).unlink()


def test_bucket(apply_output, authentication):
    """Test bucket creation."""
    _ = authentication
    function_name = get_function_name()

    bucket_name = f'test-bucket-{uuid.uuid4().int}'
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
        _ = list(apply_output(function_name))

    except Exception as e:
        raise e
    finally:
        clean_up()


def test_lb(apply_output, authentication):
    """Test load balancer creation."""
    _ = authentication
    function_name = get_function_name()

    test_id = random.randint(0, 10000)
    clean_up = process_file(
        directory=function_name,
        file=f"""
network lb-net-{test_id}:

subnetwork lb-subnet-{test_id}:
\tnetwork: lb-net-{test_id}
\tregion: europe-west1
\tip_range: 10.0.1.0/24

loadbalancer my-lb-{test_id}:
\tnetwork: lb-net-{test_id}
\tload_balancing_scheme: EXTERNAL
    """,
    )

    try:
        # Assertions on plan
        assert_number_of_resource_type_is('google_compute_network', 1)
        assert_resource_created('google_compute_network', f'lb-net-{test_id}')

        assert_number_of_resource_type_is('google_compute_subnetwork', 1)
        assert_resource_created(
            'google_compute_subnetwork', f'lb-subnet-{test_id}',
        )

        # Test apply
        _ = list(apply_output(function_name))

    except Exception as e:
        raise e
    finally:
        clean_up()
