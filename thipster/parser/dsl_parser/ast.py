"""THipster's DSL AST (Abstract Syntax Tree) module."""
from abc import ABC, abstractmethod

from thipster.engine.parsed_file import Position

from .token import Token


class Node(ABC):
    """Abstract base AST node."""

    @abstractmethod
    def accept(self, visitor):
        """Accept visitor method."""
        raise NotImplementedError

    @property
    def position(self):
        """Return node's position in the file."""
        raise NotImplementedError


class StringNode(Node):
    """String node."""

    def __init__(self, token: Token) -> None:
        super().__init__()
        self.token = token

    def __str__(self) -> str:
        """Return string representation of the node."""
        return f'<STRING {self.token}>'

    @property
    def position(self) -> Position:
        """Return node's position in the file."""
        return self.token.position

    def accept(self, visitor):
        """Accept visitor method."""
        return visitor.visit_string(self)


class StringExprNode(Node):
    """String expression node."""

    def __init__(self, *values: Node | list[Node]) -> None:
        super().__init__()
        self.values: list[Node] = []
        for v in values:
            if isinstance(v, list):
                self.values.extend(v)
            else:
                self.values.append(v)

    def __str__(self) -> str:
        """Return string representation of the node."""
        return f"<STRING-EXPR {' '.join(list(map(str, self.values)))}>"

    @property
    def position(self) -> Token:
        """Return node's position in the file."""
        return self.values[0].position

    def accept(self, visitor):
        """Accept visitor method."""
        return visitor.visit_string_expr(self)


class VariableNode(Node):
    """Variable node."""

    def __init__(self, token: Token) -> None:
        super().__init__()
        self.token = token

    def __str__(self) -> str:
        """Return string representation of the node."""
        return f'<VAR {self.token}>'

    @property
    def name(self):
        """Return variable's name."""
        return self.token.value

    @property
    def position(self) -> Position:
        """Return node's position in the file."""
        return self.token.position

    def accept(self, visitor):
        """Accept visitor method."""
        return visitor.visit_variable(self)


class BoolNode(Node):
    """Boolean node."""

    def __init__(self, token: Token) -> None:
        super().__init__()
        self.token = token

    def __str__(self) -> str:
        """Return string representation of the node."""
        return f'<BOOL {self.token}>'

    @property
    def position(self) -> Position:
        """Return node's position in the file."""
        return self.token.position

    def accept(self, visitor):
        """Accept visitor method."""
        return visitor.visit_bool(self)


class IntNode(Node):
    """Integer node."""

    def __init__(self, token: Token) -> None:
        super().__init__()
        self.token = token

    def __str__(self) -> str:
        """Return string representation of the node."""
        return f'<INT {self.token}>'

    @property
    def position(self) -> Position:
        """Return node's position in the file."""
        return self.token.position

    def accept(self, visitor):
        """Accept visitor method."""
        return visitor.visit_int(self)


class FloatNode(Node):
    """Float node."""

    def __init__(self, token: Token) -> None:
        super().__init__()
        self.token = token

    def __str__(self) -> str:
        """Return string representation of the node."""
        return f'<FLOAT {self.token}>'

    @property
    def position(self) -> Position:
        """Return node's position in the file."""
        return self.token.position

    def accept(self, visitor):
        """Accept visitor method."""
        return visitor.visit_float(self)


class VariableDefinitionNode(Node):
    """Variable definition node."""

    def __init__(self, name: Token, value: IntNode) -> None:
        super().__init__()
        self.__name = name
        self.value = value

    def __str__(self) -> str:
        """Return string representation of the node."""
        return f'<VARDEF {self.__name} = {self.value}>'

    @property
    def name(self):
        """Return variable's name."""
        return self.__name.value

    @property
    def position(self) -> Position:
        """Return node's position in the file."""
        return self.__name.position

    def accept(self, visitor):
        """Accept visitor method."""
        return visitor.visit_variable_definition(self)


class IfNode(Node):
    """If node."""

    def __init__(self, condition: StringNode, if_case: Node) -> None:
        super().__init__()
        self.condition = condition
        self.if_case = if_case

    def __str__(self) -> str:
        """Return string representation of the node."""
        return f'<IF {self.condition}: {self.if_case}>'

    @property
    def position(self) -> Position:
        """Return node's position in the file."""
        return self.if_case.position

    def accept(self, visitor):
        """Accept visitor method."""
        return visitor.visit_if(self)


class IfElseNode(IfNode):
    """If-else node."""

    def __init__(
        self, condition: StringNode, if_case: Node,
        else_case: Node | None,
    ) -> None:
        super().__init__(condition, if_case)
        self.else_case = else_case

    def __str__(self) -> str:
        """Return string representation of the node."""
        return f'<IF_E {self.condition!s}: {self.if_case!s}, ELSE : \
{self.else_case!s}>'

    def accept(self, visitor):
        """Accept visitor method."""
        return visitor.visit_ifelse(self)


class AmountNode(Node):
    """Amount node."""

    def __init__(
        self, position: Token,
        amount: Node, variable: VariableDefinitionNode | None, node: Node | None,
    )\
            -> None:
        super().__init__()
        self.__position = position
        self.amount = amount
        self.node = node
        self.variable = variable

    def __str__(self) -> str:
        """Return string representation of the node."""
        return f'<AMOUNT {self.amount} #{self.variable}: {self.node}>'

    @property
    def position(self) -> Position:
        """Return node's position in the file."""
        return self.__position

    @position.setter
    def position(self, _value) -> Position:
        self.__position = _value

    def accept(self, visitor):
        """Accept visitor method."""
        return visitor.visit_amount(self)


