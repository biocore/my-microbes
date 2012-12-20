#!/usr/bin/env python
from __future__ import division

__author__ = "John Chase"
__copyright__ = "Copyright 2013, The QIIME project"
__credits__ = ["John Chase", "Greg Caporaso"]
__license__ = "GPL"
__version__ = "0.0.0-dev"
__maintainer__ = "John Chase"
__email__ = "jc33@nau.edu"
 
from personal_microbiome.util import create_personal_results
from qiime.util import parse_command_line_parameters, make_option
import os
from os.path import exists, join
from os import makedirs 

script_info = {}
script_info['brief_description'] = """Generate distinct 3d plots for unique individuals based on the metadata mapping file."""
script_info['script_description'] = """This script generates a prefs file which assigns a unique color to the individual and then generates a 3d plot based on that prefs file"""
script_info['script_usage'] = [("""Basic usage""", 
                                """The required options are a mapping file, a distance matrix, a directory of collated alpha files, an output directory, and a preferences file. This will create alpha and beta diversity plots for all of the individuals. """, 
                                """%prog  -m StudentHouseMF072212.txt -i unweighted_unifrac_pc.txt -c alpha_div_collated/ -o personal_micro_out -p universal_prefs.txt"""),
                            ("""Limit output""",
                                """If the user wishes to limit the output so that plots are not created for every individual in the mapping file they can pass a list of the desired individual ids. For instance to create output for CUB027 and NAU113 the user would pass:""",
                                """%prog  -m StudentHouseMF072212.txt -i unweighted_unifrac_pc.txt -c alpha_div_collated/ -o limited_results_out -p universal_prefs.txt -l CUB027,NAU113"""),                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
                            ("""Change default id column title""",
                                """If the column indicating the individual is named something other than 'PersonalID' the user can indicate the name of that column. This will however require the updating the example prefs file to reflect the mapping file that is being used.""",
                                """%prog -m StudentHouseMF072212.txt -i unweighted_unifrac_pc.txt -c alpha_div_collated/ -o personal_micro_out -p universal_prefs.txt -n title_of_column"""),
                            ("""Change default titles for new column in mapping file""", 
                                """By default the new column will be titles "Self" and the categories are "Self" and "Other" if the user wishes to change this they can specify the new titles. These changes will have to be made manually in the prefs file as well.""",
                                """%prog -m StudentHouseMF072212.txt -i unweighted_unifrac_pc.txt -c alpha_div_collated/ -o def_cat_out -p universal_prefs_2.txt -l CUB027,NAU113 -t individual -r yes,no""")]

script_info['output_description'] = "A directory containing all of the 3d and rarefaction plots for each individual"
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
    make_option('-a', '--otu_table',
        help='Input otu table filepath',
        type='existing_path')
]

script_info['optional_options'] = [
    make_option('-n','--personal_id_column',
        default='PersonalID', type='string',
        help='Name of the column in the header that denotes the individual '
        'of interest, default is PersonalID.'),
    make_option('-l','--personal_ids',
        default=None, type='string',
        help='A comma seperated list of individual ids '
        'the default will create a list of all of the individuals '
        'in the mapping file.'),
    make_option('-t','--column_title',
        default="Self", type='string',
        help='Name of the column.'
        'A new column will be created to indicate '
        'whether a sample is from the specified individual '
        'or from a differeent individual. This option defines '
        'the name of that column. [default: %default]'
        'This change requires that the prefs file is modified as well '),
    make_option('-r','--individual_titles',
        default=None, type='string',
        help='Comma seperated values, i.e(Self,Other). '
        'The "self" title should be listed first. '
        'The default is "Self" '
        'if the sample is from the individual of interest ' 
        'and "Other" if the sample is not from the person '
        'of interest. Currently this requires modifying '
        'the prefs file to match the indicated titles. '),
    make_option('--category_to_split',
        default="BodySite", type='string',
        help='This is the second category that the otu table '
        'will be split on. The first is "column_title" '
        'a new otu table will be created for each value ' 
        'in each category.'),
    make_option('--time_series_category',
        default="WeeksSinceStart", type='string',
        help='path to the parameter file, which specifies changes to '
        'the default behavior. See '
        'http://www.qiime.org/documentation/file_formats.html '
        '#qiime-parameters. [if omitted, default values will be '
        'used]'),
    make_option('--parameter_fp',
        default=None, type='string',
        help='This is the category that will be graphed in ' 
        'the area plot along the x-axis. The default is ' 
        '"WeeksSinceStart" if the time series has a different ' 
        'name it will need to be provided.'),
    make_option('--suppress_alpha_rarefaction',
         default=False,action='store_true',
         help=('Suppress generation of alpha rarefaction data'
               ' [default: %default]'))
]

script_info['version'] = __version__



def main():
    option_parser, opts, args = parse_command_line_parameters(**script_info)
    mapping_file = opts.mapping_fp
    distance_matrix = opts.coord_fname
    collated_dir = opts.collated_dir
    output_dir = opts.output_dir
    prefs = opts.prefs_fp
    personal_id_column = opts.personal_id_column
    personal_ids = opts.personal_ids
    column_title = opts.column_title
    individual_titles = opts.individual_titles
    otu_table = opts.otu_table
    category_to_split = opts.category_to_split
    time_series_category = opts.time_series_category
    parameter_fp = opts.parameter_fp
    
    if exists(output_dir):
        # don't overwrite existing output directory - make the user provide a different name or 
        # move/delete the existing directory since it may have taken a while to create.
        raise ValueError, "Output directory (%s) already exists. Won't overwrite." % output_dir

    create_personal_results(mapping_file, 
                            distance_matrix, 
                            collated_dir, 
                            output_dir, 
                            prefs, 
                            personal_id_column,
                            otu_table,
                            parameter_fp, 
                            personal_ids, 
                            column_title, 
                            individual_titles,
                            category_to_split, 
                            time_series_category,
                            suppress_alpha_rarefaction=opts.suppress_alpha_rarefaction,
                            verbose=opts.verbose)
    
if __name__ == "__main__":
    main()