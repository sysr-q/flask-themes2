"""
Flask-Themes2
=============

.. _docs: http://flask-themes2.rtfd.org
.. _GitHub: https://github.com/plausibility/flask-themes2

.. image:: https://travis-ci.org/plausibility/flask-themes2.png?branch=master
    :target: http://travis-ci.org/plausibility/flask-themes2
    :alt: Build Status

Flask-Themes2 is a fork of Spirits, which is in turn a fork of Flask-Themes.

- `Flask-Themes2 <https://github.com/plausibility/flask-themes2>`_ maintained by Christopher "plausibility" Carter
- `Spirits <https://github.com/drewlustro/spirits>`_ maintained by Drew Lustro
- `Flask-Themes <https://bitbucket.org/leafstorm/flask-themes>`_ by Matthew "LeafStorm" Frazier

This provides infrastructure for themes in Flask.

This was created as Flask-Themes doesn't support versions of \
Flask past 0.6 (or 0.7, I'm not 100% certain),
and as such, it has been no use since the last update \
(which was in 2011, would you believe!).

Installation
------------

To install normally:

.. code-block:: sh

    $ pip install flask-themes2

To install the development (latest) version:

.. code-block:: sh

    $ pip install -e git://github.com/plausibility/flask-themes2.git#egg=flask_themes2-dev

Documentation
-------------

The documentation is on the Flask-Themes2 `docs`_.

Development
-----------
If you're interested in helping, the source is available on `GitHub`_,
feel free to contribute.
"""
from setuptools import setup

requires = ["Flask>=0.6", "simplejson"]

setup(
    name="Flask-Themes2",
    version="0.1.3",  # No execfile() here!
    url="https://github.com/plausibility/flask-themes2",
    license="MIT",
    author="plausibility",
    author_email="chris@gibsonsec.org",
    description="Provides infrastructure for theming Flask applications \
                    (and supports Flask>=0.6!)",
    long_description=__doc__,
    keywords="flask themes theming style",
    packages=[
        "flask_themes2"
    ],
    zip_safe=False,
    install_requires=requires,
    tests_require="nose",
    test_suite="nose.collector",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ]
)
