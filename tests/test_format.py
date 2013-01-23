#!/usr/bin/env python
from __future__ import division

__author__ = "Jai Ram Rideout"
__copyright__ = "Copyright 2013, The QIIME Project"
__credits__ = ["Jai Ram Rideout", "John Chase"]
__license__ = "GPL"
__version__ = "0.0.0-dev"
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
        format_otu_category_significance_tables_as_html,
        format_participant_table,
        format_title,
        create_alpha_diversity_boxplots_html,
        create_otu_category_significance_html)

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

    def test_format_participant_table(self):
        """Test formatting an HTML table of study participants."""
        # Test URL prefix without trailing slash.
        exp = ('<table class="data-table">\n'
               '<tr><th>Personal ID</th></tr>\n'
               '<tr><td><a href="http://my-microbes.qiime.org/'
                 'foo1/index.html">foo1</a></td></tr>\n'
               '<tr><td><a href="http://my-microbes.qiime.org/'
                 'foo2/index.html">foo2</a></td></tr>\n'
               '</table>\n')
        obs = format_participant_table(self.recipients,
                                       'http://my-microbes.qiime.org')
        self.assertEqual(obs, exp)

        # Test URL prefix with trailing slash.
        obs = format_participant_table(self.recipients,
                                       'http://my-microbes.qiime.org/')
        self.assertEqual(obs, exp)

        # Test empty recipients file.
        exp = ('<table class="data-table">\n'
               '<tr><th>Personal ID</th></tr>\n'
               '</table>\n')
        obs = format_participant_table(self.empty_recipients,
                                       'http://my-microbes.qiime.org')
        self.assertEqual(obs, exp)
        
    def test_create_alpha_diversity_boxplots_html(self): 
        """Test alpha diversity boxplots"""
        input = ('pd.txt', 'chao.txt')
        exp = expected_alpha_diversity_boxplots
        self.assertEqual(create_alpha_diversity_boxplots_html(input), exp)
    
    def test_create_otu_category_significance_html(self): 
        """Test create_otu_category_significance"""
        input = ('gut.html', 'palm.html')
        exp = otu_category_significance_text
        self.assertEqual(create_otu_category_significance_html(input), exp)
    
    def test_format_otu_category_significance_tables_as_html(self): 
        """test that a value error is raised if number not between 0 and 1 is passed"""
        self.assertRaises(ValueError,
                          format_otu_category_significance_tables_as_html,
                          otu_category_significance_text, 10, 'output_dir',
                          ['Self','Other'])

        obs = format_otu_category_significance_tables_as_html(
                [self.otu_cat_sig_gut_fp, self.otu_cat_sig_palm_fp], 0.05,
                self.output_dir,['Self','Other'])
        self.assertEquals(obs, ['gut.html', 'palm.html'])

        out_f = open(join(self.output_dir, 'gut.html'), 'U')
        obs = out_f.read()
        out_f.close()
        self.assertEqual(obs, exp_otu_cat_sig_gut)

    def test_format_title(self):
        """Tests converting string to title."""
        self.assertEqual(format_title("observed_species"), "Observed Species")
        self.assertEqual(format_title("PD_whole_tree"), "PD Whole Tree")
        self.assertEqual(format_title("chao1"), "Chao1")
        self.assertEqual(format_title("shannon"), "Shannon")


expected_alpha_diversity_boxplots = """
<h2>Alpha Diversity Boxplots</h2>\nHere we present a series of comparative boxplots showing the distributions of your alpha diversity (<i>Self</i>) versus all other individuals\' alpha diversity (<i>Other</i>), for each body site. Alpha diversity refers to within sample diversity, and is a measure of the number of different types of organisms that are present in a given sample (i.e., the richness of the sample) or some other property of a single sample, such as the shape of the taxonomic distribution (i.e., the evenness of the sample). Here we look at richness using two measures: <i>Observed Species</i>, which is a count of the distinct Operational Taxonomic Units (OTUs) in a sample, and <i>Phylogenetic Diversity</i> (PD), which in our case is the sum of the branch length in a reference phylogenetic tree that is observed in a sample. PD is a phylogenetic measure of richness, meaning that the evolutionary relatedness of different organisms is taken into account via the phylogenetic tree, while observed species is a non-phylogenetic measure, meaning that all of the different organisms are treated as equally related.\n<br/><br/>\nYou should be able to answer several questions about your microbial communities from these plots:\n<ol>\n  <li>How rich are the microbial communities at your different body sites relative to the average for that body site in this study (e.g., is your gut community more diverse than the average gut community in this study)?</li>\n  <li>Which of your body sites is most diverse, and which is least diverse? Do other individuals exhibit the same pattern?</li>\n</ol>\n\n\n<h3>Click on the following links to see your alpha diversity boxplots:</h3>\n<ul>\n  <li><a href="pd.txt">Pd</a></li><li><a href="chao.txt">Chao</a></li>\n</ul>
"""

