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

# The following formatting functions are not unit-tested.
def create_index_html(personal_id, output_fp,
                      alpha_diversity_boxplots_html='',
                      otu_category_significance_html=''):
    output_f = open(output_fp,'w')
    output_f.write(index_text % (personal_id, personal_id,
                                 alpha_diversity_boxplots_html,
                                 otu_category_significance_html))
    output_f.close()

def create_alpha_diversity_boxplots_html(plot_fps):
    return alpha_diversity_boxplots_text % \
            _create_alpha_diversity_boxplots_links(plot_fps)

def create_comparative_taxa_plots_html(category, output_fp):
    output_f = open(output_fp,'w')
    output_f.write(comparative_taxa_plots_text % (category.title(),
            category.title(), category.title(), category, category,
            category.title(), category, category.title(), category))
    output_f.close()

def create_otu_category_significance_html(table_fps):
    return otu_category_significance_text % \
            _create_otu_category_significance_links(table_fps)

def get_personalized_notification_email_text(personal_id):
    """Returns the text for the body of an email based on personal ID."""
    return notification_email_text % (personal_id, personal_id)

# The remaining functions are unit-tested.
def _create_alpha_diversity_boxplots_links(plot_fps):
    plot_links_text = '<ul>\n'

    for plot_fp in plot_fps:
        adiv_metric_title = format_title(splitext(basename(plot_fp))[0])
        plot_links_text += '<li><a href="%s" target="_blank">%s</a></li>\n' % (
                plot_fp, adiv_metric_title)

    return plot_links_text + '</ul>\n'

def _create_otu_category_significance_links(table_fps):
    table_links_text = '<ul>\n'

    for table_fp in table_fps:
        body_site = splitext(basename(table_fp))[0].title()
        table_links_text += ('<li><a href="%s" target="_blank">%s</a></li>\n' %
            (table_fp, body_site))

    return table_links_text + '</ul>\n'

def create_otu_category_significance_html_tables(table_fps, alpha, output_dir,
                                                 individual_titles,
                                                 rep_set_fp=None):
    per_body_site_tables = _format_otu_category_significance_tables_as_html(
            table_fps, alpha, individual_titles, rep_set_fp)

    created_files = []
    for body_site, (table_html, rep_seq_html) in per_body_site_tables.items():
        out_html_fp = join(output_dir, '%s.html' % body_site)
        out_html_f = open(out_html_fp, 'w')

        out_html_f.write(otu_category_significance_table_text % (body_site,
                individual_titles[0], individual_titles[1],
                individual_titles[0], individual_titles[1], table_html,
                rep_seq_html))

        out_html_f.close()
        created_files.append(basename(out_html_fp))

    return sorted(created_files)

def _format_otu_category_significance_tables_as_html(table_fps, alpha,
                                                     individual_titles,
                                                     rep_set_fp=None):
    if alpha < 0 or alpha > 1:
        raise ValueError("Alpha must be between zero and one.")

    otu_id_lookup = {}
    if rep_set_fp is not None:
        for seq_id, seq in MinimalFastaParser(open(rep_set_fp, 'U')):
            seq_id = seq_id.strip().split()[0]
            otu_id_lookup[seq_id] = seq

    per_body_site_tables = {}
    for table_fp in table_fps:
        body_site = splitext(basename(table_fp))[0].split('otu_cat_sig_')[-1]
        html_table_text = ('<table class="data-table">\n'
                           '<tr>\n'
                           '<th>OTU ID</th>\n'
                           '<th>Taxonomy</th>\n'
                           '</tr>\n')

        rep_seq_html = ''
        processed_header = False

        with open(table_fp, 'U') as table_f:
            for line in table_f:
                cells = map(lambda e: e.strip(), line.strip().split('\t'))

                if not processed_header:
                    otu_id_idx = cells.index('OTU')
                    p_value_idx = cells.index('FDR_corrected')
                    taxonomy_idx = cells.index('Consensus Lineage')
                    individual_title0_idx = cells.index('%s_mean' %
                                                        individual_titles[0])
                    individual_title1_idx = cells.index('%s_mean' %
                                                        individual_titles[1])
                    processed_header = True
                    continue

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
                        # first double underscore) - we only want to include
                        # this in the google links for better search
                        # sensitivity
                        tax_name = tax_level.split('__',1)[1]
                        if len(tax_name) == 0:
                            # if there is no taxa name
                            # (e.g., tax_level == "s__") don't print anything
                            # for this level or any levels below it (which all
                            # should have no name anyway)
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

                    html_table_text += ('<tr>\n<td bgcolor=%s>%s</td>\n'
                                        '<td>%s</td>\n</tr>\n' % (row_color,
                                        otu_id_html, taxonomy))
        html_table_text += '</table>\n'
        per_body_site_tables[body_site] = (html_table_text, rep_seq_html)

    return per_body_site_tables

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

