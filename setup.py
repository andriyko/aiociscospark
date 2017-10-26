#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Note: To use the 'upload' functionality of this file, you must:
#   $ pip install twine

import io
import os
import sys
from shutil import rmtree

from setuptools import find_packages, setup, Command
from setuptools.command.test import test as TestCommand

# Package meta-data.
NAME = 'aiociscospark'
DESCRIPTION = 'Python asynchronous HTTP client for Cisco Spark API'
URL = 'https://github.com/andriyko/aiociscospark'
EMAIL = 'ahrytskiv@gmail.com'
AUTHOR = 'Andriy Hrytskiv'

here = os.path.abspath(os.path.dirname(__file__))
# Import the README and use it as the long-description.
# Note: this will only work if 'README.rst' is present in your MANIFEST.in file!
with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = '\n' + f.read()


def read_req_from_file(filename):
    fpath = os.path.join(here, filename)
    return [i.strip() for i in open(fpath).readlines()]


class UploadCommand(Command):
    """Support setup.py upload."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(here, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution…')
        os.system('{0} setup.py sdist bdist_wheel --universal'.format(sys.executable))

        self.status('Uploading the package to PyPi via Twine…')
        os.system('twine upload dist/*')

        sys.exit()


class PyTest(TestCommand):
    """
    Setup the py.test test runner.
    """

    def finalize_options(self):
        """
        Set options for the command line.
        """
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        """
        Execute the test runner command.
        """
        # Import here, because outside the required eggs aren't loaded yet
        import pytest
        sys.exit(pytest.main(self.test_args))


# Where the magic happens:
setup(
    name=NAME,
    version='0.0.1',
    description=DESCRIPTION,
    long_description=long_description,
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    packages=find_packages(exclude=('tests', 'scripts', 'examples')),
    install_requires=read_req_from_file('requirements.txt'),
    tests_require=read_req_from_file('dev-requirements.txt'),
    include_package_data=True,
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython'
    ],
    cmdclass={
        'upload': UploadCommand,
        'test': PyTest
    },
)