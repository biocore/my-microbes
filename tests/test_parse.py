#!/usr/bin/env python
from __future__ import division

__author__ = "Jai Ram Rideout"
__copyright__ = "Copyright 2013, The QIIME Project"
__credits__ = ["Jai Ram Rideout"]
__license__ = "GPL"
__version__ = "0.1.0"
__maintainer__ = "Jai Ram Rideout"
__email__ = "jai.rideout@gmail.com"

"""Test suite for the parse.py module."""

from unittest import main, TestCase

from my_microbes.parse import (parse_email_settings, parse_recipients,
                               _can_ignore)

class ParseTests(TestCase):
    """Tests for the parse.py module.

    Many of these tests are taken from Clout's
    (https://github.com/qiime/clout) test_parse module.
    """

    def setUp(self):
        """Define some sample data that will be used by the tests."""
        # Standard recipients file with two recipients, one with multiple email
        # addresses.
        self.recipients1 = ["# a comment", " ",
                            " foo1\tabcABC123\tfoo@bar.baz  ",
                            "foo2\t1skdiwoadk\t foo2@bar.baz,  foo3@bar.baz,foo4@bar.baz "]

        # An empty recipients file.
        self.recipients2 = ["# a comment", " ", "\n\t\t\t\t"]

        # An incorrectly-formatted recipients file (not the right number of
        # fields).
        self.recipients3 = ["# a comment", "foo1\tfoo@bar.baz",
                            "foo2\tfoo2@bar.baz\t foo3@bar.baz"]

        # Non-unique personal IDs.
        self.recipients4 = ["foo1\tskwowkdklw\tfoo@bar.baz",
                            "foo2\tslkfjwo229309\tfoo2@bar.baz, foo3@bar.baz",
                            "foo1\tslkjdskl9929\tfoo4@bar.baz"]

        # Empty fields.
        self.recipients5 = ["foo1\tfoo@bar.baz",
                            "\tsdlkfjsdkj\tfoo2@bar.baz, foo3@bar.baz"]

        # Invalid email addresses.
        self.recipients6 = ["# a comment...", "foo1\tskskwo2\tfoo@bar.baz",
                            "  ", "foo2\tljwojiio\tfoo.bar.baz"]

        # Standard email settings.
        self.email_settings1 = ["# A comment", "# Another comment",
                "smtp_server\tsome.smtp.server", "smtp_port\t42",
                "sender\tfoo@bar.baz", "password\t424242!"]

        # Bad email settings (no tab).
        self.email_settings2 = ["# A comment", "", "  ", "\t\n",
                "smtp_server some.smtp.server", " ", "smtp_port\t42",
                "sender foo@bar.baz", "password 424242!"]

        # Bad email settings (too many fields).
        self.email_settings3 = ["# A comment", "", "  ", "\t\n",
                "smtp_server\tsome.smtp.server\tfoo", " ", "smtp_port\t42",
                "sender foo@bar.baz", "password 424242!"]

        # Bad email settings (unrecognized setting).
        self.email_settings4 = ["# A comment", "smtp_server\tfoo.bar.com",
                                "stmp_port\t44"]

        # Bad email settings (missing required settings).
        self.email_settings5 = ["# A comment", "smtp_server\tfoo.bar.com",
                                "smtp_port\t44"]

    def test_parse_recipients_standard(self):
        """Test parsing a standard recipients file."""
        exp = {'foo1': ('abcABC123', ['foo@bar.baz']),
               'foo2': ('1skdiwoadk',
                        ['foo2@bar.baz', 'foo3@bar.baz', 'foo4@bar.baz'])}
        obs = parse_recipients(self.recipients1)
        self.assertEqual(obs, exp)

    def test_parse_recipients_empty(self):
        """Test parsing an empty recipients file."""
        obs = parse_recipients(self.recipients2)
        self.assertEqual(obs, {})

    def test_parse_recipients_invalid(self):
        """Test parsing an incorrectly-formatted recipients file."""
        self.assertRaises(ValueError, parse_recipients, self.recipients3)

    def test_parse_recipients_repeated_personal_ids(self):
        """Test parsing a recipients file with non-unique personal IDs."""
        self.assertRaises(ValueError, parse_recipients, self.recipients4)

    def test_parse_recipients_empty_fields(self):
        """Test parsing a recipients file with empty fields."""
        self.assertRaises(ValueError, parse_recipients, self.recipients5)

    def test_parse_recipients_bad_address(self):
        """Test parsing a recipients file with an invalid email address."""
        self.assertRaises(ValueError, parse_recipients, self.recipients6)

    def test_parse_email_settings_standard(self):
        """Test parsing a standard email settings file."""
        exp = {'smtp_server': 'some.smtp.server', 'smtp_port': '42',
                'sender': 'foo@bar.baz', 'password': '424242!'}
        obs = parse_email_settings(self.email_settings1)
        self.assertEqual(obs, exp)

    def test_parse_email_settings_invalid(self):
        """Test parsing invalid email settings files."""
        self.assertRaises(ValueError,
                          parse_email_settings, self.email_settings2)
        self.assertRaises(ValueError,
                          parse_email_settings, self.email_settings3)
        self.assertRaises(ValueError,
                          parse_email_settings, self.email_settings4)
        self.assertRaises(ValueError,
                          parse_email_settings, self.email_settings5)

    def test_can_ignore(self):
        """Test whether comments and whitespace-only lines are ignored."""
        self.assertEqual(_can_ignore("# a comment..."), True)
        self.assertEqual(_can_ignore("  \t# a comment..."), True)
        self.assertEqual(_can_ignore("  \t\n   "), True)
        self.assertEqual(_can_ignore("abc"), False)
        self.assertEqual(_can_ignore(" \t abc   "), False)


if __name__ == "__main__":
    main()
