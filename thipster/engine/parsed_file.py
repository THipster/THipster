"""parsedFile.py Module."""

from abc import ABC


class ParsedValue(ABC):
    """Parsed Value Interface."""

    pass


class Position():
    """Class representing the position of a token.

    Indicates the initial position of a token, resource or character in the input files.
    It includes the file name, line and column numbers of the designated element.
    """

    def __init__(self, filename: str, ln: int, col: int):
        """Class representing the position of a token.

        Indicates the initial position of a token, resource or character in the input
        files.
        It includes the file name, line and column numbers of the designated element.

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
        """Return a string of the position object.

        Returns
        -------
        str
            (File : {}, Ln {}, Col {})
        """
        return f'(File : {self.filename}, Ln {self.ln}, Col {self.col})'

    def __eq__(self, __value: object) -> bool:
        """Check if 2 positions are equal.

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
        if not isinstance(__value, Position):
            msg = 'Value must be a Position'
            raise TypeError(msg)

        return (
            self.filename == __value.filename and
            self.ln == __value.ln and
            self.col == __value.col
        )


class ParsedAttribute():
    """Class reprensenting a Parsed Attribute Object."""

    def __init__(self, name: str, position: Position | None, value: ParsedValue):
        """
        Initialize a ParsedAttribute object.

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
        """Value of the parsed attribute."""
        return self.__value.value


class ParsedList(ParsedValue):
    """Class representing a Parsed List Object."""

    def __init__(self, value: list[ParsedValue]):
        """
        Initialize a ParsedList object.

        Parameters
        ----------
        value : list[ParsedValue]
        """
        super().__init__()
        self.value: list[ParsedValue] = value

    def __iter__(self):
        """Return an iterator object."""
        self.i = 0
        return self

    def __next__(self):
        """Return the next value of the iterator."""
        if self.i > len(self.__value):
            raise StopIteration

        self.i += 1
        return self.value[self.i-1]


class ParsedLiteral(ParsedValue):
    """Class representing a Parsed Literal Object."""

    def __init__(self, value: bool | int | float | str):
        """
        Initialize a ParsedLiteral object.

        Parameters
        ----------
        value : Literal
        """
        super().__init__()
        self.value: bool | int | float | str = value


class ParsedDict(ParsedValue):
    """Class representing a Parsed Dictionnary Object."""

    def __init__(self, value: list[ParsedAttribute]):
        """
        Initialize a ParsedDict object.

        Parameters
        ----------
        value : list[ParsedAttribute]
        """
        super().__init__()
        self.value: list[ParsedAttribute] = value


class ParsedResource():
    """Class representing a Parsed Resource."""

    def __init__(
            self,
            parsed_resource_type: str,
            name: str,
            position: Position | None,
            attributes: list[ParsedAttribute],
    ):
        """
        Initialize a ParsedResource object.

        Parameters
        ----------
        parsed_resource_type : str
        name : str
            name of the resource
        position : Position
            position of the resource in its origin file
        attributes : list[ParsedAttribute]
            list of attributes of the resource
        """
        self.resource_type: str = parsed_resource_type
        self.name: str = name
        self.position: Position | None = position
        self.attributes: list[ParsedAttribute] = attributes


class ParsedFile():
    """Class representing a Parsed File.

    Object containing a list of parsed resources making up a file.

    """

    def __init__(self):
        self.resources: list[ParsedResource] = []
