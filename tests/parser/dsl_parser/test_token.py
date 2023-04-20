from parser.dsl_parser.Token import Token
from engine.ParsedFile import Position

def test_create_token():
    position = Position(ln=2,col=6)
    type = 'test_type'
    value = 'test_value'

    token = Token(position, type=type, value=value,)

    assert isinstance(token,Token)
    assert token.position == position
    assert token.type == type
    assert token.value == value
