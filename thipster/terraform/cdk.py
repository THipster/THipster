import copy
import importlib
import os
import shutil
import subprocess
import sys
import uuid

from cdktf import App, TerraformStack
from constructs import Construct
from python_terraform import Terraform

import thipster.engine.parsed_file as pf
import thipster.engine.resource_model as rm
import thipster.terraform.exceptions as cdk_exceptions
from thipster.engine import AuthPort, TerraformPort
from thipster.helpers import create_logger


class ResourceCreationContext():
    def __init__(self) -> None:
        pass


class CDK(TerraformPort):
    _models = []
    _parent_resources_stack = []
    _resources_to_create = []

    _inherited_attributes: list[pf.ParsedAttribute] = []
    _created_resources = {}
    _logger = create_logger(__name__)

    @classmethod
    def apply(cls, plan_file_path: str | None = None):
        """Applies generated Terraform plan

        Parameters
        ----------
        plan_file_path : str, optional
            path to the plan file, default None

        Returns
        -------
        str
            Terraform apply output
        """
        t = Terraform()
        _, stdout, stderr = t.apply(plan_file_path)
        return stdout + stderr

    @classmethod
    def generate(
        cls, file: pf.ParsedFile, models: dict[str, rm.ResourceModel],
        _authenticator: AuthPort,
    ):
        """Generate Terraform file from given parsed file and models

        Parameters
        ----------
        file : pf.ParsedFile
            parsedFile object to transform
        models : dict[str, rm.ResourceModel]
            associated models
        _auth : AuthPort
            authenticator to use
        """
        cls._created_resources = {}
        cls._models = models
        cls._parent_resources_stack = []

        # Init CDK
        app = App()

        f_position = file.resources[0].position
        file_name = f_position.filename if f_position else 'thipster_infrastructure'

        cls._logger.debug('Creating tf code for file %s', file_name)

        # Declare new stack in CDK
        class _ResourceStack(TerraformStack):
            def __init__(self, scope: Construct, ns: str):
                super().__init__(scope, ns)

                _authenticator.authenticate(self)

                for resource in file.resources:
                    created_resource = _create_resource_from_resource(
                        self,
                        resource=resource,
                    )

                    cls._created_resources[f'{resource.resource_type}/{resource.name}']\
                        = created_resource.id

        _ResourceStack(app, file_name)

        # Synth files
        app.synth()

        output_directories = [
            f'{app.outdir}/stacks/{c.node.path}' for c in app.node.children
        ]

        CDK._logger.info(
            'Created %s terraform file(s)',
            len(output_directories),
        )

        # Move files
        for dirname in output_directories:
            shutil.move(
                os.path.join(os.getcwd(), dirname, 'cdk.tf.json'),
                os.path.join(os.getcwd(), 'thipster.tf.json'),
            )

        # Delete cdktf.out directory
            for content in os.listdir(os.path.join(os.getcwd(), dirname)):
                os.remove(f'{dirname}/{content}')
            os.rmdir(dirname)
        for content in os.listdir(os.path.join(os.getcwd(), 'cdktf.out')):
            d = f'cdktf.out/{content}'
            os.rmdir(d) if os.path.isdir(d) else os.remove(d)
        os.rmdir('cdktf.out')

    @classmethod
    def init(cls):
        """Initilize terraform

        Returns
        -------
        str
            Terraform init output
        """
        t = Terraform()
        _, stdout, stderr = t.init()
        return stdout + stderr

    @classmethod
    def plan(cls):
        """Get plan from generated terraform code

        Returns
        -------
        str
            Terraform plan output
        """
        t = Terraform()
        _, stdout, stderr = t.plan(out='thipster.tfplan')
        return stdout + stderr

    @classmethod
    def _pip_install(cls, package: str):
        """Install a package if it wasn't already installed by thipster

        Parameters
        ----------
        package : str
            package to install
        """
        if package not in sys.modules:
            subprocess.check_call(
                [sys.executable, '-m', 'pip', 'install', '-qqq', package],
            )

    @classmethod
    def _import(cls, package_name: str, module_name: str, class_name: str) -> type:
        """Import a class from any package

        Parameters
        ----------
        package_name : str
            package that contains the class
        module_name : str
            module that contains the class
        class_name : str
            class to import

        Returns
        -------
        type :
            the imported class
        """
        module = importlib.import_module(f'{package_name}.{module_name}')
        class_ = getattr(module, class_name)

        return class_


