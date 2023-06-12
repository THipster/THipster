import os

from thipster.engine import I_Parser
from thipster.engine.parsed_file import ParsedFile
from .dsl_parser import DSLParser
from .yaml_parser import YAMLParser


class ParserPathNotFound(Exception):
    def __init__(self, path, *args: object) -> None:
        super().__init__(*args)

        self.__message = f'Path not found : {path}'

    @property
    def message(self):
        return self.__message


class ParserFactory(I_Parser):

    __parsers = {
        '.yaml': YAMLParser,
        '.yml': YAMLParser,
        '.jinja': YAMLParser,
        '.thips': DSLParser,
    }

    def addParser(parser: I_Parser, extensions: list[str]):
        ParserFactory.__parsers.update({e: parser for e in extensions})

    def __getfiles(self, path: str) -> list[str]:
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
                files += self.__getfiles(f'{path}/{content}')

        if os.path.isfile(path):
            return [path]

        return files

    def __noParser(self, pathExtension):
        class noParser():
            def run(path):
                raise Exception(f'{pathExtension} files can\'t be parsed')

        return noParser

    def run(self, path: str) -> ParsedFile:
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
        files = self.__getfiles(path)

        res = ParsedFile()
        for file in files:
            parsedFile = self.__getParser(file).run(file)
            res.resources += parsedFile.resources

        return res

    def __getParser(self, path) -> I_Parser:

        _, pathExtension = os.path.splitext(path)

        return ParserFactory.__parsers.get(
            pathExtension, self.__noParser(pathExtension),
        )
