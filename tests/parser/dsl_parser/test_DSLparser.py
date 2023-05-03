from engine.ParsedFile import ParsedDict, ParsedFile, ParsedList, ParsedLiteral
from parser.dsl_parser.DSLParser import DSLParser
from parser.dsl_parser.DSLParser import DSLParserPathNotFound
import os
from parser.dsl_parser.TokenParser import DSLSyntaxException, DSLUnexpectedEOF
import pytest


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


def test_get_files():
    path_input = 'test'
    _destroy_dir = create_dir(
        path_input,
        {f'test_file{i}.thips': 'content' for i in range(1, 4)},
    )

    parser = DSLParser()

    files = parser._DSLParser__getfiles(path_input)

    assert isinstance(files, dict)
    assert len(files) == 3

    for k, v in files.items():
        assert 'test_file' in k
        assert v == 'content'

    _destroy_dir()


def test_get_absent_files():
    with pytest.raises(DSLParserPathNotFound):

        parser = DSLParser()
        parser._DSLParser__getfiles('inexistant_path')


def __test_file(file: str):
    path_input = 'test'
    _destroy_dir = create_dir(
        path_input,
        {
            'test_file.thips':
            file,
        },
    )

    parser = DSLParser()
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
        file="""bucket my-bucket:
\tregion: euw
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


def test_parse_empty_file():
    out = __test_file(
        file="""""",
    )

    assert len(out.resources) == 0


def test_parse_simple_file_with_newlines():
    out = __test_file(
        file="""

bucket my-bucket:


\tregion: euw

bucket my-bucket2:
\tregion: euw



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


