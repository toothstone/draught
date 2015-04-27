#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Drupalport auf Python im Zuge der Entwicklung von Pycroft.
Erstellt am 02.03.2014 von Dominik Pataky pataky@wh2.tu-dresden.de
"""

from flask import Flask, render_template, request, redirect, \
    url_for, flash, session
from flask_babel import gettext, get_locale
from flask_login import LoginManager, current_user, login_user, \
    logout_user
from sqlalchemy.exc import OperationalError
from ldap import SERVER_DOWN

from babel import Locale
from .babel import babel, possible_locales
from draught.blueprints.news import bp_news
from draught.flatpages import cf_pages
from draught.blueprints import bp_usersuite, bp_pages, bp_documents, \
    bp_features
from draught.forms import flash_formerrors, LoginForm
from draught.utils.database_utils import query_trafficdata, \
    query_gauge_data, user_id_from_ip
from draught.utils.exceptions import UserNotFound, PasswordInvalid, \
    ForeignIPAccessError
from draught.utils.ldap_utils import User, authenticate

from werkzeug.routing import IntegerConverter as BaseIntegerConverter


class IntegerConverter(BaseIntegerConverter):
    """Modification of the standard IntegerConverter which does not support
    negative values. See
    http://werkzeug.pocoo.org/docs/0.10/routing/#werkzeug.routing.IntegerConverter
    """
    regex = r'-?\d+'


app = Flask('draught')

app.url_map.converters['int'] = IntegerConverter
login_manager = LoginManager()


def init_app():
    login_manager.init_app(app)
    babel.init_app(app)
    babel.localeselector(babel_selector)
    cf_pages.init_app(app)
    # Blueprints
    app.register_blueprint(bp_features)
    app.register_blueprint(bp_usersuite)
    app.register_blueprint(bp_pages)
    app.register_blueprint(bp_documents)
    app.register_blueprint(bp_news)

    if not app.debug:
        app.config.setdefault('LOG_MAX_BYTES', 1024**2)
        app.config.setdefault('LOG_BACKUP_COUNT', 10)
        import logging
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            app.config['LOG_FILE'],
            maxBytes=app.config['LOG_MAX_BYTES'],
            backupCount=app.config['LOG_BACKUP_COUNT'])
        file_handler.setLevel(logging.WARNING)
        app.logger.addHandler(file_handler)


    # global jinja variables
    app.jinja_env.globals.update(
        cf_pages=cf_pages,
        traffic=query_gauge_data,
        get_locale=get_locale,
        possible_locales=possible_locales,
    )


def errorpage(e):
    if e.code in (404,):
        flash(gettext(u"Seite nicht gefunden!"), "warning")
    elif e.code in (401, 403):
        flash(gettext(
            u"Du hast nicht die notwendigen Rechte um die Seite zu sehen!"),
            "warning")
    else:
        flash(gettext(u"Es ist ein Fehler aufgetreten!"), "error")
    return redirect(url_for("index"))


app.register_error_handler(401, errorpage)
app.register_error_handler(403, errorpage)
app.register_error_handler(404, errorpage)


@app.errorhandler(OperationalError)
def exceptionhandler_sql(ex):
    """Handles global MySQL errors (server down).
    """
    flash(gettext("Verbindung zum SQL-Server konnte nicht hergestellt werden!"),
          "error")
    # todo check if infinite redirection might still occur
    # Proviously, requesting `/` w/o having a connection to the mysql database
    # would result in an infinite loop of redirects to `/` since
    # OperationalError is being handled globally.
    # In the latter case, the cause was the request of the traffic chart data.
    # A quick fix was catching it and returning an error status.
    return redirect(url_for('index'))


@app.errorhandler(SERVER_DOWN)
def exceptionhandler_ldap(ex):
    """Handles global LDAP SERVER_DOWN exceptions.
    The session must be reset, because if the user is logged in and the server
    fails during his session, it would cause a redirect loop.
    This also resets the language choice, btw.

    The alternative would be a try-except catch block in load_user, but login
    also needs a handler.
    """
    session.clear()
    flash(gettext(
        "Verbindung zum LDAP-Server konnte nicht hergestellt werden!"),
        "error"
    )
    return redirect(url_for('index'))


@login_manager.user_loader
def load_user(username):
    """Loads a User object from/into the session at every request
    """
    return User.get(username)


def babel_selector():
    """Tries to get the language setting from the current session cookie.
    If this fails (if it is not set) it first checks if a language was
    submitted as an argument ('/page?lang=de') and if not, the best matching
    language out of the header accept-language is chosen and set.
    """

    if 'locale' in request.args and Locale(
            request.args['locale']) in possible_locales():
        session['locale'] = request.args['locale']
    elif not session.get('locale'):
        langs = []
        for lang in possible_locales():
            langs.append(lang.language)
        session['locale'] = request.accept_languages.best_match(langs)

    return session.get('locale')


@app.route("/language/<string:lang>")
def set_language(lang='de'):
    """Set the session language via URL
    """
    session['locale'] = lang
    return redirect(request.referrer)


@app.route('/index.php')
@app.route('/')
def index():
    return redirect(url_for("news.display"))

#
# @app.route("/login", methods=['GET', 'POST'])
# def login():
#     """Login page for users
#     """
#     form = LoginForm()
#
#     if form.validate_on_submit():
#         username = form.username.data
#         password = form.password.data
#
#         try:
#             user = authenticate(username, password)
#         except UserNotFound:
#             flash(gettext(u"Nutzer nicht gefunden!"), "error")
#         except PasswordInvalid:
#             flash(gettext(u"Passwort war inkorrekt!"), "error")
#         else:
#             if isinstance(user, User):
#                 login_user(user)
#     elif form.is_submitted():
#         flash_formerrors(form)
#
#     if current_user.is_authenticated():
#         return redirect(url_for('usersuite.usersuite'))
#
#     return render_template('login.html', form=form)
#
#
# @app.route("/logout")
# def logout():
#     logout_user()
#     return redirect(url_for("index"))
#
