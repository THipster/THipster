from parser.dsl_parser.Lexer import Lexer
from parser.dsl_parser.Token import TOKENTYPES as TT
import pytest


def getTokenString(fileName: str, ln: int, col: int, tokenType: str, value: str = None):
    positionStr = f'(File : {fileName}, Ln {ln}, Col {col})'
    tokenStr = f'(Type: {tokenType.upper()}, Position: {positionStr}'
    if value:
        tokenStr += f', Value: {value}'
    tokenStr += ')'
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


def test_lex_column():
    input = ':'
    expectedOutput = [
        getTokenString('file', 1, 1, TT.COLUMN.value),
        getTokenString('file', 1, 2, TT.NEWLINE.value),
        getTokenString('file', 2, 1, TT.EOF.value),
    ]
    lexer = Lexer('')
    lexer.lex(input, 'file')
    output = lexer.tokenList

    assert len(output) == 3
    for i in range(len(expectedOutput)):
        assert repr(output[i]) == expectedOutput[i]


def test_lex_quoted_string():
    input = '"bucket number 21"'
    expectedOutput = [
        getTokenString('file', 1, 2, TT.STRING.value, 'bucket number 21'),
        getTokenString('file', 1, 19, TT.NEWLINE.value),
        getTokenString('file', 2, 1, TT.EOF.value),
    ]
    lexer = Lexer('')
    lexer.lex(input, 'file')
    output = lexer.tokenList

    assert len(output) == 3
    for i in range(len(expectedOutput)):
        assert repr(output[i]) == expectedOutput[i]


def test_lex_quoted_string_error():
    input = {
        'file': 'bucket nom-8: "amount: 5 \n\t',
    }
    lexer = Lexer(input)
    with pytest.raises(SyntaxError):
        lexer.run()


def test_lex_var():
    input = '#variable'
    expectedOutput = [
        getTokenString('file', 1, 2, TT.VAR.value, 'variable'),
        getTokenString('file', 1, 10, TT.NEWLINE.value),
        getTokenString('file', 2, 1, TT.EOF.value),
    ]
    lexer = Lexer('')
    lexer.lex(input, 'file')
    output = lexer.tokenList

    assert len(output) == 3
    for i in range(len(expectedOutput)):
        assert repr(output[i]) == expectedOutput[i]


def test_lex_newline():
    input = '\n'
    expectedOutput = [
        getTokenString('file', 1, 1, TT.NEWLINE.value),
        getTokenString('file', 2, 1, TT.NEWLINE.value),
        getTokenString('file', 3, 1, TT.EOF.value),
    ]
    lexer = Lexer('')
    lexer.lex(input, 'file')
    output = lexer.tokenList

    assert len(output) == 3
    for i in range(len(expectedOutput)):
        assert repr(output[i]) == expectedOutput[i]


def test_lex_tab():
    input = '\t'
    expectedOutput = [
        getTokenString('file', 1, 1, TT.TAB.value),
        getTokenString('file', 1, 2, TT.NEWLINE.value),
        getTokenString('file', 2, 1, TT.EOF.value),
    ]
    lexer = Lexer('')
    lexer.lex(input, 'file')
    output = lexer.tokenList

    assert len(output) == 3
    for i in range(len(expectedOutput)):
        assert repr(output[i]) == expectedOutput[i]


def test_lex_4_whitespaces_as_tab():
    input = {
        'file': '    \n\t',
    }
    expectedOutput = [
        getTokenString('file', 1, 1, TT.TAB.value),
        getTokenString('file', 1, 2, TT.NEWLINE.value),
        getTokenString('file', 2, 1, TT.TAB.value),
        getTokenString('file', 2, 2, TT.NEWLINE.value),
        getTokenString('file', 3, 1, TT.EOF.value),
    ]
    lexer = Lexer(input)
    output = lexer.run()

    assert len(output) == 5
    for i in range(len(expectedOutput)):
        assert repr(output[i]) == expectedOutput[i]


def test_lex_2_4_whitespaces_as_tabs():
    input = {
        'file': '        \n\t',
    }
    expectedOutput = [
        getTokenString('file', 1, 1, TT.TAB.value),
        getTokenString('file', 1, 2, TT.TAB.value),
        getTokenString('file', 1, 3, TT.NEWLINE.value),
        getTokenString('file', 2, 1, TT.TAB.value),
        getTokenString('file', 2, 2, TT.NEWLINE.value),
        getTokenString('file', 3, 1, TT.EOF.value),
    ]
    lexer = Lexer(input)
    output = lexer.run()

    assert len(output) == 6
    for i in range(len(expectedOutput)):
        assert repr(output[i]) == expectedOutput[i]


