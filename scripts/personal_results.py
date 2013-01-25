#!/usr/bin/env python
from __future__ import division

__author__ = "John Chase"
__copyright__ = "Copyright 2013, The QIIME project"
__credits__ = ["John Chase", "Greg Caporaso", "Jai Ram Rideout"]
__license__ = "GPL"
__version__ = "0.0.0-dev"
__maintainer__ = "John Chase"
__email__ = "jc33@nau.edu"
 
from os import makedirs 
from os.path import exists, join

from qiime.util import parse_command_line_parameters, make_option
from qiime.workflow import (call_commands_serially, no_status_updates,
                            print_commands, print_to_stdout)

from my_microbes.util import create_personal_results

script_info = {}
script_info['brief_description'] = """Generate personalized results for individuals in a study"""

script_info['script_description'] = """
This script generates various microbial ecology analysis results on a
per-individual basis, allowing a study participant to easily view his/her
results and compare them to all other individuals in the study. The output is
organized as a set of HTML pages that can be viewed locally or from a hosted
location on the web.
"""

script_info['script_usage'] = [("Basic usage",
"The following command will create alpha rarefaction, beta diversity, and "
"taxa summary plots, as well as alpha diversity boxplots and OTU category "
"significance tables for all of the individuals in the study.",
"%prog -m map.txt -i unweighted_unifrac_pc.txt -c alpha_div_collated/ -a "
"otu_table.biom -p prefs.txt -o my_microbes_output"),

("Limit output",
"If the user wishes to limit the output so that plots are not created for "
"every individual in the mapping file they can pass a list of the desired "
"individual IDs. For instance, the following command creates output for "
"CUB027 and NAU113 only.",
"%prog -m map.txt -i unweighted_unifrac_pc.txt -c alpha_div_collated/ -a "
"otu_table.biom -p prefs.txt -o limited_output -l CUB027,NAU113"),

("Change default ID column title",
"If the column indicating the individual is named something other than "
"'PersonalID' the user can indicate the name of that column. This will, "
"however, require updating the example prefs file to reflect the mapping file "
"that is being used.",
"%prog -m map.txt -i unweighted_unifrac_pc.txt -c alpha_div_collated/ -a "
"otu_table.biom -p prefs.txt -o custom_pid_column_output -n title_of_column"),

("Change default title for new column in mapping file",
"By default a new column will be named 'Self' will be added to each "
"personalized mapping file in order to distinguish samples from the current "
"individual from all other samples. The column will have the categories "
"'Self' and 'Other'. If the user wishes to change this, they can specify the "
"column and category names. These changes will have to be made manually in "
"the prefs file as well.",
"%prog -m map.txt -i unweighted_unifrac_pc.txt -c alpha_div_collated/ -a "
"otu_table.biom -p prefs.txt -o custom_column_output -l CUB027,NAU113 -t "
"individual -r yes,no""")]

script_info['output_description'] = """
The output directory will contain sets of HTML pages for each individual in the
study, organized by personal ID.
"""

script_info['required_options'] = [ 
    make_option('-m', '--mapping_fp', type='existing_filepath', 
        help='Metadata mapping file filepath'),
    make_option('-i', '--coord_fname',
        help='Input principal coordinates filepath (i.e.,'
        ' resulting file from principal_coordinates.py). Alternatively,'
        ' a directory containing multiple principal coordinates files for'
        ' jackknifed PCoA results.',
        type='existing_path'),
    make_option('-c', '--collated_dir',
        help='Input collated directory filepath (i.e.,'
        ' resulting file from collate_alpha.py)',
        type='existing_path'),
    make_option('-o', '--output_dir',
        help="Output directory. One will be created if it doesn't exist.",
        type='new_dirpath'),
    make_option('-p', '--prefs_fp',
        help='Input prefs filepath, this is user generated (i.e.,'
        'not currently created from any qiime function)',
        type='existing_path'),
    make_option('-a', '--otu_table_fp',
        help='Input otu table filepath',
        type='existing_path')
]

