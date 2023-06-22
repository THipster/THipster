"""Module containing the Token class and the TOKENTYPES enum."""
from enum import Enum

from thipster.engine.parsed_file import Position


class TOKENTYPES(Enum):
    """Contains all the possible token types."""

    AMOUNT = 'AMOUNT'
    AND = 'AND'
    BOOLEAN = 'BOOLEAN'
    BRACKETS_START = 'BRACKETS_START'
    BRACKETS_END = 'BRACKETS_END'
    COLON = 'COLON'
    COMMA = 'COMMA'
    ELIF = 'ELIF'
    ELSE = 'ELSE'
    EOF = 'EOF'
    EXCLAMATION = 'EXCLAMATION'
    FLOAT = 'FLOAT'
    IF = 'IF'
    INT = 'INT'
    NEWLINE = 'NEWLINE'
    NOT = 'NOT'
    OR = 'OR'
    PARENTHESES_START = 'PARENTHESES_START'
    PARENTHESES_END = 'PARENTHESES_END'
    STRING = 'STRING'
    TAB = 'TAB'
    VAR = 'VAR'
    WHITESPACE = 'WHITESPACE'

    PLUS = 'PLUS'
    MINUS = 'MINUS'
    MUL = 'MUL'
    DIV = 'DIV'
    POW = 'POW'
    EQ = 'EQ'
    EE = 'EE'
    NE = 'NE'
    LT = 'LT'
    LTE = 'LTE'
    GT = 'GT'
    GTE = 'GTE'

    def __str__(self) -> str:
        """Return the string representation of the token type."""
        return self.value


class Token():
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