def test_parse_simple_file_with_empty_lines():
    out = __test_file(
        file="""bucket my-bucket:
\tregion: euw
\t
bucket my-bucket2:
\tregion: euw
\t\t

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


def test_parse_dict_list_in_dict():
    out = __test_file(
        file="""bucket my-bucket:
\ttoto:
\t\t aaa: val1
\t\t bbb: val2
\ttata:
\t\t- ccc
\t\t- ddd
""",
    )

    assert len(out.resources) == 1

    bucket = out.resources[0]
    assert bucket.type == 'bucket'
    assert bucket.name == 'my-bucket'
    assert len(bucket.attributes) == 2

    toto = bucket.attributes[0]
    assert toto.name == 'toto'
    assert type(toto._ParsedAttribute__value) == ParsedDict
    tata = bucket.attributes[1]
    assert tata.name == 'tata'
    assert type(tata._ParsedAttribute__value) == ParsedList


def test_parse_if_else():
    # IN DICT
    out = __test_file(
        file="""bucket my-bucket:
\tregion: euw if "1==1" else us
""",
    )

    assert len(out.resources) == 1

    bucket = out.resources[0]
    assert bucket.type == 'bucket'
    assert bucket.name == 'my-bucket'
    assert len(bucket.attributes) == 1

    region = bucket.attributes[0]
    assert region.name == 'region'
    assert region.value == 'euw'

    # ELSE CASE
    out = __test_file(
        file="""bucket my-bucket:
\tregion: euw if "1==2" else us
""",
    )

    assert len(out.resources) == 1

    bucket = out.resources[0]
    assert bucket.type == 'bucket'
    assert bucket.name == 'my-bucket'
    assert len(bucket.attributes) == 1

    region = bucket.attributes[0]
    assert region.name == 'region'
    assert region.value == 'us'

    # IN LIST
    out = __test_file(
        file="""bucket my-bucket:
\tregion:
\t\t- euw if "1==1" else us
""",
    )

    assert len(out.resources) == 1

    bucket = out.resources[0]
    assert bucket.type == 'bucket'
    assert bucket.name == 'my-bucket'
    assert len(bucket.attributes) == 1

    region = bucket.attributes[0]
    assert region.name == 'region'
    assert type(region._ParsedAttribute__value) == ParsedList

    assert len(region.value) == 1
    r = region.value[0]
    assert r.value == 'euw'


def test_parse_literal_types():
    out = __test_file(
        file="""bucket my-bucket:
\tregion: euw
""",
    )

    assert len(out.resources) == 1

    bucket = out.resources[0]
    assert bucket.type == 'bucket'
    assert bucket.name == 'my-bucket'
    assert len(bucket.attributes) == 1

    region = bucket.attributes[0]
    assert region.name == 'region'
    assert region.value == 'euw'

    out = __test_file(
        file="""bucket my-bucket:
\tregion: 1
""",
    )

    assert len(out.resources) == 1

    bucket = out.resources[0]
    assert bucket.type == 'bucket'
    assert bucket.name == 'my-bucket'
    assert len(bucket.attributes) == 1

    region = bucket.attributes[0]
    assert region.name == 'region'
    assert region.value == 1

    out = __test_file(
        file="""bucket my-bucket:
\tregion: 3.2
""",
    )

    assert len(out.resources) == 1

    bucket = out.resources[0]
    assert bucket.type == 'bucket'
    assert bucket.name == 'my-bucket'
    assert len(bucket.attributes) == 1

    region = bucket.attributes[0]
    assert region.name == 'region'
    assert region.value == 3.2

    out = __test_file(
        file="""bucket my-bucket:
\tregion: true
""",
    )

    assert len(out.resources) == 1

    bucket = out.resources[0]
    assert bucket.type == 'bucket'
    assert bucket.name == 'my-bucket'
    assert len(bucket.attributes) == 1

    region = bucket.attributes[0]
    assert region.name == 'region'
    assert region.value is True


def test_parse_amount():
    out = __test_file(
        file="""bucket my-bucket: amount: 3
\tregion: euw
""",
    )

    assert len(out.resources) == 3
    for bucket in out.resources:
        assert bucket.type == 'bucket'
        assert 'my-bucket' in bucket.name
        assert len(bucket.attributes) == 1

        region = bucket.attributes[0]
        assert region.name == 'region'
        assert region.value == 'euw'

    out = __test_file(
        file="""bucket my-bucket: amount: 3 #i
\tregion: #i
""",
    )

    assert len(out.resources) == 3
    for bucket, i in zip(out.resources, range(1, 4)):
        assert bucket.type == 'bucket'
        assert 'my-bucket' in bucket.name
        assert len(bucket.attributes) == 1

        region = bucket.attributes[0]
        assert region.name == 'region'
        assert region.value == i


def __test_parser_raises(mocker, input: str, exception: Exception)\
        -> pytest.ExceptionInfo:
    with pytest.raises(exception) as exc_info:
        __test_file(
            file=input,
        )

    return exc_info


def __test_syntax_error(mocker, input: str, ln: int, col: int):
    exc_info = __test_parser_raises(mocker, input, DSLSyntaxException)

    assert repr(exc_info.value) == f'Syntax error at (File : \
{os.getcwd()}/test/test_file.thips, Ln {str(ln)}, Col {str(col)})'


def test_syntax_error_resource(mocker):
    # MISSING NAME
    input = """bucket :
            """
    __test_syntax_error(mocker, input=input, ln=1, col=8)


def test_syntax_error_dict(mocker):
    # MISSING COLUMN
    input = """
bucket my-bucket:
\tregion euw
            """
    __test_syntax_error(mocker, input=input, ln=3, col=9)

    # MISSING TAB
    input = """
bucket my-bucket:
region: euw
            """
    __test_syntax_error(mocker, input=input, ln=3, col=1)

    # MISSING VALUE
    input = """
bucket my-bucket:
\ttest:
\tregion: euw
"""
    __test_syntax_error(mocker, input=input, ln=4, col=1)

    # MISSING VALUE 2
    input = """
bucket my-bucket:
\ttest:





"""
    exc_info = __test_parser_raises(
        mocker, input=input, exception=DSLUnexpectedEOF,
    )

    assert repr(exc_info.value) == 'Unexpected EOF'


def test_syntax_error_amount(mocker):
    # MISSING COLUMN
    input = """
bucket my-bucket: amount 3
\tregion: euw
"""
    __test_syntax_error(mocker, input=input, ln=2, col=26)

    # NO INTEGER
    input = """
bucket my-bucket: amount: str
\tregion: euw
"""
    __test_syntax_error(mocker, input=input, ln=2, col=27)


def test_syntax_error_if(mocker):
    # MISSING CONDITION
    input = """
bucket my-bucket: if
"""
    __test_syntax_error(mocker, input=input, ln=2, col=21)

    # UNEXPECTED IF ELSE
    input = """
bucket my-bucket: if aaa else bbb
"""
    __test_syntax_error(mocker, input=input, ln=2, col=26)


def test_syntax_error_if_else(mocker):
    # MISSING ELSE VALUE
    input = """
bucket my-bucket:
\ttoto:
\t\t- foo : bar if aaa else
"""
    __test_syntax_error(mocker, input=input, ln=4, col=26)

    # MISSING CONDITION VALUE
    input = """
bucket my-bucket:
\ttoto:
\t\t- foo : bar if  else bbb
"""
    __test_syntax_error(mocker, input=input, ln=4, col=19)


def test_syntax_error_unexpected_token(mocker):
    # RESERVED TOKEN NAME
    input = """
bucket if:
\tregion: euw
"""
    __test_syntax_error(mocker, input=input, ln=2, col=8)
