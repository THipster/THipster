from engine.I_Parser import I_Parser
from engine.ParsedFile import ParsedFile

import os
from helpers import logger
from parser.dsl_parser.Interpreter import Interpreter
from parser.dsl_parser.Lexer import Lexer
from parser.dsl_parser.TokenParser import TokenParser

from parser.dsl_parser.DSLExceptions import DSLParserPathNotFound, \
    DSLParserBaseException


class DSLParser(I_Parser):

    def __getfiles(self, path: str) -> dict[str, str]:

        path = os.path.abspath(path)

        if not os.path.exists(path):
            raise DSLParserPathNotFound(path)

        files = {}

        if os.path.isdir(path):
            for content in os.listdir(path):
                files.update(self.__getfiles(f'{path}/{content}'))

        if os.path.isfile(path):
            with open(path, 'r') as f:
                files.update({path: f.read()})

                f.close()

        return files

    @logger('- Parser')
    def run(self, path: str) -> ParsedFile:

        try:
            files = self.__getfiles(path)
            lexer = Lexer(files)
            token_list = lexer.run()
            parser = TokenParser(token_list)
            ast = parser.run()

            interpreter = Interpreter()
            parsedFiles = interpreter.run(ast)

            return parsedFiles
        except DSLParserBaseException as e:
            print(e.message)
            raise e
        except Exception as e:
            raise e
