"""
test-themes.py
==============
This tests the Flask-Themes2 extension.
"""

import json
import logging
import os
from operator import attrgetter

import pytest
from flask import Flask
from flask import render_template
from flask import url_for
from jinja2 import FileSystemLoader
from jinja2 import TemplateNotFound

import flask_themes2

TESTS = os.path.dirname(__file__)


def make_theme(root, identifier, hello):
    path = root / identifier
    (path / "templates").mkdir(parents=True)
    (path / "static").mkdir()
    info = {
        "application": "testing",
        "identifier": identifier,
        "name": identifier.title(),
        "author": "Tests",
    }
    (path / "info.json").write_text(json.dumps(info))
    (path / "templates" / "hello.html").write_text(hello)
    return path


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
        path = os.path.join(TESTS, "themes", "plain")
        plain = flask_themes2.Theme(path)
        assert plain.license_text.strip() == "The license."


class TestLoaders:
    def test_load_themes_from(self):
        path = os.path.join(TESTS, "themes")
        themes_iter = flask_themes2.load_themes_from(path)
        themes = sorted(themes_iter, key=attrgetter("identifier"))
        assert themes[0].identifier == "cool"
        assert themes[1].identifier == "notthis"
        assert themes[2].identifier == "plain"

    def test_packaged_themes_loader(self):
        app = Flask(__name__)
        themes_iter = flask_themes2.packaged_themes_loader(app)
        themes = sorted(themes_iter, key=attrgetter("identifier"))
        assert themes[0].identifier == "cool"
        assert themes[1].identifier == "notthis"
        assert themes[2].identifier == "plain"

    def test_theme_paths_loader(self):
        app = Flask(__name__)
        app.config["THEME_PATHS"] = [os.path.join(TESTS, "morethemes")]
        themes = list(flask_themes2.theme_paths_loader(app))
        assert themes[0].identifier == "cool"

    def test_load_themes_from_warns_about_broken_themes(self, tmp_path, caplog):
        make_theme(tmp_path, "good", "")
        (tmp_path / "notatheme").mkdir()
        broken = make_theme(tmp_path, "broken", "")
        (broken / "info.json").write_text("{not json")
        incomplete = make_theme(tmp_path, "incomplete", "")
        (incomplete / "info.json").write_text('{"identifier": "incomplete"}')
        renamed = make_theme(tmp_path, "renamed", "")
        info = json.loads((renamed / "info.json").read_text())
        (renamed / "info.json").write_text(json.dumps(info | {"identifier": "other"}))

        with caplog.at_level(logging.WARNING, logger="flask_themes2"):
            themes = list(flask_themes2.load_themes_from(tmp_path))

        assert [t.identifier for t in themes] == ["good"]
        messages = "\n".join(caplog.messages)
        assert str(broken) in messages and "JSONDecodeError" in messages
        assert str(incomplete) in messages and "KeyError" in messages
        assert str(renamed) in messages and "'other'" in messages
        assert "notatheme" not in messages
        assert len(caplog.records) == 3


class TestSetup:
    def test_manager(self):
        app = Flask(__name__)
        manager = flask_themes2.ThemeManager(app, "testing")
        assert app.theme_manager is manager
        app.config["THEME_PATHS"] = [os.path.join(TESTS, "morethemes")]
        manager.refresh()
        themeids = sorted(manager.themes.keys())
        assert themeids == ["cool", "plain"]
        assert manager.themes["cool"].name == "Cool Blue v2"

    def test_setup_themes(self):
        app = Flask(__name__)
        app.config["THEME_PATHS"] = [os.path.join(TESTS, "morethemes")]
        flask_themes2.Themes(app, app_identifier="testing")

        assert hasattr(app, "theme_manager")
        assert "_themes" in app.blueprints
        assert "theme" in app.jinja_env.globals
        assert "theme_static" in app.jinja_env.globals

    def test_init_themes_is_a_deprecated_alias(self):
        app = Flask(__name__)
        app.config["THEME_PATHS"] = [os.path.join(TESTS, "morethemes")]
        with pytest.warns(DeprecationWarning, match="init_app"):
            flask_themes2.Themes().init_themes(app, app_identifier="testing")

        assert "_themes" in app.blueprints
        assert flask_themes2.get_theme_manager(app).app_identifier == "testing"

    def test_setup_themes_on_multiple_apps(self, tmp_path):
        (tmp_path / "cool").mkdir()
        (tmp_path / "cool" / "style.css").write_text("")
        first = Flask(__name__)
        first.config["THEME_PATHS"] = [os.path.join(TESTS, "morethemes")]
        flask_themes2.Themes(first, app_identifier="testing")
        second = Flask(__name__, static_url_path="/assets")
        flask_themes2.Themes(
            second,
            app_identifier="testing",
            static_folder=str(tmp_path),
            theme_url_prefix="/skins",
        )

        assert first.blueprints["_themes"] is not second.blueprints["_themes"]
        with first.test_request_context("/"):
            assert flask_themes2.static_file_url("cool", "style.css") == (
                "/_themes/cool/style.css"
            )
        with second.test_request_context("/"):
            assert flask_themes2.static_file_url("cool", "style.css") == (
                "/assets/skins/cool/style.css"
            )

    def test_get_helpers(self):
        app = Flask(__name__)
        app.config["THEME_PATHS"] = [os.path.join(TESTS, "morethemes")]
        flask_themes2.Themes(app, app_identifier="testing")

        with app.test_request_context("/"):
            cool = flask_themes2.get_theme_manager(app).themes["cool"]
            plain = flask_themes2.get_theme_manager(app).themes["plain"]
            assert flask_themes2.get_theme("cool") is cool
            assert flask_themes2.get_theme("plain") is plain
            tl = flask_themes2.get_themes_list()
            assert tl[0] is cool
            assert tl[1] is plain
            with pytest.raises(KeyError):
                flask_themes2.get_theme("notthis")


