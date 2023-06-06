from .token import TOKENTYPES as TT
from .token import Token


class DSLParserBaseException(Exception):
    def __init__(self, message, *args: object) -> None:
        super().__init__(*args)

        self.__message = message

    @property
    def message(self):
        return self.__message


class DSLParserPathNotFound(DSLParserBaseException):
    def __init__(self, file, *args: object) -> None:
        super().__init__(f'Path not found : {file}', *args)


class DSLSyntaxException(Exception):
    def __init__(self, token: Token, expected: TT | list[TT], *args: object) -> None:
        super().__init__(*args)
        self.__tok = token
        self.__exp = expected

    def __repr__(self) -> str:

        if type(self.__exp) is TT:
            return f"""{str(self.__tok.position)} :\n\tSyntax error : Expected \
{str(self.__exp.value)}, got {str(self.__tok.tokenType)}"""
        else:
            return f"""{str(self.__tok.position)} :\n\tSyntax error : Expected \
{str(' or '.join(list(map(lambda x : str(x), self.__exp))))}, got {
    str(self.__tok.tokenType)}"""

    @property
    def tok(self):
        return self.__tok


class DSLConditionException(Exception):
    def __init__(self, token: Token, *args: object) -> None:
        super().__init__(*args)
        self.__tok = token

    def __repr__(self) -> str:
        return f"""{str(self.__tok.position)} :\n\tBad condition"""


class DSLUnexpectedEOF(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

    def __repr__(self) -> str:
        return 'Unexpected EOF'


class DSLParserNoEndingQuotes(DSLParserBaseException):
    def __init__(self, position, *args: object) -> None:
        super().__init__(
            f'Invalid syntax, missing ending quotes at : {position}', *args,
        )
