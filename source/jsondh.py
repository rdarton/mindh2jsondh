"""

    jsondh.py

    Contains a jsondh instance.

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
import point3d

class Jsondh:

    name = 'jsondh'
    description = ''
    version = 0.01
    crs = 4326
    coordinate_decimals = 6
    boxMin = point3d.Point3d()
    boxMax = point3d.Point3d()

    def write_header(self, json_file):
    #------------------------------------------------------------------------------
        """
        Write header information to a JSON file.
        """
        print "Writing header."
        json_file.start_object()
        json_file.newline()
        json_file.increase_indent()
        json_file.write_label_and_string('projectName', self.name)
        json_file.write_label_and_string('description', self.description)
        json_file.write_label_and_int('projectionEPSG', self.crs)
        json_file.write_label_and_objectstr('boxMin', self.boxMin.get_as_json_array(self.coordinate_decimals))
        json_file.write_label_and_objectstr('boxMax', self.boxMax.get_as_json_array(self.coordinate_decimals))
        json_file.write_label_and_float('formatVersion', self.version, 2, False)
        json_file.decrease_indent()
        json_file.end_object()
        json_file.newline()
