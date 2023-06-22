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
