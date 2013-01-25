#!/usr/bin/env python
from __future__ import division

__author__ = "John Chase"
__copyright__ = "Copyright 2013, The QIIME project"
__credits__ = ["John Chase", "Greg Caporaso", "Jai Ram Rideout"]
__license__ = "GPL"
__version__ = "0.0.0-dev"
__maintainer__ = "John Chase"
__email__ = "jc33@nau.edu"

from os.path import basename, join, splitext

from cogent.parse.fasta import MinimalFastaParser

from my_microbes.parse import parse_recipients

index_text = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
  <head>
    <link href="../support_files/css/themes/start/jquery-ui.css" rel="stylesheet">
    <link href="../support_files/css/main.css" rel="stylesheet">

    <script src="../support_files/js/jquery.js"></script>
    <script src="../support_files/js/jquery-ui.js"></script>
    <script>
      $(function() {
        $("#tabs").tabs({
          select: function(event, ui) {                   
            window.location.hash = ui.tab.hash;
          }
        });
      });
    </script>

    <title>My Microbes: %s</title>
  </head>

  <body class="ui-widget">
    <div id="header">
      <img src="../support_files/images/my_microbes.png"/>
      <br/>
      <div class="ui-tabs ui-widget ui-widget-content ui-corner-all text">
        <center><h1>Personalized Results for %s</h1></center>
        <p>
          Below are links to your personal microbiome data, along with descriptions that should help you interpret those results. As our analyses progress, we may have periodic updates to the data on this page. We'll alert you to those new data as they're available. If you have questions about your results, you can get in touch by email at <a href="mailto:student.microbiome@gmail.com">student.microbiome@gmail.com</a>.
        </p>
        <center>
          <noscript>
            <h2 class="error">You <em>must</em> have JavaScript enabled to use My Microbes.</h2>
          </noscript>

          <!--[if ie]>
            <br/><br/>
            <h2 class="error">Internet Explorer is not a recommened browser to use with My Microbes. We recommend using either Firefox or Safari.</h2>
          <![endif]-->
        </center>
      </div>
    </div>
    <br/>

    <div id="tabs">
      <ul>
        <li><a href="#taxonomic-composition">Taxonomic Composition</a></li>
        <li><a href="#beta-diversity">Beta Diversity</a></li>
        <li><a href="#alpha-diversity-boxplots">Alpha Diversity Boxplots</a></li>
        <li><a href="#differential-otus">Differential OTUs</a></li>
        <li><a href="#alpha-rarefaction">Alpha Rarefaction</a></li>
      </ul>

      <div id="taxonomic-composition">
        <h2>Taxonomic Composition</h2>
        Here we present the taxonomic composition of each body site (on the y-axis) over time (on the x-axis) for you (<i>Self</i>) versus the average of all other participants in the study (<i>Other</i>). The composition is provided at different taxonomic levels, from Phylum to Genus. This allows you to quickly get an idea of the temporal variability in your microbial communities, and determine which taxonomic groups are coming and going in your different body habitats.
        <br/><br/>
        You should be able to answer several questions from these plots:
        <ol>
          <li>What was the dominant phylum in your gut on the first week that you donated a sample?</li>
          <li>Was the dominant phylum in your gut the same over all weeks, or did it change with time?</li>
          <li>Was the dominant phylum in each of your body sites the same as the average across the other individuals?</li>
          <li>Does the composition of each of your body sites look consistent over time, or do certain groups appear to bloom and then die off?</li>
        </ol>

        <h3>Click on the following links to see your taxonomic summary plots:</h3>
        <table cellpadding="5px">
          <tr>
            <td><b>Tongue:</b></td>
            <td><a href="time_series/taxa_plots_Self_tongue/taxa_summary_plots/area_charts.html">Self</a></td>
            <td><a href="time_series/taxa_plots_Other_tongue/taxa_summary_plots/area_charts.html">Other</a></td><td><a href="time_series/tongue_comparative.html">Self versus Other</a></td>
          </tr>
          <tr>
            <td><b>Palm:</b></td>
            <td><a href="time_series/taxa_plots_Self_palm/taxa_summary_plots/area_charts.html">Self</a></td>
            <td><a href="time_series/taxa_plots_Other_palm/taxa_summary_plots/area_charts.html">Other</a></td>
            <td><a href="time_series/palm_comparative.html">Self versus Other</a></td>
          </tr>
          <tr>
            <td><b>Gut:</b></td>
            <td><a href="time_series/taxa_plots_Self_gut/taxa_summary_plots/area_charts.html">Self</a></td>
            <td><a href="time_series/taxa_plots_Other_gut/taxa_summary_plots/area_charts.html">Other</a></td>
            <td><a href="time_series/gut_comparative.html">Self versus Other</a></td>
          </tr>
          <tr>
            <td><b>Forehead:</b></td>
            <td><a href="time_series/taxa_plots_Self_forehead/taxa_summary_plots/area_charts.html">Self</a></td>
            <td><a href="time_series/taxa_plots_Other_forehead/taxa_summary_plots/area_charts.html">Other</a></td>
            <td><a href="time_series/forehead_comparative.html">Self versus Other</a></td>
          </tr>
        </table>
      </div>

      <div id="beta-diversity">
        <h2>Beta Diversity</h2>
        Beta diversity measures between sample diversity, in contrast to alpha (or within-sample) diversity.  For example, if you have human gut microbial communities from three individuals, a beta diversity metric will tell you the relative similarity or dissimilarity of those samples: perhaps that individual <i>A</i> is more similar to individual <i>B</i> than either is to individual <i>C</i>. Ecologists use many different metrics to measure beta diversity - the metric we use here is called UniFrac (see <a href="http://www.ncbi.nlm.nih.gov/pubmed/16332807">Lozupone and Knight, 2005</a> for a discussion of UniFrac).
        <br/><br/>
        Because we're often looking at more than three samples (for example, in the Student Microbiome Project we compared over 3700 samples) ecologists often use ordination techniques to summarize pairwise distances between samples in a two- or three-dimensional scatter plot. In an ordination plot, points that are closer to each other in space are more similar to one another, and points that are more distant from one another are more dissimilar.
        <br/><br/>
        The plots presented here allow you to view the general clustering patterns observed in the Student Microbiome Project. We have colored these ordination plots so forehead samples are yellow, palm samples are orange, gut samples are blue and tongue samples are red. You can tell your samples from those of the rest of the participants as yours are colored in lighter shades of the same colors.
        <br/><br/>
        You should be able to answer several questions from these plots:
        <ol>
          <li>Which is more similar: microbial communities from the same body site but from different individuals, or microbial communities from different body sites but from the same individual?</li>
          <li>Do your microbial communities look typical of each body site, or are they outliers?</li>
          <li>Which body sites exhibit the most variability across individuals?</li> 
        </ol>
        While many of the results apparent in this ordination plot were already known, the unprecedented number of indivduals and timepoints in the Student Microbiome Project data set allows us to address more sophisticated questions. For example, we are using these results to determine whether microbial communities of males or females more variable through time, if there are geographical differences in community composition that are visible across the three universities, and the affects of antibiotic usage and other <i>disturbances</i> on the composition of microbial communities. These are just a few examples that illustrate the utility of beta diversity analyses and the uniqueness of our dataset.

        <h3>Click <a href="./beta_diversity/unweighted_unifrac_pc_3D_PCoA_plots.html">here</a> to see your beta diversity PCoA plots.</h3>
      </div>

      <div id="alpha-diversity-boxplots">%s</div>

      <div id="differential-otus">%s</div>

      <div id="alpha-rarefaction">
        <h2>Alpha Rarefaction</h2>
        Alpha rarefaction plots are a tool for interpreting measures of alpha diversity. Alpha diversity refers to within sample diversity, and is a measure of the number of different types of organisms that are present in a given sample (i.e., the richness of the sample) or some other property of a single sample, such as the shape of the taxonomic distribution (i.e., the evenness of the sample). Here we look at richness using two measures: <i>Observed Species</i>, which is a count of the distinct Operational Taxonomic Units (OTUs) in a sample, and <i>Phylogenetic Diversity</i> (PD), which in our case is the sum of the branch length in the Greengenes tree that is observed in a sample. PD is a phylogenetic measure, meaning that the evolutionary relatedness of different organisms is taken into account via the phylogenetic tree, while observed species is a non-phylogenetic measure, meaning that all of the different organisms are treated as equally related.
        <br/><br/>
        Alpha rarefaction plots show the alpha diversity at different depths of sampling (i.e., as if different numbers of sequences were collected). This is done because a measure of richness is very dependent on how much sampling effort was applied. For example, in macro-scale ecology, if you're interested in counting the number of different insect species in a rain forest, you would likely get a very different answer if you counted the number of insect species in a square meter versus a square kilometer. The analog to area in sequence-based studies of microbial ecology is the number of sequences collected. An alpha rarefaction plot presents the alpha diversity (y-axis) at different depths of sampling (or number of sequences collected; x-axis).
        <br/><br/>
        You should be able to answer several questions about your microbial communities from these plots:
        <ol>
          <li>How rich are the microbial communities at your different body sites relative to the average for that body site (e.g., is your gut community more diverse than the average gut community)?</li>
          <li>Which of your body sites is most diverse, and which is least diverse? Do others exhibit the same pattern?</li>
          <li>If we were to collect more sequences per sample, do you expect that your answers to questions 1 and 2 would change?</li>
        </ol>

        <h3>Click <a href="./alpha_rarefaction/rarefaction_plots.html">here</a> to see your alpha rarefaction plots. Select an alpha diversity metric from the first drop-down menu, and then a category from the second menu.</h3>
      </div>
    </div>

    <div id="footer">
      <br/>
      <div class="ui-tabs ui-widget ui-widget-content ui-corner-all text">
        <center>
          <p>
            Thanks for participating in the study! Please direct any questions to
            <a href="mailto:student.microbiome@gmail.com">student.microbiome@gmail.com</a>.
          </p>
          <h3>Powered by:</h3>
          <table>
            <tr>
              <td>
                <a href="http://www.qiime.org">
                  <img src="../support_files/images/qiime_logo.png" width="143px" height="46px"/>
                </a>
              </td>
              <td>
                <a href="http://www.pycogent.org">
                  <img src="../support_files/images/pycogent_logo.jpg" width="65" height="69"/>
                </a>
              </td>
              <td>
                <a href="http://biom-format.org">
                  <img src="../support_files/images/biom_format_logo.png" width="65" height="69"/>
                </a>
              </td>
              <td>
                <a href="http://www.jquery.com">
                  <img src="../support_files/images/jquery_logo.png" width="143px" height="46px"/>
                </a>
              </td>
              <td>
                <a href="http://www.jqueryui.com">
                  <img src="../support_files/images/jquery_ui_logo.jpg" width="143px" height="46px"/>
                </a>
              </td>
            </tr>
          </table>
          &copy; Copyright 2013, The QIIME Team.
        </center>
      </div>
    </div>
 </body>
