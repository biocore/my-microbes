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
from os.path import abspath, dirname, exists
from StringIO import StringIO
from cogent.util.unit_test import TestCase, main
from qiime.parse import parse_mapping_file
from qiime.util import MetadataMap

from personal_microbiome.util import (_collect_alpha_diversity_boxplot_data,
                                      create_personal_mapping_file,
                                      get_personal_ids,
                                      get_project_dir,
                                      notify_participants)

class UtilTests(TestCase):

    def setUp(self):
        # Define some data here...
        self.metadata_map = MetadataMap.parseMetadataMap(
                mapping_str.split('\n'))

        self.rarefaction_lines = collated_alpha_div_str.split('\n')
        self.na_rarefaction_lines = collated_alpha_div_na_str.split('\n')

        self.recipients = ["# a comment", " ", " foo1\tfoo1@bar.baz  ",
                            "foo2\t foo2@bar.baz,  foo3@bar.baz,foo4@bar.baz "]

        self.email_settings = ["# A comment", "# Another comment",
                "smtp_server\tsome.smtp.server", "smtp_port\t42",
                "sender\tfrom@foobarbaz.com", "password\t424242!"]

#    def test_get_personal_ids(self): 
#        """Does the function return correct output when given correct output"""
#        obs = get_personal_ids(self.mapping_data)
#        
#        column = 'PersonalID'
#        input  = [['A01393', 'GTTATCGCATGG', 'CCGGACTACHVGGGTWTCTAAT', 'student', 'na', 'na', 'armpit', 'CUB', 'CUB027'],
#                  ['A00994', 'CGGATAACCTCC', 'CCGGACTACHVGGGTWTCTAAT', 'student', 'na', 'na', 'armpit', 'NAU', 'NAU113'], 
#                  ['A00981', 'TAACGCTGTGTG', 'CCGGACTACHVGGGTWTCTAAT', 'student', 'na', 'na', 'armpit', 'NAU', 'NAU133'], 
#                  ['A00936', 'ATTGACCGGTCA', 'CCGGACTACHVGGGTWTCTAAT', 'student', 'na', 'na', 'armpit', 'NAU', 'NAU144'], 
#                  ['A01497', 'AGCGCTCACATC', 'CCGGACTACHVGGGTWTCTAAT', 'student', 'na', 'na', 'armpit', 'NCS', 'NCS210'], 
#                  ['A00663', 'CTCATCATGTTC', 'CCGGACTACHVGGGTWTCTAAT', 'student', 'na', 'na', 'armpit', 'NCS', 'NCS214'], 
#                  ['A01367', 'GCAACACCATCC', 'CCGGACTACHVGGGTWTCTAAT', 'student', 'na', 'na', 'armpit', 'CUB', 'CUB000'], 
#                  ['A01383', 'GCTTGAGCTTGA', 'CCGGACTACHVGGGTWTCTAAT', 'student', 'na', 'na', 'armpit', 'CUB', 'CUB003'], 
#                  ['A01332', 'AGTAGCGGAAGA', 'CCGGACTACHVGGGTWTCTAAT', 'student', 'na', 'na', 'armpit', 'CUB', 'CUB004']]
#        expected = ['CUB027', 'NAU113', 'NAU133', 'NAU144', 'NCS210', 'NCS214', 'CUB000', 'CUB003', 'CUB004']
#        self.assertEqual(get_personal_ids(input, 8), expected)
#        
#    def test_create_personal_mapping_file(self): 
#        """Does the function return correct output when given correct input?"""
#        map_as_list = [['A01393', 'GTTATCGCATGG', 'CCGGACTACHVGGGTWTCTAAT', 'student', 'na', 'na', 'armpit', 'CUB', 'CUB027'],
#                       ['A00994', 'CGGATAACCTCC', 'CCGGACTACHVGGGTWTCTAAT', 'student', 'na', 'na', 'armpit', 'NAU', 'NAU113'], 
#                       ['A00981', 'TAACGCTGTGTG', 'CCGGACTACHVGGGTWTCTAAT', 'student', 'na', 'na', 'armpit', 'NAU', 'NAU133'], 
#                       ['A00936', 'ATTGACCGGTCA', 'CCGGACTACHVGGGTWTCTAAT', 'student', 'na', 'na', 'armpit', 'NAU', 'NAU144'], 
#                       ['A01497', 'AGCGCTCACATC', 'CCGGACTACHVGGGTWTCTAAT', 'student', 'na', 'na', 'armpit', 'NCS', 'NCS210'], 
#                       ['A00663', 'CTCATCATGTTC', 'CCGGACTACHVGGGTWTCTAAT', 'student', 'na', 'na', 'armpit', 'NCS', 'NCS214'], 
#                       ['A01367', 'GCAACACCATCC', 'CCGGACTACHVGGGTWTCTAAT', 'student', 'na', 'na', 'armpit', 'CUB', 'CUB000'], 
#                       ['A01383', 'GCTTGAGCTTGA', 'CCGGACTACHVGGGTWTCTAAT', 'student', 'na', 'na', 'armpit', 'CUB', 'CUB003'], 
#                       ['A01332', 'AGTAGCGGAAGA', 'CCGGACTACHVGGGTWTCTAAT', 'student', 'na', 'na', 'armpit', 'CUB', 'CUB004']]
#        header = ['SampleID', 'BarcodeSequence', 'LinkerPrimerSequence', 'Study', 'HouseZipCode', 'SamplingLocation', 'BodyHabitat', 'University', 'PersonalID']
#        comments = [] 
#        personal_id_of_interest = 'CUB027'
#        "So how do I write something out to file here and then check to make sure that is correct?"
#        output_fp
#        personal_id_index = 8
#        individual_titles=None

    def test_get_qiime_project_dir(self):
        """getting the qiime project directory functions as expected
        
        Taken from QIIME's (https://github.com/qiime/qiime)
        tests.test_util.test_get_qiime_project_dir.
        """
        
        # Do an explicit check on whether the file system containing
        # the current file is case insensitive. This is in response
        # to SF bug #2945548, where this test would fail on certain
        # unusual circumstances on case-insensitive file systems
        # because the case of abspath(__file__) was inconsistent. 
        # (If you don't believe this, set case_insensitive_filesystem
        # to False, and rename your top-level Qiime directory as 
        # qiime on OS X. That sould cause this test to fail as 
        # actual will be path/to/qiime and expected will be 
        # path/to/Qiime.) Note that we don't need to change anything
        # in the get_project_dir() function as if the 
        # file system is case insenstive, the case of the returned
        # string is irrelevant.
        case_insensitive_filesystem = \
         exists(__file__.upper()) and exists(__file__.lower())
         
        actual = get_project_dir()
        # I base the expected here off the imported location of
        # personal_microbiome/util.py here, to handle cases where either the
        # user has the delivery system in their PYTHONPATH, or when they've
        # installed it with setup.py.
        # If util.py moves this test will fail -- that 
        # is what we want in this case, as the get_project_dir()
        # function would need to be modified.
        import personal_microbiome.util
        util_py_filepath = abspath(abspath(personal_microbiome.util.__file__))
        expected = dirname(dirname(util_py_filepath))
        
        if case_insensitive_filesystem:
            # make both lowercase if the file system is case insensitive
            actual = actual.lower()
            expected = expected.lower()
        self.assertEqual(actual,expected)

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

    def test_collect_alpha_diversity_boxplot_data(self):
        """Tests collecting data for creating boxplots."""
        exp = (['Palm (Other)', 'Palm (Self)', 'Tongue (Other)',
                'Tongue (Self)'], [[3.0, 8.0, 11.0, 16.0],
                [1.0, 4.0, 9.0, 12.0], [2.0, 6.0, 10.0, 14.0],
                [5.0, 7.0, 13.0, 15.0]])

        obs = _collect_alpha_diversity_boxplot_data(self.rarefaction_lines,
                self.metadata_map, 10, 'BodySite', 'Self')
        self.assertFloatEqual(obs, exp)

    def test_collect_alpha_diversity_boxplot_data_invalid_depth(self):
        """Tests throws error on invalid rarefaction depth."""
        self.assertRaises(ValueError, _collect_alpha_diversity_boxplot_data,
                self.rarefaction_lines, self.metadata_map, 42, 'BodySite',
                'Self')

    def test_collect_alpha_diversity_boxplot_data_na_values(self):
        """Tests correctly ignores n/a values in rarefaction file."""
        obs = _collect_alpha_diversity_boxplot_data(
                self.na_rarefaction_lines, self.metadata_map, 10, 'BodySite',
                'Self')
        self.assertEqual(obs, ([], []))


