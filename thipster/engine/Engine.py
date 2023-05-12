"""_Engine.py module.
"""

import subprocess
import sys
import os
import importlib
import time
from constructs import Construct
from cdktf import App, TerraformStack

from engine.I_Parser import I_Parser
from engine.I_Repository import I_Repository
from engine.I_Auth import I_Auth
from cdktf_cdktf_provider_google.provider import GoogleProvider
from engine.I_Terraform import I_Terraform
import engine.ParsedFile as pf
from engine.ResourceModel import ResourceModel


class Engine():
    """Class representing the engine of thipster

    The core of the application, it is used to call and link all
    interfaces together.

    Methods
    -------
    run(filename: str)
        Processes a fileName and creates the corresponding Cloud architecture plan

    """

    importedPackages = []

    def __init__(
            self, parser: I_Parser,
            repository: I_Repository,
            auth: I_Auth,
            terraform:  I_Terraform,
    ):
        """
        Parameters
        ----------
        parser : I_Parser
            Instance of a Parser class
        repository : I_Repository
            Instance of a Respository class
        auth : I_Auth
            Instance of an Auth class
        terraform : I_Terraform
            Instance of a Terraform class

        """
        self.__parser = parser
        self.__repository = repository
        self.__auth = auth
        self.__terraform = terraform

    def pip_install(package: str):
        if package not in Engine.importedPackages:
            subprocess.check_call(
                [sys.executable, '-m', 'pip', 'install', '-qqq', package],
            )
            Engine.importedPackages.append(package)

    def _import(packageName: str, moduleName: str, className: str) -> type:

        module = importlib.import_module(f'{packageName}.{moduleName}')
        clazz = getattr(module, className)

        return clazz

    def _create_resource(self, model: ResourceModel, resource: pf.ParsedResource):
        # 3 - TODO: vérifie les paramètres de la ressource correspondent à ceux du
        # modèle
        # 4 - TODO: vérifie chaque dépendance explicite est bien déclarée dans le
        # fichier

        # # 5 - TODO: ajoute la ressource et ses dépendances dans un graphe orienté
        # # 6 - TODO: ajoute une relation dans le graphe orienté

        # Import
        Engine.pip_install(model.cdk_provider)

        resourceClass = Engine._import(
            model.cdk_provider, model.cdk_module, model.cdk_name,
        )

        resource_args = {
            model.name_key: resource.name,
        }

        for a in resource.attributes:
            resource_args[model.attributes[a.name].cdk_name] = a.value
        # 8 - TODO: y crée les dépendances implicites

        # 9 - y crée la ressource à l’aide des paramètres demandés et les
        # valeurs par défaut si nécessaire
        resourceClass(self, resource.name, **resource_args)

    def run(self, path: str):
        """Returns an AST from the input file name

        Calls the different run methods of the parser, repository,
        auth and terraform modules.
        Transforms the inputed filename into a Cloud architecture plan.

        Parameters
        ----------
        path : str
            The path of the files to be processed

        Returns
        -------
        list[ResourceModel]
            List of resource models
        """
        start = time.time()
        # Parse files
        file = self.__parser.run(path)
        assert type(file) == pf.ParsedFile

        end = time.time()
        print("Parsed:", end - start)
        start = time.time()

        # Get needed models
        types = [r.type for r in file.resources]
        models = self.__repository.get(types)

        end = time.time()
        print("Models:", end - start)
        start = time.time()

        # Init CDK
        app = App()

        for resource in file.resources:
            # 7 - déclare un nouvel objet stack dans le CDK Terraform
            class __ResourceStack(TerraformStack):
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

                    Engine._create_resource(
                        self,
                        model=models[resource.type],
                        resource=resource,
                    )

            __ResourceStack(app, f'{resource.type}/{resource.name}')

        # 10 - L’engine synthétise les fichiers
        app.synth()

        end = time.time()
        print("CDK:", end - start)

        # self.__auth.run()
        # self.__terraform.run()

        return [f'{app.outdir}/stacks/{c.node.path}' for c in app.node.children]
