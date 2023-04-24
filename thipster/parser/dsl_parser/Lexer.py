from parser.dsl_parser.Token import Token
from engine.ParsedFile import Position

from enum import Enum


class TOKENS(str, Enum):
    WHITESPACE = ' '
    DASH = '-'
    TAB = '\t'
    NEWLINE = '\n'
    COLUMN = ':'
    HASH = '#'
    IF = 'if'
    ELSE = 'else'
    ELIF = 'elif'


class Lexer():
    def __init__(self, files: dict[str, str]):
        self.__files = files
        self.tokenList = []
        self.__currentFile = ''
        self.__currentLine = 1
        self.__variable = False

    @property
    def files(self):
        return self.__files

    def run(self) -> list[Token]:
        for fileName in self.files:
            self.lex(self.files.get(fileName), fileName, 1, 1)
        return self.tokenList

    def lex(
        self,
        codeString: str,
        fileName: str,
        startLine: int = 1,
        startColumn: int = 1,
    ) -> None:
        self.__currentFile = fileName
        self.__currentLine = startLine
        column = startColumn
        currentToken = ''
        currentTokenIndex = 1
        for char in codeString:
            if char == TOKENS.WHITESPACE.value:
                self.handleCurrentToken(currentToken, currentTokenIndex)
                currentToken = ''
                currentTokenIndex = column+1
            elif char == TOKENS.NEWLINE.value:
                self.handleCurrentToken(currentToken, currentTokenIndex)
                self.addTokenToList(column, 'NEWLINE')
                currentToken = ''
                currentTokenIndex = 1
                self.__currentLine += 1
                column = 0
            elif char == TOKENS.TAB.value:
                self.handleCurrentToken(currentToken, currentTokenIndex)
                self.addTokenToList(column, 'TAB')
                currentToken = ''
                currentTokenIndex = column+1
            elif char == TOKENS.COLUMN.value:
                self.handleCurrentToken(currentToken, currentTokenIndex)
                self.addTokenToList(column, 'COLUMN')
                currentToken = ''
                currentTokenIndex = column+1
            elif char == TOKENS.HASH.value:
                self.handleCurrentToken(currentToken, currentTokenIndex)
                self.__variable = True
                currentToken = ''
                currentTokenIndex = column+1
            else:
                currentToken += char
            column += 1
        if len(currentToken.strip()) > 0:
            self.handleCurrentToken(currentToken, currentTokenIndex)
        self.addTokenToList(column, 'EOF')

    def handleCurrentToken(self, currentToken: str, currentTokenIndex: int) -> None:
        if currentToken == TOKENS.DASH.value:
            self.addTokenToList(currentTokenIndex, 'DASH')
        elif currentToken == TOKENS.IF.value:
            self.addTokenToList(currentTokenIndex, 'IF')
        elif currentToken == TOKENS.ELSE.value:
            self.addTokenToList(currentTokenIndex, 'ELSE')
        elif currentToken == TOKENS.ELIF.value:
            self.addTokenToList(currentTokenIndex, 'ELIF')
        elif len(currentToken.strip()) > 0:
            if self.__variable:
                self.addTokenToList(
                    currentTokenIndex,
                    'VAR', currentToken,
                )
                self.__variable = False
            elif currentToken.isdigit():
                self.addTokenToList(
                    currentTokenIndex,
                    'INT', currentToken,
                )
            elif self._isfloat(currentToken):
                self.addTokenToList(
                    currentTokenIndex,
                    'FLOAT', currentToken,
                )
            else:
                self.addTokenToList(
                    currentTokenIndex,
                    'STRING', currentToken,
                )

    def addTokenToList(self, column: int, type: str, value: str = None) -> None:
        self.tokenList.append(
            Token(
                position=Position(
                    self.__currentFile,
                    self.__currentLine, column,
                ),
                type=type,
                value=value,
            ),
        )

    def _isfloat(self, num):
        try:
            float(num)
            return True
        except ValueError:
            return False
