#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
from sqlalchemy import create_engine

from exceptions import DBQueryEmpty
from config import *
from utils import timestamp_from_timetag, timetag_from_timestamp


db_atlantis = create_engine('mysql+mysqldb://{0}:{1}@{2}:3306/netusers'.format(
    DB_ATLANTIS_USER, DB_ATLANTIS_PASSWORD, DB_ATLANTIS_HOST), echo=False)

db_helios = create_engine('mysql+mysqldb://{0}:{1}@{2}:3306/'.format(
    DB_HELIOS_USER, DB_HELIOS_PASSWORD, DB_HELIOS_HOST), echo=False)


def sql_query(query, args=(), database=db_atlantis):
    """Prepare and execute a raw sql query.
    'args' is a tuple needed for string replacement.
    """
    conn = database.connect()
    result = conn.execute(query, args)
    conn.close()
    return result


def query_userinfo(username):
    """Executes select query for the username and returns a prepared dict.

    * Dormitory IDs in Mysql are from 1-11, so we map to 0-10 with "x-1".

    Returns "-1" if a query result was empty (None), else
    returns the prepared dict.
    """
    user = sql_query(
        "SELECT nutzer_id, wheim_id, etage, zimmernr, status "
        "FROM nutzer "
        "WHERE unix_account = %s",
        (username,)
    ).fetchone()

    if not user:
        raise DBQueryEmpty

    computer = sql_query(
        "SELECT c_etheraddr, c_ip, c_hname, c_alias "
        "FROM computer "
        "WHERE nutzer_id = %s",
        (user['nutzer_id'])
    ).fetchone()

    if not computer:
        raise DBQueryEmpty

    user = {
        'id': user['nutzer_id'],
        'address': u"{0} / {1} {2}".format(
            dormitories[user['wheim_id'] - 1],
            user['etage'],
            user['zimmernr']
        ),
        'status': status[user['status']],
        'ip': computer['c_ip'],
        'mac': computer['c_etheraddr'].upper(),
        'hostname': computer['c_hname'],
        'hostalias': computer['c_alias']
    }

    return user


def query_trafficdata(ip):
    """Query traffic input/output for IP
    """
    userid = sql_query(
        "SELECT nutzer_id "
        "FROM computer "
        "WHERE c_ip = %s",
        (ip,)
    ).fetchone()

    if not userid:
        raise DBQueryEmpty

    trafficdata = sql_query(
        "SELECT t.timetag - %(today)s AS day, input, output, amount "
        "FROM traffic.tuext AS t "
        "LEFT OUTER JOIN credit AS c ON t.timetag = c.timetag "
        "WHERE ip = %(ip)s AND c.user_id = %(uid)s "
        "AND t.timetag BETWEEN %(weekago)s AND %(today)s "
        "ORDER BY 'day' DESC ",
        {'today': timetag_from_timestamp(),
         'weekago': timetag_from_timestamp() - 6,
         'ip': ip,
         'uid': userid['nutzer_id']}
    ).fetchall()

    if not trafficdata:
        raise DBQueryEmpty

    traffic = {'history': [], 'credit': 0}

    for i in trafficdata:
        day = datetime.date.fromtimestamp(
            timestamp_from_timetag(timetag_from_timestamp() + i['day'])
        ).strftime('%w')

        (input, output, credit) = (round(i[param] / 1024.0, 2)
                                   for param in ['input', 'output', 'amount'])

        traffic['history'].append((weekdays[day], input, output, credit))

    traffic['credit'] = (lambda d: d[3] - d[1] - d[2])(traffic['history'][-1])

    return traffic


def update_macaddress(ip, oldmac, newmac):
    """Update a MAC address in computer table.

    TODO: check, if 'LIMIT 1' causes problems (sqlalchemy says
    "Warning: Unsafe statement")
    """
    sql_query(
        "UPDATE computer "
        "SET c_etheraddr = %s "
        "WHERE c_ip = %s "
        "AND c_etheraddr = %s "
        "LIMIT 1",
        (newmac.lower(), ip, oldmac)
    )


def user_has_mysql_db(username):
    """Returns true if a database with the given name exists on
    helios-userdatabase, otherwise false.
    """
    userdb = sql_query(
        "SELECT SCHEMA_NAME "
        "FROM INFORMATION_SCHEMA.SCHEMATA "
        "WHERE SCHEMA_NAME = %s",
        (username,),
        database=db_helios
    ).fetchone()

    if userdb is not None:
        return True
    return False


def create_mysql_userdatabase(username, password):
    """A user specific database on helios is going to be created.
    """
    sql_query(
        "CREATE DATABASE "
        "IF NOT EXISTS `%s`" % username,
        database=db_helios
    )

    change_mysql_userdatabase_password(username, password)


def change_mysql_userdatabase_password(username, password):
    """This changes a user password for the helios MySQL-database.
    """
    user = sql_query(
        "SELECT user "
        "FROM mysql.user "
        "WHERE user = %s",
        (username,),
        database=db_helios
    ).fetchall()

    if not user:
        sql_query(
            "CREATE USER %s@'10.1.7.%%' "
            "IDENTIFIED BY %s",
            (username, password),
            database=db_helios
        )
    else:
        sql_query(
            "SET PASSWORD "
            "FOR %s@'10.1.7.%%' = PASSWORD(%s)",
            (username, password),
            database=db_helios
        )

    sql_query(
        "GRANT SELECT, INSERT, UPDATE, DELETE, ALTER, CREATE, DROP, INDEX, LOCK TABLES "
        "ON `%s`.* "
        "TO %%s@'10.1.7.%%%%'" % username,
        (username,),
        database=db_helios
    )


def drop_mysql_userdatabase(username):
    """This removes a userdatabase on helios.
    """
    sql_query(
        "DROP DATABASE "
        "IF EXISTS `%s`" % username,
        database=db_helios
    )

    sql_query(
        "DROP USER %s@'10.1.7.%%'",
        (username,),
        database=db_helios
    )
