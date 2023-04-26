from engine.ParsedFile import Position
from parser.dsl_parser.TokenParser import TokenParser
from parser.dsl_parser.Token import Token


def test_simple_file():
    input = [
        Token(Position('file', 1, 1), 'STRING', 'bucket'),
        Token(Position('file', 1, 8), 'STRING', 'nom-8'),
        Token(Position('file', 1, 8), 'COLUMN'),
        Token(Position('file', 1, 14), 'NEWLINE'),
        Token(Position('file', 2, 1), 'TAB'),
        Token(Position('file', 2, 2), 'STRING', 'region'),
        Token(Position('file', 1, 8), 'COLUMN'),
        Token(Position('file', 2, 3), 'STRING', 'euw'),
        Token(Position('file', 1, 14), 'NEWLINE'),
        Token(Position('file', 2, 4), 'EOF'),
    ]

    parser = TokenParser(input)
    output = parser.run()

    assert str(output) == '<RESOURCE \
type = <STRING (STRING bucket)>, \
name = <STRING (STRING nom-8)>, \
parameters = <DICT <PARAMETER name = <STRING (STRING region)>, \
value = <LITERAL <STRING (STRING euw)>>>>>'


def test_newline_remover():
    input = [
        Token(Position('file', 1, 14), 'NEWLINE'),
        Token(Position('file', 1, 14), 'NEWLINE'),
        Token(Position('file', 1, 1), 'STRING', 'bucket'),
        Token(Position('file', 1, 8), 'STRING', 'nom-8'),
        Token(Position('file', 1, 8), 'COLUMN'),
        Token(Position('file', 1, 14), 'NEWLINE'),
        Token(Position('file', 1, 14), 'NEWLINE'),
        Token(Position('file', 2, 1), 'TAB'),
        Token(Position('file', 2, 2), 'STRING', 'region'),
        Token(Position('file', 1, 8), 'COLUMN'),
        Token(Position('file', 2, 3), 'STRING', 'euw'),
        Token(Position('file', 1, 14), 'NEWLINE'),
        Token(Position('file', 1, 14), 'NEWLINE'),
        Token(Position('file', 1, 14), 'NEWLINE'),
        Token(Position('file', 1, 1), 'STRING', 'bucket'),
        Token(Position('file', 1, 8), 'STRING', 'nom-8'),
        Token(Position('file', 1, 8), 'COLUMN'),
        Token(Position('file', 1, 14), 'NEWLINE'),
        Token(Position('file', 2, 1), 'TAB'),
        Token(Position('file', 2, 2), 'STRING', 'region'),
        Token(Position('file', 1, 8), 'COLUMN'),
        Token(Position('file', 2, 3), 'STRING', 'euw'),
        Token(Position('file', 1, 14), 'NEWLINE'),
        Token(Position('file', 2, 4), 'EOF'),
    ]

    parser = TokenParser(input)
    output = parser.run()

    assert str(output) == '<RESOURCE \
type = <STRING (STRING bucket)>, \
name = <STRING (STRING nom-8)>, \
parameters = <DICT <PARAMETER name = <STRING (STRING region)>, \
value = <LITERAL <STRING (STRING euw)>>>>>\n\
<RESOURCE \
type = <STRING (STRING bucket)>, \
name = <STRING (STRING nom-8)>, \
parameters = <DICT <PARAMETER name = <STRING (STRING region)>, \
value = <LITERAL <STRING (STRING euw)>>>>>'
