from abc import ABC, abstractmethod


class AuthPort(ABC):
    """Authentification module interface
    """

    @abstractmethod
    def authenticate(self):
        """Abstract method used for authentication

        Raises
        ------
        NotImplementedError
            If method is not implemented in inheriting classes

        """
        raise NotImplementedError('Should implement authenticate()')
