#!/usr/bin/env python
from __future__ import division

__author__ = "Jai Ram Rideout"
__copyright__ = "Copyright 2013, The QIIME Project"
__credits__ = ["Jai Ram Rideout"]
__license__ = "GPL"
__version__ = "0.1.0-dev"
__maintainer__ = "Jai Ram Rideout"
__email__ = "jai.rideout@gmail.com"

"""Module to parse various supported file formats."""

def parse_recipients(recipients_f):
    """Parses and validates a file containing recipients' email addresses.

    Returns a dictionary mapping personal ID to a tuple containing the user's
    password and list of email addresses.

    Some code taken and modified from Clout's (https://github.com/qiime/clout)
    parse.parse_config_file and parse.parse_email_list functions.

    Arguments:
        recipients_f - the recipients file (three-column TSV with personal ID,
            password, and comma-separated email address(es))
    """
    results = {}

    for line in recipients_f:
        if not _can_ignore(line):
            fields = line.strip().split('\t')
            if len(fields) != 3:
                raise ValueError("Each line in the recipients file must "
                                 "contain exactly three fields separated by "
                                 "tabs.")

            personal_id = fields[0].strip()
            if personal_id in results:
                raise ValueError("The personal ID '%s' has already been "
                                 "encountered. A personal ID may only be used "
                                 "once in the recipients file." % personal_id)

            password = fields[1].strip()

            emails = map(lambda e: e.strip(), fields[2].strip().split(','))
            for email in emails:
                if '@' not in email:
                    raise ValueError("The email address '%s' doesn't look "
                                     "like a valid email address." % email)
            results[personal_id] = password, emails

    return results

def parse_email_settings(email_settings_f):
    """Parses and validates a file containing email SMTP settings.

    Returns a dictionary with the key/value pairs 'smtp_server', 'smtp_port',
    'sender', and 'password' defined.

    Taken from Clout's (https://github.com/qiime/clout) parse module.

    Arguments:
        email_settings_f - the input file containing tab-separated email
            settings
    """
    required_fields = ['smtp_server', 'smtp_port', 'sender', 'password']
    settings = {}
    for line in email_settings_f:
        if not _can_ignore(line):
            try:
                setting, val = line.strip().split('\t')
            except:
                raise ValueError("The line '%s' in the email settings file "
                                 "must have exactly two fields separated by a "
                                 "tab." % line)
            if setting not in required_fields:
                raise ValueError("Unrecognized setting '%s' in email settings "
                                 "file. Valid settings are %r." % (setting,
                                 required_fields))
            settings[setting] = val
    if len(settings) != 4:
        raise ValueError("The email settings file does not contain one or "
                "more of the following required fields: %r" % required_fields)
    return settings

def _can_ignore(line):
    """Returns True if the line can be ignored (comment or blank line).
    
    Taken from Clout's (https://github.com/qiime/clout) parse module.
    """
    return False if line.strip() != '' and not line.strip().startswith('#') \
           else True
