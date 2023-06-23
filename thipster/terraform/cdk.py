"""THipster's Terraform CDK module."""
import copy
import importlib
import os
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

from cdktf import App, TerraformStack
from constructs import Construct
from python_terraform import Terraform

import thipster.engine.parsed_file as pf
import thipster.engine.resource_model as rm
import thipster.terraform.exceptions as cdk_exceptions
from thipster.engine import AuthPort, TerraformPort
from thipster.helpers import create_logger


class ResourceCreationContext:
    """Context from which a resource is created."""

    def __init__(
        self,
        stack_self: TerraformStack,
        resource_name: str | None = None,
        resource_type: str | None = None,
        resource_class: type | None = None,
        parent_name: str | None = None,
        parent_type: str | None = None,
        parent_args: dict | None = {},
        arg_to_complete: str | None = None,
        no_modif: bool = True,
        no_dependencies: bool = False,
    ):
        """Context from which a resource is created.

        Parameters
        ----------
        stack_self : TerraformStack
            Stack in which the resource is created
        resource_name : str, optional
            Name of the resource, default None
        resource_type : str, optional
            Type of the resource, default None
        resource_class : type, optional
            Class of the resource (Python CDK), default None
        parent_name : str, optional
            Name of the parent resource, default None
        parent_type : str, optional
            Type of the parent resource, default None
        parent_args : dict, optional
            Arguments of the parent resource, default {}
        arg_to_complete : str, optional
            Name of the argument to complete, default None
        no_modif : bool, optional
            If the resource is created with default values, default True
        no_dependencies : bool, optional
            If the resource is created without dependencies, default False
        """
        self.stack_self = stack_self

        self.model: rm.ResourceModel = None
        self.dependencies = None
        self.__resource_type = None

        # Parent resource info
        self.parent_name = parent_name
        self.parent_type = parent_type
        self.parent_args = parent_args

        self.arg_to_complete = arg_to_complete
        self.no_modif: bool = no_modif
        self.no_dependencies: bool = no_dependencies

        # Resource info
        self.resource_name = resource_name
        self.resource_type = resource_type
        self.resource_class = resource_class
        self.resource_args = {}

    @classmethod
    def from_parent(cls, parent, **args):
        """Create context from a parent context.

        Parameters
        ----------
        ctx: ResourceCreationContext
            Context from which the resource is created
        """
        parent_name = parent.parent_name if parent.parent_name else parent.resource_name
        return ResourceCreationContext(
            parent.stack_self,
            resource_name=f'{parent_name}-{uuid.uuid4().hex[:8]}',
            parent_name=parent_name,
            parent_type=parent.resource_type,
            parent_args=parent.resource_args,
            **args,
        )

    def regenerate(self):
        """Regenerate resource name."""
        self.resource_name = f'{self.parent_name}-{uuid.uuid4().hex[:8]}'
        return self

    @property
    def resource_type(self):
        """Return resource type."""
        return self.__resource_type

    @resource_type.setter
    def resource_type(self, value):
        self.__resource_type = value

        if value is not None:
            self.model: rm.ResourceModel = CDK._models[self.resource_type]
            self.dependencies = copy.deepcopy(self.model.dependencies)
            if self.arg_to_complete in self.dependencies:
                del self.dependencies[self.arg_to_complete]


