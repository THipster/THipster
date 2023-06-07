from abc import ABC, abstractmethod

import thipster.engine.parsed_file as pf
import thipster.engine.resource_model as rm


class I_Terraform(ABC):
    """Terraform module interface
    """
    @abstractmethod
    def apply(self, plan_file_path: str | None = None):
        """Apply generated terraform code

        Parameters
        ----------
        plan_file_path : str, optional
            Path to plan file, by default None

        Raises
        ------
        NotImplementedError
            If method is not implemented in inheriting classes

        """
        raise NotImplementedError('Should implement apply()')

    @abstractmethod
    def generate(self, file: pf.ParsedFile, models: dict[str, rm.ResourceModel]):
        """Generates Terraform code from parsed file and models

        Parameters
        ----------
        file : pf.ParsedFile
            The ParsedFile object containing the resources defined in the input file
        models : dict[str, rm.ResourceModel]
            The dictionary of models

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