def test_lex_dash():
    input = '-'
    expectedOutput = [
        getTokenString('file', 1, 1, TT.DASH.value),
        getTokenString('file', 1, 2, TT.NEWLINE.value),
        getTokenString('file', 2, 1, TT.EOF.value),
    ]
    lexer = Lexer('')
    lexer.lex(input, 'file')
    output = lexer.tokenList

    assert len(output) == 3
    for i in range(len(expectedOutput)):
        assert repr(output[i]) == expectedOutput[i]


def test_lex_amount():
    input = 'amount '
    expectedOutput = [
        getTokenString('file', 1, 1, TT.AMOUNT.value),
        getTokenString('file', 1, 8, TT.NEWLINE.value),
        getTokenString('file', 2, 1, TT.EOF.value),
    ]
    lexer = Lexer('')
    lexer.lex(input, 'file')
    output = lexer.tokenList

    assert len(output) == 3
    for i in range(len(expectedOutput)):
        assert repr(output[i]) == expectedOutput[i]


def test_lex_if():
    input = 'if '
    expectedOutput = [
        getTokenString('file', 1, 1, TT.IF.value),
        getTokenString('file', 1, 4, TT.NEWLINE.value),
        getTokenString('file', 2, 1, TT.EOF.value),
    ]
    lexer = Lexer('')
    lexer.lex(input, 'file')
    output = lexer.tokenList

    assert len(output) == 3
    for i in range(len(expectedOutput)):
        assert repr(output[i]) == expectedOutput[i]


def test_lex_elif():
    input = 'elif '
    expectedOutput = [
        getTokenString('file', 1, 1, TT.ELIF.value),
        getTokenString('file', 1, 6, TT.NEWLINE.value),
        getTokenString('file', 2, 1, TT.EOF.value),
    ]
    lexer = Lexer('')
    lexer.lex(input, 'file')
    output = lexer.tokenList

    assert len(output) == 3
    for i in range(len(expectedOutput)):
        assert repr(output[i]) == expectedOutput[i]


def test_lex_else():
    input = 'else '
    expectedOutput = [
        getTokenString('file', 1, 1, TT.ELSE.value),
        getTokenString('file', 1, 6, TT.NEWLINE.value),
        getTokenString('file', 2, 1, TT.EOF.value),
    ]
    lexer = Lexer('')
    lexer.lex(input, 'file')
    output = lexer.tokenList

    assert len(output) == 3
    for i in range(len(expectedOutput)):
        assert repr(output[i]) == expectedOutput[i]


def test_lex_if_else():
    input = 'if condition else something'
    expectedOutput = [
        getTokenString('file', 1, 1, TT.IF.value),
        getTokenString('file', 1, 4, TT.STRING.value, 'condition'),
        getTokenString('file', 1, 14, TT.ELSE.value),
        getTokenString('file', 1, 19, TT.STRING.value, 'something'),
        getTokenString('file', 1, 28, TT.NEWLINE.value),
        getTokenString('file', 2, 1, TT.EOF.value),
    ]
    lexer = Lexer('')
    lexer.lex(input, 'file')
    output = lexer.tokenList

    assert len(output) == 6
    for i in range(len(expectedOutput)):
        assert repr(output[i]) == expectedOutput[i]


def test_lex_true():
    input = 'true '
    expectedOutput = [
        getTokenString('file', 1, 1, TT.BOOLEAN.value, 'true'),
        getTokenString('file', 1, 6, TT.NEWLINE.value),
        getTokenString('file', 2, 1, TT.EOF.value),
    ]
    lexer = Lexer('')
    lexer.lex(input, 'file')
    output = lexer.tokenList

    assert len(output) == 3
    for i in range(len(expectedOutput)):
        assert repr(output[i]) == expectedOutput[i]


def test_lex_false():
    input = 'false '
    expectedOutput = [
        getTokenString('file', 1, 1, TT.BOOLEAN.value, 'false'),
        getTokenString('file', 1, 7, TT.NEWLINE.value),
        getTokenString('file', 2, 1, TT.EOF.value),
    ]
    lexer = Lexer('')
    lexer.lex(input, 'file')
    output = lexer.tokenList

    assert len(output) == 3
    for i in range(len(expectedOutput)):
        assert repr(output[i]) == expectedOutput[i]


