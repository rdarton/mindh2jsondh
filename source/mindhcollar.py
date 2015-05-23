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
from copy import deepcopy
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
        self.desurvey_list = []

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
        """
        Create downhole survey points from the raw surveys.

        Adds additional dummy surveys if needed at the top and bottom of the hole.  The dummy
        surveys will have the same value at the next or previous survey at the top and bottom
        of the hole respectively.  If no surveys exist for a drillhole a survey at the collar
        and Td will be created with an azimuth of 0.0 and an inclination of -90.0 (vertical down).
        """
        #
        # ----- add new dummy survey at the top of the hole
        #
        if len(self.surveys_list) > 0 and self.surveys_list[0].depth != 0:
            svy = mindhsurvey.Mindhsurvey()
            svy.rowid = 0
            svy.depth = 0.0
            svy.azimuth = self.surveys_list[0].azimuth
            svy.inclination = self.surveys_list[0].inclination
            self.surveys_list.insert(0, svy)
        #
        # ----- add new dummy survey at the end of the hole
        #
        if len(self.surveys_list) > 0 and self.surveys_list[len(self.surveys_list) - 1].depth != self.depth:
            svy = mindhsurvey.Mindhsurvey()
            svy.rowid = 0
            svy.depth = self.depth
            svy.azimuth = self.surveys_list[len(self.surveys_list) - 1].azimuth
            svy.inclination = self.surveys_list[len(self.surveys_list) - 1].inclination
            self.surveys_list.append(svy)
        #
        # ----- if no surveys assume vertical down
        #
        if len(self.surveys_list) == 0:
            svy = mindhsurvey.Mindhsurvey()
            svy.rowid = 0
            svy.depth = 0.0
            svy.azimuth = 0.0
            svy.inclination = -90.0
            self.surveys_list.append(svy)
            svy = mindhsurvey.Mindhsurvey()
            svy.rowid = 0
            svy.depth = self.depth
            svy.azimuth = 0.0
            svy.inclination = -90.0
            self.surveys_list.append(svy)

    def desurvey_midpoint_split(self):
    #------------------------------------------------------------------------------
        del self.desurvey_list[:]
        self.add_dummy_surveys()
        if len(self.surveys_list) > 0:
            #
            # ----- start at the collar
            #
            svy = deepcopy(self.surveys_list[0])
            svy.location = deepcopy(self.location)
            self.desurvey_list.append(svy)
            #
            # ----- loop through each survey
            #
            for i in range(1, len(self.surveys_list)):
                if self.surveys_list[i].azimuth == self.surveys_list[i-1].azimuth and self.surveys_list[i].inclination == self.surveys_list[i-1].inclination:
                    distance = float(self.surveys_list[i].depth) - float(self.surveys_list[i-1].depth)
                    svy = deepcopy(self.surveys_list[i])
                    svy.location = deepcopy(self.desurvey_list[len(self.desurvey_list) - 1].location)
                    svy.location.azimuth_move(svy.azimuth, svy.inclination, distance)
                    self.desurvey_list.append(svy)
                else:
                    distance = float(self.surveys_list[i].depth - self.surveys_list[i-1].depth) / 2
                    svy = deepcopy(self.surveys_list[i-1])
                    svy.location = deepcopy(self.desurvey_list[len(self.desurvey_list) - 1].location)
                    svy.location.azimuth_move(svy.azimuth, svy.inclination, distance)
                    svy.depth = self.surveys_list[i].depth - distance
                    self.desurvey_list.append(svy)
                    svy = deepcopy(self.surveys_list[i])
                    svy.location = deepcopy(self.desurvey_list[len(self.desurvey_list) - 1].location)
                    svy.location.azimuth_move(svy.azimuth, svy.inclination, distance)
                    self.desurvey_list.append(svy)









