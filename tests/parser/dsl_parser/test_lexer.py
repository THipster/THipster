import pytest

from thipster.parser.dsl_parser.exceptions import DSLParserNoEndingQuotesError
from thipster.parser.dsl_parser.lexer import Lexer
from thipster.parser.dsl_parser.token import TOKENTYPES as TT


def __get_token_string(
    file_name: str,
    ln: int,
    col: int,
    token_type: TT,
    value: str | None = None,
):
    position_str = f'(File : {file_name}, Ln {ln}, Col {col})'
    token_str = f'(Type: {token_type.value}, Position: {position_str}'
    if value:
        token_str += f', Value: {value}'
    token_str += ')'
    return token_str


def __single_token_test(
    input: str,
    token: str,
    token_value: str | None = None,
    is_newline: bool = False,
):

    line_value, column_value = 1, len(input)+1
    if is_newline:
        line_value, column_value = 2, 1
    expected_output = [
        __get_token_string('test_file.thips', 1, 1, token, token_value),
        __get_token_string(
            'test_file.thips', line_value,
            column_value, TT.NEWLINE,
        ),
        __get_token_string('test_file.thips', line_value+1, 1, TT.EOF),
    ]
    lexer = Lexer({'test_file.thips': input})
    lexer.run()
    output = lexer.tokenList

    assert len(output) == len(expected_output)
    for i in range(len(expected_output)):
        assert repr(output[i]) == expected_output[i]


def test_create_lexer():
    files = {
        'file_name_1': 'file_content_1',
        'file_name_2': 'file_content_2',
    }
    lexer = Lexer(files)

    assert isinstance(lexer, Lexer)
    assert lexer.files == files
    assert len(lexer.tokenList) == 0


def test_lex_single_tokens():
    for input, output in {
        ':': TT.COLON,
        ',': TT.COMMA,
        '+': TT.PLUS,
        '-': TT.MINUS,
        '=': TT.EQ,
        '*': TT.MUL,
        '/': TT.DIV,
        '!': TT.EXCLAMATION,
        '<': TT.LT,
        '>': TT.GT,
        '^': TT.POW,
    }.items():
        __single_token_test(input, output)


def test_lex_brackets():
    lexer = Lexer({'': ''})
    input = '[toto]'
    expected_output = [
        __get_token_string('file', 1, 1, TT.BRACKETS_START),
        __get_token_string('file', 1, 2, TT.STRING, 'toto'),
        __get_token_string('file', 1, 6, TT.BRACKETS_END),
        __get_token_string('file', 1, 7, TT.NEWLINE),
        __get_token_string('file', 2, 1, TT.EOF),
    ]
    lexer.lex('file', input)
    output = lexer.tokenList

    assert len(output) == len(expected_output)
    for i in range(len(expected_output)):
        assert repr(output[i]) == expected_output[i]


def test_lex_quoted_string():
    lexer = Lexer({'': ''})

    input = '"bucket number 21""bucket number 22"'
    expected_output = [
        __get_token_string('file', 1, 2, TT.STRING, 'bucket number 21'),
        __get_token_string('file', 1, 20, TT.STRING, 'bucket number 22'),
        __get_token_string('file', 1, 37, TT.NEWLINE),
        __get_token_string('file', 2, 1, TT.EOF),
    ]
    lexer.lex('file', input)
    output = lexer.tokenList

    assert len(output) == len(expected_output)
    for i in range(len(expected_output)):
        assert repr(output[i]) == expected_output[i]

    lexer = Lexer({'': ''})
    input = "'bucket number 21'"
    expected_output = [
        __get_token_string('file', 1, 2, TT.STRING, 'bucket number 21'),
        __get_token_string('file', 1, 19, TT.NEWLINE),
        __get_token_string('file', 2, 1, TT.EOF),
    ]
    lexer.lex('file', input)
    output = lexer.tokenList

    assert len(output) == len(expected_output)
    for i in range(len(expected_output)):
        assert repr(output[i]) == expected_output[i]

    lexer = Lexer({'': ''})
    input = "'bucket number \"21\"'"
    expected_output = [
        __get_token_string('file', 1, 2, TT.STRING, 'bucket number "21"'),
        __get_token_string('file', 1, 21, TT.NEWLINE),
        __get_token_string('file', 2, 1, TT.EOF),
    ]
    lexer.lex('file', input)
    output = lexer.tokenList

    assert len(output) == len(expected_output)
    for i in range(len(expected_output)):
        assert repr(output[i]) == expected_output[i]

    lexer = Lexer({'': ''})
    input = '"bucket number \'21\'"'
    expected_output = [
        __get_token_string('file', 1, 2, TT.STRING, "bucket number '21'"),
        __get_token_string('file', 1, 21, TT.NEWLINE),
        __get_token_string('file', 2, 1, TT.EOF),
    ]
    lexer.lex('file', input)
    output = lexer.tokenList

    assert len(output) == len(expected_output)
    for i in range(len(expected_output)):
        assert repr(output[i]) == expected_output[i]


