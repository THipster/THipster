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
    val = pf.Parsed_Litteral(3)
    pos = pf.Position(3, 7)

    attr = pf.Attribute('test_attr', value=val, position=pos)

    assert isinstance(attr, pf.Attribute)
    assert isinstance(attr._Attribute__value, pf.Parsed_Litteral)
    assert attr.value == 3


def test_create_str_attr():
    val = pf.Parsed_Litteral('test_value')
    pos = pf.Position(3, 7)

    attr = pf.Attribute('test_attr', value=val, position=pos)

    assert isinstance(attr, pf.Attribute)
    assert isinstance(attr._Attribute__value, pf.Parsed_Litteral)
    assert attr.value == 'test_value'


def test_create_list_str_attr():
    val = pf.Parsed_List(
        [pf.Parsed_Litteral('test_value_' + str(i)) for i in range(3)],
    )
    pos = pf.Position(3, 7)

    attr = pf.Attribute('test_attr', value=val, position=pos)

    assert isinstance(attr, pf.Attribute)
    assert isinstance(attr._Attribute__value, pf.Parsed_List)

    assert len(attr.value) == 3
    for val in attr.value:
        assert 'test_value' in val.value


def test_create_dict_str_attr():
    val = pf.Parsed_Dict(
        {pf.Parsed_Litteral('test_value_' + str(i)) for i in range(3)},
    )
    pos = pf.Position(3, 7)

    attr = pf.Attribute('test_attr', value=val, position=pos)

    assert isinstance(attr, pf.Attribute)
    assert isinstance(attr._Attribute__value, pf.Parsed_Dict)

    assert len(attr.value) == 3
    for val in attr.value:
        assert 'test_value' in val.value


def test_add_resource():
    file = pf.ParsedFile()

    pos = pf.Position(3, 7)
    resource = pf.ParsedResource(
        'test_type', 'test_name',
        attributes=None, position=pos,
    )

    file.resources.append(resource)

    assert resource in file.resources
