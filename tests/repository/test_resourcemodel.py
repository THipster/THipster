"""Tests for the ResourceModel class."""
import thipster.engine.resource_model as rm


def test_create_empty_resource():
    """Test creating a resource with no attributes or dependencies."""
    model = rm.ResourceModel(
        'test_type',
        attributes=None,
        dependencies=None,
        internal_objects=None,
        name_key='test_key',
        cdk_provider='test_provider',
        cdk_module='test_module',
        cdk_name='test_name',
    )

    assert isinstance(model, rm.ResourceModel)
    assert model.resource_type == 'test_type'
    assert model.attributes is None
    assert model.dependencies is None
    assert model.internal_objects is None


def test_create_resource_with_dependencies():
    """Test creating a resource with dependencies."""
    dependencies = [
        rm.ResourceModel(
            'dependency_'+str(i),
            attributes=None,
            dependencies=None,
            internal_objects=None,
            name_key='test_key',
            cdk_provider='test_provider',
            cdk_module='test_module',
            cdk_name='test_name_'+str(i),
        ) for i in range(3)
    ]

    model = rm.ResourceModel(
        'test_type',
        attributes=None,
        dependencies=dependencies,
        internal_objects=None,
        name_key='test_key',
        cdk_provider='test_provider',
        cdk_module='test_module',
        cdk_name='test_name',
    )

    assert isinstance(model, rm.ResourceModel)
    assert model.resource_type == 'test_type'
    assert model.attributes is None
    assert isinstance(model.dependencies, list)
    for dep in model.dependencies:
        assert isinstance(dep, rm.ResourceModel)
        assert 'dependency_' in dep.resource_type


def test_create_num_attr():
    """Test creating a resource with a numeric attribute."""
    val = rm.ModelLiteral(3)

    attr = rm.ModelAttribute(
        cdk_name='test_attr',
        default=val, optional=False,
    )

    assert isinstance(attr, rm.ModelAttribute)
    assert isinstance(attr._ModelAttribute__default, rm.ModelLiteral)
    assert attr.default == 3


def test_create_str_attr():
    """Test creating a string attribute."""
    val = rm.ModelLiteral('test_default')

    attr = rm.ModelAttribute(
        cdk_name='test_attr',
        default=val, optional=False,
    )

    assert isinstance(attr, rm.ModelAttribute)
    assert isinstance(attr._ModelAttribute__default, rm.ModelLiteral)
    assert attr.default == 'test_default'


def test_create_list_str_attr():
    """Test creating a list of strings attribute."""
    val = rm.ModelList(
        [rm.ModelLiteral('test_default_' + str(i)) for i in range(3)],
    )

    attr = rm.ModelAttribute(
        cdk_name='test_attr',
        default=val, optional=False,
    )

    assert isinstance(attr, rm.ModelAttribute)
    assert isinstance(attr._ModelAttribute__default, rm.ModelList)

    assert len(attr.default) == 3
    for val in attr.default:
        assert 'test_default' in val.value


def test_create_dict_str_attr():
    """Test creating a dict of strings attribute."""
    val = rm.ModelDict(
        {rm.ModelLiteral('test_default_' + str(i)) for i in range(3)},
    )

    attr = rm.ModelAttribute(
        cdk_name='test_attr',
        default=val, optional=False,
    )

    assert isinstance(attr, rm.ModelAttribute)
    assert isinstance(attr._ModelAttribute__default, rm.ModelDict)

    assert len(attr.default) == 3
    for val in attr.default:
        assert 'test_default' in val.value


def test_create_resource_with_attributes():
    """Test creating a resource with attributes."""
    attr = {
        'attr_num': rm.ModelAttribute(
            cdk_name='attr_num',
            default=rm.ModelLiteral(3),
            optional=False,
        ),
        'attr_str': rm.ModelAttribute(
            cdk_name='attr_str',
            default=rm.ModelLiteral('test'),
            optional=False,
        ),
        'attr_list': rm.ModelAttribute(
            cdk_name='attr_list',
            default=rm.ModelList([
                rm.ModelLiteral('test_list_1'),
                rm.ModelLiteral('test_list_2'),
                rm.ModelLiteral('test_list_3'),
            ]),
            optional=False,
        ),
        'attr_dict': rm.ModelAttribute(
            cdk_name='attr_dict',
            default=rm.ModelDict([
                rm.ModelAttribute(
                    'attr_dict_1',
                    default=rm.ModelLiteral('test'),
                    optional=False,
                ),
                rm.ModelAttribute(
                    'attr_dict_2',
                    default=rm.ModelLiteral('test'),
                    optional=False,
                ),
            ]),
            optional=False,
        ),
    }

    model = rm.ResourceModel(
        'test_type',
        attributes=attr,
        dependencies=None,
        internal_objects=None,
        name_key='test_key',
        cdk_provider='test_provider',
        cdk_module='test_provider',
        cdk_name='test_provider',
    )

    assert isinstance(model, rm.ResourceModel)
    assert model.resource_type == 'test_type'
    assert isinstance(model.attributes, dict)
    for _, attribute in model.attributes.items():
        assert isinstance(attribute, rm.ModelAttribute)
        assert isinstance(
            attribute._ModelAttribute__default, rm.ModelValue,
        )
        if isinstance(attribute._ModelAttribute__default, rm.ModelDict):
            for val in attribute.default:
                assert isinstance(val, rm.ModelAttribute)

        elif isinstance(attribute._ModelAttribute__default, rm.ModelList):
            for val in attribute.default:
                assert isinstance(val, rm.ModelValue)

    assert model.dependencies is None


def test_create_internal_object():
    """Test creating an internal object."""
    model = rm.ResourceModel(
        'test_type',
        attributes=None,
        dependencies=None,
        internal_objects=None,
        name_key=None,
        cdk_provider='test_provider',
        cdk_module='test_module',
        cdk_name='test_name',
    )

    assert isinstance(model, rm.ResourceModel)
    assert model.name_key is None