class CDK(TerraformPort):
    """Terraform code generation and usage.

    Works using the CDK for Terraform in python, and the python_terraform library.
    """

    _models = []
    _parent_resources_stack = []
    _resources_to_create: list[ResourceCreationContext] = []

    _inherited_attributes: list[pf.ParsedAttribute] = []
    _created_resources = {}
    _logger = create_logger(__name__)

    @classmethod
    def apply(cls, plan_file_path: str):
        """Apply generated Terraform plan.

        Parameters
        ----------
        plan_file_path : str
            Path to the plan file

        Returns
        -------
        str
            Terraform apply output
        """
        output = subprocess.run(
            ['terrraform', 'apply', plan_file_path],
            shell=True,
            capture_output=True,
            encoding='utf-8',
        )
        return output.stdout + output.stderr

    @classmethod
    def generate(
        cls, file: pf.ParsedFile, models: dict[str, rm.ResourceModel],
        _authenticator: AuthPort,
    ):
        """Generate Terraform file from given parsed file and models.

        Parameters
        ----------
        file : pf.ParsedFile
            ParsedFile object to transform
        models : dict[str, rm.ResourceModel]
            Associated models
        _auth : AuthPort
            Authenticator to use
        """
        cls._created_resources = {}
        cls._models = models
        cls._parent_resources_stack = []

        # Init CDK
        app = App()

        f_position = file.resources[0].position
        file_name = Path(f_position.filename).parts[-1] if f_position \
            else 'thipster_infrastructure'

        cls._logger.debug('Creating tf code for file %s', file_name)

        # Declare new stack in CDK

        class _ResourceStack(TerraformStack):
            def __init__(self, scope: Construct, ns: str):

                super().__init__(scope, ns)

                _authenticator.authenticate(self)

                for resource in file.resources:
                    ctx = ResourceCreationContext(self)
                    created_resource = _create_resource_from_resource(
                        ctx,
                        resource=resource,
                    )

                    cls._created_resources[f'{resource.resource_type}/{resource.name}']\
                        = created_resource

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
                Path(Path.cwd(), dirname, 'cdk.tf.json'),
                Path(Path.cwd(), 'thipster.tf.json'),
            )

        # Delete cdktf.out directory
            for content in os.listdir(Path(Path.cwd(), dirname)):
                if Path(f'{dirname}/{content}').is_dir():
                    shutil.rmtree(f'{dirname}/{content}')
                    continue

                Path(f'{dirname}/{content}').unlink()
            Path(dirname).rmdir()
        for content in os.listdir(Path(Path.cwd(), 'cdktf.out')):
            d = f'cdktf.out/{content}'
            Path(d).rmdir() if Path(d).is_dir() else Path(d).unlink()
        Path('cdktf.out').rmdir()

    @classmethod
    def init(cls):
        """Initilize terraform.

        Returns
        -------
        str
            Terraform init output
        """
        t = Terraform()
        _, stdout, stderr = t.init(upgrade=True)
        return stdout + stderr

    @classmethod
    def plan(cls, plan_file_path: str):
        """Get plan from generated terraform code.

        Parameters
        ----------
        plan_file_path : str
            Path and name of the plan file

        Returns
        -------
        str
            Terraform plan output
        """
        t = Terraform()
        _, stdout, stderr = t.plan(out=plan_file_path)
        return stdout + stderr

    @classmethod
    def _pip_install(cls, package: str):
        """Install a package if it wasn't already installed by thipster.

        Parameters
        ----------
        package : str
            Package to install
        """
        if package not in sys.modules:
            subprocess.check_call(
                [sys.executable, '-m', 'pip', 'install', '-qqq', package],
            )

    @classmethod
    def _import(cls, package_name: str, module_name: str, class_name: str) -> type:
        """Import a class from any package.

        Parameters
        ----------
        package_name : str
            Package that contains the class
        module_name : str
            Module that contains the class
        class_name : str
            Class to import

        Returns
        -------
        type :
            the imported class
        """
        module = importlib.import_module(f'{package_name}.{module_name}')
        return getattr(module, class_name)


