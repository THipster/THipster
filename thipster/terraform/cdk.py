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
from thipster.engine import I_Auth, I_Terraform
from thipster.helpers import createLogger as Logger


class CDK(I_Terraform):
    _models = []
    _parent_resources_stack = []
    _imported_packages = []

    _created_resources = {}
    _logger = Logger(__name__)

    def apply(self):
        """Apply generated terraform code

        Raises
        ------
        NotImplementedError
            If method is not implemented in inheriting classes

        """
        t = Terraform()
        _, stdout, stderr = t.apply()
        return stdout + stderr

    def generate(
        self, file: pf.ParsedFile, models: dict[str, rm.ResourceModel],
        _auth: I_Auth,
    ):
        CDK._created_resources = {}
        CDK._models = models
        CDK._parent_resources_stack = []
        # Init CDK
        app = App()

        f_position = file.resources[0].position
        file_name = f_position.fileName if f_position else 'thipster_infrastructure'

        CDK._logger.debug('Creating tf code for file %s', file_name)

        # Declare new stack in CDK
        class _ResourceStack(TerraformStack):
            def __init__(self, scope: Construct, ns: str):
                super().__init__(scope, ns)

                _auth.authenticate(self)

                for resource in file.resources:
                    res = CDK._create_resource_from_resource(
                        self,
                        resource=resource,
                    )

                    CDK._created_resources[f'{resource.type}/{resource.name}'] = res.id

        _ResourceStack(app, file_name)

        # Synth files
        app.synth()

        self.__dirs = [
            f'{app.outdir}/stacks/{c.node.path}' for c in app.node.children
        ]

        CDK._logger.info('Created %s terraform file(s)', len(self.__dirs))

        # Move files
        for dirname in self.__dirs:
            shutil.move(
                os.path.join(os.getcwd(), dirname, "cdk.tf.json"),
                os.path.join(os.getcwd(), "thipster.tf.json"),
            )

        # Delete cdktf.out directory
            for content in os.listdir(os.path.join(os.getcwd(), dirname)):
                os.remove(f'{dirname}/{content}')
            os.rmdir(dirname)
        for content in os.listdir(os.path.join(os.getcwd(), 'cdktf.out')):
            d = f'cdktf.out/{content}'
            os.rmdir(d) if os.path.isdir(d) else os.remove(d)
        os.rmdir('cdktf.out')

    def init(self):
        """Get plan from generated terraform code

        Raises
        ------
        NotImplementedError
            If method is not implemented in inheriting classes

        """
        t = Terraform()
        _, stdout, stderr = t.init()
        return stdout + stderr

    def plan(self):
        """Get plan from generated terraform code

        Raises
        ------
        NotImplementedError
            If method is not implemented in inheriting classes

        """
        t = Terraform()
        _, stdout, stderr = t.plan(out="thipster.tfplan")
        return stdout + stderr

    def _pip_install(package: str):
        if package not in CDK._imported_packages:
            subprocess.check_call(
                [sys.executable, '-m', 'pip', 'install', '-qqq', package],
            )
            CDK._imported_packages.append(package)

    def _import(package_name: str, module_name: str, class_name: str) -> type:

        module = importlib.import_module(f'{package_name}.{module_name}')
        class_ = getattr(module, class_name)

        return class_

    def _create_default_resource(
        self, resource_type: str, parent_name: str | None = None,
        no_modif: bool = True, no_dependencies: bool = False,
    ):
        # Checks for cyclic dependency
        if resource_type in CDK._parent_resources_stack:
            CDK._logger.error(
                '%s already present in parent Stack', resource_type,
            )
            raise cdk_exceptions.CDKCyclicDependencies(
                CDK._parent_resources_stack,
            )

        CDK._parent_resources_stack.append(resource_type)

        model = CDK._models[resource_type]

        # Checks that all attributes are optional
        if no_modif and not all(map(lambda x: x.optional, model.attributes.values())):
            raise cdk_exceptions.CDKMissingAttributeInDependency(resource_type)

        # Import package and class
        CDK._pip_install(model.cdk_provider)
        resource_class = CDK._import(
            model.cdk_provider, model.cdk_module, model.cdk_name,
        )

        # Process name + default values
        dependencies = copy.deepcopy(model.dependencies)
        resource_args = {}

        name = f"{parent_name}-{uuid.uuid4()}"
        if model.name_key:
            resource_args[model.name_key] = name

        for _, v in model.attributes.items():
            resource_args[v.cdk_name] = v.default

        # Create default defendencies if needed
        if not no_dependencies:
            CDK._generate_default_dependencies(
                self, dependencies,
                model, resource_args, name,
            )

        CDK._logger.debug('Created default %s named %s', resource_class, name)

        return (resource_class, name, resource_args)

    def _create_resource(self, resource_args: object, resource_type: str = None):
        if isinstance(resource_args, dict):
            return CDK._create_resource_from_dict(self, resource_type, resource_args)

        if isinstance(resource_args, pf.ParsedResource):
            return CDK._create_resource_from_resource(self, resource_args)

        return CDK._create_resource_from_args(self, resource_type, resource_args)

    def _create_resource_from_args(
        self, resource_type: str, input_args: list[pf.ParsedAttribute] | None,
    ):

        resource_class, resource_name, resource_args = CDK._create_default_resource(
            self,
            resource_type,
            no_modif=False,
            no_dependencies=True,
        )
        model = CDK._models[resource_type]

        # Process attributes
        dependencies = copy.deepcopy(model.dependencies)
        for attribute in input_args:
            if attribute.name and model.name_key:
                resource_args[model.name_key] = attribute.name

            resource_args, dependencies = CDK._process_attribute(
                self, model, attribute, resource_args, dependencies,
            )

        CDK._generate_default_dependencies(
            self, dependencies, model, resource_args, resource_name,
        )

        # Create resource
        CDK._parent_resources_stack.remove(resource_type)

        CDK._logger.debug(
            'Created default %s named %s',
            resource_class, resource_name,
        )

        if not model.name_key:
            return resource_class(**resource_args)
        return resource_class(self, resource_name, **resource_args)

    def _create_resource_from_dict(
        self, resource_type: str, input_args: dict | None,
    ):
        resource_class, resource_name, resource_args = CDK._create_default_resource(
            self,
            resource_type,
            no_modif=False,
            no_dependencies=True,
        )
        model = CDK._models[resource_type]

        # Process attributes
        dependencies = copy.deepcopy(model.dependencies)
        for name, value in input_args.items():
            if name and model.name_key:
                resource_args[model.name_key] = name

            resource_args, dependencies = CDK._process_attribute(
                self, model,
                pf.ParsedAttribute(
                    name, None, pf.ParsedLiteral(value),
                ),
                resource_args, dependencies,
            )

        CDK._generate_default_dependencies(
            self, dependencies, model, resource_args, resource_name,
        )

        # Create resource
        CDK._parent_resources_stack.remove(resource_type)

        CDK._logger.debug(
            'Created default %s named %s',
            resource_class, resource_name,
        )

        if not model.name_key:
            return resource_class(**resource_args)
        return resource_class(self, resource_name, **resource_args)

    def _create_resource_from_resource(self, resource: pf.ParsedResource):
        # Create resource with default values
        resource_class, _, resource_args = CDK._create_default_resource(
            self,
            resource.type,
            no_modif=False,
            no_dependencies=True,
        )
        model = CDK._models[resource.type]

        if model.name_key:
            resource_args[model.name_key] = resource.name

        # Process attributes
        dependencies = copy.deepcopy(model.dependencies)
        for attribute in resource.attributes:
            resource_args, dependencies = CDK._process_attribute(
                self,
                model,
                attribute,
                resource_args,
                dependencies,
            )

        CDK._generate_default_dependencies(
            self, dependencies, model, resource_args, resource.name,
        )

        # Create resource
        CDK._parent_resources_stack.remove(resource.type)

        CDK._logger.debug(
            'Created resource %s named %s',
            resource_class, resource.name,
        )

        return resource_class(self, resource.name, **resource_args)

    def _process_attribute(
        self,
        model: rm.ResourceModel,
        attribute: pf.ParsedAttribute,
        resource_args: dict[str, object],
        dependencies: dict[str, dict[str, object]] | None,
    ):
        if attribute.name in dependencies:
            created_name = f"{dependencies[attribute.name]['resource']}/"\
                           f"{attribute.value}"

            # Checks if attribute is an explicit dependency
            if created_name not in CDK._created_resources.keys():

                if isinstance(attribute.value, str):
                    raise cdk_exceptions.CDKDependencyNotDeclared(
                        attribute.name, attribute.value,
                    )

                # Creates explicit dependency
                CDK._create_dependency(
                    self, attribute.name, attribute.value,
                    resource_args, attribute.name,
                )

            resource_args[attribute.name] = CDK._created_resources[created_name]

            del dependencies[attribute.name]
            return resource_args, dependencies

        # Checks if attribute is an internal object
        if attribute.name in model.internal_objects:
            resource_args = CDK._create_internal_object(
                self,
                model.internal_objects[attribute.name],
                attribute.name,
                attribute.value,
                resource_args,
            )
            return resource_args, dependencies

        # Checks if attribute is expected as an attibute
        if attribute.name not in model.attributes:
            raise cdk_exceptions.CDKInvalidAttribute(
                attribute.name, model.type,
            )

        # Processes list attribute
        attribute_value = attribute.value
        if model.attributes[attribute.name].is_list:
            if type(attribute.value) is list:
                attribute_value = [i.value for i in attribute.value]
            else:
                attribute_value = [attribute.value]

        # Sets attribute value
        resource_args[model.attributes[attribute.name].cdk_name] = attribute_value

        return resource_args, dependencies

    def _generate_default_dependencies(
            self,
            dependencies,
            model: rm.ResourceModel,
            resource_args,
            resourceName,
    ):
        # Create missing dependencies
        for dependency_name, dependency_object in dependencies.items():
            CDK._create_dependency(
                self, dependency_name, dependency_object, resource_args, resourceName,
            )

        # Create default internal objects if needed
        for internal_object_name, internal_object in model.internal_objects.items():
            if internal_object_name not in resource_args:
                for default_args in internal_object['defaults']:
                    CDK._create_internal_object(
                        self,
                        model.internal_objects[internal_object_name],
                        internal_object_name,
                        default_args,
                        resource_args,
                    )

    def _create_internal_object(
        self,
        internal_object_model,
        name: str,
        internal_object_args,
        resource_args: dict,
    ):
        internal_object_type = internal_object_model['var_type'] \
            if 'var_type' in internal_object_model else 'Unknown'

        if internal_object_type.startswith('list'):
            if name not in resource_args:
                resource_args[name] = []

            if isinstance(internal_object_args, list) \
                    and isinstance(internal_object_args[0], pf.ParsedDict):

                for internalObject in internal_object_args:
                    res = CDK._create_resource(
                        self,
                        internalObject.value,
                        internal_object_model['resource'],
                    )
                    resource_args[name] += [res]

                return resource_args

            res = CDK._create_resource(
                self,
                internal_object_args,
                internal_object_model['resource'],
            )
            resource_args[name] += [res]
            return resource_args

        res = CDK._create_resource(
            self,
            internal_object_args,
            internal_object_model['resource'],
        )
        resource_args[name] = res

        return resource_args

    def _create_dependency(self, dep_name, dep_value, resource_args, parent_name):
        class_, class_name, class_attributes = CDK._create_default_resource(
            self, dep_value['resource'], parent_name,
        )

        id = class_(self, class_name, **class_attributes).id
        if dep_name:
            resource_args[dep_name] = id

        CDK._parent_resources_stack.remove(dep_value['resource'])
