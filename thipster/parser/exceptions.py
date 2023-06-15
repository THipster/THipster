from thipster.engine import THipsterError


class ParserPathNotFoundError(THipsterError):
    def __init__(self, path, *args: object) -> None:
        super().__init__(*args)

        self.__path = path

    @property
    def message(self) -> str:
        return f'Path not found : {self.__path}'


class NoFileFoundError(THipsterError):
    def __init__(self, path, *args: object) -> None:
        super().__init__(*args)

        self.__path = path

    @property
    def message(self) -> str:
        return f'No files to parse in {self.__path}'
