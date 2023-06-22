"""YAML Parser module."""
import os
from abc import ABC
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader

import thipster.engine.parsed_file as pf
from thipster.engine import ParserPort, THipsterError

from .exceptions import ParserPathNotFoundError


class YAMLParserBaseError(THipsterError, ABC):
    """Base error for YAMLParser."""

    def __init__(self, *args: object) -> None:
        """Shared base exception for the YAML parser."""
        super().__init__(*args)


class YAMLParserNoNameError(YAMLParserBaseError):
    """Error raised when a resource has no name."""

    def __init__(self, resource, *args: object) -> None:
        """Error raised when a resource has no name.

        Parameters
        ----------
        resource
            The resource that has no name.
        """
        super().__init__(*args)
        self.resource = resource

    @property
    def message(self) -> str:
        """Return the error message."""
        return f'No name for resource : {self.resource}'


class YAMLParser(ParserPort):
    """YAMLParser class, used to parse YAML files."""

    @classmethod
    def __getfiles(cls, path: str) -> list[str]:
        """Get the file(s) on the requested path.

        Recursively get all files names in the requested directory and its
        sudirectories. Can be run on a path file as well.

        Parameters
        ----------
        path: str
            Path to run this function onto

        Returns
        -------
        list[str]
            A list of all the filenames
        """
        path = Path(path).resolve().as_posix()

        if not Path(path).exists():
            raise ParserPathNotFoundError(path)

        files = []

        if Path(path).is_dir():
            for content in os.listdir(path):
                files += cls.__getfiles(f'{path}/{content}')

        if Path(path).is_file():
            return [path]

        return files

    @classmethod
    def run(cls, path: str) -> pf.ParsedFile:
        """Run the YAMLParser.

        Parameters
        ----------
        path: str
            Path to run the parser into

        Returns
        -------
        ParsedFile
            A ParsedFile object with the content of all the files in the input path
        """
        try:
            files = cls.__getfiles(path)
            parsed_file = pf.ParsedFile()

            for file in files:
                filedir, filename = os.path.split(file)

                environment = Environment(
                    loader=FileSystemLoader(filedir),
                    autoescape=True,
                )
                template = environment.get_template(filename)
                rendered = template.render()
                content = yaml.safe_load(rendered)

                parsed_file.resources += cls.__convert(content)

            return parsed_file
        except yaml.YAMLError as exc:
            raise exc
        except YAMLParserBaseError as e:
            raise e
        except Exception as e:
            raise e

    @classmethod
    def __convert(cls, file: dict) -> list[pf.ParsedResource]:
        """Convert a dictionnary into a list of ParsedResources.

        Parameters
        ----------
        file: dict
            Dict to convert

        Returns
        -------
        list[ParsedResource]
            Converted dict
        """
        resources = []

        for key, val in file.items():
            if type(val) == list:
                for res in val:
                    if 'name' not in res:
                        raise YAMLParserNoNameError(key)

                    name = res['name']
                    del res['name']

                    resources.append(
                        cls.__get_resource(
                            content=res, resource_type=key, name=name,
                        ),
                    )
            elif type(val) == dict:
                if 'name' not in val:
                    raise YAMLParserNoNameError(key)

                name = val['name']
                del val['name']

                resources.append(
                    cls.__get_resource(
                        content=val, resource_type=key, name=name,
                    ),
                )

        return resources

    @classmethod
    def __get_resource(cls, content: dict, resource_type: str, name: str)\
            -> pf.ParsedResource:
        """Convert a dict in a ParsedResource.

        Parameters
        ----------
        content: dict
            Dict of attributes of the resource
        resourceType: str
            Type of the resource
        name: str
            Name of the resource

        Returns
        -------
        ParsedResource
            A ParsedResource object with the content of the dict
        """
        attr = []

        for key, val in content.items():
            attr.append(cls.__get__attr(key, val))

        return pf.ParsedResource(
            parsed_resource_type=resource_type,
            name=name,
            position=None,
            attributes=attr,
        )

    @classmethod
    def __get__attr(cls, name: str, value: object) -> pf.ParsedAttribute:
        """Convert an object in a ParsedAttribute.

        Parameters
        ----------
        value: object
            Object to convert
        name: str
            Name of the attribute

        Returns
        -------
        ParsedResource
            A ParsedAttribute object with wanted value type
        """
        if type(value) == dict:
            val = cls.__get_dict(value)
        elif type(value) == list:
            val = cls.__get_list(value)
        else:
            val = pf.ParsedLiteral(value)

        return pf.ParsedAttribute(
            name=name,
            value=val,
            position=None,
        )

    @classmethod
    def __get_dict(cls, input_dict: dict) -> pf.ParsedDict:
        """Convert a dict into a list of ParsedDict.

        Parameters
        ----------
        input_dict: dict
            Dict to convert

        Returns
        -------
        ParsedDict
            Converted dict
        """
        attr = []

        for key, val in input_dict.items():
            attr.append(cls.__get__attr(key, val))

        return pf.ParsedDict(attr)

    @classmethod
    def __get_list(cls, input_list: list) -> pf.ParsedList:
        """Convert a dictionnary into a ParsedList.

        Parameters
        ----------
        input_list: list
            List to convert

        Returns
        -------
        ParsedList
            Converted list
        """
        attr = []

        for val in input_list:
            if isinstance(val, dict):
                attr.append(cls.__get_dict(val))
            else:
                attr.append(pf.ParsedLiteral(val))

        return pf.ParsedList(attr)
