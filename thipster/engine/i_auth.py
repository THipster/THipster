"""Authentification module interface."""
from abc import ABC, abstractmethod


class AuthPort(ABC):
    """Authentification port."""

    @abstractmethod
    def authenticate(self):
        """Abstract method used for authentication.

        Raises
        ------
        NotImplementedError
            If method is not implemented in inheriting classes

        """
        msg = 'Should implement authenticate()'
        raise NotImplementedError(msg)
