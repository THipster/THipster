from thipster.engine.parsed_file import Position


class LexerPosition():
    def __init__(
        self,
        fileName: str = '',
        startLine: int = 1,
        startColumn: int = 1,
    ) -> None:
        """Class to represent the state and position of the lexer

        Parameters
        ----------
        fileName : str
            Name of the current file
        startLine : int, optional
            Starting line in the current file, by default 1
        startColumn : int, optional
            Starting column in the current file, by default 1
        """
        self.__currentFile = fileName
        self.__currentLine = startLine
        self.__currentColumn = startColumn
        self.__currentToken = ''
        self.__currentTokenIndex = startColumn
        self.__currentTokenLine = startColumn
        self.__isVariable = False
        self.__isQuotedString = False
        self.__isMultiLine = False
        self.__consecutiveWhitespaces = 0

    @property
    def currentFile(self):
        return self.__currentFile

    @property
    def currentLine(self):
        return self.__currentLine

    @property
    def currentColumn(self):
        return self.__currentColumn

    @property
    def currentToken(self):
        return self.__currentToken

    @property
    def currentTokenIndex(self):
        return self.__currentTokenIndex

    @property
    def isCurrentTokenAVariable(self):
        return self.__isVariable

    @property
    def isCurrentTokenMultiLine(self):
        return self.__isMultiLine

    @property
    def isQuotedString(self):
        return self.__isQuotedString

    @isQuotedString.setter
    def isQuotedString(self, value):
        self.__isQuotedString = value

    @property
    def consecutiveWhitespaces(self):
        return self.__consecutiveWhitespaces

    @property
    def currentCharPosition(self) -> Position:
        return Position(
            self.__currentFile,
            self.__currentLine,
            self.__currentColumn,
        )

    @property
    def currentTokenPosition(self) -> Position:
        return Position(
            self.__currentFile,
            self.__currentTokenLine,
            self.__currentTokenIndex,
        )

    def newLine(self) -> None:
        """Get the position to the next line
        """
        self.__currentLine += 1
        self.__currentColumn = 1

    def nextColumn(self, step: int = 1) -> None:
        """Get the position to a new column

        Parameters
        ----------
        step : int
            Step to modify the current column, by default 1
        """
        if (self.__currentColumn + step) > 0:
            self.__currentColumn += step
        else:
            self.__currentColumn = 0  # Raise exception ?

    def addCharToCurrentToken(self, char) -> None:
        """Add a char to the current stored token

        Parameters
        ----------
        char : _type_
            Char to add to the token
        """
        self.__currentToken += char

    def setCurrentTokenIndex(self, newIndex: int | None = None) -> None:
        """Modify the stored token index

        Parameters
        ----------
        newIndex : int, optional
            New index of the stored token, by default None
        """
        if newIndex:
            self.__currentTokenIndex = newIndex
        else:
            self.__currentTokenIndex = self.__currentColumn
            self.__currentTokenLine = self.__currentLine

    def resetCurrentToken(self, newIndex: int | None = None) -> None:
        """Reset the current stored token and its index

        Parameters
        ----------
        newIndex : int, optional
            New index of the stored token, by default None
        """
        self.__currentToken = ''
        self.setCurrentTokenIndex(newIndex)

    def addConsecutiveWhitespace(self) -> None:
        """Add a consecutive whitespace to the lexer state
        """
        self.__consecutiveWhitespaces += 1

    def resetConsecutiveWhitespaces(self) -> None:
        """Reset consecutive whitespaces of the lexer state to 0
        """
        self.__consecutiveWhitespaces = 0

    def setIsVariable(self, value: bool = False) -> None:
        """Set the current stored token as a variable

        Parameters
        ----------
        value : bool, optional
            Is the stored token a variable True or False, by default False
        """
        self.__isVariable = value

    def setIsMultiLine(self, value: bool = False) -> None:
        """Set the current token as a multi-line input

        Parameters
        ----------
        value : bool, optional
            Is the current token a multi-line input True or False, by default False
        """
        self.__isMultiLine = value
