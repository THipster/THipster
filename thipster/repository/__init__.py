"""Repository module.

Contains the various options to store the JSON models used by THipster to generate the
Python Terraform CDK constructs.
Currently, two options are available:
- A local repository, which stores the models in a local folder
- A GitHub repository
"""

from .github import GithubRepo
from .local import LocalRepo
