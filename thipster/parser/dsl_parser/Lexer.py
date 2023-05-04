from parser.dsl_parser.Token import Token, TOKENTYPES as TT
from engine.ParsedFile import Position
from helpers import createLogger
from parser.dsl_parser.DSLExceptions import DSLParserBaseException


class DSLParserNoEndingQuotes(DSLParserBaseException):
    def __init__(self, position, *args: object) -> None:
        super().__init__(
            f'Invalid syntax, missing ending quotes at : {position}', *args,
        )


class Lexer():
    """Lexer class for the DSL Parser
    """

    def __init__(self, files: dict[str, str]):
        """
        Parameters
        ----------
        files : dict[str, str]
            Dictionnary of files to tokenize, fileName : fileContent
        """
        self.__logger = createLogger(__name__)
        self.__files = files
        self.__tokenList = []
        self.__lexerPosition = LexerPosition('')
        self.__currentChar = ''

    @property
    def files(self):
        return self.__files

    @property
    def tokenList(self):
        return self.__tokenList

    def run(self) -> list[Token]:
        """Function to launch the Lexer

        Returns
        -------
        list[Token]
            List of Tokens representing the input files
        """
        self.__logger.info('Start Lexer')
        for fileName in self.files:
            self.lex(self.files.get(fileName), fileName, 1, 1)

        self.__logger.info(
            'Shuting down Lexer, processed %d file(s) and generated %d tokens',
            len(self.__files),
            len(self.__tokenList),
        )
        return self.__tokenList

    def lex(
        self,
        codeString: str,
        fileName: str,
        startLine: int = 1,
        startColumn: int = 1,
    ) -> None:
        """Function to tokenize a file contents

        Parameters
        ----------
        codeString : str
            Content of the file
        fileName : str
            Name of the file
        startLine : int, optional
            Starting line of the content in the file, by default 1
        startColumn : int, optional
            Starting column of the content in the file, by default 1

        Raises
        ------
        DSLParserNoEndingQuotes
            Syntax error : detected a starting quote but no ending one
        """
        self.__logger.debug('Lex file %s', fileName)
        self.__lexerPosition = LexerPosition(fileName, startLine, startColumn)

        for char in codeString:
            self.__logger.debug('char %s', char)
            self.__currentChar = char
            if not self.__lexerPosition.isCurrentTokenAString:
                self.__handleSyntaxTokens()
                continue

            if char == '"':
                self.__handleDoubleQuotes()
                continue

            if char == '\n':
                position = str(
                    Position(
                        self.__lexerPosition.currentFile,
                        self.__lexerPosition.currentLine,
                        self.__lexerPosition.currentColumn,
                    ),
                )
                self.__logger.error(
                    f'Invalid syntax, missing ending quotes at : {position}',
                )
                raise DSLParserNoEndingQuotes(position)

            self.__iterateNextChar()

        self.__addFileEnd()
        self.__logger.debug('Finished lexing file %s', fileName)

    def __iterateNextChar(self):
        """Function to iterate to the next character

        Add the current character to the current Token
        """
        self.__lexerPosition.addCharToCurrentToken(self.__currentChar)
        self.__lexerPosition.nextColumn()

    def __handleEmptyToken(self):
        pass

    def __handleSyntaxTokens(self) -> None:
        """Function to handle single character tokens

        Check if the current character is a special token and calls the corresponding
        function.
        If it isn't, it calls the '__iterateNextChar' function
        """
        singleCharTokens = {
            ':': self.__handleColumnToken,
            '"': self.__handleDoubleQuotes,
            '#': self.__handleHashToken,
            '\n': self.__handleNewlineToken,
            '\t': self.__handleTabToken,
            ' ': self.__handleWhitespace,
        }

        singleCharTokens.get(self.__currentChar, self.__iterateNextChar)()

    def __handleCurrentToken(self) -> None:
        """Function to process the current stored token

        Check if the current token is a keyword, calls the cprresponding function, or
        the '__handleLiteralsAndVariables' otherwise.
        """
        currentTokenLower = self.__lexerPosition.currentToken.lower()

        keyWordsAndTokens = {
            '': self.__handleEmptyToken,
            '-': self.__handleDashToken,
            'amount': self.__handleAmountToken,
            'if': self.__handleIfToken,
            'elif': self.__handleElifToken,
            'else': self.__handleElseToken,
            'true': self.__handleBooleanToken,
            'false': self.__handleBooleanToken,
        }

        keyWordsAndTokens.get(
            currentTokenLower, self.__handleLiteralsAndVariables,
        )()

    def __handleLiteralsAndVariables(self) -> None:
        """Function to create a literal or var token

        Checks the current token to create a var, int, float or string token
        """
        currentToken = self.__lexerPosition.currentToken
        if self.__lexerPosition.isCurrentTokenAVariable:
            self.__addLiteralTokenToList(TT.VAR.value, currentToken)
            self.__lexerPosition.setIsVariable(False)

        elif currentToken.isdigit():
            self.__addLiteralTokenToList(TT.INT.value, currentToken)

        elif self.__isfloat(currentToken):
            self.__addLiteralTokenToList(TT.FLOAT.value, currentToken)

        else:
            self.__addLiteralTokenToList(TT.STRING.value, currentToken)

    def __addLiteralTokenToList(self, tokenType: str, value: str):
        """Function to add a literal token to the token list

        Parameters
        ----------
        tokenType : str
            Type of the token
        value : str
            Value of the token
        """
        self.__addBaseToken(
            tokenType,
            value,
            isCurrentToken=True,
        )

    def __addBaseToken(
        self,
        tokenType: str,
        value: str = None,
        isCurrentToken: bool = False,
    ) -> None:
        """Basic function to add a token to the token list

        Parameters
        ----------
        tokenType : str
            Type of the token
        value : str, optional
            Value of the token, by default None
        isCurrentToken : bool, optional
            Indicates if this token is the current stored token, by default False
        """
        if not isCurrentToken:
            self.__addTokenToList(
                Token(
                    self.__lexerPosition.currentCharPosition,
                    tokenType,
                    value,
                ),
            )
            return

        self.__addTokenToList(
            Token(
                self.__lexerPosition.currentTokenPosition,
                tokenType,
                value,
            ),
        )

    def __basePositionUpdate(
        self,
        resetCurrentToken: bool = True,
    ) -> None:
        """Basic function to update the lexer's current position

        Parameters
        ----------
        resetCurrentToken : bool, optional
            Indicates if the current stored token should be reset, by default True
        """
        self.__lexerPosition.nextColumn()
        if resetCurrentToken:
            self.__lexerPosition.resetCurrentToken()

        self.__lexerPosition.resetConsecutiveWhitespaces()
        self.__lexerPosition.setIsVariable(False)

    def __handleBaseToken(
        self,
        tokenType: str,
        value: str = None,
        isCurrentToken: bool = False,
        handleCurrentToken: bool = True,
        resetCurrentToken: bool = True,
    ) -> None:
        """Basic function to handle a token creation and lexer position

        Parameters
        ----------
        tokenType : str
            Type of the token
        value : str, optional
            Value of the token, by default None
        isCurrentToken : bool, optional
            Indicates if this token is the current stored token, by default False
        handleCurrentToken : bool, optional
            Indicates if the current stored token should be processed, by default True
        resetCurrentToken : bool, optional
            Indicates if the current stored token should be reset, by default True
        """
        if handleCurrentToken:
            self.__handleCurrentToken()
        self.__addBaseToken(tokenType, value, isCurrentToken)
        self.__basePositionUpdate(resetCurrentToken)

    def __handleColumnToken(self):
        """Function to handle a COLUMN token ':'
        """
        self.__handleBaseToken(TT.COLUMN.value)

    def __handleHashToken(self) -> None:
        """Function to handle a HASH token '#'

        Sets a variable to indicate that the following literal is a Variable
        """
        self.__handleCurrentToken()
        self.__basePositionUpdate()
        self.__lexerPosition.setIsVariable(True)

    def __handleWhitespace(self) -> None:
        """Function to handle a WHITESPACE token ' '

        Replaces 4 following whitespaces by a TAB token
        """
        self.__handleCurrentToken()
        self.__lexerPosition.nextColumn()
        self.__lexerPosition.resetCurrentToken()
        self.__lexerPosition.setIsVariable(False)
        self.__lexerPosition.addConsecutiveWhitespace()
        if self.__lexerPosition.consecutiveWhitespaces == 4:
            self.__lexerPosition.nextColumn(-4)
            self.__addBaseToken(TT.TAB.value)
            self.__lexerPosition.resetConsecutiveWhitespaces()
            self.__lexerPosition.nextColumn()
            self.__lexerPosition.setCurrentTokenIndex()

    def __handleNewlineToken(self) -> None:
        """Function to handle a NEWLINE token '\\n'
        """
        self.__handleBaseToken(TT.NEWLINE.value)
        self.__lexerPosition.newLine()
        self.__lexerPosition.setCurrentTokenIndex(1)

    def __handleTabToken(self) -> None:
        """Function to handle a TAB token '\\t'
        """
        self.__handleBaseToken(TT.TAB.value)

    def __handleDoubleQuotes(self) -> None:
        """Function to handle a DOUBLEQUOTES token '"'

        Sets a variable to indicate that the following characters are a STRING token.
        """
        if self.__lexerPosition.isCurrentTokenAString:
            self.__addLiteralTokenToList(
                TT.STRING.value, self.__lexerPosition.currentToken,
            )
            self.__lexerPosition.setIsString()
            self.__basePositionUpdate()
        else:
            self.__handleCurrentToken()
            self.__lexerPosition.nextColumn()
            self.__lexerPosition.setIsString(True)
        self.__lexerPosition.resetCurrentToken()

    def __handleDashToken(self):
        """Function to handle a DASH token '-'
        """
        self.__addBaseToken(TT.DASH.value, isCurrentToken=True)

    def __handleAmountToken(self):
        """Function to handle an AMOUNT token 'amount'
        """
        self.__addBaseToken(TT.AMOUNT.value, isCurrentToken=True)

    def __handleIfToken(self):
        """Function to handle an IF token 'if'
        """
        self.__addBaseToken(TT.IF.value, isCurrentToken=True)

    def __handleElifToken(self):
        """Function to handle an ELIF token 'elif'
        """
        self.__addBaseToken(TT.ELIF.value, isCurrentToken=True)

    def __handleElseToken(self):
        """Function to handle an ELSE token 'else'
        """
        self.__addBaseToken(TT.ELSE.value, isCurrentToken=True)

    def __handleBooleanToken(self):
        """Function to handle a BOOLEAN token 'true' or 'false'
        """
        self.__addBaseToken(
            TT.BOOLEAN.value, self.__lexerPosition.currentToken, True,
        )

    def __handleEofToken(self) -> None:
        """Function to add an EOF token at the end of each file
        """
        self.__addBaseToken(TT.EOF.value)

    def __addTokenToList(self, token: Token | None) -> None:
        """Function to add a new token to the parser's token list

        Parameters
        ----------
        token : Token | None
            New token to add
        """
        if not token:
            pass
        self.__tokenList.append(token)

    def __addFileEnd(self) -> None:
        """Function to add a NEWLINE and an EOF token at the end of each file
        """
        if len(self.__lexerPosition.currentToken.strip()) > 0:
            self.__handleCurrentToken()
            self.__lexerPosition.resetCurrentToken()
        self.__handleNewlineToken()
        self.__handleEofToken()

    def __isfloat(self, num: str) -> bool:
        """_summary_

        Parameters
        ----------
        num : str
            The input string to check

        Returns
        -------
        bool
            Is the string a float true or false
        """
        try:
            float(num)
            return True
        except ValueError:
            return False


