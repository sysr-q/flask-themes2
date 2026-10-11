"""
test-themes.py
==============
This tests the Flask-Themes2 extension.
"""

import os
from importlib import reload
from operator import attrgetter

import pytest
from flask import Flask
from flask import render_template
from flask import url_for
from jinja2 import FileSystemLoader
from jinja2 import TemplateNotFound

TESTS = os.path.dirname(__file__)


def import_flask_themes2():
    import flask_themes2

    flask_themes2 = reload(flask_themes2)
    return flask_themes2


def count_loader_lookups(app, monkeypatch):
    loader = app.jinja_env.loader
    get_source = loader.get_source
    calls = []

    def counting_get_source(environment, template):
        calls.append(template)
        return get_source(environment, template)

    monkeypatch.setattr(loader, "get_source", counting_get_source)
    return calls


class TestThemeObject:
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


class TestLoaders:
    def test_load_themes_from(self):
        flask_themes2 = import_flask_themes2()
        path = os.path.join(TESTS, "themes")
        themes_iter = flask_themes2.load_themes_from(path)
        themes = sorted(themes_iter, key=attrgetter("identifier"))
        assert themes[0].identifier == "cool"
        assert themes[1].identifier == "notthis"
        assert themes[2].identifier == "plain"

    def test_packaged_themes_loader(self):
        flask_themes2 = import_flask_themes2()
        app = Flask(__name__)
        themes_iter = flask_themes2.packaged_themes_loader(app)
        themes = sorted(themes_iter, key=attrgetter("identifier"))
        assert themes[0].identifier == "cool"
        assert themes[1].identifier == "notthis"
        assert themes[2].identifier == "plain"

    def test_theme_paths_loader(self):
        flask_themes2 = import_flask_themes2()
        app = Flask(__name__)
        app.config["THEME_PATHS"] = [os.path.join(TESTS, "morethemes")]
        themes = list(flask_themes2.theme_paths_loader(app))
        assert themes[0].identifier == "cool"


class TestSetup:
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
                    "Getting a nonexistent theme should raise KeyError"
                )


class TestStatic:
    def test_static_file_url(self):
        flask_themes2 = import_flask_themes2()
        app = Flask(__name__)
        app.config["THEME_PATHS"] = [os.path.join(TESTS, "morethemes")]
        flask_themes2.Themes(app, app_identifier="testing")

        with app.test_request_context("/"):
            url = flask_themes2.static_file_url("cool", "style.css")
            genurl = url_for("_themes.static", themeid="cool", filename="style.css")
            assert url == genurl


