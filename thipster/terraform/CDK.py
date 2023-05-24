import copy
import shutil
import subprocess
import sys
import os
import importlib
import uuid

from python_terraform import Terraform
from constructs import Construct
from cdktf import App, TerraformStack, TerraformOutput

import engine.ResourceModel as rm
import engine.ParsedFile as pf
from cdktf_cdktf_provider_google.provider import GoogleProvider
from engine.I_Terraform import I_Terraform
from helpers import createLogger as Logger


class CDKException(Exception):
    @property
    def message(self):
        return str(self)


class CDKInvalidAttribute(CDKException):
    def __init__(self, attr: str, modelType: str, **args: object) -> None:
        super().__init__(*args)
        self.__attr = attr
        self.__modelType = modelType

    def __str__(self) -> str:
        return f'{self.__attr} in {self.__modelType} but not useful'


class CDKMissingAttribute(CDKException):
    pass


class CDKMissingAttributeInDependency(CDKMissingAttribute):
    pass


class CDKDependencyNotDeclared(CDKException):
    def __init__(self, depType: str, depName: str, **args: object) -> None:
        super().__init__(*args)
        self.__name = depName
        self.__type = depType

    def __str__(self) -> str:
        return f'{self.__type} {self.__name} not declared \
(be sure to declare it before using it)'


class CDKCyclicDependencies(CDKException):
    def __init__(self, stack: list[str], **args: object) -> None:
        super().__init__(*args)
        self.__stack = stack

    def __str__(self) -> str:
        return ','.join(self.__stack)


