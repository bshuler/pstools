#!/usr/bin/env python
# coding=utf-8
#

from __future__ import absolute_import, division, print_function, unicode_literals
import app
import time
from datetime import datetime

from splunklib.searchcommands import dispatch, StreamingCommand, Configuration, Option, validators
import sys
from splunklib import six


@Configuration()
class StrptimeFindCommand(StreamingCommand):
    """ Finds a strptime value in a string

    ##Syntax

    .. code-block::
        strptimefind fieldname=<field> pattern=<valid_strptime_string> outputfield=<field>

    ##Description

    Uses multiple methods to find a valid time from within the string from the field <fieldname>

    ##Example

    From the first 35 characters of this line, find a valid time.

    .. code-block::
        | makeresults | eval line="Tue Oct 30 16:58:50 EDT 2018 This i", strptime_string="%a %b %d %H:%M:%S %Z %Y" | strptimefind fieldname=line pattern=strptime_string outputfield=found_time

    """
    fieldname = Option(
        doc='''
        **Syntax:** **fieldname=***<fieldname>*
        **Description:** Name of the field that holds the text to be evaluated''',
        require=True, validate=validators.Fieldname())

    pattern = Option(
        doc='''
        **Syntax:** **pattern=***<valid_strptime_string>*
        **Description:** A valid strptime string''',
        require=True)

    outputfield = Option(
        doc='''
        **Syntax:** **outputfield=***<fieldname>*
        **Description:** Name of the field that will hold the found time''',
        require=True, validate=validators.Fieldname())

    def stream(self, records):
        self.logger.debug('StrptimeFindCommand: %s', self)  # logs command line
        pattern = self.pattern
        for record in records:
            count = 0
            datetime_str_orig = record[self.fieldname]
            valid_strptime_string = record[self.pattern]
            datetime_object = 0
            limit=len(valid_strptime_string)
            while len(datetime_str_orig) > limit:
                datetime_str=datetime_str_orig
                while len(datetime_str) > limit:
                    try:
                        datetime_object = datetime.strptime(datetime_str, valid_strptime_string)
                        break
                    except:
                        datetime_str = datetime_str[:-1]
                datetime_str_orig = datetime_str_orig[1:]
            if datetime_object:
                record[self.outputfield] = time.mktime(datetime_object.timetuple())
            yield record

dispatch(StrptimeFindCommand, sys.argv, sys.stdin, sys.stdout, __name__)
