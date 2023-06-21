"""Repository module interface."""
from abc import ABC, abstractmethod

from thipster.engine.resource_model import ResourceModel


class RepositoryPort(ABC):
    """Repository port."""

    @abstractmethod
    def get(self, resource_names: list[str]) -> dict[str, ResourceModel]:
        """Abstract get method.

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
