from abc import ABC, abstractmethod


class THipsterError(Exception, ABC):
    @property
    @abstractmethod
    def message():
        raise NotImplementedError

    def __str__(self) -> str:
        return self.message
