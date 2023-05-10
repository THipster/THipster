from abc import ABC, abstractmethod
from engine.ResourceModel import ResourceModel


class I_Repository(ABC):
    """Repository module interface

    Methods
    -------
    get()
        Abstract get method

    """
    @abstractmethod
    def get(self, resourceNames: list[str]) -> dict[str, ResourceModel]:
        pass
