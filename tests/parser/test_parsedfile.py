import engine.ParsedFile as pf


def test_create_parsed_file():
    file = pf.ParsedFile()

    assert isinstance(file, pf.ParsedFile)


def test_create_resource():
    pos = pf.Position(3, 7)
    resource = pf.ParsedResource(
        'test_type', 'test_name',
        attributes=None, position=pos,
    )

    assert isinstance(resource, pf.ParsedResource)
    assert resource.type == 'test_type'
    assert resource.name == 'test_name'
    assert resource.attributes is None
    assert resource.position is pos


def test_create_position():
    pos = pf.Position(ln=3, col=7)

    assert isinstance(pos, pf.Position)
    assert pos.ln == 3
    assert pos.col == 7


def test_create_num_attr():
    val = pf.Parsed_Literal(3)
    pos = pf.Position(3, 7)

    attr = pf.Parsed_Attribute('test_attr', value=val, position=pos)

    assert isinstance(attr, pf.Parsed_Attribute)
    assert isinstance(attr._Parsed_Attribute__value, pf.Parsed_Literal)
    assert attr.value == 3


def test_create_str_attr():
    val = pf.Parsed_Literal('test_value')
    pos = pf.Position(3, 7)

    attr = pf.Parsed_Attribute('test_attr', value=val, position=pos)

    assert isinstance(attr, pf.Parsed_Attribute)
    assert isinstance(attr._Parsed_Attribute__value, pf.Parsed_Literal)
    assert attr.value == 'test_value'


def test_create_list_str_attr():
    val = pf.Parsed_List(
        [pf.Parsed_Literal('test_value_' + str(i)) for i in range(3)],
    )
    pos = pf.Position(3, 7)

    attr = pf.Parsed_Attribute('test_attr', value=val, position=pos)

    assert isinstance(attr, pf.Parsed_Attribute)
    assert isinstance(attr._Parsed_Attribute__value, pf.Parsed_List)

    assert len(attr.value) == 3
    for val in attr.value:
        assert 'test_value' in val.value


def test_create_dict_str_attr():
    val = pf.Parsed_Dict(
        {pf.Parsed_Literal('test_value_' + str(i)) for i in range(3)},
    )
    pos = pf.Position(3, 7)

    attr = pf.Parsed_Attribute('test_attr', value=val, position=pos)

    assert isinstance(attr, pf.Parsed_Attribute)
    assert isinstance(attr._Parsed_Attribute__value, pf.Parsed_Dict)

    assert len(attr.value) == 3
    for val in attr.value:
        assert 'test_value' in val.value


def test_create_composite_attr():
    attr = [
        pf.Parsed_Attribute(
            'attr_num',
            value=pf.Parsed_Literal(3),
            position=pf.Position(3, 7),
        ),
        pf.Parsed_Attribute(
            'attr_str',
            value=pf.Parsed_Literal('test'),
            position=pf.Position(4, 7),
        ),
        pf.Parsed_Attribute(
            'attr_list',
            value=pf.Parsed_List([
                pf.Parsed_Literal('test_list_1'),
                pf.Parsed_Literal('test_list_2'),
                pf.Parsed_Literal('test_list_3'),
            ]),
            position=pf.Position(5, 7),
        ),
        pf.Parsed_Attribute(
            'attr_dict',
            value=pf.Parsed_Dict([
                pf.Parsed_Attribute(
                    'attr_dict_1',
                    value=pf.Parsed_Literal('test'),
                    position=pf.Position(11, 7),
                ),
                pf.Parsed_Attribute(
                    'attr_dict_2',
                    value=pf.Parsed_Literal('test'),
                    position=pf.Position(12, 7),
                ),
            ]),
            position=pf.Position(10, 7),
        ),
    ]

    resource = pf.ParsedResource(
        'test_type',
        'test_name',
        position=pf.Position(3, 7),
        attributes=attr,
    )

    assert isinstance(resource, pf.ParsedResource)
    assert resource.type == 'test_type'
    assert isinstance(resource.attributes, list)
    for attribute in resource.attributes:
        assert isinstance(attribute, pf.Parsed_Attribute)
        assert isinstance(
            attribute._Parsed_Attribute__value,
            pf.I_Parsed_Value,
        )
        if isinstance(attribute._Parsed_Attribute__value, pf.Parsed_Dict):
            for val in attribute.value:
                assert isinstance(val, pf.Parsed_Attribute)

        elif isinstance(attribute._Parsed_Attribute__value, pf.Parsed_List):
            for val in attribute.value:
                assert isinstance(val, pf.I_Parsed_Value)


def test_add_resource():
    file = pf.ParsedFile()

    pos = pf.Position(3, 7)
    resource = pf.ParsedResource(
        'test_type', 'test_name',
        attributes=None, position=pos,
    )

    file.resources.append(resource)

    assert resource in file.resources
