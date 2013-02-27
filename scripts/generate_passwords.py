#!/usr/bin/env python
from __future__ import division

__author__ = "Jai Ram Rideout"
__copyright__ = "Copyright 2013, The QIIME project"
__credits__ = ["Jai Ram Rideout"]
__license__ = "GPL"
__version__ = "0.0.0-dev"
__maintainer__ = "Jai Ram Rideout"
__email__ = "jai.rideout@gmail.com"

from qiime.util import (create_dir, get_options_lookup, make_option,
                        parse_command_line_parameters)

from my_microbes.util import generate_passwords

options_lookup = get_options_lookup()

script_info = {}
script_info['brief_description'] = "Generates passwords for individuals"
script_info['script_description'] = """
This script randomly generates passwords for each specified study participant.
It also generates a single .htpasswd file containing the personal ID (which is
the username) and the encrypted password. A .htaccess file is created in the
root of each personalized results subdirectory to allow only the participant to
see his/her personalized results.

WARNING: be very careful with the output file that maps personal IDs (i.e.
usernames) to unencrypted passwords. If someone gains access to this file, they
will be able to view everyone's personalized results!
"""

script_info['script_usage'] = []

script_info['output_description'] = ""

script_info['required_options'] = [
    make_option('-i', '--personal_ids_fp', type='existing_filepath',
        help='the list of personal IDs to generate passwords for. Should be a '
        'file with a single personal ID per line'),
    make_option('-r', '--results_dir', type='existing_dirpath',
        help='the directory containing a subdirectory for each personal ID in '
        '-i/--personal_ids_fp. This will most likely be the output directory '
        'of personal_results.py. A .htaccess file will be created within each '
        'subdirectory in order to make the contents private on a '
        'per-individual basis'),
    make_option('-p', '--password_dir', type='string',
        help='the full (absolute) path to the directory where the .htpasswd '
        'file will be stored on the web server. This path will be placed in '
        'each .htaccess file'),
    options_lookup['output_dir']
]

script_info['optional_options'] = []

script_info['version'] = __version__

def main():
    option_parser, opts, args = parse_command_line_parameters(**script_info)

    create_dir(opts.output_dir)

    generate_passwords(open(opts.personal_ids_fp, 'U'), opts.results_dir,
                       opts.password_dir, opts.output_dir)


if __name__ == "__main__":
    main()
