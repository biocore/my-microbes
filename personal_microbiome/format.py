#!/usr/bin/env python
from __future__ import division

__author__ = "John Chase"
__copyright__ = "Copyright 2013, The QIIME project"
__credits__ = ["John Chase", "Greg Caporaso", "Jai Ram Rideout"]
__license__ = "GPL"
__version__ = "0.0.0-dev"
__maintainer__ = "John Chase"
__email__ = "jc33@nau.edu"

from os.path import basename, splitext

index_text = """
<html>
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
          Below are links to your personal microbiome results, along with descriptions that should help you interpret those results. As our analysis progresses, we may have periodic updates to the data on this page. We'll alert you to those new data as they're available. If you have questions about your results, you can get in touch by email at <a href="mailto:student.microbiome@gmail.com">student.microbiome@gmail.com</a>.
        </p>
      </div>
    </div>
    <br/>

    <div id="tabs">
      <ul>
        <li><a href="#taxonomic-composition">Taxonomic Composition</a></li>
        <li><a href="#beta-diversity">Beta Diversity</a></li>
        <li><a href="#alpha-diversity-boxplots">Alpha Diversity Boxplots</a></li>
        <li><a href="#alpha-rarefaction">Alpha Rarefaction</a></li>
      </ul>

      <div id="taxonomic-composition">
        <table>
          <tr><td colspan=4>Comparative taxonomic summary plots</td></tr>
          <tr>
            <td>Tongue</td><td><a href="time_series/taxa_plots_Self_tongue/taxa_summary_plots/area_charts.html">Self</a></td><td><a href="time_series/taxa_plots_Other_tongue/taxa_summary_plots/area_charts.html">Other</a></td><td><a href="time_series/tongue_comparative.html">Self v Other</a></td>
          </tr>
            <td>Palm</td><td><a href="time_series/taxa_plots_Self_palm/taxa_summary_plots/area_charts.html">Self</a></td><td><a href="time_series/taxa_plots_Other_palm/taxa_summary_plots/area_charts.html">Other</a></td><td><a href="time_series/palm_comparative.html">Self v Other</a></td>
          </tr>
            <td>Gut</td><td><a href="time_series/taxa_plots_Self_gut/taxa_summary_plots/area_charts.html">Self</a></td><td><a href="time_series/taxa_plots_Other_gut/taxa_summary_plots/area_charts.html">Other</a></td><td><a href="time_series/gut_comparative.html">Self v Other</a></td>
          </tr>
            <td>Forehead</td><td><a href="time_series/taxa_plots_Self_forehead/taxa_summary_plots/area_charts.html">Self</a></td><td><a href="time_series/taxa_plots_Other_forehead/taxa_summary_plots/area_charts.html">Other</a></td><td><a href="time_series/forehead_comparative.html">Self v Other</a></td>
          </tr>
        </table>
        <br/>
        <b>Taxonomic composition</b><br>
        Here we present the composition of each body site (on the y-axis) over time (on the x-axis) for you (<i>Self</i>) versus the average of all other participants in the study (<i>Other</i>). The composition is provided at different taxonomic levels, from Phylum to Genus. This allows you to quickly get an idea of the temporal variability in your microbial communities, and determine which taxonomic groups are coming and going in your different body habitats.
        <p>
        You should be able to answer several questions from these plots:
        <ol>
          <li>What was the dominant phylum in your gut on the first week that you donated a sample?
          <li>Was the dominant phylum in your gut the same over all weeks, or did it change with time? 
          <li>Was the dominant phylum in each of your body sites the same as the average across the other individuals?
        </ol>
      </div>

      <div id="beta-diversity">
          <a href="./beta_diversity/unweighted_unifrac_pc_3D_PCoA_plots.html">Beta diversity PCoA plots</a>
          <br/>
          <b>Beta diversity</b><br>
          Beta diversity refers to the variation in species composition across samples, in contrast to alpha (i.e., within-sample) diversity, and is often computed as a distance between samples. If you have three samples, for example a sample from your tongue, another indivdual's tongue, and your palm, you could compute the beta diveristy or distance between all pairs of these three samples and determine if your tongue microbial community was more similar in composition to someone else's tongue microbial community, or to your palm microbial community. Ecologists use many different metrics to measure beta diversity - the metric we use here is called UniFrac (see <a href="http://www.ncbi.nlm.nih.gov/pubmed/16332807">Lozupone and Knight, 2005</a> for a discussion of UniFrac).
          <p>
          Because we're often looking at more than three samples (for example, in the Student Microbiome Project we compared over 3700 samples) ecologists often use ordination techniques to summarize pairwise distances between samples in a two- or three-dimensional scatter plot. In these ordination plots, points that are closer to each other in space are more similar to one another, and points that are more distant from one another are more dissimilar.
<p>
The plots presented here allow you to view the general clustering patterns observed in the Student Microbiome Project. We have colored these ordination plots so forehead samples are XXX, palm samples are XXX, gut samples are XXX and tongue samples are XXX. You can tell your samples from those of the rest of the participants as yours are colored in a lighter shade of the same colors.
<p>
You should be able to answer several questions from these plots:
<ol>
<li>Which is more similar: microbial communities from the same body site but from different individuals, or microbial communities from different body sites but from the same individual? 
<li>Do your microbial communities look typical of each body site, or are they outliers?
<li>Which body sites exhibit the most variability in composition across individuals?
</ol>
<p>
While many of the results apparent in this ordination plot were already known, the unprecedented number of indivduals and timepoints in the Student Microbiome Project data set allows us to address more sophisticated questions. For example, we are using these results to determine whether microbial communities of males or females more variable through time, if there are geographical differences in community composition that are visible across the three universities, and the affects of antibiotic usage and other <i>disturbances</i> on the composition of microbial communities. These are just a few examples that illustrate the utility of beta diversity analyses and the uniqueness of our dataset.
        </div>

        <div id="alpha-diversity-boxplots">
        %s
        </div>
        <div id="alpha-rarefaction">
          <a href="./alpha_rarefaction/rarefaction_plots.html">Alpha rarefaction plots</a>
          <b>Alpha rarefaction</b><br>
          Alpha rarefaction plots are a tool for interpreting measures of alpha diversity. Alpha diversity refers to within sample diversity, and is a measure of the number of different types of organisms that are present in a given sample (i.e., the richness of the sample) or some other property of a single sample, such as the shape of the taxonomic distribution (i.e., the evenness of the sample). Here we look at richness using two measures: <i>Observed Species</i>, which is a count of the distinct Operational Taxonomic Units (OTUs) in a sample, and <i>Phylogenetic Diversity</i> (PD), which in our case is the sum of the branch length in the Greengenes tree that is observed in a sample. PD is a phylogenetic measure, meaning that the evolutionary relatedness of different organisms is taken into account via the phylogenetic tree, while observed species is a non-phylogenetic measure, meaning that all of the different organisms are treated as equally related.
          <p>
          Alpha rarefaction plots show the alpha diversity at different depths of sampling (i.e., as if different numbers of sequences were collected). This is done because a measure of richness is very dependent on how much sampling effort was applied. For example, in macro-scale ecology, if you're interested in counting the number of different insect species in a rain forest, you would likely get a very different answer if you counted the number of insect species in a square meter versus a square kilometer. The analog to area in sequence-based studies of microbial ecology is the number of sequences collected. An alpha rarefaction plot presents the alpha diversity (y-axis) at different depths of sampling (or number of sequences collected; x-axis).
          <p>
          You should be able to answer several questions about your microbial communities from these plots:
          <ol>
                  <li>How rich are the microbial communities at your different body sites relative to the average for that body site (e.g., is your gut community more diverse than the average gut community)?
                  <li> Which of your body sites is most diverse, and which is least diverse? Do others exhibit the same pattern? 
                  <li>If we were to collect more sequences per sample, do you expect that your answers to questions 1 and 2 would change?
          </ol>
        </div>
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

The website has additional details on how to view and interpret your results.  If you have any questions, please send an email to student.microbiome@gmail.com.

Thanks for participating in the study!

The Student Microbiome Project Team
"""

