#!/usr/bin/env python
from __future__ import division

__author__ = "John Chase"
__copyright__ = "Copyright 2013, The QIIME project"
__credits__ = ["John Chase", "Greg Caporaso"]
__license__ = "GPL"
__version__ = "0.0.0-dev"
__maintainer__ = "John Chase"
__email__ = "jc33@nau.edu"

text = """
<html>
 <head><title>Personal Microbiome Results: %s</title></head>
 <body>
	<table width=100%%>
	<tr>
		<td>
			<h3>Personal microbiome results: %s</h3>
			Below are links to your personal microbiome results, along with descriptions that should help you interpret those results. As our analysis progresses, we may have periodic updates to the data on this page. We'll alert you to those new data as they're available. 
		</td>
		<td><img src="https://s3.amazonaws.com/my-microbes/my_microbes_logo.png"></td>
	</tr>
	<tr>
		<td colspan=2 width=100%%>
		<hr>
		<table width=100%%>
			<tr>
				<td width=25%% align=center valign=center>
					<a href="./alpha_rarefaction/rarefaction_plots.html">Alpha rarefaction plots</a>
				</td>
				<td>
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
				</td>
			</tr>
			<tr>
				<td width=25%% align=center valign=center>
					<a href="./beta_diversity/unweighted_unifrac_pc_3D_PCoA_plots.html">Beta diversity PCoA plots</a>
				</td>
				<td>
					<b>Beta diversity</b><br>
					Beta diversity refers to the variation in species composition among sites or within a site through time. In ecology, there are numerous metrics to measure beta diversity with some accounting only for presence/absence of species (unweighted) and others that also account for species abundances (weighted). The metric used here is known as UniFrac and differs from most other beta diversity metrics because it incorporates phylogenetic information into the calculation. For details on the UniFrac metric please refer to XXXX.
                    <p>
                    Once a beta diversity matrix is constructed of all the pairwise comparisons of samples, any number of ordination techniques can be used to condense the multidimensional data in order to visualize the results. Here we present the principal coordinate analysis results of the UniFrac distance matrices to visualize how microbial communities differ between body sites and individuals through time. How you interpret these figures is that each point represents the microbial community of one sample and points closer together in space are more similar in composition than points further apart. We have colored these ordination plots so that forehead samples are XXX, palm samples are XXX, gut samples are XXX and tongue samples are XXX with your samples being lighter (or darker) shades of each of those colors. As you can see, gut and tongue samples generally form distinct clusters while the two skin habitats have some overlap. After running some statistical tests to verify these observations, we can conclude that gut, tongue, and skin communities are distinct. While these observations were expected, we are using these beta diversity results to run other more sophisticated analyses. For example, we can use these results to ask the question; are gut communities of males or females more variable through time? Or, are there differences in community composition between the three universities? Or, what are the affects of antibiotic usage on the composition of tongue communities? These are just a few examples that illustrate the utility of beta diversity analyses and the uniqueness of our dataset.
				</td>
			</tr>
			<tr>
				<td width=25%% align=center valign=center>
					<table>
						<tr><td colspan=3>Comparative taxonomic summary plots</td></tr>
						<tr>
							<td>Tongue</td><td><a href="time_series/taxa_plots_Self_tongue/taxa_summary_plots/area_charts.html">Self</a></td><td><a href="time_series/taxa_plots_Other_tongue/taxa_summary_plots/area_charts.html">Other</a></td>
						</tr>
							<td>Palm</td><td><a href="time_series/taxa_plots_Self_palm/taxa_summary_plots/area_charts.html">Self</a></td><td><a href="time_series/taxa_plots_Other_palm/taxa_summary_plots/area_charts.html">Other</a></td>
						</tr>
							<td>Gut</td><td><a href="time_series/taxa_plots_Self_gut/taxa_summary_plots/area_charts.html">Self</a></td><td><a href="time_series/taxa_plots_Other_gut/taxa_summary_plots/area_charts.html">Other</a></td>
						</tr>
							<td>Forehead</td><td><a href="time_series/taxa_plots_Self_forehead/taxa_summary_plots/area_charts.html">Self</a></td><td><a href="time_series/taxa_plots_Other_forehead/taxa_summary_plots/area_charts.html">Other</a></td>
						</tr>
					</table>
				</td>
				<td>
					Taxonomy plots:
				</td>
			</tr>
		</table>
	</tr>
	<tr>
		<td colspan=2>
			<hr>
			Thanks for participating in the study! Please direct any questions to ...
		</td>
 </body>
</html>
"""

def create_index_html(personal_id, output_fp):
    output_f = open(output_fp,'w')
    output_f.write(text % (personal_id,personal_id))
    output_f.close()
    