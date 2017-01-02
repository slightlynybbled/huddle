from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='auto_deploy',
    packages=find_packages(),
    version='0.0.1dev0',
    description='A server-oriented auto-deployment utility',
    author='Jason Jones',
    author_email='slightlynybbled@gmail.com',
    url='https://github.com/slightlynybbled/auto_deploy',
    keywords=['auto-deployment'],
    classifiers=[],
    install_requires=requirements
)
