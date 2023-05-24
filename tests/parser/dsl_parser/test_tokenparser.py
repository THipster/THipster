from engine.ParsedFile import Position
from parser.dsl_parser.TokenParser import TokenParser
from parser.dsl_parser.Token import Token, TOKENTYPES as TT


def test_simple_file():
    input = [
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

    parser = TokenParser(input)
    output = parser.run()

    assert str(output) == '<RESOURCE \
type = <STRING-EXPR <STRING (STRING bucket)>>, \
name = <STRING-EXPR <STRING (STRING nom)> <STRING (STRING -)> <INT (INT 8)>>, \
parameters = <DICT <PARAMETER name = <STRING (STRING region)>, \
value = <STRING-EXPR <STRING (STRING euw)>>>>>'


def test_newline_remover():
    input = [
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
    parser = TokenParser(input)
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
