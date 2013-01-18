#!/usr/bin/env python
"""Run all unit test suites by executing this script.

This script is adapted from the QIIME project's tests/all_tests.py:
    https://github.com/qiime/qiime
"""

from os import walk
from subprocess import PIPE, Popen
from os.path import abspath, dirname, join, split
from glob import glob
import re

__author__ = "Rob Knight"
__copyright__ = "Copyright 2013, The QIIME Project"
__credits__ = ["Rob Knight", "Greg Caporaso", "Jai Ram Rideout"]
__license__ = "GPL"
__version__ = "0.9-dev"
__maintainer__ = "Jai Ram Rideout"
__email__ = "jai.rideout@gmail.com"
__status__ = "Development"

def main():
    my_microbes_dir = abspath(join(dirname(__file__), '..'))
    tests_dir = join(my_microbes_dir, 'tests')
    scripts_dir = join(my_microbes_dir, 'scripts')

    unit_test_good_pattern = re.compile('OK\s*$')
    python_name = 'python'
    bad_tests = []

    # Run through all of the unit tests, and keep track of any files that fail
    # unit tests.
    unit_test_names = []
    for root, dirs, files in walk(tests_dir):
        for name in files:
            if name.startswith('test_') and name.endswith('.py'):
                unit_test_names.append(join(root, name))
    unit_test_names.sort()

    for unit_test_name in unit_test_names:
        print "Testing %s:\n" % unit_test_name
        command = '%s %s -v' % (python_name, unit_test_name)
        proc = Popen(command, shell=True, universal_newlines=True, stdout=PIPE,
                     stderr=PIPE)
        stdout, stderr =  proc.communicate()
        print stderr

        if not unit_test_good_pattern.search(stderr):
            bad_tests.append(unit_test_name)

    # Run through all of the scripts, and pass -h to each one. If the
    # resulting stdout does not begin with the usage text, that is an indicator
    # of something being wrong with the script. Issues that would cause that
    # are bad import statements in the script, SyntaxErrors, or other failures
    # prior to running parse_args().
    script_names = []
    script_names = glob('%s/*' % scripts_dir)
    script_names.sort()

    bad_scripts = []
    for script_name in script_names:
        script_good_pattern = re.compile('^Usage: %s' % split(script_name)[1])
        print "Testing %s." % script_name
        command = '%s %s -h' % (python_name, script_name)
        proc = Popen(command, shell=True, universal_newlines=True, stdout=PIPE,
                     stderr=PIPE)
        stdout, stderr =  proc.communicate()

        if not script_good_pattern.search(stdout):
            bad_scripts.append(script_name)

    if bad_tests:
        print "\nFailed the following unit tests.\n%s" % '\n'.join(bad_tests)

    if bad_scripts:
        print "\nFailed the following script tests.\n%s" % '\n'.join(
              bad_scripts)

    # If any of the unit tests or script tests failed, use return code 1 (as
    # Python's unittest module does) to indicate one or more failures with the
    # test suite.
    return_code = 1
    if not (bad_tests or bad_scripts):
        print "\nAll tests passed successfully."
        return_code = 0
    return return_code


if __name__ == "__main__":
    exit(main())
