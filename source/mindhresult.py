"""

    mindhresult.py

    Contains a downhole result from a mindh database.

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
import mindhsurvey
import point3d

class Mindhresult:

    def __init__(self):
    #------------------------------------------------------------------------------
        """
        Constructor.
        """
        self.start_depth = 0.0
        self.end_depth = 0.0
        self.value = 0.0
        self.path = []

    def get_path_as_json(self, decimals = 2):
    #------------------------------------------------------------------------------
        """
        Get the desurveyed path of the interval as a JSON object.
        Returns something like:
        [[4199.39,33689.04,199.00],[4199.39,33689.04,195.00]]
        Note that the path may have more than two points.
        """
        json = ''
        delimiter = ''
        if len(self.path) > 0:
            json = '['
            for p in self.path:
                json += delimiter
                json += p.get_as_json_array(decimals)
                delimiter = ','
            json += ']'
        return json


    def desurvey(self, surveys_list):
    #------------------------------------------------------------------------------
        """
        De-survey the interval by adding a 3D coordinate path that defines where
        the interval is.  The path will typically be two points, but may be
        multiple segments.
        """
        svy = mindhsurvey.Mindhsurvey()
        #
        # ----- interpolate XYZ at start and end depths of the interval
        #
        start_location = svy.interpolate_location(surveys_list, self.start_depth)
        end_location = svy.interpolate_location(surveys_list, self.end_depth)
        if start_location != None and end_location != None:
            #
            # ----- get indexes to see if there are any intermediate surveys that are part of the path
            #
            start_index = svy.get_next_deepest_survey_index(surveys_list, self.start_depth)
            end_index = svy.get_next_deepest_survey_index(surveys_list, self.start_depth)
            #
            # ----- build path including any intermediate points
            #
            self.path.append(start_location)
            if start_index != end_index:
                print 'DEBUG: Interval crossing survey points found from depth %r to %r' % \
                      (self.start_depth, self.end_depth)
                cur = start_index
                while cur < end_index:
                    if surveys_list[cur].depth > self.start_depth and surveys_list[cur].depth < self.end_depth:
                        pt = deepcopy(surveys_list[cur].location)
                        self.path.append(pt)
                    cur += 1
            self.path.append(end_location)
        else:
            print 'ERROR: Problem desurveying interval from %r to %r.' % (self.start_depth, self.end_depth)


