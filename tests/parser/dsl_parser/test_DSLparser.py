from thipster.engine.ParsedFile import ParsedDict, ParsedFile, ParsedList, ParsedLiteral
from thipster.parser.dsl_parser.DSLParser import DSLParser
from thipster.parser.dsl_parser.DSLParser import DSLParserPathNotFound
from thipster.parser.dsl_parser.Token import TOKENTYPES as TT
import os
from thipster.parser.dsl_parser.TokenParser import DSLConditionException,\
    DSLSyntaxException, DSLUnexpectedEOF
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

    parser = DSLParser

    files = parser._DSLParser__getfiles(path_input)

    assert isinstance(files, dict)
    assert len(files) == 3

    for k, v in files.items():
        assert 'test_file' in k
        assert v == 'content'

    _destroy_dir()


def test_get_absent_files():
    with pytest.raises(DSLParserPathNotFound):

        parser = DSLParser
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

    parser = DSLParser
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
    assert region.value == 'euw'


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


def test_parse_list():
    out = __test_file(
        file="""bucket my-bucket:
\tregion: 
\t\t- toto
\t\t- titi
\t\t- tata
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
    assert len(region.value) == 3

    out = __test_file(
        file="""bucket my-bucket:
\tregion: [toto, titi, tata]
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
    assert len(region.value) == 3

    out = __test_file(
        file="""bucket my-bucket:
\tregion: []
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
    assert len(region.value) == 0


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
\tregion: euw if 1 == 1 else us
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
\tregion: euw if 1 == 2 else us
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
\t\t- euw if 1 == 1 else us
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


def test_var_in_name():
    out = __test_file(
        file="""bucket my-bucket#i: amount: 3 #i
\tregion: #i
""",
    )

    assert len(out.resources) == 3
    for bucket, i in zip(out.resources, range(1, 4)):
        assert bucket.type == 'bucket'
        assert bucket.name == 'my-bucket' + str(i)
        assert len(bucket.attributes) == 1

        region = bucket.attributes[0]
        assert region.name == 'region'
        assert region.value == i


def test_comparisons():
    def test_cmp(cmpExpr: str, result: str):
        out = __test_file(
            file=f"""bucket my-bucket:
\tregion: truCase if {cmpExpr} else falsCase
""",
        )

        assert len(out.resources) == 1

        bucket = out.resources[0]
        assert bucket.type == 'bucket'
        assert bucket.name == 'my-bucket'
        assert len(bucket.attributes) == 1

        region = bucket.attributes[0]
        assert region.name == 'region'
        assert region.value == result

    # OR
    test_cmp('(1==1 OR 1==2)', 'truCase')

    # AND
    test_cmp('(not 1==1 AND false)', 'falsCase')

    # LTE
    test_cmp('2<=2', 'truCase')
    test_cmp('3<=2', 'falsCase')

    # GTE
    test_cmp('2>=2', 'truCase')
    test_cmp('1>=2', 'falsCase')

    # LT
    test_cmp('1<2', 'truCase')
    test_cmp('2<2', 'falsCase')

    # GT
    test_cmp('3>2', 'truCase')
    test_cmp('2>2', 'falsCase')

    # NE
    test_cmp('3!=2', 'truCase')
    test_cmp('2!=2', 'falsCase')


def test_arithmetic():
    # PLUS
    out = __test_file(
        file="""bucket my-bucket:
\tvalue: -1+1-3
""",
    )

    assert len(out.resources) == 1

    bucket = out.resources[0]
    assert bucket.type == 'bucket'
    assert bucket.name == 'my-bucket'
    assert len(bucket.attributes) == 1

    region = bucket.attributes[0]
    assert region.name == 'value'
    assert region.value == 3

    # OPERATION ORDER
    out = __test_file(
        file="""bucket my-bucket:
\tvalue2: 10/2+3*3
""",
    )

    assert len(out.resources) == 1

    bucket = out.resources[0]
    assert bucket.type == 'bucket'
    assert bucket.name == 'my-bucket'
    assert len(bucket.attributes) == 1

    region = bucket.attributes[0]
    assert region.name == 'value2'
    assert region.value == 14

    out = __test_file(
        file="""bucket my-bucket:
\tvalue: 10/(2+3)*3
""",
    )

    assert len(out.resources) == 1

    bucket = out.resources[0]
    assert bucket.type == 'bucket'
    assert bucket.name == 'my-bucket'
    assert len(bucket.attributes) == 1

    region = bucket.attributes[0]
    assert region.name == 'value'
    assert region.value == 6

    # POW
    out = __test_file(
        file="""bucket my-bucket:
\tvalue: (-2)^4
""",
    )

    assert len(out.resources) == 1

    bucket = out.resources[0]
    assert bucket.type == 'bucket'
    assert bucket.name == 'my-bucket'
    assert len(bucket.attributes) == 1

    region = bucket.attributes[0]
    assert region.name == 'value'
    assert region.value == 16


def __test_parser_raises(mocker, input: str, exception: Exception)\
        -> pytest.ExceptionInfo:
    with pytest.raises(exception) as exc_info:
        __test_file(
            file=input,
        )

    return exc_info


def __test_syntax_error(
    mocker, input: str, ln: int, col: int,
    expected: str, got: str,
):

    exc_info = __test_parser_raises(mocker, input, DSLSyntaxException)

    exp = str(' or '.join(list(map(lambda x: str(x), expected))))\
        if isinstance(expected, list) else str(expected.value)

    assert repr(exc_info.value) == f'(File : \
{os.getcwd()}/test/test_file.thips, Ln {str(ln)}, Col {str(col)}) :\n\t\
Syntax error : Expected {exp}, got {str(got.value)}'


def test_syntax_error_resource(mocker):
    # MISSING NAME
    input = """bucket :
            """
    __test_syntax_error(
        mocker, input=input, ln=1, col=8,
        expected=[TT.STRING, TT.VAR], got=TT.COLON,
    )


def test_syntax_error_dict(mocker):
    # MISSING COLON
    input = """
bucket my-bucket:
\tregion euw
            """
    __test_syntax_error(
        mocker, input=input, ln=3, col=9,
        expected=TT.COLON, got=TT.STRING,
    )

    # MISSING TAB
    input = """
bucket my-bucket:
region: euw
            """
    __test_syntax_error(
        mocker, input=input, ln=3, col=1,
        expected=TT.TAB, got=TT.STRING,
    )

    # MISSING VALUE
    input = """
bucket my-bucket:
\ttest:
\tregion: euw
"""
    __test_syntax_error(
        mocker, input=input, ln=3, col=7,
        expected=TT.STRING, got=TT.NEWLINE,
    )

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
    # MISSING COLON
    input = """
bucket my-bucket: amount 3
\tregion: euw
"""
    __test_syntax_error(
        mocker, input=input, ln=2, col=26,
        expected=TT.COLON, got=TT.INT,
    )

    # NO INTEGER
    input = """
bucket my-bucket: amount: str
\tregion: euw
"""
    __test_syntax_error(
        mocker, input=input, ln=2, col=27,
        expected=[TT.INT, TT.FLOAT, TT.PARENTHESES_START], got=TT.STRING,
    )


def test_syntax_error_if(mocker):
    # MISSING CONDITION
    input = """
bucket my-bucket: if
"""
    __test_parser_raises(mocker, input=input, exception=DSLConditionException)

    # UNEXPECTED IF ELSE
    input = """
bucket my-bucket: if 1 == 1 else bbb
"""
    __test_syntax_error(
        mocker, input=input, ln=2, col=29,
        expected=TT.NEWLINE, got=TT.ELSE,
    )


def test_syntax_error_if_else(mocker):
    # MISSING ELSE VALUE
    input = """
bucket my-bucket:
\ttoto:
\t\tfoo : bar if true else
"""
    __test_syntax_error(
        mocker, input=input, ln=4, col=25,
        expected=[TT.INT, TT.FLOAT, TT.PARENTHESES_START], got=TT.NEWLINE,
    )

    # MISSING CONDITION VALUE
    input = """
bucket my-bucket:
\ttoto:
\t\tfoo : bar if  else bbb
"""
    __test_parser_raises(mocker, input=input, exception=DSLConditionException)


def test_syntax_error_unexpected_token(mocker):
    # RESERVED TOKEN NAME
    input = """
bucket if:
\tregion: euw
"""
    __test_syntax_error(
        mocker, input=input, ln=2, col=8,
        expected=[TT.STRING, TT.VAR], got=TT.IF,
    )
