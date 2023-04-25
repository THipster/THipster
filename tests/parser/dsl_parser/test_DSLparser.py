from parser.dsl_parser.AST import FileNode
from parser.dsl_parser.DSLParser import DSLParser
from parser.dsl_parser.DSLParser import DSLParserPathNotFound
import os
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


def test_parse_simple_file():
    path_input = 'test'
    _destroy_dir = create_dir(
        path_input,
        {
            'test_file.thips':
            """bucket my-bucket:
\tregion: euw
""",
        },
    )

    parser = DSLParser()
    try:
        output = parser.run(path_input)

        assert type(output) == FileNode

        assert str(output) == """<RESOURCE \
type = <STRING (STRING bucket)>, \
name = <STRING (STRING my-bucket)>, \
parameters = <DICT <PARAMETER name = <STRING (STRING region)>, \
value = <LITERAL <STRING (STRING euw)>>>>>"""
    except Exception as e:
        print(e)
        pytest.fail()
    finally:
        _destroy_dir()


def test_parse_simple_file_with_newlines():
    path_input = 'test'
    _destroy_dir = create_dir(
        path_input,
        {
            'test_file.thips':
            """

bucket my-bucket:


\tregion: euw

bucket my-bucket2:
\tregion: euw



""",
        },
    )

    parser = DSLParser()
    try:
        output = parser.run(path_input)

        assert type(output) == FileNode

        assert str(output) == '<RESOURCE \
type = <STRING (STRING bucket)>, \
name = <STRING (STRING my-bucket)>, \
parameters = <DICT <PARAMETER name = <STRING (STRING region)>, \
value = <LITERAL <STRING (STRING euw)>>>>>\n\
<RESOURCE \
type = <STRING (STRING bucket)>, \
name = <STRING (STRING my-bucket2)>, \
parameters = <DICT <PARAMETER name = <STRING (STRING region)>, \
value = <LITERAL <STRING (STRING euw)>>>>>'
    except Exception as e:
        print(e)
        pytest.fail()
    finally:
        _destroy_dir()


def test_parse_longer_file():
    path_input = 'test'
    _destroy_dir = create_dir(
        path_input,
        {
            'test_file.thips':
            """bucket my-bucket:
\ttoto:
\t\t aaa: val1
\t\t bbb: val2
\ttata:
\t\t- ccc
\t\t- ddd
""",
        },
    )

    parser = DSLParser()
    try:
        output = parser.run(path_input)

        assert type(output) == FileNode

        assert str(output) == """<RESOURCE \
type = <STRING (STRING bucket)>, \
name = <STRING (STRING my-bucket)>, \
parameters = <DICT <PARAMETER name = <STRING (STRING toto)>, \
value = <DICT \
<PARAMETER name = <STRING (STRING aaa)>, value = <LITERAL <STRING (STRING val1)>>> \
<PARAMETER name = <STRING (STRING bbb)>, value = <LITERAL <STRING (STRING val2)>>>>> \
<PARAMETER name = <STRING (STRING tata)>, \
value = <LIST \
<LITERAL <STRING (STRING ccc)>> \
<LITERAL <STRING (STRING ddd)>>>>>>"""
    except Exception as e:
        print(e)
        pytest.fail()
    finally:
        _destroy_dir()
