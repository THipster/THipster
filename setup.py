from setuptools import setup, find_packages

__version__ = '0.16.4'

with open('requirements.txt') as f:
    required = f.read().splitlines()

with open('README.md') as rm:
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
    classifiers=[
        'Development Status :: 1 - Planning',
        'Programming Language :: Python',
    ],

    download_url='https://github.com/THipster/THipster.git',
    url='https://github.com/THipster/THipster',

    version=__version__,
    install_requires=required,
    packages=find_packages(
        exclude=['pipelines'],
    ),
    extras_require={
        'test': [
            'pytest==7.3.1',
            'pytest-mock==3.10.0',
        ],
        'dev': [
            'pytest==7.3.1',
            'pytest-mock==3.10.0',
            'dagger-io==0.6.1',
            'pre-commit==3.3.2',
        ],
        'doc': [
            'Sphinx==6.2.1',
            'myst-parser==1.0.0',
        ],
        'google': [
            'cdktf-cdktf-provider-google==7.0.10',
            'google-auth==2.19.1',
        ],
    },
)
