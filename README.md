# THipster

THipster is a tool dedicated to simplifying the difficulty associated with writing Terraform files.
It allows users to write infrastructure as code in a simplified format, using either YAML (with JINJA) or the dedicated Thipster DSL.

Written entirely in Python, it leverages the Python CDK for Terraform to create Terraform files and apply them to the chosen provider.

## Technology Stack
Written in Python 3.11, thipster is designed as a python package, to be used either as a standalone tool, or as a module inside a running process like a CI/CD pipeline.

## Project Status
THipster is currently in an active development state. If you want to know more, please check the [CHANGELOG](CHANGELOG.md) for more details.

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

The list of available versions can be found on [PyPI](https://pypi.org/project/thipster/).

## Usage

You can use THipster in two ways:
- By leveraging the [THipster CLI](https://github.com/THipster/THipster-cli)
- By directly using the [THipster Python package](https://pypi.org/project/thipster/) in your own code

Main feature:
- Generate Terraform files from a YAML+JINJA or THIPS file:
```python
from thipster.engine.Engine import Engine as ThipsterEngine
from thipster.repository.GithubRepo import GithubRepo
from thipster.parser.ParserFactory import ParserFactory
from thipster.auth.Google import GoogleAuth
from thipster.terraform.CDK import CDK

# create new THipster engine
engine = ThipsterEngine(ParserFactory(), GithubRepo('THipster/models'), GoogleAuth, CDK())

# generate Terraform files and plan from a YAML+JINJA file

list_dir, tf_plan = engine.run('path/to/file/or/directory')
print(tf_plan)
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
pip install -r requirements.txt && pip install -e .[dev,test,doc]
pre-commit install && pre-commit run --all-files
```

For more information on how to help out, please check the [CONTRIBUTING](CONTRIBUTING.md) file.

## Open source licensing info
1. [TERMS](TERMS.md)
2. [LICENSE](LICENSE)
3. [CFPB Source Code Policy](https://github.com/cfpb/source-code-policy/)

## Credits and references

1. Projects that inspired you
    - [AWS Application Composer](https://aws.amazon.com/application-composer/?nc1=h_ls)
2. Related projects
    - [Wing Programming Language](https://www.winglang.io/)
