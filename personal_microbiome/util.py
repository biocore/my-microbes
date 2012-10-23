import os
from qiime.util import qiime_system_call
from os import makedirs
from os.path import join
from qiime.parse import parse_mapping_file
from qiime.format import format_mapping_file

def create_PersonalID_list(mapping_data):
    result = []
    for i in mapping_data:
        if i[8] not in result: 
            result.append(i[8]) 
        else: 
            pass
    return result
    
def create_personal_mapping_file(map_as_list, header, comments, personal_id_of_interest, output_fp):
    """ creates mapping file on a per-individual basis """
    map_as_list = tuple(map_as_list)
    personal_map = []
    for line in map_as_list:
        personal_map.append(line[:])
    for i in personal_map:   
        if i[8] == personal_id_of_interest: 
            i.insert(9, 'Self')
        else: 
            i.insert(9, 'Other')
    personal_mapping_file = format_mapping_file(header, personal_map, comments) 
    output_f = open(output_fp,'w')
    output_f.write(personal_mapping_file)
    output_f.close()

def create_html(personal_id, output_fp):
    output_f = open(output_fp,'w')
    output_f.write('<html>')
    output_f.write('<head>')
    output_f.write('<title>Personal Microbiome Results: %s</title>' % personal_id)
    output_f.write('</head>')
    output_f.write('<body>')
    output_f.write('Subject %s: here are your personal microbiome results.' % personal_id)
    output_f.write('<hr>')
    output_f.write('Alpha rarefaction: alpha rarefaction measures ...<br>')
    output_f.write('''<a href="./alpha_rarefaction/rarefaction_plots.html">Open rarefaction plots</a>''')
    output_f.write('<hr>')
    output_f.write('Beta diversity: beta diversity shows... <br>')
    output_f.write('''<a href="./beta_diversity/unweighted_unifrac_pc_3D_PCoA_plots.html">Open beta diversity PCoA plots</a>''')
    output_f.write('<hr>')
    output_f.write('Thanks for participating in the study! Please direct any questions to ...')
    output_f.write('</body>')
    output_f.write('</html>')
    output_f.close()
    
def create_personal_results(mapping_fp, distance_matrix_fp, collated_dir_fp, output_fp, prefs_fp):
    map_as_list, header, comments = parse_mapping_file(open(mapping_fp, 'U'))
    PersonalID_list  = create_PersonalID_list(map_as_list)[0:2]
    header.insert(9, 'Self')  
    output_directories = []
    makedirs(output_fp)
    for person_of_interest in PersonalID_list:
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
                                     personal_mapping_file_fp)
        create_html(person_of_interest, html_fp)
        cmd = "make_rarefaction_plots.py -i %s -m %s -p %s -o %s" % (collated_dir_fp, 
                                                                     personal_mapping_file_fp,
                                                                     prefs_fp, 
                                                                     rarefaction_dir)
        stdout, stderr, return_code = qiime_system_call(cmd)
        if return_code != 0:
            print "Command failed!\nCommand: %s\n Stdout: %s\n Stderr: %s\n" %\
             (cmd, stdout, stderr)
        cmd = "make_3d_plots.py -m %s -p %s -i %s -o %s" % (personal_mapping_file_fp, 
                                                            prefs_fp, 
                                                            distance_matrix_fp, 
                                                            pcoa_dir)
        stdout, stderr, return_code = qiime_system_call(cmd)
        if return_code != 0:
            print "Command failed!\nCommand: %s\n Stdout: %s\n Stderr: %s\n" %\
             (cmd, stdout, stderr)
        
    return output_directories
    
    
    
    
    
    
    
    
    
    
    
    
    
