from engine.I_Parser import I_Parser
from engine.ParsedFile import ParsedAttribute, ParsedDict, ParsedFile, ParsedList,\
    ParsedLiteral, ParsedResource
from jinja2 import Environment, FileSystemLoader

import os
import yaml


class YAMLParserBaseException(Exception):
    def __init__(self, message, *args: object) -> None:
        super().__init__(*args)

        self.__message = message

    @property
    def message(self):
        return self.__message


class YAMLParserPathNotFound(YAMLParserBaseException):
    def __init__(file, *args: object) -> None:
        super().__init__(f'Path not found : {file}', *args)


class YAMLParserNoName(YAMLParserBaseException):
    def __init__(resource, *args: object) -> None:
        super().__init__(f'No name for resource : {resource}', *args)


class YAMLParser(I_Parser):

    def __getfiles(path: str) -> list[str]:
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
            raise YAMLParserPathNotFound(path)

        files = []

        if os.path.isdir(path):
            for content in os.listdir(path):
                files += YAMLParser.__getfiles(f'{path}/{content}')

        if os.path.isfile(path):
            return [path]

        return files

    def run(path: str) -> ParsedFile:
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
            files = YAMLParser.__getfiles(path)
            parsedFile = ParsedFile()

            for file in files:
                filedir, filename = os.path.split(file)

                environment = Environment(loader=FileSystemLoader(filedir))
                template = environment.get_template(filename)
                rendered = template.render()
                content = yaml.safe_load(rendered)

                parsedFile.resources += YAMLParser.__convert(content)

            return parsedFile
        except yaml.YAMLError as exc:
            raise exc
        except YAMLParserBaseException as e:
            raise e
        except Exception as e:
            raise e

    def __convert(file: dict) -> list[ParsedResource]:
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
                        raise YAMLParserNoName(key)

                    resources.append(
                        YAMLParser.__get_resource(
                            content=res, resourceType=key, name=name,
                        ),
                    )
            elif type(val) == dict:
                if 'name' in val:
                    name = val['name']
                    del val['name']
                else:
                    raise YAMLParserNoName(key)

                resources.append(
                    YAMLParser.__get_resource(
                        content=val, resourceType=key, name=name,
                    ),
                )

        return resources

    def __get_resource(content: dict, resourceType: str, name: str)\
            -> ParsedResource:
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
            attr.append(YAMLParser.__get__attr(key, val))

        return ParsedResource(
            type=resourceType,
            name=name,
            position=None,
            attributes=attr,
        )

    def __get__attr(name: str, value: object) -> ParsedAttribute:
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
            val = YAMLParser.__get_dict(value)
        elif type(value) == list:
            val = YAMLParser.__get_list(value)
        else:
            val = ParsedLiteral(str(value))

        return ParsedAttribute(
            name=name,
            value=val,
            position=None,
        )

    def __get_dict(input: dict) -> ParsedDict:
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
            attr.append(YAMLParser.__get__attr(key, val))

        return ParsedDict(attr)

    def __get_list(input: list) -> ParsedList:
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
            attr.append(ParsedList(val))

        return ParsedList(attr)
