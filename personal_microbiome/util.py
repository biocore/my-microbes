import os
from qiime.util import qiime_system_call
from os import makedirs
from os.path import join
from qiime.parse import parse_mapping_file
from qiime.format import format_mapping_file
from personal_microbiome.format import create_index_html

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
                                 personal_id_index):
    """ creates mapping file on a per-individual basis """   
    personal_map = []
    for line in map_as_list:
        personal_map.append(line[:])
    for i in personal_map:   
        if i[personal_id_index] == personal_id_of_interest: 
            i.append('Self')
        else: 
            i.append('Other')
    personal_mapping_file = format_mapping_file(header, personal_map, comments) 
    output_f = open(output_fp,'w')
    output_f.write(personal_mapping_file)
    output_f.close()
    
def create_personal_results(mapping_fp, 
                            distance_matrix_fp, 
                            collated_dir_fp, 
                            output_fp, prefs_fp, 
                            personal_id_field, 
                            personal_ids=None):
    map_as_list, header, comments = parse_mapping_file(open(mapping_fp, 'U'))
    try:
        personal_id_index = header.index(personal_id_field)
    except ValueError:
        raise ValueError, "personal id field (%s) is not a mapping file column header" % personal_id_field
    header.append('Self')
    if personal_ids == None: 
        personal_ids  = get_personal_ids(map_as_list, personal_id_index)
    else:
        for id in personal_ids.split(','):
            if id not in get_personal_ids(map_as_list, personal_id_index):
                raise ValueError('%s is not an id in the mapping file.' %id)
        personal_ids = personal_ids.split(',')
    output_directories = []
    makedirs(output_fp)
    for person_of_interest in personal_ids:
        makedirs(join(output_fp, person_of_interest))
        pcoa_dir = join(output_fp, person_of_interest, "beta_diversity")
        rarefaction_dir = join(output_fp, person_of_interest, "alpha_rarefaction")
        output_directories.append(pcoa_dir)
        output_directories.append(rarefaction_dir)
        personal_mapping_file_fp = join(output_fp, person_of_interest, "mapping_file.txt")
        html_fp = join(output_fp, person_of_interest, "index.html")
        create_personal_mapping_file(map_as_list,
                                     header,
                                     comments,
                                     person_of_interest,
                                     personal_mapping_file_fp, 
                                     personal_id_index)
        create_index_html(person_of_interest, html_fp)
        cmd = "make_rarefaction_plots.py -i %s -m %s -p %s -o %s" % (collated_dir_fp, 
                                                                     personal_mapping_file_fp,
                                                                     prefs_fp, 
                                                                     rarefaction_dir)          
        stdout, stderr, return_code = qiime_system_call(cmd)
        if return_code != 0:
            raise ValueError("Command failed!\nCommand: %s\n Stdout: %s\n Stderr: %s\n" %\
            (cmd, stdout, stderr))
        cmd = "make_3d_plots.py -m %s -p %s -i %s -o %s" % (personal_mapping_file_fp, 
                                                            prefs_fp, 
                                                            distance_matrix_fp, 
                                                            pcoa_dir)
        stdout, stderr, return_code = qiime_system_call(cmd)
        if return_code != 0:
            raise ValueError("Command failed!\nCommand: %s\n Stdout: %s\n Stderr: %s\n" %\
             (cmd, stdout, stderr))
        
    return output_directories
    
    
    

    
    
    
    
    
    
    