def _create_default_resource(
    resource_self, resource_type: str, parent_name: str | None = None,
    no_modif: bool = True, no_dependencies: bool = False, arg_to_complete: str = None,
):
    """Create a resource with all default values

    Parameters
    ----------
    self : _ResourceStack
        Terraform CDK stack that contains the resource
    resource_type : str
        type of the resource to create
    parent_name : str
        name of the parent resource
    parent_name : str, optional
        name of its parent, default None
    no_modif : bool, optional
        if True, raise errors if resource can't be created with default values, \
default False
    no_dependencies : bool, optional
        if True, create the default dependencies, default False
    arg_to_complete: str
        name of the argument that will get a value after parent resource creation

    Returns
    -------
    (type, str, dict[str, object]) :
        all the information needed to instantiate the class with default values
    """
    # Checks for cyclic dependency
    if resource_type in CDK._parent_resources_stack:
        CDK._logger.error(
            '%s already present in parent Stack', resource_type,
        )
        raise cdk_exceptions.CDKCyclicDependenciesError(
            CDK._parent_resources_stack,
        )

    CDK._parent_resources_stack.append(resource_type)

    model = CDK._models[resource_type]

    attributes = copy.deepcopy(model.attributes)

    for a in CDK._inherited_attributes:
        if a.name in attributes.keys():
            attributes[a.name].default = rm.ModelLiteral(a.value)

        else:
            attributes[a.name] = rm.ModelAttribute(
                cdk_name=a.name,
                default=rm.ModelLiteral(a.value),
            )

    # Checks that all attributes have a default value
    if (
        no_modif
        and not all(map(lambda x: x.default is not None, attributes.values()))
    ):
        raise cdk_exceptions.CDKMissingAttributeInDependencyError(
            resource_type,
        )

    # Import package and class
    CDK._pip_install(model.cdk_provider)
    resource_class = CDK._import(
        model.cdk_provider, model.cdk_module, model.cdk_name,
    )

    # Process name + default values
    dependencies = _get_dependency_list(model, arg_to_complete)
    resource_args = {}

    name = f'{parent_name}-{uuid.uuid4()}'
    if model.name_key:
        resource_args[model.name_key] = name

    for attribute_name, attribute_value in attributes.items():

        if not no_dependencies and attribute_name in dependencies:

            _check_explicit_dependency(
                resource_self, resource_args, dependencies[attribute_name]['resource'],
                attribute_value.default, attribute_name,
            )

            del dependencies[attribute_name]

        if attribute_name in model.attributes:
            resource_args[attribute_value.cdk_name] = attribute_value.default

    # Create default defendencies if needed
    if not no_dependencies:
        _generate_default_dependencies(
            resource_self, dependencies, model, resource_args, parent_name,
        )

    CDK._logger.debug('Created default %s named %s', resource_class, name)

    return (resource_class, name, resource_args)


def _create_resource(
        resource_self, resource_args: object, parent_name: str,
        resource_type: str = None, arg_to_complete: bool = True,
):
    """Create a resource with the given values

    Parameters
    ----------
    self : _ResourceStack
        Terraform CDK stack that contains the resource
    resource_args : object
        data source to create the resource
    parent_name : str
        name of the parent resource
    resource_type : str, optional
        type of the resource to create, default None
    arg_to_complete: str
        name of the argument that will get a value after parent resource creation

    Returns
    -------
    object :
        the created resource
    """

    if isinstance(resource_args, pf.ParsedResource):
        return _create_resource_from_resource(
            resource_self, resource_args, parent_name, arg_to_complete,
        )

    return _create_resource_from_args(
        resource_self, resource_type, parent_name, resource_args, arg_to_complete,
    )


def _create_resource_from_args(
    resource_self, resource_type: str, parent_name: str,
    input_args: list[pf.ParsedAttribute] | None, arg_to_complete: str = None,
):
    """Create a resource from a list of ParsedAttributes

    Parameters
    ----------
    self : _ResourceStack
        Terraform CDK stack that contains the resource
    resource_type : str, optional
        type of the resource to create, default None
    parent_name : str
        name of the parent resource
    input_args : list[ParsedAttribute]
        data source to create the resource
    arg_to_complete: str
        name of the argument that will get a value after parent resource creation

    Returns
    -------
    object :
        the created resource
    """
    resource_class, resource_name, resource_args = _create_default_resource(
        resource_self,
        resource_type,
        parent_name=parent_name,
        no_modif=False,
        no_dependencies=True,
        arg_to_complete=arg_to_complete,
    )
    model = CDK._models[resource_type]

    # Process attributes
    dependencies = _get_dependency_list(model, arg_to_complete)

    def attributes(attribute_list):
        for attribute in attribute_list:
            if attribute.name == model.name_key:
                resource_args[model.name_key] = attribute.name
            else:
                _process_attribute(
                    resource_self, model,
                    attribute, resource_args, dependencies, parent_name,
                )

    attributes(input_args)
    attributes(CDK._inherited_attributes)

    CDK._inherited_attributes += input_args
    _generate_default_dependencies(
        resource_self, dependencies, model, resource_args, resource_name,
    )
    CDK._inherited_attributes = CDK._inherited_attributes[
        :-len(
            input_args,
        )
    ]

    # Create resource
    CDK._parent_resources_stack.remove(resource_type)

    CDK._logger.debug(
        'Created default %s named %s',
        resource_class, resource_name,
    )

    if not arg_to_complete:
        if not model.name_key:
            class_ = resource_class(**resource_args)
        else:
            class_ = resource_class(
                resource_self, resource_name, **resource_args,
            )

        while len(CDK._resources_to_create) != 0:
            to_create_class, to_create_name, to_create_args, to_create_complete = \
                CDK._resources_to_create.pop()
            to_create_args[to_create_complete] = class_.id

            to_create_class(
                resource_self, to_create_name, **to_create_args,
            )
        return class_

    CDK._resources_to_create.append(
        (resource_class, resource_name, resource_args, arg_to_complete),
    )


