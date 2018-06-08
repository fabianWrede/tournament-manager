from setuptools import setup, find_packages


package_name = 'tournament-manager'

def get_long_description():
    try:
        with open('README.md', 'r') as f:
            return f.read()
    except IOError:
        return ''


setup(
    name=package_name,
    version='1.0.2',
    author='Fabian Wrede',
    author_email='fabian.wrede@posteo.de',
    packages=find_packages(),
    py_modules=['cli'],
    description='Manage tournaments with the swiss system on the command line.',
    url='https://github.com/fabianWrede/tournament-manager',
    long_description=get_long_description(),
    entry_points={
        'console_scripts': [
            'tournament-manager = cli:main'
        ]
    },
    license='License :: Apache License 2.0',
)
