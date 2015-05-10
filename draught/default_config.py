#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
all configuration options and dicts of external
information (dormitory mapping etc.)
Project-specific options should be included in the `config_local.py`,
which is a file not tracked in git containing IPs, user names, passwords, etc.
"""

from flask.ext.babel import gettext

SECRET_KEY = "development key!"
FLASK_SECRET_KEY = "development key!"

LOG_FILE = 'error.log'

FLATPAGES_ROOT = ""
FLATPAGES_EXTENSION = '.md'
FLATPAGES_MARKDOWN_EXTENSIONS = [
    'sane_lists',
    'draught.utils.bootstraped_tables',
    'nl2br',
    'meta',
    'attr_list'
]

LOGGING_CONFIG_LOCATION = "draught/default_log_config"

# Mail configuration
MAILSERVER_HOST = "127.0.0.1"
MAILSERVER_PORT = 25

WEEKDAYS = {
    '0': gettext('Sonntag'),
    '1': gettext('Montag'),
    '2': gettext('Dienstag'),
    '3': gettext('Mittwoch'),
    '4': gettext('Donnerstag'),
    '5': gettext('Freitag'),
    '6': gettext('Samstag')
}

# Languages
LANGUAGES = {
    'de': 'Deutsch',
    'en': 'English'
}

# Bus & tram stops
BUSSTOPS = [
    "Zellescher Weg",
    "Strehlener Platz",
    "Weberplatz"
]