def _create_resource_from_resource(
        resource_self, resource: pf.ParsedResource,
        parent_name: str = None, arg_to_complete: str = None,
):
    """Create a resource from a list of ParsedAttributes

    Parameters
    ----------
    resource_self : _ResourceStack
        Terraform CDK stack that contains the resource
    resource : ParsedResource
        data source to create the resource
    parent_name : str
        name of the parent resource
    arg_to_complete: str
        name of the argument that will get a value after parent resource creation

    Returns
    -------
    object :
        the created resource
    """

    # Create resource with default values
    resource_class, _, resource_args = _create_default_resource(
        resource_self,
        resource.resource_type,
        parent_name=parent_name,
        no_modif=False,
        no_dependencies=True,
        arg_to_complete=arg_to_complete,
    )
    model = CDK._models[resource.resource_type]

    if model.name_key:
        resource_args[model.name_key] = resource.name

    # Process attributes
    dependencies = _get_dependency_list(model, arg_to_complete)

    def attributes(attribute_list):
        for attribute in attribute_list:
            _process_attribute(
                resource_self,
                model,
                attribute,
                resource_args,
                dependencies,
                resource.name,
            )

    attributes(resource.attributes)
    attributes(CDK._inherited_attributes)

    CDK._inherited_attributes += resource.attributes
    _generate_default_dependencies(
        resource_self, dependencies, model, resource_args, resource.name,
    )
    CDK._inherited_attributes = CDK._inherited_attributes[
        :-len(
            resource.attributes,
        )
    ]

    # Create resource
    CDK._parent_resources_stack.remove(resource.resource_type)

    CDK._logger.debug(
        'Created resource %s named %s',
        resource_class, resource.name,
    )

    if not arg_to_complete:
        if not model.name_key:
            class_ = resource_class(**resource_args)
        else:
            class_ = resource_class(
                resource_self, resource.name, **resource_args,
            )

        while len(CDK._resources_to_create) != 0:
            to_create_class, to_create_name, to_create_args, to_create_complete = \
                CDK._resources_to_create.pop()
            to_create_args[to_create_complete] = class_.id

            to_create_class(
                resource_self, to_create_name, **to_create_args,
            )
        return class_

    CDK._resources_to_create.append(
        (resource_class, resource.name, resource_args, arg_to_complete),
    )
    return True


def _process_attribute(
    resource_self,
    model: rm.ResourceModel,
    attribute: pf.ParsedAttribute,
    resource_args: dict[str, object],
    dependencies: dict[str, dict[str, object]] | None,
    parent_name: str,
):
    """Process an attribute

    Parameters
    ----------
    resource_self : _ResourceStack
        Terraform CDK stack that contains the resource
    model : ResourceModel
        model of the resource that is being created
    attribute : ParsedAttribute
        attribute to handle
    resource_args : object
        data source needed to create the resource
    dependencies : dict[str, dict[str, object]]
        dependencies needed to create the resource
    parent_name : str
        name of the parent resource
    """
    if attribute.name in dependencies:
        _check_explicit_dependency(
            resource_self, resource_args, dependencies[attribute.name]['resource'],
            attribute.value, attribute.name,
        )
        del dependencies[attribute.name]
        return

    # Checks if attribute is an internal object
    if attribute.name in model.internal_objects:
        _create_internal_object(
            resource_self,
            attribute.name,
            model.internal_objects[attribute.name],
            attribute.value,
            resource_args,
            parent_name,
        )
        return

    # Checks if attribute is expected as an attibute
    if attribute.name not in model.attributes:
        return

    # Processes list attribute
    attribute_value = attribute.value
    if model.attributes[attribute.name].is_list:
        if type(attribute.value) is list:
            attribute_value = [i.value for i in attribute.value]
        else:
            attribute_value = [attribute.value]

    # Sets attribute value
    resource_args[model.attributes[attribute.name].cdk_name] = attribute_value


