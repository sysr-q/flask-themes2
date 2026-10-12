# Flask-Themes2

[docs]: https://flask-themes2.readthedocs.io/en/latest/
[GitHub]: https://github.com/sysr-q/flask-themes2

Flask-Themes2 is a fork of Spirits, which is in turn a fork of Flask-Themes.

- [Flask-Themes2](https://github.com/sysr-q/flask-themes2) maintained by Chris Carter et al.
- [Spirits](https://github.com/drewlustro/spirits) maintained by Drew Lustro
- [Flask-Themes](https://bitbucket.org/leafstorm/flask-themes) by Matthew "LeafStorm" Frazier
- Many more contributors to this fork and all others! It wouldn't be this good without you.

This provides infrastructure for themes in Flask >= 2.0.

> [!NOTE]
> Flask-Themes2 2.x requires Python 3.11 or newer.


## Installation

To install normally:
```sh
$ pip install flask-themes2
```

To install the development version from the latest commit on `master`:
```sh
$ pip install "Flask-Themes2 @ git+https://github.com/sysr-q/flask-themes2.git@master"
```

## Documentation

The documentation is on the Flask-Themes2 [docs].

## Development

If you're interested in helping, the source is available on [GitHub], feel free to contribute.

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then clone
the repository and install the project and development dependencies:

```sh
git clone https://github.com/sysr-q/flask-themes2.git
cd flask-themes2
uv sync --locked
```

Run the tests on the development Python version:

```sh
uv run --locked pytest
```

Run the full test matrix (Python 3.11–3.14), formatting and lint checks,
type checks, and documentation build:

```sh
uv python install 3.11 3.12 3.13 3.14
uv run --locked tox
```

You can also run individual checks, for example:

```sh
uv run --locked tox run -e py3.11,typing,docs
uv run --locked pre-commit run --all-files
```

## Releases

Update `__version__` in `src/flask_themes2/__init__.py`, commit the release
changes, and push them to `master`. Release tags use the plain `MAJOR.MINOR.PATCH`
format, for example `2.0.0`, without a `v` prefix or prerelease suffix.

Pushing a release tag triggers the publish workflow. It checks that the tag
matches `__version__`, runs the full test matrix and other checks, and builds and
validates the distributions before publishing to PyPI through the `publish`
environment. After successful publication, it creates a draft GitHub release
for you to add release notes and publish; pushing commits to `master` alone
does not publish a release.

