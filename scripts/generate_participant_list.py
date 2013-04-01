#!/usr/bin/env python
from __future__ import division

__author__ = "Jai Ram Rideout"
__copyright__ = "Copyright 2013, The QIIME project"
__credits__ = ["Jai Ram Rideout"]
__license__ = "GPL"
__version__ = "0.1.0-dev"
__maintainer__ = "Jai Ram Rideout"
__email__ = "jai.rideout@gmail.com"

from qiime.util import (parse_command_line_parameters, get_options_lookup,
                        make_option)
from my_microbes.format import format_participant_list

options_lookup = get_options_lookup()

script_info = {}
script_info['brief_description'] = "Generates a list of participant IDs with links to personalized results"
script_info['script_description'] = """
This script generates a list containing participant IDs (i.e. personal IDs)
with links to personalized results. Currently, the only supported output format
is HTML. This list can then be dropped into a main index page to allow
participants to find links to their results (in addition to the email they
should also receive).

This script is kept separate from the personal_results.py script because that
script may be run many times (in parallel) over different subsets of personal
IDs. This script can then be used once a final comprehensive list of
participants has been prepared.
"""

script_info['script_usage'] = []
script_info['script_usage'].append((
"Generate HTML list of participants",
"The following command generates an HTMl list of all participants in "
"participants.txt, using the provided URL prefix. An example of a "
"personalized results link for personal ID 'NAU123' using the provided URL "
"prefix is 'http://my-microbes.qiime.org/NAU123/index.html'.",
"%prog -p participants.txt -u http://my-microbes.qiime.org -o "
"participants.html"))

script_info['output_description'] = """
The script produces an output HTML file containing the list.
"""

script_info['required_options'] = [
    make_option('-p', '--participants', type='existing_filepath',
        help='the list of participants to include in the HTML list. This '
        'should be a file with a personal ID on each line. If additional '
        'tab-separated columns exist (e.g. the file format accepted by '
        'notify_participants.py\'s -r/--recipients option), only the first '
        'column will be processed (this functionality is provided for '
        'convenience)'),
    options_lookup['output_fp'],
    make_option('-u', '--url_prefix', type='string',
        help='the URL to prefix to each personal ID (used for personalized '
        'results links)')
]

script_info['optional_options'] = []

script_info['version'] = __version__

def main():
    option_parser, opts, args = parse_command_line_parameters(**script_info)

    participant_list = format_participant_list(open(opts.participants, 'U'),
                                               opts.url_prefix)

    with open(opts.output_fp, 'w') as output_f:
        output_f.write(participant_list)


if __name__ == "__main__":
    main()
