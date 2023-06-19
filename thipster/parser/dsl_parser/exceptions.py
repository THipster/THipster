"""Exceptions for the DSL parser."""
from thipster.engine import THipsterError
from thipster.engine.parsed_file import Position

from .token import TOKENTYPES as TT
from .token import Token


class DSLParserBaseError(THipsterError):
    """Base class for DSL parser exceptions."""

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class DSLParserPathNotFoundError(DSLParserBaseError):
    """Exception raised when a file or directory is not found."""

    def __init__(self, file, *args: object) -> None:
        super().__init__(*args)
        self.file = file

    @property
    def message(self) -> str:
        """Return the exception message."""
        return f'Path not found : {self.file}'


class DSLSyntaxError(DSLParserBaseError):
    """Exception raised when a syntax error is encountered."""

    def __init__(self, token: Token, expected: TT | list[TT], *args: object) -> None:
        super().__init__(*args)
        self.token = token
        self.expected = expected

    @property
    def message(self) -> str:
        """Return the exception message."""
        if type(self.expected) is TT:
            return f"""{self.token.position!s} :\n\tSyntax error : Expected \
{self.expected.value!s}, got {self.token.token_type!s}"""

        return f"""{self.token.position!s} :\n\tSyntax error : Expected \
{' or '.join(list(map(str, self.expected)))!s}, got {
    self.token.token_type!s}"""


class DSLConditionError(DSLParserBaseError):
    """Exception raised when a condition is not valid."""

    def __init__(self, token: Token, *args: object) -> None:
        super().__init__(*args)
        self.token = token

    @property
    def message(self) -> str:
        """Return the exception message."""
        return f'{self.token.position!s} :\n\tBad condition'


class DSLArithmeticError(DSLParserBaseError):
    """Exception raised when an arithmetic error is encountered."""

    def __init__(self, position: Position, error_message: str, *args: object) -> None:
        super().__init__(*args)
        self.position = position
        self.error_message = error_message

    @property
    def message(self) -> str:
        """Return the exception message."""
        return f'{self.position!s} :\n\tArithmetic error :{self.error_message}'


class DSLUnexpectedEOFError(DSLParserBaseError):
    """Exception raised when an unexpected EOF is encountered."""

    def __init__(self, *args: object) -> None:
        super().__init__(*args)

    @property
    def message(self) -> str:
        """Return the exception message."""
        return 'Unexpected EOF'


class DSLParserNoEndingQuotesError(DSLParserBaseError):
    """Exception raised when no ending quotes are found."""

    def __init__(self, position, *args: object) -> None:
        super().__init__(*args)
        self.position = position

    @property
    def message(self) -> str:
        """Return the exception message."""
        return f'Invalid syntax, missing ending quotes at : {self.position}'


class DSLParserVariableAlreadyUsedError(DSLParserBaseError):
    """Exception raised when a variable name is already used."""

    def __init__(self, var: str, *args: object) -> None:
        super().__init__(*args)
        self.variable = var

    @property
    def message(self) -> str:
        """Return the exception message."""
        return f'Variable already used : {self.variable}'


class DSLParserVariableNotDeclaredError(DSLParserBaseError):
    """Exception raised when a variable is not declared."""

    def __init__(self, var: str, *args: object) -> None:
        super().__init__(*args)
        self.variable = var

    @property
    def message(self) -> str:
        """Return the exception message."""
        return f'Variable not declared : {self.variable}'
