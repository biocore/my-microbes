#!/usr/bin/env python
from __future__ import division

__author__ = "Jai Ram Rideout"
__copyright__ = "Copyright 2013, The QIIME project"
__credits__ = ["Jai Ram Rideout"]
__license__ = "GPL"
__version__ = "0.1.0"
__maintainer__ = "Jai Ram Rideout"
__email__ = "jai.rideout@gmail.com"

from qiime.util import (parse_command_line_parameters, get_options_lookup,
                        make_option)
from my_microbes.util import notify_participants

script_info = {}
script_info['brief_description'] = "Notifies participants of personal results"
script_info['script_description'] = """
This script sends notifications containing links to personal results to
participants of a study. Currently, the only supported notification method is
email.

A separate email will be sent to each participant with his or her personalized
link (based on personal ID).

WARNING: this script is potentially very dangerous, as it can send mass emails.
Please be extremely cautious when using, and make sure you've double-checked
everything before executing it. For this reason, the script will not send any
emails by default, and will only print useful information about what it *would*
have done. When you are sure you want to run the script for real, execute it
with the --really option.

When executed with --really, a line will be printed to stdout for each
participant that is successfully emailed. The line will say something like:
    Sending email to <personal ID> (<email addresses>)... success!

If there is a problem during the email sending process, you will be able to see
which recipients (if any) were emailed successfully, so that you'll know not to
email them again when you rerun the script.
"""

script_info['script_usage'] = []
script_info['script_usage'].append((
"Email personal results links to participants (dry-run)",
"The following command does a dry-run of sending an email to each participant "
"in recipients.txt with a link to his or her results using the email account "
"specified in email_settings.txt. No emails are actually sent, and helpful "
"information is printed to stdout, to (hopefully) avoid potential mistakes.",
"%prog -r recipients.txt -s email_settings.txt"))

script_info['output_description'] = """
The script does not produce any output files. It will print useful information
to stdout by default unless --really is used, in which case the script will
print a line for each recipient that is successfully emailed.
"""

script_info['required_options'] = [
    make_option('-r', '--recipients', type='existing_filepath',
        help='the list of recipients to email. Should be a TSV file '
        'with a line for each recipient. The first column should be the '
        'personal ID, the second column should be their password, and the '
        'third column should be one or more email addresses '
        '(comma-separated).'),
    make_option('-s', '--email_settings', type='existing_filepath',
        help='the email account information to send the email from. Should be '
        'a two-column TSV file containing the following keys: smtp_server, '
        'smtp_port, sender, and password')
]

script_info['optional_options'] = [
    make_option('--really', action='store_true',
        help='instruct script to actually send emails. It is HIGHLY '
        'recommended to run the script without this option first to see what '
        'will be done, and to double-check everything. There is no going back '
        'after executing the script with this option enabled '
        '[default: %default]', default=False)
]

script_info['version'] = __version__

def main():
    option_parser, opts, args = parse_command_line_parameters(**script_info)

    notify_participants(open(opts.recipients, 'U'),
                        open(opts.email_settings, 'U'),
                        dry_run=not opts.really)


if __name__ == "__main__":
    main()
