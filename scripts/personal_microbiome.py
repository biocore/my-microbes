import os
from sys import argv
from qiime.parse import parse_mapping_file_to_dict
from qiime.util import qiime_system_call
from os import makedirs
from os.path import join

#create color scheme for the individual. The individual of interest will be based on 
#the special_colors. Everyone else will be colored by the 'standard_colors' 
# kinemage_colors = ['hotpink','blue', 'lime','gold','red','sea','purple','green']
def get_current_color(special_coloring,field_value):
#define the colors for each body habitat. They are different for individual vs. other
    standard_colors = {'armpit':'green',
                       'palm':'green',
                       'tongue':'blue',
                       'gut':'gold',
                       'forehead':'green'}
    special_colors = {'armpit':'hotpink',
                      'palm':'hotpink',
                      'tongue':'red',
                      'gut':'purple',
                      'forehead':'hotpink'}
#determine which color scheme will be used.
    if special_coloring == True:
        try:
            return special_colors[field_value]
        except KeyError:
#this exception is for an individual that may not have data for a given habitat.
            return 'grey'
    else:
        try:
            return standard_colors[field_value]
        except KeyError:
            return 'grey'

#This function takes a mapping file, an output path for the prefs file, the
#the personal_id_field and the other_field. it defaults to BodyHabitat, meaning the prefs
#file created will contain coloring based on based on the individual and their body
#habitat
def personal_prefs_from_map(mapping_data, 
                            output_fp,
                            person_of_interest,
                            personal_id_field='PersonalID', 
                            other_field='BodyHabitat'):
#make empty list to put all of the output. 
    output_lines = []
    output_field_id = "%s&&%s" % (personal_id_field, other_field)
    output_lines.append("{'background_color':'black','sample_coloring':{")
    output_lines.append("'%s':" % output_field_id)
    output_lines.append('{')
    output_lines.append("'column':'%s'," % output_field_id)
    output_lines.append("'colors':{")
#.items creates a list of the dictionary. Note mapping data is a two dimensional list
# therefore this becomes a list of dictionarys. and allows for it to be looped through. 
#sample_id was the key in the original dictionary,. d is that keys values which is a 
#dictionary of  personalids
    for sample_id, d in mapping_data.items():
        if d[personal_id_field] == person_of_interest:
#here the person_of_interest will determine the color scheme that was defined in 
#get_current_color
            current_entry_is_person_of_interest = True
        else:
            current_entry_is_person_of_interest = False
        color = get_current_color(current_entry_is_person_of_interest,d[other_field])
#create an entry for each individual and other_field.   
        output_lines.append("'%s%s':'%s'," % (d[personal_id_field],d[other_field],color))

    output_lines.append('}}}}')
    output_f = open(output_fp,'w')
    output_f.write('\n'.join(output_lines))
    output_f.close()

def create_PersonalID_list(mapping_data):
    result = []
    for sample_id, d in mapping_data.items():
        if d['PersonalID'] not in result: 
            result.append(d['PersonalID']) 
        else: 
            pass
    return result


def create_indiv_3d_plot(mapping_fp, distance_matrix_fp, output_fp):
    mapping_data = parse_mapping_file_to_dict(open(mapping_fp,'U'))[0]
    PersonalID_list  = create_PersonalID_list(mapping_data)  
    output_directories = []
    makedirs(output_fp)
    for person_of_interest in PersonalID_list:
        makedirs(join(output_fp, person_of_interest))
        #output = join(output_dir, name, name)
        personal_output_dir = join(output_fp, person_of_interest, "%s_pcoa_plots" % person_of_interest)
        output_directories.append(personal_output_dir)
        personal_prefs_fp = join(output_fp, person_of_interest, "%s_prefs.txt" % person_of_interest)
        personal_prefs_from_map(mapping_data, 
                                personal_prefs_fp,
                                person_of_interest,
                                personal_id_field='PersonalID', 
                                other_field='BodyHabitat')
        cmd = "make_3d_plots.py -m %s -p %s -i %s -o %s" % (mapping_fp, 
                                                            personal_prefs_fp, 
                                                            distance_matrix_fp, 
                                                            personal_output_dir)
        stdout, stderr, return_code = qiime_system_call(cmd)
        if return_code != 0:
            print "Command failed!\nCommand: %s\n Stdout: %s\n Stderr: %s\n" %\
             (cmd, stdout, stderr)
    return output_directories
