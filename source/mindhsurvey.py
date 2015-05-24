"""

    mindhsurvey.py

    Contains a downhole survey from a mindh database.

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
import point3d

class Mindhsurvey:

    def __init__(self):
    #------------------------------------------------------------------------------
        self.rowid = -1
        self.depth = 0.0
        self.azimuth = 0.0
        self.inclination = 0.0
        self.location = point3d.Point3d()
        self.is_raw = True

    def get_next_deepest_survey_index(self, surveys_list, depth):
    #------------------------------------------------------------------------------
        start_survey = 0
        bracketed = False
        while not bracketed and start_survey < len(surveys_list):
            if float(depth) <= float(surveys_list[start_survey].depth):
                bracketed = True
            else:
                start_survey += 1
        if not bracketed:
            start_survey = -1
            print 'ERROR: Could not get next deepest survey for depth %r.' % depth
        return start_survey

    def interpolate_location(self, surveys_list, depth):
    #------------------------------------------------------------------------------
        start_survey = self.get_next_deepest_survey_index(surveys_list, depth)
        pt = None
        if start_survey >= 0:
            if depth == surveys_list[start_survey].depth:
                pt = deepcopy(surveys_list[start_survey].location)
            else:
                if start_survey > 0:
                    pt = deepcopy(surveys_list[start_survey - 1].location)
                    pt.azimuth_move(surveys_list[start_survey - 1].azimuth,
                                    surveys_list[start_survey - 1].inclination,
                                    depth - surveys_list[start_survey - 1].depth)
                else:
                    print 'ERROR: No prior survey to interpolate from for depth %r.' % depth
        return pt




