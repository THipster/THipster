from parser.dsl_parser.Lexer import Lexer, DSLParserNoEndingQuotes
from parser.dsl_parser.Token import TOKENTYPES as TT
import pytest


def __getTokenString(
    fileName: str,
    ln: int,
    col: int,
    tokenType: TT,
    value: str | None = None,
):
    positionStr = f'(File : {fileName}, Ln {ln}, Col {col})'
    tokenStr = f'(Type: {tokenType.value}, Position: {positionStr}'
    if value:
        tokenStr += f', Value: {value}'
    tokenStr += ')'
    return tokenStr


def __single_token_test(
    input: str,
    token: str,
    tokenValue: str | None = None,
    isNewLine: bool = False,
):

    lineValue, columnValue = 1, len(input)+1
    if isNewLine:
        lineValue, columnValue = 2, 1
    expectedOutput = [
        __getTokenString('test_file.thips', 1, 1, token, tokenValue),
        __getTokenString(
            'test_file.thips', lineValue,
            columnValue, TT.NEWLINE,
        ),
        __getTokenString('test_file.thips', lineValue+1, 1, TT.EOF),
    ]
    lexer = Lexer({'test_file.thips': input})
    lexer.run()
    output = lexer.tokenList

    assert len(output) == len(expectedOutput)
    for i in range(len(expectedOutput)):
        assert repr(output[i]) == expectedOutput[i]


def test_create_lexer():
    files = {
        'file_name_1': 'file_content_1',
        'file_name_2': 'file_content_2',
    }
    lexer = Lexer(files)

    assert isinstance(lexer, Lexer)
    assert lexer.files == files
    assert len(lexer.tokenList) == 0


def test_lex_colon():
    __single_token_test(':', TT.COLON)


def test_lex_comma():
    __single_token_test(',', TT.COMMA)


def test_lex_brackets():
    lexer = Lexer({'': ''})
    input = '[toto]'
    expectedOutput = [
        __getTokenString('file', 1, 1, TT.BRACKETS_START),
        __getTokenString('file', 1, 2, TT.STRING, 'toto'),
        __getTokenString('file', 1, 6, TT.BRACKETS_END),
        __getTokenString('file', 1, 7, TT.NEWLINE),
        __getTokenString('file', 2, 1, TT.EOF),
    ]
    lexer.lex(input, 'file')
    output = lexer.tokenList

    assert len(output) == len(expectedOutput)
    for i in range(len(expectedOutput)):
        assert repr(output[i]) == expectedOutput[i]


def test_lex_quoted_string():
    lexer = Lexer({'': ''})

    input = '"bucket number 21""bucket number 22"'
    expectedOutput = [
        __getTokenString('file', 1, 2, TT.STRING, 'bucket number 21'),
        __getTokenString('file', 1, 20, TT.STRING, 'bucket number 22'),
        __getTokenString('file', 1, 37, TT.NEWLINE),
        __getTokenString('file', 2, 1, TT.EOF),
    ]
    lexer.lex(input, 'file')
    output = lexer.tokenList

    assert len(output) == len(expectedOutput)
    for i in range(len(expectedOutput)):
        assert repr(output[i]) == expectedOutput[i]

    lexer = Lexer({'': ''})
    input = "'bucket number 21'"
    expectedOutput = [
        __getTokenString('file', 1, 2, TT.STRING, 'bucket number 21'),
        __getTokenString('file', 1, 19, TT.NEWLINE),
        __getTokenString('file', 2, 1, TT.EOF),
    ]
    lexer.lex(input, 'file')
    output = lexer.tokenList

    assert len(output) == len(expectedOutput)
    for i in range(len(expectedOutput)):
        assert repr(output[i]) == expectedOutput[i]

    lexer = Lexer({'': ''})
    input = "'bucket number \"21\"'"
    expectedOutput = [
        __getTokenString('file', 1, 2, TT.STRING, 'bucket number "21"'),
        __getTokenString('file', 1, 21, TT.NEWLINE),
        __getTokenString('file', 2, 1, TT.EOF),
    ]
    lexer.lex(input, 'file')
    output = lexer.tokenList

    assert len(output) == len(expectedOutput)
    for i in range(len(expectedOutput)):
        assert repr(output[i]) == expectedOutput[i]

    lexer = Lexer({'': ''})
    input = '"bucket number \'21\'"'
    expectedOutput = [
        __getTokenString('file', 1, 2, TT.STRING, "bucket number '21'"),
        __getTokenString('file', 1, 21, TT.NEWLINE),
        __getTokenString('file', 2, 1, TT.EOF),
    ]
    lexer.lex(input, 'file')
    output = lexer.tokenList

    assert len(output) == len(expectedOutput)
    for i in range(len(expectedOutput)):
        assert repr(output[i]) == expectedOutput[i]


def test_lex_quoted_string_error():
    input = {
        'file': 'bucket nom-8: "amount: 5 \n\t',
    }
    lexer = Lexer(input)
    with pytest.raises(DSLParserNoEndingQuotes):
        lexer.run()


