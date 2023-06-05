from abc import ABC, abstractmethod
from thipster.engine.ParsedFile import ParsedFile


class I_Parser(ABC):
    """Parser module interface
    """
    @abstractmethod
    def run(self, path: str) -> ParsedFile:
        """Abstract run method

        Parameters
        ----------
        path : str
            The path of the filesor directory to be processed

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
