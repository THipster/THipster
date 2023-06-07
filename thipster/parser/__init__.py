"""Parser module.

Contains the various parsers used by THipster to interpret the input files.
Currently, two options are available:
- The DSL parser, which interprets .thips files
- The YAML JINJA parser, which interprets .yml/.yaml/.jinja files
"""

from .dsl_parser import DSLParser
from .parser_factory import ParserFactory
from .yaml_parser import YAMLParser