class ValueNode(Node, ABC):
    """Abstract base value node."""

    pass


class ParameterNode(Node):
    """Parameter node."""

    def __init__(self, name: StringNode, value: ValueNode) -> None:
        super().__init__()
        self.name = name
        self.value = value

    def __str__(self) -> str:
        """Return string representation of the node."""
        return f'<PARAMETER name = {self.name!s}, value = {self.value!s}>'

    @property
    def position(self) -> Position:
        """Return node's position in the file."""
        return self.name.position

    def accept(self, visitor):
        """Accept visitor method."""
        return visitor.visit_parameter(self)


class DictNode(ValueNode):
    """Dictionary node."""

    def __init__(self, values: list[ParameterNode]) -> None:
        super().__init__()
        self.values = values

    def __str__(self) -> str:
        """Return string representation of the node."""
        return f"<DICT {' '.join(list(map(str, self.values)))}>"

    @property
    def position(self) -> Position:
        """Return node's position in the file."""
        return self.values[0].position

    def accept(self, visitor):
        """Accept visitor method."""
        return visitor.visit_dict(self)


class LiteralNode(ValueNode):
    """Literal node."""

    def __init__(self, values: Node) -> None:
        super().__init__()
        self.value = values

    def __str__(self) -> str:
        """Return string representation of the node."""
        return f'<LITERAL {self.value!s}>'

    @property
    def position(self) -> Position:
        """Return node's position in the file."""
        return self.value.position

    def accept(self, visitor):
        """Accept visitor method."""
        return visitor.visit_literal(self)


class ListNode(ValueNode):
    """List node."""

    def __init__(self, values: list[ValueNode]) -> None:
        super().__init__()
        self.values = values

    def __str__(self) -> str:
        """Return string representation of the node."""
        return f"<LIST {' '.join(list(map(str, self.values)))}>"

    @property
    def position(self) -> Position:
        """Return node's position in the file."""
        return self.values[0].position

    def accept(self, visitor):
        """Accept visitor method."""
        return visitor.visit_list(self)


class CompExprNode(Node):
    """Comparison expression node."""

    def __init__(
            self, left_value: Node, operation, right_value: Node | None = None,
    ) -> None:
        super().__init__()
        self.left_value = left_value
        self.operation = operation
        self.right_value = right_value

    @property
    def position(self) -> Position:
        """Return node's position in the file."""
        return self.left_value.position

    def accept(self, visitor):
        """Accept visitor method."""
        return visitor.visit_comp_expr(self)


class TermNode(Node):
    """Term node."""

    def __init__(self, factors, operation) -> None:
        super().__init__()
        if len(factors) != len(operation) + 1:
            raise
        self.factors: list[FactorNode] = factors
        self.operation = operation

    @property
    def position(self) -> Position:
        """Return node's position in the file."""
        return self.factors[0].position

    def accept(self, visitor):
        """Accept visitor method."""
        return visitor.visit_term(self)


class ArithExprNode(Node):
    """Arithmetic expression node."""

    def __init__(self, terms: list[TermNode], operations) -> None:
        super().__init__()
        if len(terms) != len(operations) + 1:
            raise
        self.terms = terms
        self.operations = operations

    @property
    def position(self) -> Position:
        """Return node's position in the file."""
        return self.terms[0].position

    def accept(self, visitor):
        """Accept visitor method."""
        return visitor.visit_arith_expr(self)


class FactorNode(Node):
    """Factor node."""

    def __init__(self, factors: list[Node], operation) -> None:
        super().__init__()
        self.factors = factors
        self.operation = operation

    @property
    def position(self) -> Position:
        """Return node's position in the file."""
        return self.factors[0].position

    def accept(self, visitor):
        """Accept visitor method."""
        return visitor.visit_factor(self)


class ResourceNode(Node):
    """Resource node."""

    def __init__(
        self,
        resource_type: StringNode,
        name: StringNode,
        parameters: DictNode | ListNode,
    ) -> None:
        super().__init__()
        self.type = resource_type
        self.name = name
        self.parameters = parameters

    def __str__(self) -> str:
        """Return string representation of the node."""
        return f'<RESOURCE type = {self.type!s}, \
name = {self.name!s}, parameters = {self.parameters!s}>'

    @property
    def position(self) -> Position:
        """Return node's position in the file."""
        return self.type.position

    def accept(self, visitor):
        """Accept visitor method."""
        return visitor.visit_resource(self)


class FileNode(Node):
    """File node."""

    def __init__(self) -> None:
        super().__init__()
        self.resources: list[ResourceNode | IfNode | AmountNode] = []

    def add(self, item: ResourceNode | IfNode | AmountNode) -> None:
        """Add item to the node."""
        self.resources.append(item)

    def __str__(self) -> str:
        """Return string representation of the node."""
        return '\n'.join(list(map(str, self.resources)))

    @property
    def position(self) -> Position:
        """Return node's position in the file."""
        return self.resources[0].position

    def accept(self, visitor):
        """Accept visitor method."""
        return visitor.visit_file(self)
