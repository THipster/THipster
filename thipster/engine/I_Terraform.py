from abc import ABC, abstractmethod


class I_Terraform(ABC):

    @abstractmethod
    def run(self):
        pass
