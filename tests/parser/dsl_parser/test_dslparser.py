"""Tests for the DSLParser class."""
from pathlib import Path

import pytest

import thipster.engine.parsed_file as pf
from tests.test_tools import create_dir
from thipster.parser import DSLParser
from thipster.parser.dsl_parser.exceptions import (
    DSLArithmeticError,
    DSLConditionError,
    DSLParserPathNotFoundError,
    DSLSyntaxError,
    DSLUnexpectedEOFError,
)
from thipster.parser.dsl_parser.token import TOKENTYPES as TT


def test_get_files():
    """Test the getfiles method."""
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
    """Test the getfiles method with an inexistant path."""
    with pytest.raises(DSLParserPathNotFoundError):

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

        assert isinstance(output, pf.ParsedFile)
    except Exception as e:
        raise e
    finally:
        _destroy_dir()

    return output


def test_parse_simple_file():
    """Test the parsing of a simple file."""
    out = __test_file(
        file="""bucket my-bucket:
\tregion: euw
""",
    )

    assert len(out.resources) == 1

    bucket = out.resources[0]
    assert bucket.resource_type == 'bucket'
    assert bucket.name == 'my-bucket'
    assert len(bucket.attributes) == 1

    region = bucket.attributes[0]
    assert region.name == 'region'
    assert isinstance(region._ParsedAttribute__value, pf.ParsedLiteral)
    assert region.value == 'euw'


def test_parse_empty_file():
    """Test the parsing of an empty file."""
    out = __test_file(
        file="""""",
    )

    assert len(out.resources) == 0


def test_parse_simple_file_with_newlines():
    """Test the parsing of a simple file with newlines."""
    out = __test_file(
        file="""

bucket    my-bucket:

\tregion:   euw

bucket my-bucket2:
\tregion: euw



   """,
    )
    assert len(out.resources) == 2
    for bucket in out.resources:
        assert bucket.resource_type == 'bucket'
        assert 'my-bucket' in bucket.name
        assert len(bucket.attributes) == 1

        region = bucket.attributes[0]
        assert region.name == 'region'
        assert region.value == 'euw'


def test_parse_simple_file_with_empty_lines():
    """Test the parsing of a simple file with empty lines."""
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
        assert bucket.resource_type == 'bucket'
        assert 'my-bucket' in bucket.name
        assert len(bucket.attributes) == 1

        region = bucket.attributes[0]
        assert region.name == 'region'
        assert region.value == 'euw'


def test_parse_list():
    """Test the parsing of a list."""
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
    assert bucket.resource_type == 'bucket'
    assert bucket.name == 'my-bucket'
    assert len(bucket.attributes) == 1

    region = bucket.attributes[0]
    assert region.name == 'region'
    assert isinstance(region._ParsedAttribute__value, pf.ParsedList)
    assert len(region.value) == 3

    out = __test_file(
        file="""bucket my-bucket:
\tregion: [toto, titi, tata]
""",
    )

    assert len(out.resources) == 1

    bucket = out.resources[0]
    assert bucket.resource_type == 'bucket'
    assert bucket.name == 'my-bucket'
    assert len(bucket.attributes) == 1

    region = bucket.attributes[0]
    assert region.name == 'region'
    assert isinstance(region._ParsedAttribute__value, pf.ParsedList)
    assert len(region.value) == 3

    out = __test_file(
        file="""bucket my-bucket:
\tregion: []
""",
    )

    assert len(out.resources) == 1

    bucket = out.resources[0]
    assert bucket.resource_type == 'bucket'
    assert bucket.name == 'my-bucket'
    assert len(bucket.attributes) == 1

    region = bucket.attributes[0]
    assert region.name == 'region'
    assert isinstance(region._ParsedAttribute__value, pf.ParsedList)
    assert len(region.value) == 0


