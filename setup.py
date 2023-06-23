"""Setup file for the THipster-cli package."""
from pathlib import Path

from setuptools import find_packages, setup


def get_extra_requires() -> dict[str, list[str]]:
    """Get the extra requirements from the requirements folder."""
    extras_require = {}
    for req_file in Path('requirements').glob('requirements-*.txt'):
        extras_require[
            req_file.stem.removeprefix('requirements-')
        ] = req_file.read_text().splitlines()
    return extras_require


__version__ = '0.19.3'

with Path('requirements.txt').open() as f:
    required = f.read().splitlines()

with Path('README.md').open() as rm:
    readme = rm.read()

setup(
    name='thipster',
    authors=[
        {'name': 'rcattin', 'email': 'rafa.cattin+thipster@gmail.com'},
        {'name': 'gsuquet', 'email': 'gsuquet@ippon.fr'},
    ],
    description='THipster is a tool dedicated to simplifying the difficulty associated \
with writing Terraform files. It allows users to write infrastructure as code in a \
simplified format, using either YAML (with JINJA) or the dedicated Thipster DSL.',
    long_description=readme,
    long_description_content_type='text/markdown',
    keywords=[
        'thipster',
        'terraform',
        'infrastructure',
        'infrastructure-as-code',
        'iac',
        'generator',
        'dsl',
        'yaml',
    ],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Programming Language :: Python :: 3.11',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],

    download_url='https://github.com/THipster/THipster.git',
    url='https://github.com/THipster/THipster',

    version=__version__,
    install_requires=required,
    packages=find_packages(
        exclude=['pipelines'],
    ),
    extras_require=get_extra_requires(),
)
