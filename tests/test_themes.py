"""
test-themes.py
==============
This tests the Flask-Themes2 extension.
"""
from __future__ import with_statement

import os
from importlib import reload
from operator import attrgetter

from flask import Flask, render_template, url_for
from jinja2 import FileSystemLoader

TESTS = os.path.dirname(__file__)


def import_flask_themes2():
    import flask_themes2
    flask_themes2 = reload(flask_themes2)
    return flask_themes2


class TestThemeObject(object):
    def test_theme(self):
        flask_themes2 = import_flask_themes2()
        path = os.path.join(TESTS, "themes", "cool")
        cool = flask_themes2.Theme(path)
        assert cool.name == "Cool Blue v1"
        assert cool.identifier == "cool"
        assert cool.path == os.path.abspath(path)
        assert cool.static_path == os.path.join(cool.path, "static")
        assert cool.templates_path == os.path.join(cool.path, "templates")
        assert cool.license_text is None
        assert isinstance(cool.jinja_loader, FileSystemLoader)

    def test_license_text(self):
        flask_themes2 = import_flask_themes2()
        path = os.path.join(TESTS, "themes", "plain")
        plain = flask_themes2.Theme(path)
        assert plain.license_text.strip() == "The license."


class TestLoaders(object):
    def test_load_themes_from(self):
        flask_themes2 = import_flask_themes2()
        path = os.path.join(TESTS, "themes")
        themes_iter = flask_themes2.load_themes_from(path)
        themes = list(sorted(themes_iter, key=attrgetter("identifier")))
        assert themes[0].identifier == "cool"
        assert themes[1].identifier == "notthis"
        assert themes[2].identifier == "plain"

    def test_packaged_themes_loader(self):
        flask_themes2 = import_flask_themes2()
        app = Flask(__name__)
        themes_iter = flask_themes2.packaged_themes_loader(app)
        themes = list(sorted(themes_iter, key=attrgetter("identifier")))
        assert themes[0].identifier == "cool"
        assert themes[1].identifier == "notthis"
        assert themes[2].identifier == "plain"

    def test_theme_paths_loader(self):
        flask_themes2 = import_flask_themes2()
        app = Flask(__name__)
        app.config["THEME_PATHS"] = [os.path.join(TESTS, "morethemes")]
        themes = list(flask_themes2.theme_paths_loader(app))
        assert themes[0].identifier == "cool"


class TestSetup(object):
    def test_manager(self):
        flask_themes2 = import_flask_themes2()
        app = Flask(__name__)
        manager = flask_themes2.ThemeManager(app, "testing")
        assert app.theme_manager is manager
        app.config["THEME_PATHS"] = [os.path.join(TESTS, "morethemes")]
        manager.refresh()
        themeids = sorted(manager.themes.keys())
        assert themeids == ["cool", "plain"]
        assert manager.themes["cool"].name == "Cool Blue v2"

    def test_setup_themes(self):
        flask_themes2 = import_flask_themes2()
        app = Flask(__name__)
        app.config["THEME_PATHS"] = [os.path.join(TESTS, "morethemes")]
        flask_themes2.Themes(app, app_identifier="testing")

        assert hasattr(app, "theme_manager")
        assert "_themes" in app.blueprints
        assert "theme" in app.jinja_env.globals
        assert "theme_static" in app.jinja_env.globals

    def test_get_helpers(self):
        flask_themes2 = import_flask_themes2()
        app = Flask(__name__)
        app.config["THEME_PATHS"] = [os.path.join(TESTS, "morethemes")]
        flask_themes2.Themes(app, app_identifier="testing")

        with app.test_request_context("/"):
            cool = app.theme_manager.themes["cool"]
            plain = app.theme_manager.themes["plain"]
            assert flask_themes2.get_theme("cool") is cool
            assert flask_themes2.get_theme("plain") is plain
            tl = flask_themes2.get_themes_list()
            assert tl[0] is cool
            assert tl[1] is plain
            try:
                flask_themes2.get_theme("notthis")
            except KeyError:
                pass
            else:
                raise AssertionError(
                    "Getting a nonexistent theme should " "raise KeyError"
                )