mapping_str = """#SampleID\tBodySite\tSelf\tDescription
S1\tPalm\tSelf\tS1
S2\tTongue\tOther\tS2
S3\tPalm\tOther\tS3
S4\tPalm\tSelf\tS4
S5\tTongue\tSelf\tS5
S6\tTongue\tOther\tS6
S7\tTongue\tSelf\tS7
S8\tPalm\tOther\tS8"""

collated_alpha_div_str = """\tsequences per sample\titeration\tS1\tS2\tS3\tS4\tS5\tS6\tS7\tS8
alpha_rarefaction_10_0.biom\t10\t0\t1\t2\t3\t4\t5\t6\t7\t8
alpha_rarefaction_10_1.biom\t10\t1\t9\t10\t11\t12\t13\t14\t15\t16"""

collated_alpha_div_na_str = """\tsequences per sample\titeration\tS1\tS2\tS3
alpha_rarefaction_10_0.biom\t10\t0\tn/a\tn/a\tn/a
alpha_rarefaction_10_1.biom\t10\t1\tn/a\tn/a\tn/a"""

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

The website has additional details on how to view and interpret your results. If you have any questions, please send an email to student.microbiome@gmail.com.

Thanks for participating in the study!

The Student Microbiome Project Team"""


if __name__ == "__main__":
    main()