def test_lex_quoted_string_error():
    input = {
        'file': 'bucket nom-8: "amount: 5 \n\t',
    }
    lexer = Lexer(input)
    with pytest.raises(DSLParserNoEndingQuotesError):
        lexer.run()


def test_lex_multiline_input():
    input = {
        'file': 'bucket nom\\\ntest:',
    }
    expected_output = [
        __get_token_string('file', 1, 1, TT.STRING, 'bucket'),
        __get_token_string('file', 1, 7, TT.WHITESPACE),
        __get_token_string('file', 1, 8, TT.STRING, 'nomtest'),
        __get_token_string('file', 2, 5, TT.COLON),
        __get_token_string('file', 2, 6, TT.NEWLINE),
        __get_token_string('file', 3, 1, TT.EOF),
    ]
    lexer = Lexer(input)
    lexer.run()
    output = lexer.tokenList

    assert len(output) == len(expected_output)
    for i in range(len(expected_output)):
        assert repr(output[i]) == expected_output[i]


def test_lex_var():
    input = '#variable'
    expected_output = [
        __get_token_string('file', 1, 2, TT.VAR, 'variable'),
        __get_token_string('file', 1, 10, TT.NEWLINE),
        __get_token_string('file', 2, 1, TT.EOF),
    ]
    lexer = Lexer({'': ''})
    lexer.lex('file', input)
    output = lexer.tokenList

    assert len(output) == len(expected_output)
    for i in range(len(expected_output)):
        assert repr(output[i]) == expected_output[i]


def test_lex_newline():
    __single_token_test('\n', TT.NEWLINE, is_newline=True)


def test_lex_tab():
    __single_token_test('\t', TT.TAB)


def test_lex_4_whitespaces_as_tab():
    input = {
        'file': '    \n\t',
    }
    expected_output = [
        __get_token_string('file', 1, 1, TT.TAB),
        __get_token_string('file', 1, 5, TT.NEWLINE),
        __get_token_string('file', 2, 1, TT.TAB),
        __get_token_string('file', 2, 2, TT.NEWLINE),
        __get_token_string('file', 3, 1, TT.EOF),
    ]
    lexer = Lexer(input)
    output = lexer.run()

    assert len(output) == len(expected_output)
    for i in range(len(expected_output)):
        assert repr(output[i]) == expected_output[i]


def test_lex_2_4_whitespaces_as_tabs():
    input = {
        'file': '        \n\t',
    }
    expected_output = [
        __get_token_string('file', 1, 1, TT.TAB),
        __get_token_string('file', 1, 5, TT.TAB),
        __get_token_string('file', 1, 9, TT.NEWLINE),
        __get_token_string('file', 2, 1, TT.TAB),
        __get_token_string('file', 2, 2, TT.NEWLINE),
        __get_token_string('file', 3, 1, TT.EOF),
    ]
    lexer = Lexer(input)
    output = lexer.run()

    assert len(output) == len(expected_output)
    for i in range(len(expected_output)):
        assert repr(output[i]) == expected_output[i]


def test_lex_dash():
    __single_token_test('-', TT.MINUS)


def test_lex_amount():
    input = 'amount '
    expected_output = [
        __get_token_string('file', 1, 1, TT.AMOUNT),
        __get_token_string('file', 1, 7, TT.WHITESPACE),
        __get_token_string('file', 1, 8, TT.NEWLINE),
        __get_token_string('file', 2, 1, TT.EOF),
    ]
    lexer = Lexer({'': ''})
    lexer.lex('file', input)
    output = lexer.tokenList

    assert len(output) == len(expected_output)
    for i in range(len(expected_output)):
        assert repr(output[i]) == expected_output[i]


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
    expected_output = [
        __get_token_string('file', 1, 1, TT.IF),
        __get_token_string('file', 1, 3, TT.WHITESPACE),
        __get_token_string('file', 1, 4, TT.STRING, 'condition'),
        __get_token_string('file', 1, 13, TT.WHITESPACE),
        __get_token_string('file', 1, 14, TT.ELSE),
        __get_token_string('file', 1, 18, TT.WHITESPACE),
        __get_token_string('file', 1, 19, TT.STRING, 'something'),
        __get_token_string('file', 1, 28, TT.NEWLINE),
        __get_token_string('file', 2, 1, TT.EOF),
    ]
    lexer = Lexer({'': ''})
    lexer.lex('file', input)
    output = lexer.tokenList

    assert len(output) == len(expected_output)
    for i in range(len(expected_output)):
        assert repr(output[i]) == expected_output[i]


def test_lex_or():
    __single_token_test('or', TT.OR)


def test_lex_true():
    __single_token_test('true', TT.BOOLEAN, token_value='true')


def test_lex_false():
    __single_token_test('false', TT.BOOLEAN, token_value='false')


def test_lex_int():
    __single_token_test('8', TT.INT, token_value='8')


def test_lex_float():
    __single_token_test('4.5', TT.FLOAT, token_value='4.5')


