import os

from thipster.engine.parsed_file import ParsedFile
from thipster.parser import ParserFactory


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
    assert bucket.type == 'bucket'
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
    assert bucket.type == 'bucket'
    assert bucket.name == 'my-bucket'
    assert len(bucket.attributes) == 1

    region = bucket.attributes[0]
    assert region.name == 'region'
    assert region.value == 'euw'


def test_thips_file():
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
    assert bucket.type == 'bucket'
    assert bucket.name == 'my-bucket'
    assert len(bucket.attributes) == 1

    region = bucket.attributes[0]
    assert region.name == 'region'
    assert region.value == 'euw'


def test_two_types_of_file():
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
        assert bucket.type == 'bucket'
        assert 'my-bucket' in bucket.name
        assert len(bucket.attributes) == 1

        region = bucket.attributes[0]
        assert region.name == 'region'
        assert region.value == 'euw'
