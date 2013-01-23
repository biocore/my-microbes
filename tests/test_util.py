#!/usr/bin/env python
from __future__ import division

__author__ = "John Chase"
__copyright__ = "Copyright 2013, The QIIME project"
__credits__ = ["John Chase", "Greg Caporaso", "Jai Ram Rideout",
    "Yoshiki Vazquez-Baeza"]
__license__ = "GPL"
__version__ = "0.0.0-dev"
__maintainer__ = "John Chase"
__email__ = "jc33@nau.edu"

"""Test suite for the util.py module."""

import sys
from glob import glob
from os import chdir, getcwd
from os.path import abspath, basename, dirname, exists, isdir, isfile, join
from shutil import rmtree
from StringIO import StringIO
from tempfile import mkdtemp

from cogent.util.misc import remove_files
from cogent.util.unit_test import TestCase, main
from qiime.parse import parse_mapping_file
from qiime.util import create_dir, get_qiime_temp_dir, MetadataMap
from qiime.workflow import print_commands

from my_microbes.util import (_collect_alpha_diversity_boxplot_data,
                              create_personal_mapping_file,
                              create_personal_results,
                              get_personal_ids,
                              get_project_dir,
                              notify_participants)

class UtilTests(TestCase):
    """Tests for the util.py module."""

    def setUp(self):
        """Define some sample data that will be used by the tests."""
        # The prefix to use for temporary files. This prefix may be added to,
        # but all temp dirs and files created by the tests will have this
        # prefix at a minimum.
        self.prefix = 'my_microbes_tests_'

        self.start_dir = getcwd()
        self.dirs_to_remove = []
        self.files_to_remove = []

        self.tmp_dir = get_qiime_temp_dir()
        if not exists(self.tmp_dir):
            makedirs(self.tmp_dir)
            # If test creates the temp dir, also remove it.
            self.dirs_to_remove.append(self.tmp_dir)

        # Set up temporary input and output directories.
        self.input_dir = mkdtemp(dir=self.tmp_dir,
                                  prefix='%sinput_dir_' % self.prefix)
        self.dirs_to_remove.append(self.input_dir)

        self.output_dir = mkdtemp(dir=self.tmp_dir,
                                  prefix='%soutput_dir_' % self.prefix)
        self.dirs_to_remove.append(self.output_dir)

        # Data that will be used by the tests.
        self.metadata_map = MetadataMap.parseMetadataMap(
                mapping_str.split('\n'))
        self.mapping_data, self.mapping_header = parse_mapping_file(
                mapping_str.split('\n'))[:2]

        self.mapping_fp = join(self.input_dir, 'map.txt')
        mapping_f = open(self.mapping_fp, 'w')
        mapping_f.write(mapping_str)
        mapping_f.close()
        self.files_to_remove.append(self.mapping_fp)

        self.personal_metadata_map = MetadataMap.parseMetadataMap(
                personal_mapping_str.split('\n'))
        self.personal_mapping_data = parse_mapping_file(
                personal_mapping_str.split('\n'))[0]

        self.rarefaction_lines = collated_alpha_div_str.split('\n')
        self.na_rarefaction_lines = collated_alpha_div_na_str.split('\n')

        self.rarefaction_dir = join(self.input_dir, 'collated_adiv')
        create_dir(self.rarefaction_dir)
        self.rarefaction_fp = join(self.rarefaction_dir, 'PD_whole_tree.txt')
        rarefaction_f = open(self.rarefaction_fp, 'w')
        rarefaction_f.write(collated_alpha_div_str)
        rarefaction_f.close()
        self.files_to_remove.append(self.rarefaction_fp)

        self.coord_fp = join(self.input_dir, 'coord.txt')
        coord_f = open(self.coord_fp, 'w')
        coord_f.write(coord_str)
        coord_f.close()
        self.files_to_remove.append(self.coord_fp)

        self.otu_table_fp = join(self.input_dir, 'otu_table.biom')
        otu_table_f = open(self.otu_table_fp, 'w')
        otu_table_f.write(otu_table_str)
        otu_table_f.close()
        self.files_to_remove.append(self.otu_table_fp)

        self.prefs_fp = join(self.input_dir, 'prefs.txt')
        prefs_f = open(self.prefs_fp, 'w')
        prefs_f.write(prefs_str)
        prefs_f.close()
        self.files_to_remove.append(self.prefs_fp)

        self.recipients = ["# a comment", " ", " foo1\tfoo1@bar.baz  ",
                            "foo2\t foo2@bar.baz,  foo3@bar.baz,foo4@bar.baz "]

        self.email_settings = ["# A comment", "# Another comment",
                "smtp_server\tsome.smtp.server", "smtp_port\t42",
                "sender\tfrom@foobarbaz.com", "password\t424242!"]

    def tearDown(self):
        """Remove temporary files/dirs created by tests."""
        # Change back to the start dir - some workflows change directory.
        chdir(self.start_dir)

        remove_files(self.files_to_remove)
        # Remove directories last, so we don't get errors trying to remove
        # files which may be in the directories.
        for d in self.dirs_to_remove:
            if exists(d):
                rmtree(d)

    def test_get_personal_ids(self):
        """Test extracting a set of personal IDs."""
        exp = set(['NAU123', 'NAU789', 'NAU456'])
        obs = get_personal_ids(self.mapping_data, 2)
        self.assertEqual(obs, exp)

    def test_create_personal_mapping_file(self):
        """Test creating a personalized mapping file (adding a new column)."""
        obs = create_personal_mapping_file(self.mapping_data, 'NAU123', 2, 1)
        self.assertEqual(obs, self.personal_mapping_data)

    def test_create_personal_mapping_file_invalid_input(self):
        """Test creating a personalized mapping file given invalid input."""
        # Invalid number of individual_titles.
        self.assertRaises(ValueError, create_personal_mapping_file,
                self.mapping_data, 'NAU123', 2, 1,
                individual_titles=['Self', 'Other', 'SelfOther'])

        # Non-distinct individual_titles.
        self.assertRaises(ValueError, create_personal_mapping_file,
                self.mapping_data, 'NAU123', 2, 1,
                individual_titles=['Self', 'Self'])

    def test_create_personal_results_invalid_input(self):
        """Test running workflow on invalid input (should throw errors)."""
        # Invalid personal ID column name.
        self.assertRaises(ValueError, create_personal_results, self.output_dir,
                self.mapping_fp, self.coord_fp, self.rarefaction_dir,
                self.otu_table_fp, self.prefs_fp, 'foo')

        # Invalid category to split.
        self.assertRaises(ValueError, create_personal_results, self.output_dir,
                self.mapping_fp, self.coord_fp, self.rarefaction_dir,
                self.otu_table_fp, self.prefs_fp, 'PersonalID',
                category_to_split='foo')

        # Invalid personal IDs.
        self.assertRaises(ValueError, create_personal_results, self.output_dir,
                self.mapping_fp, self.coord_fp, self.rarefaction_dir,
                self.otu_table_fp, self.prefs_fp, 'PersonalID',
                personal_ids=['foo', 'bar'])

        # Invalid time series category.
        self.assertRaises(ValueError, create_personal_results, self.output_dir,
                self.mapping_fp, self.coord_fp, self.rarefaction_dir,
                self.otu_table_fp, self.prefs_fp, 'PersonalID',
                time_series_category='foo')

    def test_create_personal_results_suppress_all(self):
        """Test running workflow with all output types suppressed."""
        # No output directories should be created under each personal ID
        # directory. We should only end up with a log file, support_files
        # directory, directories for each personal ID, and an index.html file
        # in each.
        exp_personal_ids = ['NAU123', 'NAU456', 'NAU789']

        obs = create_personal_results(self.output_dir, self.mapping_fp,
                self.coord_fp, self.rarefaction_dir, self.otu_table_fp,
                self.prefs_fp, 'PersonalID',
                suppress_alpha_rarefaction=True,
                suppress_beta_diversity=True,
                suppress_taxa_summary_plots=True,
                suppress_alpha_diversity_boxplots=True,
                suppress_otu_category_significance=True)
        self.assertEqual(obs, [])

        num_logs = len(glob(join(self.output_dir, 'log_*.txt')))
        self.assertEqual(num_logs, 1)

        support_files_exist = isdir(join(self.output_dir, 'support_files'))
        self.assertTrue(support_files_exist)

        for personal_id in exp_personal_ids:
            personal_dir_exists = isdir(join(self.output_dir, personal_id))
            self.assertTrue(personal_dir_exists)

            personal_files = map(basename,
                                 glob(join(self.output_dir, personal_id, '*')))
            self.assertEqual(personal_files, ['index.html'])

    def test_create_personal_results_print_only(self):
        """Test running workflow, but only printing the commands."""
        # Save stdout and replace it with something that will capture the print
        # statement. Note: this code was taken from here:
        # http://stackoverflow.com/questions/4219717/how-to-assert-output-
        #     with-nosetest-unittest-in-python/4220278#4220278
        saved_stdout = sys.stdout
        exp_personal_ids = ['NAU123', 'NAU456', 'NAU789']

        try:
            out = StringIO()
            sys.stdout = out

            obs = create_personal_results(self.output_dir, self.mapping_fp,
                    self.coord_fp, self.rarefaction_dir, self.otu_table_fp,
                    self.prefs_fp, 'PersonalID', rarefaction_depth=10,
                    command_handler=print_commands)
            #self.assertEqual(obs, [])

            obs_output = out.getvalue().strip()
            #self.assertEqual(obs_output, exp_dry_run_output)

            #num_logs = len(glob(join(self.output_dir, 'log_*.txt')))
            #self.assertEqual(num_logs, 1)

            #support_files_exist = isdir(join(self.output_dir, 'support_files'))
            #self.assertTrue(support_files_exist)

            #for personal_id in exp_personal_ids:
            #    personal_dir_exists = isdir(join(self.output_dir, personal_id))
            #    self.assertTrue(personal_dir_exists)
