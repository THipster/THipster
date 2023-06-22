"""Exceptions for the THipster parser module."""
from thipster.engine import THipsterError


class ParserPathNotFoundError(THipsterError):
    """Exception raised when the parser cannot find the path."""

    def __init__(self, path: str, *args: object) -> None:
        """Exception raised when the parser cannot find the path.

        Parameters
        ----------
        path : str
            The path that was not found.
        """
        super().__init__(*args)

        self.__path = path

    @property
    def message(self) -> str:
        """Return the exception message."""
        return f'Path not found : {self.__path}'


class NoFileFoundError(THipsterError):
    """Exception raised when the parser cannot find any files to parse."""

    def __init__(self, path: str, *args: object) -> None:
        """Exception raised when the parser cannot find any files to parse.

        Parameters
        ----------
        path : str
            The path where no files were found.
        """
        super().__init__(*args)

        self.__path = path

    @property
    def message(self) -> str:
        """Return the exception message."""
        return f'No files to parse in {self.__path}'
