from thipster.engine.ParsedFile import ParsedDict, ParsedFile, ParsedList, ParsedLiteral
from thipster.parser.YAMLParser import YAMLParser, YAMLParserNoName
import os
import pytest


def __test_parser_raises(mocker, input: str, exception: Exception)\
        -> pytest.ExceptionInfo:
    with pytest.raises(exception) as exc_info:
        __test_file(
            file=input,
        )

    return exc_info


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

        assert type(output) == ParsedFile
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
    assert type(region._ParsedAttribute__value) == ParsedLiteral
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
    assert type(region._ParsedAttribute__value) == ParsedLiteral
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
    assert type(toto._ParsedAttribute__value) == ParsedDict


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
    assert type(toto._ParsedAttribute__value) == ParsedList
    assert len(toto.value) == 2


def test_syntax_error_no_name(mocker):
    input = """bucket:
  toto:
    - aaa
    - bbb
"""
    __test_parser_raises(mocker, input, YAMLParserNoName)