def get_personalized_notification_email_text(personal_id):
    """Returns the text for the body of an email based on personal ID."""
    return notification_email_text % (personal_id, personal_id)

def create_index_html(personal_id, output_fp,
                      alpha_diversity_boxplots_html=''):
    output_f = open(output_fp,'w')
    output_f.write(index_text % (personal_id, personal_id,
                                 alpha_diversity_boxplots_html))
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
comparative_taxa_plots_text = """<html>
<head>
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
    <h2>%s taxonomic composition plots (comparing self versus other)</h2>
    The two panels below show taxonomic composition plots for yourself and all
    other individuals in the study, respectively. The x-axis contains the week
    number that the samples were taken from so that you can see how the
    community composition changes over time.
    <br/><br/>
    The two panels are synchronized such that when you scroll one, the other
    will also scroll. This makes it easier to compare your results to all other
    individuals in the study.

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

def create_alpha_diversity_boxplots_html_table_row(plot_fps):
    plot_links_text = ''

    for plot_fp in plot_fps:
        adiv_metric = splitext(basename(plot_fp))[0]
        plot_links_text += '<li><a href="%s">%s</a></li>' % (plot_fp,
                                                             adiv_metric)

    return alpha_diversity_boxplots_text % plot_links_text

alpha_diversity_boxplots_text = """
Alpha diversity boxplots
<table>
    <tr>
        <td>
            <ul>
                %s
            </ul>
        </td>
    </tr>
</table>
<br/>
<b>Alpha diversity boxplots:</b><br>
Here we present a series of comparative boxplots showing the
distributions of your alpha diversity (<i>Self</i>) versus all other
individuals' alpha diversity (<i>Other</i>) for each body site.
Separate boxplots are provided for each alpha diversity metric. For
more details about alpha diversity, please refer to the <b>Alpha
rarefaction</b> description.
"""
