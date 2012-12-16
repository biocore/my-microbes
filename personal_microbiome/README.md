The personal_microbiome_results.py script takes a variety of input and returns a list of
directories, one for each unique individual. The directories contain an html file that 
contains paths to alpha_rarefaction plots and beta_diversity plots.

Usage: 

Basic Usage:
The required options are a mapping file, a distance matrix, a directory of collated alpha
files, an output directory, and a preferences file. This will create output for all of the
individuals, if you are just testing this script the use the second example.

python personal_results.py -m StudentHouseMF072212.txt -i unweighted_unifrac_pc.txt
-c alpha_div_collated/ -o personal_micro_out -p universal_prefs.txt


If you don't want to create output for all of the individuals in the mapping file you can 
specify which individuals you wish to include. For instance to create output for
CUB027 and NAU113 would be as follows: 

python personal_results.py -m StudentHouseMF072212.txt -i unweighted_unifrac_pc.txt
-c alpha_div_collated/ -o personal_micro_out -p universal_prefs.txt -l CUB027,NAU113 

If the column indicating the individual is named something other than 'PersonalID'
you can indicate the name of that column. This will however require the updating the 
example prefs file to reflect the mapping file that is being used.

python personal_results.py -m StudentHouseMF072212.txt -i unweighted_unifrac_pc.txt
-c alpha_div_collated/ -o personal_micro_out -p universal_prefs.txt 
-n title_of_column