class CDK(I_Terraform):
    _models = []
    _parentStack = []
    _importedPackages = []

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

    def generate(self, file: pf.ParsedFile, models: dict[str, rm.ResourceModel]):

        CDK._models = models
        # Init CDK
        app = App()

        f_position = file.resources[0].position
        file_name = f_position.fileName if f_position else 'thipster_infrastructure'

        CDK._logger.debug('Creating tf code for file %s', file_name)

        # Declare new stack in CDK
        class _ResourceStack(TerraformStack):
            def __init__(self, scope: Construct, ns: str):
                super().__init__(scope, ns)

                GoogleProvider(
                    self, f"{file_name}_google",
                    project="rcattin-sandbox",
                    credentials=os.path.join(
                        os.getcwd(),
                        "rcattin-sandbox-credentials.json",
                    ),

                    region="europe-west1",
                    zone="europe-west1-b",
                )

                for resource in file.resources:
                    res = CDK._create_resource_from_resource(
                        self,
                        resource=resource,
                    )

                    CDK._created_resources[f'{resource.type}/{resource.name}'] = res.id

                    TerraformOutput(
                        self, f"{resource.name}_id",
                        value=res.id,
                    )

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

        return self.__dirs

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
        if package not in CDK._importedPackages:
            subprocess.check_call(
                [sys.executable, '-m', 'pip', 'install', '-qqq', package],
            )
            CDK._importedPackages.append(package)

    def _import(packageName: str, moduleName: str, className: str) -> type:

        module = importlib.import_module(f'{packageName}.{moduleName}')
        class_ = getattr(module, className)

        return class_

    def _create_default_resource(
        self, typ: str, parentName: str | None = None,
        noModif: bool = True, noDependencies: bool = False,
    ):
        # Checks for cyclic dependency
        if typ in CDK._parentStack:
            CDK._logger.error('%s already present in parent Stack', typ)
            raise CDKCyclicDependencies(CDK._parentStack)

        CDK._parentStack.append(typ)

        model = CDK._models[typ]

        # Checks that all attributes are optional
        if noModif and not all(map(lambda x: x.optional, model.attributes.values())):
            raise CDKMissingAttributeInDependency(typ)

        # Import package and class
        CDK._pip_install(model.cdk_provider)
        resourceClass = CDK._import(
            model.cdk_provider, model.cdk_module, model.cdk_name,
        )

        # Process name + default values
        deps = copy.deepcopy(model.dependencies)
        resource_args = {}

        name = f"{parentName}-{uuid.uuid4()}"
        if model.name_key:
            resource_args[model.name_key] = name

        for _, v in model.attributes.items():
            resource_args[v.cdk_name] = v.default

        # Create default defendencies if needed
        if not noDependencies:
            CDK._create_dependencies(self, deps, resource_args, name)

        CDK._logger.debug('Created default %s named %s', resourceClass, name)

        return (resourceClass, name, resource_args)

    def _create_resource_from_args(
        self, typ: str, args: list[pf.ParsedAttribute] | None,
    ):
        resourceClass, resourceName, resource_args = CDK._create_default_resource(
            self,
            typ,
            noModif=False,
            noDependencies=True,
        )
        model = CDK._models[typ]

        # Process attributes
        deps = copy.deepcopy(model.dependencies)
        for attribute in args:
            if attribute.name and model.name_key:
                resource_args[model.name_key] = attribute.name

            resource_args, deps = CDK._process_attribute(
                self,
                model=model,
                attribute=attribute,
                resource_args=resource_args,
                deps=deps,
            )

        # Create missing dependencies
        CDK._create_dependencies(self, deps, resource_args, resourceName)

        # Create resource
        CDK._parentStack.remove(typ)
        if not model.name_key:
            return resourceClass(**resource_args)

        CDK._logger.debug(
            'Created default %s named %s',
            resourceClass, resourceName,
        )
        return resourceClass(self, resourceName, **resource_args)

    def _create_resource_from_resource(self, resource: pf.ParsedResource):
        # Create resource with default values
        resourceClass, _, resource_args = CDK._create_default_resource(
            self,
            resource.type,
            noModif=False,
            noDependencies=True,
        )
        model = CDK._models[resource.type]

        if model.name_key:
            resource_args[model.name_key] = resource.name

        # Process attributes
        deps = copy.deepcopy(model.dependencies)
        for attribute in resource.attributes:
            resource_args, deps = CDK._process_attribute(
                self,
                model=model,
                attribute=attribute,
                resource_args=resource_args,
                deps=deps,
            )

        # Create missing dependencies
        CDK._create_dependencies(self, deps, resource_args, resource.name)

        # Create resource
        CDK._parentStack.remove(resource.type)

        CDK._logger.debug(
            'Created resource %s named %s',
            resourceClass, resource.name,
        )

        return resourceClass(self, resource.name, **resource_args)

    def _process_attribute(
        self,
        model: rm.ResourceModel,
        attribute: pf.ParsedAttribute,
        resource_args: dict[str, object],
        deps: dict[str, dict[str, object]] | None,
    ):
        # Checks if attribute is an explicit dependency
        if attribute.name in deps:
            created_name = f"{deps[attribute.name]['resource']}/{attribute.value}"

            if created_name not in CDK._created_resources:
                raise CDKDependencyNotDeclared(attribute.name, attribute.value)

            resource_args[attribute.name] = CDK._created_resources[created_name]
            del deps[attribute.name]
            return resource_args, deps

        # Checks if attribute is an internal object
        if attribute.name in model.internalObjects:
            resource_args = CDK._handle_internal_object(
                self,
                model=model,
                attribute=attribute,
                resource_args=resource_args,
            )
            return resource_args, deps

        # Checks if attribute is expected as an attibute
        if attribute.name not in model.attributes:
            raise CDKInvalidAttribute(attribute.name, model.type)

        # Processes list attribute
        attribute_value = attribute.value
        if model.attributes[attribute.name].is_list:
            if type(attribute.value) is list:
                attribute_value = [i.value for i in attribute.value]
            else:
                attribute_value = [attribute.value]

        # Sets attribute value
        resource_args[model.attributes[attribute.name].cdk_name] = attribute_value

        return resource_args, deps

    def _handle_internal_object(
        self,
        model: rm.ResourceModel,
        attribute: pf.ParsedAttribute,
        resource_args: dict,
    ):
        res = CDK._create_resource_from_args(
            self,
            model.internalObjects[attribute.name]['resource'],
            attribute.value,
        )

        int_obj = model.internalObjects[attribute.name]
        var_type = int_obj['var_type'] if 'var_type' in int_obj else 'Unknown'

        if 'list' in var_type:
            if attribute.name not in resource_args:
                resource_args[attribute.name] = []
            resource_args[attribute.name] += [res]
        else:
            resource_args[attribute.name] = res

        return resource_args

    def _create_dependencies(self, deps, resource_args, name):
        for k, d in deps.items():
            c, n, a = CDK._create_default_resource(self, d['resource'], name)
            id = c(self, n, **a).id
            if k:
                resource_args[k] = id

            CDK._parentStack.remove(d['resource'])