def _create_default_resource(ctx: ResourceCreationContext):
    """Create a resource with all default values.

    Parameters
    ----------
    ctx: ResourceCreationContext
        Context from which the resource is created
    """
    # Checks for cyclic dependency
    if ctx.resource_type in CDK._parent_resources_stack:
        CDK._logger.error(
            '{ctx.resource_type} already present in parent Stack',
        )
        raise cdk_exceptions.CDKCyclicDependenciesError(
            CDK._parent_resources_stack,
        )

    CDK._parent_resources_stack.append(ctx.resource_type)

    attributes = copy.deepcopy(ctx.model.attributes)

    for a in CDK._inherited_attributes:
        if a.name in attributes:
            attributes[a.name].default = rm.ModelLiteral(a.value)

        else:
            attributes[a.name] = rm.ModelAttribute(
                cdk_name=a.name,
                default=rm.ModelLiteral(a.value),
            )

    # Checks that all attributes have a default value
    if ctx.no_modif and not all(
        x.optional or (x.default is not None) for x in attributes.values()
    ):
        missing_atributes = [
            k for k, v in attributes.items() if not v.optional and v.default is None
        ]

        raise cdk_exceptions.CDKMissingAttributeInDependencyError(
            ctx.resource_type,
            missing_atributes,
        )

    for attribute_name, attribute_value in attributes.items():
        _process_attribute(
            ctx, pf.ParsedAttribute(
                name=attribute_name,
                position=None,
                value=(
                    attribute_value.default
                    if isinstance(attribute_value.default, pf.ParsedLiteral)
                    else pf.ParsedLiteral(attribute_value.default)
                ),
            ),
        )

    # Create default defendencies if needed
    if not ctx.no_dependencies:
        _generate_default_dependencies(ctx)

    if ctx.model.name_key:
        ctx.resource_args[ctx.model.name_key] = ctx.resource_name

    # Import package and class
    CDK._pip_install(ctx.model.cdk_provider)
    ctx.resource_class = CDK._import(
        ctx.model.cdk_provider, ctx.model.cdk_module, ctx.model.cdk_name,
    )

    CDK._logger.debug(
        f'Created default {ctx.resource_class} named {ctx.resource_name}',
    )


def _create_resource(ctx: ResourceCreationContext, resource_args: object):
    """Create a resource with the given values.

    Parameters
    ----------
    ctx: ResourceCreationContext
        Context from which the resource is created
    resource_args : object
        Data source to create the resource

    Returns
    -------
    object :
        Created resource
    """
    if isinstance(resource_args, pf.ParsedResource):
        return _create_resource_from_resource(
            ctx, resource_args,
        )

    if isinstance(resource_args, list):
        return _create_resource_from_args(
            ctx, resource_args,
        )
    return None


def _create_resource_from_args(
    ctx: ResourceCreationContext, input_args: list[pf.ParsedAttribute] | None,
):
    """Create a resource from a list of ParsedAttributes.

    Parameters
    ----------
    ctx: ResourceCreationContext
        Context from which the resource is created
    input_args : list[ParsedAttribute]
        data source to create the resource

    Returns
    -------
    object :
        Created resource
    """
    ctx.no_modif = False
    ctx.no_dependencies = True

    # Create resource with default values
    _create_default_resource(ctx)
    ctx.no_modif = True
    ctx.no_dependencies = False

    # Process attributes
    def attributes(attribute_list: list[pf.ParsedAttribute]):
        for attribute in attribute_list:
            if attribute.name == ctx.model.name_key:
                ctx.resource_name = attribute.value
                ctx.resource_args[ctx.model.name_key] = attribute.value
            else:
                _process_attribute(ctx, attribute)

    attributes(input_args)
    attributes(CDK._inherited_attributes)

    CDK._inherited_attributes += input_args
    _generate_default_dependencies(ctx)
    CDK._inherited_attributes = CDK._inherited_attributes[:-len(input_args)]

    return _instantiate_class(ctx)


def _create_resource_from_resource(
        ctx: ResourceCreationContext, resource: pf.ParsedResource,
):
    """Create a resource from a list of ParsedAttributes.

    Parameters
    ----------
    ctx: ResourceCreationContext
        Context from which the resource is created
    resource : ParsedResource
        Data source to create the resource

    Returns
    -------
    object :
        Created resource
    """
    ctx.resource_name = resource.name
    ctx.resource_type = resource.resource_type

    return _create_resource_from_args(ctx, resource.attributes)


