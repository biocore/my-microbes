#!/usr/bin/env python
from __future__ import division

__author__ = "John Chase"
__copyright__ = "Copyright 2013, The QIIME project"
__credits__ = ["John Chase", "Greg Caporaso", "Jai Ram Rideout"]
__license__ = "GPL"
__version__ = "0.0.0-dev"
__maintainer__ = "John Chase"
__email__ = "jc33@nau.edu"

import sys
from StringIO import StringIO
from unittest import TestCase, main
from qiime.parse import parse_mapping_file
from personal_microbiome.util import (get_personal_ids,
                                      create_personal_mapping_file,
                                      notify_participants)

class UtilTests(TestCase):

    def setUp(self):
        # Define some data here...
        #self.mapping_data = parse_mapping_file(mapping_str.split('\n'))

        self.recipients = ["# a comment", " ", " foo1\tfoo1@bar.baz  ",
                            "foo2\t foo2@bar.baz,  foo3@bar.baz,foo4@bar.baz "]

        self.email_settings = ["# A comment", "# Another comment",
                "smtp_server\tsome.smtp.server", "smtp_port\t42",
                "sender\tfrom@foobarbaz.com", "password\t424242!"]

    def test_get_personal_ids(self): 
        """Does the function return correct output when given correct output"""
        obs = get_personal_ids(self.mapping_data)
        
        column = 'PersonalID'
        input  = [['A01393', 'GTTATCGCATGG', 'CCGGACTACHVGGGTWTCTAAT', 'student', 'na', 'na', 'armpit', 'CUB', 'CUB027'],
                  ['A00994', 'CGGATAACCTCC', 'CCGGACTACHVGGGTWTCTAAT', 'student', 'na', 'na', 'armpit', 'NAU', 'NAU113'], 
                  ['A00981', 'TAACGCTGTGTG', 'CCGGACTACHVGGGTWTCTAAT', 'student', 'na', 'na', 'armpit', 'NAU', 'NAU133'], 
                  ['A00936', 'ATTGACCGGTCA', 'CCGGACTACHVGGGTWTCTAAT', 'student', 'na', 'na', 'armpit', 'NAU', 'NAU144'], 
                  ['A01497', 'AGCGCTCACATC', 'CCGGACTACHVGGGTWTCTAAT', 'student', 'na', 'na', 'armpit', 'NCS', 'NCS210'], 
                  ['A00663', 'CTCATCATGTTC', 'CCGGACTACHVGGGTWTCTAAT', 'student', 'na', 'na', 'armpit', 'NCS', 'NCS214'], 
                  ['A01367', 'GCAACACCATCC', 'CCGGACTACHVGGGTWTCTAAT', 'student', 'na', 'na', 'armpit', 'CUB', 'CUB000'], 
                  ['A01383', 'GCTTGAGCTTGA', 'CCGGACTACHVGGGTWTCTAAT', 'student', 'na', 'na', 'armpit', 'CUB', 'CUB003'], 
                  ['A01332', 'AGTAGCGGAAGA', 'CCGGACTACHVGGGTWTCTAAT', 'student', 'na', 'na', 'armpit', 'CUB', 'CUB004']]
        expected = ['CUB027', 'NAU113', 'NAU133', 'NAU144', 'NCS210', 'NCS214', 'CUB000', 'CUB003', 'CUB004']
        self.assertEqual(get_personal_ids(input, 8), expected)
        
    def test_create_personal_mapping_file(self): 
        """Does the function return correct output when given correct input?"""
        map_as_list = [['A01393', 'GTTATCGCATGG', 'CCGGACTACHVGGGTWTCTAAT', 'student', 'na', 'na', 'armpit', 'CUB', 'CUB027'],
                       ['A00994', 'CGGATAACCTCC', 'CCGGACTACHVGGGTWTCTAAT', 'student', 'na', 'na', 'armpit', 'NAU', 'NAU113'], 
                       ['A00981', 'TAACGCTGTGTG', 'CCGGACTACHVGGGTWTCTAAT', 'student', 'na', 'na', 'armpit', 'NAU', 'NAU133'], 
                       ['A00936', 'ATTGACCGGTCA', 'CCGGACTACHVGGGTWTCTAAT', 'student', 'na', 'na', 'armpit', 'NAU', 'NAU144'], 
                       ['A01497', 'AGCGCTCACATC', 'CCGGACTACHVGGGTWTCTAAT', 'student', 'na', 'na', 'armpit', 'NCS', 'NCS210'], 
                       ['A00663', 'CTCATCATGTTC', 'CCGGACTACHVGGGTWTCTAAT', 'student', 'na', 'na', 'armpit', 'NCS', 'NCS214'], 
                       ['A01367', 'GCAACACCATCC', 'CCGGACTACHVGGGTWTCTAAT', 'student', 'na', 'na', 'armpit', 'CUB', 'CUB000'], 
                       ['A01383', 'GCTTGAGCTTGA', 'CCGGACTACHVGGGTWTCTAAT', 'student', 'na', 'na', 'armpit', 'CUB', 'CUB003'], 
                       ['A01332', 'AGTAGCGGAAGA', 'CCGGACTACHVGGGTWTCTAAT', 'student', 'na', 'na', 'armpit', 'CUB', 'CUB004']]
        header = ['SampleID', 'BarcodeSequence', 'LinkerPrimerSequence', 'Study', 'HouseZipCode', 'SamplingLocation', 'BodyHabitat', 'University', 'PersonalID']
        comments = [] 
        personal_id_of_interest = 'CUB027'
        "So how do I write something out to file here and then check to make sure that is correct?"
        output_fp
        personal_id_index = 8
        individual_titles=None

    def test_notify_participants(self):
        """Tests the dry-run capability of notify_participants."""
        # Save stdout and replace it with something that will capture the print
        # statement. Note: this code was taken from here:
        # http://stackoverflow.com/questions/4219717/how-to-assert-output-
        #     with-nosetest-unittest-in-python/4220278#4220278
        saved_stdout = sys.stdout

        try:
            out = StringIO()
            sys.stdout = out
            notify_participants(self.recipients, self.email_settings)
            obs_output = out.getvalue().strip()
            self.assertEqual(obs_output, exp_dry_run_output)
        finally:
            sys.stdout = saved_stdout


mapping_str = """
S1
S2
S3
"""

exp_dry_run_output = """Running script in dry-run mode. No emails will be sent. Here's what I would have done:

Sender information:

From address: from@foobarbaz.com
Password: 424242!
SMTP server: some.smtp.server
Port: 42

Sending emails to 2 recipient(s).

Sample email:

To: foo1@bar.baz
From: from@foobarbaz.com
Subject: Your personal microbiome results are ready!
Body:

Dear participant,

We are pleased to announce that the results of the Student Microbiome Project (SMP) have been processed, and your personalized results are available via the "My Microbes" delivery system:

https://s3.amazonaws.com/my-microbes/index.html

Each participant in the study was given a unique, anonymous personal ID, which can be used to link each of your weekly samples back to you.

Your personal ID is foo1.

To view your personalized results, please visit the following link:

https://s3.amazonaws.com/my-microbes/foo1/index.html

The website has additional details on how to view and interpret your results.  If you have any questions, please send an email to student.microbiome@gmail.com.

Thanks for participating in the study!

The Student Microbiome Project Team"""


if __name__ == "__main__":
    main()
