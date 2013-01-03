#!/usr/bin/env python
from __future__ import division

__author__ = "John Chase"
__copyright__ = "Copyright 2013, The QIIME project"
__credits__ = ["John Chase", "Greg Caporaso"]
__license__ = "GPL"
__version__ = "0.0.0-dev"
__maintainer__ = "John Chase"
__email__ = "jc33@nau.edu"

import os
from qiime.util import qiime_system_call
from os import makedirs
from os.path import join
from os.path import exists
from qiime.parse import parse_mapping_file
from qiime.format import format_mapping_file
from personal_microbiome.format import create_index_html, create_comparative_taxa_plots_html

def get_personal_ids(mapping_data, personal_id_index):
    result = []
    for i in mapping_data:
        if i[personal_id_index] not in result: 
            result.append(i[personal_id_index]) 
        else: 
            pass
    return result
    
def create_personal_mapping_file(map_as_list,
                                 header, 
                                 comments, 
                                 personal_id_of_interest, 
                                 output_fp, 
                                 personal_id_index, 
                                 individual_titles):
    """ creates mapping file on a per-individual basis """
    if individual_titles == None: 
        individual_titles = ['Self', 'Other']
    else: 
        individual_titles = individual_titles.split(',')   
    personal_map = []
    for line in map_as_list:
        personal_map.append(line[:])
    for i in personal_map:   
        if i[personal_id_index] == personal_id_of_interest: 
            i.append(individual_titles[0])
        else: 
            i.append(individual_titles[1])
    personal_mapping_file = format_mapping_file(header, personal_map, comments) 
    output_f = open(output_fp,'w')
    output_f.write(personal_mapping_file)
    output_f.close()
    return personal_map
    
def create_personal_results(mapping_fp, 
                            distance_matrix_fp, 
                            collated_dir_fp, 
                            output_fp, prefs_fp, 
                            personal_id_field,
                            otu_table,
                            parameter_fp, 
                            personal_ids=None, 
                            column_title='Self', 
                            individual_titles=None,
                            category_to_split='BodySite',
                            time_series_category='WeeksSinceStart',
                            suppress_alpha_rarefaction=False,
                            verbose=False):
    map_as_list, header, comments = parse_mapping_file(open(mapping_fp, 'U'))
    try:
        personal_id_index = header.index(personal_id_field)
    except ValueError:
        raise ValueError("personal id field (%s) is not a mapping file column header" %
                         personal_id_field)
    header.append(column_title)
    
    if personal_ids == None: 
        personal_ids  = get_personal_ids(map_as_list, personal_id_index)
    else:
        for id in personal_ids.split(','):
            if id not in get_personal_ids(map_as_list, personal_id_index):
                raise ValueError('%s is not an id in the mapping file.' %id)
        personal_ids = personal_ids.split(',')
        
    output_directories = []
    makedirs(output_fp)
    otu_table_title = otu_table.split('/')[-1].split('.')
    for person_of_interest in personal_ids:
        makedirs(join(output_fp, person_of_interest))
        pcoa_dir = join(output_fp, person_of_interest, "beta_diversity")
        rarefaction_dir = join(output_fp, person_of_interest, "alpha_rarefaction")
        area_plots_dir = join(output_fp, person_of_interest, "time_series")
        output_directories.append(pcoa_dir)
        output_directories.append(rarefaction_dir)
        output_directories.append(area_plots_dir)
        personal_mapping_file_fp = join(output_fp, person_of_interest, "mapping_file.txt")
        html_fp = join(output_fp, person_of_interest, "index.html")
        personal_map = create_personal_mapping_file(map_as_list,
                                     header,
                                     comments,
                                     person_of_interest,
                                     personal_mapping_file_fp, 
                                     personal_id_index, 
                                     individual_titles)
        create_index_html(person_of_interest, html_fp)
        column_title_index = header.index(column_title)
        column_title_values = set([e[column_title_index] for e in personal_map])
        cat_index = header.index(category_to_split)
        cat_values = set([e[cat_index] for e in personal_map])
        
        ## Alpha rarefaction steps
        if not suppress_alpha_rarefaction:
            cmd = "make_rarefaction_plots.py -i %s -m %s -p %s -o %s" % (collated_dir_fp, 
                                                                         personal_mapping_file_fp,
                                                                         prefs_fp, 
                                                                         rarefaction_dir)
            if verbose:
                print cmd          
            stdout, stderr, return_code = qiime_system_call(cmd)
            if return_code != 0:
                raise ValueError("Command failed!\nCommand: %s\n Stdout: %s\n Stderr: %s\n" %\
                (cmd, stdout, stderr))
        
        ## Beta diversity steps
        cmd = "make_3d_plots.py -m %s -p %s -i %s -o %s" % (personal_mapping_file_fp, 
                                                            prefs_fp, 
                                                            distance_matrix_fp, 
                                                            pcoa_dir)
        if verbose:
            print cmd
        stdout, stderr, return_code = qiime_system_call(cmd)
        if return_code != 0:
            raise ValueError("Command failed!\nCommand: %s\n Stdout: %s\n Stderr: %s\n" %\
            (cmd, stdout, stderr))
        
        ## Split OTU table into self/other per-body-site tables
        cmd = "split_otu_table.py -i %s -m %s -f %s -o %s" % (otu_table,
                                                              personal_mapping_file_fp,
                                                              column_title, 
                                                              area_plots_dir)
        if verbose:
            print cmd
        stdout, stderr, return_code = qiime_system_call(cmd)
        if return_code != 0:
            raise ValueError("Command failed!\nCommand: %s\n Stdout: %s\n Stderr: %s\n" %\
            (cmd, stdout, stderr))
            
        
        for column_title_value in column_title_values:
            print column_title_value
            biom_fp = join(area_plots_dir, '%s_%s.%s' % (otu_table_title[0], column_title_value, otu_table_title[1]))
            body_site_dir = join(area_plots_dir, column_title_value)
            cmd = "split_otu_table.py -i %s -m %s -f %s -o %s" % (biom_fp,
                                                                  personal_mapping_file_fp,
                                                                  category_to_split, 
                                                                  body_site_dir)
            if verbose:
                print cmd
            stdout, stderr, return_code = qiime_system_call(cmd)
            if return_code != 0:
                raise ValueError("Command failed!\nCommand: %s\n Stdout: %s\n Stderr: %s\n" %\
                (cmd, stdout, stderr))
                
            for cat_value in cat_values:
                otu_table_fp = join(body_site_dir, "otu_table_%s_%s.biom" % (column_title_value, cat_value))
                print otu_table_fp
                if exists(otu_table_fp):
                    # Not supporting parameter files yet
                    #if parameter_fp == None:
                    #    parameter_fp = ''
                    #else:
                    #    parameter_fp = '-p %s' %parameter_fp
                    plots = join(area_plots_dir, "taxa_plots_%s_%s" % (column_title_value, cat_value))
                    cmd = "summarize_taxa_through_plots.py -i %s -o %s -c %s -m %s -s" % (otu_table_fp,
                                                                                                plots,
                                                                                                time_series_category, 
                                                                                                personal_mapping_file_fp)
                                                                                                #parameter_fp)
                    if verbose:
                        print cmd
                    stdout, stderr, return_code = qiime_system_call(cmd)
                    if return_code != 0:
                        raise ValueError("Command failed!\nCommand: %s\n Stdout: %s\n Stderr: %s\n" %\
                        (cmd, stdout, stderr))
                    create_comparative_taxa_plots_html(cat_value, 
                                                       join(area_plots_dir,'%s_comparative.html' % cat_value))
    return output_directories
    
    


    
    
    
    
    
    
    
