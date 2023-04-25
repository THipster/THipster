from parser.dsl_parser.Lexer import Lexer
import pytest


def getTokenString(fileName: str, ln: int, col: int, tokenType: str, value: str = None):
    positionStr = f'File : {fileName}, Ln {ln}, Col {col}'
    tokenStr = f'Position: {positionStr}, Type: {tokenType}'
    if value:
        return tokenStr + f', Value: {value}'
    else:
        return tokenStr


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
    tokenType = 'STRING'
    value = 'babyfoot'
    lexer = Lexer('')
    lexer.addTokenToList(1, tokenType, value)

    tokenStr = getTokenString('', 1, 1, tokenType, value)
    assert len(lexer.tokenList) == 1
    assert str(lexer.tokenList[0]) == tokenStr


def test_handle_current_token():
    lexer = Lexer('')
    lexer.handleCurrentToken('if', 1)
    lexer.handleCurrentToken('babyfoot', 4)
    lexer.handleCurrentToken('amount', 12)
    assert len(lexer.tokenList) == 3
    assert lexer.tokenList[0].tokenType == 'IF'
    assert lexer.tokenList[2].tokenType == 'AMOUNT'


def test_lex():
    input = 'bucket nom-8 \n\t'
    expectedOutput = [
        getTokenString('file', 1, 1, 'STRING', 'bucket'),
        getTokenString('file', 1, 8, 'STRING', 'nom-8'),
        getTokenString('file', 1, 14, 'NEWLINE'),
        getTokenString('file', 2, 1, 'TAB'),
        getTokenString('file', 2, 2, 'EOF'),
    ]
    lexer = Lexer('')
    lexer.lex(input, 'file')
    output = lexer.tokenList

    assert len(output) == 5
    for i in range(len(expectedOutput)):
        assert str(output[i]) == expectedOutput[i]


def test_lex_quoted_string():
    input = {
        'file': 'bucket nom-8: "amount: 5" \n\t',
    }
    expectedOutput = [
        getTokenString('file', 1, 1, 'STRING', 'bucket'),
        getTokenString('file', 1, 8, 'STRING', 'nom-8'),
        getTokenString('file', 1, 13, 'COLUMN'),
        getTokenString('file', 1, 16, 'STRING', 'amount: 5'),
        getTokenString('file', 1, 27, 'NEWLINE'),
        getTokenString('file', 2, 1, 'TAB'),
        getTokenString('file', 2, 2, 'EOF'),
    ]
    lexer = Lexer(input)
    output = lexer.run()

    assert len(output) == 7
    for i in range(len(expectedOutput)):
        assert str(output[i]) == expectedOutput[i]


def test_lex_quoted_string_error():
    input = {
        'file': 'bucket nom-8: "amount: 5 \n\t',
    }
    lexer = Lexer(input)
    with pytest.raises(SyntaxError):
        lexer.run()


def test_run_lexer():
    input = {
        'file': 'bucket nom-8: amount: 5 \n\t',
        'file2': 'network aaaa-#i: nombre: 2 4.5\n\t- property',
    }
    expectedOutput = [
        getTokenString('file', 1, 1, 'STRING', 'bucket'),
        getTokenString('file', 1, 8, 'STRING', 'nom-8'),
        getTokenString('file', 1, 13, 'COLUMN'),
        getTokenString('file', 1, 15, 'AMOUNT'),
        getTokenString('file', 1, 21, 'COLUMN'),
        getTokenString('file', 1, 23, 'INT', '5'),
        getTokenString('file', 1, 25, 'NEWLINE'),
        getTokenString('file', 2, 1, 'TAB'),
        getTokenString('file', 2, 2, 'EOF'),

        getTokenString('file2', 1, 1, 'STRING', 'network'),
        getTokenString('file2', 1, 9, 'STRING', 'aaaa-'),
        getTokenString('file2', 1, 15, 'VAR', 'i'),
        getTokenString('file2', 1, 16, 'COLUMN'),
        getTokenString('file2', 1, 18, 'STRING', 'nombre'),
        getTokenString('file2', 1, 24, 'COLUMN'),
        getTokenString('file2', 1, 26, 'INT', '2'),
        getTokenString('file2', 1, 28, 'FLOAT', '4.5'),
        getTokenString('file2', 1, 31, 'NEWLINE'),
        getTokenString('file2', 2, 1, 'TAB'),
        getTokenString('file2', 2, 2, 'DASH'),
        getTokenString('file2', 2, 4, 'STRING', 'property'),
        getTokenString('file2', 2, 12, 'EOF'),
    ]
    lexer = Lexer(input)
    output = lexer.run()

    assert len(output) == 22
    for i in range(len(expectedOutput)):
        assert str(output[i]) == expectedOutput[i]
