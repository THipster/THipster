from abc import ABC, abstractclassmethod

from thipster.engine.parsed_file import ParsedFile


class ParserPort(ABC):
    """Parser module interface
    """
    @classmethod
    @abstractclassmethod
    def run(cls, path: str) -> ParsedFile:
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