</html>
"""

notification_email_subject = "Your personal microbiome results are ready!"

notification_email_text = """
Dear participant,

We are pleased to announce that the results of the Student Microbiome Project (SMP) have been processed, and your personalized results are available via the "My Microbes" delivery system:

https://s3.amazonaws.com/my-microbes/index.html

Each participant in the study was given a unique, anonymous personal ID, which can be used to link each of your weekly samples back to you.

Your personal ID is %s.

To view your personalized results, please visit the following link:

https://s3.amazonaws.com/my-microbes/%s/index.html

The website has additional details on how to view and interpret your results. If you have any questions, please send an email to student.microbiome@gmail.com.

Thanks for participating in the study!

The Student Microbiome Project Team
"""

def get_personalized_notification_email_text(personal_id):
    """Returns the text for the body of an email based on personal ID."""
    return notification_email_text % (personal_id, personal_id)

def create_index_html(personal_id, output_fp,
                      alpha_diversity_boxplots_html='',
                      otu_category_significance_html=''):
    output_f = open(output_fp,'w')
    output_f.write(index_text % (personal_id, personal_id,
                                 alpha_diversity_boxplots_html,
                                 otu_category_significance_html))
    output_f.close()

# This javascript synchronizes the scrolling of the two iframes. It has been
# tested in Chrome, Safari, and Firefox. It will work in all browsers when
# hosted (i.e. not opened locally). If opened locally, Chrome will not support
# synchronized scrolling because it does not allow javascript to access
# properties of the iframes on the local machine for security reasons. In this
# case, all other aspects of the page continue to function, but synchronized
# scrolling is disabled. This issue can be circumvented in Chrome by starting
# it with the --allow-file-access-from-files flag. Firefox and Safari support
# synchronized scrolling when run locally.
#
# See http://stackoverflow.com/a/5664399 for more details.
comparative_taxa_plots_text = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
  <link href="../../support_files/css/themes/start/jquery-ui.css" rel="stylesheet">
  <link href="../../support_files/css/main.css" rel="stylesheet">

  <script language="javascript" type="text/javascript">
    function init() {
      document.getElementById("selfIFrame").contentWindow.onscroll = syncOther;
      document.getElementById("otherIFrame").contentWindow.onscroll = syncSelf;
    }

    function syncSelf() {
      selfContent = document.getElementById("selfIFrame").contentWindow;
      otherContent = document.getElementById("otherIFrame").contentWindow;
      selfContent.scrollTo(otherContent.scrollX, otherContent.scrollY);
    }

    function syncOther() {
      selfContent = document.getElementById("selfIFrame").contentWindow;
      otherContent = document.getElementById("otherIFrame").contentWindow;
      otherContent.scrollTo(selfContent.scrollX, selfContent.scrollY);
    }
  </script>
</head>

<body onload="init()">
  <div class="ui-tabs ui-widget ui-widget-content ui-corner-all text">
    <h2>%s taxonomic composition plots (comparing self versus other)</h2>
    The two panels below show taxonomic composition plots for yourself and all
    other individuals in the study, respectively. The x-axis contains the week
    number that the samples were taken from so that you can see how the community
    composition changes over time.
    <br/><br/>
    The two panels are synchronized such that when you scroll one, the other will
    also scroll. This makes it easier to compare your results to all other
    individuals in the study.
  </div>

  <h3>%s taxonomic composition by weeks since experiment start (self)</h3>
  <div style="margin: 0 auto; width:90%%; height:48%%">
    <iframe id="selfIFrame"
            src="taxa_plots_Self_%s/taxa_summary_plots/area_charts.html"
            frameborder="0" style="width:100%%; height:100%%; margin:1%%;"
            scrolling="auto">
    </iframe>
  </div>

  <h3>%s taxonomic composition by weeks since experiment start (other; average)</h3>
  <div style="margin: 0 auto; width:90%%; height:48%%;">
    <iframe id="otherIFrame"
            src="taxa_plots_Other_%s/taxa_summary_plots/area_charts.html"
            frameborder="0" style="width:100%%; height:100%%; margin:1%%;"
            scrolling="auto">
    </iframe>
  </div>
</body>
</html>
"""

