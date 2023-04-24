from parser.dsl_parser.Token import Token, TOKENTYPES as TT
from parser.dsl_parser.AST import DictNode, FileNode, IfElseNode, IfNode, AmountNode, \
    IntNode, ListNode, ParameterNode, ResourceNode, StringNode, LiteralNode, ValueNode,\
    VariableNode


class DSLSyntaxException(Exception):
    def __init__(self, token: Token, *args: object) -> None:
        super().__init__(*args)
        self.__pos = token.position

    def __repr__(self) -> str:
        return f'Syntax error at {str(self.__pos)}'


class TokenParser():
    def __init__(self, tokens: list[Token]) -> None:
        self.__tokens = tokens

    def run(self) -> FileNode:
        tree = FileNode()
        tree.add(self.__create_resource())

        return tree

    def __next(self, expected: TT | None = None) -> Token:
        """Get next token and pop it from the list"""
        tok = self.__tokens.pop(0)
        if expected and tok.tokenType != expected.value:
            raise DSLSyntaxException(tok)
        return tok

    def __check(self, expected: TT) -> Token | None:
        """Check if the type of the next token is equal to the expected parameter. \
        Pop it from the list in that case"""
        token = self.__get_next_type()
        if token != expected.value:
            return None

        return self.__next(expected)

    def __get_next_type(self, index: int = 0):
        """Get the type of the next token"""
        if len(self.__tokens) == 0:
            raise

        return self.__tokens[index].tokenType

    def __create_resource(self, indent=0) -> ResourceNode | IfNode | AmountNode:
        """type, name, ":", [amt_ctrl], [if_ctrl] ,"\\n"
                                (list | dict | {parameter, "\\n"})"""
        try:
            for _ in range(indent):
                self.__next(TT.TAB)

            resType = self.__next(TT.STRING)
            name = self.__next(TT.STRING)
            self.__next(TT.COLUMN)

            nbCtrl = self.__get_nb_ctrl()
            ifCtrl = self.__get_if_ctrl()

            self.__next(TT.NEWLINE)

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

    def __get_tabs(self, nb: int) -> bool:
        for i in range(nb):
            try:
                self.__next(TT.TAB)
            except DSLSyntaxException as e:
                if i == nb - 1:
                    return False
                else:
                    raise e

        return True

    def __get_parameter(self, indent: int) -> ParameterNode:
        """name, ":", (value, [if_else_ctrl] | [if_ctrl], "\\n", (list | dict))"""
        try:
            name = self.__next(TT.STRING)
            self.__next(TT.COLUMN)
        except DSLSyntaxException as e:
            raise e

        next = self.__get_next_type()

        if next == TT.STRING.value:
            # value, [if_else_ctrl]
            try:
                value = self.__next()
                ifElseCtrl = self.__get_if_else_ctrl()
            except:
                raise

            parameter = ParameterNode(
                name=StringNode(name),
                value=LiteralNode(StringNode(value)),
            )

            if ifElseCtrl:
                ifElseCtrl.ifCase = parameter
                parameter = ifElseCtrl

            return parameter

        # [if_ctrl], "\n" (liste | dict)
        try:
            ifCtrl = self.__get_if_ctrl()
            self.__next(TT.NEWLINE)
            properties = self.__get_properties(indent+1)
        except:
            raise

        parameter = ParameterNode(
            name=name,
            value=properties,
        )

        if ifCtrl:
            ifCtrl.ifCase = parameter
            parameter = ifCtrl

        return parameter

    def __get_list(self, indent: int):
        """{ "-", value, [amt_ctrl], [if_else_ctrl], "\\n"}"""
        items = []

        try:
            while self.__get_tabs(indent):
                self.__check(TT.DASH)
                items.append(ValueNode(self.__next(TT.STRING)))
                self.__next(TT.NEWLINE)
        except:
            raise

        return ListNode(items)

    def __get_dict(self, indent: int) -> DictNode:
        """{ ["-"], parameter, "\\n" }
        """
        props = []

        try:
            while self.__get_tabs(indent):
                self.__check(TT.DASH)
                props.append(self.__get_parameter(indent))
                self.__next(TT.NEWLINE)
        except:
            raise

        return DictNode(props)

    def __get_properties(self, indent: int) -> list[ParameterNode]:
        """(list | dict)
        """

        next = self.__get_next_type(indent)

        if next == TT.STRING.value:
            props = self.__get_dict(indent)

        elif next == TT.DASH.value:
            diff = self.__get_next_type(indent+2)

            if diff == TT.COLUMN.value:
                props = self.__get_dict(indent)
            else:
                props = self.__get_list(indent)

        else:
            raise DSLSyntaxException(self.__next())

        return props

    def __get_nb_ctrl(self) -> AmountNode | None:
        """"amount", ":", int, ["#", var]"""
        nextToken = self.__check(TT.AMOUNT)
        if not nextToken:
            return None

        try:
            nb = self._pop(TT.INT)
        except DSLSyntaxException as e:
            raise e

        var = nextToken = self.__check(TT.AMOUNT)

        return AmountNode(
            amount=IntNode(nb),
            variable=VariableNode(var) if var else None,
            node=None,
        )

    def __get_if_ctrl(self) -> IfNode | None:
        """"if", condition"""
        condition = self.__check(TT.IF)
        if not condition:
            return None

        try:
            # TODO : Add real conditions
            condition = self.__next(TT.STRING)
        except DSLSyntaxException as e:
            raise e

        return IfNode(
            condition=condition,
            ifCase=None,
        )

    def __get_if_else_ctrl(self) -> IfElseNode | None:
        """if_ctrl, ["else" , valeur]"""
        ifCtrl = self.__get_if_ctrl()
        if not ifCtrl:
            return None

        if self.__get_next_type() == TT.ELSE.value:
            elseCase = self.__next(TT.STRING)
        else:
            elseCase = None

        return IfElseNode(
            condition=ifCtrl.condition,
            ifCase=None,
            elseCase=LiteralNode(elseCase),
        )
