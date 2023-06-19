"""Test the AST of the DSL parser."""
import thipster.parser.dsl_parser.ast as ast
from thipster.engine.parsed_file import Position
from thipster.parser.dsl_parser.token import Token


def test_create_ast():
    """Test the creation of an AST."""
    # bucket nom-#test \n\t toto: tata
    tree = ast.FileNode()

    tree.add(
        ast.ResourceNode(
            resource_type=ast.StringNode(
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
