from parser.dsl_parser.Token import Token, TOKENTYPES as TT
from parser.dsl_parser.AST import FileNode, IfElseNode, IfNode, AmountNode, IntNode,\
    ResourceNode, StringNode, LiteralNode, VariableNode


class SyntaxException(Exception):
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

    def __pop(self, expected: TT | None = None) -> Token:
        tok = self.__tokens.pop(0)
        if expected and tok.tokenType != expected.value:
            raise SyntaxException(tok)
        return tok

    def __check(self, expected: TT) -> Token | None:
        token = self.__tokens[0]
        if token.tokenType != expected.value:
            return None

        return self.__pop(expected)

    def __create_resource(self, indent=0) -> ResourceNode | IfNode | AmountNode:
        try:
            for _ in range(indent):
                self.__pop(TT.TAB)

            resType = self.__pop(TT.STRING)
            name = self.__pop(TT.STRING)
            self.__pop(TT.COLUMN)

            nbCtrl = self.__get_nb_ctrl()
            ifCtrl = self.__get_if_ctrl()

            self.__pop(TT.NEWLINE)

            properties = self.__get_properties(indent+1)

        except SyntaxException as e:
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

    def __get_parameter(self):
        pass

    def __get_list(self):
        pass

    def __get_dict(self):
        pass

    def __get_properties(self, indent: int):
        return None

    def __get_nb_ctrl(self) -> AmountNode | None:
        nextToken = self.__check(TT.AMOUNT)
        if not nextToken:
            return None

        try:
            nb = self._pop(TT.INT)
        except SyntaxException as e:
            raise e

        var = nextToken = self.__check(TT.AMOUNT)

        return AmountNode(
            amount=IntNode(nb),
            variable=VariableNode(var) if var else None,
            node=None,
        )

    def __get_if_ctrl(self) -> IfNode | None:
        condition = self.__check(TT.IF)
        if not condition:
            return None

        try:
            # TODO : Add real conditions
            condition = self.__pop(TT.STRING)
        except SyntaxException as e:
            raise e

        return IfNode(
            condition=condition,
            ifCase=None,
        )

    def __get_if_else_ctrl(self) -> IfElseNode | None:
        ifCtrl = self.__get_if_ctrl()
        if not ifCtrl:
            return None

        try:
            elseCase = self.__pop(TT.STRING)
        except SyntaxException as e:
            raise e

        return IfElseNode(
            condition=ifCtrl.condition,
            ifCase=None,
            elseCase=LiteralNode(elseCase),
        )
