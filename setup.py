from setuptools import setup, find_packages

__version__ = '0.13.1'

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    version=__version__,
    install_requires=required,
    packages=find_packages(
        exclude=['pipelines'],
    ),
    extras_require={
        'test': [
            'pytest',
            'pytest-mock',
        ],
        'dev': [
            'pytest',
            'pytest-mock',
            'dagger.io',
            'pre-commit',
        ],
        'doc': [
            'sphinx',
        ],
    },
)
