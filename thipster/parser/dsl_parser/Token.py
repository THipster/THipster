from engine.ParsedFile import Position
from enum import Enum


class TOKENTYPES(Enum):
    AMOUNT = 'AMOUNT'
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


class Token():
    def __init__(self, position: Position, tokenType: str, value: str = None):
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

    def __str__(self) -> str:
        tokenString = f'Position: {str(self.position)}, Type: {self.tokenType}'
        if self.value:
            return tokenString + f', Value: {self.value}'
        else:
            return tokenString
