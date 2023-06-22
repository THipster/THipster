"""Test the THipster DSL token parser."""
from thipster.engine.parsed_file import Position
from thipster.parser.dsl_parser.token import TOKENTYPES as TT
from thipster.parser.dsl_parser.token import Token
from thipster.parser.dsl_parser.token_parser import TokenParser


def test_simple_file():
    """Test the correct parsing of a simple tokenized file."""
    tokenized_input = [
        Token(Position('file', 1, 1), TT.STRING, 'bucket'),
        Token(Position('file', 1, 7), TT.WHITESPACE),
        Token(Position('file', 1, 8), TT.STRING, 'nom'),
        Token(Position('file', 1, 11), TT.MINUS),
        Token(Position('file', 1, 12), TT.INT, 8),
        Token(Position('file', 1, 13), TT.COLON),
        Token(Position('file', 1, 14), TT.NEWLINE),
        Token(Position('file', 2, 1), TT.TAB),
        Token(Position('file', 2, 2), TT.STRING, 'region'),
        Token(Position('file', 1, 8), TT.COLON),
        Token(Position('file', 2, 3), TT.STRING, 'euw'),
        Token(Position('file', 1, 14), TT.NEWLINE),
        Token(Position('file', 2, 4), TT.EOF),
    ]

    parser = TokenParser(tokenized_input)
    output = parser.run()

    assert str(output) == '<RESOURCE \
type = <STRING-EXPR <STRING (STRING bucket)>>, \
name = <STRING-EXPR <STRING (STRING nom)> <STRING (STRING -)> <INT (INT 8)>>, \
parameters = <DICT <PARAMETER name = <STRING (STRING region)>, \
value = <STRING-EXPR <STRING (STRING euw)>>>>>'


def test_newline_remover():
    """Test the correct parsing of a tokenized file with multiple newlines."""
    tokenized_input = [
        Token(Position('file', 1, 14), TT.NEWLINE),
        Token(Position('file', 1, 14), TT.NEWLINE),
        Token(Position('file', 1, 1), TT.STRING, 'bucket'),
        Token(Position('file', 1, 1), TT.WHITESPACE),
        Token(Position('file', 1, 8), TT.STRING, 'nom'),
        Token(Position('file', 1, 8), TT.MINUS),
        Token(Position('file', 1, 8), TT.INT, 8),
        Token(Position('file', 1, 8), TT.COLON),
        Token(Position('file', 1, 14), TT.NEWLINE),
        Token(Position('file', 1, 14), TT.NEWLINE),
        Token(Position('file', 2, 1), TT.TAB),
        Token(Position('file', 2, 2), TT.STRING, 'region'),
        Token(Position('file', 1, 8), TT.COLON),
        Token(Position('file', 2, 3), TT.STRING, 'euw'),
        Token(Position('file', 1, 14), TT.NEWLINE),
        Token(Position('file', 1, 14), TT.NEWLINE),
        Token(Position('file', 1, 14), TT.NEWLINE),
        Token(Position('file', 1, 1), TT.STRING, 'bucket'),
        Token(Position('file', 1, 1), TT.WHITESPACE),
        Token(Position('file', 1, 8), TT.STRING, 'nom'),
        Token(Position('file', 1, 8), TT.MINUS),
        Token(Position('file', 1, 8), TT.INT, 8),
        Token(Position('file', 1, 8), TT.COLON),
        Token(Position('file', 1, 14), TT.NEWLINE),
        Token(Position('file', 2, 1), TT.TAB),
        Token(Position('file', 2, 2), TT.STRING, 'region'),
        Token(Position('file', 1, 8), TT.COLON),
        Token(Position('file', 2, 3), TT.STRING, 'euw'),
        Token(Position('file', 1, 14), TT.NEWLINE),
        Token(Position('file', 2, 4), TT.EOF),
    ]
    parser = TokenParser(tokenized_input)
    output = parser.run()

    assert str(output) == '<RESOURCE \
type = <STRING-EXPR <STRING (STRING bucket)>>, \
name = <STRING-EXPR <STRING (STRING nom)> <STRING (STRING -)> <INT (INT 8)>>, \
parameters = <DICT <PARAMETER name = <STRING (STRING region)>, \
value = <STRING-EXPR <STRING (STRING euw)>>>>>\n\
<RESOURCE \
type = <STRING-EXPR <STRING (STRING bucket)>>, \
name = <STRING-EXPR <STRING (STRING nom)> <STRING (STRING -)> <INT (INT 8)>>, \
parameters = <DICT <PARAMETER name = <STRING (STRING region)>, \
value = <STRING-EXPR <STRING (STRING euw)>>>>>'
