from parser.dsl_parser.Token import Token, TOKENTYPES as TT
from engine.ParsedFile import Position
from enum import Enum


class CHARS(str, Enum):
    AMOUNT = 'amount'
    WHITESPACE = ' '
    DASH = '-'
    DOUBLEQUOTES = '"'
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
        quotedString = False
        for char in codeString:
            if not quotedString:
                if char == CHARS.WHITESPACE.value:
                    self.handleCurrentToken(currentToken, currentTokenIndex)
                    currentToken = ''
                    currentTokenIndex = column+1
                elif char == CHARS.NEWLINE.value:
                    self.handleCurrentToken(currentToken, currentTokenIndex)
                    self.addTokenToList(column, TT.NEWLINE.value)
                    currentToken = ''
                    currentTokenIndex = 1
                    self.__currentLine += 1
                    column = 0
                elif char == CHARS.TAB.value:
                    self.handleCurrentToken(currentToken, currentTokenIndex)
                    self.addTokenToList(column, TT.TAB.value)
                    currentToken = ''
                    currentTokenIndex = column+1
                elif char == CHARS.COLUMN.value:
                    self.handleCurrentToken(currentToken, currentTokenIndex)
                    self.addTokenToList(column, TT.COLUMN.value)
                    currentToken = ''
                    currentTokenIndex = column+1
                elif char == CHARS.HASH.value:
                    self.handleCurrentToken(currentToken, currentTokenIndex)
                    self.__variable = True
                    currentToken = ''
                    currentTokenIndex = column+1
                elif char == CHARS.DOUBLEQUOTES.value:
                    self.handleCurrentToken(currentToken, currentTokenIndex)
                    quotedString = True
                    currentToken = ''
                    currentTokenIndex = column+1
                else:
                    currentToken += char
            else:
                if char == CHARS.DOUBLEQUOTES.value:
                    self.addTokenToList(
                        currentTokenIndex,
                        TT.STRING.value, currentToken,
                    )
                    quotedString = False
                    currentToken = ''
                    currentTokenIndex = column+1
                elif char == CHARS.NEWLINE.value:
                    position = str(
                        Position(
                            self.__currentFile,
                            self.__currentLine, column,
                        ),
                    )
                    error = "Invalid syntax, missing ending quotes at '%s'" % position
                    raise SyntaxError(error)
                else:
                    currentToken += char
            column += 1
        if len(currentToken.strip()) > 0:
            self.handleCurrentToken(currentToken, currentTokenIndex)
        self.addTokenToList(column, TT.EOF.value)

    def handleCurrentToken(self, currentToken: str, currentTokenIndex: int) -> None:
        currentTokenLower = currentToken.lower()
        if currentToken == CHARS.DASH.value:
            self.addTokenToList(currentTokenIndex, TT.DASH.value)
        elif currentTokenLower == CHARS.IF.value:
            self.addTokenToList(currentTokenIndex, TT.IF.value)
        elif currentTokenLower == CHARS.ELSE.value:
            self.addTokenToList(currentTokenIndex, TT.ELSE.value)
        elif currentTokenLower == CHARS.ELIF.value:
            self.addTokenToList(currentTokenIndex, TT.ELIF.value)
        elif currentTokenLower == CHARS.AMOUNT.value:
            self.addTokenToList(currentTokenIndex, TT.AMOUNT.value)
        elif len(currentToken.strip()) > 0:
            if self.__variable:
                self.addTokenToList(
                    currentTokenIndex,
                    TT.VAR.value, currentToken,
                )
                self.__variable = False
            elif currentToken.isdigit():
                self.addTokenToList(
                    currentTokenIndex,
                    TT.INT.value, currentToken,
                )
            elif self._isfloat(currentToken):
                self.addTokenToList(
                    currentTokenIndex,
                    TT.FLOAT.value, currentToken,
                )
            else:
                self.addTokenToList(
                    currentTokenIndex,
                    TT.STRING.value, currentToken,
                )

    def addTokenToList(self, column: int, tokenType: str, value: str = None) -> None:
        self.tokenList.append(
            Token(
                position=Position(
                    self.__currentFile,
                    self.__currentLine, column,
                ),
                tokenType=tokenType,
                value=value,
            ),
        )

    def _isfloat(self, num):
        try:
            float(num)
            return True
        except ValueError:
            return False
