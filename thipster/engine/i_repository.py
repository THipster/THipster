from abc import ABC, abstractmethod
from thipster.engine.resource_model import ResourceModel


class I_Repository(ABC):
    """Repository module interface
    """
    @abstractmethod
    def get(self, resourceNames: list[str]) -> dict[str, ResourceModel]:
        """Abstract get method

        Parameters
        ----------
        resourceNames : list[str]
            List of resource names to be retrieved from the repository

        Returns
        -------
        dict[str, ResourceModel]
            Dictionary of ResourceModel objects, indexed by resource name
        """
        pass
