from thipster.engine.ParsedFile import Position
from thipster.parser.dsl_parser.Token import Token
import thipster.parser.dsl_parser.AST as ast


def test_create_AST():
    # bucket nom-#test \n\t toto: tata
    tree = ast.FileNode()

    tree.add(
        ast.ResourceNode(
            resourceType=ast.StringNode(
                Token(Position('file', 1, 1), 'STRING', 'bucket'),
            ),
            name=ast.StringExprNode(
                Token(Position('file', 1, 8), 'STRING', 'nom-'),
                Token(Position('file', 1, 8), 'VAR', 'test'),
            ),

            # amount = IntNode(),

            # condition = IfNode(),

            parameters=ast.DictNode(
                [
                    ast.ParameterNode(
                        name=Token(Position('file', 2, 3), 'STRING', 'toto'),
                        value=ast.LiteralNode(
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
name = <STRING-EXPR (STRING nom-) (VAR test)>, \
parameters = <DICT <PARAMETER name = (STRING toto), value = <LITERAL (STRING tata)>>>>'
