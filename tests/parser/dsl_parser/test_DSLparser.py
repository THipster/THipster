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


def test_tokenize_file():
    path_input = 'test'
    _destroy_dir = create_dir(
        path_input,
        {
            'test_file.thips':
            """bucket my-bucket:
\tregion: euw""",
        },
    )

    parser = DSLParser()

    tokens = parser.run(path_input)

    assert len(tokens) == 9

    _destroy_dir()


def test_tokenize_longer_file():
    path_input = 'test'
    _destroy_dir = create_dir(
        path_input,
        {
            'test_file.thips':
            """bucket my-bucket:
\t toto: if #a=b
\t\t aaa: val1
\t\t bbb: val2
\t tata:
\t- ccc: val3
\t- ddd: val4
""",
        },
    )

    parser = DSLParser()

    tokens = parser.run(path_input)

    assert len(tokens) == 39

    _destroy_dir()
