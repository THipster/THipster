from engine.I_Parser import I_Parser
from engine.ParsedFile import ParsedAttribute, ParsedDict, ParsedFile, ParsedList,\
    ParsedLiteral, ParsedResource

import os
import yaml
from helpers import logger


class YAMLParserBaseException(Exception):
    def __init__(self, message, *args: object) -> None:
        super().__init__(*args)

        self.__message = message

    @property
    def message(self):
        return self.__message


class YAMLParserPathNotFound(YAMLParserBaseException):
    def __init__(self, file, *args: object) -> None:
        super().__init__(f'Path not found : {file}', *args)


class YAMLParserNoName(YAMLParserBaseException):
    def __init__(self, resource, *args: object) -> None:
        super().__init__(f'No name for resource : {resource}', *args)


class YAMLParser(I_Parser):

    def __getfiles(self, path: str) -> list[str]:

        path = os.path.abspath(path)

        if not os.path.exists(path):
            raise YAMLParserPathNotFound(path)

        files = []

        if os.path.isdir(path):
            for content in os.listdir(path):
                files += self.__getfiles(f'{path}/{content}')

        if os.path.isfile(path):
            return [path]

        return files

    @logger('- YAML Parser')
    def run(self, path: str) -> ParsedFile:
        try:
            files = self.__getfiles(path)
            parsedFile = ParsedFile()

            for file in files:
                with open(file, 'r') as stream:
                    content = yaml.safe_load(stream)
                    parsedFile.resources += self.__convert(content)

            return parsedFile
        except yaml.YAMLError as exc:
            raise exc
        except YAMLParserBaseException as e:
            raise e
        except Exception as e:
            raise e

    def __convert(self, file: dict) -> list[ParsedResource]:
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
                        self.__get_resource(
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
                    self.__get_resource(
                        content=val, resourceType=key, name=name,
                    ),
                )

        return resources

    def __get_resource(self, content: dict, resourceType: str, name: str)\
            -> ParsedResource:
        attr = []

        for key, val in content.items():
            attr.append(self.__get__attr(key, val))

        return ParsedResource(
            type=resourceType,
            name=name,
            position=None,
            attributes=attr,
        )

    def __get__attr(self, name: str, value: object) -> ParsedAttribute:
        if type(value) == dict:
            val = self.__get_dict(value)
        elif type(value) == list:
            val = self.__get_list(value)
        else:
            val = ParsedLiteral(value)

        return ParsedAttribute(
            name=name,
            value=val,
            position=None,
        )

    def __get_dict(self, input: dict):
        attr = []

        for key, val in input.items():
            attr.append(self.__get__attr(key, val))

        return ParsedDict(attr)

    def __get_list(self, input: list):
        attr = []

        for val in input:
            attr.append(ParsedList(val))

        return ParsedList(attr)