top_level_index_text = """
This page contains the personalized microbiome results generated by the <a href="https://github.com/qiime/my-microbes/">My Microbes</a> system for participants in the Student Microbiome Project at the University of Colorado at Boulder, Northern Arizona University, and North Carolina State University. You should have received a personalized link to your microbiome data by email. If you're not a participant in the study, but interested in seeing data, you can see example data from one of the participants:
<br/><br/>
<a href="./NAU144/index.html">Personal microbiome data for individual NAU144</a>
<br/><br/>
In this study, we asked students to collect weekly samples from their forehead, tongue, palm, armpit, and gut for ten-weeks. After the samples were collected, we extracted DNA from those samples (over 3700 samples in all), and sequenced the 16S rRNA gene from the bacteria and the archaea in these samples. We then used that DNA sequence data to characterize the microbial communities living at each of the sites that were sampled, as well as the temporal variability in those microbial communities. For details on the 16S rRNA gene, and why it's useful in this type of study, you can refer to <a href="http://www.microbe.net/fact-sheet-ribosomal-rna-rrna-the-details/">this discussion</a>. Due to technical limitations we were unable to sequence the armpit samples. We additionally were not able to sequence samples from individuals who turned in fewer than six weeks of samples.

While producing this delivery system and the results presented has been a great deal of work, it is just the beginning. Analyses of these data are ongoing and interesting trends are beginning to emerge. We hope to publish our findings in the scientific literature within the year. As our analyses progress, we will send periodic updates and may have new results to share with you. Once again, we are grateful for your participation and hope you learned something along the way. Thank you!

Please direct any questions you have about this study or your personal microbiome data to <a href="mailto:student.microbiome@gmail.com">student.microbiome@gmail.com</a>.

"""

