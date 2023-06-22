"""Module to represent the state and position of the lexer."""
from thipster.engine.parsed_file import Position


class LexerPosition():
    """Represents the state and position of the DSL lexer."""

    def __init__(
        self,
        filename: str = '',
    ) -> None:
        """Represent the state and position of the DSL lexer.

        Parameters
        ----------
        filename : str
            Name of the current file
        """
        self.currentFile = filename
        self.currentLine = 1
        self.currentColumn = 1
        self.currentToken = ''
        self.currentTokenIndex = 1
        self.__currentTokenLine = 1
        self.isVariable = False
        self.isQuotedString = False
        self.isMultiLine = False
        self.consecutiveWhitespaces = 0

    @property
    def currentCharPosition(self) -> Position:  # noqa: N802
        """Get the current position of the lexer."""
        return Position(
            self.currentFile,
            self.currentLine,
            self.currentColumn,
        )

    @property
    def currentTokenPosition(self) -> Position:  # noqa: N802
        """Get the position of the current stored token."""
        return Position(
            self.currentFile,
            self.__currentTokenLine,
            self.currentTokenIndex,
        )

    def new_line(self) -> None:
        """Get the position to the next line."""
        self.currentLine += 1
        self.currentColumn = 1

    def next_column(self, step: int = 1) -> None:
        """Get the position to a new column.

        Parameters
        ----------
        step : int
            Step to modify the current column, by default 1
        """
        if (self.currentColumn + step) > 0:
            self.currentColumn += step
        else:
            self.currentColumn = 0  # Raise exception ?

    def add_to_current_token(self, char) -> None:
        """Add a char to the current stored token.

        Parameters
        ----------
        char : _type_
            Char to add to the token
        """
        self.currentToken += char

    def set_current_token_index(self, new_index: int | None = None) -> None:
        """Modify the stored token index.

        Parameters
        ----------
        new_index : int, optional
            New index of the stored token, by default None
        """
        if new_index:
            self.currentTokenIndex = new_index
        else:
            self.currentTokenIndex = self.currentColumn
            self.__currentTokenLine = self.currentLine

    def reset_current_token(self, new_index: int | None = None) -> None:
        """Reset the current stored token and its index.

        Parameters
        ----------
        new_index : int, optional
            New index of the stored token, by default None
        """
        self.currentToken = ''
        self.set_current_token_index(new_index)

    def increment_consecutive_whitespaces(self) -> None:
        """Add a consecutive whitespace to the lexer state."""
        self.consecutiveWhitespaces += 1

    def reset_consecutive_whitespaces(self) -> None:
        """Reset consecutive whitespaces of the lexer state to 0."""
        self.consecutiveWhitespaces = 0
