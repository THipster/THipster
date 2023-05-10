from abc import ABC, abstractmethod


class I_Auth(ABC):
    """Authentification module interface

    Methods
    -------
    run()
        Abstract run method

    """
    @abstractmethod
    def run(self):
        """Abstract run method

        Raises
        ------
        NotImplementedError
            If method is not implemented in inheriting classes

        """
        raise NotImplementedError('Should implement run()')
