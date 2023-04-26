from parser.dsl_parser.AST import FileNode
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


def __test_file(file: str, expected: str):
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

        assert type(output) == FileNode

        assert str(output) == expected
    except Exception as e:
        raise e
    finally:
        _destroy_dir()


def test_parse_simple_file():
    __test_file(
        file="""bucket my-bucket:
\tregion: euw
""",
        expected="""<RESOURCE \
type = <STRING (STRING bucket)>, \
name = <STRING (STRING my-bucket)>, \
parameters = <DICT <PARAMETER name = <STRING (STRING region)>, \
value = <LITERAL <STRING (STRING euw)>>>>>""",

    )


def test_parse_simple_file_with_newlines():
    __test_file(
        file="""

bucket my-bucket:


\tregion: euw

bucket my-bucket2:
\tregion: euw



""",
        expected='<RESOURCE \
type = <STRING (STRING bucket)>, \
name = <STRING (STRING my-bucket)>, \
parameters = <DICT <PARAMETER name = <STRING (STRING region)>, \
value = <LITERAL <STRING (STRING euw)>>>>>\n\
<RESOURCE \
type = <STRING (STRING bucket)>, \
name = <STRING (STRING my-bucket2)>, \
parameters = <DICT <PARAMETER name = <STRING (STRING region)>, \
value = <LITERAL <STRING (STRING euw)>>>>>',
    )


def test_parse_dict_list_in_dict():
    __test_file(
        file="""bucket my-bucket:
\ttoto:
\t\t aaa: val1
\t\t bbb: val2
\ttata:
\t\t- ccc
\t\t- ddd
""",
        expected="""<RESOURCE \
type = <STRING (STRING bucket)>, \
name = <STRING (STRING my-bucket)>, \
parameters = <DICT <PARAMETER name = <STRING (STRING toto)>, \
value = <DICT \
<PARAMETER name = <STRING (STRING aaa)>, value = <LITERAL <STRING (STRING val1)>>> \
<PARAMETER name = <STRING (STRING bbb)>, value = <LITERAL <STRING (STRING val2)>>>>> \
<PARAMETER name = <STRING (STRING tata)>, \
value = <LIST \
<LITERAL <STRING (STRING ccc)>> \
<LITERAL <STRING (STRING ddd)>>>>>>""",
    )


def test_parse_if_else():
    # IN DICT
    __test_file(
        file="""bucket my-bucket:
\tregion: euw if aaa else na
""", expected="""<RESOURCE \
type = <STRING (STRING bucket)>, \
name = <STRING (STRING my-bucket)>, \
parameters = <DICT <PARAMETER name = <STRING (STRING region)>, \
value = <IF_E <STRING (STRING aaa)>: <LITERAL <STRING (STRING euw)>>, \
ELSE : <LITERAL <STRING (STRING na)>>>>>>\
""",
    )
    # IN LIST
    __test_file(
        file="""bucket my-bucket:
\tregion:
\t\t- euw if aaa else na
""", expected="""<RESOURCE \
type = <STRING (STRING bucket)>, \
name = <STRING (STRING my-bucket)>, \
parameters = <DICT <PARAMETER name = <STRING (STRING region)>, \
value = <LIST <IF_E <STRING (STRING aaa)>: <LITERAL <STRING (STRING euw)>>, \
ELSE : <LITERAL <STRING (STRING na)>>>>>>>\
""",
    )


def test_parse_amount():
    __test_file(
        file="""bucket my-bucket: amount: 3
\tregion: euw
""", expected="""<AMOUNT <INT (INT 3)> #None: \
<RESOURCE \
type = <STRING (STRING bucket)>, \
name = <STRING (STRING my-bucket)>, \
parameters = <DICT <PARAMETER name = <STRING (STRING region)>, \
value = <LITERAL <STRING (STRING euw)>>>>>>\
""",
    )


def __test_parser_raises(mocker, input: str, exception: Exception)\
        -> pytest.ExceptionInfo:
    with pytest.raises(exception) as exc_info:
        __test_file(
            file=input, expected="""""",
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
