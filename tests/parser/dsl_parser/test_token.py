from thipster.engine.parsed_file import Position
from thipster.parser.dsl_parser.token import Token


def test_create_token():
    position = Position(filename='testFile', ln=2, col=6)
    tokenType = 'test_type'
    value = 'test_value'

    token = Token(position, token_type=tokenType, value=value)

    assert isinstance(token, Token)
    assert token.position == position
    assert token.token_type == tokenType
    assert token.value == value


def test_token_to_string():
    position = Position(filename='testFile', ln=2, col=6)
    positionStr = '(File : testFile, Ln 2, Col 6)'
    assert str(position) == positionStr

    tokenType = 'test_type'
    value = 'test_value'
    token = Token(position, token_type=tokenType, value=value)
    tokenStr = f'(Type: {str(tokenType)}, Position: {positionStr}, Value: {value})'
    assert repr(token) == tokenStr
