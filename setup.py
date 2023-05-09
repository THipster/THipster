from setuptools import setup

__version__ = '0.7.0'

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='thipster',
    version=__version__,
    package_dir={'': 'thipster'},
    install_requires=required,
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
    },
    entry_points={
        'console_scripts': [
            'thipster-demo = demo:demo',
        ],
    },
)