class TestTemplates:
    def test_template_exists(self):
        flask_themes2 = import_flask_themes2()
        app = Flask(__name__)
        app.config["THEME_PATHS"] = [os.path.join(TESTS, "morethemes")]
        flask_themes2.Themes(app, app_identifier="testing")

        with app.test_request_context("/"):
            assert flask_themes2.template_exists("hello.html")
            assert flask_themes2.template_exists("_themes/cool/hello.html")
            assert not flask_themes2.template_exists("_themes/plain/hello.html")

    def test_template_exists_caches_lookups(self, monkeypatch):
        flask_themes2 = import_flask_themes2()
        app = Flask(__name__)
        app.config["THEME_PATHS"] = [os.path.join(TESTS, "morethemes")]
        flask_themes2.Themes(app, app_identifier="testing")

        with app.test_request_context("/"):
            assert not app.jinja_env.auto_reload
            calls = count_loader_lookups(app, monkeypatch)
            assert flask_themes2.template_exists("_themes/plain/hello.html") is False
            assert flask_themes2.template_exists("_themes/cool/hello.html") is True
            assert len(calls) == 2
            assert flask_themes2.template_exists("_themes/plain/hello.html") is False
            assert flask_themes2.template_exists("_themes/cool/hello.html") is True
            assert len(calls) == 2

    def test_template_exists_skips_cache_with_auto_reload(self, monkeypatch):
        flask_themes2 = import_flask_themes2()
        app = Flask(__name__)
        app.config["THEME_PATHS"] = [os.path.join(TESTS, "morethemes")]
        app.config["TEMPLATES_AUTO_RELOAD"] = True
        flask_themes2.Themes(app, app_identifier="testing")

        with app.test_request_context("/"):
            assert app.jinja_env.auto_reload
            calls = count_loader_lookups(app, monkeypatch)
            assert not flask_themes2.template_exists("_themes/plain/hello.html")
            assert not flask_themes2.template_exists("_themes/plain/hello.html")
            assert calls == ["_themes/plain/hello.html"] * 2

    def test_refresh_clears_template_cache(self, monkeypatch):
        flask_themes2 = import_flask_themes2()
        app = Flask(__name__)
        app.config["THEME_PATHS"] = [os.path.join(TESTS, "morethemes")]
        flask_themes2.Themes(app, app_identifier="testing")

        with app.test_request_context("/"):
            calls = count_loader_lookups(app, monkeypatch)
            assert not flask_themes2.template_exists("_themes/plain/hello.html")
            app.theme_manager.refresh()
            assert not flask_themes2.template_exists("_themes/plain/hello.html")
            assert calls == ["_themes/plain/hello.html"] * 2

    def test_resolve_template(self):
        flask_themes2 = import_flask_themes2()
        app = Flask(__name__)
        app.config["THEME_PATHS"] = [os.path.join(TESTS, "morethemes")]
        flask_themes2.Themes(app, app_identifier="testing")

        with app.test_request_context("/"):
            manager = app.theme_manager
            cool = manager.themes["cool"]
            assert manager.get_template("cool", "hello.html") == (
                "_themes/cool/hello.html"
            )
            assert manager.get_template(cool, "hello.html") == (
                "_themes/cool/hello.html"
            )
            assert manager.get_template("plain", "hello.html") == "hello.html"
            assert manager.get_template("plain", "missing.html") == "missing.html"

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

    def test_render_theme_template_reuses_resolution(self, monkeypatch):
        flask_themes2 = import_flask_themes2()
        app = Flask(__name__)
        app.config["THEME_PATHS"] = [os.path.join(TESTS, "morethemes")]
        flask_themes2.Themes(app, app_identifier="testing")

        with app.test_request_context("/"):
            flask_themes2.render_theme_template("plain", "hello.html")
            flask_themes2.render_theme_template("cool", "hello.html")
            calls = count_loader_lookups(app, monkeypatch)
            plainsrc = flask_themes2.render_theme_template("plain", "hello.html")
            coolsrc = flask_themes2.render_theme_template("cool", "hello.html")
            assert plainsrc.strip() == "Hello from the application"
            assert coolsrc.strip() == "Hello from Cool Blue v2."
            assert calls == []

    def test_render_theme_template_missing(self):
        flask_themes2 = import_flask_themes2()
        app = Flask(__name__)
        app.config["THEME_PATHS"] = [os.path.join(TESTS, "morethemes")]
        flask_themes2.Themes(app, app_identifier="testing")

        with app.test_request_context("/"):
            with pytest.raises(TemplateNotFound) as excinfo:
                flask_themes2.render_theme_template("cool", "missing.html")
            assert excinfo.value.name == "missing.html"
            with pytest.raises(TemplateNotFound) as excinfo:
                flask_themes2.render_theme_template(
                    "plain", "hello.html", _fallback=False
                )
            assert excinfo.value.name == "_themes/plain/hello.html"

    def test_theme_global(self):
        flask_themes2 = import_flask_themes2()
        app = Flask(__name__)
        app.config["THEME_PATHS"] = [os.path.join(TESTS, "morethemes")]
        flask_themes2.Themes(app, app_identifier="testing")

        with app.test_request_context("/"):
            assert flask_themes2.render_theme_template(
                "cool", "theme_global.html"
            ).strip() == (
                "_themes/cool/hello.html _themes/cool/hello.html "
                "_themes/cool/static.html _themes/cool/static.html"
            )
            assert flask_themes2.render_theme_template(
                "plain", "theme_global.html"
            ).strip() == (
                "hello.html _themes/plain/hello.html "
                "_themes/plain/static.html _themes/plain/static.html"
            )

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
            assert cooldata == f"Cool Blue v2, {coolurl}"

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
                    "Rendering static.html should have caused a RuntimeError"
                )

    def test_theme_include_static(self):
        flask_themes2 = import_flask_themes2()
        app = Flask(__name__)
        app.config["THEME_PATHS"] = [os.path.join(TESTS, "morethemes")]
        flask_themes2.Themes(app, app_identifier="testing")

        with app.test_request_context("/"):
            data = render_template("static_parent.html").strip()
            url = flask_themes2.static_file_url("plain", "style.css")
            assert data == f"Application, Plain, {url}"
