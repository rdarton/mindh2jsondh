#!/usr/bin/python

"""

    mindh2json.py

    Export drillhole data from a mindh database to a JSON file.

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

import sys
import os
import argparse
import psycopg2

#
# ----- mindh2jsondh libraries
#
import dbhelper as db
import worker

#
# ----- setup command line arguments
#
parser = argparse.ArgumentParser(description='Export drillhole data from a mindh database to a JSON file.')
parser.add_argument("output_file", help="The name of the output file.")
parser.add_argument("-d", "--database", default="mindh",
                    help="Database to export from, mindh if not specified.")
parser.add_argument("-p", "--port", type=int, default=5432,
                    help="Port the database is on, 5432 if not specified.")
parser.add_argument("-U", "--username", default="postgres",
                    help="Username, postgres if not specified.")
parser.add_argument("-W", "--password", required=True,
                    help="Password, no default.")
parser.add_argument("-s", "--selection", required=True,
                    help="SQL selection that returns the rowids of holes to export.")
parser.add_argument("-c", "--crs", type=int, default=4326,
                    help="Output coordinate reference system, numeric EPSG code, 4326 if not specified.")
parser.add_argument("-cd", "--coordinate_decimals", type=int, default=2,
                    help="Number of decimal places for coordinates, 2 if not specified.")
parser.add_argument("-n", "--name", default="mindh2jsondh",
                    help="Project name, mindh2jsondh if not specified.")
parser.add_argument("-desc", "--description",
                    help="Project description.")
parser.add_argument("-a", "--analytes",
                    help="A comma separated list of analytes.")
parser.add_argument("-zo", "--zero_origin", help="Zero the origin, when set the bounding box minimum XY is set at 0,0 and the coordinates are shifted accordingly.", action="store_true")
parser.add_argument("-v", "--verbose", help="Verbose messages.", action="store_true")
args = parser.parse_args()

#
# ----- show args
#
if args.verbose:
    print "args.database = %r" % args.database
    print "args.port = %r" % args.port
    print "args.username = %r" % args.username
    print "args.selection = %r" % args.selection
    print "args.analytes = %r" % args.analytes
    print "args.crs = %r" % args.crs
    print "args.coordinate_decimals = %r" % args.coordinate_decimals
    print "args.name = %r" % args.name
    print "args.description = %r" % args.description
    print "args.zero_origin = %r" % args.zero_origin
    print "args.verbose = %r" % args.verbose

#
# ----- open the database connection
#
try:
    con = psycopg2.connect("dbname='%s' user='%s' port='%d' password='%s'" %
                           (args.database, args.username, args.port, args.password))
except:
    print "ERROR: Unable to connect to the database."
    sys.exit()
if con:
    if args.verbose:
        print "Successfully connected to the database."
    #
    # ----- just list the number of holes to export
    #
    sql = "SELECT COUNT(rowid) FROM dh.collar WHERE rowid IN ({select})" \
            .format(select=args.selection)
    num_holes = db.get_scalar_integer(con, sql, 0)
    if args.verbose:
        print "%r hole(s) found to export." % num_holes
    #
    #
    #
    if num_holes > 0:
        w = worker.Worker()
        w.start_export(args, con);
    #
    # ----- close the database connection
    #
    con.close()
else:
    print "ERROR: Connection not established."


