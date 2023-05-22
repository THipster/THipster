import copy
import subprocess
import sys
import os
import importlib
import uuid
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
    _logger = Logger(__name__)

    def _pip_install(package: str):
        if package not in CDK._importedPackages:
            subprocess.check_call(
                [sys.executable, '-m', 'pip', 'install', '-qqq', package],
            )
            CDK._importedPackages.append(package)

    def _import(packageName: str, moduleName: str, className: str) -> type:

        module = importlib.import_module(f'{packageName}.{moduleName}')
        clazz = getattr(module, className)

        return clazz

    def _create_default_resource(
        self, typ: str, parentName: str | None = None,
        noModif: bool = True,
    ):
        if typ in CDK._parentStack:
            raise CDKCyclicDependencies(CDK._parentStack)

        CDK._parentStack.append(typ)

        model = CDK._models[typ]
        if noModif and not all(map(lambda x: x.optional, model.attributes.values())):
            raise CDKMissingAttributeInDependency(typ)

        name = f"{parentName}-{uuid.uuid4()}"

        # Import package and class
        CDK._pip_install(model.cdk_provider)
        resourceClass = CDK._import(
            model.cdk_provider, model.cdk_module, model.cdk_name,
        )

        deps = copy.deepcopy(model.dependencies)

        resource_args = {}

        if model.name_key:
            resource_args[model.name_key] = name

        for _, v in model.attributes.items():
            resource_args[v.cdk_name] = v.default

        # Create dependencies
        for k, d in deps.items():
            c, n, a = CDK._create_default_resource(self, d['resource'], name)
            id = c(self, n, **a).id
            if k:
                resource_args[k] = id

            CDK._parentStack.remove(d['resource'])

        return (resourceClass, name, resource_args)

    def _create_resource_from_args(
        self, typ: str, args: list[pf.ParsedAttribute] | None,
    ):
        resourceClass, resourceName, resource_args = CDK._create_default_resource(
            self,
            typ,
            noModif=False,
        )
        model = CDK._models[typ]

        # 3 - vérifie les paramètres de la ressource correspondent à ceux du modèle
        deps = copy.deepcopy(model.dependencies)

        for attribute in args:

            if attribute.name and model.name_key:
                resource_args[model.name_key] = attribute.name

            # Checks if attribute is an already declared dependency
            if attribute.name in deps:
                del deps[attribute.name]
                continue

            # Checks if attribute is an internal object
            if attribute.name in model.internalObjects:
                CDK._create_resource_from_args(
                    self,
                    model.internalObjects[attribute.name]['resource'],
                    attribute.value,
                )

            # Checks if attribute is required
            if attribute.name not in model.attributes:
                raise CDKInvalidAttribute(attribute.name, model.type)

            resource_args[model.attributes[attribute.name].cdk_name] = attribute.value

        # Create resource
        CDK._parentStack.remove(typ)
        if not model.name_key:
            return resourceClass(**resource_args)
        return resourceClass(self, resourceName, **resource_args)

    def _create_resource_from_resource(self, resource: pf.ParsedResource):
        resourceClass, _, resource_args = CDK._create_default_resource(
            self,
            resource.type,
            noModif=False,
        )
        model = CDK._models[resource.type]

        # 3 - vérifie les paramètres de la ressource correspondent à ceux du modèle
        deps = copy.deepcopy(model.dependencies)

        if model.name_key:
            resource_args[model.name_key] = resource.name
        for _, v in model.attributes.items():
            resource_args[v.cdk_name] = v.default

        for attribute in resource.attributes:
            # Checks if attribute is an already declared dependency
            if attribute.name in deps:
                del deps[attribute.name]
                continue

            # Checks if attribute is an internal object
            if attribute.name in model.internalObjects:
                res = CDK._create_resource_from_args(
                    self,
                    model.internalObjects[attribute.name]['resource'],
                    attribute.value,
                )

                if model.internalObjects[attribute.name]['is_list']:
                    if attribute.name not in resource_args:
                        resource_args[attribute.name] = []
                    resource_args[attribute.name] += [res]
                    continue

                resource_args[attribute.name] = res
                continue

            # Checks if attribute is required
            if attribute.name not in model.attributes:
                raise CDKInvalidAttribute(attribute.name, model.type)

            resource_args[model.attributes[attribute.name].cdk_name] = attribute.value

        # Create resource
        CDK._parentStack.remove(resource.type)
        return resourceClass(self, resource.name, **resource_args)

    def generate(self, file: pf.ParsedFile, models: dict[str, rm.ResourceModel]):

        CDK._models = models
        # Init CDK
        app = App()

        for resource in file.resources:
            # 7 - déclare un nouvel objet stack dans le CDK Terraform
            class _ResourceStack(TerraformStack):
                def __init__(self, scope: Construct, ns: str):
                    super().__init__(scope, ns)

                    GoogleProvider(
                        self, f"{resource.name}_google",
                        project="rcattin-sandbox",
                        credentials=os.path.join(
                            os.getcwd(),
                            "rcattin-sandbox-credentials.json",
                        ),

                        region="europe-west1",
                        zone="europe-west1-b",
                    )

                    res = CDK._create_resource_from_resource(
                        self,
                        resource=resource,
                    )

                    TerraformOutput(
                        self, 'id',
                        value=res.id,
                    )

            _ResourceStack(app, f'{resource.type}/{resource.name}')

        # 10 - L’engine synthétise les fichiers
        app.synth()

        self.__dirs = [
            f'{app.outdir}/stacks/{c.node.path}' for c in app.node.children
        ]

        return self.__dirs

    def apply(self):
        """Apply generated terraform code

        Raises
        ------
        NotImplementedError
            If method is not implemented in inheriting classes

        """
        raise NotImplementedError('Should implement apply()')

    def plan(self):
        """Get plan from generated terraform code

        Raises
        ------
        NotImplementedError
            If method is not implemented in inheriting classes

        """
        raise NotImplementedError('Should implement plan()')
