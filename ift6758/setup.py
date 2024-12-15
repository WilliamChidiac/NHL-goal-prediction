from setuptools import find_packages, setup

def parse_requirements():
    with open('requirements.txt', 'r') as f:
        return f.read().splitlines()

setup(
    name='ift6758',
    packages=find_packages(),
    version='0.1.0',
    description='Sample project repo for IFT6758-2021',
    author='[FILL IN TEAM MEMBERS]',
    license='',
    install_requires=parse_requirements(),
)
