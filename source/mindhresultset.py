"""

    mindhresultset.py

    Contains a set of results from a mindh database.

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
import mindhresult

class Mindhresultset:

    def __init__(self):
    #------------------------------------------------------------------------------
        self.name = ''
        self.results_list = []

    def read_results(self, connection, collar_rowid_fk):
    #------------------------------------------------------------------------------
        sql = """
                SELECT start_depth, end_depth, MAX(norm_value)
                FROM dh.result res
                INNER JOIN ref.result_field field ON res.result_field_rowid_fk = field.rowid
                WHERE res.collar_rowid_fk = {collar_rowid_fk}
                  AND field.analyte_rowid_fk = (SELECT rowid FROM ref.analyte WHERE name = '{analyte}')
                GROUP BY start_depth, end_depth
            """.format(collar_rowid_fk=collar_rowid_fk, analyte=self.name)
        # print "Reading results for %r" % self.name
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
                res = mindhresult.Mindhresult()
                res.start_depth = int(row[0])
                res.end_depth = float(row[1])
                res.value = float(row[2])
                self.results_list.append(res)
        except psycopg2.DatabaseError, e:
            print 'ERROR: %s' % e