def create_comparative_taxa_plots_html(category, output_fp):
    output_f = open(output_fp,'w')
    output_f.write(comparative_taxa_plots_text % (category.title(),
            category.title(), category, category.title(), category))
    output_f.close()

def create_alpha_diversity_boxplots_html(plot_fps):
    plot_links_text = ''

    for plot_fp in plot_fps:
        adiv_metric_title = format_title(splitext(basename(plot_fp))[0])
        plot_links_text += '<li><a href="%s">%s</a></li>' % (plot_fp,
                                                             adiv_metric_title)

    return alpha_diversity_boxplots_text % plot_links_text

alpha_diversity_boxplots_text = """
<h2>Alpha Diversity Boxplots</h2>
Here we present a series of comparative boxplots showing the distributions of your alpha diversity (<i>Self</i>) versus all other individuals' alpha diversity (<i>Other</i>), for each body site. Alpha diversity refers to within sample diversity, and is a measure of the number of different types of organisms that are present in a given sample (i.e., the richness of the sample) or some other property of a single sample, such as the shape of the taxonomic distribution (i.e., the evenness of the sample). Here we look at richness using two measures: <i>Observed Species</i>, which is a count of the distinct Operational Taxonomic Units (OTUs) in a sample, and <i>Phylogenetic Diversity</i> (PD), which in our case is the sum of the branch length in a reference phylogenetic tree that is observed in a sample. PD is a phylogenetic measure of richness, meaning that the evolutionary relatedness of different organisms is taken into account via the phylogenetic tree, while observed species is a non-phylogenetic measure, meaning that all of the different organisms are treated as equally related.
<br/><br/>
You should be able to answer several questions about your microbial communities from these plots:
<ol>
  <li>How rich are the microbial communities at your different body sites relative to the average for that body site in this study (e.g., is your gut community more diverse than the average gut community in this study)?</li>
  <li>Which of your body sites is most diverse, and which is least diverse? Do other individuals exhibit the same pattern?</li>
</ol>


<h3>Click on the following links to see your alpha diversity boxplots:</h3>
<ul>
  %s
</ul>
"""

