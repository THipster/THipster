import pytest

import thipster.engine.parsed_file as pf
from thipster.parser import YAMLParser
from thipster.parser.yaml_parser import YAMLParserNoName

from ..test_tools import create_dir


def __test_parser_raises(mocker, input: str, exception: Exception)\
        -> pytest.ExceptionInfo:
    with pytest.raises(exception) as exc_info:
        __test_file(
            file=input,
        )

    return exc_info


def __test_file(file: str):
    path_input = 'test'
    _destroy_dir = create_dir(
        path_input,
        {
            'test_file.yaml':
            file,
        },
    )

    parser = YAMLParser
    try:
        output = parser.run(path_input)

        assert isinstance(output, pf.ParsedFile)
    except Exception as e:
        raise e
    finally:
        _destroy_dir()

    return output


def test_parse_simple_file():
    out = __test_file(
        file="""bucket:
  name: my-bucket
  region: euw
""",
    )
    assert len(out.resources) == 1

    bucket = out.resources[0]
    assert bucket.type == 'bucket'
    assert bucket.name == 'my-bucket'
    assert len(bucket.attributes) == 1

    region = bucket.attributes[0]
    assert region.name == 'region'
    assert isinstance(region._ParsedAttribute__value, pf.ParsedLiteral)
    assert region.value == 'euw'


def test_parse_simple_jinja_file():
    out = __test_file(
        file="""
{% set name = "test_name" %}
{% set region = "europe-west1" %}
bucket:
  name: {{ name|lower }}
  region: {{ region }}
""",
    )
    assert len(out.resources) == 1

    bucket = out.resources[0]
    assert bucket.type == 'bucket'
    assert bucket.name == 'test_name'
    assert len(bucket.attributes) == 1

    region = bucket.attributes[0]
    assert region.name == 'region'
    assert isinstance(region._ParsedAttribute__value, pf.ParsedLiteral)
    assert region.value == 'europe-west1'


def test_parse_two_resources():
    out = __test_file(
        file="""bucket:
  - name: my-bucket1
    region: euw
  - name: my-bucket2
    region: euw
""",
    )
    assert len(out.resources) == 2
    for bucket in out.resources:
        assert bucket.type == 'bucket'
        assert 'my-bucket' in bucket.name
        assert len(bucket.attributes) == 1

        region = bucket.attributes[0]
        assert region.name == 'region'
        assert region.value == 'euw'


def test_parse_dict_in_dict():
    out = __test_file(
        file="""bucket:
  name: my-bucket
  region: euw
  toto:
    aaa: val1
    bbb: val2
""",
    )
    assert len(out.resources) == 1

    bucket = out.resources[0]
    assert bucket.type == 'bucket'
    assert bucket.name == 'my-bucket'
    assert len(bucket.attributes) == 2

    region = bucket.attributes[0]
    assert region.name == 'region'
    assert region.value == 'euw'

    toto = bucket.attributes[1]
    assert toto.name == 'toto'
    assert isinstance(toto._ParsedAttribute__value, pf.ParsedDict)


def test_parse_list():
    out = __test_file(
        file="""bucket:
  name: my-bucket
  toto:
    - aaa
    - bbb
""",
    )
    assert len(out.resources) == 1

    bucket = out.resources[0]
    assert bucket.type == 'bucket'
    assert bucket.name == 'my-bucket'
    assert len(bucket.attributes) == 1

    toto = bucket.attributes[0]
    assert toto.name == 'toto'
    assert isinstance(toto._ParsedAttribute__value, pf.ParsedList)
    assert len(toto.value) == 2

    for val in toto.value:
        assert isinstance(val, pf.ParsedLiteral)


def test_parse_dict_in_list():
    out = __test_file(
        file="""bucket:
  name: my-bucket
  toto:
    - aaa : 12
      bbb : OK
    - ccc : 10
      ddd : OK
""",
    )
    assert len(out.resources) == 1

    bucket = out.resources[0]
    assert bucket.type == 'bucket'
    assert bucket.name == 'my-bucket'
    assert len(bucket.attributes) == 1

    toto = bucket.attributes[0]
    assert toto.name == 'toto'
    assert isinstance(toto._ParsedAttribute__value, pf.ParsedList)
    assert len(toto.value) == 2

    for val in toto.value:
        assert isinstance(val, pf.ParsedDict)
        assert len(val.value) == 2
        for v in val.value:
            assert isinstance(v, pf.ParsedAttribute)


def test_syntax_error_no_name(mocker):
    input = """bucket:
  toto:
    - aaa
    - bbb
"""
    __test_parser_raises(mocker, input, YAMLParserNoName)
