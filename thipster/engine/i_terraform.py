"""Terraform module interface."""
from abc import ABC, abstractclassmethod
from pathlib import Path

import thipster.engine.parsed_file as pf
import thipster.engine.resource_model as rm

from .i_auth import AuthPort


class TerraformPort(ABC):
    """Terraform port."""

    @classmethod
    @abstractclassmethod
    def apply(
        cls,
        working_dir: Path,  # noqa: ARG003
        plan_file_path: str | None = None,  # noqa: ARG003
    ) -> tuple[int, str]:
        """Apply generated terraform code.

        Parameters
        ----------
        working_dir : Path
            Path to the working directory
        plan_file_path : str, optional
            Path to plan file, by default None

        Returns
        -------
        tuple[int, str]
            The Terraform apply exit code and output

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
    def init(cls, working_dir: Path, upgrade: bool):  # noqa: ARG003
        """Init Terraform for generated terraform code.

        Parameters
        ----------
        working_dir : Path
            Path to the working directory
        upgrade : bool
            Whether to upgrade Terraform providers or not

        Raises
        ------
        NotImplementedError
            If method is not implemented in inheriting classes

        """
        msg = 'Should implement generate()'
        raise NotImplementedError(msg)

    @classmethod
    @abstractclassmethod
    def plan(
        cls,
        working_dir: Path,  # noqa: ARG003
        plan_file_path: str,  # noqa: ARG003
    ) -> tuple[int, str]:
        """Get plan from generated terraform code.

        Parameters
        ----------
        working_dir : Path
            Path to the working directory
        plan_file_path : str
            Path and name of the plan file

        Returns
        -------
        tuple[int, str]
            Terraform plan exitcode and output

        Raises
        ------
        NotImplementedError
            If method is not implemented in inheriting classes

        """
        msg = 'Should implement plan()'
        raise NotImplementedError(msg)