class LexerPosition():
    def __init__(
        self,
        fileName: str,
        startLine: int = 1,
        startColumn: int = 1,
    ) -> None:
        """Class to represent the state and position if the lexer

        Parameters
        ----------
        fileName : str
            Name of the current file
        startLine : int, optional
            Starting line in the current file, by default 1
        startColumn : int, optional
            Starting column in the current file, by default 1
        """
        self.__currentFile = fileName
        self.__currentLine = startLine
        self.__currentColumn = startColumn
        self.__currentToken = ''
        self.__currentTokenIndex = startColumn
        self.__isVariable = False
        self.__inQuotedString = False
        self.__consecutiveWhitespaces = 0

    @property
    def currentFile(self):
        return self.__currentFile

    @property
    def currentLine(self):
        return self.__currentLine

    @property
    def currentColumn(self):
        return self.__currentColumn

    @property
    def currentToken(self):
        return self.__currentToken

    @property
    def currentTokenIndex(self):
        return self.__currentTokenIndex

    @property
    def isCurrentTokenAVariable(self):
        return self.__isVariable

    @property
    def isCurrentTokenAString(self):
        return self.__inQuotedString

    @property
    def consecutiveWhitespaces(self):
        return self.__consecutiveWhitespaces

    @property
    def currentCharPosition(self) -> Position:
        return Position(
            self.__currentFile,
            self.__currentLine,
            self.__currentColumn,
        )

    @property
    def currentTokenPosition(self) -> Position:
        return Position(
            self.__currentFile,
            self.__currentLine,
            self.__currentTokenIndex,
        )

    def newLine(self) -> None:
        """Function to set the position to the next line
        """
        self.__currentLine += 1
        self.__currentColumn = 1

    def nextColumn(self, step: int = 1) -> None:
        """Function to set the position to a new column

        Parameters
        ----------
        step : int
            Step to modify the current column, by default 1
        """
        if (self.__currentColumn + step) > 0:
            self.__currentColumn += step
        else:
            self.__currentColumn = 0  # Raise exception ?

    def addCharToCurrentToken(self, char) -> None:
        """_Function to add a char to the current stored token

        Parameters
        ----------
        char : _type_
            Char to add to the token
        """
        self.__currentToken += char

    def setCurrentTokenIndex(self, newIndex: int = None) -> None:
        """Function to modify the stored token index

        Parameters
        ----------
        newIndex : int, optional
            New index of the stored token, by default None
        """
        if newIndex:
            self.__currentTokenIndex = newIndex
        else:
            self.__currentTokenIndex = self.__currentColumn

    def resetCurrentToken(self, newIndex: int = None) -> None:
        """Function to reset the current stored token and its index

        Parameters
        ----------
        newIndex : int, optional
            New index of the stored token, by default None
        """
        self.__currentToken = ''
        self.setCurrentTokenIndex(newIndex)

    def addConsecutiveWhitespace(self) -> None:
        """Function to add a consecutive whitespace to the lexer state
        """
        self.__consecutiveWhitespaces += 1

    def resetConsecutiveWhitespaces(self) -> None:
        """Function to reset consecutive whitespaces of the lexer state to 0
        """
        self.__consecutiveWhitespaces = 0

    def setIsVariable(self, value: bool = False) -> None:
        """Function to set the current stored token as a variable

        Parameters
        ----------
        value : bool, optional
            Is the stored token a variable True or False, by default False
        """
        self.__isVariable = value

    def setIsString(self, value: bool = False) -> None:
        """Function to set the current stored token as a string

        Parameters
        ----------
        value : bool, optional
            Is the stored token a string True or False, by default False
        """
        self.__inQuotedString = value