def test_lex_multiline_input():
    input = {
        'file': 'bucket nom-\\\n8:',
    }
    expectedOutput = [
        __getTokenString('file', 1, 1, TT.STRING, 'bucket'),
        __getTokenString('file', 1, 7, TT.WHITESPACE),
        __getTokenString('file', 1, 8, TT.STRING, 'nom-8'),
        __getTokenString('file', 2, 2, TT.COLON),
        __getTokenString('file', 2, 3, TT.NEWLINE),
        __getTokenString('file', 3, 1, TT.EOF),
    ]
    lexer = Lexer(input)
    lexer.run()
    output = lexer.tokenList

    assert len(output) == len(expectedOutput)
    for i in range(len(expectedOutput)):
        assert repr(output[i]) == expectedOutput[i]


def test_lex_var():
    input = '#variable'
    expectedOutput = [
        __getTokenString('file', 1, 2, TT.VAR, 'variable'),
        __getTokenString('file', 1, 10, TT.NEWLINE),
        __getTokenString('file', 2, 1, TT.EOF),
    ]
    lexer = Lexer({'': ''})
    lexer.lex(input, 'file')
    output = lexer.tokenList

    assert len(output) == len(expectedOutput)
    for i in range(len(expectedOutput)):
        assert repr(output[i]) == expectedOutput[i]


def test_lex_newline():
    __single_token_test('\n', TT.NEWLINE, isNewLine=True)


def test_lex_tab():
    __single_token_test('\t', TT.TAB)


def test_lex_4_whitespaces_as_tab():
    input = {
        'file': '    \n\t',
    }
    expectedOutput = [
        __getTokenString('file', 1, 1, TT.TAB),
        __getTokenString('file', 1, 5, TT.NEWLINE),
        __getTokenString('file', 2, 1, TT.TAB),
        __getTokenString('file', 2, 2, TT.NEWLINE),
        __getTokenString('file', 3, 1, TT.EOF),
    ]
    lexer = Lexer(input)
    output = lexer.run()

    assert len(output) == len(expectedOutput)
    for i in range(len(expectedOutput)):
        assert repr(output[i]) == expectedOutput[i]


def test_lex_2_4_whitespaces_as_tabs():
    input = {
        'file': '        \n\t',
    }
    expectedOutput = [
        __getTokenString('file', 1, 1, TT.TAB),
        __getTokenString('file', 1, 5, TT.TAB),
        __getTokenString('file', 1, 9, TT.NEWLINE),
        __getTokenString('file', 2, 1, TT.TAB),
        __getTokenString('file', 2, 2, TT.NEWLINE),
        __getTokenString('file', 3, 1, TT.EOF),
    ]
    lexer = Lexer(input)
    output = lexer.run()

    assert len(output) == len(expectedOutput)
    for i in range(len(expectedOutput)):
        assert repr(output[i]) == expectedOutput[i]


def test_lex_dash():
    __single_token_test('-', TT.DASH)


def test_lex_amount():
    input = 'amount '
    expectedOutput = [
        __getTokenString('file', 1, 1, TT.AMOUNT),
        __getTokenString('file', 1, 7, TT.WHITESPACE),
        __getTokenString('file', 1, 8, TT.NEWLINE),
        __getTokenString('file', 2, 1, TT.EOF),
    ]
    lexer = Lexer({'': ''})
    lexer.lex(input, 'file')
    output = lexer.tokenList

    assert len(output) == len(expectedOutput)
    for i in range(len(expectedOutput)):
        assert repr(output[i]) == expectedOutput[i]


def test_lex_and():
    __single_token_test('and', TT.AND)


def test_lex_if():
    __single_token_test('if', TT.IF)


def test_lex_elif():
    __single_token_test('elif', TT.ELIF)


def test_lex_else():
    __single_token_test('else', TT.ELSE)


def test_lex_if_else():
    input = 'if condition else something'
    expectedOutput = [
        __getTokenString('file', 1, 1, TT.IF),
        __getTokenString('file', 1, 3, TT.WHITESPACE),
        __getTokenString('file', 1, 4, TT.STRING, 'condition'),
        __getTokenString('file', 1, 13, TT.WHITESPACE),
        __getTokenString('file', 1, 14, TT.ELSE),
        __getTokenString('file', 1, 18, TT.WHITESPACE),
        __getTokenString('file', 1, 19, TT.STRING, 'something'),
        __getTokenString('file', 1, 28, TT.NEWLINE),
        __getTokenString('file', 2, 1, TT.EOF),
    ]
    lexer = Lexer({'': ''})
    lexer.lex(input, 'file')
    output = lexer.tokenList

    assert len(output) == len(expectedOutput)
    for i in range(len(expectedOutput)):
        assert repr(output[i]) == expectedOutput[i]


def test_lex_or():
    __single_token_test('or', TT.OR)


def test_lex_true():
    __single_token_test('true', TT.BOOLEAN, tokenValue='true')


def test_lex_false():
    __single_token_test('false', TT.BOOLEAN, tokenValue='false')


