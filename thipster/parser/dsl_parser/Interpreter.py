from engine.ParsedFile import ParsedAttribute, ParsedDict, ParsedFile, ParsedList, \
    ParsedLiteral, ParsedResource
from parser.dsl_parser.AST import AmountNode, BoolNode, DictNode, FileNode, FloatNode, \
    IfElseNode, IfNode, IntNode, ListNode, LiteralNode, ParameterNode, ResourceNode, \
    StringNode, VariableDefinitionNode, VariableNode
from parser.dsl_parser.DSLExceptions import DSLParserBaseException


class DSLParserVariableAlreadyUsed(DSLParserBaseException):
    def __init__(self, var, *args: object) -> None:
        super().__init__(f'Variable already used : {var}', *args)


class DSLParserVariableNotDeclared(DSLParserBaseException):
    def __init__(self, var, *args: object) -> None:
        super().__init__(f'Variable already used : {var}', *args)


class Interpreter():
    def __init__(self) -> None:
        super().__init__()

        self.__variables = {}

    def run(self, tree: FileNode) -> ParsedFile:
        return tree.accept(self)

    def visitString(self, element: StringNode):
        return ''.join(element.values)

    def visitVariableDefinition(self, element: VariableDefinitionNode):
        if element.name in self.__variables:
            raise DSLParserVariableAlreadyUsed

        self.__variables[element.name] = element.value.accept(self)

        return element.name

    def visitVariable(self, element: VariableNode):
        if element.name not in self.__variables:
            raise DSLParserVariableNotDeclared

        return self.__variables[element.name]

    def visitInt(self, element: IntNode):
        return int(element.value)

    def visitFloat(self, element: FloatNode):
        return float(element.value)

    def visitBool(self, element: BoolNode):
        return bool(element.value)

    def visitIf(self, element: IfNode):
        return element.ifCase.accept(self) if eval(element.condition.accept(self)) \
            else None

    def visitIfElse(self, element: IfElseNode):
        return element.ifCase.accept(self) if eval(element.condition.accept(self))\
            else element.elseCase.accept(self)

    def visitAmount(self, element: AmountNode):
        var = element.variable.accept(self) if element.variable else None
        res = []

        for _ in range(element.amount.accept(self)):
            res += element.node.accept(self)
            if var:
                self.__variables[var] += 1
        return res

    def visitParameter(self, element: ParameterNode):
        return ParsedAttribute(
            name=element.name.accept(self),
            position=element.position,
            value=element.value.accept(self),
        )

    def visitDict(self, element: DictNode):
        return ParsedDict([v.accept(self) for v in element.value])

    def visitLiteral(self, element: LiteralNode):
        return ParsedLiteral(element.value.accept(self))

    def visitList(self, element: ListNode):
        return ParsedList([v.accept(self) for v in element.value])

    def visitResource(self, element: ResourceNode):
        return [
            ParsedResource(
                type=element.type.accept(self),
                name=element.name.accept(self),
                position=element.position,
                attributes=[v.accept(self) for v in element.parameters.value],
            ),
        ]

    def visitFile(self, element: FileNode):
        file = ParsedFile()
        for res in element.resources:
            file.resources += res.accept(self)

        return file
