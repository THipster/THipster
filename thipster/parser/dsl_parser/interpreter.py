"""Interpreter for the DSL Parser."""
import thipster.engine.parsed_file as pf
import thipster.parser.dsl_parser.ast as ast

from .exceptions import (
    DSLArithmeticError,
    DSLParserVariableAlreadyUsedError,
    DSLParserVariableNotDeclaredError,
)
from .token import TOKENTYPES as TT


class Interpreter():
    """Interpreter class for the DSL Parser.

    Implements a visitor design pattern on the AST nodes
    """

    def __init__(self) -> None:
        """Interpreter class for the DSL Parser.

        Implements a visitor design pattern on the AST nodes
        """
        super().__init__()

        self.__variables = dict[str, int]()

    def run(self, tree: ast.FileNode) -> pf.ParsedFile:
        """Run the interpreter on an Abstract Syntax Tree.

        Parameters
        ----------
        tree: FileNode
            The root node of the abstract syntax tree

        Returns
        -------
        ParsedFile
            The parsed file stucture assiociated to the given AST
        """
        return tree.accept(self)

    def visit_comp_expr(self, element: ast.CompExprNode) -> bool:
        """Visitor for a CompExprNode.

        Parameters
        ----------
        element: CompExprNode
            The visited node

        Returns
        -------
        bool
            The boolean value of the node
        """
        match element.operation.token_type:
            case TT.NOT:
                return pf.ParsedLiteral(not element.left_value.accept(self).value)

            case TT.OR:
                return pf.ParsedLiteral(
                    element.left_value.accept(self).value or
                    element.right_value.accept(self).value,
                )

            case TT.AND:
                return pf.ParsedLiteral(
                    element.left_value.accept(self).value and
                    element.right_value.accept(self).value,
                )

            case TT.EE:
                return pf.ParsedLiteral(
                    element.left_value.accept(self).value ==
                    element.right_value.accept(self).value,
                )

            case TT.NE:
                return pf.ParsedLiteral(
                    element.left_value.accept(self).value !=
                    element.right_value.accept(self).value,
                )

            case TT.LT:
                return pf.ParsedLiteral(
                    element.left_value.accept(self).value <
                    element.right_value.accept(self).value,
                )

            case TT.LTE:
                return pf.ParsedLiteral(
                    element.left_value.accept(self).value <=
                    element.right_value.accept(self).value,
                )

            case TT.GT:
                return pf.ParsedLiteral(
                    element.left_value.accept(self).value >
                    element.right_value.accept(self).value,
                )

            case TT.GTE:
                return pf.ParsedLiteral(
                    element.left_value.accept(self).value >=
                    element.right_value.accept(self).value,
                )

    def visit_arith_expr(self, element: ast.ArithExprNode) -> int | float:
        """Visitor for an ArithExprNode.

        Parameters
        ----------
        element: ArithExprNode
            The visited node

        Returns
        -------
        int | float
            The arithmetic value of the node
        """
        total = element.terms[0].accept(self)
        if isinstance(total, pf.ParsedLiteral):
            total = total.value

        for i in range(len(element.operations)):
            match element.operations[i]:
                case TT.PLUS:
                    add = element.terms[i+1].accept(self)
                    if isinstance(add, pf.ParsedLiteral):
                        add = add.value
                    total += add

                case TT.MINUS:
                    rm = element.terms[i+1].accept(self)
                    if isinstance(rm, pf.ParsedLiteral):
                        rm = rm.value
                    total -= rm

        return pf.ParsedLiteral(total)

    def visit_term(self, element: ast.TermNode) -> int | float:
        """Visitor for a TermNode.

        Parameters
        ----------
        element: TermNode
            The visited node

        Returns
        -------
        int | float
            The arithmetic value of the node
        """
        total = element.factors[0].accept(self)
        if isinstance(total, pf.ParsedLiteral):
            total = total.value

        for i in range(len(element.operation)):
            match element.operation[i]:
                case TT.MUL:
                    mul = element.factors[i+1].accept(self)
                    if isinstance(mul, pf.ParsedLiteral):
                        mul = mul.value
                    total *= mul

                case TT.DIV:
                    div = element.factors[i+1].accept(self)
                    if isinstance(div, pf.ParsedLiteral):
                        div = div.value
                    total /= div

        return total

    def visit_factor(self, element: ast.FactorNode) -> int | float:
        """Visitor for a Factor node.

        Parameters
        ----------
        element: FactorNode
            The visited node

        Returns
        -------
        int | float
            The arithmetic value of the node
        """
        total = element.factors[0].accept(self)
        if isinstance(total, pf.ParsedLiteral):
            total = total.value

        match element.operation:
            case TT.PLUS:
                return pf.ParsedLiteral(total)

            case TT.MINUS:
                return pf.ParsedLiteral(-total)

            case TT.POW:
                for f in element.factors[1:]:
                    power = f.accept(self)
                    if isinstance(power, pf.ParsedLiteral):
                        power = power.value
                    total = total**power
                return pf.ParsedLiteral(total)

    def visit_string_expr(self, element: ast.StringExprNode) -> str:
        """Visitor for a StringExprNode.

        Parameters
        ----------
        element: StringExprNode
            The visited node

        Returns
        -------
        str
            The string value of the node
        """
        ret = ''
        for value in element.values:
            ret += str(value.accept(self))

        return pf.ParsedLiteral(ret)

    def visit_variable_definition(self, element: ast.VariableDefinitionNode) -> str:
        """Visitor for a VariableDefinitionNode.

        Parameters
        ----------
        element: VariableDefinitionNode
            The visited node

        Returns
        -------
        str
            The name of the declared variable

        Raises
        ------
        DSLParserVariableAlreadyUsed
            Tried to declare a varible that was already declared
        """
        if element.name in self.__variables:
            raise DSLParserVariableAlreadyUsedError(element.name)

        self.__variables[element.name] = element.value.accept(self)

        return element.name

    def visit_variable(self, element: ast.VariableNode) -> object:
        """Visitor for a VariableNode.

        Parameters
        ----------
        element: VariableNode
            The visited node

        Returns
        -------
        object
            The value of the declared variable

        Raises
        ------
        DSLParserVariableNotDeclared
            Tried to use a varible that was not declared
        """
        if element.name not in self.__variables:
            raise DSLParserVariableNotDeclaredError(element.name)

        return self.__variables[element.name]

    def visit_int(self, element: ast.IntNode) -> int:
        """Visitor for an IntNode.

        Parameters
        ----------
        element: IntNode
            The visited node

        Returns
        -------
        int
            The value of the node
        """
        return int(element.token.value)

    def visit_float(self, element: ast.FloatNode) -> float:
        """Visitor for a FloatNode.

        Parameters
        ----------
        element: FloatNode
            The visited node

        Returns
        -------
        float
            The value of the node
        """
        return float(element.token.value)

    def visit_bool(self, element: ast.BoolNode) -> bool:
        """Visitor for a BoolNode.

        Parameters
        ----------
        element: BoolNode
            The visited node

        Returns
        -------
        bool
            The value of the node
        """
        return bool(element.token.value)

    def visit_string(self, element: ast.StringNode) -> str:
        """Visitor for a BoolNode.

        Parameters
        ----------
        element: BoolNode
            The visited node

        Returns
        -------
        bool
            The value of the node
        """
        return str(element.token.value)

    def visit_if(self, element: ast.IfNode) -> object | None:
        """Visitor for an IfNode.

        Parameters
        ----------
        element: IfNode
            The visited node

        Returns
        -------
        object | None
            The value of the child node if the condition is true, else None
        """
        return element.if_case.accept(self) if element.condition.accept(self).value\
            else None

    def visit_ifelse(self, element: ast.IfElseNode):
        """Visitor for an IfElseNode.

        Parameters
        ----------
        element: IfElseNode
            The visited node

        Returns
        -------
        object | None
            The value of the "if" child node if the condition is true, else the value\
            of the "else" child node
        """
        return element.if_case.accept(self) if element.condition.accept(self).value\
            else element.else_case.accept(self)

    def visit_amount(self, element: ast.AmountNode) -> list[object]:
        """Visitor for an AmountNode.

        Parameters
        ----------
        element: AmountNode
            The visited node

        Returns
        -------
        list[object]
            A list with the required number of object (resource, list item, ...)
        """
        var = element.variable.accept(self) if element.variable else None
        res = []
        amount = element.amount.accept(self).value
        if not isinstance(amount, int):
            raise DSLArithmeticError(
                element.amount.position, 'Integer expected',
            )

        for _ in range(amount):
            res += element.node.accept(self)
            if var:
                self.__variables[var] += 1
        return res

    def visit_parameter(self, element: ast.ParameterNode) -> pf.ParsedAttribute:
        """Visitor for a ParameterNode.

        Parameters
        ----------
        element: ParameterNode
            The visited node

        Returns
        -------
        ParsedAttribute
            A ParsedAttribute object containing the name, position and value of \
                the node
        """
        return pf.ParsedAttribute(
            name=element.name.accept(self),
            position=element.position,
            value=element.value.accept(self),
        )

    def visit_dict(self, element: ast.DictNode) -> pf.ParsedDict:
        """Visitor for a DictNode.

        Parameters
        ----------
        element: DictNode
            The visited node

        Returns
        -------
        ParsedDict
            A ParsedDict object based on the node attributes
        """
        return pf.ParsedDict([v.accept(self) for v in element.values])

    def visit_literal(self, element: ast.LiteralNode) -> pf.ParsedLiteral:
        """Visitor for a LiteralNode.

        Parameters
        ----------
        element: LiteralNode
            The visited node

        Returns
        -------
        ParsedLiteral
            A ParsedLiteral object based on the node value
        """
        return pf.ParsedLiteral(element.value.accept(self))

    def visit_list(self, element: ast.ListNode) -> pf.ParsedList:
        """Visitor for a ListNode.

        Parameters
        ----------
        element: ListNode
            The visited node

        Returns
        -------
        ParsedList
            A ParsedLiteral object based on the node elements
        """
        return pf.ParsedList([v.accept(self) for v in element.values])

    def visit_resource(self, element: ast.ResourceNode) -> list[pf.ParsedResource]:
        """Visitor for a ResourceNode.

        Parameters
        ----------
        element: ResourceNode
            The visited node

        Returns
        -------
        int
            A ParsedResource object based on the node's attributes
        """
        return [
            pf.ParsedResource(
                parsed_resource_type=element.type.accept(self).value,
                name=element.name.accept(self).value,
                position=element.position,
                attributes=[v.accept(self) for v in element.parameters.values],
            ),
        ]

    def visit_file(self, element: ast.FileNode):
        """Visitor for a FileNode.

        Parameters
        ----------
        element: FileNode
            The visited node

        Returns
        -------
        ParsedFile
            A ParsedFile object based on the node's resources
        """
        parsed_file = pf.ParsedFile()
        for res in element.resources:
            parsed_file.resources += res.accept(self)

        return parsed_file
