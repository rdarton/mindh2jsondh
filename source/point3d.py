"""

    point3d.py

    Contains a 3d point instance.

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
import math
import point2d

class Point3d:

    def __init__(self):
    #------------------------------------------------------------------------------
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0

    def get_as_json_array(self, decimals = 2):
    #------------------------------------------------------------------------------
        return '[{:.{prec}f},{:.{prec}f},{:.{prec}f}]'.format(self.x, self.y, self.z, prec=decimals)

    def azimuth_move(self, azimuth, inclination, distance):
    #------------------------------------------------------------------------------
        if distance != 0.0:
            dHorizDist = distance
            dVertDist  = 0.0
            pt = point2d.Point2d()
            pt.x = self.x
            pt.y = self.y
            if inclination != 0.0:
                dHorizDist = distance * math.cos(math.radians(inclination))
                dVertDist  = distance * math.sin(math.radians(inclination))
            pt.azimuth_move(azimuth, dHorizDist)
            self.x = pt.x
            self.y = pt.y
            self.z += dVertDist



