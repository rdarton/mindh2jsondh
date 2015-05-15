"""

    dbhelper.py

    Database helper functions for the mindh2jsondh application.

    For more information see: https://github.com/cokrzys/mindh2jsondh

    Copyright (C) 2015 cokrzys

    Permission is hereby granted, free of charge, to any person
    obtaining a copy of this software and associated documentation
    files (the "Software"), to deal in the Software without
    restriction, including without limitation the rights to use,
    copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the
    Software is furnished to do so, subject to the following
    conditions:

    The above copyright notice and this permission notice shall be
    included in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
    OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
    NON-INFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
    HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
    WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
    OTHER DEALINGS IN THE SOFTWARE.

"""

import psycopg2
import point3d

def get_scalar_string(connection, sql, default = None):
    #------------------------------------------------------------------------------
    """
    Get a scalar string value from a PostgreSQL database.
    """
    ret = default
    try:
        cur = connection.cursor()
        cur.execute(sql)
        row = cur.fetchone()
        if row != None:
            ret = row[0]
    except psycopg2.DatabaseError, e:
        print 'ERROR: %s' % e
    return ret

def get_scalar_integer(connection, sql, default):
    #------------------------------------------------------------------------------
    """
    Get a scalar integer value from a PostgreSQL database.
    """
    ret = default
    str = get_scalar_string(connection, sql, None)
    if str != None:
        ret = int(str)
    return ret

def get_scalar_float(connection, sql, default):
    #------------------------------------------------------------------------------
    """
    Get a scalar float value from a PostgreSQL database.
    """
    ret = default
    str = get_scalar_string(connection, sql, None)
    if str != None:
        ret = float(str)
    return ret

def get_point3d(connection, sql):
    #------------------------------------------------------------------------------
    """
    Read a 3d point from the database.
    """
    ret = point3d.Point3d()
    try:
        cur = connection.cursor()
        cur.execute(sql)
        row = cur.fetchone()
        if row != None:
            ret.x = float(row[0])
            ret.y = float(row[1])
            ret.z = float(row[2])
    except psycopg2.DatabaseError, e:
        print 'ERROR: %s' % e
    return ret

def get_rowid_sql_or_null(table, field, value):
    #------------------------------------------------------------------------------
    """
    Get a portion of an insert statement to get the rowid for a lookup table.
    For example returns "(SELECT rowid FROM std.record_status WHERE name = 'Active')"
    """
    sql = 'NULL'
    if value != None and len(value.strip()) > 0:
        sql = "(SELECT rowid FROM {table} WHERE {field} = '{value}')" \
            .format(table=table, field=field, value=value.strip())
    return sql

def get_string_or_null(str):
    #------------------------------------------------------------------------------
    """
    Get a quote delimited string to use in a SQL statement or NULL if the
    string does not exist or is empty.
    """
    if str != None and len(str.strip()) > 0:
        return "'" + str.strip() + "'"
    else:
        return "NULL"

def get_numeric_or_null(value, num_decimals, null_value):
    #------------------------------------------------------------------------------
    """
    Get a string representation of a number or a NULL if the value does not exist.
    """
    if value != None and value != null_value:
        return get_string_or_null("{num:.{decimals}f}".format(num=float(value), decimals=num_decimals))
    else:
        return "NULL"

def execute_query(connection, sql, data):
    #------------------------------------------------------------------------------
    try:
        cur = connection.cursor()
        cur.execute(sql, data)
        connection.commit()
        return True
    except psycopg2.DatabaseError, e:
        if connection:
            connection.rollback()
        print 'ERROR: %s' % e
    return False



