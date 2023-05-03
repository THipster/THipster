from abc import ABC, abstractmethod
from engine.ResourceModel import ResourceModel


class I_Repository(ABC):

    @abstractmethod
    def get(self, resourceNames: list[str]) -> list[ResourceModel]:
        pass
