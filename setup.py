#!/usr/bin/env python
import os
import ast
import re

from setuptools import setup

_version_re = re.compile(r"__version__\s+=\s+(.*)")


def read(*parts):
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, *parts), "r") as fp:
        return fp.read()


version_line = re.search(
    r"__version__\s+=\s+(.*)", read("flask_themes2", "__init__.py")
).group(1)

version = str(ast.literal_eval(version_line))
long_description = read("README.md")

requires = ["Flask>=2.0"]

setup(
    name="Flask-Themes2",
    version=version,
    url="https://github.com/sysr-q/flask-themes2",
    license="MIT",
    author="sysr-q",
    author_email="chris@gibsonsec.org",
    description="Provides infrastructure for theming Flask applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="flask themes theming style",
    packages=["flask_themes2"],
    zip_safe=False,
    install_requires=requires,
    tests_require="pytest",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
