from abc import ABC, abstractmethod

import thipster.engine.parsed_file as pf
import thipster.engine.resource_model as rm


class I_Terraform(ABC):
    """Terraform module interface
    """
    @abstractmethod
    def apply(self):
        """Apply generated terraform code

        Raises
        ------
        NotImplementedError
            If method is not implemented in inheriting classes

        """
        raise NotImplementedError('Should implement apply()')

    @abstractmethod
    def generate(self, file: pf.ParsedFile, models: dict[str, rm.ResourceModel]):
        """Generates Terraform code from parsed file and models

        Raises
        ------
        NotImplementedError
            If method is not implemented in inheriting classes

        """
        raise NotImplementedError('Should implement generate()')

    @abstractmethod
    def init(self):
        """Init Terraform for generated terraform code

        Raises
        ------
        NotImplementedError
            If method is not implemented in inheriting classes

        """
        raise NotImplementedError('Should implement generate()')

    @abstractmethod
    def plan(self):
        """Get plan from generated terraform code

        Raises
        ------
        NotImplementedError
            If method is not implemented in inheriting classes

        """
        raise NotImplementedError('Should implement plan()')
