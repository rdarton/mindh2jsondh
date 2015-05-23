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
import mindhcollar

class Jsondh:

    def __init__(self):
    #------------------------------------------------------------------------------
        self.name = 'jsondh'
        self.description = ''
        self.version = 0.01
        self.crs = 4326
        self.coordinate_decimals = 6
        self.boxMin = point3d.Point3d()
        self.boxMax = point3d.Point3d()
        self.num_holes_written = 0
        self.num_surveys_written = 0
        self.num_assay_sets_written = 0

    def expand_box(self, max_depth):
    #------------------------------------------------------------------------------
        """
        Expand the box so there is a buffer around the known area.
        """
        xy_factor = 0.05
        z_factor = 0.05
        self.boxMin.z -= max_depth
        if self.boxMin.z == self.boxMax.z:
            self.boxMin.z -= 10
        if self.boxMin.x == self.boxMax.x:
            self.boxMax.x += 10
        if self.boxMin.y == self.boxMax.y:
            self.boxMax.y += 10
        d = (self.boxMax.x - self.boxMin.x) * xy_factor
        self.boxMin.x -= d
        self.boxMax.y += d
        d = (self.boxMax.y - self.boxMin.y) * xy_factor
        self.boxMin.y -= d
        self.boxMax.y += d
        d = (self.boxMax.z - self.boxMin.z) * z_factor
        self.boxMin.z -= d
        self.boxMax.z += d


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
        json_file.write_label_and_float('formatVersion', self.version, 2)

    def write_footer(self, json_file):
    #------------------------------------------------------------------------------
        json_file.newline()
        json_file.decrease_indent()
        json_file.end_object()
        json_file.newline()

    def start_holes_section(self, json_file):
    #------------------------------------------------------------------------------
        json_file.write_label('holes')
        json_file.newline()
        json_file.start_array()
        json_file.increase_indent()

    def end_holes_section(self, json_file):
    #------------------------------------------------------------------------------
        json_file.decrease_indent()
        json_file.newline()
        json_file.end_array()

    def write_downhole_survey(self, json_file, survey):
    #------------------------------------------------------------------------------
        if self.num_surveys_written > 0:
            json_file.write_object_delimiter()
        json_file.newline()
        json_file.start_object()
        json_file.increase_indent()
        json_file.newline()
        # json_file.write_label_and_int('id', survey.rowid)
        json_file.write_label_and_float('depth', survey.depth, 2)
        json_file.write_label_and_float('azimuth', survey.azimuth, 2)
        json_file.write_label_and_float('inclination', survey.inclination, 2)
        json_file.write_label_and_objectstr('location', survey.location.get_as_json_array(self.coordinate_decimals),
                                            False, False)
        json_file.decrease_indent()
        json_file.newline()
        json_file.end_object()
        self.num_surveys_written += 1

    def write_downhole_surveys(self, json_file, collar):
    #------------------------------------------------------------------------------
        if len(collar.desurvey_list) > 0:
            json_file.write_object_delimiter()
            json_file.newline()
            json_file.write_label('downholeSurveys')
            json_file.newline()
            json_file.start_array()
            json_file.increase_indent()
            self.num_surveys_written = 0
            for survey in collar.desurvey_list:
                self.write_downhole_survey(json_file, survey)
            json_file.decrease_indent()
            json_file.newline()
            json_file.end_array()

    def write_results(self, json_file, results_list):
    #------------------------------------------------------------------------------
        if len(results_list) > 0:
            num_written = 0
            for result in results_list:
                if num_written > 0:
                    json_file.write_object_delimiter()
                json_file.newline()
                json_file.start_object()
                json_file.write_label_and_float('from', result.start_depth, 2, True, False)
                json_file.write_label_and_float('to', result.end_depth, 2, True, False)
                json_file.write_label_and_float('value', result.value, 5, False, False)
                json_file.end_object()
                num_written += 1


    def write_set_of_assays(self, json_file, assay):
    #------------------------------------------------------------------------------
        if self.num_assay_sets_written > 0:
            json_file.write_object_delimiter()
        json_file.newline()
        json_file.start_object()
        json_file.increase_indent()
        json_file.newline()
        # json_file.write_label_and_int('id', survey.rowid)
        json_file.write_label_and_string('name', assay.name, True, True)
        json_file.write_label('intervals')
        json_file.newline()
        if len(assay.results_list) > 0:
            # json_file.write_object_delimiter()
            # json_file.newline()
            json_file.start_array()
            json_file.increase_indent()
            self.write_results(json_file, assay.results_list)
            json_file.decrease_indent()
            json_file.newline()
            json_file.end_array()
        json_file.decrease_indent()
        json_file.newline()
        json_file.end_object()
        self.num_assay_sets_written += 1

    def write_assays(self, json_file, collar):
    #------------------------------------------------------------------------------
        if len(collar.assays_list) > 0:
            json_file.write_object_delimiter()
            json_file.newline()
            json_file.write_label('downholeDataValues')
            json_file.newline()
            json_file.start_array()
            json_file.increase_indent()
            self.num_assay_sets_written = 0
            for assay in collar.assays_list:
                self.write_set_of_assays(json_file, assay)
            json_file.decrease_indent()
            json_file.newline()
            json_file.end_array()

    def write_hole(self, json_file, collar):
    #------------------------------------------------------------------------------
        if self.num_holes_written > 0:
            json_file.write_object_delimiter()
        json_file.newline()
        json_file.start_object()
        json_file.increase_indent()
        json_file.newline()
        json_file.write_label_and_int('id', collar.rowid)
        json_file.write_label_and_string('name', collar.name)
        json_file.write_label_and_float('depth', collar.depth, 2)
        json_file.write_label_and_objectstr('location',
                                            collar.location.get_as_json_array(self.coordinate_decimals),
                                            False, False)
        self.write_downhole_surveys(json_file, collar)
        self.write_assays(json_file, collar)
        json_file.decrease_indent()
        json_file.newline()
        json_file.end_object()
        self.num_holes_written += 1