def _generate_default_dependencies(
        resource_self,
        dependencies,
        model: rm.ResourceModel,
        resource_args,
        resource_name,
):
    """Generate default dependencies and internal objects in a resource

    Parameters
    ----------
    self : _ResourceStack
        Terraform CDK stack that contains the resource
    dependencies :
        list of dependencies to create
    model : str
        model of the resource that is being created
    resource_args : _type_
        data source needed to create the resource
    resource_name : dict
        name of the resource that is being created
    """
    # Create missing dependencies
    for dependency_name, dependency_object in dependencies.items():
        _create_dependency(
            resource_self, dependency_name,
            dependency_object, resource_args, resource_name,
        )

    # Create default internal objects if needed
    for internal_object_name, internal_object in model.internal_objects.items():
        if internal_object_name not in resource_args:
            for default_args_json in internal_object['defaults']:

                # Transform in list of ParsedAttributes
                default_args = []
                for arg_key, arg_value in default_args_json.items():
                    default_args.append(
                        pf.ParsedAttribute(
                            arg_key, None, pf.ParsedLiteral(arg_value),
                        ),
                    )

                _create_internal_object(
                    resource_self,
                    internal_object_name,
                    model.internal_objects[internal_object_name],
                    default_args,
                    resource_args,
                    resource_name,
                )


def _create_internal_object(
    resource_self,
    name: str,
    internal_object_model: dict,
    internal_object_args,
    resource_args: dict,
    parent_name: str,
):
    """Create an internal object in a resource

    Parameters
    ----------
    resource_self : _ResourceStack
        Terraform CDK stack that contains the resource
    name : str
        name of the internal object
    internal_object_model : ResourceModel
        model of the internal object
    internal_object_args : object
        data source to create the internal object
    resource_args : dict
        data source needed to create the resource
    parent_name : str
        name of the parent resource
    """
    internal_object_type = internal_object_model['var_type'] \
        if 'var_type' in internal_object_model else 'Unknown'

    arg_to_complete = internal_object_model.get('arg_to_complete')

    if internal_object_type.startswith('list'):
        if name not in resource_args and not arg_to_complete:
            resource_args[name] = []

        if isinstance(internal_object_args, list) \
                and isinstance(internal_object_args[0], pf.ParsedDict):

            for internal_object in internal_object_args:
                res = _create_resource(
                    resource_self,
                    internal_object.value,
                    parent_name,
                    internal_object_model['resource'],
                    arg_to_complete=arg_to_complete,
                )
                if not arg_to_complete:
                    resource_args[name] += [res]
            return True

        res = _create_resource(
            resource_self,
            internal_object_args,
            parent_name,
            internal_object_model['resource'],
            arg_to_complete=arg_to_complete,
        )
        if not arg_to_complete:
            resource_args[name] += [res]
        return True

    res = _create_resource(
        resource_self,
        internal_object_args,
        parent_name,
        internal_object_model['resource'],
        arg_to_complete=arg_to_complete,
    )
    if not arg_to_complete:
        resource_args[name] = res

    return True


def _get_dependency_list(model, arg_to_complete):
    dependencies = copy.deepcopy(model.dependencies)
    if arg_to_complete in dependencies.keys():
        del dependencies[arg_to_complete]
    return dependencies


def _create_dependency(resource_self, dep_name, dep_value, resource_args, parent_name):
    """Create an internal object in a resource

    Parameters
    ----------
    self : _ResourceStack
        Terraform CDK stack that contains the resource
    dep_name : str
        name of the dependency
    dep_value : ResourceModel
        model of the dependency
    resource_args : dict
        data source needed to create the resource
    parent_name : str
        name of its parent
    """
    class_, class_name, class_attributes = _create_default_resource(
        resource_self, dep_value['resource'], parent_name,
    )

    id = class_(resource_self, class_name, **class_attributes).id
    if dep_name:
        resource_args[dep_name] = id

    CDK._parent_resources_stack.remove(dep_value['resource'])


def _check_explicit_dependency(
    resource_self, resource_args, dependency_type, dependency_value, attribute_name,
):
    created_name = f'{dependency_type}/'\
        f'{dependency_value}'

    # Checks if attribute is an explicit dependency
    if created_name not in CDK._created_resources.keys():

        if isinstance(dependency_value, str):
            raise cdk_exceptions.CDKDependencyNotDeclaredError(
                attribute_name, dependency_value,
            )

        # Creates explicit dependency
        _create_dependency(
            resource_self, attribute_name, dependency_value,
            resource_args, attribute_name,
        )

    resource_args[attribute_name] = CDK._created_resources[created_name]
