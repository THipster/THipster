import engine.ResourceModel as rm


def test_create_empty_resource():
    model = rm.ResourceModel(
        'test_type',
        attributes=None,
        dependencies=None,
        cdk_provider='test_provider',
        cdk_module='test_module',
        cdk_name='test_name',
    )

    assert isinstance(model, rm.ResourceModel)
    assert model.type == 'test_type'
    assert model.attributes is None
    assert model.dependencies is None


def test_create_resource_with_dependencies():
    dependencies = [
        rm.ResourceModel(
            'dependency_'+str(i),
            attributes=None,
            dependencies=None,
            cdk_provider='test_provider',
            cdk_module='test_module',
            cdk_name='test_name_'+str(i),
        ) for i in range(3)
    ]

    model = rm.ResourceModel(
        'test_type',
        attributes=None,
        dependencies=dependencies,
        cdk_provider='test_provider',
        cdk_module='test_module',
        cdk_name='test_name',
    )

    assert isinstance(model, rm.ResourceModel)
    assert model.type == 'test_type'
    assert model.attributes is None
    assert isinstance(model.dependencies, list)
    for dep in model.dependencies:
        assert isinstance(dep, rm.ResourceModel)
        assert 'dependency_' in dep.type


def test_create_num_attr():
    val = rm.Model_Literal(3)

    attr = rm.Model_Attribute('test_attr', default=val, optional=False)

    assert isinstance(attr, rm.Model_Attribute)
    assert isinstance(attr._Model_Attribute__default, rm.Model_Literal)
    assert attr.default == 3


def test_create_str_attr():
    val = rm.Model_Literal('test_default')

    attr = rm.Model_Attribute('test_attr', default=val, optional=False)

    assert isinstance(attr, rm.Model_Attribute)
    assert isinstance(attr._Model_Attribute__default, rm.Model_Literal)
    assert attr.default == 'test_default'


def test_create_list_str_attr():
    val = rm.Model_List(
        [rm.Model_Literal('test_default_' + str(i)) for i in range(3)],
    )

    attr = rm.Model_Attribute('test_attr', default=val, optional=False)

    assert isinstance(attr, rm.Model_Attribute)
    assert isinstance(attr._Model_Attribute__default, rm.Model_List)

    assert len(attr.default) == 3
    for val in attr.default:
        assert 'test_default' in val.value


def test_create_dict_str_attr():
    val = rm.Model_Dict(
        {rm.Model_Literal('test_default_' + str(i)) for i in range(3)},
    )

    attr = rm.Model_Attribute('test_attr', default=val, optional=False)

    assert isinstance(attr, rm.Model_Attribute)
    assert isinstance(attr._Model_Attribute__default, rm.Model_Dict)

    assert len(attr.default) == 3
    for val in attr.default:
        assert 'test_default' in val.value


def test_create_resource_with_attributes():
    attr = [
        rm.Model_Attribute(
            'attr_num',
            default=rm.Model_Literal(3),
            optional=False,
        ),
        rm.Model_Attribute(
            'attr_str',
            default=rm.Model_Literal('test'),
            optional=False,
        ),
        rm.Model_Attribute(
            'attr_list',
            default=rm.Model_List([
                rm.Model_Literal('test_list_1'),
                rm.Model_Literal('test_list_2'),
                rm.Model_Literal('test_list_3'),
            ]),
            optional=False,
        ),
        rm.Model_Attribute(
            'attr_dict',
            default=rm.Model_Dict([
                rm.Model_Attribute(
                    'attr_dict_1',
                    default=rm.Model_Literal('test'),
                    optional=False,
                ),
                rm.Model_Attribute(
                    'attr_dict_2',
                    default=rm.Model_Literal('test'),
                    optional=False,
                ),
            ]),
            optional=False,
        ),
    ]

    model = rm.ResourceModel(
        'test_type',
        attributes=attr,
        dependencies=None,
        cdk_provider='test_provider',
        cdk_module='test_provider',
        cdk_name='test_provider',
    )

    assert isinstance(model, rm.ResourceModel)
    assert model.type == 'test_type'
    assert isinstance(model.attributes, list)
    for attribute in model.attributes:
        assert isinstance(attribute, rm.Model_Attribute)
        assert isinstance(
            attribute._Model_Attribute__default, rm.I_Model_Value,
        )
        if isinstance(attribute._Model_Attribute__default, rm.Model_Dict):
            for val in attribute.default:
                assert isinstance(val, rm.Model_Attribute)

        elif isinstance(attribute._Model_Attribute__default, rm.Model_List):
            for val in attribute.default:
                assert isinstance(val, rm.I_Model_Value)

    assert model.dependencies is None
