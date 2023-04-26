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


def test_token_to_string():
    position = Position(fileName='testFile', ln=2, col=6)
    positionStr = '(File : testFile, Ln 2, Col 6)'
    assert str(position) == positionStr

    tokenType = 'test_type'
    value = 'test_value'
    token = Token(position, tokenType=tokenType, value=value)
    tokenStr = f'(Type: {tokenType.upper()}, Position: {positionStr}, Value: {value})'
    assert repr(token) == tokenStr
