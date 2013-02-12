=============
Flask-Themes2
=============
.. currentmodule:: flask.ext.themes2

Flask-Themes2 makes it easy for your application to support a wide range of
appearances.

.. contents::
   :local:
   :backlinks: none


Writing Themes
==============
A theme is simply a folder containing static media (like CSS files, images,
and JavaScript) and Jinja2 templates, with some metadata. A theme folder
should look something like this:

.. sourcecode:: text

    my_theme
    ├── info.json
    ├── license.txt
    ├── static
    │   └── style.css
    └── templates
        ├── layout.html
        └── index.html

The ``info.json`` file contains the theme's metadata, so that the application
can provide a nice switching interface if necessary. ``license.txt`` is
optional and contains the full text of the theme's license. ``static`` is
served directly to clients, and ``templates`` contains the Jinja2 template
files.

Note that exactly what templates you need to create will vary between
applications. Check the application's docs (or source code) to see what you
need.


Writing Templates
-----------------
Flask uses the Jinja2 template engine, so you should read `its documentation`_
to learn about the actual syntax of the templates.

All templates loaded from a theme will have a global function named `theme`
available to look up the theme's templates. For example, if you want to
extend, import, or include another template from your theme, you can use
``theme(template_name)``, like this:

.. sourcecode:: html+jinja

    {% extends theme('layout.html') %}
    {% from theme('_helpers.html') import form_field %}

If the template you requested doesn't exist within the theme, it will fall
back to using the application's template. If you pass `false` as the second
parameter, it will only return the theme's template.

.. sourcecode:: html+jinja

    {% include theme('header.html', false) %}

You can still import/include templates from the application, though. Just use
the tag without calling `theme`.

.. sourcecode:: html+jinja

    {% from '_helpers.html' import link_to %}
    {% include '_jquery.html' %}

You can also get the URL for the theme's media files with the `theme_static`
function:

.. sourcecode:: html+jinja

    <link rel=stylesheet href="{{ theme_static('style.css') }}">

If you want to get information about the currently active theme, you can do
that with the `theme_get_info` function:

.. sourcecode:: html+jinja

    This theme is <a href="{{ theme_get_info('website'}}">
      <b>{{ theme_get_info('name') }}</b>
    </a>

If you want to include things which might or might not be in your theme, you can do
something like this:

.. sourcecode:: html+jinja

    This theme is <a href="{{ theme_get_info('website'}}">
      <b>{{ theme_get_info('name') }}</b>
      {%- if theme_get_info('version') != "" %}
        <b>({{ theme_get_info('version') }})</b>
      {% endif -%}
    </a>

By default, this will first check if that's direct theme information, then it
will check if it's part of the ``options`` dictionary of the theme.

.. _its documentation: http://jinja.pocoo.org/2/documentation/templates


``info.json`` Fields
--------------------
``application`` : required
    This is the application's identifier. Exactly what identifier you need to
    use varies between applications.

``identifier`` : required
    The theme's identifier. It should be a Python identifier (starts with a
    letter or underscore, the rest can be letters, underscores, or numbers)
    and should match the name of the theme's folder.

``name`` : required
    A human-readable name for the theme.

``author`` : required
    The name of the theme's author, that is, you. It does not have to include
    an e-mail address, and should be displayed verbatim.

``description``
    A description of the theme in a few sentences. If you can write multiple
    languages, you can include additional fields in the form
    ``description_lc``, where ``lc`` is a two-letter language code like ``es``
    or ``de``. They should contain the description, but in the indicated
    language.

``website``
    The URL of the theme's Web site. This can be a Web site specifically for
    this theme, Web site for a collection of themes that includes this theme,
    or just the author's Web site.

``license``
    A simple phrase indicating your theme's license, like ``GPL``,
    ``MIT/X11``, ``Public Domain``, or ``Creative Commons BY-SA 3.0``. You
    can put the full license's text in the ``license.txt`` file.

``license_url``
    If you don't want to include the full text in the ``license.txt`` file,
    you can include a URL for a Web site where the text can be viewed. This is
    good for long licenses like the GPL or Creative Commons licenses.

``preview``
    A preview image for the theme. This should be the filename for an image
    within the ``static`` directory.

``doctype``
    The version of HTML used by the theme. It can be ``html4``, ``html5``, or
    ``xhtml``. The application can use this to do things like switch the
    output format of a markup generator. (The default if this is left out is
    ``html5`` to be safe. HTML5 is used by the majority of Flask users, so
    it's best to use it.)

``version``
    This is simply to make it easier to distinguish between what version
    of your theme people are using. It's up to the theme/layout to decide
    whether or not to show this, though.

``options``
    If this is given, it should be a dictionary (object in JSON parlance)
    containing application-specific options. You will need to check the
    application's docs to see what options it uses. (For example, an
    application like a pastebin or wiki that highlights source code may
    want the theme to specify a default `Pygments`_ style in the options.)


.. _Pygments: http://pygments.org/

