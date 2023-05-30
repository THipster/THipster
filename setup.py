from setuptools import setup, find_packages

__version__ = '0.13.2'

with open('requirements.txt') as f:
    required = f.read().splitlines()

with open("README.md") as rm:
    readme = rm.read()

setup(
    name="thipster",
    authors=[
        {"name": "rcattin", "email": "rafa.cattin+thipster@gmail.com"},
        {"name": "gsuquet", "email": "gsuquet@ippon.fr"},
    ],
    description="",
    long_description=readme,
    classifiers=[
        "Development Status :: 1 - Planning",
        "Programming Language :: Python",
    ],

    download_url="https://github.com/THipster/THipster.git",
    url="https://github.com/THipster/THipster",

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
