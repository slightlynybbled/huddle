from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='auto_deploy',

    version='0.0.1dev0',
    description='A server-oriented auto-deployment utility',
    author='Jason Jones',
    author_email='slightlynybbled@gmail.com',
    url='https://github.com/slightlynybbled/auto_deploy',
    keywords=['auto-deployment'],
    classifiers=[],
    install_requires=requirements,
    packages=find_packages(),
    entry_points={'console_scripts': ['auto_deploy = auto_deploy.__main__:main']}
)
