from abc import ABC, abstractmethod


class I_Auth(ABC):
    """Authentification module interface
    """
    @property
    @abstractmethod
    def description(self) -> str:
        """Abstract property used for help

        Raises
        ------
        NotImplementedError
            If property is not implemented in inheriting classes

        """
        raise NotImplementedError('Should have a description')

    @property
    @abstractmethod
    def help(self) -> str:
        """Abstract property used for help

        Raises
        ------
        NotImplementedError
            If property is not implemented in inheriting classes

        """
        raise NotImplementedError('Should have a help section')

    @abstractmethod
    def authenticate(self):
        """Abstract method used for authentication

        Raises
        ------
        NotImplementedError
            If method is not implemented in inheriting classes

        """
        raise NotImplementedError('Should implement authenticate()')
