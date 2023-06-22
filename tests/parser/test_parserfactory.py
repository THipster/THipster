"""Tests for the parser factory."""
import pytest

from tests.test_tools import create_dir
from thipster.engine.parsed_file import ParsedFile
from thipster.parser import ParserFactory
from thipster.parser.exceptions import NoFileFoundError


def __test_file(files: str):
    path_input = 'test'
    _destroy_dir = create_dir(
        path_input,
        files,
    )

    parser = ParserFactory()
    try:
        output = parser.run(path_input)

        assert type(output) == ParsedFile
    except Exception as e:
        raise e
    finally:
        _destroy_dir()

    return output


def test_yaml_file():
    """Test the parser with .YAML and .YML files."""
    # .YAML
    out = __test_file(
        {
            'test_file.yaml':
            """bucket:
  name: my_bucket
  region: euw
""",
        },
    )
    assert len(out.resources) == 1

    bucket = out.resources[0]
    assert bucket.resource_type == 'bucket'
    assert bucket.name == 'my_bucket'
    assert len(bucket.attributes) == 1

    region = bucket.attributes[0]
    assert region.name == 'region'
    assert region.value == 'euw'

    # .YML
    out = __test_file(
        {
            'test_file.yml':
            """bucket:
  name: my-bucket
  region: euw
""",
        },
    )
    assert len(out.resources) == 1

    bucket = out.resources[0]
    assert bucket.resource_type == 'bucket'
    assert bucket.name == 'my-bucket'
    assert len(bucket.attributes) == 1

    region = bucket.attributes[0]
    assert region.name == 'region'
    assert region.value == 'euw'


def test_thips_file():
    """Test the parser with .THIPS files."""
    out = __test_file(
        {
            'test_file.thips':
            """bucket my-bucket:
\tregion: euw
""",
        },
    )
    assert len(out.resources) == 1

    bucket = out.resources[0]
    assert bucket.resource_type == 'bucket'
    assert bucket.name == 'my-bucket'
    assert len(bucket.attributes) == 1

    region = bucket.attributes[0]
    assert region.name == 'region'
    assert region.value == 'euw'


def test_two_types_of_file():
    """Test the parser with both .THIPS and .YAML files."""
    out = __test_file(
        {
            'test_file.thips':
            """bucket my-bucket1:
\tregion: euw
""",
            'test_file.yml':
            """bucket:
  name: my-bucket2
  region: euw
""",
        },
    )
    assert len(out.resources) == 2

    for bucket in out.resources:
        assert bucket.resource_type == 'bucket'
        assert 'my-bucket' in bucket.name
        assert len(bucket.attributes) == 1

        region = bucket.attributes[0]
        assert region.name == 'region'
        assert region.value == 'euw'


def test_no_parsable_file():
    """Test the parser with no parsable files."""
    with pytest.raises(NoFileFoundError):
        __test_file(
            {
                'test_file.txt':
                """ """,
                'test_file2.txt':
                """ """,
            },
        )


def test_one_parsable_file():
    """Test the parser with one parsable file and one non-parsable file."""
    out = __test_file(
        {
            'test_file.thips':
            """bucket my-bucket1:
\tregion: euw
""",
            'test_file2.txt':
            """ """,
        },
    )

    assert len(out.resources) == 1

    bucket = out.resources[0]
    assert bucket.resource_type == 'bucket'
    assert bucket.name == 'my-bucket1'
    assert len(bucket.attributes) == 1

    region = bucket.attributes[0]
    assert region.name == 'region'
    assert region.value == 'euw'
