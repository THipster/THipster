from abc import ABC, abstractmethod


class I_Auth(ABC):

    @abstractmethod
    def run(self):
        pass
