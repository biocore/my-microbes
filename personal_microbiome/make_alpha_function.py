from qiime.parse import parse_mapping_file
from qiime.format import format_mapping_file
from sys import argv
from os import makedirs
from os.path import join

script_name, map, dir, out, prefs = argv

def create_PersonalID_list(mapping_data):
    result = []
    for i in mapping_data:
        if i[8] not in result: 
            result.append(i[8]) 
        else: 
            pass
    return result

def create_personal_mapping_file(map_as_list, header, comments, personal_id_of_interest):
    """ creates mapping file on a per-individual basis """
    for line in map_list: 
        if line[8] == personal_id_of_interest: 
            line.insert(9, 'yes')
        else: 
            line.insert(9, 'no')
    personal_mapping_file = format_mapping_file(header, map_list, comments) 
    return personal_mapping_file
    
    ##
    ##
def create_indiv_rarefaction_plot(mapping_fp, collated_dir_fp, output_fp, prefs_fp):
    map_as_list, header, comments = parse_mapping_file(open(mapping_fp, 'U'))
    header.insert(9, 'Self')
    PersonalID_list = create_PersonalID_list(map_as_list)  
    output_directories = []
    makedirs(output_fp)
    for person_of_interest in PersonalID_list:
        makedirs(join(output_fp, person_of_interest))
        personal_output_dir = join(output_fp, person_of_interest, "%s_rarefaction" % person_of_interest)
        output_directories.append(personal_output_dir)
        personal_map_fp = join(output_fp, person_of_interest, "%s_map.txt" % person_of_interest)
        cmd = "make_rarefaction_plots.py -i %s -m %s -p %s -o %s" % (collated_dir_fp, 
                                                                     personal_map_fp,
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