def create_otu_category_significance_html(table_fps):
    table_links_text = ''

    for table_fp in table_fps:
        body_site = splitext(basename(table_fp))[0].title()
        table_links_text += '<li><a href="%s">%s</a></li>' % (table_fp,
                                                              body_site)

    return otu_category_significance_text % table_links_text

otu_category_significance_text = """
<h2>Differences in OTU Abundances</h2>
Here we present <i>Operational Taxonomic Units (or OTUs)</i> that seemed to differ in their average relative abundance when comparing you to all other individuals in the study. An OTU is a functional definition of a taxonomic group, often based on percent identity of 16S rRNA sequences. In this study, we began with a reference collection of 16S rRNA sequences (derived from the <a href="http://greengenes.secondgenome.com">Greengenes database</a>), and each of those sequences was used to define an Opertational Taxonomic Unit. We then compared all of the sequence reads that we obtained in this study (from your microbial communities and everyone else's) to those reference OTUs, and if a sequence read matched one of those sequences at at least 97%% identity, the read was considered an observation of that reference OTU. This process is one strategy for <i>OTU picking</i>, or assigning sequence reads to OTUs. 
<br/><br/>
Here we present the OTUs that were most different in abundance in your microbial communities relative to those from other individuals. (These are not necessarily statistically significant, but rather just the most different.)

<h3>Click on the following links to see what OTU abundances differed by body
site:</h3>
<ul>
  %s
</ul>
"""