def test_lex_string():
    input = 'bucket nom-8'
    expected_output = [
        __get_token_string('file', 1, 1, TT.STRING, 'bucket'),
        __get_token_string('file', 1, 7, TT.WHITESPACE),
        __get_token_string('file', 1, 8, TT.STRING, 'nom'),
        __get_token_string('file', 1, 11, TT.MINUS),
        __get_token_string('file', 1, 12, TT.INT, 8),
        __get_token_string('file', 1, 13, TT.NEWLINE),
        __get_token_string('file', 2, 1, TT.EOF),
    ]
    lexer = Lexer({'': ''})
    lexer.lex('file', input)
    output = lexer.tokenList

    assert len(output) == len(expected_output)
    for i in range(len(expected_output)):
        assert repr(output[i]) == expected_output[i]


def test_run_lexer():
    input = {
        'file': 'bucket nom-8: amount: 5 \n\t',
        'file2': 'network aaaa-#i: nombre: 2 4.5\n\t- property',
    }
    expected_output = [
        __get_token_string('file', 1, 1, TT.STRING, 'bucket'),
        __get_token_string('file', 1, 7, TT.WHITESPACE),
        __get_token_string('file', 1, 8, TT.STRING, 'nom'),
        __get_token_string('file', 1, 11, TT.MINUS),
        __get_token_string('file', 1, 12, TT.INT, 8),
        __get_token_string('file', 1, 13, TT.COLON),
        __get_token_string('file', 1, 14, TT.WHITESPACE),
        __get_token_string('file', 1, 15, TT.AMOUNT),
        __get_token_string('file', 1, 21, TT.COLON),
        __get_token_string('file', 1, 22, TT.WHITESPACE),
        __get_token_string('file', 1, 23, TT.INT, '5'),
        __get_token_string('file', 1, 24, TT.WHITESPACE),
        __get_token_string('file', 1, 25, TT.NEWLINE),
        __get_token_string('file', 2, 1, TT.TAB),
        __get_token_string('file', 2, 2, TT.NEWLINE),
        __get_token_string('file', 3, 1, TT.EOF),

        __get_token_string('file2', 1, 1, TT.STRING, 'network'),
        __get_token_string('file2', 1, 8, TT.WHITESPACE),
        __get_token_string('file2', 1, 9, TT.STRING, 'aaaa'),
        __get_token_string('file2', 1, 13, TT.MINUS),
        __get_token_string('file2', 1, 15, TT.VAR, 'i'),
        __get_token_string('file2', 1, 16, TT.COLON),
        __get_token_string('file2', 1, 17, TT.WHITESPACE),
        __get_token_string('file2', 1, 18, TT.STRING, 'nombre'),
        __get_token_string('file2', 1, 24, TT.COLON),
        __get_token_string('file2', 1, 25, TT.WHITESPACE),
        __get_token_string('file2', 1, 26, TT.INT, '2'),
        __get_token_string('file2', 1, 27, TT.WHITESPACE),
        __get_token_string('file2', 1, 28, TT.FLOAT, '4.5'),
        __get_token_string('file2', 1, 31, TT.NEWLINE),
        __get_token_string('file2', 2, 1, TT.TAB),
        __get_token_string('file2', 2, 2, TT.MINUS),
        __get_token_string('file2', 2, 3, TT.WHITESPACE),
        __get_token_string('file2', 2, 4, TT.STRING, 'property'),
        __get_token_string('file2', 2, 12, TT.NEWLINE),
        __get_token_string('file2', 3, 1, TT.EOF),
    ]
    lexer = Lexer(input)
    output = lexer.run()

    assert len(output) == len(expected_output)
    for i in range(len(expected_output)):
        assert repr(output[i]) == expected_output[i]


def test_run_lexer_var_in_name():
    input = {
        'file': 'bucket nom-#test \n\t toto: tata',
    }
    expected_output = [
        __get_token_string('file', 1, 1, TT.STRING, 'bucket'),
        __get_token_string('file', 1, 7, TT.WHITESPACE),
        __get_token_string('file', 1, 8, TT.STRING, 'nom'),
        __get_token_string('file', 1, 11, TT.MINUS),
        __get_token_string('file', 1, 13, TT.VAR, 'test'),
        __get_token_string('file', 1, 17, TT.WHITESPACE),
        __get_token_string('file', 1, 18, TT.NEWLINE),
        __get_token_string('file', 2, 1, TT.TAB),
        __get_token_string('file', 2, 2, TT.WHITESPACE),
        __get_token_string('file', 2, 3, TT.STRING, 'toto'),
        __get_token_string('file', 2, 7, TT.COLON),
        __get_token_string('file', 2, 8, TT.WHITESPACE),
        __get_token_string('file', 2, 9, TT.STRING, 'tata'),
        __get_token_string('file', 2, 13, TT.NEWLINE),
        __get_token_string('file', 3, 1, TT.EOF),
    ]
    lexer = Lexer(input)
    output = lexer.run()

    assert len(output) == len(expected_output)
    for i in range(len(expected_output)):
        assert repr(output[i]) == expected_output[i]
