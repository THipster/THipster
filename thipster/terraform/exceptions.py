"""Exceptions for the Terraform CDK module."""
from thipster.engine import THipsterError


class CDKError(THipsterError):
    """Shared base Exception for the Terraform CDK module."""

    pass


class CDKInvalidAttributeError(CDKError):
    """Exception raised when an attribute is invalid."""

    def __init__(self, attr: str, model_type: str, **args: object) -> None:
        """Exception raised when an attribute is invalid.

        Parameters
        ----------
        attr: str
            The attribute that is invalid
        model_type: str
            The model type that contains the attribute
        """
        super().__init__(*args)
        self.__attr = attr
        self.__modelType = model_type

    @property
    def message(self) -> str:
        """Return the exception message."""
        return f'{self.__attr} in {self.__modelType} but not useful'


class CDKMissingAttributeError(CDKError):
    """Exception raised when an attribute is missing."""

    def __init__(self, resource: str, attributes: list[str], **args: object) -> None:
        """Exception raised when an attribute is missing."""
        super().__init__(**args)
        self.__resource = resource
        self.__attributes = attributes

    @property
    def message(self) -> str:
        """Return the exception message."""
        attr_str = ', '.join(self.__attributes)
        return f'Missing {attr_str} in {self.__resource}'


class CDKMissingAttributeInDependencyError(CDKMissingAttributeError):
    """Exception raised when an attribute is missing in a dependency."""

    def __init__(self, resource: str, attributes: list[str], **args: object) -> None:
        """Exception raised when an attribute is missing in a dependency.

        Parameters
        ----------
        resource: str
            The resource where the attribute(s) is missing
        attributes: list[str]
            list of attributes that are missing
        """
        super().__init__(resource, attributes, **args)


class CDKDependencyNotDeclaredError(CDKError):
    """Exception raised when a dependency is used but not declared."""

    def __init__(
            self, dependency_type: str, dependency_name: str, **args: object,
    ) -> None:
        """Exception raised when a dependency is used but not declared.

        Parameters
        ----------
        dependency_type: str
            The type of the dependency
        dependency_name: str
            The name of the dependency
        """
        super().__init__(*args)
        self.__name = dependency_name
        self.__type = dependency_type

    @property
    def message(self) -> str:
        """Return the exception message."""
        return f'{self.__type} {self.__name} not declared \
(be sure to declare it before using it)'


class CDKCyclicDependenciesError(CDKError):
    """Exception raised when cyclic dependencies are detected."""

    def __init__(self, stack: list[str], **args: object) -> None:
        """Exception raised when cyclic dependencies are detected.

        Parameters
        ----------
        stack: list[str]
            The stack of dependencies that are cyclic
        """
        super().__init__(*args)
        self.__stack = stack

    @property
    def message(self) -> str:
        """Return the exception message."""
        return ','.join(self.__stack)