class TestStatic:
    def test_static_file_url(self):
        app = Flask(__name__)
        app.config["THEME_PATHS"] = [os.path.join(TESTS, "morethemes")]
        flask_themes2.Themes(app, app_identifier="testing")

        with app.test_request_context("/"):
            url = flask_themes2.static_file_url("cool", "style.css")
            genurl = url_for("_themes.static", themeid="cool", filename="style.css")
            assert url == genurl

    def test_static_file_url_passes_values_to_url_for(self):
        app = Flask(__name__)
        app.config["THEME_PATHS"] = [os.path.join(TESTS, "morethemes")]
        flask_themes2.Themes(app, app_identifier="testing")

        with app.test_request_context("/"):
            url = flask_themes2.static_file_url("cool", "style.css", v=3)
            genurl = url_for("_themes.static", themeid="cool", filename="style.css")
            assert url == f"{genurl}?v=3"

    def test_static_file_url_passes_values_when_falling_back(self, tmp_path):
        theme_path = make_theme(tmp_path, "partial", "")
        (theme_path / "static" / "own.css").write_text("")
        static_folder = tmp_path / "static"
        static_folder.mkdir()
        (static_folder / "app.css").write_text("")
        app = Flask(__name__, static_folder=str(static_folder))
        app.config["THEME_PATHS"] = [str(tmp_path)]
        flask_themes2.Themes(app, app_identifier="testing")

        with app.test_request_context("/"):
            url = flask_themes2.static_file_url("partial", "app.css", v=3)
            assert url == url_for("static", filename="app.css", v=3)

    def test_theme_static_global_passes_values_to_url_for(self):
        app = Flask(__name__)
        app.config["THEME_PATHS"] = [os.path.join(TESTS, "morethemes")]
        flask_themes2.Themes(app, app_identifier="testing")

        with app.test_request_context("/"):
            url = app.jinja_env.from_string(
                "{{ theme_static('style.css', v=3) }}"
            ).render(_theme="cool")
            assert url == flask_themes2.static_file_url("cool", "style.css", v=3)

    def test_static_file_url_falls_back_to_app_static(self, tmp_path):
        theme_path = make_theme(tmp_path, "partial", "")
        (theme_path / "static" / "own.css").write_text("")
        app_static = tmp_path / "static"
        app_static.mkdir()
        (app_static / "shared.css").write_text("")
        app = Flask(__name__, static_folder=str(app_static))
        app.config["THEME_PATHS"] = [str(tmp_path)]
        flask_themes2.Themes(app, app_identifier="testing")

        with app.test_request_context("/"):
            url = flask_themes2.static_file_url
            assert url("partial", "own.css") == "/_themes/partial/own.css"
            assert url("partial", "shared.css") == "/static/shared.css"
            assert url("partial", "shared.css", fallback=False) == (
                "/_themes/partial/shared.css"
            )

    def test_static_file_url_falls_back_with_static_folder(self, tmp_path):
        make_theme(tmp_path / "themes", "partial", "")
        shared = tmp_path / "shared"
        (shared / "partial").mkdir(parents=True)
        (shared / "partial" / "own.css").write_text("")
        app_static = tmp_path / "static"
        app_static.mkdir()
        app = Flask(__name__, static_folder=str(app_static))
        app.config["THEME_PATHS"] = [str(tmp_path / "themes")]
        flask_themes2.Themes(app, app_identifier="testing", static_folder=str(shared))

        with app.test_request_context("/"):
            url = flask_themes2.static_file_url
            assert url("partial", "own.css") == "/static/_themes/partial/own.css"
            assert url("partial", "shared.css") == "/static/shared.css"

    def test_static_exists_caches_lookups(self, tmp_path):
        theme_path = make_theme(tmp_path, "partial", "")
        app_static = tmp_path / "static"
        app_static.mkdir()
        app = Flask(__name__, static_folder=str(app_static))
        app.config["THEME_PATHS"] = [str(tmp_path)]
        flask_themes2.Themes(app, app_identifier="testing")

        with app.test_request_context("/"):
            assert not app.jinja_env.auto_reload
            url = flask_themes2.static_file_url
            assert url("partial", "late.css") == "/static/late.css"
            (theme_path / "static" / "late.css").write_text("")
            assert url("partial", "late.css") == "/static/late.css"
            flask_themes2.get_theme_manager(app).refresh()
            assert url("partial", "late.css") == "/_themes/partial/late.css"

    def test_theme_static_global_falls_back(self, tmp_path):
        make_theme(
            tmp_path,
            "partial",
            "{{ theme_static('shared.css') }} "
            "{{ theme_static('shared.css', fallback=false) }}",
        )
        app_static = tmp_path / "static"
        app_static.mkdir()
        app = Flask(__name__, static_folder=str(app_static))
        app.config["THEME_PATHS"] = [str(tmp_path)]
        flask_themes2.Themes(app, app_identifier="testing")

        with app.test_request_context("/"):
            assert flask_themes2.render_theme_template("partial", "hello.html") == (
                "/static/shared.css /_themes/partial/shared.css"
            )


