"""ParserFactory module."""
import os
from pathlib import Path

from thipster.engine import ParserPort
from thipster.engine.parsed_file import ParsedFile

from .dsl_parser import DSLParser
from .exceptions import (
    NoFileFoundError,
    ParserPathNotFoundError,
)
from .yaml_parser import YAMLParser


class NoParser(ParserPort):
    """Used when no parser is found for a file extension."""

    @classmethod
    def run(cls, path) -> ParsedFile:  # noqa: ARG003
        """Run the Parser."""
        return ParsedFile()


class ParserFactory(ParserPort):
    """Parser factory, used to run the right parser on the right file."""

    __parsers = {
        '.yaml': YAMLParser,
        '.yml': YAMLParser,
        '.jinja': YAMLParser,
        '.thips': DSLParser,
    }

    @classmethod
    def add_parser(cls, parser: ParserPort, extensions: list[str]):
        """Add a parser to the ParserFactory."""
        cls.__parsers.update({e: parser for e in extensions})

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
    def run(cls, path: str) -> ParsedFile:
        """Run the ParserFactory.

        Parameters
        ----------
        path: str
            Path to run the parser into

        Returns
        -------
        ParsedFile
            A ParsedFile object with the content of all the files in the input path
        """
        files = cls.__getfiles(path)

        res = ParsedFile()
        for file in files:
            parsed_file = cls.__get_parser(file).run(file)
            res.resources += parsed_file.resources

        if len(res.resources) == 0:
            raise NoFileFoundError(path)

        return res

    @classmethod
    def __get_parser(cls, path) -> ParserPort:

        path_extension = Path(path).suffix

        return cls.__parsers.get(
            path_extension, NoParser,
        )
