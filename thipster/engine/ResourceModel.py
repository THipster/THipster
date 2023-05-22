"""ResourceModel.py module.
"""

from abc import ABC, abstractmethod


class I_Model_Value(ABC):
    """Model Attribute Value Interface
    """

    @property
    @abstractmethod
    def value(self):
        pass


class Model_Attribute():
    """Represents a Resource Model attribute
    """

    def __init__(
            self, cdk_name: str,
            default: I_Model_Value | None = None,
            optional: bool = True,
            is_list: bool = False,
    ):
        """
        Parameters
        ----------
        name : str
            Attribute name
        default : I_Model_Value, optional
            Default Attribute value if there is one, by default None
        optional : bool, optional
            Is attribute optional ?, by default True
        is_list : bool, optional
            Is attribute a list ?, by default False
        """
        self.__cdk_name = cdk_name
        self.__default = default
        self.__optional = optional
        self.__is_list = is_list

    @property
    def default(self):
        return self.__default.value if self.__default else None

    @property
    def cdk_name(self):
        return self.__cdk_name

    @property
    def optional(self):
        return self.__optional

    @property
    def is_list(self):
        return self.__is_list


class Model_List(I_Model_Value):
    """Represents a List of values for a Resource Model attribute
    """

    def __init__(self, value: list[I_Model_Value | None] | None):
        super().__init__()
        self.__value = value

    @property
    def value(self):
        return self.__value

    def __iter__(self):
        self.i = 0
        return self

    def __next__(self):
        if not self.__value:
            return None
        ret = self.__value[self.i]
        if self.i > len(self.__value):
            raise StopIteration
        else:
            self.i += 1

        return ret


class Model_Literal(I_Model_Value):
    """Represents a literal value for a Resource Model attribute
    """

    def __init__(self, value):
        super().__init__()
        self.__value = value

    @property
    def value(self):
        return self.__value


class Model_Dict(I_Model_Value):
    """Represents a dictionary value for a Resource Model attribute
    """

    def __init__(self, value: dict[str, Model_Attribute] | None):
        super().__init__()
        self.__value = value

    @property
    def value(self):
        return self.__value

    def __iter__(self):
        self.i = 0
        return self

    def __next__(self):
        if not self.__value:
            return None
        ret = self.__value[self.i]
        if self.i > len(self.__value):
            raise StopIteration
        else:
            self.i += 1

        return ret


class ResourceModel():
    """Represents a Resource Model
    """

    def __init__(
            self,
            type: str,
            attributes: dict[str, Model_Attribute] | None,
            dependencies: dict[str, dict[str, object]] | None,
            internalObjects: dict[str, dict[str, object]] | None,
            name_key: str | None,
            cdk_provider: str,
            cdk_module: str,
            cdk_name: str,
    ):
        self.__type = type
        self.__attributes = attributes
        self.__dependencies = dependencies
        self.__internal_objects = internalObjects
        self.__name_key = name_key
        self.__cdk_provider = cdk_provider
        self.__cdk_module = cdk_module
        self.__cdk_name = cdk_name

    @property
    def type(self):
        return self.__type

    @property
    def attributes(self):
        return self.__attributes

    @property
    def dependencies(self):
        return self.__dependencies

    @property
    def internalObjects(self):
        return self.__internal_objects

    @property
    def name_key(self):
        return self.__name_key

    @property
    def cdk_provider(self):
        return self.__cdk_provider

    @property
    def cdk_module(self):
        return self.__cdk_module

    @property
    def cdk_name(self):
        return self.__cdk_name
