import os
from abc import ABC

import yaml
from jinja2 import Environment, FileSystemLoader

import thipster.engine.parsed_file as pf
from thipster.engine import ParserPort, THipsterError

from .exceptions import ParserPathNotFoundError


class YAMLParserBaseError(THipsterError, ABC):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class YAMLParserNoNameError(YAMLParserBaseError):
    def __init__(self, resource, *args: object) -> None:
        super().__init__(*args)
        self.resource = resource

    @property
    def message(self) -> str:
        return f'No name for resource : {self.resource}'


class YAMLParser(ParserPort):
    @classmethod
    def __getfiles(cls, path: str) -> list[str]:
        """Recursively get all files names in the requested directory and its\
              sudirectories
        Can be run on a path file aswell

        Parameters
        ----------
        path: str
            Path to run this function into

        Returns
        -------
        list[str]
            A list of all the filenames
        """
        path = os.path.abspath(path)

        if not os.path.exists(path):
            raise ParserPathNotFoundError(path)

        files = []

        if os.path.isdir(path):
            for content in os.listdir(path):
                files += cls.__getfiles(f'{path}/{content}')

        if os.path.isfile(path):
            return [path]

        return files

    @classmethod
    def run(cls, path: str) -> pf.ParsedFile:
        """Run the YAMLParser

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
        """Converts a dictionnary into a list of ParsedResources

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
                    if 'name' in res:
                        name = res['name']
                        del res['name']
                    else:
                        raise YAMLParserNoNameError(key)

                    resources.append(
                        cls.__get_resource(
                            content=res, resource_type=key, name=name,
                        ),
                    )
            elif type(val) == dict:
                if 'name' in val:
                    name = val['name']
                    del val['name']
                else:
                    raise YAMLParserNoNameError(key)

                resources.append(
                    cls.__get_resource(
                        content=val, resource_type=key, name=name,
                    ),
                )

        return resources

    @classmethod
    def __get_resource(cls, content: dict, resource_type: str, name: str)\
            -> pf.ParsedResource:
        """Converts a dict in a ParsedResource

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
            type=resource_type,
            name=name,
            position=None,
            attributes=attr,
        )

    @classmethod
    def __get__attr(cls, name: str, value: object) -> pf.ParsedAttribute:
        """Converts an object in a ParsedAttribute

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
    def __get_dict(cls, input: dict) -> pf.ParsedDict:
        """Converts a dict into a list of ParsedDict

        Parameters
        ----------
        input: dict
            Dict to convert

        Returns
        -------
        ParsedDict
            Converted dict
        """
        attr = []

        for key, val in input.items():
            attr.append(cls.__get__attr(key, val))

        return pf.ParsedDict(attr)

    @classmethod
    def __get_list(cls, input: list) -> pf.ParsedList:
        """Converts a dictionnary into a ParsedList

        Parameters
        ----------
        input: list
            List to convert

        Returns
        -------
        ParsedList
            Converted list
        """
        attr = []

        for val in input:
            if isinstance(val, dict):
                attr.append(cls.__get_dict(val))
            else:
                attr.append(pf.ParsedLiteral(val))

        return pf.ParsedList(attr)