def _instantiate_class(ctx: ResourceCreationContext):
    """Instantiate a class.

    Parameters
    ----------
    ctx: ResourceCreationContext
        Context from which the resource is created

    Returns
    -------
    object :
        Created resource
    """
    CDK._parent_resources_stack.remove(ctx.resource_type)

    if not ctx.arg_to_complete:

        # check args
        if ctx.no_modif and not all(
            value.get('optional') or ctx.resource_args.get(name)
            for name, value in ctx.model.internal_objects.items()
        ):
            missing_internal_objects = [
                name for name, value in ctx.model.internal_objects.items()
                if not value.get('optional') and not ctx.resource_args.get(name)
            ]

            raise cdk_exceptions.CDKMissingAttributeInDependencyError(
                ctx.resource_type,
                missing_internal_objects,
            )

        if not ctx.model.name_key:
            class_ = ctx.resource_class(**ctx.resource_args)
        else:
            class_ = ctx.resource_class(
                ctx.stack_self, ctx.resource_name, **ctx.resource_args,
            )

        while len(CDK._resources_to_create) != 0:
            to_create = CDK._resources_to_create.pop()
            to_create.resource_args[to_create.arg_to_complete] = class_.id

            created_resource = to_create.resource_class(
                to_create.stack_self, to_create.resource_name,
                **to_create.resource_args,
            )

            CDK._created_resources[f'{to_create.resource_type}/{to_create.resource_name}']\
                = created_resource

        CDK._logger.debug(
            f'Created {ctx.resource_class} named {ctx.resource_name}',
        )
        return class_

    CDK._resources_to_create.append(ctx)
    return True


def _process_attribute(ctx: ResourceCreationContext, attribute: pf.ParsedAttribute):
    """Process an attribute.

    Parameters
    ----------
    ctx: ResourceCreationContext
        Context from which the resource is created
    attribute : ParsedAttribute
        Attribute to process
    """
    if not ctx.no_dependencies and attribute.name in ctx.dependencies:
        _check_explicit_dependency(
            ctx, attribute.name, attribute.value,
        )
        del ctx.dependencies[attribute.name]
        return

    # Checks if attribute is an internal object
    if attribute.name in ctx.model.internal_objects:
        _create_internal_object(
            ctx,
            attribute.name,
            attribute.value,
        )
        return

    # Checks if attribute is expected as an attibute
    if attribute.name not in ctx.model.attributes:
        return

    # Processes list attribute
    attribute_value = attribute.value
    if ctx.model.attributes[attribute.name].is_list:
        if isinstance(attribute.value, list):
            attribute_value = [i.value for i in attribute.value]
        else:
            attribute_value = [attribute.value]

    # Sets attribute value
    if attribute_value is not None:
        ctx.resource_args[ctx.model.attributes[attribute.name].cdk_name]\
            = attribute_value


def _generate_default_dependencies(ctx: ResourceCreationContext):
    """Generate default dependencies and internal objects in a resource.

    Parameters
    ----------
    ctx: ResourceCreationContext
        Context from which the resource is created
    """
    # Create missing dependencies
    for dependency_name, dependency_object in ctx.dependencies.items():
        dep_ctx = ResourceCreationContext.from_parent(
            ctx,
            resource_type=dependency_object['resource'],
        )
        ctx.resource_args[dependency_name] = _create_dependency(dep_ctx)

    # Create default internal objects if needed
    for internal_object_name, internal_object in ctx.model.internal_objects.items():
        if internal_object_name not in ctx.resource_args:
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
                    ctx,
                    internal_object_name,
                    default_args,
                )