#
#                personal_files = map(basename,
#                                     glob(join(self.output_dir, personal_id, '*')))
#                self.assertEqual(personal_files, ['index.html'])
        finally:
            sys.stdout = saved_stdout

        print obs
        print
        print obs_output

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
        # my_microbes/util.py here, to handle cases where either the
        # user has the delivery system in their PYTHONPATH, or when they've
        # installed it with setup.py.
        # If util.py moves this test will fail -- that 
        # is what we want in this case, as the get_project_dir()
        # function would need to be modified.
        import my_microbes.util
        util_py_filepath = abspath(abspath(my_microbes.util.__file__))
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
                self.personal_metadata_map, 10, 'BodySite', 'Self')
        self.assertFloatEqual(obs, exp)

    def test_collect_alpha_diversity_boxplot_data_invalid_depth(self):
        """Tests throws error on invalid rarefaction depth."""
        self.assertRaises(ValueError, _collect_alpha_diversity_boxplot_data,
                self.rarefaction_lines, self.personal_metadata_map, 42,
                'BodySite', 'Self')

    def test_collect_alpha_diversity_boxplot_data_na_values(self):
        """Tests correctly ignores n/a values in rarefaction file."""
        obs = _collect_alpha_diversity_boxplot_data(
                self.na_rarefaction_lines, self.personal_metadata_map, 10,
                'BodySite', 'Self')
        self.assertEqual(obs, ([], []))

