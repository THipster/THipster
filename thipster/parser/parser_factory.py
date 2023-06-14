import os

from thipster.engine import I_Parser, THipsterException
from thipster.engine.parsed_file import ParsedFile

from .dsl_parser import DSLParser
from .yaml_parser import YAMLParser


def _noParser(pathExtension):
    class noParser():
        def run(path):
            raise Exception(f'{pathExtension} files can\'t be parsed')

    return noParser


class ParserPathNotFound(THipsterException):
    def __init__(cls, path, *args: object) -> None:
        super().__init__(*args)

        cls.__path = path

    @property
    def message(cls) -> str:
        return f'Path not found : {cls.__path}'


class ParserFactory(I_Parser):

    __parsers = {
        '.yaml': YAMLParser,
        '.yml': YAMLParser,
        '.jinja': YAMLParser,
        '.thips': DSLParser,
    }

    @classmethod
    def addParser(cls, parser: I_Parser, extensions: list[str]):
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
            raise ParserPathNotFound(path)

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
            parsedFile = cls.__getParser(file).run(file)
            res.resources += parsedFile.resources

        return res

    @classmethod
    def __getParser(cls, path) -> I_Parser:

        _, pathExtension = os.path.splitext(path)

        return cls.__parsers.get(
            pathExtension, _noParser(pathExtension),
        )
