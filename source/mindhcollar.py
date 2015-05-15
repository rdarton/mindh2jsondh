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

class Mindhcollar:

    rowid = -1
    name = ''
    location = point3d.Point3d()
    depth = 0.0
    survey_list = []

    def init(self):
    #------------------------------------------------------------------------------
        self.rowid = -1
        self.name = ''
        self.location.zero()
        self.depth = 0.0

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
                self.survey_list.append(svy)
        except psycopg2.DatabaseError, e:
            print 'ERROR: %s' % e

