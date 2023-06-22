"""Lexer module for the DSL Parser."""
from thipster.engine.parsed_file import Position
from thipster.helpers import create_logger

from .exceptions import DSLParserNoEndingQuotesError
from .lexer_position import LexerPosition
from .token import TOKENTYPES as TT
from .token import Token


class Lexer():
    """Lexer for the DSL Parser."""

    def __init__(self, files: dict[str, str]):
        """Lexer for the DSL Parser.

        Parameters
        ----------
        files : dict[str, str]
            Dictionnary of files to tokenize, fileName : fileContent
        """
        self.__logger = create_logger(__name__)
        self.files = files
        self.tokenList = []
        self.__lexerPosition = LexerPosition()
        self.__currentChar = ''

    def run(self) -> list[Token]:
        """Launch the Lexer.

        Returns
        -------
        list[Token]
            List of Tokens representing the input files
        """
        self.__logger.info('Start Lexer')
        for filename, file_content in self.files.items():
            self.lex(filename, file_content)

        self.__logger.info(
            'Shuting down Lexer, processed %d file(s) and generated %d tokens',
            len(self.files),
            len(self.tokenList),
        )
        return self.tokenList

    def lex(
        self,
        filename: str,
        file_content: str,
    ) -> None:
        """Tokenize a file contents.

        Parameters
        ----------
        filename : str
            Name of the file
        file_content : str
            Content of the file

        Raises
        ------
        DSLParserNoEndingQuotes
            Syntax error : detected a starting quote but no ending one
        """
        self.__logger.debug('Lex file %s', filename)
        self.__lexerPosition = LexerPosition(filename)

        for char in file_content:
            self.__logger.debug('char %s', char)
            self.__currentChar = char
            if not self.__lexerPosition.isQuotedString:
                self.__handle_syntax_tokens()
                continue

            if char in ['"', "'"]:
                self.__handle_quotes(char)()
                continue

            if char == '\n':
                if self.__lexerPosition.isMultiLine:
                    self.__lexerPosition.new_line()
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
                raise DSLParserNoEndingQuotesError(position)

            self.__add_next_char()

        self.__end_file()
        self.__logger.debug('Finished lexing file %s', filename)

    def __add_next_char(self):
        """Add the current character to the current Token."""
        self.__lexerPosition.add_to_current_token(self.__currentChar)
        self.__lexerPosition.next_column()

    def __handle_empty_token(self):
        """Pass EMPTY tokens ''."""
        pass

    def __handle_syntax_tokens(self) -> None:
        """Handle single character tokens.

        Check if the current character is a special token and calls the corresponding
        function.
        If it isn't, it calls the '__iterateNextChar' function
        """
        single_char_tokens = {
            ':': self.__handle_colon_oken,
            ',': self.__handle_comma_token,
            '[': self.__handle_brackets_start_token,
            ']': self.__handle_brackets_end_token,
            '(': self.__handle_parentheses_start_token,
            ')': self.__handle_parentheses_end_token,
            '"': self.__handle_quotes('"'),
            "'": self.__handle_quotes("'"),
            '#': self.__handle_hash_token,
            '\n': self.__handle_newline_token,
            '\\': self.__handle_backslash_token,
            '\t': self.__handle_tab_token,
            ' ': self.__handle_whitespace,

            '=': self.__handle_eq_token,
            '/': self.__handle_div_token,
            '-': self.__handle_minus_token,
            '+': self.__handle_plus_token,
            '*': self.__handle_mul_token,
            '^': self.__handle_pow_token,
            '<': self.__handle_lt_token,
            '>': self.__handle_gt_token,
            '!': self.__handle_exclamation_token,
        }

        single_char_tokens.get(self.__currentChar, self.__add_next_char)()

    def __handle_current_token(self) -> None:
        """Process the current stored token.

        Check if the current token is a keyword, calls the cprresponding function, or
        the '__handleLiteralsAndVariables' otherwise.
        """
        current_token = self.__lexerPosition.currentToken.lower()

        keywords = {
            '': self.__handle_empty_token,
            'amount': self.__handle_amount_token,
            'and': self.__handle_and_token,
            'if': self.__handle_if_token,
            'elif': self.__handle_elif_token,
            'else': self.__handle_else_token,
            'or': self.__handle_or_token,
            'true': self.__handle_boolean_token,
            'false': self.__handle_boolean_token,
            'not': self.__handle_not_token,
        }

        keywords.get(current_token, self.__handle_literals_and_variables)()

    def __handle_literals_and_variables(self) -> None:
        """Create a literal or var token.

        Checks the current token to create a var, int, float or string token
        """
        current_token = self.__lexerPosition.currentToken
        if self.__lexerPosition.isVariable:
            self.__add_literal_token_to_list(TT.VAR, current_token)
            self.__lexerPosition.isVariable = False

        elif current_token.isdigit():
            self.__add_literal_token_to_list(TT.INT, current_token)

        elif self.__isfloat(current_token):
            self.__add_literal_token_to_list(TT.FLOAT, current_token)

        else:
            self.__add_literal_token_to_list(TT.STRING, current_token)

    def __add_literal_token_to_list(self, token_type: str, value: str):
        """Add a literal token to the token list.

        Parameters
        ----------
        tokenType : str
            Type of the token
        value : str
            Value of the token
        """
        self.__lexerPosition.reset_consecutive_whitespaces()
        self.__add_base_token(
            token_type,
            value,
            is_current_token=True,
        )

    def __add_base_token(
        self,
        token_type: str,
        value: str | None = None,
        is_current_token: bool = False,
    ) -> None:
        """Add a token to the token list.

        Parameters
        ----------
        tokenType : str
            Type of the token
        value : str, optional
            Value of the token, by default None
        isCurrentToken : bool, optional
            Indicates if this token is the current stored token, by default False
        """
        if not is_current_token:
            self.__add_token_to_list(
                Token(
                    self.__lexerPosition.currentCharPosition,
                    token_type,
                    value,
                ),
            )
            return

        self.__add_token_to_list(
            Token(
                self.__lexerPosition.currentTokenPosition,
                token_type,
                value,
            ),
        )

    def __update_position(
        self,
        reset_current_token: bool = True,
    ) -> None:
        """Update the lexer's current position.

        Parameters
        ----------
        resetCurrentToken : bool, optional
            Indicates if the current stored token should be reset, by default True
        """
        self.__lexerPosition.next_column()
        if reset_current_token:
            self.__lexerPosition.reset_current_token()

        self.__lexerPosition.reset_consecutive_whitespaces()
        self.__lexerPosition.isVariable = False

    def __handle_base_token(
        self,
        token_type: str,
        value: str | None = None,
        is_current_token: bool = False,
        handle_current_token: bool = True,
        reset_current_token: bool = True,
    ) -> None:
        """Handle a token creation and lexer position.

        Parameters
        ----------
        token_type : str
            Type of the token
        value : str, optional
            Value of the token, by default None
        is_current_token : bool, optional
            Indicates if this token is the current stored token, by default False
        handle_current_token : bool, optional
            Indicates if the current stored token should be processed, by default True
        reset_current_token : bool, optional
            Indicates if the current stored token should be reset, by default True
        """
        if handle_current_token:
            self.__handle_current_token()
        self.__add_base_token(token_type, value, is_current_token)
        self.__update_position(reset_current_token)

    def __handle_colon_oken(self):
        """Handle a COLON token ':'."""
        self.__handle_base_token(TT.COLON)

    def __handle_comma_token(self):
        """Handle a COMMA token ','."""
        self.__handle_base_token(TT.COMMA)

    def __handle_brackets_start_token(self):
        """Handle a BRACKETS_START token '['."""
        self.__handle_base_token(TT.BRACKETS_START)

    def __handle_brackets_end_token(self):
        """Handle a BRACKETS_END token ']'."""
        self.__handle_base_token(TT.BRACKETS_END)

    def __handle_parentheses_start_token(self):
        """Handle a PARENTHESES_START token '('."""
        self.__handle_base_token(TT.PARENTHESES_START)

    def __handle_parentheses_end_token(self):
        """Handle a PARENTHESES_END token ')'."""
        self.__handle_base_token(TT.PARENTHESES_END)

    def __handle_plus_token(self):
        """Handle a PLUS token '+'."""
        self.__handle_base_token(TT.PLUS)

    def __handle_minus_token(self):
        """Handle a MINUS token '-'."""
        self.__handle_base_token(TT.MINUS)

    def __handle_mul_token(self):
        """Handle a MUL token '*'."""
        self.__handle_base_token(TT.MUL)

    def __handle_div_token(self):
        """Handle a DIV token '/'."""
        self.__handle_base_token(TT.DIV)

    def __handle_eq_token(self):
        """Handle a EQ token '='."""
        self.__handle_base_token(TT.EQ)

    def __handle_exclamation_token(self):
        """Handle a EXCLAMATION token '!'."""
        self.__handle_base_token(TT.EXCLAMATION)

    def __handle_lt_token(self):
        """Handle a LT token '<'."""
        self.__handle_base_token(TT.LT)

    def __handle_gt_token(self):
        """Handle a GT token '>'."""
        self.__handle_base_token(TT.GT)

    def __handle_pow_token(self):
        """Handle a POW token '^'."""
        self.__handle_base_token(TT.POW)

    def __handle_hash_token(self) -> None:
        """Handle a HASH token '#'.

        Sets a variable to indicate that the following literal is a Variable
        """
        self.__handle_current_token()
        self.__update_position()
        self.__lexerPosition.isVariable = True

    def __handle_whitespace(self) -> None:
        """Handle a WHITESPACE token ' '.

        Replaces 4 following whitespaces by a TAB token
        """
        self.__handle_current_token()
        self.__add_base_token(TT.WHITESPACE)
        self.__lexerPosition.next_column()
        self.__lexerPosition.reset_current_token()
        self.__lexerPosition.isVariable = False
        self.__lexerPosition.increment_consecutive_whitespaces()
        if self.__lexerPosition.consecutiveWhitespaces == 4:
            self.__lexerPosition.next_column(-4)
            self.__rm_last_tokens(4)
            self.__add_base_token(TT.TAB)
            self.__lexerPosition.next_column(4)
            self.__lexerPosition.reset_consecutive_whitespaces()
            self.__lexerPosition.set_current_token_index()

    def __handle_newline_token(self) -> None:
        r"""Handle a NEWLINE token '\\n'."""
        if not self.__lexerPosition.isMultiLine:
            self.__handle_base_token(TT.NEWLINE)

        self.__lexerPosition.new_line()
        if not self.__lexerPosition.isMultiLine:
            self.__lexerPosition.set_current_token_index()

        self.__lexerPosition.isMultiLine = False

    def __handle_backslash_token(self) -> None:
        r"""Handle a BACKSLASH token '\\'.

        Sets a variable to indicate that the following line is part of the same token.
        """
        self.__lexerPosition.isMultiLine = True
        self.__lexerPosition.next_column()

    def __handle_tab_token(self) -> None:
        r"""Handle a TAB token '\\t'."""
        self.__handle_base_token(TT.TAB)

    def __handle_quotes(self, char) -> None:
        """Handle a DOUBLEQUOTES token '"'.

        Sets a variable to indicate that the following characters are a STRING token.
        """

        def quote_handler(self=self):

            if self.__lexerPosition.isQuotedString:
                if char == self.__lexerPosition.isQuotedString:
                    self.__add_literal_token_to_list(
                        TT.STRING, self.__lexerPosition.currentToken,
                    )
                    self.__lexerPosition.isQuotedString = False
                    self.__update_position()
                else:
                    self.__add_next_char()
            else:
                self.__handle_current_token()
                self.__lexerPosition.next_column()
                self.__lexerPosition.isQuotedString = char
                self.__lexerPosition.reset_current_token()

        return quote_handler

    def __handle_amount_token(self):
        """Handle an AMOUNT token 'amount'."""
        self.__lexerPosition.reset_consecutive_whitespaces()
        self.__add_base_token(TT.AMOUNT, is_current_token=True)

    def __handle_and_token(self):
        """Handle an AND token 'and'."""
        self.__lexerPosition.reset_consecutive_whitespaces()
        self.__add_base_token(TT.AND, is_current_token=True)

    def __handle_if_token(self):
        """Handle an IF token 'if'."""
        self.__lexerPosition.reset_consecutive_whitespaces()
        self.__add_base_token(TT.IF, is_current_token=True)

    def __handle_elif_token(self):
        """Handle an ELIF token 'elif'."""
        self.__lexerPosition.reset_consecutive_whitespaces()
        self.__add_base_token(TT.ELIF, is_current_token=True)

    def __handle_else_token(self):
        """Handle an ELSE token 'else'."""
        self.__lexerPosition.reset_consecutive_whitespaces()
        self.__add_base_token(TT.ELSE, is_current_token=True)

    def __handle_not_token(self):
        """Handle an OR token 'or'."""
        self.__lexerPosition.reset_consecutive_whitespaces()
        self.__add_base_token(TT.NOT, is_current_token=True)

    def __handle_or_token(self):
        """Handle an OR token 'or'."""
        self.__lexerPosition.reset_consecutive_whitespaces()
        self.__add_base_token(TT.OR, is_current_token=True)

    def __handle_boolean_token(self):
        """Handle a BOOLEAN token 'true' or 'false'."""
        self.__lexerPosition.reset_consecutive_whitespaces()
        self.__add_base_token(
            TT.BOOLEAN, self.__lexerPosition.currentToken, True,
        )

    def __handle_eof_token(self) -> None:
        """Add an EOF token at the end of each file."""
        self.__add_base_token(TT.EOF)

    def __add_token_to_list(self, token: Token | None) -> None:
        """Add a new token to the parser's token list.

        Parameters
        ----------
        token : Token | None
            New token to add
        """
        if not token:
            pass
        self.tokenList.append(token)

    def __rm_last_tokens(self, amount: int = 1):
        self.tokenList = self.tokenList[:-amount]

    def __end_file(self) -> None:
        """Add a NEWLINE and an EOF token at the end of each file."""
        if len(self.__lexerPosition.currentToken.strip()) > 0:
            self.__handle_current_token()
            self.__lexerPosition.reset_current_token()
        self.__handle_newline_token()
        self.__handle_eof_token()

    def __isfloat(self, num: str) -> bool:
        """Check if the string is a float.

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
