from abc import ABC, abstractmethod


class I_Model_Value(ABC):
    @property
    @abstractmethod
    def value(self):
        pass


class Model_Attribute():
    def __init__(self, name: str, default: I_Model_Value = None, optional: bool = True):
        self.__name = name
        self.__default = default
        self.__optional = optional

    @property
    def default(self):
        return self.__default.value

    @property
    def name(self):
        return self.__name

    @property
    def optional(self):
        return self.__optional


class Model_List(I_Model_Value):
    def __init__(self, value: list[I_Model_Value]):
        super().__init__()
        self.__value = value

    @property
    def value(self):
        return self.__value

    def __iter__(self):
        self.i = 0
        return self

    def __next__(self):
        ret = self.value[self.i]
        if self.i > len(self.__value):
            raise StopIteration
        else:
            self.i += 1

        return ret


class Model_Literal(I_Model_Value):
    def __init__(self, value):
        super().__init__()
        self.__value = value

    @property
    def value(self):
        return self.__value


class Model_Dict(I_Model_Value):
    def __init__(self, value: dict[str, Model_Attribute]):
        super().__init__()
        self.__value = value

    @property
    def value(self):
        return self.__value

    def __iter__(self):
        self.i = 0
        return self

    def __next__(self):
        ret = self.value[self.i]
        if self.i > len(self.__value):
            raise StopIteration
        else:
            self.i += 1

        return ret


class ResourceModel():
    def __init__(
            self,
            type: str,
            attributes: list[Model_Attribute],
            dependencies: dict[str, str],
            cdk_provider: str,
            cdk_module: str,
            cdk_name: str,
    ):
        self.__type = type
        self.__attributes = attributes
        self.__dependencies = dependencies
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
    def cdk_provider(self):
        return self.__cdk_provider

    @property
    def cdk_module(self):
        return self.__cdk_module

    @property
    def cdk_name(self):
        return self.__cdk_name
