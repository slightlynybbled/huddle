from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='huddle',

    version='0.0.1dev0',
    description='A server-oriented auto-deployment utility for any type of program or script',
    author='Jason Jones',
    author_email='slightlynybbled@gmail.com',
    url='https://github.com/slightlynybbled/huddle',
    keywords=['auto-deployment', 'huddle'],
    classifiers=[],
    install_requires=requirements,
    packages=find_packages(),
    entry_points={'console_scripts': ['huddle = huddle.__main__:main']}
)
