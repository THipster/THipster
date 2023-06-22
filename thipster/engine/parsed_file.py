"""parsedFile.py Module."""

from abc import ABC


class ParsedValue(ABC):
    """Parsed Value Interface."""

    pass


class Position():
    """Represents the position of a token.

    Indicates the initial position of a token, resource or character in the input files.
    It includes the file name, line and column numbers of the designated element.
    """

    def __init__(self, filename: str, ln: int, col: int):
        """Represent the position of a token.

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
    """Reprensents a Parsed Attribute Object."""

    def __init__(self, name: str, position: Position | None, value: ParsedValue):
        """
        Represent a Parsed Attribute Object.

        Parameters
        ----------
        name : str
            name of the attribute
        position : Position | None
            position of the attribute in its origin file
        value : ParsedValue
            value of the attribute
        """
        self.name: str = name
        self.position: Position | None = position
        self.__value = value

    @property
    def value(self):
        """Value of the parsed attribute."""
        return self.__value.value


class ParsedList(ParsedValue):
    """Represents a Parsed List Object."""

    def __init__(self, value: list[ParsedValue]):
        """
        Represent a Parsed List Object.

        Parameters
        ----------
        value : list[ParsedValue]
            value of the parsed list
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
    """Represents a Parsed Literal Object."""

    def __init__(self, value: bool | int | float | str):
        """
        Represent a Parsed Literal Object.

        Parameters
        ----------
        value : Literal
            value of the parsed literal
        """
        super().__init__()
        self.value: bool | int | float | str = value


class ParsedDict(ParsedValue):
    """Represents a Parsed Dictionnary Object."""

    def __init__(self, value: list[ParsedAttribute]):
        """
        Represent a Parsed Dictionnary Object.

        Parameters
        ----------
        value : list[ParsedAttribute]
            value of the parsed dictionnary
        """
        super().__init__()
        self.value: list[ParsedAttribute] = value


class ParsedResource():
    """Represents a Parsed Resource."""

    def __init__(
            self,
            parsed_resource_type: str,
            name: str,
            position: Position | None,
            attributes: list[ParsedAttribute],
    ):
        """
        Represent a Parsed Resource.

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
    """Represents a Parsed File.

    Object containing a list of parsed resources making up a file.
    """

    def __init__(self):
        """Represent a Parsed File."""
        self.resources: list[ParsedResource] = []
