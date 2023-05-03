from abc import ABC, abstractmethod
from engine.ParsedFile import Position

from parser.dsl_parser.Token import Token


class Node(ABC):

    @abstractmethod
    def accept(self, visitor):
        raise NotImplementedError()


class StringNode(Node):
    def __init__(self, *values: Token) -> None:
        super().__init__()
        self.__value = list(values)

    def __str__(self) -> str:
        return f"<STRING {' '.join(list(map(lambda x : str(x), self.__value)))}>"

    @property
    def values(self):
        return list(map(lambda x: x.value, self.__value))

    def accept(self, visitor):
        return visitor.visitString(self)


class VariableNode(Node):
    def __init__(self, name: Token) -> None:
        super().__init__()
        self.__name = name

    def __str__(self) -> str:
        return f'<VAR {self.__name}>'

    @property
    def name(self):
        return self.__name.value

    def accept(self, visitor):
        return visitor.visitVariable(self)


class IntNode(Node):
    def __init__(self, value: Token) -> None:
        super().__init__()
        self.__value = value

    def __str__(self) -> str:
        return f'<INT {self.__value}>'

    @property
    def value(self):
        return self.__value.value

    def accept(self, visitor):
        return visitor.visitInt(self)


class BoolNode(Node):
    def __init__(self, value: Token) -> None:
        super().__init__()
        self.__value = value

    def __str__(self) -> str:
        return f'<BOOL {self.__value}>'

    @property
    def value(self) -> bool:
        return self.__value.value

    def accept(self, visitor):
        return visitor.visitBool(self)


class FloatNode(Node):
    def __init__(self, value: Token) -> None:
        super().__init__()
        self.__value = value

    def __str__(self) -> str:
        return f'<FLOAT {self.__value}>'

    @property
    def value(self):
        return self.__value.value

    def accept(self, visitor):
        return visitor.visitFloat(self)


class VariableDefinitionNode(Node):
    def __init__(self, name: Token, value: IntNode) -> None:
        super().__init__()
        self.__name = name
        self.__value = value

    def __str__(self) -> str:
        return f'<VARDEF {self.__name} = {self.__value}>'

    @property
    def name(self):
        return self.__name.value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, __value):
        self.__value = __value

    def accept(self, visitor):
        return visitor.visitVariableDefinition(self)


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

    def accept(self, visitor):
        return visitor.visitIf(self)


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

    def accept(self, visitor):
        return visitor.visitIfElse(self)


class AmountNode(Node):
    def __init__(self, amount: IntNode, variable: VariableDefinitionNode, node: Node)\
            -> None:
        super().__init__()
        self.__amount = amount
        self.__node = node
        self.__variable = variable

    def __str__(self) -> str:
        return f'<AMOUNT {self.__amount} #{self.__variable}: {self.__node}>'

    @property
    def node(self) -> Node:
        return self.__node

    @property
    def amount(self) -> IntNode:
        return self.__amount

    @property
    def variable(self) -> VariableDefinitionNode:
        return self.__variable

    @node.setter
    def node(self, __value):
        self.__node = __value

    def accept(self, visitor):
        return visitor.visitAmount(self)


class ValueNode(Node, ABC):

    @abstractmethod
    def accept(self, visitor):
        raise NotImplementedError()


class ParameterNode(Node):
    def __init__(self, name: StringNode, value: ValueNode) -> None:
        super().__init__()
        self.__name = name
        self.__value = value
        self.__position = None

    def __str__(self) -> str:
        return f'<PARAMETER name = {str(self.__name)}, value = {str(self.__value)}>'

    @property
    def name(self):
        return self.__name

    @property
    def value(self):
        return self.__value

    @property
    def position(self):
        return self.__position

    @value.setter
    def value(self, __value):
        self.__value = __value

    def accept(self, visitor):
        return visitor.visitParameter(self)


class DictNode(ValueNode):
    def __init__(self, value: list[ParameterNode]) -> None:
        super().__init__()
        self.__value = value

    def __str__(self) -> str:
        return f"<DICT {' '.join(list(map(lambda x : str(x), self.__value)))}>"

    @property
    def value(self):
        return self.__value

    def accept(self, visitor):
        return visitor.visitDict(self)


class LiteralNode(ValueNode):
    def __init__(self, value: Node) -> None:
        super().__init__()
        self.__value = value

    def __str__(self) -> str:
        return f'<LITERAL {str(self.__value)}>'

    @property
    def value(self) -> Node:
        return self.__value

    def accept(self, visitor):
        return visitor.visitLiteral(self)


class ListNode(ValueNode):
    def __init__(self, value: list[ValueNode]) -> None:
        super().__init__()
        self.__value = value

    def __str__(self) -> str:
        return f"<LIST {' '.join(list(map(lambda x : str(x), self.__value)))}>"

    @property
    def value(self):
        return self.__value

    def accept(self, visitor):
        return visitor.visitList(self)


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
        self.__position = None
        self.__parameters = parameters

    def __str__(self) -> str:
        return f'<RESOURCE type = {str(self.__type)}, \
name = {str(self.__name)}, parameters = {str(self.__parameters)}>'

    @property
    def type(self) -> StringNode:
        return self.__type

    @property
    def name(self) -> StringNode:
        return self.__name

    @property
    def position(self) -> Position:
        return self.__position

    @property
    def parameters(self) -> ValueNode:
        return self.__parameters

    def accept(self, visitor):
        return visitor.visitResource(self)


class FileNode(Node):

    def __init__(self) -> None:
        super().__init__()
        self.__resources = []

    def add(self, item: ResourceNode) -> None:
        self.__resources.append(item)

    def __str__(self) -> str:
        return '\n'.join(list(map(lambda x: str(x), self.__resources)))

    @property
    def resources(self) -> list[ResourceNode]:
        return self.__resources

    def accept(self, visitor):
        return visitor.visitFile(self)
