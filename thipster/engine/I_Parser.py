from abc import ABC, abstractmethod
from engine.ParsedFile import ParsedFile


class I_Parser(ABC):

    @abstractmethod
    def run(self) -> ParsedFile:
        pass
