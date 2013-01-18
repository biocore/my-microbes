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
from personal_microbiome.format import format_participant_table

options_lookup = get_options_lookup()

script_info = {}
script_info['brief_description'] = "Generates a table of participant IDs with links to personalized results"
script_info['script_description'] = """
This script generates a table containing participant IDs (i.e. personal IDs)
with links to personalized results. Currently, the only supported output format
is HTML. This table can then be dropped into a main index page to allow
participants to find links to their results (in addition to the email they
should also receive).

This script is kept separate from the personal_results.py script because that
script may be run many times (in parallel) over different subsets of personal
IDs. This script can then be used once a final comprehensive list of
participants has been prepared. For convenience, it accepts the same input file
format as the notify_participants.py script, as this final list of participants
will likely be the same list that you'll want to email.
"""

script_info['script_usage'] = []
script_info['script_usage'].append((
"Generate HTML table of participants",
"The following command generates an HTMl table of all participants in "
"participants.txt, using the provided URL prefix. An example of a "
"personalized results link for personal ID 'NAU123' using the provided URL "
"prefix is 'http://my-microbes.qiime.org/NAU123/index.html'.",
"%prog -p participants.txt -u http://my-microbes.qiime.org -o "
"participants.html"))

script_info['output_description'] = """
The script produces an output HTML file containing the table.
"""

script_info['required_options'] = [
    make_option('-p', '--participants', type='existing_filepath',
        help='the list of participants to include in the table. This should '
        'be in the same format as that accepted by notify_participants.py\'s '
        '-r/--recipients option (provided for convenience). The email address '
        'column will be ignored'),
    options_lookup['output_fp'],
    make_option('-u', '--url_prefix', type='string',
        help='the URL to prefix to each personal ID (used for personalized '
        'results links)')
]

script_info['optional_options'] = []

script_info['version'] = __version__

def main():
    option_parser, opts, args = parse_command_line_parameters(**script_info)

    participant_table = format_participant_table(open(opts.participants, 'U'),
                                                  opts.url_prefix)

    with open(opts.output_fp, 'w') as output_f:
        output_f.write(participant_table)


if __name__ == "__main__":
    main()
