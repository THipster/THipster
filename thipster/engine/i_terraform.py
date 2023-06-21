"""Terraform module interface."""
from abc import ABC, abstractclassmethod

import thipster.engine.parsed_file as pf
import thipster.engine.resource_model as rm

from .i_auth import AuthPort


class TerraformPort(ABC):
    """Terraform port."""

    @classmethod
    @abstractclassmethod
    def apply(
        cls,
        plan_file_path: str | None = None,  # noqa: ARG003
    ):
        """Apply generated terraform code.

        Parameters
        ----------
        plan_file_path : str, optional
            Path to plan file, by default None

        Raises
        ------
        NotImplementedError
            If method is not implemented in inheriting classes

        """
        msg = 'Should implement apply()'
        raise NotImplementedError(msg)

    @classmethod
    @abstractclassmethod
    def generate(
        cls,
        file: pf.ParsedFile,  # noqa: ARG003
        models: dict[str, rm.ResourceModel],  # noqa: ARG003
        _authenticator: AuthPort,
    ):
        """Generate Terraform code from parsed file and models.

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
        msg = 'Should implement generate()'
        raise NotImplementedError(msg)

    @classmethod
    @abstractclassmethod
    def init(cls):
        """Init Terraform for generated terraform code.

        Raises
        ------
        NotImplementedError
            If method is not implemented in inheriting classes

        """
        msg = 'Should implement generate()'
        raise NotImplementedError(msg)

    @classmethod
    @abstractclassmethod
    def plan(cls):
        """Get plan from generated terraform code.

        Raises
        ------
        NotImplementedError
            If method is not implemented in inheriting classes

        """
        msg = 'Should implement plan()'
        raise NotImplementedError(msg)