script_info['optional_options'] = [
    make_option('-n','--personal_id_column',
        default='PersonalID', type='string',
        help='Name of the column in the header that denotes the individual '
        'of interest [default: %default]'),
    make_option('-l','--personal_ids',
        default=None, type='string',
        help='A comma seperated list of individual ids '
        'to generate results for [default: all]'),
    make_option('-t','--column_title',
        default="Self", type='string',
        help='Name of new column will be created to indicate '
        'whether a sample is from the specified personal_id '
        'or from a differeent personal_id. This option defines '
        'the name of that column. This must correspond to the name '
        'of a column in prefs_fp [default: %default]'),
    make_option('-r','--individual_titles',
        default="Self,Other", type='string',
        help='Comma seperated values describing how to name '
        'the individuals in the new column_title column. Must be exactly two '
        'distinct values [default: %default]'),
    make_option('-d','--rarefaction_depth',
        default=10000, type='int',
        help='single rarefaction depth (seqs/sample) to use when generating '
        'alpha diversity boxplots of self versus other, as well as otu '
        'category significance tables [default: %default]'),
    make_option('--category_to_split',
        default="BodySite", type='string',
        help='This is the second category that the otu table '
        'will be split on. The first is "column_title" '
        'a new otu table will be created for each value ' 
        'in each category [default: %default].'),
    make_option('--time_series_category',
        default="WeeksSinceStart", type='string',
        help='Header in mapping_fp describing the timeseries column '
        '[default: %default]'),
    make_option('--alpha', default=0.05, type='float',
        help='the alpha value to use when choosing OTUs to display in the OTU '
        'category significance tables. For an OTU to be included in the '
        'table, it must have an FDR-corrected p-value <= to alpha '
        '[default: %default]'),
    make_option('--rep_set_fp',
        help='input representative set of sequences (with IDs matching those '
        'found in the OTU table supplied with -a). If supplied, the OTU '
        'category significance tables will have clickable OTU IDs that will '
        'open the fasta-formatted representative sequence in a dialog '
        '[default: %default]', type='existing_filepath', default=None),
    make_option('--body_site_rarefied_otu_table_dir',
        help='path to directory containing per-body-site OTU tables that were '
        'split from a rarefied OTU table. If provided, the '
        'single_rarefaction.py and split_otu_table.py steps are skipped when '
        'generating the OTU category significance tables (the tables in this '
        'directory are used instead). This option only applies if OTU '
        'category significance tables are not suppressed. This option is '
        'useful if you are running this script many times on subsets of '
        'individuals, so that rarefaction/splitting doesn\'t occur each time '
        'the script is run. The tables\' filenames must be in the format '
        '\'<otu table name>_even<rarefaction depth>_<body site>.<extension>\' '
        '[default: %default]', type='existing_dirpath', default=None),
    make_option('--retain_raw_data', default=False, action='store_true',
         help='Retain raw data files (OTU tables, taxa summary files, etc.). '
               'By default, these files will be cleaned up by the script, as '
               'they are not viewable in the hosted delivery system and they '
               'roughly double the size of the output [default: %default]'),
    make_option('--suppress_alpha_rarefaction',
         default=False,action='store_true',
         help=('Suppress generation of alpha rarefaction data'
               ' [default: %default]')),
    make_option('--suppress_beta_diversity',
         default=False,action='store_true',
         help=('Suppress generation of beta diversity plots '
               '[default: %default]')),
    make_option('--suppress_taxa_summary_plots',
         default=False,action='store_true',
         help=('Suppress generation of taxa summary (time series) plots '
               '[default: %default]')),
    make_option('--suppress_alpha_diversity_boxplots',
         default=False,action='store_true',
         help=('Suppress generation of alpha diversity boxplots '
               '[default: %default]')),
    make_option('--suppress_otu_category_significance',
         default=False,action='store_true',
         help=('Suppress generation of otu category significance tables '
               '[default: %default]')),
    make_option('-w', '--print_only', action='store_true',
        help='Print the commands but don\'t call them -- useful for debugging '
        '[default: %default]', default=False)
]

script_info['version'] = __version__

def main():
    option_parser, opts, args = parse_command_line_parameters(**script_info)

    if exists(opts.output_dir):
        # don't overwrite existing output directory - make the user provide a
        # different name or move/delete the existing directory since it may
        # have taken a while to create.
        option_parser.error("Output directory (%s) already exists. "
                            "Won't overwrite." % opts.output_dir)

    personal_ids = opts.personal_ids
    if personal_ids is not None:
        personal_ids = opts.personal_ids.split(',')

    individual_titles = opts.individual_titles.split(',')

    if opts.print_only:
        command_handler = print_commands
    else:
        command_handler = call_commands_serially

    if opts.verbose:
        status_update_callback = print_to_stdout
    else:
        status_update_callback = no_status_updates

    create_personal_results(opts.output_dir,
                            opts.mapping_fp,
                            opts.coord_fname,
                            opts.collated_dir,
                            opts.otu_table_fp,
                            opts.prefs_fp,
                            opts.personal_id_column,
                            personal_ids,
                            opts.column_title,
                            individual_titles,
                            opts.category_to_split,
                            opts.time_series_category,
                            rarefaction_depth=opts.rarefaction_depth,
                            alpha=opts.alpha,
                            rep_set_fp=opts.rep_set_fp,
                            body_site_rarefied_otu_table_dir=opts.body_site_rarefied_otu_table_dir,
                            retain_raw_data=opts.retain_raw_data,
                            suppress_alpha_rarefaction=opts.suppress_alpha_rarefaction,
                            suppress_beta_diversity=opts.suppress_beta_diversity,
                            suppress_taxa_summary_plots=opts.suppress_taxa_summary_plots,
                            suppress_alpha_diversity_boxplots=opts.suppress_alpha_diversity_boxplots,
                            suppress_otu_category_significance=opts.suppress_otu_category_significance,
                            command_handler=command_handler,
                            status_update_callback=status_update_callback)


if __name__ == "__main__":
    main()
