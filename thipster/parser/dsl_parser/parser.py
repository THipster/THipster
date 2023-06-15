import os

from thipster.engine import ParserPort
from thipster.engine.parsed_file import ParsedFile

from .exceptions import DSLParserBaseError, DSLParserPathNotFoundError
from .interpreter import Interpreter
from .lexer import Lexer
from .token_parser import TokenParser


class DSLParser(ParserPort):

    @classmethod
    def __getfiles(cls, path: str) -> dict[str, str]:
        """Recursively get all files in the requested directory and its sudirectories
        Can be run on a path file aswell

        Parameters
        ----------
        path: str
            Path to run this function into

        Returns
        -------
        dict[str, str]
            A dictionary that links a filename to its content, fileName : fileContent
        """

        path = os.path.abspath(path)

        if not os.path.exists(path):
            raise DSLParserPathNotFoundError(path)

        files = {}

        if os.path.isdir(path):
            for content in os.listdir(path):
                files.update(DSLParser.__getfiles(f'{path}/{content}'))

        if os.path.isfile(path):
            with open(path) as f:
                files.update({path: f.read()})

                f.close()

        return files

    @classmethod
    def run(cls, path: str) -> ParsedFile:
        """Run the DSLParser

        Parameters
        ----------
        path: str
            Path to run the parser into

        Returns
        -------
        ParsedFile
            A ParsedFile object with the content of all the files in the input path
        """

        try:
            files = DSLParser.__getfiles(path)
            lexer = Lexer(files)
            token_list = lexer.run()
            parser = TokenParser(token_list)
            ast = parser.run()

            interpreter = Interpreter()
            parsed_file = interpreter.run(ast)

            return parsed_file
        except DSLParserBaseError as e:
            raise e
        except Exception as e:
            raise e
