from parser.dsl_parser.Token import Token
from engine.ParsedFile import Position


def test_create_token():
    position = Position(fileName='testFile', ln=2, col=6)
    tokenType = 'test_type'
    value = 'test_value'

    token = Token(position, tokenType=tokenType, value=value)

    assert isinstance(token, Token)
    assert token.position == position
    assert token.tokenType == tokenType
    assert token.value == value
