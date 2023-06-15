import os

from thipster.engine import ParserPort, THipsterError
from thipster.engine.parsed_file import ParsedFile

from .dsl_parser import DSLParser
from .yaml_parser import YAMLParser


def _no_parser(path_extension):
    class NoParser(ParserPort):
        @classmethod
        def run(cls, path):
            raise Exception(f'{path_extension} files can\'t be parsed')

    return NoParser


class ParserPathNotFoundError(THipsterError):
    def __init__(self, path, *args: object) -> None:
        super().__init__(*args)

        self.__path = path

    @property
    def message(self) -> str:
        return f'Path not found : {self.__path}'


class ParserFactory(ParserPort):

    __parsers = {
        '.yaml': YAMLParser,
        '.yml': YAMLParser,
        '.jinja': YAMLParser,
        '.thips': DSLParser,
    }

    @classmethod
    def add_parser(cls, parser: ParserPort, extensions: list[str]):
        cls.__parsers.update({e: parser for e in extensions})

    @classmethod
    def __getfiles(cls, path: str) -> list[str]:
        """Recursively get all files names in the requested directory and its\
              sudirectories
        Can be run on a path file aswell

        Parameters
        ----------
        path: str
            Path to run this function into

        Returns
        -------
        list[str]
            A list of all the filenames
        """

        path = os.path.abspath(path)

        if not os.path.exists(path):
            raise ParserPathNotFoundError(path)

        files = []

        if os.path.isdir(path):
            for content in os.listdir(path):
                files += cls.__getfiles(f'{path}/{content}')

        if os.path.isfile(path):
            return [path]

        return files

    @classmethod
    def run(cls, path: str) -> ParsedFile:
        """Run the ParserFactory

        Parameters
        ----------
        path: str
            Path to run the parser into

        Returns
        -------
        ParsedFile
            A ParsedFile object with the content of all the files in the input path
        """
        files = cls.__getfiles(path)

        res = ParsedFile()
        for file in files:
            parsed_file = cls.__get_parser(file).run(file)
            res.resources += parsed_file.resources

        return res

    @classmethod
    def __get_parser(cls, path) -> ParserPort:

        _, path_extension = os.path.splitext(path)

        return cls.__parsers.get(
            path_extension, _no_parser(path_extension),
        )
