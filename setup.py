#!/usr/bin/env python3
# coding=utf-8

from setuptools import setup


package_name = 'tournament-manager'
filename = 'src/cli.py'


#def get_version():
#    import ast

#    with open(filename) as input_file:
#        for line in input_file:
#            if line.startswith('__version__'):
#                return ast.parse(line).body[0].value.s


def get_long_description():
    try:
        with open('README.md', 'r') as f:
            return f.read()
    except IOError:
        return ''


setup(
    name=package_name,
    version='1.0.1',
    author='Fabian Wrede',
    author_email='fabian.wrede@posteo.de',
    description='Manage tournaments.',
    url='https://github.com/fabianWrede/tournament-manager',
    long_description=get_long_description(),
    py_modules=[package_name],
    entry_points={
        'console_scripts': [
            'cli = cli:main'
        ]
    },
    license='License :: Apache 2.0 License',
)