#!/usr/bin/env python
from __future__ import division

__author__ = "John Chase"
__copyright__ = "Copyright 2013, The QIIME project"
__credits__ = ["John Chase", "Greg Caporaso"]
__license__ = "GPL"
__version__ = "0.0.0-dev"
__maintainer__ = "John Chase"
__email__ = "jc33@nau.edu"

from unittest import TestCase, main
from qiime.parse import parse_mapping_file
from personal_microbiome.util import get_personal_ids, create_personal_mapping_file

class ExampleTests(TestCase):

    def setUp(self):
        # Define some data here...
        self.mapping_data = parse_mapping_file(mapping_str.split('\n'))

##Test that indiv_snp_variation returns a list of the allele variation information. 
    def test_get_personal_ids(self): 
        """Does the function return correct output when given correct output"""
        obs = get_personal_ids(self.mapping_data)
        
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
        
mapping_str = """
S1
S2
S3
"""

if __name__ == "__main__":
    main()