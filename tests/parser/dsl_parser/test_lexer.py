from parser.dsl_parser.Lexer import Lexer
from parser.dsl_parser.Token import Token
from engine.ParsedFile import Position


def test_create_lexer():
    files = {
        'file_name_1': 'file_content_1',
        'file_name_2': 'file_content_2',
    }
    lexer = Lexer(files)

    assert isinstance(lexer, Lexer)
    assert lexer.files == files
    assert len(lexer.tokenList) == 0


def test_add_token_to_list():
    lexer = Lexer('')
    lexer.addTokenToList(1, 'STRING', 'babyfoot')
    assert len(lexer.tokenList) == 1
    assert lexer.tokenList[0] == Token(
        Position('', 1, 1), 'STRING', 'babyfoot',
    )


def test_handle_current_token():
    lexer = Lexer('')
    lexer.handleCurrentToken('if', 1)
    lexer.handleCurrentToken('babyfoot', 4)
    assert len(lexer.tokenList) == 2


def test_lex():
    input = 'bucket nom-8 \n\t'
    expectedOutput = [
        Token(Position('file', 1, 1), 'STRING', 'bucket'),
        Token(Position('file', 1, 8), 'STRING', 'nom-8'),
        Token(Position('file', 1, 14), 'NEWLINE'),
        Token(Position('file', 2, 1), 'TAB'),
        Token(Position('file', 2, 2), 'EOF'),
    ]
    lexer = Lexer('')
    lexer.lex(input, 'file')
    output = lexer.tokenList

    assert len(output) == 5
    for i in range(len(expectedOutput)):
        assert output[i] == expectedOutput[i]


def test_run_lexer():
    input = {
        'file': 'bucket nom-8 \n\t',
        'file2': 'network aaaa-#i: nombre: 2 4.5',
    }
    expectedOutput = [
        Token(Position('file', 1, 1), 'STRING', 'bucket'),
        Token(Position('file', 1, 8), 'STRING', 'nom-8'),
        Token(Position('file', 1, 14), 'NEWLINE'),
        Token(Position('file', 2, 1), 'TAB'),
        Token(Position('file', 2, 2), 'EOF'),

        Token(Position('file2', 1, 1), 'STRING', 'network'),
        Token(Position('file2', 1, 9), 'STRING', 'aaaa-'),
        Token(Position('file2', 1, 15), 'VAR', 'i'),
        Token(Position('file2', 1, 16), 'COLUMN'),
        Token(Position('file2', 1, 18), 'STRING', 'nombre'),
        Token(Position('file2', 1, 24), 'COLUMN'),
        Token(Position('file2', 1, 26), 'INT', '2'),
        Token(Position('file2', 1, 28), 'FLOAT', '4.5'),
        Token(Position('file2', 1, 31), 'EOF'),
    ]
    lexer = Lexer(input)
    output = lexer.run()

    assert len(output) == 14
    for i in range(len(expectedOutput)):
        assert output[i] == expectedOutput[i]
