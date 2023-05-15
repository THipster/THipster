from abc import ABC, abstractmethod
from engine.ParsedFile import ParsedFile


class I_Parser(ABC):
    """Parser module interface

    Methods
    -------
    run()
        Abstract run method

    """
    @abstractmethod
    def run(self, path: str) -> ParsedFile:
        """Abstract run method

        Returns
        -------
        ParsedFile
            Object containing a representation of an input file broken down into
            individual resources

        Raises
        ------
        NotImplementedError
            If method is not implemented in inheriting classes

        """
        raise NotImplementedError('Should implement run()')
