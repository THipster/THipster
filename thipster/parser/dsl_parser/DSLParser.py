from thipster.engine.I_Parser import I_Parser
from thipster.engine.ParsedFile import ParsedFile

import os
from thipster.parser.dsl_parser.Interpreter import Interpreter
from thipster.parser.dsl_parser.Lexer import Lexer
from thipster.parser.dsl_parser.TokenParser import TokenParser

from thipster.parser.dsl_parser.DSLExceptions import DSLParserPathNotFound, \
    DSLParserBaseException


class DSLParser(I_Parser):

    def __getfiles(path: str) -> dict[str, str]:
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
            raise DSLParserPathNotFound(path)

        files = {}

        if os.path.isdir(path):
            for content in os.listdir(path):
                files.update(DSLParser.__getfiles(f'{path}/{content}'))

        if os.path.isfile(path):
            with open(path, 'r') as f:
                files.update({path: f.read()})

                f.close()

        return files

    def run(path: str) -> ParsedFile:
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
            parsedFile = interpreter.run(ast)

            return parsedFile
        except DSLParserBaseException as e:
            raise e
        except Exception as e:
            raise e