def test_parse_dict_list_in_dict():
    """Test the parsing of a list and dict in a dict."""
    out = __test_file(
        file="""bucket my-bucket:
\ttoto:
\t\taaa: val1
\t\tbbb: val2
\ttata:
\t\t- ccc
\t\t- ddd
""",
    )

    assert len(out.resources) == 1

    bucket = out.resources[0]
    assert bucket.resource_type == 'bucket'
    assert bucket.name == 'my-bucket'
    assert len(bucket.attributes) == 2

    toto = bucket.attributes[0]
    assert toto.name == 'toto'
    assert isinstance(toto._ParsedAttribute__value, pf.ParsedDict)
    tata = bucket.attributes[1]
    assert tata.name == 'tata'
    assert isinstance(tata._ParsedAttribute__value, pf.ParsedList)


def test_parse_dict_list_in_list():
    """Test the parsing of a list and dict in a dict."""
    out = __test_file(
        file="""
bucket my-bucket:
  toto:
  - aaa: val1
    bbb: val2
  - tata:
    - ccc
    - ddd
  - foo
""",
    )

    assert len(out.resources) == 1

    bucket = out.resources[0]
    assert bucket.resource_type == 'bucket'
    assert bucket.name == 'my-bucket'
    assert len(bucket.attributes) == 1

    toto = bucket.attributes[0]
    assert toto.name == 'toto'
    assert isinstance(toto._ParsedAttribute__value, pf.ParsedList)
    tested_list = toto.value
    assert len(tested_list) == 3
    assert isinstance(tested_list[0], pf.ParsedDict)
    assert isinstance(tested_list[1], pf.ParsedDict)
    assert isinstance(tested_list[2], pf.ParsedValue)


def test_parse_if_else():
    """Test the parsing of if else statements."""
    # IN DICT
    out = __test_file(
        file="""bucket my-bucket:
\tregion: euw if 1 == 1 else us
""",
    )

    assert len(out.resources) == 1

    bucket = out.resources[0]
    assert bucket.resource_type == 'bucket'
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
    assert bucket.resource_type == 'bucket'
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
    assert bucket.resource_type == 'bucket'
    assert bucket.name == 'my-bucket'
    assert len(bucket.attributes) == 1

    region = bucket.attributes[0]
    assert region.name == 'region'
    assert isinstance(region._ParsedAttribute__value, pf.ParsedList)

    assert len(region.value) == 1
    r = region.value[0]
    assert r.value == 'euw'


def test_parse_literal_types():
    """Test the parsing of literal types."""
    out = __test_file(
        file="""bucket my-bucket:
\tregion: euw
""",
    )

    assert len(out.resources) == 1

    bucket = out.resources[0]
    assert bucket.resource_type == 'bucket'
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
    assert bucket.resource_type == 'bucket'
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
    assert bucket.resource_type == 'bucket'
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
    assert bucket.resource_type == 'bucket'
    assert bucket.name == 'my-bucket'
    assert len(bucket.attributes) == 1

    region = bucket.attributes[0]
    assert region.name == 'region'
    assert region.value is True


def test_parse_comment():
    """Test the parsing of an amount."""
    out = __test_file(
        file="""bucket my-bucket:
\ttoto: aaaaa // MY COMMENT
\ttata: bbbbb
""",
    )

    assert len(out.resources) == 1
    bucket = out.resources[0]
    assert bucket.resource_type == 'bucket'
    assert 'my-bucket' in bucket.name
    assert len(bucket.attributes) == 2

    region = bucket.attributes[0]
    assert region.name == 'toto'
    assert region.value == 'aaaaa'
    region = bucket.attributes[1]
    assert region.name == 'tata'
    assert region.value == 'bbbbb'


def test_parse_amount():
    """Test the parsing of an amount."""
    out = __test_file(
        file="""bucket my-bucket: amount: 3
\tregion: euw
""",
    )

    assert len(out.resources) == 3
    for bucket in out.resources:
        assert bucket.resource_type == 'bucket'
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
        assert bucket.resource_type == 'bucket'
        assert 'my-bucket' in bucket.name
        assert len(bucket.attributes) == 1

        region = bucket.attributes[0]
        assert region.name == 'region'
        assert region.value == i


def test_parse_amount_if_value():
    """Test the parsing of an amount."""
    out = __test_file(
        file="""bucket my-bucket: amount: 3 if 1==1 else 2
\tregion: euw
""",
    )

    assert len(out.resources) == 3

    out = __test_file(
        file="""bucket my-bucket: amount: 3 if 1==2 else 2
\tregion: euw
""",
    )

    assert len(out.resources) == 2


