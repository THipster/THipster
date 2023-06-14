# THipster

THipster is a tool dedicated to simplifying the difficulty associated with writing Terraform files.
It allows users to write infrastructure as code in a simplified format, using either YAML (with JINJA) or the dedicated Thipster DSL.

Written entirely in Python, it leverages the Python CDK for Terraform to create Terraform files and apply them to the chosen provider.

<p align="center">
  <a href="https://github.com/THipster/THipster/blob/main/LICENSE" target="_blank" alt="License">
    <img src="https://img.shields.io/github/license/THipster/THipster" alt="License">
  </a>
  <a href="https://thipster.readthedocs.io/en/latest/?badge=latest" target="_blank" alt="Read the docs documentation">
    <img src="https://readthedocs.org/projects/thipster/badge/?version=latest" alt="Read the docs documentation">
  </a>
  <a href="https://pypi.org/project/thipster/" target="_blank" alt="PyPi package">
    <img src="https://img.shields.io/pypi/v/thipster?color=brightgreen&label=pypi%20package" alt="Package version">
  </a>
  <a href="https://pypi.org/project/thipster/" target="_blank" alt="PyPi package">
    <img src="https://img.shields.io/pypi/pyversions/thipster?color=brightgreen" alt="Supported Python versions">
  </a>
</p>

## Technology Stack
Written in Python 3.11, thipster is designed as a python package, to be used either as a standalone tool, or as a module inside a running process like a CI/CD pipeline.

## Project Status
THipster is currently in an active development state. If you want to know more, please check the [CHANGELOG](https://github.com/THipster/THipster/blob/main/CHANGELOG.md) for more details.

## Dependencies

In order to user THipster, you will need to have the following installed:
- [Python](https://www.python.org/downloads/) (3.11+)
- [pipenv](https://pipenv.pypa.io/en/latest/) v2021.5+
- [Terraform CLI](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli) (1.2+)
- [Node.js](https://nodejs.org/) and npm v16+.

## Installation

To use THipster, you can simply install the package with pip:

```console
pip install thipster
```

If you want to install the google dependencies aswell use

```console
pip install thipster[google]
```

The list of available versions can be found on [PyPI](https://pypi.org/project/thipster/).

## Usage

You can use THipster in two ways:
- By leveraging the [THipster CLI](https://github.com/THipster/THipster-cli)
- By directly using the [THipster Python package](https://pypi.org/project/thipster/) in your own code

Main feature:
- Generate Terraform files from a YAML+JINJA or THIPS file:
```python
from thipster import Engine as ThipsterEngine
from thipster.auth import Google
from thipster.parser import ParserFactory
from thipster.repository import GithubRepo
from thipster.terraform import Terraform

# create new THipster engine
engine = ThipsterEngine(ParserFactory(), GithubRepo('THipster/models'), Google, Terraform())

# generate Terraform files and plan from a YAML+JINJA file
terraform_plan = engine.run('path/to/file/or/directory')
print(terraform_plan)
```

## How to test the software

To run the tests, you can use the following command:

```console
pip install -e .[test]
pytest tests
```

## Known issues

All known issues, bugs, and feature requests are tracked in the [Issue tracker](https://github.com/THipster/THipster/issues).

## Getting help

If you have questions, concerns, bug reports, etc, please file an issue in this repository's [Issue tracker](https://github.com/THipster/THipster/issues).

## Getting involved

To install the project for development, you can use the following command:

```console
pip install -r requirements.txt && pip install -e .[dev,test,doc,google]
pre-commit install && pre-commit run --all-files
```

For more information on how to help out, please check the [CONTRIBUTING](https://github.com/THipster/THipster/blob/main/CONTRIBUTING.md) file.

## Open source licensing info
1. [LICENSE](https://github.com/THipster/THipster/blob/main/LICENSE)
2. [CFPB Source Code Policy](https://github.com/cfpb/source-code-policy/)

## Credits and references

1. Projects that inspired you
    - [AWS Application Composer](https://aws.amazon.com/application-composer/?nc1=h_ls)
2. Related projects
    - [Wing Programming Language](https://www.winglang.io/)
