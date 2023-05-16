from parser.dsl_parser.Token import Token, TOKENTYPES as TT
import parser.dsl_parser.AST as ast


class DSLSyntaxException(Exception):
    def __init__(self, token: Token, expected: TT | list[TT], *args: object) -> None:
        super().__init__(*args)
        self.__tok = token
        self.__exp = expected

    def __repr__(self) -> str:

        if type(self.__exp) is TT:
            return f"""{str(self.__tok.position)} :\n\tSyntax error : Expected \
{str(self.__exp.value)}, got {str(self.__tok.tokenType)}"""
        else:
            return f"""{str(self.__tok.position)} :\n\tSyntax error : Expected \
{str(' or '.join(list(map(lambda x : str(x), self.__exp))))}, got {
    str(self.__tok.tokenType)}"""

    @property
    def tok(self):
        return self.__tok


class DSLConditionException(Exception):
    def __init__(self, token: Token, *args: object) -> None:
        super().__init__(*args)
        self.__tok = token

    def __repr__(self) -> str:
        return f"""{str(self.__tok.position)} :\n\tBad condition"""


class DSLUnexpectedEOF(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

    def __repr__(self) -> str:
        return 'Unexpected EOF'


class TokenParser():
    def __init__(self, tokens: list[Token]) -> None:
        self.__tokens = tokens

    def run(self) -> ast.FileNode:
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
        """Get next token and pop it from the list"""
        tok = self.__get_next_type()

        if expected:
            if type(expected) is list:
                if tok not in expected:
                    raise DSLSyntaxException(self.__tokens[0], expected)
            elif tok != expected:
                raise DSLSyntaxException(self.__tokens[0], expected)
        return self.__tokens.pop(0)

    def __check(self, expected: TT, index: int = 0) -> Token | None:
        """Check if the type of the next token is equal to the expected parameter. \
        Pop it from the list in that case"""
        token = self.__get_next_type(index=index)
        if token != expected:
            return None

        return self.__next(expected)

    def __get_next_type(self, index: int = 0):
        """Get the type of the next token"""
        if len(self.__tokens) <= index:
            raise DSLUnexpectedEOF

        return self.__tokens[index].tokenType

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
        nl = self.__next(TT.NEWLINE)
        self.__trim_newlines()

        return nl

    def __get_whitespaces(self):
        while self.__check(TT.WHITESPACE):
            pass

    def __get_tabs(self, indent: int) -> bool:
        """Check if the number of tabs is correct/ if it is the end of the block"""

        if self.__get_next_type() == TT.EOF:
            return False
        elif self.__get_next_type(indent-1) == TT.TAB:
            for i in range(indent):
                self.__next(TT.TAB)
            return True
        return False

    def __create_resource(self, indent=0) \
            -> ast.ResourceNode | ast.IfNode | ast.AmountNode:
        """type, name, ":", [amt_ctrl], [if_ctrl] ,"\\n"
                                (list | dict | {parameter, "\\n"})"""
        try:
            for _ in range(indent):
                self.__next(TT.TAB)

            resType = self.__next(TT.STRING)
            self.__get_whitespaces()
            name = self.__get_string()
            self.__get_whitespaces()
            self.__next(TT.COLON)
            self.__get_whitespaces()

            nbCtrl = self.__get_nb_ctrl()
            self.__get_whitespaces()
            ifCtrl = self.__get_if_ctrl()
            self.__get_whitespaces()

            self.__get_newline()

            properties = self.__get_properties(indent+1)

        except DSLSyntaxException as e:
            raise e

        resource = ast.ResourceNode(
            resourceType=ast.StringNode(resType),
            name=name,
            parameters=properties,
        )

        if ifCtrl:
            ifCtrl.ifCase = resource
            resource = ifCtrl

        if nbCtrl:
            nbCtrl.node = resource
            resource = nbCtrl

        return resource

    def __get_parameter(self, indent: int) -> ast.ParameterNode:
        """name, ":", (value, [if_else_ctrl] | [if_ctrl], "\\n", (list | dict))"""
        try:
            name = self.__next(TT.STRING)
            self.__get_whitespaces()
            self.__next(TT.COLON)
            self.__get_whitespaces()
        except DSLSyntaxException as e:
            raise e

        next = self.__get_next_type()

        if next not in [
            TT.IF,
            TT.NEWLINE,
        ]:
            # value, [if_else_ctrl]
            try:
                value = self.__get_value()
                self.__get_whitespaces()
                ifElseCtrl = self.__get_if_else_ctrl()
                self.__get_whitespaces()
            except:
                raise

            parameter = ast.ParameterNode(
                name=ast.StringNode(name),
                value=value,
            )

            if ifElseCtrl:
                ifElseCtrl.ifCase = parameter.value
                parameter.value = ifElseCtrl

            return parameter

        # [if_ctrl], "\n" (liste | dict)
        try:
            ifCtrl = self.__get_if_ctrl()
            self.__get_whitespaces()
            nl = self.__get_newline()
            properties = self.__get_properties(indent+1)
        except DSLSyntaxException as e:
            if e.tok.tokenType == TT.TAB:
                raise DSLSyntaxException(
                    token=nl,
                    expected=TT.STRING,
                )

            raise e

        parameter = ast.ParameterNode(
            name=ast.StringNode(name),
            value=properties,
        )

        if ifCtrl:
            ifCtrl.ifCase = parameter
            parameter = ifCtrl

        return parameter

    def __get_properties(self, indent: int) -> list[ast.ParameterNode]:
        """(list | dict)
        """
        i = indent
        next = self.__get_next_type(indent)
        while next == TT.WHITESPACE:
            i += 1
            next = self.__get_next_type(i)

        if next == TT.STRING:
            props = self.__get_dict(indent)

        elif next == TT.MINUS:
            props = self.__get_list(indent)

        else:
            raise DSLSyntaxException(self.__next(), TT.TAB)

        return props

    def __get_list(self, indent: int) -> ast.ListNode:
        """{ "-", value, [amt_ctrl], [if_else_ctrl], "\\n"}"""
        items = []

        try:
            while self.__get_tabs(indent):
                self.__check(TT.MINUS)
                self.__get_whitespaces()

                value = self.__get_value()
                self.__get_whitespaces()

                amountCtrl = self.__get_nb_ctrl()
                self.__get_whitespaces()

                ifElseCtrl = self.__get_if_else_ctrl()
                self.__get_whitespaces()

                if ifElseCtrl:
                    ifElseCtrl.ifCase = value
                    value = ifElseCtrl

                if amountCtrl:
                    amountCtrl.node = value
                    value = amountCtrl

                items.append(value)

                self.__get_newline()
        except Exception as e:
            raise e

        self.__tokens.insert(
            0, Token(
                position=self.__tokens[0].position,
                tokenType=TT.NEWLINE,
            ),
        )

        return ast.ListNode(items)

    def __get_inline_list(self) -> ast.ListNode:
        items = []

        self.__next(TT.BRACKETS_START)
        self.__get_whitespaces()
        next = self.__get_next_type()

        if next in [
            TT.BOOLEAN,
            TT.FLOAT,
            TT.INT,
            TT.STRING,
            TT.VAR,
            TT.BRACKETS_START,
        ]:
            items.append(self.__get_value())
            while not self.__check(TT.BRACKETS_END):
                self.__next([TT.COMMA, TT.NEWLINE])
                while self.__check(TT.TAB):
                    pass
                self.__get_whitespaces()

                items.append(self.__get_value())
                self.__get_whitespaces()
        else:
            self.__next(TT.BRACKETS_END)

        return ast.ListNode(items)

    def __get_dict(self, indent: int) -> ast.DictNode:
        """{ parameter, "\\n" }
        """
        props = []

        try:
            while self.__get_tabs(indent):
                self.__get_whitespaces()
                props.append(self.__get_parameter(indent))
                self.__get_whitespaces()
                self.__get_newline()
        except Exception as e:
            raise e

        self.__tokens.insert(
            0, Token(
                position=self.__tokens[0].position,
                tokenType=TT.NEWLINE,
            ),
        )

        return ast.DictNode(props)

    def __get_nb_ctrl(self) -> ast.AmountNode | None:
        """"amount", ":", int, ["#", var]"""

        try:
            nextToken = self.__check(TT.AMOUNT)
            if not nextToken:
                return None
            self.__get_whitespaces()

            self.__next(TT.COLON)
            self.__get_whitespaces()
            nb = self.__get_arith_expr()
            self.__get_whitespaces()
        except DSLSyntaxException as e:
            raise e

        var = self.__check(TT.VAR)

        return ast.AmountNode(
            amount=nb,
            variable=ast.VariableDefinitionNode(
                var, ast.IntNode(Token(None, TT.INT, 1)),
            )
            if var else None,
            node=None,
        )

    def __get_if_ctrl(self) -> ast.IfNode | None:
        """"if", condition"""

        condition = self.__check(TT.IF)
        if not condition:
            return None
        self.__get_whitespaces()

        try:
            condition = self.__get_comp_expr()
            self.__get_whitespaces()
        except DSLSyntaxException as e:
            raise e

        return ast.IfNode(
            condition=condition,
            ifCase=None,
        )

    def __get_if_else_ctrl(self) -> ast.IfElseNode | None:
        """if_ctrl, ["else" , valeur]"""
        ifCtrl = self.__get_if_ctrl()
        self.__get_whitespaces()
        if not ifCtrl:
            return None

        if self.__check(TT.ELSE):
            self.__get_whitespaces()
            elseCase = self.__get_value()
            self.__get_whitespaces()
        else:
            elseCase = None

        return ast.IfElseNode(
            condition=ifCtrl.condition,
            ifCase=None,
            elseCase=elseCase,
        )

    def __get_value(self) -> ast.LiteralNode:
        nextType = self.__get_next_type()
        match nextType:
            case TT.STRING:
                return self.__get_string()

            case TT.VAR:
                return ast.LiteralNode(ast.VariableNode(self.__next(TT.VAR)))

            case TT.BRACKETS_START:
                return self.__get_inline_list()

            case TT.NOT | TT.BOOLEAN:
                return self.__get_comp_expr()

            case _:
                value = self.__get_arith_expr()
                self.__get_whitespaces()

                nextType = self.__get_next_type()
                if nextType in [TT.EE, TT.LT, TT.GT, TT.LTE, TT.GTE]:
                    op = self.__next([TT.EE, TT.LT, TT.GT, TT.LTE, TT.GTE])
                    self.__get_whitespaces()
                    expr2 = self.__get_comp_expr()
                    self.__get_whitespaces()
                    self.__next(TT.PARENTHESES_END)
                    self.__get_whitespaces()

                    return ast.CompExprNode(value, op, expr2)
                return value

    def __get_comp_expr(self) -> ast.CompExprNode:
        try:
            nextType = self.__get_next_type()
            match nextType:

                case TT.NOT:
                    op = self.__next(TT.NOT)
                    self.__get_whitespaces()
                    expr = self.__get_comp_expr()
                    self.__get_whitespaces()
                    return ast.CompExprNode(expr, op)

                case TT.PARENTHESES_START:
                    self.__next(TT.PARENTHESES_START)
                    self.__get_whitespaces()
                    expr1 = self.__get_comp_expr()
                    self.__get_whitespaces()
                    op = self.__next([TT.OR, TT.AND])
                    self.__get_whitespaces()
                    expr2 = self.__get_comp_expr()
                    self.__get_whitespaces()
                    self.__next(TT.PARENTHESES_END)
                    self.__get_whitespaces()
                    return ast.CompExprNode(expr1, op, expr2)

                case TT.BOOLEAN:
                    return ast.LiteralNode(ast.BoolNode(self.__next(TT.BOOLEAN)))

                case _:
                    expr1 = self.__get_arith_expr()
                    self.__get_whitespaces()
                    op = self.__next([TT.EE, TT.LT, TT.GT, TT.LTE, TT.GTE])
                    self.__get_whitespaces()
                    expr2 = self.__get_arith_expr()
                    self.__get_whitespaces()
                    return ast.CompExprNode(expr1, op, expr2)

        except DSLSyntaxException as e:
            raise DSLConditionException(e.tok)

    def __get_arith_expr(self) -> ast.ArithExprNode:
        terms = []
        op = []
        terms.append(self.__get_term())
        self.__get_whitespaces()

        nextType = self.__get_next_type()
        while nextType in [TT.PLUS, TT.MINUS]:
            op.append(nextType)
            terms.append(self.__get_term())
            self.__get_whitespaces()
            nextType = self.__get_next_type()

        return ast.ArithExprNode(terms, op)

    def __get_term(self) -> ast.TermNode:
        factors = []
        op = []
        factors.append(self.__get_factor())
        self.__get_whitespaces()

        nextType = self.__get_next_type()
        while nextType in [TT.MUL, TT.DIV]:
            op.append(self.__next([TT.MUL, TT.DIV]).tokenType)
            self.__get_whitespaces()
            factors.append(self.__get_factor())
            self.__get_whitespaces()
            nextType = self.__get_next_type()

        return ast.TermNode(factors, op)

    def __get_factor(self) -> ast.FactorNode:
        nextType = self.__get_next_type()

        match nextType:
            case TT.PLUS | TT.MINUS:
                op = self.__next([TT.PLUS, TT.MINUS]).tokenType
                self.__get_whitespaces()
                factor = self.__get_factor()
                self.__get_whitespaces()
                return ast.FactorNode([factor], op)

            case _:
                factors = [self.__get_atom()]
                self.__get_whitespaces()

                nextType = self.__get_next_type()
                op = TT.PLUS
                while nextType == TT.POW:
                    op = self.__next(TT.POW).tokenType
                    self.__get_whitespaces()
                    factors.append(self.__get_factor())
                    self.__get_whitespaces()
                    nextType = self.__get_next_type()
                return ast.FactorNode(factors, op)

    def __get_atom(self):
        nextType = self.__get_next_type()
        match nextType:
            case TT.INT:
                return ast.IntNode(self.__next())

            case TT.FLOAT:
                return ast.FloatNode(self.__next())

            case TT.PARENTHESES_START:
                self.__next(TT.PARENTHESES_START)
                self.__get_whitespaces()
                expr = self.__get_arith_expr()
                self.__get_whitespaces()
                self.__next(TT.PARENTHESES_END)
                self.__get_whitespaces()
                return expr

            case _:
                raise DSLSyntaxException(
                    self.__tokens[0], [TT.INT, TT.FLOAT, TT.PARENTHESES_START],
                )

    def __get_string(self):
        values = []
        token = self.__next([TT.STRING, TT.VAR])
        match token.tokenType:
            case TT.STRING:
                values.append(ast.StringNode(token))

            case TT.VAR:
                values.append(ast.VariableNode(token))

        nextType = self.__get_next_type()
        while nextType in [TT.STRING, TT.VAR, TT.INT]:
            match nextType:
                case TT.STRING:
                    values.append(ast.StringNode(self.__next(TT.STRING)))

                case TT.VAR:
                    values.append(ast.VariableNode(self.__next(TT.VAR)))

                case TT.INT:
                    values.append(ast.IntNode(self.__next(TT.INT)))
            nextType = self.__get_next_type()

        return ast.StringExprNode(values)
