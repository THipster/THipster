"""Tests for the ParsedFile object."""
import thipster.engine.parsed_file as pf


def test_create_parsed_file():
    """Test creating a ParsedFile object."""
    parsed_file = pf.ParsedFile()

    assert isinstance(parsed_file, pf.ParsedFile)


def test_create_resource():
    """Test creating a ParsedResource object."""
    pos = pf.Position('test_file', 3, 7)
    resource = pf.ParsedResource(
        'test_type', 'test_name',
        attributes=None, position=pos,
    )

    assert isinstance(resource, pf.ParsedResource)
    assert resource.resource_type == 'test_type'
    assert resource.name == 'test_name'
    assert resource.attributes is None
    assert resource.position is pos


def test_create_position():
    """Test creating a Position object."""
    pos = pf.Position('test_file', ln=3, col=7)

    assert isinstance(pos, pf.Position)
    assert pos.ln == 3
    assert pos.col == 7


def test_create_num_attr():
    """Test creating a ParsedAttribute object with a number value."""
    val = pf.ParsedLiteral(3)
    pos = pf.Position('test_file', 3, 7)

    attr = pf.ParsedAttribute('test_attr', value=val, position=pos)

    assert isinstance(attr, pf.ParsedAttribute)
    assert isinstance(attr._ParsedAttribute__value, pf.ParsedLiteral)
    assert attr.value == 3


def test_create_str_attr():
    """Test creating a ParsedAttribute object with a string value."""
    val = pf.ParsedLiteral('test_value')
    pos = pf.Position('test_file', 3, 7)

    attr = pf.ParsedAttribute('test_attr', value=val, position=pos)

    assert isinstance(attr, pf.ParsedAttribute)
    assert isinstance(attr._ParsedAttribute__value, pf.ParsedLiteral)
    assert attr.value == 'test_value'


def test_create_list_str_attr():
    """Test creating a ParsedAttribute object with a list value."""
    val = pf.ParsedList(
        [pf.ParsedLiteral('test_value_' + str(i)) for i in range(3)],
    )
    pos = pf.Position('test_file', 3, 7)

    attr = pf.ParsedAttribute('test_attr', value=val, position=pos)

    assert isinstance(attr, pf.ParsedAttribute)
    assert isinstance(attr._ParsedAttribute__value, pf.ParsedList)

    assert len(attr.value) == 3
    for val in attr.value:
        assert 'test_value' in val.value


def test_create_dict_str_attr():
    """Test creating a ParsedAttribute object with a dict value."""
    val = pf.ParsedDict(
        {pf.ParsedLiteral('test_value_' + str(i)) for i in range(3)},
    )
    pos = pf.Position('test_file', 3, 7)

    attr = pf.ParsedAttribute('test_attr', value=val, position=pos)

    assert isinstance(attr, pf.ParsedAttribute)
    assert isinstance(attr._ParsedAttribute__value, pf.ParsedDict)

    assert len(attr.value) == 3
    for val in attr.value:
        assert 'test_value' in val.value


def test_create_composite_attr():
    """Test creating a ParsedAttribute object with a composite value."""
    attr = [
        pf.ParsedAttribute(
            'attr_num',
            value=pf.ParsedLiteral(3),
            position=pf.Position('test_file', 3, 7),
        ),
        pf.ParsedAttribute(
            'attr_str',
            value=pf.ParsedLiteral('test'),
            position=pf.Position('test_file', 4, 7),
        ),
        pf.ParsedAttribute(
            'attr_list',
            value=pf.ParsedList([
                pf.ParsedLiteral('test_list_1'),
                pf.ParsedLiteral('test_list_2'),
                pf.ParsedLiteral('test_list_3'),
            ]),
            position=pf.Position('test_file', 5, 7),
        ),
        pf.ParsedAttribute(
            'attr_dict',
            value=pf.ParsedDict([
                pf.ParsedAttribute(
                    'attr_dict_1',
                    value=pf.ParsedLiteral('test'),
                    position=pf.Position('test_file', 11, 7),
                ),
                pf.ParsedAttribute(
                    'attr_dict_2',
                    value=pf.ParsedLiteral('test'),
                    position=pf.Position('test_file', 12, 7),
                ),
            ]),
            position=pf.Position('test_file', 10, 7),
        ),
    ]

    resource = pf.ParsedResource(
        'test_type',
        'test_name',
        position=pf.Position('test_file', 3, 7),
        attributes=attr,
    )

    assert isinstance(resource, pf.ParsedResource)
    assert resource.resource_type == 'test_type'
    assert isinstance(resource.attributes, list)
    for attribute in resource.attributes:
        assert isinstance(attribute, pf.ParsedAttribute)
        assert isinstance(
            attribute._ParsedAttribute__value,
            pf.ParsedValue,
        )
        if isinstance(attribute._ParsedAttribute__value, pf.ParsedDict):
            for val in attribute.value:
                assert isinstance(val, pf.ParsedAttribute)

        elif isinstance(attribute._ParsedAttribute__value, pf.ParsedList):
            for val in attribute.value:
                assert isinstance(val, pf.ParsedValue)


def test_add_resource():
    """Test adding a resource to a ParsedFile object."""
    parsed_file = pf.ParsedFile()

    pos = pf.Position('test_file', 3, 7)
    resource = pf.ParsedResource(
        'test_type', 'test_name',
        attributes=None, position=pos,
    )

    parsed_file.resources.append(resource)

    assert resource in parsed_file.resources
