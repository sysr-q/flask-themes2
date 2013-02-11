from setuptools import setup
import sys

requires = ["Flask>=0.6"]
if sys.version_info < (2, 6):
    requires.append("simplejson")

def long_desc():
    with open('README.rst', 'rb') as f:
        return f.read()

kw = {
    "name": "Flask-Themes2",
    "version": "0.1.0",
    "url": "https://github.com/plausibility/Flask-Themes2",
    "license": "MIT",
    "author": "plausibility",
    "author_email": "chris@gibsonsec.org",
    "description": "Provides infrastructure for theming Flask applications",
    "long_description": long_desc(),
    "packages": [
        "flask_themes2"
    ],
    "zip_safe": False,
    "install_requires": requires,
    "tests_require": "nose",
    "test_suite": "nose.collector",
    "classifiers": [
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ]
}

if __name__ == "__main__":
    setup(**kw)
