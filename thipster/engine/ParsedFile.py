from abc import ABC, abstractmethod


class I_ParsedValue(ABC):
    @property
    @abstractmethod
    def value(self):
        pass


class Position():
    def __init__(self, fileName: str, ln: int, col: int):
        self.__fileName = fileName
        self.__ln = ln
        self.__col = col

    @property
    def fileName(self):
        return self.__fileName

    @property
    def ln(self):
        return self.__ln

    @property
    def col(self):
        return self.__col

    def __str__(self) -> str:
        return f'(File : {self.fileName}, Ln {self.ln}, Col {self.col})'

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, Position):
            return (
                self.fileName == __value.fileName and
                self.ln == __value.ln and
                self.col == __value.col
            )
        else:
            raise TypeError('Value must be a Position')


class ParsedAttribute():
    def __init__(self, name: str, position: Position, value: I_ParsedValue):
        self.__name = name
        self.__position = position
        self.__value = value

    @property
    def value(self):
        return self.__value.value

    @property
    def name(self):
        return self.__name

    @property
    def position(self):
        return self.__position


class ParsedList(I_ParsedValue):
    def __init__(self, value: list[I_ParsedValue]):
        super().__init__()
        self.__value = value

    @property
    def value(self):
        return self.__value

    def __iter__(self):
        self.i = 0
        return self

    def __next__(self):
        if self.i > len(self.__value):
            raise StopIteration
        else:
            ret = self.value[self.i]
            self.i += 1

        return ret


class ParsedLiteral(I_ParsedValue):
    def __init__(self, value):
        super().__init__()
        self.__value = value

    @property
    def value(self):
        return self.__value


class ParsedDict(I_ParsedValue):
    def __init__(self, value: list[ParsedAttribute]):
        super().__init__()
        self.__value = value

    @property
    def value(self):
        return self.__value


class ParsedResource():
    def __init__(
            self,
            type: str,
            name: str,
            position: Position,
            attributes=list[ParsedAttribute],
    ):
        self.__type = type
        self.__name = name
        self.__position = position
        self.__attributes = attributes

    @property
    def type(self) -> str:
        return self.__type

    @property
    def name(self) -> str:
        return self.__name

    @property
    def position(self) -> Position:
        return self.__position

    @property
    def attributes(self) -> list[ParsedAttribute]:
        return self.__attributes


class ParsedFile():
    def __init__(self):
        self.__resources = []

    @property
    def resources(self) -> list[ParsedResource]:
        return self.__resources

    @resources.setter
    def resources(self, resources):
        self.__resources = resources
