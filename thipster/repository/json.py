"""JSONRepo.py module."""

import json
from abc import ABC, abstractmethod

import thipster.engine.resource_model as rm
from thipster.engine import RepositoryPort


class JSONRepo(RepositoryPort, ABC):
    """Represents a JSON resources Repository.

    JSON Models of resources and services offered by supported cloud providers are
    stored in a repository.
    """

    _parent_stack = []

    def __init__(self) -> None:
        """Represent a JSON resources Repository.

        JSON Models of resources and services offered by supported cloud providers are
        stored in a repository.
        """
        super().__init__()
        self.model_list = {}

    @abstractmethod
    def get_json(self, name: str) -> str | bytes | bytearray:
        """Get the JSON file corresponding to the name given."""
        raise Exception

    def get(self, resource_names: list[str]) -> dict[str, rm.ResourceModel]:
        """Get the corresponding resource Models from a list of names.

        Parameters
        ----------
        resourceNames : list[str]
            List of the desired resource models names

        Returns
        -------
        dict[str, rm.ResourceModel]
            Dictionnary of the corresponding resource models
        """
        for resource in resource_names:
            self.__add_model(resource)

        return self.model_list

    def __create_value(self, val: object | None) -> rm.ModelValue | None:
        """Create the right Model value implementation from the raw JSON.

        Parameters
        ----------
        val : object
            Raw JSON model's attribute value

        Returns
        -------
        ModelValue | None
            Value of the attribute, implementation of ModelValue : ModelDict,
            ModelList, ModelLiteral or None
        """
        if val is None:
            return None
        if isinstance(val, dict):
            return rm.ModelDict(None)
        if isinstance(val, list):
            return rm.ModelList([self.__create_value(i) for i in val])

        return rm.ModelLiteral(val)

    def __create_attribute(self, raw: dict[str, str]) -> list[rm.ModelAttribute]:
        """Create a model's attributes from the raw JSON input.

        Parameters
        ----------
        raw : dict[str, str]
            Json model's raw attributes

        Returns
        -------
        list[ModelAttribute]
            Attributes of the resource model
        """
        attributes = {}

        for name, attr in raw.items():
            optional = attr['optional'] if 'optional' in attr else True

            value = attr['default'] if 'default' in attr else None

            is_list = 'list' in attr['var_type'] if 'var_type' in attr else False

            default = self.__create_value(value)

            attributes[name] = rm.ModelAttribute(
                attr['cdk_key'],
                default=default,
                optional=optional,
                is_list=is_list,
            )

        return attributes

    def __create_model(self, name: str) -> rm.ResourceModel:
        """Get the json file and create a Resource Model.

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
            if dep['resource'] not in self.model_list.keys():
                self.__add_model(dep['resource'])

        for _, internal_object in json_model['internalObjects'].items():
            if internal_object['resource'] not in self.model_list.keys():
                self.__add_model(internal_object['resource'])

        return rm.ResourceModel(
            name,
            attributes=self.__create_attribute(json_model['attributes']),
            dependencies=json_model['dependencies'],
            internal_objects=json_model['internalObjects'],
            name_key=json_model['cdk_name_key']
            if 'cdk_name_key' in json_model else None,
            cdk_provider=json_model['cdk_provider'],
            cdk_module=json_model['cdk_module'],
            cdk_name=json_model['cdk_class'],
        )

    def __add_model(self, model: str) -> rm.ResourceModel:
        """Add a model to the list.

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
