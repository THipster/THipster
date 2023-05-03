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