def test_lex_int():
    input = '8'
    expectedOutput = [
        getTokenString('file', 1, 1, TT.INT.value, '8'),
        getTokenString('file', 1, 2, TT.NEWLINE.value),
        getTokenString('file', 2, 1, TT.EOF.value),
    ]
    lexer = Lexer('')
    lexer.lex(input, 'file')
    output = lexer.tokenList

    assert len(output) == 3
    for i in range(len(expectedOutput)):
        assert repr(output[i]) == expectedOutput[i]


def test_lex_float():
    input = '4.5'
    expectedOutput = [
        getTokenString('file', 1, 1, TT.FLOAT.value, '4.5'),
        getTokenString('file', 1, 4, TT.NEWLINE.value),
        getTokenString('file', 2, 1, TT.EOF.value),
    ]
    lexer = Lexer('')
    lexer.lex(input, 'file')
    output = lexer.tokenList

    assert len(output) == 3
    for i in range(len(expectedOutput)):
        assert repr(output[i]) == expectedOutput[i]


def test_lex_string():
    input = 'bucket nom-8'
    expectedOutput = [
        getTokenString('file', 1, 1, TT.STRING.value, 'bucket'),
        getTokenString('file', 1, 8, TT.STRING.value, 'nom-8'),
        getTokenString('file', 1, 13, TT.NEWLINE.value),
        getTokenString('file', 2, 1, TT.EOF.value),
    ]
    lexer = Lexer('')
    lexer.lex(input, 'file')
    output = lexer.tokenList

    assert len(output) == 4
    for i in range(len(expectedOutput)):
        assert repr(output[i]) == expectedOutput[i]


def test_run_lexer():
    input = {
        'file': 'bucket nom-8: amount: 5 \n\t',
        'file2': 'network aaaa-#i: nombre: 2 4.5\n\t- property',
    }
    expectedOutput = [
        getTokenString('file', 1, 1, TT.STRING.value, 'bucket'),
        getTokenString('file', 1, 8, TT.STRING.value, 'nom-8'),
        getTokenString('file', 1, 13, TT.COLUMN.value),
        getTokenString('file', 1, 15, TT.AMOUNT.value),
        getTokenString('file', 1, 21, TT.COLUMN.value),
        getTokenString('file', 1, 23, TT.INT.value, '5'),
        getTokenString('file', 1, 25, TT.NEWLINE.value),
        getTokenString('file', 2, 1, TT.TAB.value),
        getTokenString('file', 2, 2, TT.NEWLINE.value),
        getTokenString('file', 3, 1, TT.EOF.value),

        getTokenString('file2', 1, 1, TT.STRING.value, 'network'),
        getTokenString('file2', 1, 9, TT.STRING.value, 'aaaa-'),
        getTokenString('file2', 1, 15, TT.VAR.value, 'i'),
        getTokenString('file2', 1, 16, TT.COLUMN.value),
        getTokenString('file2', 1, 18, TT.STRING.value, 'nombre'),
        getTokenString('file2', 1, 24, TT.COLUMN.value),
        getTokenString('file2', 1, 26, TT.INT.value, '2'),
        getTokenString('file2', 1, 28, TT.FLOAT.value, '4.5'),
        getTokenString('file2', 1, 31, TT.NEWLINE.value),
        getTokenString('file2', 2, 1, TT.TAB.value),
        getTokenString('file2', 2, 2, TT.DASH.value),
        getTokenString('file2', 2, 4, TT.STRING.value, 'property'),
        getTokenString('file2', 2, 12, TT.NEWLINE.value),
        getTokenString('file2', 3, 1, TT.EOF.value),
    ]
    lexer = Lexer(input)
    output = lexer.run()

    assert len(output) == 24
    for i in range(len(expectedOutput)):
        assert repr(output[i]) == expectedOutput[i]


def test_run_lexer_var_in_name():
    input = {
        'file': 'bucket nom-#test \n\t toto: tata',
    }
    expectedOutput = [
        getTokenString('file', 1, 1, 'STRING', 'bucket'),
        getTokenString('file', 1, 8, 'STRING', 'nom-'),
        getTokenString('file', 1, 13, 'VAR', 'test'),
        getTokenString('file', 1, 18, 'NEWLINE'),
        getTokenString('file', 2, 1, 'TAB'),
        getTokenString('file', 2, 3, 'STRING', 'toto'),
        getTokenString('file', 2, 7, 'COLUMN'),
        getTokenString('file', 2, 9, 'STRING', 'tata'),
        getTokenString('file', 2, 13, 'NEWLINE'),
        getTokenString('file', 3, 1, 'EOF'),
    ]
    lexer = Lexer(input)
    output = lexer.run()

    assert len(output) == 10
    for i in range(len(expectedOutput)):
        assert repr(output[i]) == expectedOutput[i]
