from abc import ABC, abstractmethod
import json
from engine.I_Repository import I_Repository

import engine.ResourceModel as rm


class JSONRepo(I_Repository, ABC):
    def __init__(self) -> None:
        super().__init__()
        self.model_list = {}

    @abstractmethod
    def get_json(self, name: str) -> str | bytes | bytearray:
        raise Exception()

    def get(self, resourceNames: list[str]) -> dict[str, rm.ResourceModel]:
        for resource in resourceNames:
            self.__add_model(resource)

        return self.model_list

    def __create_value(self, val: object) -> rm.I_Model_Value:
        if val is None:
            return None
        elif isinstance(val, dict):
            return rm.Model_Dict(None)
        elif isinstance(val, list):
            return rm.Model_List([self.__create_value(i) for i in val])

        return rm.Model_Literal(val)

    def __create_attribute(self, raw: dict[str, str]):
        attributes = []

        for name, attr in raw.items():
            optional = attr['optional'] if 'optional' in attr.keys(
            ) else True

            value = attr['default'] if 'default' in attr.keys(
            ) else None

            default = self.__create_value(value)

            attributes.append(
                rm.Model_Attribute(
                    name,
                    default=default,
                    optional=optional,
                ),
            )

        return attributes

    def __create_model(self, name: str):
        model = self.get_json(name)

        json_model = json.loads(model)

        for _, dep in json_model['dependencies'].items():
            self.__add_model(dep)

        res = rm.ResourceModel(
            name,
            attributes=self.__create_attribute(json_model['attributes']),
            dependencies=json_model['dependencies'],
            cdk_provider=json_model['cdk_provider'],
            cdk_module=json_model['cdk_module'],
            cdk_name=json_model['cdk_class'],
        )

        return res

    def __add_model(self, model: str) -> rm.ResourceModel:
        if model not in self.model_list.keys():
            self.model_list[model] = self.__create_model(model)

        return self.model_list[model]
