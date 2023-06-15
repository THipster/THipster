"""parsedFile.py Module
"""

from abc import ABC


class ParsedValue(ABC):
    """Parsed Value Interface
    """

    pass


class Position():
    """Class representing the position of a token

    Indicates the initial position of a token, resource or character in the input files.
    It includes the file name, line and column numbers of the designated element.
    """

    def __init__(self, filename: str, ln: int, col: int):
        """
        Parameters
        ----------
        fileName : str
            file name
        ln : int
            line number
        col : int
            column number
        """

        self.filename = filename
        self.ln = ln
        self.col = col

    def __str__(self) -> str:
        """Returns a string of the position object

        Returns
        -------
        str
            (File : {}, Ln {}, Col {})
        """

        return f'(File : {self.filename}, Ln {self.ln}, Col {self.col})'

    def __eq__(self, __value: object) -> bool:
        """Check if 2 positions are equal

        Parameters
        ----------
        __value : object
            Position to compare

        Returns
        -------
        bool
            True if both positions are equal or False otherwise

        Raises
        ------
        TypeError
            If '__value' is not a Position
        """

        if isinstance(__value, Position):
            return (
                self.filename == __value.filename and
                self.ln == __value.ln and
                self.col == __value.col
            )
        else:
            raise TypeError('Value must be a Position')


class ParsedAttribute():
    """Class reprensenting a Parsed Attribute Object
    """

    def __init__(self, name: str, position: Position | None, value: ParsedValue):
        """
        Parameters
        ----------
        name : str
        position : Position
        value : ParsedValue
        """

        self.name: str = name
        self.position: Position | None = position
        self.__value = value

    @property
    def value(self):
        """Value of the parsed attribute
        """

        return self.__value.value


class ParsedList(ParsedValue):
    """Class representing a Parsed List Object
    """

    def __init__(self, value: list[ParsedValue]):
        """
        Parameters
        ----------
        value : list[ParsedValue]
        """

        super().__init__()
        self.value: list[ParsedValue] = value

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


class ParsedLiteral(ParsedValue):
    """Class representing a Parsed Literal Object
    """

    def __init__(self, value: bool | int | float | str):
        """
        Parameters
        ----------
        value : Literal
        """

        super().__init__()
        self.value: bool | int | float | str = value


class ParsedDict(ParsedValue):
    """Class representing a Parsed Dictionnary Object
    """

    def __init__(self, value: list[ParsedAttribute]):
        """
        Parameters
        ----------
        value : list[ParsedAttribute]
        """

        super().__init__()
        self.value: list[ParsedAttribute] = value


class ParsedResource():
    """Class representing a Parsed Resource
    """

    def __init__(
            self,
            type: str,
            name: str,
            position: Position | None,
            attributes: list[ParsedAttribute],
    ):
        """
        Parameters
        ----------
        type : str
        name : str
            name of the resource
        position : Position
            position of the resource in its origin file
        attributes : list[ParsedAttribute]
            list of attributes of the resource
        """

        self.resource_type: str = type
        self.name: str = name
        self.position: Position | None = position
        self.attributes: list[ParsedAttribute] = attributes


class ParsedFile():
    """Class representing a Parsed File

    Object containing a list of parsed resources making up a file.

    """

    def __init__(self):
        self.resources: list[ParsedResource] = []
