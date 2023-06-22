"""Parser module interface."""
from abc import ABC, abstractclassmethod

from thipster.engine.parsed_file import ParsedFile


class ParserPort(ABC):
    """Parser port."""

    @classmethod
    @abstractclassmethod
    def run(
        cls,
        path: str,  # noqa: ARG003
    ) -> ParsedFile:
        """Abstract run method.

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
        msg = 'Should implement run()'
        raise NotImplementedError(msg)