def format_otu_category_significance_tables_as_html(table_fps, alpha,
                                                    output_dir,
                                                    individual_titles,
                                                    rep_set_fp=None):
    if alpha < 0 or alpha > 1:
        raise ValueError("Alpha must be between zero and one.")

    otu_id_lookup = {}
    if rep_set_fp is not None:
        for seq_id, seq in MinimalFastaParser(open(rep_set_fp, 'U')):
            seq_id = seq_id.strip().split()[0]
            otu_id_lookup[seq_id] = seq

    created_files = []
    for table_fp in table_fps:
        body_site = splitext(basename(table_fp))[0].split('otu_cat_sig_')[-1]
        table_f = open(table_fp, 'U')

        out_html_fp = join(output_dir, '%s.html' % body_site)
        out_html_f = open(out_html_fp, 'w')
        created_files.append(basename(out_html_fp))

        html_row_text = ''
        rep_seq_html = ''
        processed_header = False
        for line in table_f:
            cells = map(lambda e: e.strip(), line.strip().split('\t'))

            if not processed_header:
                otu_id_idx = cells.index('OTU')
                p_value_idx = cells.index('FDR_corrected')
                taxonomy_idx = cells.index('Consensus Lineage')
                individual_title0_idx = cells.index('%s_mean' % individual_titles[0])
                individual_title1_idx = cells.index('%s_mean' % individual_titles[1])
                processed_header = True
            else:
                otu_id = cells[otu_id_idx]
                p_value = float(cells[p_value_idx])
                taxonomy = cells[taxonomy_idx]
                individual_title0_mean = float(cells[individual_title0_idx])
                individual_title1_mean = float(cells[individual_title1_idx])

                if p_value <= alpha:
                    # Taken from qiime.plot_taxa_summary.
                    taxa_links = []
                    for tax_level in taxonomy.split(';'):
                        # identify the taxa name (e.g., everything after the
                        # first double underscore) - we only want to include this
                        # in the google links for better search sensitivity
                        tax_name = tax_level.split('__',1)[1]
                        if len(tax_name) == 0:
                            # if there is no taxa name (e.g., tax_level == "s__")
                            # don't print anything for this level or any levels
                            # below it (which all should have no name anyway)
                            break
                        else:
                            taxa_links.append(
                                    '<a href="javascript:gg(\'%s\');">%s</a>' %
                                    (tax_name.replace(' ', '+'),
                                     tax_level.replace(' ', '&nbsp;')))
                    taxonomy = ';'.join(taxa_links).replace('"', '')
                    if individual_title0_mean < individual_title1_mean:
                        row_color = "#FF9900" # orange
                    else:
                        row_color = "#99CCFF" # blue

                    # If we have a rep seq for the current OTU ID, create a
                    # link. If not, simply display the OTU ID as text.
                    otu_id_html = otu_id
                    if otu_id in otu_id_lookup:
                        rep_seq = otu_id_lookup[otu_id]

                        # Splitting code taken from
                        # http://code.activestate.com/recipes/496784-split-
                        # string-into-n-size-pieces/
                        rep_seq = '\n'.join([rep_seq[i:i+40]
                            for i in range(0, len(rep_seq), 40)])

                        rep_seq_div_id = '%s-rep-seq' % otu_id
                        otu_id_html = ('<a href="#" id="%s" '
                                       'onclick="openDialog(\'%s\', \'%s\'); '
                                       'return false;">%s</a>' % (otu_id,
                                       rep_seq_div_id, otu_id, otu_id))
                        rep_seq_html += ('<div id="%s" class="rep-seq-dialog" '
                                         'title="Representative Sequence for '
                                         'OTU ID %s">\n<pre>&gt;%s\n%s</pre>\n'
                                         '</div>\n' % (rep_seq_div_id, otu_id,
                                                       otu_id, rep_seq))

                    html_row_text += '<tr><td bgcolor=%s>%s</td><td>%s</td></tr>\n' % (
                            row_color, otu_id_html, taxonomy)

        out_html_f.write(otu_category_significance_table_text %
                         (body_site, individual_titles[0], 
                          individual_titles[1], individual_titles[0], 
                          individual_titles[1], html_row_text, rep_seq_html))
        out_html_f.close()
        table_f.close()

    return created_files

