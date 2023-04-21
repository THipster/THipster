from engine.I_Parser import I_Parser
from engine.ParsedFile import ParsedFile

import os
from parser.dsl_parser.Lexer import Lexer


class DSLParserBaseException(Exception):
    def __init__(self, message, *args: object) -> None:
        super().__init__(*args)

        self.__message = message

    @property
    def message(self):
        return self.__message


class DSLParserPathNotFound(DSLParserBaseException):
    def __init__(self, file, *args: object) -> None:
        super().__init__(f'Path not found : {file}', *args)


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

    def run(self, path: str) -> ParsedFile:

        try:
            files = self.__getfiles(path)
            print(files)
            lexer = Lexer(files)
            token_list = lexer.run()

            return token_list
        except DSLParserBaseException as e:
            print(e.message)
            pass
        except Exception:
            pass