Tips for Theme Writers
----------------------
- Always specify a doctype.
- Remember that you have to use double-quotes with strings in JSON.
- Look at the non-theme templates provided with the application. See how they
  interact.
- Remember that most of the time, you can alter the application's appearance
  completely just by changing the layout template and the style.


Using Themes in Your Application
================================
To set up your application to use themes, you need to use `Themes` (``flask.ext.themes2.Themes``),
in one of two ways:

.. code-block:: python

    # The first way
    app = Flask(__name__)
    Themes(app, app_identifer="...")

    # The second way
    app = Flask(__name__)
    t = Themes()
    t.init_themes(app, app_identifer="...")

The first is simply a quicker way of the second, as it will automatically call `init_themes` on your app.

This does three things:

* Adds a `ThemeManager` instance to your application as `app.theme_manager`.
* Registers the ``theme`` and ``theme_static`` globals with the Jinja2
  environment.
* Registers the ``_themes`` module or blueprint (depending on the Flask version)
  to your application, by default with the URL prefix ``/_themes`` (you can
  change it).

.. warning::

   Since the "Blueprints" mechanism of Flask 0.7 causes headaches in module
   compatibility mode, `init_themes` will automatically register ``_themes``
   as a blueprint and not as a module if possible. If this causes headaches
   with your application, then you need to either (a) upgrade to Flask 0.7 or
   (b) set ``Flask<0.7`` in your requirements.txt file.


Theme Loaders
-------------
`init_themes` takes a few arguments, but the one you will probably be using
most is ``loaders``, which is a list of theme loaders to use (in order) to find
themes. The default theme loaders are:

* `packaged_themes_loader`, which looks in your application's ``themes``
  directory for themes (you can use this to ship one or two default themes
  with your application)
* `theme_paths_loader`, which looks at the `THEME_PATHS` configuration
  setting and loads themes from each folder therein

It's easy to write your own loaders, though - a loader is just a callable that
takes an application instance and returns an iterable of `Theme` instances.
You can use the `load_themes_from` helper function to yield all the valid
themes contained within a folder. For example, if your app uses an "instance
folder" like `Zine`_ that can have a "themes" directory::

    def instance_loader(app):
        themes_dir = os.path.join(app.instance_root, 'themes')
        if os.path.isdir(themes_dir):
            return load_themes_from(themes_dir)
        else:
            return ()

.. _Zine: http://zine.pocoo.org/


Rendering Templates
-------------------
Once you have the themes set up, you can call in to the theme machinery with
`render_theme_template`. It works like `render_template`, but takes a ``theme``
parameter before the template name. Also, `static_file_url` will generate a
URL to the given static file.

When you call `render_theme_template`, it sets the "active template" to the
given theme, even if you have to fall back to rendering the application's
template. That way, if you have a template like ``by_year.html`` that isn't
defined by the current theme, you can still

- extend (``{% extends theme('layout.html') %}``)
- include (``{% include theme('archive_header.html') %}``)
- import (``{% from theme('_helpers.html') import show_post %}``)

templates defined by the theme. This way, the theme author doesn't have to
implement every possible template - they can define templates like the layout,
and showing posts, and things like that, and the application-provided
templates can use those building blocks to form the more complicated pages.


Selecting Themes
----------------
How exactly you select the theme will vary between applications, so
Flask-Themes2 doesn't make the decision for you. If your app is any larger than
a few views, though, you will probably want to provide a helper function that
selects the theme based on whatever (settings, logged-in user, page) and
renders the template. For example:

.. code-block:: python

    def get_current_theme():
        if g.user is not None:
            ident = g.user.theme
        else:
            ident = current_app.config.get('DEFAULT_THEME', 'plain')
        return get_theme(ident)
    
    def render(template, **context):
        return render_theme_template(get_current_theme(), template, **context)


.. warning::
   
   Make sure that you *only* get `Theme` instances from the theme manager. If
   you need to create a `Theme` instance manually outside of a theme loader,
   that's a sign that you're doing it wrong. Instead, write a loader that can
   load that theme and pass it to `init_themes`, because if the theme is not
   loaded by the manager, then its templates and static files won't be
   available, which will usually lead to your application breaking.


Tips for Application Programmers
--------------------------------
- Provide default templates, preferably for everything. Use simple, unstyled
  HTML.
- If you find yourself repeating design elements, put them in a macro in a
  separate template. That way, theme authors can override them more easily.
- Put class names or IDs on any elements that the theme author may want to
  style. (And by that I mean all of them.) That way they won't have to
  override the template unnecessarily if all they want to do is right-align
  the meta information.


API Documentation
=================
This API documentation is automatically generated from the source code.

.. autoclass:: Themes
  :members:
  :special-members:
  :exclude-members: __weakref__

.. autoclass:: Theme
  :members:

.. autofunction:: render_theme_template

.. autofunction:: static_file_url

.. autofunction:: get_theme

.. autofunction:: get_themes_list


Loading Themes
--------------
.. autoclass:: ThemeManager
   :members:

.. autofunction:: packaged_themes_loader

.. autofunction:: theme_paths_loader

.. autofunction:: load_themes_from
