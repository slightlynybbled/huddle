import os
from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'readme.md')) as f:
    README = f.read()
exec(open(os.path.join(here, 'huddle/version.py')).read())

setup(
    name='huddle',
    version=__version__,
    description='A server-oriented auto-deployment utility for any type of program or script',
    long_description = README,
    author='Jason Jones',
    author_email='slightlynybbled@gmail.com',
    url='https://github.com/slightlynybbled/huddle',
    keywords=['auto-deployment', 'huddle'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: System :: Software Distribution',
        'Topic :: Utilities'
    ],
    install_requires=requirements,
    packages=find_packages(),
    entry_points={'console_scripts': ['huddle = huddle.__main__:main']}
)
