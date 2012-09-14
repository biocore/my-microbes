import os
from sys import argv
from qiime.parse import parse_mapping_file_to_dict
from qiime.util import qiime_system_call

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
#determine which color scheme will be used. If 
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
def personal_prefs_from_map(mapping_fp, 
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
    mapping_data = parse_mapping_file_to_dict(open(mapping_fp,'U'))[0]
#.items creates a list of the dictionary. Note mapping data is a two dimensional list
# therefore this becomes a list of dictionarys. and allows for it to be looped through. 
#sample_id was the key in the original dictionary,. d is that keys values which is a 
#dictionary of  personal
    for sample_id, d in mapping_data.items():
        if d[personal_id_field] == person_of_interest:
#here the person_of_interest is will determine the color scheme that was defined in 
#get_current_color
            current_entry_is_person_of_interest = True
        else:
            current_entry_is_person_of_interest = False
        color = get_current_color(current_entry_is_person_of_interest,d[other_field])
#create an entry for each individual and other_field.   
        output_lines.append("'%s%s':'%s'," % (d[personal_id_field],d[other_field],color))

    output_lines.append('}}}}')
    #return '\n'.join(output_lines)
    output_f = open(output_fp,'w')
#write 
    output_f.write('\n'.join(output_lines))
    output_f.close()

def create_PersonalID_list(mapping_fp):
    mapping_data = parse_mapping_file_to_dict(open(mapping_fp,'U'))[0]
    result = []
    for sample_id, d in mapping_data.items():
        if d['PersonalID'] not in result: 
            result.append(d['PersonalID']) 
        else: 
            pass
    return result
    
#make_3d_plots.py -m StudentHouseMF072212.txt -p prefs_NAU113.txt -i beta_diversity/wf_bdiv_even4052/unweighted_unifrac_pc.txt -o 3dplots_NAU113

#question how will I specify an object as opposed to a file for the prefs file in
#make_3d_plots.
def create_indiv_3d_plot(mapping_fp, distance_matrix_fp): 
    PersonalID_list  = create_PersonalID_list(mapping_fp)  
# I might as well just open the mapping file here since I need to use it twice. As opposed
#to opening it in two different functions.
    output_directories = []
    for person_of_interest in PersonalID_list:
        personal_output_dir = "%s_pcoa_plots" % person_of_interest
        output_directories.append(personal_output_dir)
        personal_prefs_fp = "%s_prefs.txt" % person_of_interest
        personal_prefs_from_map(mapping_fp, 
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
#this will need to be written out to file. Unless it is already with the make_3d?
    return output_directories


def main():
#should I use arguments here or do I need to create options? parse command line 
#parameters
    script_name, mapping_fp, distance_matrix_fp = argv
    create_indiv_3d_plot(mapping_fp, distance_matrix_fp)



if __name__ == "__main__":
    main()
    
