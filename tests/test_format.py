#!/usr/bin/env python
from __future__ import division

__author__ = "Jai Ram Rideout"
__copyright__ = "Copyright 2013, The QIIME Project"
__credits__ = ["Jai Ram Rideout", "John Chase"]
__license__ = "GPL"
__version__ = "0.1.0"
__maintainer__ = "Jai Ram Rideout"
__email__ = "jai.rideout@gmail.com"

"""Test suite for the format.py module."""

from unittest import main, TestCase
from os import chdir, getcwd
from qiime.util import create_dir, get_qiime_temp_dir
from os.path import exists, join
from tempfile import mkdtemp
from shutil import rmtree

from cogent.util.misc import remove_files

from my_microbes.format import (
        _create_alpha_diversity_boxplots_links,
        create_otu_category_significance_html_tables,
        _create_otu_category_significance_links,
        _create_taxa_summary_plots_links,
        format_htaccess_file,
        _format_otu_category_significance_tables_as_html,
        format_participant_list,
        format_title)

class FormatTests(TestCase):
    """Tests for the format.py module."""
    
    def setUp(self):
        """Define some sample data that will be used by the tests."""
        # Standard recipients file with two recipients, one with multiple email
        # addresses.
        self.recipients = ["# a comment", " ", " foo1\tfoo@bar.baz  ",
                           "foo2\t foo2@bar.baz,  foo3@bar.baz,foo4@bar.baz "]

        # An empty recipients file.
        self.empty_recipients = ["# a comment", " ", "\n\t\t\t\t"]

        # Standard participants list.
        self.participants = ["# a comment", " ", " foo1  ", "foo2"]

        # Invalid (duplicate) participants list.
        self.duplicate_participants = ["foo1", "foo2", "foo1"]
        
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
        self.output_dir = mkdtemp(dir=self.tmp_dir,
                                  prefix='%soutput_dir_' % self.prefix)
        self.dirs_to_remove.append(self.output_dir)
        
        # Set up temporary input and output directories.
        self.input_dir = mkdtemp(dir=self.tmp_dir,
                                  prefix='%sinput_dir_' % self.prefix)
        self.dirs_to_remove.append(self.input_dir)

        # Data that will be used by the tests.
        self.otu_cat_sig_gut_fp = join(self.input_dir, 'otu_cat_sig_gut.txt')
        otu_cat_sig_gut_f = open(self.otu_cat_sig_gut_fp, 'w')
        otu_cat_sig_gut_f.write(otu_cat_sig_gut_text)
        otu_cat_sig_gut_f.close()
        self.files_to_remove.append(self.otu_cat_sig_gut_fp)
        
        self.otu_cat_sig_palm_fp = join(self.input_dir, 'otu_cat_sig_palm.txt')
        otu_cat_sig_palm_f = open(self.otu_cat_sig_palm_fp, 'w')
        otu_cat_sig_palm_f.write(otu_cat_sig_gut_text)
        otu_cat_sig_palm_f.close()
        self.files_to_remove.append(self.otu_cat_sig_palm_fp)

        self.rep_seqs_fp = join(self.input_dir, 'rep_seqs.fna')
        rep_seqs_f = open(self.rep_seqs_fp, 'w')
        rep_seqs_f.write(rep_seqs_text)
        rep_seqs_f.close()
        self.files_to_remove.append(self.rep_seqs_fp)

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

    def test_format_participant_list(self):
        """Test formatting an HTML list of study participants."""
        # Test URL prefix without trailing slash.
        exp = ('<ul>\n'
               '  <li><a href="http://my-microbes.qiime.org/'
               'foo1/index.html" target="_blank">foo1</a></li>\n'
               '  <li><a href="http://my-microbes.qiime.org/'
               'foo2/index.html" target="_blank">foo2</a></li>\n'
               '</ul>\n')
        obs = format_participant_list(self.recipients,
                                      'http://my-microbes.qiime.org')
        self.assertEqual(obs, exp)

        # Test URL prefix with trailing slash.
        obs = format_participant_list(self.recipients,
                                      'http://my-microbes.qiime.org/')
        self.assertEqual(obs, exp)

        # Test standard single-column format.
        obs = format_participant_list(self.participants,
                                      'http://my-microbes.qiime.org')
        self.assertEqual(obs, exp)

        # Test empty recipients file.
        exp = '<ul>\n</ul>\n'
        obs = format_participant_list(self.empty_recipients,
                                      'http://my-microbes.qiime.org')
        self.assertEqual(obs, exp)

        # Test invalid participants file.
        self.assertRaises(ValueError, format_participant_list,
                          self.duplicate_participants,
                          'http://my-microbes.qiime.org')

    def test_create_taxa_summary_plots_links(self):
        """Test creating links to taxa summary plots."""
        obs = _create_taxa_summary_plots_links('/foobarbaz', 'foo123',
                                               ['tongue', 'forehead'])
        self.assertEqual(obs, '<table cellpadding="5px">\n</table>\n')

    def test_create_alpha_diversity_boxplots_links(self): 
        """Test creating links to alpha diversity boxplots."""
        filenames = ('pd.txt', 'chao.txt', 'observed_species.txt')
        self.assertEqual(_create_alpha_diversity_boxplots_links(filenames),
                         expected_alpha_diversity_boxplots_links)

    def test_create_otu_category_significance_links(self): 
        """Test creating links to OTU category significance tables."""
        filenames = ('gut.html', 'palm.html')
        self.assertEqual(_create_otu_category_significance_links(filenames),
                         expected_otu_category_significance_links)

    def test_create_otu_category_significance_html_tables(self):
        obs = create_otu_category_significance_html_tables(
                [self.otu_cat_sig_gut_fp, self.otu_cat_sig_palm_fp], 0.05,
                self.output_dir,['Self','Other'], rep_set_fp=self.rep_seqs_fp)

        self.assertEqual(obs, ['gut.html', 'palm.html'])

    def test_format_otu_category_significance_tables_as_html(self): 
        """Test that an error is raised if alpha not between 0 and 1."""
        self.assertRaises(ValueError,
                          _format_otu_category_significance_tables_as_html,
                          [self.otu_cat_sig_gut_fp, self.otu_cat_sig_palm_fp],
                          10, ['Self','Other'])

        exp = {'gut': (expected_otu_cat_sig_table_html,
                       expected_otu_cat_sig_rep_seq_html)}
        obs = _format_otu_category_significance_tables_as_html(
                [self.otu_cat_sig_gut_fp], 0.05,
                ['Self','Other'], rep_set_fp=self.rep_seqs_fp)
        self.assertEqual(obs, exp)

    def test_format_title(self):
        """Tests converting string to title."""
        self.assertEqual(format_title("observed_species"), "Observed Species")
        self.assertEqual(format_title("chao1"), "Chao1")
        self.assertEqual(format_title("shannon"), "Shannon")

        # Test special mapping.
        self.assertEqual(format_title("PD_whole_tree"),
                         "Phylogenetic Diversity")

    def test_format_htaccess_file(self):
        """Tests correctly formatting a .htaccess file."""
        # With trailing slash.
        obs = format_htaccess_file('/foo/bar/baz/', 'NAU123')
        self.assertEqual(obs, expected_htaccess_file)

        # Without trailing slash.
        obs = format_htaccess_file('/foo/bar/baz', 'NAU123')
        self.assertEqual(obs, expected_htaccess_file)


