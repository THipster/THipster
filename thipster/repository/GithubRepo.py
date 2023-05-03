import json

import requests
from engine.ResourceModel import ResourceModel, Model_Attribute, Model_Dict, \
    Model_List, Model_Literal, I_Model_Value


class GithubRepo():
    def __init__(self, repo: str) -> None:
        self.__repo = repo
        self.model_list = {}

    def get(self, resourceNames: list[str]) -> list[ResourceModel]:
        for resource in resourceNames:
            self.__add_model(resource)

        return self.model_list

    def __create_value(self, val: object) -> I_Model_Value:
        if val is None:
            return None
        elif isinstance(val, dict):
            return Model_Dict(None)
        elif isinstance(val, list):
            return Model_List([self.__create_value(i) for i in val])

        return Model_Literal(val)

    def __create_attribute(self, raw: dict[str, str]):
        attributes = []

        for name, attr in raw.items():
            optional = attr['optional'] if 'optional' in attr.keys(
            ) else True

            value = attr['default'] if 'default' in attr.keys(
            ) else None

            default = self.__create_value(value)

            attributes.append(
                Model_Attribute(
                    name,
                    default=default,
                    optional=optional,
                ),
            )

        return attributes

    def __create_model(self, name: str):
        response = requests.get(
            f'https://raw.githubusercontent.com/{self.__repo}/main/{name}.json',
        )

        bucket = response.content
        json_model = json.loads(bucket)

        dependencies = []
        for dep in json_model['dependencies']:
            dependencies.append(self.__add_model(dep))

        res = ResourceModel(
            name,
            attributes=self.__create_attribute(json_model['attributes']),
            dependencies=json_model['dependencies'],
            cdk_provider=json_model['cdk_provider'],
            cdk_module=json_model['cdk_module'],
            cdk_name=json_model['cdk_class'],
        )

        return res

    def __add_model(self, model: str) -> ResourceModel:
        if model not in self.model_list.keys():
            self.model_list[model] = self.__create_model(model)

        return self.model_list[model]
