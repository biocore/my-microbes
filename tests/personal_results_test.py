
# File created on 08 Feb 2012
from __future__ import division

__author__ = ""
__copyright__ = ""
__credits__ = ""
__license__ = ""
__version__ = ""
__maintainer__ = ""
__email__ = ""
__status__ = ""

from unittest import TestCase, main
from util import get_personal_ids, create_personal_mapping_file

class ExampleTests(TestCase):

##Test that indiv_snp_variation returns a list of the allele variation information. 
    def test_get_personal_ids(self): 
        """Does the function return correct output when given correct output"""
        column = 'PersonalID'
        input  = [['A01393', 'GTTATCGCATGG', 'CCGGACTACHVGGGTWTCTAAT', 'student', 'na', 'na', 'armpit', 'CUB', 'CUB027'],
                  ['A00994', 'CGGATAACCTCC', 'CCGGACTACHVGGGTWTCTAAT', 'student', 'na', 'na', 'armpit', 'NAU', 'NAU113'], 
                  ['A00981', 'TAACGCTGTGTG', 'CCGGACTACHVGGGTWTCTAAT', 'student', 'na', 'na', 'armpit', 'NAU', 'NAU133'], 
                  ['A00936', 'ATTGACCGGTCA', 'CCGGACTACHVGGGTWTCTAAT', 'student', 'na', 'na', 'armpit', 'NAU', 'NAU144'], 
                  ['A01497', 'AGCGCTCACATC', 'CCGGACTACHVGGGTWTCTAAT', 'student', 'na', 'na', 'armpit', 'NCS', 'NCS210'], 
                  ['A00663', 'CTCATCATGTTC', 'CCGGACTACHVGGGTWTCTAAT', 'student', 'na', 'na', 'armpit', 'NCS', 'NCS214'], 
                  ['A01367', 'GCAACACCATCC', 'CCGGACTACHVGGGTWTCTAAT', 'student', 'na', 'na', 'armpit', 'CUB', 'CUB000'], 
                  ['A01383', 'GCTTGAGCTTGA', 'CCGGACTACHVGGGTWTCTAAT', 'student', 'na', 'na', 'armpit', 'CUB', 'CUB003'], 
                  ['A01332', 'AGTAGCGGAAGA', 'CCGGACTACHVGGGTWTCTAAT', 'student', 'na', 'na', 'armpit', 'CUB', 'CUB004']]
        expected = ['CUB027', 'NAU113', 'NAU133', 'NAU144', 'NCS210', 'NCS214', 'CUB000', 'CUB003', 'CUB004']
        self.assertEqual(get_personal_ids(input, 8), expected)
        
    def test_create_personal_mapping_file(self): 
        """Does the function return correct output when given correct input?"""
        map_as_list = [['A01393', 'GTTATCGCATGG', 'CCGGACTACHVGGGTWTCTAAT', 'student', 'na', 'na', 'armpit', 'CUB', 'CUB027'],
                       ['A00994', 'CGGATAACCTCC', 'CCGGACTACHVGGGTWTCTAAT', 'student', 'na', 'na', 'armpit', 'NAU', 'NAU113'], 
                       ['A00981', 'TAACGCTGTGTG', 'CCGGACTACHVGGGTWTCTAAT', 'student', 'na', 'na', 'armpit', 'NAU', 'NAU133'], 
                       ['A00936', 'ATTGACCGGTCA', 'CCGGACTACHVGGGTWTCTAAT', 'student', 'na', 'na', 'armpit', 'NAU', 'NAU144'], 
                       ['A01497', 'AGCGCTCACATC', 'CCGGACTACHVGGGTWTCTAAT', 'student', 'na', 'na', 'armpit', 'NCS', 'NCS210'], 
                       ['A00663', 'CTCATCATGTTC', 'CCGGACTACHVGGGTWTCTAAT', 'student', 'na', 'na', 'armpit', 'NCS', 'NCS214'], 
                       ['A01367', 'GCAACACCATCC', 'CCGGACTACHVGGGTWTCTAAT', 'student', 'na', 'na', 'armpit', 'CUB', 'CUB000'], 
                       ['A01383', 'GCTTGAGCTTGA', 'CCGGACTACHVGGGTWTCTAAT', 'student', 'na', 'na', 'armpit', 'CUB', 'CUB003'], 
                       ['A01332', 'AGTAGCGGAAGA', 'CCGGACTACHVGGGTWTCTAAT', 'student', 'na', 'na', 'armpit', 'CUB', 'CUB004']]
        header = ['SampleID', 'BarcodeSequence', 'LinkerPrimerSequence', 'Study', 'HouseZipCode', 'SamplingLocation', 'BodyHabitat', 'University', 'PersonalID']
        comments = [] 
        personal_id_of_interest = 'CUB027'
        "So how do I write something out to file here and then check to make sure that is correct?"
        output_fp
        personal_id_index = 8
        individual_titles=None
        


if __name__ == "__main__":
    main()