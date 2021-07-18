# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

sys.path.insert(0, os.path.abspath("_themes"))


# -- Project information -----------------------------------------------------

project = "Flask-Themes2"
copyright = '2013-2021 Chris Carter, 2021 Peter Justin, 2012 Drew Lustro, 2010 Matthew "LeafStorm" Frazier'
author = 'Chris Carter, Peter Justin, Drew Lustro, Matthew "LeafStorm" Frazier'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "alabaster"

html_theme_options = {
    "description": "Provides infrastructure for theming Flask applications",
    "github_button": True,
    "github_banner": True,
    "github_user": "sysr-q",
    "github_repo": "flask-themes2",
    "extra_nav_links": {
        "Flask-Themes2 @ PyPI": "https://pypi.python.org/pypi/Flask-Themes2",
        "Flask-Themes2 @ GitHub": "https://github.com/sysr-q/Flask-Themes2",
    },
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

intersphinx_mapping = {
    "https://docs.python.org/": None,
    "https://flask.palletsprojects.com/": None,
}