def test_lex_int():
    __single_token_test('8', TT.INT, tokenValue='8')


def test_lex_float():
    __single_token_test('4.5', TT.FLOAT, tokenValue='4.5')


def test_lex_string():
    input = 'bucket nom-8'
    expectedOutput = [
        __getTokenString('file', 1, 1, TT.STRING, 'bucket'),
        __getTokenString('file', 1, 7, TT.WHITESPACE),
        __getTokenString('file', 1, 8, TT.STRING, 'nom-8'),
        __getTokenString('file', 1, 13, TT.NEWLINE),
        __getTokenString('file', 2, 1, TT.EOF),
    ]
    lexer = Lexer({'': ''})
    lexer.lex(input, 'file')
    output = lexer.tokenList

    assert len(output) == len(expectedOutput)
    for i in range(len(expectedOutput)):
        assert repr(output[i]) == expectedOutput[i]


def test_run_lexer():
    input = {
        'file': 'bucket nom-8: amount: 5 \n\t',
        'file2': 'network aaaa-#i: nombre: 2 4.5\n\t- property',
    }
    expectedOutput = [
        __getTokenString('file', 1, 1, TT.STRING, 'bucket'),
        __getTokenString('file', 1, 7, TT.WHITESPACE),
        __getTokenString('file', 1, 8, TT.STRING, 'nom-8'),
        __getTokenString('file', 1, 13, TT.COLON),
        __getTokenString('file', 1, 14, TT.WHITESPACE),
        __getTokenString('file', 1, 15, TT.AMOUNT),
        __getTokenString('file', 1, 21, TT.COLON),
        __getTokenString('file', 1, 22, TT.WHITESPACE),
        __getTokenString('file', 1, 23, TT.INT, '5'),
        __getTokenString('file', 1, 24, TT.WHITESPACE),
        __getTokenString('file', 1, 25, TT.NEWLINE),
        __getTokenString('file', 2, 1, TT.TAB),
        __getTokenString('file', 2, 2, TT.NEWLINE),
        __getTokenString('file', 3, 1, TT.EOF),

        __getTokenString('file2', 1, 1, TT.STRING, 'network'),
        __getTokenString('file2', 1, 8, TT.WHITESPACE),
        __getTokenString('file2', 1, 9, TT.STRING, 'aaaa-'),
        __getTokenString('file2', 1, 15, TT.VAR, 'i'),
        __getTokenString('file2', 1, 16, TT.COLON),
        __getTokenString('file2', 1, 17, TT.WHITESPACE),
        __getTokenString('file2', 1, 18, TT.STRING, 'nombre'),
        __getTokenString('file2', 1, 24, TT.COLON),
        __getTokenString('file2', 1, 25, TT.WHITESPACE),
        __getTokenString('file2', 1, 26, TT.INT, '2'),
        __getTokenString('file2', 1, 27, TT.WHITESPACE),
        __getTokenString('file2', 1, 28, TT.FLOAT, '4.5'),
        __getTokenString('file2', 1, 31, TT.NEWLINE),
        __getTokenString('file2', 2, 1, TT.TAB),
        __getTokenString('file2', 2, 2, TT.DASH),
        __getTokenString('file2', 2, 3, TT.WHITESPACE),
        __getTokenString('file2', 2, 4, TT.STRING, 'property'),
        __getTokenString('file2', 2, 12, TT.NEWLINE),
        __getTokenString('file2', 3, 1, TT.EOF),
    ]
    lexer = Lexer(input)
    output = lexer.run()

    assert len(output) == len(expectedOutput)
    for i in range(len(expectedOutput)):
        assert repr(output[i]) == expectedOutput[i]


def test_run_lexer_var_in_name():
    input = {
        'file': 'bucket nom-#test \n\t toto: tata',
    }
    expectedOutput = [
        __getTokenString('file', 1, 1, TT.STRING, 'bucket'),
        __getTokenString('file', 1, 7, TT.WHITESPACE),
        __getTokenString('file', 1, 8, TT.STRING, 'nom-'),
        __getTokenString('file', 1, 13, TT.VAR, 'test'),
        __getTokenString('file', 1, 17, TT.WHITESPACE),
        __getTokenString('file', 1, 18, TT.NEWLINE),
        __getTokenString('file', 2, 1, TT.TAB),
        __getTokenString('file', 2, 2, TT.WHITESPACE),
        __getTokenString('file', 2, 3, TT.STRING, 'toto'),
        __getTokenString('file', 2, 7, TT.COLON),
        __getTokenString('file', 2, 8, TT.WHITESPACE),
        __getTokenString('file', 2, 9, TT.STRING, 'tata'),
        __getTokenString('file', 2, 13, TT.NEWLINE),
        __getTokenString('file', 3, 1, TT.EOF),
    ]
    lexer = Lexer(input)
    output = lexer.run()

    assert len(output) == len(expectedOutput)
    for i in range(len(expectedOutput)):
        assert repr(output[i]) == expectedOutput[i]
