"""

    jsonfile.py

    Utility class to help writing a complex JSON file.

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

class Jsonfile:

    fh = None
    filename = ''
    indent = ''
    at_beginning_of_line = True
    del_object_start = '{'
    del_object_end = '}'
    del_array_start = '['
    del_array_end = ']'
    del_newline = '\n'
    del_string = '\"'
    del_object = ','

    def open(self, filename):
    #------------------------------------------------------------------------------
        self.fh = open(filename, 'w')
        if self.fh is None:
            sys.exit("ERROR: Cannot create and open the file " + filename)
        self.filename = filename

    def close(self):
    #------------------------------------------------------------------------------
        self.fh = None

    def increase_indent(self):
    #------------------------------------------------------------------------------
        self.indent = self.indent + '  '

    def decrease_indent(self):
    #------------------------------------------------------------------------------
        if len(self.indent) >= 2:
            self.indent = self.indent[:-2]

    def start_object(self):
    #------------------------------------------------------------------------------
        self.write_indent()
        self.fh.write(self.del_object_start)

    def end_object(self):
    #------------------------------------------------------------------------------
        self.write_indent()
        self.fh.write(self.del_object_end)

    def newline(self):
    #------------------------------------------------------------------------------
        self.fh.write(self.del_newline)
        self.at_beginning_of_line = True

    def write_indent(self):
    #------------------------------------------------------------------------------
        if self.at_beginning_of_line:
            self.fh.write(self.indent)
            self.at_beginning_of_line = False

    def write_string(self, str):
    #------------------------------------------------------------------------------
        self.write_indent()
        self.fh.write(self.del_string)
        if str != None and len(str) > 0:
            self.fh.write(str)
        self.fh.write(self.del_string)

    def write_label(self, label):
    #------------------------------------------------------------------------------
        self.write_string(label)
        self.fh.write(': ')

    def write_delimit_and_end(self, end_delimiter = True, newline = True):
    #------------------------------------------------------------------------------
        if end_delimiter:
            self.fh.write(self.del_object)
        if newline:
            self.newline()

    def write_label_and_string(self, label, str, end_delimiter = True, newline = True):
    #------------------------------------------------------------------------------
        self.write_label(label)
        self.write_string(str)
        self.write_delimit_and_end(end_delimiter, newline)

    def write_label_and_objectstr(self, label, str, end_delimiter = True, newline = True):
    #------------------------------------------------------------------------------
        self.write_label(label)
        self.fh.write(str)
        self.write_delimit_and_end(end_delimiter, newline)

    def write_label_and_float(self, label, num, decimals, end_delimiter = True, newline = True):
    #------------------------------------------------------------------------------
        str = '{:.{prec}f}'.format(num, prec=decimals)
        self.write_label(label)
        self.fh.write(str)
        self.write_delimit_and_end(end_delimiter, newline)

    def write_label_and_int(self, label, num, end_delimiter = True, newline = True):
    #------------------------------------------------------------------------------
        str = '{:d}'.format(num)
        self.write_label(label)
        self.fh.write(str)
        self.write_delimit_and_end(end_delimiter, newline)



