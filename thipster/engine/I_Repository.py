from abc import ABC, abstractmethod
from engine.ResourceModel import ResourceModel


class I_Repository(ABC):

    @abstractmethod
    def run(self) -> list[ResourceModel]:
        pass
