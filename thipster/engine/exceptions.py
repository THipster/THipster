from abc import ABC, abstractmethod


class THipsterException(Exception, ABC):
    @property
    @abstractmethod
    def message():
        raise NotImplementedError()

    @abstractmethod
    def __str__(self) -> str:
        return self.message
