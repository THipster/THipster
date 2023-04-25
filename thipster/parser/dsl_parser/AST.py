from abc import ABC

from parser.dsl_parser.Token import Token


class Node(ABC):
    pass


class StringNode(Node):
    def __init__(self, *values: Token) -> None:
        super().__init__()
        self.__value = list(values)

    def __str__(self) -> str:
        return f"<STRING {' '.join(list(map(lambda x : str(x), self.__value)))}>"


class VariableNode(Node):
    def __init__(self, value: Token) -> None:
        super().__init__()
        self.__value = value

    def __str__(self) -> str:
        return f'<VAR {self.__value}>'


class IntNode(Node):
    def __init__(self, value: Token) -> None:
        super().__init__()
        self.__value = value

    def __str__(self) -> str:
        return f'<INT {self.__value}>'


class FloatNode(Node):
    def __init__(self, value: Token) -> None:
        super().__init__()
        self.__value = value

    def __str__(self) -> str:
        return f'<FLOAT {self.__value}>'


class IfNode(Node):
    def __init__(self, condition: StringNode, ifCase: Node) -> None:
        super().__init__()
        self.__condition = condition
        self.__ifCase = ifCase

    def __str__(self) -> str:
        return f'<IF {self.__condition}: {self.__ifCase}>'

    @property
    def condition(self):
        return self.__condition

    @property
    def ifCase(self):
        return self.__ifCase

    @ifCase.setter
    def ifCase(self, __value):
        self.__ifCase = __value


class IfElseNode(IfNode):
    def __init__(self, condition: StringNode, ifCase: Node, elseCase: Node) -> None:
        super().__init__(condition, ifCase)
        self.__elseCase = elseCase

    def __str__(self) -> str:
        return f'<IF_E {str(self.condition)}: {str(self.ifCase)}, ELSE : \
{str(self.elseCase)}>'

    @property
    def elseCase(self):
        return self.__elseCase


class AmountNode(Node):
    def __init__(self, amount: IntNode, variable: VariableNode, node: Node) -> None:
        super().__init__()
        self.__amount = amount
        self.__node = node
        self.__variable = variable

    def __str__(self) -> str:
        return f'<AMOUNT {self.__amount} #{self.__variable}: {self.__node}>'

    @property
    def node(self):
        return self.__node

    @node.setter
    def node(self, __value):
        self.__node = __value


class ValueNode(Node, ABC):
    pass


class ParameterNode(Node):
    def __init__(self, name: Token, value: ValueNode) -> None:
        super().__init__()
        self.__name = name
        self.__value = value

    def __str__(self) -> str:
        return f'<PARAMETER name = {str(self.__name)}, value = {str(self.__value)}>'

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, __value):
        self.__value = __value


class DictNode(ValueNode):
    def __init__(self, value: list[ParameterNode]) -> None:
        super().__init__()
        self.__value = value

    def __str__(self) -> str:
        return f"<DICT {' '.join(list(map(lambda x : str(x), self.__value)))}>"


class LiteralNode(ValueNode):
    def __init__(self, value: Token) -> None:
        super().__init__()
        self.__value = value

    def __str__(self) -> str:
        return f'<LITERAL {str(self.__value)}>'


class ListNode(ValueNode):
    def __init__(self, value: list[ValueNode]) -> None:
        super().__init__()
        self.__value = value

    def __str__(self) -> str:
        return f"<LIST {' '.join(list(map(lambda x : str(x), self.__value)))}>"


class ResourceNode(Node):
    def __init__(
        self,
        resourceType: StringNode,
        name: StringNode,
        parameters: ValueNode,
    ) -> None:
        super().__init__()
        self.__type = resourceType
        self.__name = name
        self.__parameters = parameters

    def __str__(self) -> str:
        return f'<RESOURCE type = {str(self.__type)}, \
name = {str(self.__name)}, parameters = {str(self.__parameters)}>'


class FileNode(Node):

    def __init__(self) -> None:
        super().__init__()
        self.__resources = []

    def add(self, item: ResourceNode) -> None:
        self.__resources.append(item)

    def __str__(self) -> str:
        return '\n'.join(list(map(lambda x: str(x), self.__resources)))