# Input test data.
otu_cat_sig_gut_text = """OTU\tprob\tBonferroni_corrected\tFDR_corrected\tSelf_mean\tOther_mean\tConsensus Lineage
198792\t9.85322211031e-11\t5.38971249434e-08\t5.38971249434e-08\t0.0000167\t0.00249130434783\tk__Bacteria;  p__Bacteroidetes;  s__
175844\t9.11665166989e-10\t4.98680846343e-07\tNA\t0.0101\t4.34782608696e-05\tk__foo; p__bar;  c__;  o__"""

rep_seqs_text = """>175844 PC.635_779
TTGGACCGT"""

# Expected output.
expected_alpha_diversity_boxplots_links = """<ul>
<li><a href="pd.txt" target="_blank">Pd</a></li>
<li><a href="chao.txt" target="_blank">Chao</a></li>
<li><a href="observed_species.txt" target="_blank">Observed Species</a></li>
</ul>
"""

expected_otu_category_significance_links = """<ul>
<li><a href="gut.html" target="_blank">Gut</a></li>
<li><a href="palm.html" target="_blank">Palm</a></li>
</ul>
"""

expected_otu_cat_sig_table_html = """<table class="data-table">
<tr>
<th>OTU ID</th>
<th>Taxonomy</th>
</tr>
<tr>
<td bgcolor=#FF9900>198792</td>
<td><a href=javascript:gg(\'Bacteria\');>k__Bacteria</a>;<a href=javascript:gg(\'Bacteroidetes\');>&nbsp;&nbsp;p__Bacteroidetes</a></td>
</tr>
<tr>
<td bgcolor=#99CCFF><a href="#" id="175844" onclick="openDialog(\'175844-rep-seq\', \'175844\'); return false;">175844</a></td>
<td><a href=javascript:gg(\'foo\');>k__foo</a>;<a href=javascript:gg(\'bar\');>&nbsp;p__bar</a></td>
</tr>
</table>
"""

expected_otu_cat_sig_rep_seq_html = """<div id="175844-rep-seq" class="rep-seq-dialog" title="Representative Sequence for OTU ID 175844">
<pre>&gt;175844
TTGGACCGT</pre>
</div>
"""

expected_htaccess_file = """AuthUserFile /foo/bar/baz/.htpasswd
AuthGroupFile /dev/null
AuthName "Please log in to view your personalized results"
AuthType Basic

require user NAU123
"""


if __name__ == "__main__":
    main()
