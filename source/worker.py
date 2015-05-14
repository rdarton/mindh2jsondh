"""

    worker.py

    Worker class to manage an export for the mindh2jsondh application.

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

import os
import sys
import psycopg2
import dbhelper as db
import jsonfile
import jsondh
import point3d

class Worker:

    something = 1
    con = None
    json = None
    selection = None

    def get_box_sql(self, func):
    #------------------------------------------------------------------------------
        sql = """
                SELECT
                {func}(ST_X(ST_Transform(geom, {crs}))),
                {func}(ST_Y(ST_Transform(geom, {crs}))),
                {func}(ST_Z(ST_Transform(geom, {crs})))
                FROM dh.collar WHERE rowid IN ({select})
            """.format(func=func, crs=self.json.crs, select=self.selection)
        return sql

    def read_project_box(self):
    #------------------------------------------------------------------------------
        sql = self.get_box_sql('MIN')
        self.json.boxMin = db.get_point3d(self.con, sql)
        sql = self.get_box_sql('MAX')
        self.json.boxMax = db.get_point3d(self.con, sql)


    def start_export(self, args, connection):
    #------------------------------------------------------------------------------
        """
        Start the data export.
        """
        if args.verbose:
            print "Starting export."
        self.con = connection
        self.selection = args.selection
        self.crs = args.crs
        self.json = jsondh.Jsondh()
        self.json.name = args.name
        self.json.description = args.description
        self.json.crs = args.crs
        self.json.coordinate_decimals = args.coordinate_decimals
        #
        # ----- create output file and move on
        #
        jf = jsonfile.Jsonfile()
        jf.open(args.output_file)
        #
        #
        #
        self.read_project_box()
        self.json.write_header(jf)
        jf.close()