index_text = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
  <head>
    <link href="../support_files/css/themes/start/jquery-ui.css" rel="stylesheet">
    <link href="../support_files/css/main.css" rel="stylesheet">

    <script src="../support_files/js/jquery.js"></script>
    <script src="../support_files/js/jquery-ui.js"></script>
    <script src="../support_files/js/helpers.js"></script>

    <script>
      // The following code to remember accordion state is modified from
      // http://www.boduch.ca/2011/05/remembering-jquery-ui-accordion.html
      $(function() {
        // Find the index of our accordion header based on the current url
        // hash. If it can't be found (e.g. bad url hash or one isn't defined),
        // close the accordion completely to simulate a fresh page view with no
        // url hash.
        var index = $('#accordion h3.accordion-header').index(
          $('#accordion h3.accordion-header a[href="' +
             window.location.hash + '"]').parent());

        if (index < 0) {
          index = false;
        }

        var change = function(event, ui) {
          var hash = ui.newHeader.children('a').attr('href');

          if (hash !== undefined) {
            window.location.hash = hash;
          }
        }

        $("#accordion").accordion({
          collapsible: true,
          active: index,
          change: change,
          heightStyle: "content"
        });

        initializeGlossary();
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
            <h2 class="error">Internet Explorer is not a recommended browser to use with My Microbes as some features will not be available. We recommend using either Firefox or Safari.</h2>
          <![endif]-->
        </center>
      </div>
    </div>
    <br/>

    <div id="accordion">
      <h3 class="accordion-header"><a href="#taxonomic-composition">Which microbes live on my body?</a></h3>
      <div>
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
            <td><a href="time_series/taxa_plots_Self_tongue/taxa_summary_plots/area_charts.html" target="_blank">Self</a></td>
            <td><a href="time_series/taxa_plots_Other_tongue/taxa_summary_plots/area_charts.html" target="_blank">Other</a></td><td><a href="time_series/tongue_comparative.html" target="_blank">Self versus Other</a></td>
          </tr>
          <tr>
            <td><b>Palm:</b></td>
            <td><a href="time_series/taxa_plots_Self_palm/taxa_summary_plots/area_charts.html" target="_blank">Self</a></td>
            <td><a href="time_series/taxa_plots_Other_palm/taxa_summary_plots/area_charts.html" target="_blank">Other</a></td>
            <td><a href="time_series/palm_comparative.html" target="_blank">Self versus Other</a></td>
          </tr>
          <tr>
            <td><b>Gut:</b></td>
            <td><a href="time_series/taxa_plots_Self_gut/taxa_summary_plots/area_charts.html" target="_blank">Self</a></td>
            <td><a href="time_series/taxa_plots_Other_gut/taxa_summary_plots/area_charts.html" target="_blank">Other</a></td>
            <td><a href="time_series/gut_comparative.html" target="_blank">Self versus Other</a></td>
          </tr>
          <tr>
            <td><b>Forehead:</b></td>
            <td><a href="time_series/taxa_plots_Self_forehead/taxa_summary_plots/area_charts.html" target="_blank">Self</a></td>
            <td><a href="time_series/taxa_plots_Other_forehead/taxa_summary_plots/area_charts.html" target="_blank">Other</a></td>
            <td><a href="time_series/forehead_comparative.html" target="_blank">Self versus Other</a></td>
          </tr>
        </table>
      </div>

      <h3 class="accordion-header"><a href="#beta-diversity">Are my microbes different from everyone else's?</a></h3>
      <div>
        <a href="#" id="bdiv-ref-1" class="bdiv">Beta diversity</a> measures between-sample diversity, in contrast to <a href="#" id="adiv-ref-1" class="adiv">alpha (or within-sample) diversity</a>.  For example, if you have human gut microbial communities from three individuals, a <a href="#" id="bdiv-ref-2" class="bdiv">beta diversity</a> metric will tell you the relative similarity or dissimilarity of those samples: perhaps that individual <i>A</i> is more similar to individual <i>B</i> than either is to individual <i>C</i>. Ecologists use many different metrics to measure <a href="#" id="bdiv-ref-3" class="bdiv">beta diversity</a> - the metric we use here is called UniFrac (see <a href="http://www.ncbi.nlm.nih.gov/pubmed/16332807" target="_blank">Lozupone and Knight, 2005</a> for a discussion of UniFrac).
        <br/><br/>
        Because we're often looking at more than three samples (for example, in the Student Microbiome Project we compared over 3700 samples) ecologists often use <a href="#" id="ordination-ref-1" class="ordination">ordination</a> techniques to summarize pairwise distances between samples in a two- or three-dimensional scatter plot. In an <a href="#" id="ordination-ref-2" class="ordination">ordination</a> plot, points that are closer to each other in space are more similar to one another, and points that are more distant from one another are more dissimilar. The <a href="#" id="ordination-ref-3" class="ordination">ordination</a> technique that we apply here is called Principal Coordinates Analysis (PCoA), and the result is a PCoA plot.
        <br/><br/>
        The plots presented here allow you to view the general sample clustering patterns observed in the Student Microbiome Project. One of these (the <i><a href="#" id="bdiv-ref-4" class="bdiv">beta diversity</a> PCoA plots</i>) is a strict PCoA plot, while the other (the <i><a href="#" id="bdiv-ref-5" class="bdiv">beta diversity</a> PCoA plots with explicit time axis</i>) shows the first two dimensions of the strict PCoA plot, and adds a time dimension that illustrates time since the start of the experiment. Each point in the plot represents a microbial community from one individual at one body site from one timepoint. We have colored the points in these plots so forehead samples are yellow, palm samples are orange, gut samples are blue and tongue samples are red. You can tell your samples from those of the rest of the participants as yours are colored in lighter shades of the same colors. You can view the <i><a href="#" id="bdiv-ref-6" class="bdiv">beta diversity</a> PCoA plots with explicit time axis</i> to see how your samples changed over time.
        <br/><br/>
        You should be able to answer several questions from these plots:
        <ol>
          <li>Which is more similar: microbial communities from the same body site but from different individuals, or microbial communities from different body sites but from the same individual?</li>
          <li>Do your microbial communities look typical of each body site, or are they outliers?</li>
          <li>Which body sites exhibit the most variability across individuals?</li> 
        </ol>

        While many of the results apparent in this <a href="#" id="ordination-ref-4" class="ordination">ordination</a> plot were already known, the unprecedented number of indivduals and timepoints in the Student Microbiome Project data set allows us to address more sophisticated questions. For example, we are using these results to determine whether microbial communities of males or females more variable through time, if there are geographical differences in community composition that are visible across the three universities, and the affects of antibiotic usage and other <i>disturbances</i> on the composition of microbial communities. These are just a few examples that illustrate the utility of <a href="#" id="bdiv-ref-7" class="bdiv">beta diversity</a> analyses and the uniqueness of our dataset.

        <h3>Click <a href="./beta_diversity/unweighted_unifrac_pc_3D_PCoA_plots.html" target="_blank">here</a> to see your beta diversity PCoA plots.</h3>
        <h3>Click <a href="./beta_diversity_time_series/unweighted_unifrac_pc_3D_PCoA_plots.html" target="_blank">here</a> to see your beta diversity PCoA plots with an explicit time series axis.</h3>
      </div>

      <h3 class="accordion-header"><a href="#alpha-diversity">How many types of microbes live on my body?</a></h3>
      <div>%s</div>

      <h3 class="accordion-header"><a href="#differential-otus">Which microbes differentiate me from everyone else?</a></h3>
      <div>%s</div>
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

alpha_diversity_boxplots_text = """
Here we present plots showing the distributions of your <a href="#" id="adiv-ref-2" class="adiv">alpha diversity</a> (<i>Self</i>) versus all other individuals' <a href="#" id="adiv-ref-3" class="adiv">alpha diversity</a> (<i>Other</i>), for each body site. <a href="#" id="adiv-ref-4" class="adiv">Alpha diversity</a> refers to within-sample diversity, and can be a measure of the number of different types of organisms that are present in a sample (i.e., the richness of the sample), the shape of the distribution of counts of different organisms in a sample (i.e., the evenness of the sample), or some other property of a single sample.
<br/><br/>
We present the <i>Observed Species</i> for each of your body sites across the sampling period, as well as the average <i>Observed Species</i> across all individuals. <i>Observed Species</i> is a measure of richness, and here it is a count of the distinct <a href="#" id="otu-ref-1" class="otus">Operational Taxonomic Units (OTUs)</a> in a sample. An anology in macro-scale ecology would be identifying the number of insect species in a square kilometer of rainforest: when sampling this square kilometer, the <i>Observed Species</i> would simply be the number of distinct insect species that you observe.
<br/><br/>
You should be able to answer several questions about your microbial communities from these plots:
<ol>
  <li>How rich are the microbial communities at your different body sites relative to the average for that body site in this study (e.g., is your gut community more diverse than the average gut community in this study)?</li>
  <li>Which of your body sites is most rich, and which is least rich? Do other individuals exhibit the same pattern of richness?</li>
</ol>
%s
<hr>
<b>Advanced</b>: Measurements of <a href="#" id="adiv-ref-5" class="adiv">alpha diversity</a> are strongly affected by the sampling effort applied in a study.  For example, in macro-scale ecology, if you're interested in inferring the number of insect species in a rain forest, you would likely get a very different answer if you counted the number of insect species in a square meter versus a square kilometer. The area that you sampled would correspond to your sampling effort. In studies of the human microbiome based on DNA sequencing, the sampling effort corresponds to the number of sequences that are collected on a per-sample basis. If <a href="#" id="adiv-ref-6" class="adiv">alpha diversity</a> is computed in a study where 100 sequences are collected, you'll likely see many fewer taxa than in a study where 100,000 sequences are collected. To address this issue, ecologists use a tool called alpha rarefaction plots.
<br/><br/>
Alpha rarefaction plots show the <a href="#" id="adiv-ref-7" class="adiv">alpha diversity</a> at different depths of sampling (i.e., as if different numbers of sequences were collected). An alpha rarefaction plot presents the <a href="#" id="adiv-ref-8" class="adiv">alpha diversity</a> (y-axis) at different depths of sampling (or number of sequences collected; x-axis). From an alpha rarefaction plot, you should be able to answer the question: <i>If we were to collect more sequences per sample, do you expect that your answers to the above questions 1 through 3 would change?</i>
<br/><br/>
Click <a href="./alpha_rarefaction/rarefaction_plots.html" target="_blank">here</a> to see your alpha rarefaction plots. After clicking the link, select the <tt>observed_species</tt> alpha diversity metric (the only one we computed here) from the first drop-down menu, and then a category from the second menu.

"""

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

  <script src="../../support_files/js/jquery.js"></script>
  <script src="../../support_files/js/jquery-ui.js"></script>

  <script language="javascript" type="text/javascript">
    $(function() {
      $("#loading-dialog").dialog({
        modal: true,
        resizable: false,
        closeText: '',
        closeOnEscape: false,
        draggable: false,
        open: function(event, ui) {
          $(".ui-dialog-titlebar-close", $(this).parent()).hide();
        },
        position: {
          my: "center top", at: "center top", of: window
        }
      });
    });

    function init() {
      layout = 'vertical';
      toggleLayout();
    }

    function toggleLayout() {
      window.scrollTo(0, 0);

      if (layout == 'vertical') {
        $(".vertical").hide();
        $(".horizontal").show();
        layout = 'horizontal';

        var selfIFrame = document.getElementById("horizontalSelfIFrame");
        var otherIFrame = document.getElementById('horizontalOtherIFrame');
        var selfIFrameHeight = selfIFrame.contentWindow.document.body.scrollHeight;
        var otherIFrameHeight = otherIFrame.contentWindow.document.body.scrollHeight;
        var height = Math.max(selfIFrameHeight, otherIFrameHeight);

        selfIFrame.style.height = height + 'px';
        otherIFrame.style.height = height + 'px';
      }
      else {
        document.getElementById("verticalSelfIFrame").contentWindow.onscroll = syncOther;
        document.getElementById("verticalOtherIFrame").contentWindow.onscroll = syncSelf;

        $(".horizontal").hide();
        $(".vertical").show();
        layout = 'vertical';
      }

      $("#loading-dialog").dialog("close");
      window.scrollTo(0, 0);
    }

    function syncSelf() {
      var selfContent = document.getElementById("verticalSelfIFrame").contentWindow;
      var otherContent = document.getElementById("verticalOtherIFrame").contentWindow;
      selfContent.scrollTo(otherContent.scrollX, otherContent.scrollY);
    }

    function syncOther() {
      var selfContent = document.getElementById("verticalSelfIFrame").contentWindow;
      var otherContent = document.getElementById("verticalOtherIFrame").contentWindow;
      otherContent.scrollTo(selfContent.scrollX, selfContent.scrollY);
    }
  </script>
</head>

<body onload="init();">
  <div id="loading-dialog" title="Loading...">
    <center>
      <p>Loading, please wait...</p>
      <img src="../../support_files/images/loading.gif"/>
    </center>
  </div>

  <div class="ui-tabs ui-widget ui-widget-content ui-corner-all text">
    <h2>%s taxonomic composition plots (comparing self versus other)</h2>
    The two panels below show taxonomic composition plots for yourself and all
    other individuals in the study, respectively. The x-axis contains the week
    number that the samples were taken from so that you can see how the community
    composition changes over time.
    <br/><br/>

    By default, the <i>Self</i> versus <i>Other</i> plots are positioned
    side-by-side for easy comparison on wide monitors. If you're having trouble
    comparing the plots because they are overlapping each other, try clicking
    the button below to switch to a vertical layout.
    <br/><br/>

    <button id="toggleViewButton" type="button" onclick="toggleLayout();">
      Switch Layout
    </button>

    <div class="vertical">
      <br/>
      The two panels are synchronized such that when you scroll one, the other will
      also scroll. This makes it easier to compare your results to all other
      individuals in the study.
    </div>
  </div>

  <div class="horizontal">
    <table height="100%%" width="100%%" cellpadding=0 cellspacing=0>
      <tr>
        <td>
          <h3>%s taxonomic composition by weeks since experiment start (self)</h3>
        </td>
        <td>
          <h3>%s taxonomic composition by weeks since experiment start (other; average)</h3>
        </td>
      </tr>
      <tr>
        <td>
          <iframe id="horizontalSelfIFrame"
                  src="taxa_plots_Self_%s/taxa_summary_plots/area_charts.html"
                  frameborder="0" style="width:100%%;"
                  scrolling="no">
          </iframe>
        </td>
        <td>
          <iframe id="horizontalOtherIFrame"
                  src="taxa_plots_Other_%s/taxa_summary_plots/area_charts.html"
                  frameborder="0" style="width:100%%;"
                  scrolling="no">
          </iframe>
        </td>
      </tr>
    </table>
  </div>

  <div class="vertical">
    <h3>%s taxonomic composition by weeks since experiment start (self)</h3>
    <div id="selfContainer" style="margin: 0 auto; width:90%%; height:48%%">
      <iframe id="verticalSelfIFrame"
              src="taxa_plots_Self_%s/taxa_summary_plots/area_charts.html"
              frameborder="0" style="width:100%%; height:100%%; margin:1%%;"
              scrolling="auto">
      </iframe>
    </div>

    <h3>%s taxonomic composition by weeks since experiment start (other; average)</h3>
    <div id="otherContainer" style="margin: 0 auto; width:90%%; height:48%%;">
      <iframe id="verticalOtherIFrame"
              src="taxa_plots_Other_%s/taxa_summary_plots/area_charts.html"
              frameborder="0" style="width:100%%; height:100%%; margin:1%%;"
              scrolling="auto">
      </iframe>
    </div>
  </div>
</body>
</html>
"""

otu_category_significance_text = """
Here we present <a href="#" id="otu-ref-3" class="otus">Operational Taxonomic Units (OTUs)</a> that seemed to differ in their average relative abundance when comparing you to all other individuals in the study. An <a href="#" id="otu-ref-4" class="otus">OTU</a> is a functional definition of a taxonomic group, often based on percent identity of 16S rRNA sequences. In this study, we began with a reference collection of 16S rRNA sequences (derived from the <a href="http://greengenes.secondgenome.com" target="_blank">Greengenes database</a>), and each of those sequences was used to define an Opertational Taxonomic Unit. We then compared all of the sequence reads that we obtained in this study (from your microbial communities and everyone else's) to those reference <a href="#" id="otu-ref-5" class="otus">OTUs</a>, and if a sequence read matched one of those sequences at at least 97%% identity, the read was considered an observation of that reference <a href="#" id="otu-ref-6" class="otus">OTU</a>. This process is one strategy for <i>OTU picking</i>, or assigning sequence reads to <a href="#" id="otu-ref-7" class="otus">OTUs</a>.
<br/><br/>
Here we present the <a href="#" id="otu-ref-8" class="otus">OTUs</a> that were most different in abundance in your microbial communities relative to those from other individuals. (These are not necessarily statistically significant, but rather just the most different.)

<h3>Click on the following links to see what OTU abundances differed by body site:</h3>
%s
"""

otu_category_significance_table_text = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
  <link href="../../support_files/css/themes/start/jquery-ui.css" rel="stylesheet">
  <link href="../../support_files/css/main.css" rel="stylesheet">

  <script src="../../support_files/js/jquery.js"></script>
  <script src="../../support_files/js/jquery-ui.js"></script>
  <script src="../../support_files/js/helpers.js"></script>

  <script language="javascript" type="text/javascript">
    $(function() {
      // Initialize all dialogs and make sure they are hidden.
      $( ".rep-seq-dialog" ).dialog({autoOpen: false, width: 'auto'});

      initializeGlossary();
    });
  </script>
</head>

<body>
  <div class="ui-tabs ui-widget ui-widget-content ui-corner-all text">
    <h2>Operational Taxonomic Units (OTUs) that differed in relative abundance in %s samples (comparing self versus other)</h2> Click on the taxonomy links for each <a href="#" id="otu-ref-1" class="otus">OTU</a> to do a Google search for that taxonomic group. OTU IDs with an orange background are found in lower abundance in <i>%s</i> than in <i>%s</i>, and OTU IDs with a blue background are found in higher abundance in <i>%s</i> than in <i>%s</i>.  Click on the OTU ID to view the representative sequence for that OTU (try <a href="http://blast.ncbi.nlm.nih.gov/Blast.cgi?PROGRAM=blastn&BLAST_PROGRAMS=megaBlast&PAGE_TYPE=BlastSearch&SHOW_DEFAULTS=on&LINK_LOC=blasthome" target="_blank">BLASTing</a> these!).
    <br/><br/>
    %s
    %s
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
