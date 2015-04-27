#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
all configuration options and dicts of external
information (dormitory mapping etc.)
Project-specific options should be included in the `config_local.py`,
which is a file not tracked in git containing IPs, user names, passwords, etc.
"""

from flask.ext.babel import gettext

FLASK_SECRET_KEY = "development key!"

# Mail configuration
MAILSERVER_HOST = "127.0.0.1"
MAILSERVER_PORT = 25

# LDAP configuration
LDAP_HOST = "127.0.0.1"
LDAP_PORT = 1111
LDAP_SEARCH_BASE = ""

# MySQL configuration
DB_ATLANTIS_HOST = "127.0.0.1"
DB_ATLANTIS_USER = ""
DB_ATLANTIS_PASSWORD = ""

# MySQL Helios configuration
DB_HELIOS_HOST = "127.0.0.1"
DB_HELIOS_PORT = 1111
DB_HELIOS_USER = ""
DB_HELIOS_PASSWORD = ""

SQL_TIMEOUT = 15

weekdays = {
    '0': gettext('Sonntag'),
    '1': gettext('Montag'),
    '2': gettext('Dienstag'),
    '3': gettext('Mittwoch'),
    '4': gettext('Donnerstag'),
    '5': gettext('Freitag'),
    '6': gettext('Samstag')
}

# Languages
languages = {
    'de': 'Deutsch',
    'en': 'English'
}

# Bus & tram stops
busstops = [
    "Zellescher Weg",
    "Strehlener Platz",
    "Weberplatz"
]

# if local config file exists, load everything into local space.
try:
    from config_local import *
except ImportError:
    print("No local config found. Using default values.")