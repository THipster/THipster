from setuptools import setup

requirements = [
    ''
]

setup(
    name= "THipster",
    packages= [
        "thipster"
    ],

    install_requires = requirements,
    extras_require={
        'test': [
            'pytest',
        ],
        'dev':[
            'pytest',
            'dagger.io',
            'pre-commit'
        ]
    }
)