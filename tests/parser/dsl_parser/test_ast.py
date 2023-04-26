from engine.ParsedFile import Position
from parser.dsl_parser.Token import Token
from parser.dsl_parser.AST import FileNode, DictNode, LiteralNode, ParameterNode,\
    ResourceNode, StringNode


def test_create_AST():
    # bucket nom-#test \n\t toto: tata
    tree = FileNode()

    tree.add(
        ResourceNode(
            resourceType=StringNode(
                Token(Position('file', 1, 1), 'STRING', 'bucket'),
            ),
            name=StringNode(
                Token(Position('file', 1, 8), 'STRING', 'nom-'),
                Token(Position('file', 1, 8), 'VAR', 'test'),
            ),

            # amount = IntNode(),

            # condition = IfNode(),

            parameters=DictNode(
                [
                    ParameterNode(
                        name=Token(Position('file', 2, 3), 'STRING', 'toto'),
                        value=LiteralNode(
                            Token(Position('file', 2, 9), 'STRING', 'tata'),
                        ),

                        # amount = IntNode(),

                        # condition = IfElseNode(),
                    ),
                ],
            ),
        ),
    )

    assert str(tree) == '<RESOURCE \
type = <STRING (STRING bucket)>, \
name = <STRING (STRING nom-) (VAR test)>, \
parameters = <DICT <PARAMETER name = (STRING toto), value = <LITERAL (STRING tata)>>>>'
