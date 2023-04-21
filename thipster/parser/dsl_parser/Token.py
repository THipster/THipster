from engine.ParsedFile import Position


class Token():
    def __init__(self, position: Position, type: str, value: str = None):
        self.__position = position
        self.__type = type
        self.__value = value

    @property
    def position(self):
        return self.__position

    @property
    def type(self):
        return self.__type

    @property
    def value(self):
        return self.__value

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, Token):
            return (
                self.position == __value.position and
                self.type == __value.type and
                self.value == __value.value
            )
        else:
            raise TypeError('Value must be a Token')
