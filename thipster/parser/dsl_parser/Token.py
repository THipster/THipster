from engine.ParsedFile import Position
from enum import Enum


class TOKENTYPES(Enum):
    AMOUNT = 'AMOUNT'
    BOOLEAN = 'BOOLEAN'
    COLUMN = 'COLUMN'
    DASH = 'DASH'
    ELIF = 'ELIF'
    ELSE = 'ELSE'
    EOF = 'EOF'
    FLOAT = 'FLOAT'
    IF = 'IF'
    INT = 'INT'
    NEWLINE = 'NEWLINE'
    STRING = 'STRING'
    TAB = 'TAB'
    VAR = 'VAR'
    WHITESPACE = 'WHITESPACE'


class Token():
    """Class representing a Token
    """

    def __init__(self, position: Position, tokenType: str, value: str = None):
        """

        Parameters
        ----------
        position : Position
            Position of the token in its input file
        tokenType : str
            Token type
        value : str, optional
            Token value, by default None
        """
        self.__position = position
        self.__tokenType = tokenType
        self.__value = value

    @property
    def position(self):
        return self.__position

    @property
    def tokenType(self):
        return self.__tokenType

    @property
    def value(self):
        return self.__value

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, Token):
            return (
                self.position == __value.position and
                self.tokenType == __value.tokenType and
                self.value == __value.value
            )
        else:
            raise TypeError('Value must be a Token')

    def __repr__(self) -> str:
        tokenString = f'(Type: {self.tokenType.upper()}, Position: {str(self.position)}'
        if self.value:
            tokenString += f', Value: {self.value}'
        tokenString += ')'

        return tokenString

    def __str__(self) -> str:
        return f'({self.tokenType} {self.value})'