otu_category_significance_text = """
<h2>Differences in OTU Abundances</h2>\nHere we present <i>Operational Taxonomic Units (or OTUs)</i> that seemed to differ in their average relative abundance when comparing you to all other individuals in the study. An OTU is a functional definition of a taxonomic group, often based on percent identity of 16S rRNA sequences. In this study, we began with a reference collection of 16S rRNA sequences (derived from the <a href="http://greengenes.secondgenome.com">Greengenes database</a>), and each of those sequences was used to define an Opertational Taxonomic Unit. We then compared all of the sequence reads that we obtained in this study (from your microbial communities and everyone else\'s) to those reference OTUs, and if a sequence read matched one of those sequences at at least 97% identity, the read was considered an observation of that reference OTU. This process is one strategy for <i>OTU picking</i>, or assigning sequence reads to OTUs. \n<br/><br/>\nHere we present the OTUs that were most different in abundance in your microbial communities relative to those from other individuals. (These are not necessarily statistically significant, but rather just the most different.)\n\n<h3>Click on the following links to see what OTU abundances differed by body\nsite:</h3>\n<ul>\n  <li><a href="gut.html">Gut</a></li><li><a href="palm.html">Palm</a></li>\n</ul>
"""

otu_cat_sig_gut_text = """OTU	prob	Bonferroni_corrected	FDR_corrected	Self_mean	Other_mean	Consensus Lineage
198792	9.85322211031e-11	5.38971249434e-08	5.38971249434e-08	0.0000167	0.00249130434783	k__Bacteria;  p__Bacteroidetes;  c__Bacteroidia;  o__Bacteroidales;  f__Bacteroidaceae;  g__Bacteroides;  s__
175844	9.11665166989e-10	4.98680846343e-07	2.49340423172e-07	0.0101	4.34782608696e-05	k__Bacteria;  p__Bacteroidetes;  c__Bacteroidia;  o__Bacteroidales;  f__[Barnesiellaceae];  g__;  s__
205836	1.13930778482e-09	6.23201358295e-07	2.07733786098e-07	0.00583	0.000726086956522	k__Bacteria;  p__Bacteroidetes;  c__Bacteroidia;  o__Bacteroidales;  f__Bacteroidaceae;  g__Bacteroides;  s__"""

exp_otu_cat_sig_gut = """
<html>
<head>
  <link href="../../support_files/css/themes/start/jquery-ui.css" rel="stylesheet">
  <link href="../../support_files/css/main.css" rel="stylesheet">

  <script language="javascript" type="text/javascript">
    function gg(targetq) {
      window.open("http://www.google.com/search?q=" + targetq, 'searchwin');
    }
  </script>
</head>

<body>
  <div class="ui-tabs ui-widget ui-widget-content ui-corner-all text">
    <h2>Operational Taxonomic Units (OTUs) that differed in relative abundance in gut samples (comparing self
    versus other)</h2>
    Click on the taxonomy links for each OTU to do a google search for that taxonomic group. OTU IDs with an orange background are found in lower abundance in <i>Self</i> than in <i>Other</i>, and OTU IDs with a blue background are found in higher abundance in <i>Self</i> than in <i>Other</i>.
    <br/><br/>

    <table class="data-table">
      <tr>
        <th>OTU ID</th>
        <th>Taxonomy</th>
      </tr>
      <tr><td bgcolor=#FF9900>198792</td><td><a href=javascript:gg('Bacteria');>k__Bacteria</a>;<a href=javascript:gg('Bacteroidetes');>&nbsp;&nbsp;p__Bacteroidetes</a>;<a href=javascript:gg('Bacteroidia');>&nbsp;&nbsp;c__Bacteroidia</a>;<a href=javascript:gg('Bacteroidales');>&nbsp;&nbsp;o__Bacteroidales</a>;<a href=javascript:gg('Bacteroidaceae');>&nbsp;&nbsp;f__Bacteroidaceae</a>;<a href=javascript:gg('Bacteroides');>&nbsp;&nbsp;g__Bacteroides</a></td></tr>
<tr><td bgcolor=#99CCFF>175844</td><td><a href=javascript:gg('Bacteria');>k__Bacteria</a>;<a href=javascript:gg('Bacteroidetes');>&nbsp;&nbsp;p__Bacteroidetes</a>;<a href=javascript:gg('Bacteroidia');>&nbsp;&nbsp;c__Bacteroidia</a>;<a href=javascript:gg('Bacteroidales');>&nbsp;&nbsp;o__Bacteroidales</a>;<a href=javascript:gg('[Barnesiellaceae]');>&nbsp;&nbsp;f__[Barnesiellaceae]</a></td></tr>
<tr><td bgcolor=#99CCFF>205836</td><td><a href=javascript:gg('Bacteria');>k__Bacteria</a>;<a href=javascript:gg('Bacteroidetes');>&nbsp;&nbsp;p__Bacteroidetes</a>;<a href=javascript:gg('Bacteroidia');>&nbsp;&nbsp;c__Bacteroidia</a>;<a href=javascript:gg('Bacteroidales');>&nbsp;&nbsp;o__Bacteroidales</a>;<a href=javascript:gg('Bacteroidaceae');>&nbsp;&nbsp;f__Bacteroidaceae</a>;<a href=javascript:gg('Bacteroides');>&nbsp;&nbsp;g__Bacteroides</a></td></tr>

    </table>
  </div>
</body>
</html>
"""


if __name__ == "__main__":
    main()
