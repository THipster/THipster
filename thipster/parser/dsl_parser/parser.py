"""Module that contains the THipster DSL Parser."""
import os
from pathlib import Path

from thipster.engine import ParserPort
from thipster.engine.parsed_file import ParsedFile

from .exceptions import DSLParserBaseError, DSLParserPathNotFoundError
from .interpreter import Interpreter
from .lexer import Lexer
from .token_parser import TokenParser


class DSLParser(ParserPort):
    """Parser for the THipster's DSL."""

    @classmethod
    def __getfiles(cls, path: str) -> dict[str, str]:
        """Recursively get all files in the requested directory and its sudirectories.

        Can be run on a path file aswell.

        Parameters
        ----------
        path: str
            Path to run this function onto

        Returns
        -------
        dict[str, str]
            A dictionary that links a filename to its content, fileName : fileContent
        """
        path = Path(path).resolve().as_posix()

        if not Path(path).exists():
            raise DSLParserPathNotFoundError(path)

        files = {}

        if Path(path).is_dir():
            for content in os.listdir(path):
                files.update(DSLParser.__getfiles(f'{path}/{content}'))

        if Path(path).is_file():
            with Path(path).open() as f:
                files.update({path: f.read()})

                f.close()

        return files

    @classmethod
    def run(cls, path: str) -> ParsedFile:
        """Run the DSLParser.

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
