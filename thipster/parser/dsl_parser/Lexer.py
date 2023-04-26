from parser.dsl_parser.Token import Token, TOKENTYPES as TT
from engine.ParsedFile import Position
from enum import Enum


class CHARS(str, Enum):
    AMOUNT = 'amount'
    COLUMN = ':'
    DASH = '-'
    DOUBLEQUOTES = '"'
    ELIF = 'elif'
    ELSE = 'else'
    HASH = '#'
    IF = 'if'
    NEWLINE = '\n'
    TAB = '\t'
    TRUE = 'true'
    FALSE = 'false'
    WHITESPACE = ' '


class Lexer():
    def __init__(self, files: dict[str, str]):
        self.__files = files
        self.__tokenList = []
        self.__currentFile = ''
        self.__currentLine = 1
        self.__currentColumn = 1
        self.__currentToken = ''
        self.__currentTokenIndex = 1
        self.__variable = False
        self.__inQuotedString = False
        self.__consecutiveWhitespaces = 0

    @property
    def files(self):
        return self.__files

    @property
    def tokenList(self):
        return self.__tokenList

    def run(self) -> list[Token]:
        for fileName in self.files:
            self.lex(self.files.get(fileName), fileName, 1, 1)
        return self.__tokenList

    def lex(
        self,
        codeString: str,
        fileName: str,
        startLine: int = 1,
        startColumn: int = 1,
    ) -> None:
        self.__currentFile = fileName
        self.__currentLine = startLine
        self.__currentColumn = startColumn
        self.__currentToken = ''
        self.__currentTokenIndex = 1
        for char in codeString:
            if not self.__inQuotedString:
                if char == CHARS.WHITESPACE.value:
                    self.__consecutiveWhitespaces += 1
                else:
                    self.__consecutiveWhitespaces = 0

                if char == CHARS.WHITESPACE.value:
                    self.__handleWhitespace()

                elif char == CHARS.NEWLINE.value:
                    self.__handleNewline()

                elif char == CHARS.TAB.value:
                    self.__handleTab()

                elif char == CHARS.COLUMN.value:
                    self.__handleColumn()

                elif char == CHARS.HASH.value:
                    self.__handleHash()

                elif char == CHARS.DOUBLEQUOTES.value:
                    self.__handleDoubleQuotes()

                else:
                    self.__currentToken += char

            else:
                if char == CHARS.DOUBLEQUOTES.value:
                    self.__handleDoubleQuotes()

                elif char == CHARS.NEWLINE.value:
                    position = str(
                        Position(
                            self.__currentFile,
                            self.__currentLine, self.__currentColumn,
                        ),
                    )
                    error = "Invalid syntax, missing ending quotes at '%s'" % position
                    raise SyntaxError(error)

                else:
                    self.__currentToken += char

            self.__currentColumn += 1

        self.__addFileEnd()

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

        elif currentTokenLower == CHARS.TRUE.value:
            self.addTokenToList(
                currentTokenIndex,
                TT.BOOLEAN.value, currentTokenLower,
            )

        elif currentTokenLower == CHARS.FALSE.value:
            self.addTokenToList(
                currentTokenIndex,
                TT.BOOLEAN.value, currentTokenLower,
            )

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
            elif self.__isfloat(currentToken):
                self.addTokenToList(
                    currentTokenIndex,
                    TT.FLOAT.value, currentToken,
                )
            else:
                self.addTokenToList(
                    currentTokenIndex,
                    TT.STRING.value, currentToken,
                )

    def __handleWhitespace(self) -> None:
        self.handleCurrentToken(self.__currentToken, self.__currentTokenIndex)
        self.__resetCurrentToken()
        if self.__consecutiveWhitespaces == 4:
            self.__currentColumn -= 3
            self.__currentTokenIndex = self.__currentColumn+1
            self.addTokenToList(self.__currentColumn, TT.TAB.value)
            self.__consecutiveWhitespaces = 0

    def __handleNewline(self) -> None:
        self.handleCurrentToken(self.__currentToken, self.__currentTokenIndex)
        self.addTokenToList(self.__currentColumn, TT.NEWLINE.value)
        self.__resetCurrentToken(newIndex=1)
        self.__currentLine += 1
        self.__currentColumn = 0

    def __handleTab(self) -> None:
        self.handleCurrentToken(self.__currentToken, self.__currentTokenIndex)
        self.addTokenToList(self.__currentColumn, TT.TAB.value)
        self.__resetCurrentToken()

    def __handleColumn(self) -> None:
        self.handleCurrentToken(self.__currentToken, self.__currentTokenIndex)
        self.addTokenToList(self.__currentColumn, TT.COLUMN.value)
        self.__resetCurrentToken()

    def __handleHash(self) -> None:
        self.handleCurrentToken(self.__currentToken, self.__currentTokenIndex)
        self.__variable = True
        self.__resetCurrentToken()

    def __handleDoubleQuotes(self) -> None:
        if self.__inQuotedString:
            self.addTokenToList(
                self.__currentTokenIndex,
                TT.STRING.value, self.__currentToken,
            )
            self.__inQuotedString = False
        else:
            self.handleCurrentToken(
                self.__currentToken, self.__currentTokenIndex,
            )
            self.__inQuotedString = True
        self.__resetCurrentToken()

    def addTokenToList(self, column: int, tokenType: str, value: str = None) -> None:
        self.__tokenList.append(
            Token(
                position=Position(
                    self.__currentFile,
                    self.__currentLine, column,
                ),
                tokenType=tokenType,
                value=value,
            ),
        )

    def __addFileEnd(self) -> None:
        if len(self.__currentToken.strip()) > 0:
            self.handleCurrentToken(
                self.__currentToken, self.__currentTokenIndex,
            )
            self.__currentToken = ''
        self.__handleNewline()
        self.addTokenToList(self.__currentColumn+1, TT.EOF.value)

    def __resetCurrentToken(self, newIndex: int = None) -> None:
        self.__currentToken = ''
        if newIndex:
            self.__currentTokenIndex = newIndex
        else:
            self.__currentTokenIndex = self.__currentColumn+1

    def __isfloat(self, num):
        try:
            float(num)
            return True
        except ValueError:
            return False
