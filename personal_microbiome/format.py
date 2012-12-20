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
				</td>
			</tr>
			<tr>
				<td width=25%% align=center valign=center>
					<a href="">Comparative taxonomy plots</a> (not yet available)
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
    