import subprocess
import sys
import importlib
from engine.I_Parser import I_Parser
from engine.I_Repository import I_Repository
from engine.I_Auth import I_Auth
from engine.I_Terraform import I_Terraform
from engine.ParsedFile import ParsedFile
from helpers import logger

# from cdktf_cdktf_provider_google.provider import GoogleProvider

# from cdktf import App, LocalBackend, TerraformStack


class Engine():

    def __init__(
            self, parser: I_Parser,
            repository: I_Repository,
            auth: I_Auth,
            terraform:  I_Terraform,
    ):
        self.__parser = parser
        self.__repository = repository
        self.__auth = auth
        self.__terraform = terraform

    def __pip_install(self, package: str):
        subprocess.check_call(
            [sys.executable, '-m', 'pip', 'install', package],
        )

    def __import(self, packageName: str, moduleName: str, className: str) -> type:

        module = importlib.import_module(f'{packageName}.{moduleName}')
        clazz = getattr(module, className)

        return clazz

    @logger('Engine')
    def run(self, path: str):
        # Parse files
        file = self.__parser.run(path)
        assert type(file) == ParsedFile

        # Get needed models
        types = [r.type for r in file.resources]
        models = self.__repository.get(types)

        for resource in file.resources:
            model = models[resource.type]

            # 3 - vérifie les paramètres de la ressource correspondent à ceux du modèle
            # 4 - vérifie chaque dépendance explicite est bien déclarée dans le fichier

            # # 5 - ajoute la ressource et ses dépendances dans un graphe orienté
            # # 6 - ajoute une relation dans le graphe orienté

            # Import
            self.__pip_install(model.cdk_provider)

            resourceClass = self.__import(
                model.cdk_provider, model.cdk_module, model.cdk_name,
            )

            bucket = resourceClass()
            repr(bucket)
            # 7 - déclare un nouvel objet stack dans le CDK Terraform
            # 8 - y crée les dépendances implicites
            # 9 - y crée la ressource à l’aide des paramètres demandés et
            # les valeurs par défaut si nécessaire

            # 10 - L’engine synthétise les fichiers

        self.__auth.run()
        self.__terraform.run()

        return models
