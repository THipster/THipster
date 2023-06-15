from thipster.engine.parsed_file import Position
from thipster.parser.dsl_parser.token import Token


def test_create_token():
    position = Position(filename='testFile', ln=2, col=6)
    token_type = 'test_type'
    value = 'test_value'

    token = Token(position, token_type=token_type, value=value)

    assert isinstance(token, Token)
    assert token.position == position
    assert token.token_type == token_type
    assert token.value == value


def test_token_to_string():
    position = Position(filename='testFile', ln=2, col=6)
    position_str = '(File : testFile, Ln 2, Col 6)'
    assert str(position) == position_str

    token_type = 'test_type'
    value = 'test_value'
    token = Token(position, token_type=token_type, value=value)
    token_str = f'(Type: {str(token_type)}, Position: {position_str}, Value: {value})'
    assert repr(token) == token_str
