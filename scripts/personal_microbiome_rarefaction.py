#!/usr/bin/env python
# File created on 13 Sep 2012
#from __future__ import division

__author__ = "John Chase"
__copyright__ = "Copyright 2011, The QIIME project"
__credits__ = ["John Chase"]
__license__ = "GPL"
__version__ = "1.5.0"
__maintainer__ = "John Chase"
__email__ = "jc33@nau.edu"
__status__ = "Development"

#Make sure that util2 is changed at some point this ins only temporary!* 
from personal_microbiome.util2 import create_indiv_rarefaction_plot
from qiime.util import parse_command_line_parameters, make_option
import os
from os.path import exists, join
from os import makedirs 

script_info = {}
script_info['brief_description'] = """Generate rarefaction plots for each unique individual. Categories will be self verse other."""
script_info['script_description'] = """This script generates a mapping file with a new category of self. THe self category will indicate whether each sample is from the person of interest or the rest of the population"""
script_info['script_usage'] = [("""Basic usage with output directory""", """An input directory from collate_alpha.py and mapping files are required. if no output file path is specified one will be created in the working directory. """, """%prog -i alpha_diversity_collated -m mapping_file.txt -o out/""")]
script_info['output_description'] = "A directory containing all of the rarefaction plots for each individual"
script_info['required_options'] = [\
    make_option('-m', '--mapping_fp', type='existing_filepath', 
                help='Metadata mapping file filepath'),
    make_option('-i', '--collated_dir',
        help='Input collated directory filepath (i.e.,' \
        ' resulting file from collate_alpha.py)',
        type='existing_path'),
    make_option('-o', '--output_dir',
        help="Output directory. One will be created if it doesn't exist.",
        type='new_dirpath'),
    make_option('-p', '--prefs_fp',
        help='Input prefs filepath, this is user generated (i.e.,'\
        'not currently created from any qiime function)',
        type='existing_path')
]

script_info['optional_options'] = []

script_info['version'] = __version__



def main():
    option_parser, opts, args = parse_command_line_parameters(**script_info)
    mapping_file = opts.mapping_fp
    collated_dir = opts.collated_dir
    output_dir = opts.output_dir
    prefs = opts.prefs_fp
    
    if exists(output_dir):
        # don't overwrite existing output directory - make the user provide a different name or 
        # move/delete the existing directory since it may have taken a while to create.
        raise ValueError, "Output directory (%s) already exists. Won't overwrite." % output_dir

    create_indiv_rarefaction_plot(mapping_file, collated_dir, output_dir, prefs)
    
if __name__ == "__main__":
    main()