#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
themesandbox.py
===============
A sandbox to play around with themes in.

:copyright: 2010 Matthew "LeafStorm" Frazier
:license:   MIT/X11, see LICENSE for details
"""
import yaml
from flask import (Flask, url_for, redirect, session, Markup, abort)
from flask.ext.themes2 import (setup_themes, render_theme_template, get_themes_list)
from operator import attrgetter

# default settings

DEFAULT_THEME = 'calmblue'
SECRET_KEY = 'not really secret'


# application

app = Flask(__name__)
app.config.from_object(__name__)
setup_themes(app, app_identifier='themesandbox')


# data

class Post(object):
    def __init__(self, data):
        self.slug = data['slug']
        self.body = data['body']
        self.title = data['title']
        self.created = data['created']
    
    @property
    def content(self):
        return Markup('\n\n'.join(
            '<p>%s</p>' % line for line in self.body.splitlines()
        ))


class PostStore(object):
    def __init__(self):
        self.by_date = []
        self.by_slug = {}
    
    def add_posts(self, post_data):
        posts = [Post(post) for post in post_data]
        for post in posts:
            if post.slug in self.by_slug:
                raise RuntimeError("slugs must be unique")
            self.by_slug[post.slug] = post
        self.by_date.extend(posts)
        self.by_date.sort(key=attrgetter('created'), reverse=True)


store = PostStore()

with app.open_resource('posts.yaml') as fd:
    post_data = yaml.load_all(fd)
    store.add_posts(post_data)


ABOUT_TEXT = Markup('<p>This is a demonstration of Flask-Themes2.</p>')


# themes

def render(template, **context):
    theme = session.get('theme', app.config['DEFAULT_THEME'])
    return render_theme_template(theme, template, **context)


# views

@app.route('/')
def index():
    posts = store.by_date[:3]
    return render('index.html', posts=posts)


@app.route('/archive')
def archive():
    posts = store.by_date[:]
    return render('archive.html', posts=posts)


@app.route('/post/<slug>')
def post(slug):
    post = store.by_slug.get(slug)
    if post is None:
        abort(404)
    return render('post.html', post=post)


@app.route('/about')
def about():
    return render('about.html', text=ABOUT_TEXT)


@app.route('/themes/')
def themes():
    themes = get_themes_list()
    return render('themes.html', themes=themes)


@app.route('/themes/<ident>')
def settheme(ident):
    if ident not in app.theme_manager.themes:
        abort(404)
    session['theme'] = ident
    return redirect(url_for('themes'))


if __name__ == '__main__':
    app.run(debug=True)
