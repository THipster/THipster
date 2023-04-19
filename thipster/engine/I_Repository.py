from abc import ABC, abstractmethod


class I_Repository(ABC):

    @abstractmethod
    def run(self):
        pass
