from abc import ABC, abstractmethod


class I_Value(ABC):
    @property
    @abstractmethod
    def value(self):
        pass


class Position():
    def __init__(self, ln: int, col: int):
        self.__ln = ln
        self.__col = col

    @property
    def ln(self):
        return self.__ln

    @property
    def col(self):
        return self.__col

    def __str__(self) -> str:
        return 'Ln ' + self.ln + ', Col ' + self.col


class Attribute():
    def __init__(self, name: str, position: Position, value: I_Value):
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


class Parsed_List(I_Value):
    def __init__(self, value: list[I_Value]):
        super().__init__()
        self.__value = value

    @property
    def value(self):
        return self.__value

    def __iter__(self):
        self.i = 0
        return self

    def __next__(self):
        ret = self.value[self.i]
        if self.i > len(self.__value):
            raise StopIteration
        else:
            self.i += 1

        return ret


class Parsed_Litteral(I_Value):
    def __init__(self, value):
        super().__init__()
        self.__value = value

    @property
    def value(self):
        return self.__value


class Parsed_Dict(I_Value):
    def __init__(self, value: dict[Attribute]):
        super().__init__()
        self.__value = value

    @property
    def value(self):
        return self.__value

    def __iter__(self):
        self.i = 0
        return self

    def __next__(self):
        ret = self.value[self.i]
        if self.i > len(self.__value):
            raise StopIteration
        else:
            self.i += 1

        return ret


class ParsedResource():
    def __init__(
            self,
            type: str,
            name: str,
            position: Position,
            attributes=list[Attribute],
    ):
        self.__type = type
        self.__name = name
        self.__position = position
        self.__attributes = attributes

    @property
    def type(self):
        return self.__type

    @property
    def name(self):
        return self.__name

    @property
    def position(self):
        return self.__position

    @property
    def attributes(self):
        return self.__attributes


class ParsedFile():
    def __init__(self):
        self.__resources = []

    @property
    def resources(self):
        return self.__resources

    @resources.setter
    def resources(self, resources):
        self.__resources = resources