def test_parse_if_and_amount_resource():
    """Test the parsing of an amount."""
    out = __test_file(
        file="""bucket my-bucket: if 1==1 amount: 3
\tregion: euw
""",
    )

    assert len(out.resources) == 3

    out = __test_file(
        file="""bucket my-bucket: if 1==2 amount: 3
\tregion: euw
""",
    )

    assert len(out.resources) == 0


def test_var_in_name():
    """Test the parsing of a variable in a name."""
    out = __test_file(
        file="""bucket my-bucket#i: amount: 3 #i
\tregion: #i
""",
    )

    assert len(out.resources) == 3
    for bucket, i in zip(out.resources, range(1, 4)):
        assert bucket.resource_type == 'bucket'
        assert bucket.name == f'my-bucket{i!s}'
        assert len(bucket.attributes) == 1

        region = bucket.attributes[0]
        assert region.name == 'region'
        assert region.value == i

    out = __test_file(
        file="""bucket my-bucket#i#-dev: amount: 3 #i
\tregion: #i
""",
    )

    assert len(out.resources) == 3
    for bucket, i in zip(out.resources, range(1, 4)):
        assert bucket.resource_type == 'bucket'
        assert bucket.name == f'my-bucket{i!s}-dev'
        assert len(bucket.attributes) == 1

        region = bucket.attributes[0]
        assert region.name == 'region'
        assert region.value == i


def test_var_assignation():
    """Test the parsing of a variable in a name."""
    out = __test_file(
        file="""
#region = europe-west1

bucket my-bucket:
  region: #region
""",
    )

    assert len(out.resources) == 1
    bucket = out.resources[0]
    assert bucket.resource_type == 'bucket'
    assert bucket.name == 'my-bucket'
    assert len(bucket.attributes) == 1

    region = bucket.attributes[0]
    assert region.name == 'region'
    assert region.value == 'europe-west1'


def test_comparisons():
    """Test the parsing of operator comparisons."""
    def test_cmp(cmp_expr: str, result: str):
        out = __test_file(
            file=f"""bucket my-bucket:
\tregion: truCase if {cmp_expr} else falsCase
""",
        )

        assert len(out.resources) == 1

        bucket = out.resources[0]
        assert bucket.resource_type == 'bucket'
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
    """Test the parsing of arithmetic expressions."""
    def arithmetic_test(calcul: str, expected: int):
        out = __test_file(
            file=f"""bucket my-bucket:
\tvalue: {calcul}
""",
        )

        assert len(out.resources) == 1

        bucket = out.resources[0]
        assert bucket.resource_type == 'bucket'
        assert bucket.name == 'my-bucket'
        assert len(bucket.attributes) == 1

        region = bucket.attributes[0]
        assert region.name == 'value'
        assert region.value == expected

    # PLUS
    arithmetic_test('-1+1-3', 3)

    # OPERATION ORDER
    arithmetic_test('10/2+3*3', 14)
    arithmetic_test('10/(2+3)*3', 6)

    # POW
    arithmetic_test('(-2)^4', 16)

    # MODULO
    arithmetic_test('25%17', 8)


def __test_parser_raises(
    mocker,  # noqa: ARG001
    input_file: str,
    exception: Exception,
) -> pytest.ExceptionInfo:
    with pytest.raises(exception) as exc_info:
        __test_file(
            file=input_file,
        )

    return exc_info


def __test_syntax_error(
    mocker, input_file: str, ln: int, col: int,
    expected: str, got: str,
):

    exc_info = __test_parser_raises(
        mocker,
        input_file,
        DSLSyntaxError,
    )

    exp = str(' or '.join(list(map(str, expected))))\
        if isinstance(expected, list) else str(expected.value)

    assert str(exc_info.value) == f'(File : \
{Path.cwd()}/test/test_file.thips, Ln {ln!s}, Col {col!s}) :\n\t\
Syntax error : Expected {exp}, got {got.value!s}'