class TestStatic(object):
    def test_static_file_url(self):
        flask_themes2 = import_flask_themes2()
        app = Flask(__name__)
        app.config["THEME_PATHS"] = [os.path.join(TESTS, "morethemes")]
        flask_themes2.Themes(app, app_identifier="testing")

        with app.test_request_context("/"):
            url = flask_themes2.static_file_url("cool", "style.css")
            genurl = url_for("_themes.static", themeid="cool", filename="style.css")
            assert url == genurl


class TestTemplates(object):
    def test_template_exists(self):
        flask_themes2 = import_flask_themes2()
        app = Flask(__name__)
        app.config["THEME_PATHS"] = [os.path.join(TESTS, "morethemes")]
        flask_themes2.Themes(app, app_identifier="testing")

        with app.test_request_context("/"):
            assert flask_themes2.template_exists("hello.html")
            assert flask_themes2.template_exists("_themes/cool/hello.html")
            assert not flask_themes2.template_exists("_themes/plain/hello.html")

    def test_test_loader(self):
        flask_themes2 = import_flask_themes2()
        app = Flask(__name__)
        app.config["THEME_PATHS"] = [os.path.join(TESTS, "morethemes")]
        flask_themes2.Themes(app, app_identifier="testing")

        with app.test_request_context("/"):
            src = flask_themes2.themes_blueprint.jinja_loader.get_source(
                app.jinja_env, "_themes/cool/hello.html"
            )
            assert src[0].strip() == "Hello from Cool Blue v2."

    def test_render_theme_template(self):
        flask_themes2 = import_flask_themes2()
        app = Flask(__name__)
        app.config["THEME_PATHS"] = [os.path.join(TESTS, "morethemes")]
        flask_themes2.Themes(app, app_identifier="testing")

        with app.test_request_context("/"):
            coolsrc = flask_themes2.render_theme_template("cool", "hello.html").strip()
            plainsrc = flask_themes2.render_theme_template(
                "plain", "hello.html"
            ).strip()
            assert coolsrc == "Hello from Cool Blue v2."
            assert plainsrc == "Hello from the application"

    def test_active_theme(self):
        flask_themes2 = import_flask_themes2()
        app = Flask(__name__)
        app.config["THEME_PATHS"] = [os.path.join(TESTS, "morethemes")]
        flask_themes2.Themes(app, app_identifier="testing")

        with app.test_request_context("/"):
            appdata = render_template("active.html").strip()
            cooldata = flask_themes2.render_theme_template(
                "cool", "active.html"
            ).strip()
            plaindata = flask_themes2.render_theme_template(
                "plain", "active.html"
            ).strip()
            assert appdata == "Application, Active theme: none"
            assert cooldata == "Cool Blue v2, Active theme: cool"
            assert plaindata == "Application, Active theme: plain"

    def test_theme_static(self):
        flask_themes2 = import_flask_themes2()
        app = Flask(__name__)
        app.config["THEME_PATHS"] = [os.path.join(TESTS, "morethemes")]
        flask_themes2.Themes(app, app_identifier="testing")

        with app.test_request_context("/"):
            coolurl = flask_themes2.static_file_url("cool", "style.css")
            cooldata = flask_themes2.render_theme_template(
                "cool", "static.html"
            ).strip()
            assert cooldata == "Cool Blue v2, %s" % coolurl

    def test_theme_static_outside(self):
        flask_themes2 = import_flask_themes2()
        app = Flask(__name__)
        app.config["THEME_PATHS"] = [os.path.join(TESTS, "morethemes")]
        flask_themes2.Themes(app, app_identifier="testing")

        with app.test_request_context("/"):
            try:
                render_template("static.html")
            except RuntimeError:
                pass
            else:
                raise AssertionError(
                    "Rendering static.html should have " "caused a RuntimeError"
                )

    def test_theme_include_static(self):
        flask_themes2 = import_flask_themes2()
        app = Flask(__name__)
        app.config["THEME_PATHS"] = [os.path.join(TESTS, "morethemes")]
        flask_themes2.Themes(app, app_identifier="testing")

        with app.test_request_context("/"):
            data = render_template("static_parent.html").strip()
            url = flask_themes2.static_file_url("plain", "style.css")
            assert data == "Application, Plain, %s" % url
