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
 
#import personal_microbiome.util
from personal_microbiome.util import  create_indiv_3d_plot
from qiime.util import parse_command_line_parameters, make_option
import os
from os.path import exists, join
from os import makedirs 

script_info = {}
script_info['brief_description'] = """Generate distinct 3d plots for unique individuals based on the metadata mapping file."""
script_info['script_description'] = """This script generates a prefs file which assigns a unique color to the individual and then generates a 3d plot based on that prefs file"""
script_info['script_usage'] = [("""Basic usage with output directory""", """The distance matrix and mapping files are required. if no output file path is specified one will be created in the working directory. """, """%prog -i distance_matrix.txt -m mapping_file.txt -o out/""")]
script_info['output_description'] = "A directory containing all of the 3d plots for each individual"
script_info['required_options'] = [\
    make_option('-m', '--mapping_fp', type='existing_filepath', 
                help='Metadata mapping file filepath'),
    make_option('-i', '--coord_fname',
        help='Input principal coordinates filepath (i.e.,' \
        ' resulting file from principal_coordinates.py). Alternatively,' \
        ' a directory containing multiple principal coordinates files for' \
        ' jackknifed PCoA results.',
        type='existing_path'),
    make_option('-o', '--output_dir',
        help="Output directory. One will be created if it doesn't exist.",
        type='new_dirpath')
]

script_info['optional_options'] = []

script_info['version'] = __version__



def main():
    option_parser, opts, args = parse_command_line_parameters(**script_info)
    mapping_file = opts.mapping_fp
    distance_matrix = opts.coord_fname
    output_dir = opts.output_dir
    
    if exists(output_dir):
        # don't overwrite existing output directory - make the user provide a different name or 
        # move/delete the existing directory since it may have taken a while to create.
        raise ValueError, "Output directory (%s) already exists. Won't overwrite." % output_dir

    create_indiv_3d_plot(mapping_file, distance_matrix, output_dir)
    
if __name__ == "__main__":
    main()