# gg() function taken from qiime.plot_taxa_summary.
otu_category_significance_table_text = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
  <link href="../../support_files/css/themes/start/jquery-ui.css" rel="stylesheet">
  <link href="../../support_files/css/main.css" rel="stylesheet">

  <script src="../../support_files/js/jquery.js"></script>
  <script src="../../support_files/js/jquery-ui.js"></script>
  <script language="javascript" type="text/javascript">
    $(function() {
      // Initialize all dialogs and make sure they are hidden.
      $( ".rep-seq-dialog" ).dialog({autoOpen: false, width: 'auto'});
    });

    /*
     * This function accepts a dialog id as a parameter, and opens the dialog
     * box that is bound to that id. A second optional parameter, target, is
     * the id of the element where the dialog should appear next to. If this
     * parameter is null, the dialog will open at its default location,
     * according to its configured options.
     *
     * For example, if the user clicks a link to view more info, the dialog
     * should appear next to that link, instead of appearing in a location
     * relative to the dialog element, which is hidden. Therefore, the id of
     * the link that opens the dialog should be supplied as the second
     * parameter.
     */
    function openDialog(dialog, target) {
      var dialogId = "#" + dialog;

      if (typeof(target) != "undefined") {
        var targetId = "#" + target;
        var scrollOffsets = getScrollXY();

        // Move a little to the left.
        var leftPos = ($(targetId).position().left - scrollOffsets[0] + 95);
        var topPos = ($(targetId).position().top - scrollOffsets[1]);

        $(dialogId).dialog("option", "position", [leftPos, topPos]);
      }

      $(dialogId).dialog("open");
    }

    /*
     * Returns an array with the scrolling offsets (useful for displaying
     * tooltips/dialogs in the same place even when the user has scrolled on
     * the page and then opens a new dialog).
     *
     * Returns [scrollOffsetX, scrollOffsetY]. This function works in all
     * browsers.
     *
     * Code taken from: http://stackoverflow.com/a/745126
     */
    function getScrollXY() {
      var scrOfX = 0, scrOfY = 0;
      if (typeof(window.pageYOffset) == 'number') {
        // Netscape compliant.
        scrOfY = window.pageYOffset;
        scrOfX = window.pageXOffset;
      }
      else if (document.body && (document.body.scrollLeft ||
                                 document.body.scrollTop)) {
        // DOM compliant.
        scrOfY = document.body.scrollTop;
        scrOfX = document.body.scrollLeft;
      }
      else if (document.documentElement &&
               (document.documentElement.scrollLeft ||
                document.documentElement.scrollTop)) {
        // IE6 standards compliant mode.
        scrOfY = document.documentElement.scrollTop;
        scrOfX = document.documentElement.scrollLeft;
      }

      return [scrOfX, scrOfY];
    }

    function gg(targetq) {
      window.open("http://www.google.com/search?q=" + targetq, 'searchwin');
    }
  </script>
