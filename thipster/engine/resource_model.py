"""ResourceModel.py module."""

from abc import ABC


class ModelValue(ABC):
    """Model Attribute Value Interface."""

    value = None


class ModelAttribute:
    """Represents a Resource Model attribute."""

    def __init__(
            self, cdk_name: str,
            default: ModelValue | None = None,
            optional: bool = True,
            is_list: bool = False,
    ):
        """Represent a Resource Model attribute.

        Parameters
        ----------
        name : str
            Attribute name
        default : ModelValue, optional
            Default Attribute value if there is one, by default None
        optional : bool, optional
            Is attribute optional ?, by default True
        is_list : bool, optional
            Is attribute a list ?, by default False
        """
        self.cdk_name = cdk_name
        self.__default = default
        self.optional = optional
        self.is_list = is_list

    @property
    def default(self):
        """Default value of the attribute."""
        return self.__default.value if self.__default else None

    @default.setter
    def default(self, value):
        self.__default = value


class ModelList(ModelValue):
    """Represent a List of values for a Resource Model attribute."""

    def __init__(self, value: list[ModelValue | None] | None):
        """Represent a List of values for a Resource Model attribute."""
        super().__init__()
        self.value = value

    def __iter__(self):
        """Iterate over the list."""
        self.i = 0
        return self

    def __next__(self):
        """Return the next value of the iterator."""
        if not self.value:
            return None
        ret = self.value[self.i]
        if self.i > len(self.value):
            raise StopIteration

        self.i += 1

        return ret


class ModelLiteral(ModelValue):
    """Represent a literal value for a Resource Model attribute."""

    def __init__(self, value):
        """Represent a literal value for a Resource Model attribute."""
        super().__init__()
        self.value = value


class ModelDict(ModelValue):
    """Represent a dictionary value for a Resource Model attribute."""

    def __init__(self, value: dict[str, ModelAttribute] | None):
        """Represent a dictionary value for a Resource Model attribute."""
        super().__init__()
        self.value = value

    def __iter__(self):
        """Iterate over the dictionary."""
        self.i = 0
        return self

    def __next__(self):
        """Return the next value of the iterator."""
        if not self.value:
            return None
        ret = self.value[self.i]
        if self.i > len(self.value):
            raise StopIteration

        self.i += 1

        return ret


class ResourceModel:
    """Represents a Resource Model."""

    def __init__(
            self,
            resource_type: str,
            attributes: dict[str, ModelAttribute] | None,
            dependencies: dict[str, dict[str, object]] | None,
            internal_objects: dict[str, dict[str, object]] | None,
            name_key: str | None,
            cdk_provider: str,
            cdk_module: str,
            cdk_name: str,
    ):
        """Represent a Resource Model."""
        self.resource_type = resource_type
        self.attributes = attributes
        self.dependencies = dependencies
        self.internal_objects = internal_objects
        self.name_key = name_key
        self.cdk_provider = cdk_provider
        self.cdk_module = cdk_module
        self.cdk_name = cdk_name
