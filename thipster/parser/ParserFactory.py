import os
from thipster.engine.I_Parser import I_Parser
from thipster.engine.ParsedFile import ParsedFile
from thipster.parser.YAMLParser import YAMLParser
from thipster.parser.dsl_parser.DSLParser import DSLParser


class ParserPathNotFound(Exception):
    def __init__(self, path, *args: object) -> None:
        super().__init__(*args)

        self.__message = f'Path not found : {path}'

    @property
    def message(self):
        return self.__message


class ParserFactory(I_Parser):

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

    def __yamlParser(self) -> YAMLParser:
        return YAMLParser

    def __dslParser(self) -> DSLParser:
        return DSLParser

    def __noParser(self):
        raise Exception()

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
        __parsers = {
            '.yaml': self.__yamlParser,
            '.yml': self.__yamlParser,
            '.jinja': self.__yamlParser,
            '.thips': self.__dslParser,
        }

        _, pathExtension = os.path.splitext(path)

        return __parsers.get(pathExtension, self.__noParser)()
