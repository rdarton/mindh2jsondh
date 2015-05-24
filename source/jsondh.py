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
import re
import psycopg2
import dbhelper as db
import point3d
import analyte
import mindhcollar
import StringIO
from csv import reader

class Jsondh:

    def __init__(self):
    #------------------------------------------------------------------------------
        self.name = 'jsondh'
        self.description = ''
        self.version = 0.02
        self.crs = 4326
        self.coordinate_decimals = 6
        self.desurvey_method = ''
        self.boxMin = point3d.Point3d()
        self.boxMax = point3d.Point3d()
        self.num_holes_expected = 0
        self.num_holes_written = 0
        self.num_assay_sets_written = 0
        self.zero_origin = False
        self.shift = point3d.Point3d()
        self.latLongMin = point3d.Point3d()
        self.latLongMax = point3d.Point3d()
        self.analytes_list = []

    def build_analytes_list(self, names, descriptions, colors):
    #------------------------------------------------------------------------------
        """
        """
        #
        # ----- first build list of names
        #       names come in like this: "Au, As"
        #
        if names != None and len(names) > 0:
            analytes_list = re.split(r'[,\s]\s*', names)
            for name in analytes_list:
                a = analyte.Analyte()
                a.name = name
                self.analytes_list.append(a)
        #
        # ----- add descriptions if they are there
        #       descriptions are like this: "'Au (ppm)', 'As (ppm)'"
        #
        if descriptions != None and len(descriptions) > 0:
            for line in reader(StringIO.StringIO(descriptions)):
                part_num = 0
                for part in line:
                    if part_num < len(self.analytes_list):
                        self.analytes_list[part_num].description = part.strip().strip("'")
                    part_num += 1
        #
        # ----- add colors if there
        #       colors come in like this: "#00FF00, #0000FF"
        #
        if colors != None and len(colors) > 0:
            colors_list = re.split(r'[,\s]\s*', colors)
            color_num = 0
            for color in colors_list:
                if color_num < len(self.analytes_list):
                    self.analytes_list[color_num].color = color
                color_num += 1

    def show_analytes(self):
    #------------------------------------------------------------------------------
        """
        """
        print "%r analytes to export." % len(self.analytes_list)
        for analyte in self.analytes_list:
            print "Analyte = [%r], Description = [%r], Color = [%r]" % \
                  (analyte.name, analyte.description, analyte.color)

    def expand_box(self, max_depth):
    #------------------------------------------------------------------------------
        """
        Expand the box so there is a buffer around the known area.
        """
        xy_factor = 0.03
        z_factor = 0.03
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

    def setup_shift(self):
    #------------------------------------------------------------------------------
        if self.zero_origin:
            self.shift.x = self.boxMin.x
            self.shift.y = self.boxMin.y
            self.boxMin.subtract(self.shift)
            self.boxMax.subtract(self.shift)

    def write_analyte(self, json_file, analyte, num_written):
    #------------------------------------------------------------------------------
        if num_written > 0:
            json_file.write_object_delimiter()
        json_file.newline()
        json_file.start_object()
        json_file.newline()
        json_file.increase_indent()
        json_file.write_label_and_string('name', analyte.name)
        json_file.write_label_and_string('description', analyte.description)
        json_file.write_label_and_string('color', analyte.color, False, True)
        json_file.decrease_indent()
        json_file.end_object()

    def write_analytes(self, json_file):
    #------------------------------------------------------------------------------
        """
        Write the list of analytes.
        """
        json_file.write_label('analytes')
        json_file.newline()
        json_file.start_array()
        json_file.increase_indent()
        num_written = 0
        for analyte in self.analytes_list:
            self.write_analyte(json_file, analyte, num_written)
            num_written += 1
        json_file.decrease_indent()
        json_file.newline()
        json_file.end_array()
        json_file.write_object_delimiter()
        json_file.newline()

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
        json_file.write_label_and_int('numHoles', self.num_holes_expected)
        json_file.write_label_and_int('projectionEPSG', self.crs)
        if self.zero_origin:
            json_file.write_label_and_objectstr('originShift', self.shift.get_as_json_array(self.coordinate_decimals))
        json_file.write_label_and_objectstr('boxMin', self.boxMin.get_as_json_array(self.coordinate_decimals))
        json_file.write_label_and_objectstr('boxMax', self.boxMax.get_as_json_array(self.coordinate_decimals))
        json_file.write_label_and_objectstr('latLongMin', self.latLongMin.get_as_json_array(8))
        json_file.write_label_and_objectstr('latLongMax', self.latLongMax.get_as_json_array(8))
        json_file.write_label_and_string('desurveyMethod', self.desurvey_method)
        if len(self.analytes_list) > 0:
            self.write_analytes(json_file)
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

    def write_downhole_survey(self, json_file, survey, num_surveys_written, raw):
    #------------------------------------------------------------------------------
        if num_surveys_written > 0:
            json_file.write_object_delimiter()
        json_file.newline()
        json_file.start_object()
        json_file.write_label_and_float('depth', survey.depth, 2, True, False)
        json_file.write_label_and_float('azimuth', survey.azimuth, 2, True, False)
        json_file.write_label_and_float('inclination', survey.inclination, 2, False, False)
        if not raw:
            json_file.write_object_delimiter()
            json_file.write_label_and_objectstr('location',
                                                survey.location.get_as_json_array(self.coordinate_decimals),
                                                False, False)
        json_file.end_object()

    def write_downhole_surveys(self, json_file, label, surveys_list, raw):
    #------------------------------------------------------------------------------
        num_surveys_written = 0
        num_surveys_to_write = 0
        if raw:
            for survey in surveys_list:
                if survey.is_raw: num_surveys_to_write += 1
        else:
            num_surveys_to_write = len(surveys_list)
        if num_surveys_to_write > 0:
            json_file.write_object_delimiter()
            json_file.newline()
            json_file.write_label(label)
            json_file.newline()
            json_file.start_array()
            json_file.increase_indent()
            for survey in surveys_list:
                if (raw and survey.is_raw) or not raw:
                    self.write_downhole_survey(json_file, survey, num_surveys_written, raw)
                    num_surveys_written += 1
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
                json_file.write_label_and_float('value', result.value, 5, True, False)
                json_file.write_label_and_objectstr('path', result.get_path_as_json(self.coordinate_decimals),
                                                    False, False)
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
        self.write_downhole_surveys(json_file, 'rawDownholeSurveys', collar.surveys_list, True)
        self.write_downhole_surveys(json_file, 'interpolatedDownholeSurveys', collar.desurvey_list, False)
        self.write_assays(json_file, collar)
        json_file.decrease_indent()
        json_file.newline()
        json_file.end_object()
        self.num_holes_written += 1