def _create_internal_object(
    ctx: ResourceCreationContext,
    internal_object_name: str,
    internal_object_args,
):
    """Create an internal object in a resource.

    Parameters
    ----------
    ctx: ResourceCreationContext
        Context from which the resource is created
    internal_object_name : str
        Name of the internal object
    internal_object_args : object
        Data source to create the internal object
    """
    internal_object_model = ctx.model.internal_objects[internal_object_name]

    internal_object_base_ctx = ResourceCreationContext.from_parent(
        ctx,
        resource_type=internal_object_model['resource'],
        arg_to_complete=internal_object_model.get('arg_to_complete'),
    )

    internal_object_type = internal_object_model['var_type'] \
        if 'var_type' in internal_object_model else 'Unknown'

    if internal_object_type.startswith('list') or internal_object_model['is_list']:
        if internal_object_name not in ctx.resource_args\
                and not internal_object_base_ctx.arg_to_complete:
            ctx.resource_args[internal_object_name] = []

        if isinstance(internal_object_args, list)\
                and not isinstance(internal_object_args[0], pf.ParsedAttribute):
            for internal_object in internal_object_args:
                internal_object_ctx = copy.deepcopy(internal_object_base_ctx)
                internal_object_ctx.regenerate()

                if isinstance(internal_object, pf.ParsedDict):
                    res = _create_resource(
                        internal_object_ctx,
                        internal_object.value,
                    )
                    if not internal_object_base_ctx.arg_to_complete:
                        ctx.resource_args[internal_object_name] += [res]

                elif isinstance(internal_object, pf.ParsedLiteral):
                    _check_explicit_dependency(
                        internal_object_ctx,
                        internal_object_name,
                        internal_object.value,
                    )

            return True

        res = _create_resource(
            internal_object_base_ctx,
            internal_object_args,
        )
        if not internal_object_base_ctx.arg_to_complete:
            ctx.resource_args[internal_object_name] += [res]
        return True

    res = _create_resource(
        internal_object_base_ctx,
        internal_object_args,
    )
    if not internal_object_base_ctx.arg_to_complete:
        ctx.resource_args[internal_object_name] = res

    return True


def _create_dependency(
        ctx: ResourceCreationContext,
        dependency_attributes: list[pf.ParsedAttribute] = None,
):
    """Create a dependency in a resource.

    Parameters
    ----------
    ctx: ResourceCreationContext
        Context from which the resource is created
    dependency_attributes: list[pf.ParsedAttribute]
        list of attributes to pass to the dependency creation. Defaults to None
    """
    if dependency_attributes:
        ctx.no_modif = False

    _create_default_resource(ctx)

    ctx.no_modif = True

    # Process attributes
    def attributes(attribute_list: list[pf.ParsedAttribute]):
        for attribute in attribute_list:
            if attribute.name == ctx.model.name_key:
                ctx.resource_args[ctx.model.name_key] = attribute.value
            else:
                _process_attribute(ctx, attribute)

    if dependency_attributes:
        attributes(dependency_attributes)
    attributes(CDK._inherited_attributes)

    dependency = _instantiate_class(ctx)
    return dependency.id


def _check_explicit_dependency(
    ctx: ResourceCreationContext, attribute_name: str, attribute_value: str | dict,
):
    """Check if a dependency attribute was explicited before.

    If it wasn't : create a default dependency.

    Parameters
    ----------
    ctx: ResourceCreationContext
        Context from which the resource is created
    attribute_name: str
        Name of the attribute to check
    attribute_value: str | dict
        Value of the attribute to check
    """
    resource_attribute = 'id'
    explicit_value = attribute_value
    if isinstance(attribute_value, pf.ParsedLiteral):
        explicit_value = attribute_value.value

    if isinstance(explicit_value, str):
        split = explicit_value.split('.', maxsplit=1)
        explicit_value = split[0]
        resource_attribute = split[1] if len(split) > 1 else 'id'

    dependency_type = ctx.dependencies[attribute_name]['resource']
    created_name = f'{dependency_type}/{explicit_value}'

    # Checks if attribute is an explicit dependency
    if created_name not in CDK._created_resources.keys():

        if isinstance(explicit_value, str):
            raise cdk_exceptions.CDKDependencyNotDeclaredError(
                attribute_name, attribute_value,
            )

        dep_ctx = ResourceCreationContext.from_parent(
            ctx,
            resource_type=dependency_type,
        )

        # Creates explicit dependency
        if (
            isinstance(attribute_value, list)
            and isinstance(attribute_value[0], pf.ParsedDict)
        ):
            ctx.resource_args[attribute_name] = []
            for dict_value in attribute_value:
                dep_ctx.regenerate()
                ctx.resource_args[attribute_name].append(
                    _create_dependency(
                        dep_ctx, dict_value.value,
                    ),
                )
            return True

        ctx.resource_args[attribute_name] = _create_dependency(
            dep_ctx, attribute_value,
        )
        return True

    resource = getattr(
        CDK._created_resources[created_name], resource_attribute,
    )
    if attribute_name in ctx.resource_args:
        ctx.resource_args[attribute_name] += [resource]

    ctx.resource_args[attribute_name] = resource
    return True