class TestTemplates:
    def test_template_exists(self):
        app = Flask(__name__)
        app.config["THEME_PATHS"] = [os.path.join(TESTS, "morethemes")]
        flask_themes2.Themes(app, app_identifier="testing")

        with app.test_request_context("/"):
            assert flask_themes2.template_exists("hello.html")
            assert flask_themes2.template_exists("_themes/cool/hello.html")
            assert not flask_themes2.template_exists("_themes/plain/hello.html")

    def test_template_exists_caches_lookups(self, monkeypatch):
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
        app = Flask(__name__)
        app.config["THEME_PATHS"] = [os.path.join(TESTS, "morethemes")]
        flask_themes2.Themes(app, app_identifier="testing")

        with app.test_request_context("/"):
            calls = count_loader_lookups(app, monkeypatch)
            assert not flask_themes2.template_exists("_themes/plain/hello.html")
            flask_themes2.get_theme_manager(app).refresh()
            assert not flask_themes2.template_exists("_themes/plain/hello.html")
            assert calls == ["_themes/plain/hello.html"] * 2

    def test_refresh_reloads_edited_templates(self, tmp_path):
        theme_path = make_theme(tmp_path, "edited", "Before")
        app = Flask(__name__)
        app.config["THEME_PATHS"] = [str(tmp_path)]
        flask_themes2.Themes(app, app_identifier="testing")

        with app.test_request_context("/"):
            assert not app.jinja_env.auto_reload

            def render():
                return flask_themes2.render_theme_template("edited", "hello.html")

            assert render() == "Before"
            (theme_path / "templates" / "hello.html").write_text("After")
            assert render() == "Before"
            flask_themes2.get_theme_manager(app).refresh()
            assert render() == "After"

    def test_resolve_template(self):
        app = Flask(__name__)
        app.config["THEME_PATHS"] = [os.path.join(TESTS, "morethemes")]
        flask_themes2.Themes(app, app_identifier="testing")

        with app.test_request_context("/"):
            manager = flask_themes2.get_theme_manager(app)
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
        app = Flask(__name__)
        app.config["THEME_PATHS"] = [os.path.join(TESTS, "morethemes")]
        flask_themes2.Themes(app, app_identifier="testing")

        with app.test_request_context("/"):
            src = app.blueprints["_themes"].jinja_loader.get_source(
                app.jinja_env, "_themes/cool/hello.html"
            )
            assert src[0].strip() == "Hello from Cool Blue v2."

    def test_render_theme_template(self):
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
        app = Flask(__name__)
        app.config["THEME_PATHS"] = [os.path.join(TESTS, "morethemes")]
        flask_themes2.Themes(app, app_identifier="testing")

        with app.test_request_context("/"):
            with pytest.raises(RuntimeError):
                render_template("static.html")

    def test_theme_include_static(self):
        app = Flask(__name__)
        app.config["THEME_PATHS"] = [os.path.join(TESTS, "morethemes")]
        flask_themes2.Themes(app, app_identifier="testing")

        with app.test_request_context("/"):
            data = render_template("static_parent.html").strip()
            url = flask_themes2.static_file_url("plain", "style.css")
            assert data == f"Application, Plain, {url}"
