"""THipster DSL token parser module."""
import thipster.parser.dsl_parser.ast as ast

from .exceptions import (
    DSLConditionError,
    DSLSyntaxError,
    DSLUnexpectedEOFError,
)
from .token import TOKENTYPES as TT
from .token import Token


class TokenParser():
    """Parse the tokens into an AST (Abstract Syntax Tree)."""

    def __init__(self, tokens: list[Token]) -> None:
        """Parse the tokens into an AST (Abstract Syntax Tree).

        Parameters
        ----------
        tokens : list[Token]
            The list of tokens to parse.
        """
        self.__tokens = tokens

    def run(self) -> ast.FileNode:
        """Run the parser."""
        self.__rm_empty_lines()
        tree = ast.FileNode()
        try:
            self.__trim_newlines()
            while self.__get_next_type() != TT.EOF:
                self.__trim_newlines()

                tree.add(self.__create_resource())
                self.__trim_newlines()
        except Exception as e:
            raise e

        return tree

    def __next(self, expected: TT | list[TT] | None = None) -> Token:
        """Get next token and pop it from the list.

        Parameters
        ----------
        expected : TT | list[TT] | None
            Expected token type(s), by default None

        Returns
        -------
        Token
            The next token
        """
        next_token_type = self.__get_next_type()

        if expected:
            if type(expected) is list:
                if next_token_type not in expected:
                    raise DSLSyntaxError(self.__tokens[0], expected)
            elif next_token_type != expected:
                raise DSLSyntaxError(self.__tokens[0], expected)
        return self.__tokens.pop(0)

    def __check(self, expected: TT, index: int = 0) -> Token | None:
        """Check if the next token is the expected one.

        If the type of the next token is equal to the expected parameter, it is popped
        from the list.

        Parameters
        ----------
        expected : TT
            Expected token type
        index : int, optional
            Index of the token to check, by default 0

        Returns
        -------
        Token | None
            The next token if it is the expected one, None otherwise
        """
        token = self.__get_next_type(index=index)
        if token != expected:
            return None

        return self.__next(expected)

    def __get_next_type(self, index: int = 0) -> TT:
        """Get the type of the next token.

        Parameters
        ----------
        index : int, optional
            Index of the token to get, by default 0

        Returns
        -------
        TT
            The type of the next token
        """
        if len(self.__tokens) <= index:
            raise DSLUnexpectedEOFError

        return self.__tokens[index].token_type

    def __trim_newlines(self):
        while self.__check(TT.NEWLINE):
            pass

    def __rm_empty_lines(self):
        # Detect empty line
        empty_types = [TT.TAB]
        end = 0
        while end < len(self.__tokens):
            begin = end
            while self.__get_next_type(end) in empty_types:
                end += 1

            if self.__get_next_type(index=end) == TT.NEWLINE:
                for _ in range(begin, end):
                    self.__tokens.pop(begin)
            end += 1

    def __get_newline(self):
        newline = self.__next(TT.NEWLINE)
        self.__trim_newlines()

        return newline

    def __get_whitespaces(self):
        while self.__check(TT.WHITESPACE):
            pass

    def __get_tabs(self, indent: int) -> bool:
        """Check if the number of tabs is correct/ if it is the end of the block."""
        if self.__get_next_type() == TT.EOF:
            return False
        if self.__get_next_type(indent-1) == TT.TAB:
            for _ in range(indent):
                self.__next(TT.TAB)
            return True
        return False

    def __create_resource(
        self,
        indent=0,
    ) -> ast.ResourceNode | ast.IfNode | ast.AmountNode:
        r"""Create an AST Resouce, If or Amount node.

        Format: type, name, ":", [amt_ctrl], [if_ctrl] ,"\\n"
        (list | dict | {parameter, "\\n"}).
        """
        try:
            for _ in range(indent):
                self.__next(TT.TAB)

            resource_type = self.__get_type()
            self.__get_whitespaces()
            name = self.__get_string_expr()
            self.__get_whitespaces()
            self.__next(TT.COLON)
            self.__get_whitespaces()

            nb_ctrl = self.__get_nb_ctrl()
            self.__get_whitespaces()
            if_ctrl = self.__get_if_ctrl()
            self.__get_whitespaces()

            self.__get_newline()

            properties = self.__get_properties(indent+1)

        except DSLSyntaxError as e:
            raise e

        resource = ast.ResourceNode(
            resource_type=resource_type,
            name=name,
            parameters=properties,
        )

        if if_ctrl:
            if_ctrl.if_case = resource
            resource = if_ctrl

        if nb_ctrl:
            nb_ctrl.node = resource
            resource = nb_ctrl

        return resource

    def __get_parameter(self, indent: int) -> ast.ParameterNode:
        r"""Create an AST Parameter node.

        Format: name, ":", (value, [if_else_ctrl] | [if_ctrl], "\\n", (list | dict)).
        """
        try:
            name = self.__next(TT.STRING)
            self.__get_whitespaces()
            self.__next(TT.COLON)
            self.__get_whitespaces()
        except DSLSyntaxError as e:
            raise e

        next_token_type = self.__get_next_type()

        if next_token_type not in [
            TT.IF,
            TT.NEWLINE,
        ]:
            # value, [if_else_ctrl]
            try:
                value = self.__get_value()
                self.__get_whitespaces()
                if_else_ctrl = self.__get_if_else_ctrl()
                self.__get_whitespaces()
            except:
                raise

            parameter = ast.ParameterNode(
                name=ast.StringNode(name),
                value=value,
            )

            if if_else_ctrl:
                if_else_ctrl.if_case = parameter.value
                parameter.value = if_else_ctrl

            return parameter

        # [if_ctrl], "\n" (liste | dict)
        try:
            if_ctrl = self.__get_if_ctrl()
            self.__get_whitespaces()
            newline = self.__get_newline()
            properties = self.__get_properties(indent+1)
        except DSLSyntaxError as e:
            if e.token.token_type == TT.TAB:
                raise DSLSyntaxError(
                    token=newline,
                    expected=TT.STRING,
                )

            raise e

        parameter = ast.ParameterNode(
            name=ast.StringNode(name),
            value=properties,
        )

        if if_ctrl:
            if_ctrl.if_case = parameter
            parameter = if_ctrl

        return parameter

    def __get_properties(self, indent: int) -> list[ast.ParameterNode]:
        """Create a list of AST Parameter nodes.

        Format: (list | dict).
        """
        i = indent
        try:
            next_token_type = self.__get_next_type(indent)
            while next_token_type == TT.WHITESPACE:
                i += 1
                next_token_type = self.__get_next_type(i)

            if next_token_type == TT.STRING:
                props = self.__get_dict(indent)

            elif next_token_type == TT.MINUS:
                props = self.__get_list(indent)

            else:
                raise DSLSyntaxError(self.__next(), TT.TAB)

        except DSLUnexpectedEOFError as eof:
            if indent > 1:
                raise DSLUnexpectedEOFError from eof

            if eof.__cause__:
                raise DSLUnexpectedEOFError from eof.__cause__

            props = ast.DictNode([])

        return props

    def __get_list(self, indent: int) -> ast.ListNode:
        r"""Create an AST List node.

        Format: { "-", value, [amt_ctrl], [if_else_ctrl], "\\n"}.
        """
        list_items = []

        try:
            while self.__get_tabs(indent):
                self.__check(TT.MINUS)
                self.__get_whitespaces()

                value = self.__get_value()
                self.__get_whitespaces()

                amount_ctrl = self.__get_nb_ctrl()
                self.__get_whitespaces()

                if_else_ctrl = self.__get_if_else_ctrl()
                self.__get_whitespaces()

                if if_else_ctrl:
                    if_else_ctrl.if_case = value
                    value = if_else_ctrl

                if amount_ctrl:
                    amount_ctrl.node = value
                    value = amount_ctrl

                list_items.append(value)

                self.__get_newline()
        except Exception as e:
            raise e

        self.__tokens.insert(
            0, Token(
                position=self.__tokens[0].position,
                token_type=TT.NEWLINE,
            ),
        )

        return ast.ListNode(list_items)

    def __get_inline_list(self) -> ast.ListNode:
        list_items = []

        self.__next(TT.BRACKETS_START)
        self.__get_whitespaces()
        next_token_type = self.__get_next_type()

        if next_token_type in [
            TT.BOOLEAN,
            TT.FLOAT,
            TT.INT,
            TT.STRING,
            TT.VAR,
            TT.BRACKETS_START,
        ]:
            list_items.append(self.__get_value())
            while not self.__check(TT.BRACKETS_END):
                self.__next([TT.COMMA, TT.NEWLINE])
                while self.__check(TT.TAB):
                    pass
                self.__get_whitespaces()

                list_items.append(self.__get_value())
                self.__get_whitespaces()
        else:
            self.__next(TT.BRACKETS_END)

        return ast.ListNode(list_items)

    def __get_dict(self, indent: int) -> ast.DictNode:
        r"""Create an AST Dict node.

        Format: { parameter, "\\n" }.
        """
        parameters = []

        try:
            while self.__get_tabs(indent):
                self.__get_whitespaces()
                parameters.append(self.__get_parameter(indent))
                self.__get_whitespaces()
                self.__get_newline()
        except Exception as e:
            raise e

        self.__tokens.insert(
            0, Token(
                position=self.__tokens[0].position,
                token_type=TT.NEWLINE,
            ),
        )

        return ast.DictNode(parameters)

    def __get_nb_ctrl(self) -> ast.AmountNode | None:
        """Create an AST Amount node.

        Format: "amount", ":", int, ["#", var].
        """
        try:
            amount_token = self.__check(TT.AMOUNT)
            if not amount_token:
                return None

            self.__get_whitespaces()
            self.__next(TT.COLON)

            self.__get_whitespaces()
            amount = self.__get_arith_expr()

            self.__get_whitespaces()
        except DSLSyntaxError as e:
            raise e

        amount_variable = self.__check(TT.VAR)

        return ast.AmountNode(
            position=amount_token,
            amount=amount,
            variable=ast.VariableDefinitionNode(
                amount_variable, ast.IntNode(Token(None, TT.INT, 1)),
            )
            if amount_variable else None,
            node=None,
        )

    def __get_if_ctrl(self) -> ast.IfNode | None:
        """Create an AST If node.

        Format: "if", condition.
        """
        condition = self.__check(TT.IF)
        if not condition:
            return None

        self.__get_whitespaces()
        try:
            condition = self.__get_comp_expr()
            self.__get_whitespaces()
        except DSLSyntaxError as e:
            raise e

        return ast.IfNode(
            condition=condition,
            if_case=None,
        )

    def __get_if_else_ctrl(self) -> ast.IfElseNode | None:
        """Create an AST IfElse node.

        Format: if_ctrl, ["else" , value].
        """
        if_ctrl = self.__get_if_ctrl()
        self.__get_whitespaces()
        if not if_ctrl:
            return None

        if self.__check(TT.ELSE):
            self.__get_whitespaces()
            else_case = self.__get_value()
            self.__get_whitespaces()
        else:
            else_case = None

        return ast.IfElseNode(
            condition=if_ctrl.condition,
            if_case=None,
            else_case=else_case,
        )

    def __get_value(self) -> ast.LiteralNode:
        next_token_type = self.__get_next_type()
        match next_token_type:
            case TT.STRING:
                return self.__get_string_expr()

            case TT.VAR:
                return ast.LiteralNode(ast.VariableNode(self.__next(TT.VAR)))

            case TT.BRACKETS_START:
                return self.__get_inline_list()

            case TT.NOT | TT.BOOLEAN:
                return self.__get_comp_expr()

            case _:
                value = self.__get_arith_expr()
                self.__get_whitespaces()

                next_token_type = self.__get_next_type()
                if next_token_type in [TT.EE, TT.LT, TT.GT, TT.LTE, TT.GTE]:
                    operator = self.__next(
                        [TT.EE, TT.LT, TT.GT, TT.LTE, TT.GTE],
                    )
                    self.__get_whitespaces()
                    right_expression = self.__get_comp_expr()
                    self.__get_whitespaces()
                    self.__next(TT.PARENTHESES_END)
                    self.__get_whitespaces()

                    return ast.CompExprNode(value, operator, right_expression)
                return value

    def __get_comp_expr(self) -> ast.CompExprNode:
        try:
            next_token_type = self.__get_next_type()
            match next_token_type:

                case TT.NOT:
                    operator = self.__next(TT.NOT)
                    self.__get_whitespaces()
                    expression = self.__get_comp_expr()
                    self.__get_whitespaces()
                    return ast.CompExprNode(expression, operator)

                case TT.PARENTHESES_START:
                    self.__next(TT.PARENTHESES_START)
                    self.__get_whitespaces()
                    left_expression = self.__get_comp_expr()
                    self.__get_whitespaces()
                    operator = self.__next([TT.OR, TT.AND])
                    self.__get_whitespaces()
                    right_expression = self.__get_comp_expr()
                    self.__get_whitespaces()
                    self.__next(TT.PARENTHESES_END)
                    self.__get_whitespaces()

                    return ast.CompExprNode(left_expression, operator, right_expression)

                case TT.BOOLEAN:
                    return ast.LiteralNode(ast.BoolNode(self.__next(TT.BOOLEAN)))

                case _:
                    left_expression = self.__get_arith_expr()
                    self.__get_whitespaces()
                    operator = self.__next(
                        [TT.EQ, TT.LT, TT.GT, TT.EXCLAMATION],
                    )

                    # ==
                    if operator.token_type is TT.EQ:
                        self.__next(TT.EQ)
                        operator = Token(operator.position, TT.EE)

                    # !=
                    if operator.token_type is TT.EXCLAMATION:
                        self.__next(TT.EQ)
                        operator = Token(operator.position, TT.NE)

                    next_token_type = self.__get_next_type()
                    if next_token_type is TT.EQ:
                        self.__next(TT.EQ)
                        match operator.token_type:
                            case TT.LT:
                                operator = Token(operator.position, TT.LTE)
                            case TT.GT:
                                operator = Token(operator.position, TT.GTE)

                    self.__get_whitespaces()
                    right_expression = self.__get_arith_expr()
                    self.__get_whitespaces()
                    return ast.CompExprNode(left_expression, operator, right_expression)

        except DSLSyntaxError as e:
            raise DSLConditionError(e.token)

    def __get_arith_expr(self) -> ast.ArithExprNode:
        terms = []
        operator = []
        terms.append(self.__get_term())
        self.__get_whitespaces()

        next_token_type = self.__get_next_type()
        while next_token_type in [TT.PLUS, TT.MINUS]:
            operator.append(next_token_type)
            terms.append(self.__get_term())
            self.__get_whitespaces()
            next_token_type = self.__get_next_type()

        return ast.ArithExprNode(terms, operator)

    def __get_term(self) -> ast.TermNode:
        factors = []
        operator = []
        factors.append(self.__get_factor())
        self.__get_whitespaces()

        next_token_type = self.__get_next_type()
        while next_token_type in [TT.MUL, TT.DIV]:
            operator.append(self.__next([TT.MUL, TT.DIV]).token_type)
            self.__get_whitespaces()
            factors.append(self.__get_factor())
            self.__get_whitespaces()
            next_token_type = self.__get_next_type()

        return ast.TermNode(factors, operator)

    def __get_factor(self) -> ast.FactorNode:
        next_token_type = self.__get_next_type()

        match next_token_type:
            case TT.PLUS | TT.MINUS:
                operator = self.__next([TT.PLUS, TT.MINUS]).token_type
                self.__get_whitespaces()
                factor = self.__get_factor()
                self.__get_whitespaces()
                return ast.FactorNode([factor], operator)

            case _:
                factors = [self.__get_atom()]
                self.__get_whitespaces()

                next_token_type = self.__get_next_type()
                operator = TT.PLUS
                while next_token_type == TT.POW:
                    operator = self.__next(TT.POW).token_type
                    self.__get_whitespaces()
                    factors.append(self.__get_factor())
                    self.__get_whitespaces()
                    next_token_type = self.__get_next_type()
                return ast.FactorNode(factors, operator)

    def __get_atom(self):
        next_token_type = self.__get_next_type()
        match next_token_type:
            case TT.INT:
                return ast.IntNode(self.__next())

            case TT.FLOAT:
                return ast.FloatNode(self.__next())

            case TT.PARENTHESES_START:
                self.__next(TT.PARENTHESES_START)
                self.__get_whitespaces()
                expression = self.__get_arith_expr()
                self.__get_whitespaces()
                self.__next(TT.PARENTHESES_END)
                self.__get_whitespaces()
                return expression

            case _:
                raise DSLSyntaxError(
                    self.__tokens[0], [TT.INT, TT.FLOAT, TT.PARENTHESES_START],
                )

    def __get_string_expr(self):
        values = []
        token = self.__next([TT.STRING, TT.VAR])
        match token.token_type:
            case TT.STRING:
                values.append(ast.StringNode(token))

            case TT.VAR:
                values.append(ast.VariableNode(token))

        next_token_type = self.__get_next_type()
        while next_token_type in [TT.STRING, TT.VAR, TT.INT, TT.MINUS, TT.DIV]:
            match next_token_type:
                case TT.STRING:
                    values.append(ast.StringNode(self.__next(TT.STRING)))

                case TT.VAR:
                    values.append(ast.VariableNode(self.__next(TT.VAR)))

                case TT.INT:
                    values.append(ast.IntNode(self.__next(TT.INT)))

                case TT.DIV:
                    token = Token(self.__next(TT.DIV).position, TT.STRING, '/')
                    values.append(ast.StringNode(token))

                case TT.MINUS:
                    token = Token(
                        self.__next(
                            TT.MINUS,
                        ).position, TT.STRING, '-',
                    )
                    values.append(ast.StringNode(token))
            next_token_type = self.__get_next_type()

        return ast.StringExprNode(values)

    def __get_type(self):
        values = []
        values.append(ast.StringNode(self.__next(TT.STRING)))

        next_token_type = self.__get_next_type()
        while next_token_type in [TT.STRING, TT.MINUS, TT.DIV]:
            match next_token_type:
                case TT.STRING:
                    values.append(ast.StringNode(self.__next(TT.STRING)))

                case TT.DIV:
                    token = Token(self.__next(TT.DIV).position, TT.STRING, '/')
                    values.append(ast.StringNode(token))

                case TT.MINUS:
                    token = Token(
                        self.__next(
                            TT.MINUS,
                        ).position, TT.STRING, '-',
                    )
                    values.append(ast.StringNode(token))
            next_token_type = self.__get_next_type()

        return ast.StringExprNode(values)
