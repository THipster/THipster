from setuptools import setup

__version__ = '0.0.1'

requirements = [
    '',
]

setup(
    name='thipster',
    version=__version__,
    package_dir={'': 'thipster'},
    install_requires=requirements,
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
)
