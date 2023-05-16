from parser.dsl_parser.Token import Token, TOKENTYPES as TT
from parser.dsl_parser.AST import BoolNode, DictNode, FileNode, FloatNode, IfElseNode, \
    IfNode, AmountNode, IntNode, ListNode, ParameterNode, ResourceNode, StringNode, \
    LiteralNode, VariableDefinitionNode, VariableNode


class DSLSyntaxException(Exception):
    def __init__(self, token: Token, expected: TT, *args: object) -> None:
        super().__init__(*args)
        self.__tok = token
        self.__exp = expected

    def __repr__(self) -> str:
        return f"""{str(self.__tok.position)} :\n\tSyntax error : Expected \
{str(self.__exp.value)}, got {str(self.__tok.tokenType)}"""

    @property
    def tok(self):
        return self.__tok


class DSLUnexpectedEOF(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

    def __repr__(self) -> str:
        return 'Unexpected EOF'


class TokenParser():
    def __init__(self, tokens: list[Token]) -> None:
        self.__tokens = tokens

    def run(self) -> FileNode:
        self.__rm_empty_lines()
        tree = FileNode()
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
                    raise DSLSyntaxException(self.__tokens[0], str(expected))
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

    def __create_resource(self, indent=0) -> ResourceNode | IfNode | AmountNode:
        """type, name, ":", [amt_ctrl], [if_ctrl] ,"\\n"
                                (list | dict | {parameter, "\\n"})"""
        try:
            for _ in range(indent):
                self.__next(TT.TAB)

            resType = self.__next(TT.STRING)
            self.__get_whitespaces()
            name = self.__next(TT.STRING)
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
            print(e)
            raise e

        resource = ResourceNode(
            resourceType=StringNode(resType),
            name=StringNode(name),
            parameters=properties,
        )

        if ifCtrl:
            ifCtrl.ifCase = resource
            resource = ifCtrl

        if nbCtrl:
            nbCtrl.node = resource
            resource = nbCtrl

        return resource

    def __get_tabs(self, indent: int) -> bool:
        """Check if the number of tabs is correct/ if it is the end of the block"""

        if self.__get_next_type() == TT.EOF:
            return False
        elif self.__get_next_type(indent-1) == TT.TAB:
            for i in range(indent):
                self.__next(TT.TAB)
            return True
        return False

    def __get_parameter(self, indent: int) -> ParameterNode:
        """name, ":", (value, [if_else_ctrl] | [if_ctrl], "\\n", (list | dict))"""
        try:
            name = self.__next(TT.STRING)
            self.__get_whitespaces()
            self.__next(TT.COLON)
            self.__get_whitespaces()
        except DSLSyntaxException as e:
            raise e

        next = self.__get_next_type()

        if next in [
            TT.BOOLEAN,
            TT.FLOAT,
            TT.INT,
            TT.STRING,
            TT.VAR,
            TT.BRACKETS_START,
        ]:
            # value, [if_else_ctrl]
            try:
                value = self.__get_value()
                self.__get_whitespaces()
                ifElseCtrl = self.__get_if_else_ctrl()
                self.__get_whitespaces()
            except:
                raise

            parameter = ParameterNode(
                name=StringNode(name),
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

        parameter = ParameterNode(
            name=StringNode(name),
            value=properties,
        )

        if ifCtrl:
            ifCtrl.ifCase = parameter
            parameter = ifCtrl

        return parameter

    def __get_inline_list(self) -> ListNode:
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

        return ListNode(items)

    def __get_list(self, indent: int) -> ListNode:
        """{ "-", value, [amt_ctrl], [if_else_ctrl], "\\n"}"""
        items = []

        try:
            while self.__get_tabs(indent):
                self.__check(TT.DASH)
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

        return ListNode(items)

    def __get_dict(self, indent: int) -> DictNode:
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

        return DictNode(props)

    def __get_properties(self, indent: int) -> list[ParameterNode]:
        """(list | dict)
        """
        i = indent
        next = self.__get_next_type(indent)
        while next == TT.WHITESPACE:
            i += 1
            next = self.__get_next_type(i)

        if next == TT.STRING:
            props = self.__get_dict(indent)

        elif next == TT.DASH:
            props = self.__get_list(indent)

        else:
            raise DSLSyntaxException(self.__next(), TT.TAB)

        return props

    def __get_nb_ctrl(self) -> AmountNode | None:
        """"amount", ":", int, ["#", var]"""

        try:
            nextToken = self.__check(TT.AMOUNT)
            if not nextToken:
                return None
            self.__get_whitespaces()

            self.__next(TT.COLON)
            self.__get_whitespaces()
            nb = self.__next(TT.INT)
            self.__get_whitespaces()
        except DSLSyntaxException as e:
            raise e

        var = self.__check(TT.VAR)

        return AmountNode(
            amount=IntNode(nb),
            variable=VariableDefinitionNode(
                var, IntNode(Token(None, TT.INT, 1)),
            )
            if var else None,
            node=None,
        )

    def __get_if_ctrl(self) -> IfNode | None:
        """"if", condition"""

        condition = self.__check(TT.IF)
        if not condition:
            return None
        self.__get_whitespaces()

        try:
            # TODO : Add real conditions
            condition = self.__next(TT.STRING)
            self.__get_whitespaces()
        except DSLSyntaxException as e:
            raise e

        return IfNode(
            condition=StringNode(condition),
            ifCase=None,
        )

    def __get_if_else_ctrl(self) -> IfElseNode | None:
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

        return IfElseNode(
            condition=ifCtrl.condition,
            ifCase=None,
            elseCase=elseCase,
        )

    def __get_value(self) -> LiteralNode:

        nextType = self.__get_next_type()
        if nextType == TT.BOOLEAN:
            value = LiteralNode(BoolNode(self.__next()))
        elif nextType == TT.FLOAT:
            value = LiteralNode(FloatNode(self.__next()))
        elif nextType == TT.INT:
            value = LiteralNode(IntNode(self.__next()))
        elif nextType == TT.STRING:
            value = LiteralNode(StringNode(self.__next()))
        elif nextType == TT.VAR:
            value = LiteralNode(VariableNode(self.__next()))
        elif nextType == TT.BRACKETS_START:
            value = self.__get_inline_list()
        else:
            raise DSLSyntaxException(self.__next(), TT.STRING)

        return value