def test_syntax_error_resource(mocker):
    """Test the syntax errors in a resource missing its name."""
    input_file = """bucket :
            """
    __test_syntax_error(
        mocker, input_file=input_file, ln=1, col=8,
        expected=[TT.STRING, TT.VAR], got=TT.COLON,
    )


def test_syntax_error_dict(mocker):
    """Test the syntax errors associated with a dict."""
    # MISSING COLON
    input_file = """
bucket my-bucket:
\tregion euw
            """
    __test_syntax_error(
        mocker, input_file=input_file, ln=3, col=9,
        expected=TT.COLON, got=TT.STRING,
    )

    # MISSING TAB :
    # MEANS THAT NEXT LINE SHOULD BE CONSIDERED AS RESOURCE : ERROR ON COLON
    input_file = """
bucket my-bucket:
region: euw
            """
    __test_syntax_error(
        mocker, input_file=input_file, ln=3, col=7,
        expected=[TT.STRING, TT.VAR], got=TT.COLON,
    )

    # MISSING VALUE
    input_file = """
bucket my-bucket:
\ttest:
\tregion: euw
"""
    __test_syntax_error(
        mocker, input_file=input_file, ln=3, col=7,
        expected=TT.STRING, got=TT.NEWLINE,
    )

    # MISSING VALUE 2
    input_file = """
bucket my-bucket:
\ttest:





"""
    exc_info = __test_parser_raises(
        mocker, input_file=input_file, exception=DSLUnexpectedEOFError,
    )

    assert str(exc_info.value) == 'Unexpected EOF'


def test_syntax_error_amount(mocker):
    """Test the syntax errors in an amount declaration."""
    # MISSING COLON
    input_file = """
bucket my-bucket: amount 3
\tregion: euw
"""
    __test_syntax_error(
        mocker, input_file=input_file, ln=2, col=26,
        expected=TT.COLON, got=TT.INT,
    )

    # NO INTEGER
    input_file = """
bucket my-bucket: amount: str
\tregion: euw
"""
    __test_parser_raises(
        mocker,
        input_file=input_file,
        exception=DSLArithmeticError,
    )


def test_syntax_error_if(mocker):
    """Test the syntax errors in an if statement."""
    # MISSING CONDITION
    input_file = """
bucket my-bucket: if
"""
    __test_parser_raises(
        mocker,
        input_file=input_file,
        exception=DSLConditionError,
    )

    # UNEXPECTED IF ELSE
    input_file = """
bucket my-bucket: if 1 == 1 else bbb
"""
    __test_syntax_error(
        mocker, input_file=input_file, ln=2, col=29,
        expected=TT.NEWLINE, got=TT.ELSE,
    )


def test_syntax_error_if_else(mocker):
    """Test the syntax errors in an if else statement."""
    # MISSING ELSE VALUE
    input_file = """
bucket my-bucket:
\ttoto:
\t\tfoo : bar if true else
"""
    __test_syntax_error(
        mocker, input_file=input_file, ln=4, col=25,
        expected=[TT.INT, TT.FLOAT, TT.PARENTHESES_START], got=TT.NEWLINE,
    )

    # MISSING CONDITION VALUE
    input_file = """
bucket my-bucket:
\ttoto:
\t\tfoo : bar if  else bbb
"""
    __test_parser_raises(
        mocker,
        input_file=input_file,
        exception=DSLConditionError,
    )


def test_syntax_error_unexpected_token(mocker):
    """Test the syntax error with an unexpected 'if' as token name."""
    # RESERVED TOKEN NAME
    input_file = """
bucket if:
\tregion: euw
"""
    __test_syntax_error(
        mocker, input_file=input_file, ln=2, col=8,
        expected=[TT.STRING, TT.VAR], got=TT.IF,
    )


def test_amount_error(mocker):
    """Test the syntax error with an unexpected 'amount' value : 3/2 isn't an int."""
    # RESERVED TOKEN NAME
    input_file = """
bucket my-bucket: amount: 3/2
\tregion: euw
"""
    __test_parser_raises(
        mocker,
        input_file=input_file,
        exception=DSLArithmeticError,
    )
