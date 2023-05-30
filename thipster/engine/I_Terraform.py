from abc import ABC, abstractmethod
import thipster.engine.ResourceModel as rm
import thipster.engine.ParsedFile as pf


class I_Terraform(ABC):
    """Terraform module interface

    Methods
    -------
    generate()
        Generates Terraform code from parsed file and models
    plan()
        Get plan from generated terraform code
    apply()
        Apply generated terraform code

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
