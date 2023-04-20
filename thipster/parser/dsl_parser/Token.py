from engine.ParsedFile import Position

class Token():
    def __init__(self, position:Position, type:str, value:str):
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
