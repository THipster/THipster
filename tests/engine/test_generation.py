"""Test the generation of Terraform files."""
import uuid

import pytest

from tests.test_tools import (
    assert_number_of_resource_type_is,
    assert_resource_created,
    get_function_name,
    get_resource_parameter,
    process_file,
)
from thipster.terraform.exceptions import (
    CDKCyclicDependenciesError,
    CDKDependencyNotDeclaredError,
    CDKMissingAttributeInDependencyError,
)


def test_empty_bucket():
    """Test the generation of an empty bucket."""
    function_name = get_function_name()

    bucket_name = f'empty-bucket-{uuid.uuid4().int}'
    clean_up = process_file(
        directory=function_name,
        file=f"""
bucket {bucket_name}:

""",
        mock_auth=True,
    )

    # Assertions on plan
    assert_number_of_resource_type_is('google_storage_bucket', 1)
    assert_resource_created('google_storage_bucket', bucket_name)

    clean_up()


def test_empty_bucket_two():
    """Test the generation of two buckets (one is empty)."""
    function_name = get_function_name()

    empty_bucket_name = f'empty-bucket-{uuid.uuid4().int}'
    bucket_name = f'empty-bucket-{uuid.uuid4().int}'
    clean_up = process_file(
        directory=function_name,
        file=f"""
bucket {empty_bucket_name}:

bucket {bucket_name}:
    region: europe-west2
""",
        mock_auth=True,
    )

    # Assertions on plan
    assert_number_of_resource_type_is('google_storage_bucket', 2)
    assert_resource_created('google_storage_bucket', empty_bucket_name)
    assert_resource_created('google_storage_bucket', bucket_name)

    clean_up()


def test_dep_with_no_options():
    """Test the generation of a bucket with a missing attribute in its dependency."""
    function_name = get_function_name()

    with pytest.raises(CDKMissingAttributeInDependencyError):
        clean_up = process_file(
            directory=function_name,
            file="""
bucket_bad_dep_parent my-bucket:
\tregion : euw
""",
            mock_auth=True,
        )

        clean_up()


def test_cyclic_deps():
    """Test the generation of a bucket with a cyclic dependency."""
    function_name = get_function_name()

    with pytest.raises(CDKCyclicDependenciesError):
        clean_up = process_file(
            directory=function_name,
            file="""
bucket_bad_dep_cyclic my-bucket:
\tregion : euw
""",
            mock_auth=True,
        )

        clean_up()


def test_default_internal_object():
    """Test the generation of a firewall with default internal objects."""
    function_name = get_function_name()

    clean_up = process_file(
        directory=function_name,
        file="""
firewall testparent:
\tdirection: EGRESS
""",
        mock_auth=True,
    )

    clean_up()


def test_explicit_internal_object():
    """Test the generation of a firewall with explicit internal objects."""
    function_name = get_function_name()
    clean_up = process_file(
        directory=function_name,
        file="""
firewall testparent:
\tdirection: EGRESS

\tallow:
\t\tprotocol: tcp
""",
        mock_auth=True,
    )

    clean_up()


def test_missing_explicit_dependency():
    """Test the generation of a subnetwork with a missing explicit dependency."""
    function_name = get_function_name()

    with pytest.raises(CDKDependencyNotDeclaredError):
        clean_up = process_file(
            directory=function_name,
            file="""
subnetwork lb-subnet:
\tnetwork: lb-net
\tregion: europe-west1b
\tip_range: 10.0.1.0/24
""",
            mock_auth=True,
        )

        clean_up()


def test_explicit_dependency():
    """Test the generation of a subnetwork with an explicit dependency."""
    function_name = get_function_name()

    clean_up = process_file(
        directory=function_name,
        file="""
network lb-net:

subnetwork lb-subnet:
\tnetwork: lb-net
\tregion: europe-west1
\tip_range: 10.0.1.0/24
""",
        mock_auth=True,
    )

    clean_up()


def test_bucket_cors():
    """Test the generation of a bucket with cors."""
    function_name = get_function_name()

    bucket_name = f'cors-bucket-{uuid.uuid4().int}'
    clean_up = process_file(
        directory=function_name,
        file=f"""
bucket {bucket_name}:
    cors:
        origin:
            - "http://example.com"
        method:
            - "*"
        responseHeader:
            - "*"
        maxAge: 400
""",
        mock_auth=True,
    )

    # Assertions on plan
    assert_number_of_resource_type_is('google_storage_bucket', 1)
    assert_resource_created('google_storage_bucket', bucket_name)

    clean_up()


def test_bucket_two_cors():
    """Test the generation of a bucket with two cors."""
    function_name = get_function_name()

    bucket_name = f'cors-bucket-{uuid.uuid4().int}'
    clean_up = process_file(
        directory=function_name,
        file=f"""
bucket:
  name: {bucket_name}
  cors:
    - origin:
      - "http://example.com"
      method:
      - "*"
      responseHeader:
      - "*"
      maxAge: 400
    - origin:
      - "http://example.com/other"
      method:
      - "*"
      responseHeader:
      - "*"
      maxAge: 600
""",
        file_type='yaml',
        mock_auth=True,
    )

    # Assertions on plan
    assert_number_of_resource_type_is('google_storage_bucket', 1)
    bucket = assert_resource_created('google_storage_bucket', bucket_name)
    cors_block = get_resource_parameter(bucket, 'cors')

    assert len(cors_block) == 2

    clean_up()


def test_subnetwork_in_network():
    """Test the generation of multiple subnetworks in a network."""
    function_name = get_function_name()

    network_name = f'network-{uuid.uuid4().int}'
    clean_up = process_file(
        directory=function_name,
        file=f"""
network:
  name: {network_name}
  auto_create_subnetworks: false
  subnetwork:
    - region: europe-west1
      ip_range: 10.0.1.0/24
    - region: us-west1
      ip_range: 10.0.2.0/24
""",
        file_type='yaml',
        mock_auth=True,
    )

    # Assertions on plan
    assert_number_of_resource_type_is('google_compute_network', 1)
    assert_resource_created('google_compute_network', network_name)

    assert_number_of_resource_type_is('google_compute_subnetwork', 2)

    clean_up()