</head>

<body>
  <div class="ui-tabs ui-widget ui-widget-content ui-corner-all text">
    <h2>Operational Taxonomic Units (OTUs) that differed in relative abundance in %s samples (comparing self
    versus other)</h2>
    Click on the taxonomy links for each OTU to do a Google search for that
    taxonomic group. OTU IDs with an orange background are found in lower
    abundance in <i>%s</i> than in <i>%s</i>, and OTU IDs with a blue
    background are found in higher abundance in <i>%s</i> than in <i>%s</i>.
    Click on the OTU ID to view the representative sequence for that OTU (try
    <a target="_blank"
    href="http://blast.ncbi.nlm.nih.gov/Blast.cgi?PROGRAM=blastn&BLAST_PROGRAMS=megaBlast&PAGE_TYPE=BlastSearch&SHOW_DEFAULTS=on&LINK_LOC=blasthome">BLASTing</a> these!).
    <br/><br/>

    <table class="data-table">
      <tr>
        <th>OTU ID</th>
        <th>Taxonomy</th>
      </tr>
      %s
    </table>
    %s
  </div>
</body>
</html>
"""

def format_participant_table(participants_f, url_prefix):
    """Formats an HTML table of personal IDs with links to personal results.

    Returns the HTMl table as a string suitable for writing to a file. Personal
    IDs will be sorted.

    Arguments:
        participants_f - file in same format as that accepted by
            my_microbes.parse.parse_recipients. Email addresses are
            ignored
        url_prefix - URL to prefix each personal ID with to provide links to
            personalized results (string)
    """
    personal_ids = sorted(parse_recipients(participants_f).keys())
    url_prefix = url_prefix if url_prefix.endswith('/') else url_prefix + '/'

    result = '<table class="data-table">\n<tr><th>Personal ID</th></tr>\n'
    for personal_id in personal_ids:
        url = url_prefix + personal_id + '/index.html'
        result += '<tr><td><a href="%s">%s</a></td></tr>\n' % (url,
                                                               personal_id)
    result += '</table>\n'

    return result

def format_title(input_str):
    """Return title-cased string, with underscores converted to spaces.

    If input_str has a mapping in title_mapping, this will be used instead.
    """
    title_mapping = {'PD_whole_tree': 'Phylogenetic Diversity'}

    if input_str in title_mapping:
        return title_mapping[input_str]
    else:
        return ' '.join(map(lambda e: e[0].upper() + e[1:],
                            input_str.split('_')))
