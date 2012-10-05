from qiime.parse import parse_mapping_file
from qiime.format import format_mapping_file
from sys import argv
from os import makedirs
from os.path import join
import os
from qiime.parse import parse_mapping_file_to_dict
from qiime.util import qiime_system_call


script_name, map, dir, out, prefs = argv

def create_PersonalID_list(mapping_data):
    result = []
    for i in mapping_data:
        if i[8] not in result: 
            result.append(i[8]) 
        else: 
            pass
    return result
 
# I need to modify the create_personal_mapping_file to write to a file. This file path needs
# to be defined in the create_indiv_rarefaction function so that it can be passed to the 
# make_rarefaction_plots.py since it won't recognize an object.

def create_personal_mapping_file(map_as_list, header, comments, personal_id_of_interest, output_fp):
    """ creates mapping file on a per-individual basis """
    map_as_list = tuple(map_as_list)
    personal_map = []
    for line in map_as_list:
        personal_map.append(line[:])
    for i in personal_map:   
        if i[8] == personal_id_of_interest: 
            i.insert(9, 'yes')
        else: 
            i.insert(9, 'no')
    print len(map_as_list[0])
    print len(personal_map[0])
    personal_mapping_file = format_mapping_file(header, personal_map, comments) 
    output_f = open(output_fp,'w')
    output_f.write(personal_mapping_file)
    output_f.close()
    
def create_indiv_rarefaction_plot(mapping_fp, collated_dir_fp, output_fp, prefs_fp):
    map_as_list, header, comments = parse_mapping_file(open(mapping_fp, 'U'))
    PersonalID_list = create_PersonalID_list(map_as_list)
    header.insert(9, 'Self')
    output_directories = []
    makedirs(output_fp)
    for person_of_interest in PersonalID_list:
        makedirs(join(output_fp, person_of_interest))
        personal_output_dir = join(output_fp, person_of_interest, "%s_rarefaction" % person_of_interest)
        output_directories.append(personal_output_dir)
        personal_mapping_file_fp = join(output_fp, person_of_interest, "%s_mapping_file.txt" % person_of_interest)
        create_personal_mapping_file(map_as_list,
                                     header,
                                     comments,
                                     person_of_interest,
                                     personal_mapping_file_fp)
        cmd = "make_rarefaction_plots.py -i %s -m %s -p %s -o %s -s" % (collated_dir_fp, 
                                                                     personal_mapping_file_fp,
                                                                     prefs_fp, 
                                                                     personal_output_dir)
        stdout, stderr, return_code = qiime_system_call(cmd)
        if return_code != 0:
            print "Command failed!\nCommand: %s\n Stdout: %s\n Stderr: %s\n" %\
             (cmd, stdout, stderr)
    return output_directories

create_indiv_rarefaction_plot(map, dir, out, prefs)
# create a list of individuals
# create a unique mapping file for each individual
# create a prefs file, same for each individual
# run beta diversity with prefs file, unique mapping file, coordinate frame and output path
# run alpha diversity with prefs, unique mapping, alpha_collated dir, output path.