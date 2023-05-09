"""parsedFile.py Module
"""

from abc import ABC, abstractmethod


class I_ParsedValue(ABC):
    """Parsed Value Interface

    Attributes
    ----------
    value
    """

    @property
    @abstractmethod
    def value(self):
        """Abstract value attribute
        """

        pass


class Position():
    """Class representing the position of a token

    Indicates the initial position of a token, resource or character in the input files.
    It includes the file name, line and column numbers of the designated element.

    Attributes
    ----------
    fileName
    ln
    col
    """

    def __init__(self, fileName: str, ln: int, col: int):
        """
        Parameters
        ----------
        fileName : str
            File name
        ln : int
            Line number
        col : int
            Column number
        """

        self.__fileName = fileName
        self.__ln = ln
        self.__col = col

    @property
    def fileName(self):
        """Name of the file
        """

        return self.__fileName

    @property
    def ln(self):
        """Line number of the token
        """

        return self.__ln

    @property
    def col(self):
        """Column number of the token
        """

        return self.__col

    def __str__(self) -> str:
        """Returns a string of the position object

        Returns
        -------
        str
            Displays the filename, line and column
        """

        return f'(File : {self.fileName}, Ln {self.ln}, Col {self.col})'

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
                self.fileName == __value.fileName and
                self.ln == __value.ln and
                self.col == __value.col
            )
        else:
            raise TypeError('Value must be a Position')


class ParsedAttribute():
    """Class reprensenting a Parsed Attribute Object
    """

    def __init__(self, name: str, position: Position, value: I_ParsedValue):
        """
        Parameters
        ----------
        name : str
        position : Position
        value : I_parsed_Value
        """

        self.__name = name
        self.__position = position
        self.__value = value

    @property
    def value(self):
        """Value of the parsed attribute
        """

        return self.__value.value

    @property
    def name(self):
        """Name of the parsed attribute
        """

        return self.__name

    @property
    def position(self):
        """Position of the parsed attribute
        """

        return self.__position


class ParsedList(I_ParsedValue):
    """Class representing a Parsed List Object
    """

    def __init__(self, value: list[I_ParsedValue]):
        """
        Parameters
        ----------
        value : list[I_Parsed_Value]
        """

        super().__init__()
        self.__value = value

    @property
    def value(self):
        """Value of the parsed list
        """

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
    """Class representing a Parsed Literal Object
    """

    def __init__(self, value: bool | int | float):
        """
        Parameters
        ----------
        value : Literal
        """

        super().__init__()
        self.__value = value

    @property
    def value(self):
        """Value of the Parsed literal
        """

        return self.__value


class ParsedDict(I_ParsedValue):
    """Class representing a Parsed Dictionnary Object
    """

    def __init__(self, value: list[ParsedAttribute]):
        """
        Parameters
        ----------
        value : list[Parsed_Attribute]
        """

        super().__init__()
        self.__value = value

    @property
    def value(self):
        """Value of the Parsed Dictionary
        """

        return self.__value


class ParsedResource():
    """Class representing a Parsed Resource
    """

    def __init__(
            self,
            type: str,
            name: str,
            position: Position,
            attributes=list[ParsedAttribute],
    ):
        """
        Parameters
        ----------
        type : str
        name : str
        position : Position
        attributes : list[Parsed_Attribute]
        """

        self.__type = type
        self.__name = name
        self.__position = position
        self.__attributes = attributes

    @property
    def type(self):
        """Type of the Parsed Resource
        """

        return self.__type

    @property
    def name(self):
        """Name of the Parsed Resource
        """

        return self.__name

    @property
    def position(self):
        """Position of the Parsed Resource in its origin file
        """

        return self.__position

    @property
    def attributes(self) -> list[ParsedAttribute]:
        """List of Attributes of the Parsed Resource
        """

        return self.__attributes


class ParsedFile():
    """Class representing a Parsed File

    Object containing a list of parsed resources making up a file.

    """

    def __init__(self):
        self.__resources = []

    @property
    def resources(self) -> list[ParsedResource]:
        """List of the resources defined in the Parsed File
        """

        return self.__resources

    @resources.setter
    def resources(self, resources):
        """Set the resources list
        """

        self.__resources = resources
