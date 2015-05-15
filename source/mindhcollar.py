"""

    mindhcollar.py

    Contains a collar from a mindh database.

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
import point3d
import mindhsurvey
import mindhresultset

class Mindhcollar:

    def __init__(self):
    #------------------------------------------------------------------------------
        self.rowid = -1
        self.name = ''
        self.location = point3d.Point3d()
        self.depth = 0.0
        self.surveys_list = []
        self.assays_list = []

    def read_downhole_surveys(self, connection):
    #------------------------------------------------------------------------------
        sql = """
                SELECT rowid, depth, azimuth, inclination
                FROM dh.survey
                WHERE collar_rowid_fk = {rowid}
                ORDER BY depth
            """.format(rowid=self.rowid)
        #
        # ----- open cursor and loop through the surveys
        #
        try:
            cur = connection.cursor()
            cur.execute(sql)
            while True:
                row = cur.fetchone()
                if row == None:
                    break
                svy = mindhsurvey.Mindhsurvey()
                svy.rowid = int(row[0])
                svy.depth = float(row[1])
                svy.azimuth = float(row[2])
                svy.inclination = float(row[3])
                self.surveys_list.append(svy)
        except psycopg2.DatabaseError, e:
            print 'ERROR: %s' % e

    def read_assays(self, connection, analytes_list):
    #------------------------------------------------------------------------------
        if len(analytes_list) > 0:
            for analyte in analytes_list:
                rs = mindhresultset.Mindhresultset()
                rs.name = analyte
                rs.read_results(connection, self.rowid)
                self.assays_list.append(rs)

    def add_dummy_surveys(self):
    #------------------------------------------------------------------------------
        #
        # ----- add new survey at the top of the hole
        #
        if len(self.surveys_list) > 0 and self.surveys_list[0].depth != 0:
            svy = mindhsurvey.Mindhsurvey()
            svy.rowid = 0
            svy.depth = 0.0
            svy.azimuth = self.surveys_list[0].azimuth
            svy.inclination = self.surveys_list[0].inclination
            self.surveys_list.insert(0, svy)

    def desurvey_straight_line(self):
    #------------------------------------------------------------------------------
        if len(self.surveys_list) > 0 and self.surveys_list[0].depth == 0:
            self.surveys_list[0].location.x = self.location.x
            self.surveys_list[0].location.y = self.location.y
            self.surveys_list[0].location.z = self.location.z
        if len(self.surveys_list) > 1 and self.surveys_list[1].depth == self.depth and self.surveys_list[1].inclination == -90:
            self.surveys_list[1].location.x = self.location.x
            self.surveys_list[1].location.y = self.location.y
            self.surveys_list[1].location.z = self.location.z - float(self.depth)




