from thipster.engine import THipsterError


class CDKError(THipsterError):
    pass


class CDKInvalidAttributeError(CDKError):
    def __init__(self, attr: str, model_type: str, **args: object) -> None:
        super().__init__(*args)
        self.__attr = attr
        self.__modelType = model_type

    @property
    def message(self) -> str:
        return f'{self.__attr} in {self.__modelType} but not useful'


class CDKMissingAttributeError(CDKError):
    @property
    def message(self) -> str:
        return 'Missing an attribute'


class CDKMissingAttributeInDependencyError(CDKMissingAttributeError):
    pass


class CDKDependencyNotDeclaredError(CDKError):
    def __init__(
            self, dependency_type: str, dependency_name: str, **args: object,
    ) -> None:
        super().__init__(*args)
        self.__name = dependency_name
        self.__type = dependency_type

    @property
    def message(self) -> str:
        return f'{self.__type} {self.__name} not declared \
(be sure to declare it before using it)'


class CDKCyclicDependenciesError(CDKError):
    def __init__(self, stack: list[str], **args: object) -> None:
        super().__init__(*args)
        self.__stack = stack

    @property
    def message(self) -> str:
        return ','.join(self.__stack)
