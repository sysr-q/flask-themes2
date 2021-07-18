#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
new-theme.py
============
This is a simple script that creates a new theme in the given directory.
"""
import os
import os.path
import sys
import json


def ident_to_title(ident):
    return ident.replace("_", " ").title()


def create_theme(appident, destination):
    destination = destination.rstrip(os.path.sep)
    identifier = os.path.basename(destination)
    data = dict(
        application=appident,
        identifier=identifier,
        name=ident_to_title(identifier),
        author="Your Name",
    )
    os.makedirs(destination)

    info_json = os.path.join(destination, "info.json")
    templates_path = os.path.join(destination, "templates")
    static_path = os.path.join(destination, "static")
    with open(info_json, "w") as fd:
        json.dump(data, fd, indent=4)
    os.makedirs(templates_path)
    os.makedirs(static_path)


if __name__ == "__main__":
    args = sys.argv[1:]
    scriptname = os.path.basename(sys.argv[0])
    if len(args) < 2:
        print "Usage: %s APPIDENT PATH" % scriptname
        sys.exit(2)
    create_theme(args[0], args[1])
