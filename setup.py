from setuptools import setup

__version__ = '0.0.0'

requirements = [
    '',
]

setup(
    name='THipster',
    version=__version__,
    packages=[
        'thipster',
    ],

    install_requires=requirements,
    extras_require={
        'test': [
            'pytest',
        ],
        'dev': [
            'pytest',
            'dagger.io',
            'pre-commit',
        ],
    },
)
