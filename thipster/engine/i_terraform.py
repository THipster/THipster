from abc import ABC, abstractclassmethod

import thipster.engine.parsed_file as pf
import thipster.engine.resource_model as rm

from .i_auth import AuthPort


class TerraformPort(ABC):
    """Terraform module interface
    """
    @classmethod
    @abstractclassmethod
    def apply(cls, plan_file_path: str | None = None):
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

    @classmethod
    @abstractclassmethod
    def generate(
        cls, file: pf.ParsedFile, models: dict[str, rm.ResourceModel],
        _authenticator: AuthPort,
    ):
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

    @classmethod
    @abstractclassmethod
    def init(cls):
        """Init Terraform for generated terraform code

        Raises
        ------
        NotImplementedError
            If method is not implemented in inheriting classes

        """
        raise NotImplementedError('Should implement generate()')

    @classmethod
    @abstractclassmethod
    def plan(cls):
        """Get plan from generated terraform code

        Raises
        ------
        NotImplementedError
            If method is not implemented in inheriting classes

        """
        raise NotImplementedError('Should implement plan()')