mapping_str = """#SampleID\tBodySite\tPersonalID\tWeeksSinceStart\tDescription
S1\tPalm\tNAU123\t1\tS1
S2\tTongue\tNAU456\t2\tS2
S3\tPalm\tNAU789\t3\tS3
S4\tPalm\tNAU123\t4\tS4
S5\tTongue\tNAU123\t5\tS5
S6\tTongue\tNAU456\t6\tS6
S7\tTongue\tNAU123\t7\tS7
S8\tPalm\tNAU789\t8\tS8"""

personal_mapping_str = """#SampleID\tBodySite\tPersonalID\tWeeksSinceStart\tSelf\tSiteID\tDescription
S1\tPalm\tNAU123\t1\tSelf\tNAU123.Palm\tS1
S2\tTongue\tNAU456\t2\tOther\tNAU456.Tongue\tS2
S3\tPalm\tNAU789\t3\tOther\tNAU789.Palm\tS3
S4\tPalm\tNAU123\t4\tSelf\tNAU123.Palm\tS4
S5\tTongue\tNAU123\t5\tSelf\tNAU123.Tongue\tS5
S6\tTongue\tNAU456\t6\tOther\tNAU456.Tongue\tS6
S7\tTongue\tNAU123\t7\tSelf\tNAU123.Tongue\tS7
S8\tPalm\tNAU789\t8\tOther\tNAU789.Palm\tS8"""

collated_alpha_div_str = """\tsequences per sample\titeration\tS1\tS2\tS3\tS4\tS5\tS6\tS7\tS8
alpha_rarefaction_10_0.biom\t10\t0\t1\t2\t3\t4\t5\t6\t7\t8
alpha_rarefaction_10_1.biom\t10\t1\t9\t10\t11\t12\t13\t14\t15\t16"""

collated_alpha_div_na_str = """\tsequences per sample\titeration\tS1\tS2\tS3
alpha_rarefaction_10_0.biom\t10\t0\tn/a\tn/a\tn/a
alpha_rarefaction_10_1.biom\t10\t1\tn/a\tn/a\tn/a"""

coord_str = """pc vector number\t1\t2
S1\t1\t2
S2\t1\t2
S3\t1\t2
S4\t1\t2
S5\t1\t2
S6\t1\t2
S7\t1\t2
S8\t1\t2"""

otu_table_str = """foobarbaz"""

prefs_str = """foobarbaz"""

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
