"""Exceptions for the THipster engine."""
from abc import ABC, abstractmethod


class THipsterError(Exception, ABC):
    """Base class for all exceptions raised by THipster."""

    @property
    @abstractmethod
    def message():
        """Get the message of the exception."""
        raise NotImplementedError

    def __str__(self) -> str:
        """Get the string representation of the exception."""
        return self.message


class BadPortError(THipsterError):
    """Exception raised when trying to set a port with an invalid class."""

    def __init__(self, got: type, expected: type, *args: object) -> None:
        """Exception raised when trying to set a port with an invalid class.

        Parameters
        ----------
        var : str
            The variable name.
        """
        super().__init__(*args)
        self.got = got
        self.expected = expected

    @property
    def message(self):
        """Get the message of the exception."""
        return (
            f'Error while setting THipster port : got {self.got.__name__},'
            f' expected {self.expected.__name__}'
        )
