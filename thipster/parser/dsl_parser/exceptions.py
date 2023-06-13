from thipster.engine import THipsterException
from thipster.engine.parsed_file import Position
from .token import TOKENTYPES as TT
from .token import Token


class DSLParserBaseException(THipsterException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class DSLParserPathNotFound(DSLParserBaseException):
    def __init__(self, file, *args: object) -> None:
        super().__init__(*args)
        self.file = file

    @property
    def message(self) -> str:
        return f'Path not found : {self.file}'


class DSLSyntaxException(DSLParserBaseException):
    def __init__(self, token: Token, expected: TT | list[TT], *args: object) -> None:
        super().__init__(*args)
        self.token = token
        self.expected = expected

    @property
    def message(self) -> str:
        if type(self.expected) is TT:
            return f"""{str(self.token.position)} :\n\tSyntax error : Expected \
{str(self.expected.value)}, got {str(self.token.token_type)}"""
        else:
            return f"""{str(self.token.position)} :\n\tSyntax error : Expected \
{str(' or '.join(list(map(str, self.expected))))}, got {
    str(self.token.token_type)}"""


class DSLConditionException(DSLParserBaseException):
    def __init__(self, token: Token, *args: object) -> None:
        super().__init__(*args)
        self.token = token

    @property
    def message(self) -> str:
        return f'{str(self.token.position)} :\n\tBad condition'


class DSLArithmeticException(DSLParserBaseException):
    def __init__(self, position: Position, error_message: str, *args: object) -> None:
        super().__init__(*args)
        self.position = position
        self.error_message = error_message

    @property
    def message(self) -> str:
        return f'{str(self.position)} :\n\tArithmetic error :{self.error_message}'


class DSLUnexpectedEOF(DSLParserBaseException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

    @property
    def message(self) -> str:
        return 'Unexpected EOF'


class DSLParserNoEndingQuotes(DSLParserBaseException):
    def __init__(self, position, *args: object) -> None:
        super().__init__(*args)
        self.position = position

    @property
    def message(self) -> str:
        return f'Invalid syntax, missing ending quotes at : {self.position}'


class DSLParserVariableAlreadyUsed(DSLParserBaseException):
    def __init__(self, var: str, *args: object) -> None:
        super().__init__(*args)
        self.variable = var

    @property
    def message(self) -> str:
        return f'Variable already used : {self.variable}',


class DSLParserVariableNotDeclared(DSLParserBaseException):
    def __init__(self, var: str, *args: object) -> None:
        super().__init__(*args)
        self.variable = var

    @property
    def message(self) -> str:
        return f'Variable not declared : {self.variable}',
