#!/usr/bin/env python
from __future__ import division

__author__ = "Jai Ram Rideout"
__copyright__ = "Copyright 2013, The QIIME project"
__credits__ = ["Jai Ram Rideout"]
__license__ = "GPL"
__version__ = "0.0.0-dev"
__maintainer__ = "Jai Ram Rideout"
__email__ = "jai.rideout@gmail.com"

from qiime.util import (parse_command_line_parameters, get_options_lookup,
                        make_option)
from qiime.remote import load_google_spreadsheet

options_lookup = get_options_lookup()

script_info = {}
script_info['brief_description'] = "Notifies participants of personal results"
script_info['script_description'] = """
This script sends notifications containing links to personal results to
participants of a study. Currently, the only supported notification method is
email.
"""

script_info['script_usage'] = []
script_info['script_usage'].append((
"Email personal results links to participants",
"The following command sends an email to each participant in recipients.txt "
"with a link to his or her results using the email account specified in "
"email_settings.txt.",
"%prog -r recipients.txt -s email_settings.txt"))

script_info['output_description'] = "The script does not produce any output."

script_info['required_options'] = [
    make_option('-r', '--recipients', type='existing_filepath',
        help='the list of recipients to email. Should be a TSV file '
        'containing an optional header line followed by a line for each '
        'recipient. The first column should be the personal ID and the second '
        'column should be one or more email addresses (comma-separated).'),
    make_option('-s', '--email_settings', type='existing_filepath',
        help='the email account information to send the email from. Should be '
        'a two-column TSV file containing the following keys: smtp_server, '
        'smtp_port, sender, and password')
]

script_info['optional_options'] = []

script_info['version'] = __version__

def main():
    option_parser, opts, args = parse_command_line_parameters(**script_info)


if __name__ == "__main__":
    main()
