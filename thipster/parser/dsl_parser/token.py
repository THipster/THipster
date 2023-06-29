"""Module containing the Token class and the TOKENTYPES enum."""
from enum import Enum

from thipster.engine.parsed_file import Position


class TOKENTYPES(Enum):
    """Contains all the possible token types."""

    # TYPES
    BOOLEAN = 'BOOLEAN'
    FLOAT = 'FLOAT'
    INT = 'INT'
    STRING = 'STRING'
    VAR = 'VAR'

    # KEYWORDS
    AMOUNT = 'AMOUNT'
    AND = 'AND'
    ELIF = 'ELIF'
    ELSE = 'ELSE'
    IF = 'IF'
    NOT = 'NOT'
    OR = 'OR'
    OUTPUT = 'OUTPUT'

    # SYMBOLS
    BRACKETS_END = 'BRACKETS_END'
    BRACKETS_START = 'BRACKETS_START'
    COLON = 'COLON'
    COMMA = 'COMMA'
    DIV = 'DIV'
    EE = 'EE'
    EOF = 'EOF'
    EQ = 'EQ'
    EXCLAMATION = 'EXCLAMATION'
    GT = 'GT'
    GTE = 'GTE'
    LT = 'LT'
    LTE = 'LTE'
    MINUS = 'MINUS'
    MUL = 'MUL'
    NE = 'NE'
    NEWLINE = 'NEWLINE'
    PARENTHESES_END = 'PARENTHESES_END'
    PARENTHESES_START = 'PARENTHESES_START'
    PERCENT = 'PERCENT'
    PLUS = 'PLUS'
    POW = 'POW'
    TAB = 'TAB'
    WHITESPACE = 'WHITESPACE'

    def __str__(self) -> str:
        """Return the string representation of the token type."""
        return self.value


class Token:
    """Represents a Token of the THipster DSL."""

    def __init__(
        self, position: Position,
        token_type: TOKENTYPES, value: str | None = None,
    ):
        """
        Represent a Token.

        Parameters
        ----------
        position : Position
            Position of the token in its input file
        tokenType : str
            Token type
        value : str, optional
            Token value, by default None
        """
        self.position = position
        self.token_type = token_type
        self.value = value

    def __eq__(self, __value: object) -> bool:
        """Check if two tokens are equal."""
        if not isinstance(__value, Token):
            msg = 'Value must be a Token'
            raise TypeError(msg)

        return (
            self.position == __value.position and
            self.token_type == __value.token_type and
            self.value == __value.value
        )

    def __repr__(self) -> str:
        """Return the string representation of the token."""
        token_string = f'(Type: {self.token_type!s}, Position: {self.position!s}'
        if self.value:
            token_string += f', Value: {self.value}'
        token_string += ')'

        return token_string

    def __str__(self) -> str:
        """Return the string value of the token."""
        return f'({self.token_type} {self.value})'
