#!/usr/bin/env python

import sys
sys.path.append('/Applications//liclipse/plugins/org.python.pydev_4.0.0.201504092214/pysrc')
import pydevd


import logging, os, splunk

from splunklib.searchcommands import \
    dispatch, StreamingCommand, Configuration, Option, validators


@Configuration()
class SearchTableCommand(StreamingCommand):
    pattern = Option(
        doc='''
        **Syntax:** **pattern=***<regular-expression>*
        **Description:** Regular expression pattern to match''',
        require=False, validate=validators.RegularExpression())

    def stream(self, records):
        #pydevd.settrace()
        self.logger.setLevel(logging.DEBUG)
        self.logger.debug('SearchTableCommand: %s' % self)  # logs command line
        for record in records:
            found = "false"
            for field in record:
                matches = len(list(self.pattern.finditer(str(record[field]))))
                if matches > 0:
                    found = "true"
            if found == "true":
                yield record
        self.logger.debug('SearchTableCommand: Done') 

dispatch(SearchTableCommand, sys.argv, sys.stdin, sys.stdout, __name__)