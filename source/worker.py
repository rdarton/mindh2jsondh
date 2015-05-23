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
import re
import psycopg2
import dbhelper as db
import jsonfile
import jsondh
import point3d
import mindhcollar

class Worker:

    something = 1
    con = None
    json = None
    selection = None
    verbose = False
    json_file = None
    analytes_list = []

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
        sql = """
                SELECT MAX(max_depth_meters)
                FROM dh.collar WHERE rowid IN ({select})
            """.format(select=self.selection)
        max_depth = db.get_scalar_float(self.con, sql, 0.0)
        self.json.expand_box(max_depth)
        if self.verbose:
            print "Maximum hole depth = %r" % max_depth

    def start_main_loop(self):
    #------------------------------------------------------------------------------
        sql = """
                SELECT rowid, name, max_depth_meters,
                  ST_X(ST_Transform(geom, {crs})),
                  ST_Y(ST_Transform(geom, {crs})),
                  ST_Z(ST_Transform(geom, {crs}))
                FROM dh.collar WHERE rowid IN ({select})
            """.format(crs=self.json.crs, select=self.selection)
        #
        # ----- open cursor and loop through holes to export
        #
        try:
            cur = self.con.cursor()
            cur.execute(sql)
            while True:
                row = cur.fetchone()
                if row == None:
                    break
                if self.verbose:
                    print "Processing hole: %r" % row[1]
                col = mindhcollar.Mindhcollar()
                col.rowid = int(row[0])
                col.name = row[1]
                col.depth = row[2]
                col.location.x = float(row[3])
                col.location.y = float(row[4])
                col.location.z = float(row[5])
                col.read_downhole_surveys(self.con)
                col.add_dummy_surveys()
                col.desurvey_midpoint_split()
                col.read_assays(self.con, self.analytes_list)
                self.json.write_hole(self.json_file, col)
        except psycopg2.DatabaseError, e:
            print 'ERROR: %s' % e

    def start_export(self, args, connection):
    #------------------------------------------------------------------------------
        """
        Start the data export.
        """
        if args.verbose:
            print "Starting export."
        self.con = connection
        self.selection = args.selection
        self.verbose = args.verbose
        self.json = jsondh.Jsondh()
        self.json.name = args.name
        self.json.description = args.description
        self.json.crs = args.crs
        self.json.coordinate_decimals = args.coordinate_decimals
        #
        # ----- analytes to export
        #
        # self.analytes_list = args.analytes.split(",")
        self.analytes_list =re.split(r'[,\s]\s*', args.analytes)
        if self.verbose:
            print "%r analytes to export." % len(self.analytes_list)
            for analyte in self.analytes_list:
                print "Analyte = [%r]" % analyte
        #
        # ----- create output file and move on
        #
        self.json_file = jsonfile.Jsonfile()
        self.json_file.open(args.output_file)
        #
        # ----- project box and write header
        #
        self.read_project_box()
        self.json.write_header(self.json_file)
        self.json.start_holes_section(self.json_file)
        #
        # -----
        #
        self.start_main_loop()
        self.json.end_holes_section(self.json_file)
        self.json.write_footer(self.json_file)
        self.json_file.close()






