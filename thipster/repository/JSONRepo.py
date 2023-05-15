"""JSONRepo.py module.
"""

from abc import ABC, abstractmethod
import json
from engine.I_Repository import I_Repository

import engine.ResourceModel as rm


class JSONRepo(I_Repository, ABC):
    _parentStack = []
    """Class representing a JSON resources Repository

    JSON Models of resources and services offered by supported cloud providers are
    stored in a repository.
    """

    def __init__(self) -> None:
        super().__init__()
        self.model_list = {}

    @abstractmethod
    def get_json(self, name: str) -> str | bytes | bytearray:
        raise Exception()

    def get(self, resourceNames: list[str]) -> dict[str, rm.ResourceModel]:
        """Get the corresponding resource Models from a list of names

        Parameters
        ----------
        resourceNames : list[str]
            List of the desired resource models names

        Returns
        -------
        dict[str, rm.ResourceModel]
            Dictionnary of the corresponding resource models
        """
        for resource in resourceNames:
            self.__add_model(resource)

        return self.model_list

    def __create_value(self, val: object) -> rm.I_Model_Value | None:
        """Creates the right Model value implementation from the raw JSON

        Parameters
        ----------
        val : object
            Raw JSON model's attribute value

        Returns
        -------
        I_Model_Value | None
            Value of the attribute, implementation of I_Model_Value : Model_Dict,
            Model_List, Model_Literal or None
        """
        if val is None:
            return None
        elif isinstance(val, dict):
            return rm.Model_Dict(None)
        elif isinstance(val, list):
            return rm.Model_List([self.__create_value(i) for i in val])

        return rm.Model_Literal(val)

    def __create_attribute(self, raw: dict[str, str]) -> list[rm.Model_Attribute]:
        """Creates a model's attributes from the raw JSON input

        Parameters
        ----------
        raw : dict[str, str]
            Json model's raw attributes

        Returns
        -------
        list[Model_Attribute]
            Attributes of the resource model
        """

        attributes = {}

        for name, attr in raw.items():
            optional = attr['optional'] if 'optional' in attr.keys(
            ) else True

            value = attr['default'] if 'default' in attr.keys(
            ) else None

            default = self.__create_value(value)

            attributes[name] = rm.Model_Attribute(
                attr['cdk_key'],
                default=default,
                optional=optional,
            )

        return attributes

    def __create_model(self, name: str) -> rm.ResourceModel:
        """Get's the json file and creates a Resource Model

        Parameters
        ----------
        name : str
            Name of the model to find

        Returns
        -------
        ResourceModel
            Resource model corresponding to the name given
        """

        model = self.get_json(name)

        json_model = json.loads(model)

        for _, dep in json_model['dependencies'].items():
            if dep not in self.model_list.keys():
                self.__add_model(dep)

        res = rm.ResourceModel(
            name,
            attributes=self.__create_attribute(json_model['attributes']),
            dependencies=json_model['dependencies'],
            name_key=json_model['cdk_name_key'],
            cdk_provider=json_model['cdk_provider'],
            cdk_module=json_model['cdk_module'],
            cdk_name=json_model['cdk_class'],
        )

        return res

    def __add_model(self, model: str) -> rm.ResourceModel:
        """Add a model to the list

        Parameters
        ----------
        model : str
            Name of the model to add

        Returns
        -------
        ResourceModel
            Resource model corresponding to the name given
        """

        if model not in self.model_list.keys():
            self.model_list[model] = None
            self.model_list[model] = self.__create_model(model)

        return self.model_list[model]
