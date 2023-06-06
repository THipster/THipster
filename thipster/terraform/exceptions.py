class CDKException(Exception):
    @property
    def message(self):
        return str(self)


class CDKInvalidAttribute(CDKException):
    def __init__(self, attr: str, modelType: str, **args: object) -> None:
        super().__init__(*args)
        self.__attr = attr
        self.__modelType = modelType

    def __str__(self) -> str:
        return f'{self.__attr} in {self.__modelType} but not useful'


class CDKMissingAttribute(CDKException):
    pass


class CDKMissingAttributeInDependency(CDKMissingAttribute):
    pass


class CDKDependencyNotDeclared(CDKException):
    def __init__(self, depType: str, depName: str, **args: object) -> None:
        super().__init__(*args)
        self.__name = depName
        self.__type = depType

    def __str__(self) -> str:
        return f'{self.__type} {self.__name} not declared \
(be sure to declare it before using it)'


class CDKCyclicDependencies(CDKException):
    def __init__(self, stack: list[str], **args: object) -> None:
        super().__init__(*args)
        self.__stack = stack

    def __str__(self) -> str:
        return ','.join(self.__stack)
