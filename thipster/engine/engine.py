"""Engine.py module."""
from pathlib import Path

import thipster.engine.parsed_file as pf

from .exceptions import BadPortError
from .i_auth import AuthPort
from .i_parser import ParserPort
from .i_repository import RepositoryPort
from .i_terraform import TerraformPort
from .resource_model import ResourceModel

terraform_plan_file = 'thipster.tfplan'


class Engine:
    """THipster's Engine.

    The core of the application, it is used to call and link all
    interfaces together.
    """

    def __init__(
            self, parser: ParserPort = None,
            repository: RepositoryPort = None,
            auth: AuthPort = None,
            terraform:  TerraformPort = None,
    ):
        """THipster's Engine.

        The core of the application, it is used to call and link all
        interfaces together.

        Parameters
        ----------
        parser : ParserPort
            Instance of a Parser class
        repository : RepositoryPort
            Instance of a Respository class
        auth : AuthPort
            Instance of an Auth class
        terraform : TerraformPort
            Instance of a Terraform class
        """
        self.parser = parser
        self.repository = repository
        self.auth = auth
        self.terraform = terraform

    @property
    def parser(self):
        """Get the parser."""
        if self.__parser:
            return self.__parser
        raise NotImplementedError

    @parser.setter
    def parser(self, value):
        if not isinstance(value, ParserPort):
            raise BadPortError(value.__class__, ParserPort)

        self.__parser = value

    @property
    def repository(self):
        """Get the repository."""
        if self.__repository:
            return self.__repository
        raise NotImplementedError

    @repository.setter
    def repository(self, value):
        if not isinstance(value, RepositoryPort):
            raise BadPortError(value.__class__, RepositoryPort)

        self.__repository = value

    @property
    def auth(self):
        """Get the authentification module."""
        if self.__auth:
            return self.__auth
        raise NotImplementedError

    @auth.setter
    def auth(self, value):
        if not isinstance(value, AuthPort):
            raise BadPortError(value.__class__, AuthPort)

        self.__auth = value

    @property
    def terraform(self):
        """Get the Terraform module."""
        if self.__terraform:
            return self.__terraform
        raise NotImplementedError

    @terraform.setter
    def terraform(self, value):
        if not isinstance(value, TerraformPort):
            raise BadPortError(value.__class__, TerraformPort)

        self.__terraform = value

    def run(self, path: str) -> str:
        """Return json Terraform files from the input file name.

        Calls the different run methods of the parser, repository,
        auth and terraform modules.
        Transforms the inputed filename into a Cloud architecture plan.

        Parameters
        ----------
        path : str
            The path of the files to be processed

        Returns
        -------
        str
            A string with the results of the Terraform plan
        """
        # Parse file or directory
        parsed_file = self.parse_files(path)

        # Get needed models
        models = self.get_models(parsed_file)

        # Generate Terraform files
        self.generate_tf_files(parsed_file, models)

        self.init_terraform()

        terraform_plan = self.plan_terraform(
            plan_file_path=terraform_plan_file,
        )

        if not terraform_plan:
            return ''

        return terraform_plan[1]

    def parse_files(self, path: str) -> pf.ParsedFile:
        """Parse the input file or directory.

        Parameters
        ----------
        path : str
            The path of the files to be processed

        Returns
        -------
        pf.ParsedFile
            The ParsedFile object containing the resources defined in the input file
        """
        parsed_file = self.parser.run(path)
        assert type(parsed_file) == pf.ParsedFile

        return parsed_file

    def get_models(
        self, file: pf.ParsedFile,
    ) -> dict[str, ResourceModel]:
        """Get the models from the repository.

        Parameters
        ----------
        file : pf.ParsedFile
            The ParsedFile object containing the resources defined in the input file

        Returns
        -------
        dict[str, ResourceModel]
            The dictionary of models
        """
        types = [r.resource_type for r in file.resources]
        return self.repository.get(types)

    def generate_tf_files(
        self, file: pf.ParsedFile, models: dict[str, ResourceModel],
    ) -> None:
        """Generate Terraform files.

        Parameters
        ----------
        file : pf.ParsedFile
            The ParsedFile object containing the resources defined in the input file
        models : dict[str, ResourceModel]
            The dictionary of models
        """
        self.terraform.generate(file, models, self.__auth)

    def init_terraform(
        self,
        working_dir: Path = Path.cwd(),
        upgrade: bool = False,
    ) -> tuple[int, str]:
        """Initialize Terraform.

        Parameters
        ----------
        working_dir : Path, optional
            The path of the working directory, by default Path.cwd()
        upgrade : bool, optional
            Whether to upgrade the Terraform providers, by default False

        Returns
        -------
        tuple[int, str]
            The terraform init exit code and output
        """
        return self.terraform.init(working_dir, upgrade)

    def plan_terraform(
        self,
        working_dir: Path = Path.cwd(),
        plan_file_path: str = terraform_plan_file,
    ) -> tuple[int, str]:
        """Plan Terraform.

        Parameters
        ----------
        working_dir : Path, optional
            The path of the working directory, by default Path.cwd()
        plan_file_path : str, optional
            The path of the plan file, by default thipster.tfplan

        Returns
        -------
        tuple[int, str]
            The terraform plan exit code and output
        """
        return self.terraform.plan(working_dir, plan_file_path)

    def apply_terraform(
        self,
        working_dir: Path = Path.cwd(),
        plan_file_path: str = terraform_plan_file,
    ) -> tuple[int, str]:
        """Apply Terraform.

        Parameters
        ----------
        working_dir : Path, optional
            The path of the working directory, by default Path.cwd()
        plan_file_path : str, optional
            The path of the plan file, by default thipster.tfplan

        Returns
        -------
        tuple[int, str]
            The terraform apply exit code and output
        """
        return self.terraform.apply(working_dir, plan_file_path)
