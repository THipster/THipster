from thipster.engine.parsed_file import Position
from thipster.helpers import createLogger

from .exceptions import DSLParserNoEndingQuotes
from .lexer_position import LexerPosition
from .token import TOKENTYPES as TT
from .token import Token


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
        self.__lexerPosition = LexerPosition()
        self.__currentChar = ''

    @property
    def files(self):
        return self.__files

    @property
    def tokenList(self):
        return self.__tokenList

    def run(self) -> list[Token]:
        """Launch the Lexer

        Returns
        -------
        list[Token]
            List of Tokens representing the input files
        """
        self.__logger.info('Start Lexer')
        for fileName, fileContent in self.files.items():
            self.lex(fileContent, fileName, 1, 1)

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
        """Tokenize a file contents

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
            if not self.__lexerPosition.isQuotedString:
                self.__handleSyntaxTokens()
                continue

            if char in ['"', "'"]:
                self.__handleDoubleQuotes(char)()
                continue

            if char == '\n':
                if self.__lexerPosition.isCurrentTokenMultiLine:
                    self.__lexerPosition.newLine()
                    continue
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
        """Iterate to the next character

        Add the current character to the current Token
        """
        self.__lexerPosition.addCharToCurrentToken(self.__currentChar)
        self.__lexerPosition.nextColumn()

    def __handleEmptyToken(self):
        pass

    def __handleSyntaxTokens(self) -> None:
        """Handle single character tokens

        Check if the current character is a special token and calls the corresponding
        function.
        If it isn't, it calls the '__iterateNextChar' function
        """
        singleCharTokens = {
            ':': self.__handleColonToken,
            ',': self.__handleCommaToken,
            '[': self.__handleBracketsStartToken,
            ']': self.__handleBracketsEndToken,
            '(': self.__handleParenthesesStartToken,
            ')': self.__handleParenthesesEndToken,
            '"': self.__handleDoubleQuotes('"'),
            "'": self.__handleDoubleQuotes("'"),
            '#': self.__handleHashToken,
            '\n': self.__handleNewlineToken,
            '\\': self.__handleBackSlashToken,
            '\t': self.__handleTabToken,
            ' ': self.__handleWhitespace,

            '=': self._handleEQToken,
            '/': self._handleDivToken,
            '-': self._handleMinusToken,
            '+': self._handlePlusToken,
            '*': self._handleMulToken,
            '^': self._handlePowToken,
            '<': self._handleLTToken,
            '>': self._handleGTToken,
            '!': self._handleExclamationToken,
        }

        singleCharTokens.get(self.__currentChar, self.__iterateNextChar)()

    def __handleCurrentToken(self) -> None:
        """Process the current stored token

        Check if the current token is a keyword, calls the cprresponding function, or
        the '__handleLiteralsAndVariables' otherwise.
        """
        currentTokenLower = self.__lexerPosition.currentToken.lower()

        keyWordsAndTokens = {
            '': self.__handleEmptyToken,
            'amount': self.__handleAmountToken,
            'and': self.__handleAndToken,
            'if': self.__handleIfToken,
            'elif': self.__handleElifToken,
            'else': self.__handleElseToken,
            'or': self.__handleOrToken,
            'true': self.__handleBooleanToken,
            'false': self.__handleBooleanToken,
            'not': self.__handleNotToken,
        }

        keyWordsAndTokens.get(
            currentTokenLower, self.__handleLiteralsAndVariables,
        )()

    def __handleLiteralsAndVariables(self) -> None:
        """Create a literal or var token

        Checks the current token to create a var, int, float or string token
        """
        currentToken = self.__lexerPosition.currentToken
        if self.__lexerPosition.isCurrentTokenAVariable:
            self.__addLiteralTokenToList(TT.VAR, currentToken)
            self.__lexerPosition.setIsVariable(False)

        elif currentToken.isdigit():
            self.__addLiteralTokenToList(TT.INT, currentToken)

        elif self.__isfloat(currentToken):
            self.__addLiteralTokenToList(TT.FLOAT, currentToken)

        else:
            self.__addLiteralTokenToList(TT.STRING, currentToken)

    def __addLiteralTokenToList(self, tokenType: str, value: str):
        """Add a literal token to the token list

        Parameters
        ----------
        tokenType : str
            Type of the token
        value : str
            Value of the token
        """
        self.__lexerPosition.resetConsecutiveWhitespaces()
        self.__addBaseToken(
            tokenType,
            value,
            isCurrentToken=True,
        )

    def __addBaseToken(
        self,
        tokenType: str,
        value: str | None = None,
        isCurrentToken: bool = False,
    ) -> None:
        """Add a token to the token list

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
        """Update the lexer's current position

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
        value: str | None = None,
        isCurrentToken: bool = False,
        handleCurrentToken: bool = True,
        resetCurrentToken: bool = True,
    ) -> None:
        """Handle a token creation and lexer position

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

    def __handleColonToken(self):
        """Handle a COLON token ':'
        """
        self.__handleBaseToken(TT.COLON)

    def __handleCommaToken(self):
        """Handle a COMMA token ','
        """
        self.__handleBaseToken(TT.COMMA)

    def __handleBracketsStartToken(self):
        """Handle a BRACKETS_START token '['
        """
        self.__handleBaseToken(TT.BRACKETS_START)

    def __handleBracketsEndToken(self):
        """Handle a BRACKETS_END token ']'
        """
        self.__handleBaseToken(TT.BRACKETS_END)

    def __handleParenthesesStartToken(self):
        """Handle a PARENTESES_START token '('
        """
        self.__handleBaseToken(TT.PARENTHESES_START)

    def __handleParenthesesEndToken(self):
        """Handle a PARENTHESES_END token ')'
        """
        self.__handleBaseToken(TT.PARENTHESES_END)

    def _handlePlusToken(self):
        """Handle a PLUS token '+'
        """
        self.__handleBaseToken(TT.PLUS)

    def _handleMinusToken(self):
        """Handle a MINUS token '-'
        """
        self.__handleBaseToken(TT.MINUS)

    def _handleMulToken(self):
        """Handle a MUL token '*'
        """
        self.__handleBaseToken(TT.MUL)

    def _handleDivToken(self):
        """Handle a DIV token '/'
        """
        self.__handleBaseToken(TT.DIV)

    def _handleEQToken(self):
        """Handle a EQ token '='
        """
        self.__handleBaseToken(TT.EQ)

    def _handleExclamationToken(self):
        """Handle a NE token '!='
        """
        self.__handleBaseToken(TT.EXCLAMATION)

    def _handleLTToken(self):
        """Handle a LT token '<'
        """
        self.__handleBaseToken(TT.LT)

    def _handleGTToken(self):
        """Handle a GT token '>'
        """
        self.__handleBaseToken(TT.GT)

    def _handlePowToken(self):
        """Handle a POW token '^'
        """
        self.__handleBaseToken(TT.POW)

    def __handleHashToken(self) -> None:
        """Handle a HASH token '#'

        Sets a variable to indicate that the following literal is a Variable
        """
        self.__handleCurrentToken()
        self.__basePositionUpdate()
        self.__lexerPosition.setIsVariable(True)

    def __handleWhitespace(self) -> None:
        """Handle a WHITESPACE token ' '

        Replaces 4 following whitespaces by a TAB token
        """
        self.__handleCurrentToken()
        self.__addBaseToken(TT.WHITESPACE)
        self.__lexerPosition.nextColumn()
        self.__lexerPosition.resetCurrentToken()
        self.__lexerPosition.setIsVariable(False)
        self.__lexerPosition.addConsecutiveWhitespace()
        if self.__lexerPosition.consecutiveWhitespaces == 4:
            self.__lexerPosition.nextColumn(-4)
            self.__rmLastTokens(4)
            self.__addBaseToken(TT.TAB)
            self.__lexerPosition.nextColumn(4)
            self.__lexerPosition.resetConsecutiveWhitespaces()
            self.__lexerPosition.setCurrentTokenIndex()

    def __handleNewlineToken(self) -> None:
        """Handle a NEWLINE token '\\n'
        """
        if not self.__lexerPosition.isCurrentTokenMultiLine:
            self.__handleBaseToken(TT.NEWLINE)

        self.__lexerPosition.newLine()
        if not self.__lexerPosition.isCurrentTokenMultiLine:
            self.__lexerPosition.setCurrentTokenIndex()

        self.__lexerPosition.setIsMultiLine(value=False)

    def __handleBackSlashToken(self) -> None:
        """Handle a BACKSLASH token '\\'

        Sets a variable to indicate that the following line is part of the same token.
        """
        self.__lexerPosition.setIsMultiLine(value=True)
        self.__lexerPosition.nextColumn()

    def __handleTabToken(self) -> None:
        """Handle a TAB token '\\t'
        """
        self.__handleBaseToken(TT.TAB)

    def __handleDoubleQuotes(self, char) -> None:
        """Handle a DOUBLEQUOTES token '"'

        Sets a variable to indicate that the following characters are a STRING token.
        """

        def quoteHandler(self=self):

            if self.__lexerPosition.isQuotedString:
                if char == self.__lexerPosition.isQuotedString:
                    self.__addLiteralTokenToList(
                        TT.STRING, self.__lexerPosition.currentToken,
                    )
                    self.__lexerPosition.isQuotedString = False
                    self.__basePositionUpdate()
                else:
                    self.__iterateNextChar()
            else:
                self.__handleCurrentToken()
                self.__lexerPosition.nextColumn()
                self.__lexerPosition.isQuotedString = char
                self.__lexerPosition.resetCurrentToken()

        return quoteHandler

    def __handleAmountToken(self):
        """Handle an AMOUNT token 'amount'
        """
        self.__lexerPosition.resetConsecutiveWhitespaces()
        self.__addBaseToken(TT.AMOUNT, isCurrentToken=True)

    def __handleAndToken(self):
        """Handle an AND token 'and'
        """
        self.__lexerPosition.resetConsecutiveWhitespaces()
        self.__addBaseToken(TT.AND, isCurrentToken=True)

    def __handleIfToken(self):
        """Handle an IF token 'if'
        """
        self.__lexerPosition.resetConsecutiveWhitespaces()
        self.__addBaseToken(TT.IF, isCurrentToken=True)

    def __handleElifToken(self):
        """Handle an ELIF token 'elif'
        """
        self.__lexerPosition.resetConsecutiveWhitespaces()
        self.__addBaseToken(TT.ELIF, isCurrentToken=True)

    def __handleElseToken(self):
        """Handle an ELSE token 'else'
        """
        self.__lexerPosition.resetConsecutiveWhitespaces()
        self.__addBaseToken(TT.ELSE, isCurrentToken=True)

    def __handleNotToken(self):
        """Handle an OR token 'or'
        """
        self.__lexerPosition.resetConsecutiveWhitespaces()
        self.__addBaseToken(TT.NOT, isCurrentToken=True)

    def __handleOrToken(self):
        """Handle an OR token 'or'
        """
        self.__lexerPosition.resetConsecutiveWhitespaces()
        self.__addBaseToken(TT.OR, isCurrentToken=True)

    def __handleBooleanToken(self):
        """Handle a BOOLEAN token 'true' or 'false'
        """
        self.__lexerPosition.resetConsecutiveWhitespaces()
        self.__addBaseToken(
            TT.BOOLEAN, self.__lexerPosition.currentToken, True,
        )

    def __handleEofToken(self) -> None:
        """Add an EOF token at the end of each file
        """
        self.__addBaseToken(TT.EOF)

    def __addTokenToList(self, token: Token | None) -> None:
        """Add a new token to the parser's token list

        Parameters
        ----------
        token : Token | None
            New token to add
        """
        if not token:
            pass
        self.__tokenList.append(token)

    def __rmLastTokens(self, amount: int = 1):
        self.__tokenList = self.__tokenList[:-amount]

    def __addFileEnd(self) -> None:
        """Add a NEWLINE and an EOF token at the end of each file
        """
        if len(self.__lexerPosition.currentToken.strip()) > 0:
            self.__handleCurrentToken()
            self.__lexerPosition.resetCurrentToken()
        self.__handleNewlineToken()
        self.__handleEofToken()

    def __isfloat(self, num: str) -> bool:
        """Check if the string is a float

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
