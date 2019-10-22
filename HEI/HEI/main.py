#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  22 2019
Built with python 3.6
@author: gracer
"""
import os, glob
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')
from zipfile import ZipFile
import argparse

import HEI

def main():
    if arglist['SAVE'] == False:
        print('Hi')
        arglist.pop('SAVE')
        arglist['SAVE']=arglist['BASEPATH']
    print(arglist)

#    Dictionaries and lists

    important=['Participant ID','VEG0100','VEG0200','VEG0300','VEG0400','VEG0800','VEG0450','VEG0700',
           'VEG0600','VEG0900','VEG0500','VEG0100','VEG0700','FRU0100','FRU0200','FRU0300','FRU0400',
           'FRU0500','FRU0600','FRU0700','FRU0300','FRU0400','FRU0500','FRU0600','FRU0700',
           'Whole Grains (ounce equivalents)','DMF0100','DMR0100','DML0100','DMN0100','DMF0200',
           'DMR0200','DML0200','DML0300','DML0400','DCF0100','DCR0100','DCL0100','DCN0100','DYF0100',
           'DYR0100','DYL0100','DYF0200','DYR0200','DYL0200','DYN0100','DOT0300','DOT0400','DOT0500',
           'DOT0600','DOT0100','MRF0100','MRL0100','MRF0200','MRL0200','MRF0300','MRL0300','MRF0400',
           'MRL0400','MCF0200','MCL0200','MRF0500','MPF0100','MPL0100','MPF0200','MFF0100','MFL0100',
           'MFF0200','MSL0100','MSF0100','MCF0100','MCL0100','MOF0100','MOF0200','MOF0300','MOF0400',
           'MOF0500','MOF0600','MOF0700','VEG0700','MFF0100','MFL0100','MFF0200','MSL0100','MSF0100',
           'MOF0500','MOF0600','MOF0700','VEG0700','Sodium (mg)','Refined Grains (ounce equivalents)',
           'Added Sugars (by Total Sugars) (g)','% Calories from SFA','Energy (kcal)',
           'Total Polyunsaturated Fatty Acids (PUFA) (g)','Total Monounsaturated Fatty Acids (MUFA) (g)',
           'Total Saturated Fatty Acids (SFA) (g)']

    para_dict = {'hei_totveg': {'parameters':[1.1], 'name': 'HEIX1_TOTALVEG'},
             'hei_greensbeans': {'parameters':[0.2], 'name': 'HEIX2_GREEN_AND_BEAN'},
             'hei_totfruit': {'parameters':[0.8], 'name': 'HEIX3_TOTALFRUIT'},
             'hei_wholefruit': {'parameters':[0.4], 'name': 'HEIX4_WHOLEFRUIT'},
             'hei_wholegrains': {'parameters':[1.5], 'name': 'HEIX5_WHOLEGRAIN'},
             'hei_dairy': {'parameters':[1.3], 'name': 'HEIX6_TOTALDAIRY'},
             'hei_totproteins': {'parameters':[2.5], 'name': 'HEIX7_TOTPROT'},
             'hei_seafoodplantprot': {'parameters':[0.8], 'name': 'HEIX8_SEAPLANT_PROT'},
             'hei_refinedgrains': {'parameters':[1.8,4.3], 'name': 'HEIX11_REFINEDGRAIN'},
             'hei_addedsugars': {'parameters':[6.5,26], 'name': 'HEIX12_ADDEDSUGARS'},
             'hei_SFA': {'parameters':[8,16], 'name': 'HEIX13_SATFATS'},
             'Fats': {'parameters':[1.2,2.5], 'name': 'HEIX9_FATTYACID'},
             'hei_sodium':{'parameters':[1.1,2.0],'name':'HEIX10_SODIUM'}
            }
    hei_dict={'hei_totveg':
          ['VEG0100','VEG0200','VEG0300','VEG0400','VEG0800','VEG0450','VEG0700','VEG0600','VEG0900','VEG0500'],
          'hei_greensbeans':
          ['VEG0100','VEG0700'],
          'hei_totfruit':
          ['FRU0100','FRU0200','FRU0300','FRU0400','FRU0500','FRU0600','FRU0700'],
          'hei_wholefruit':
          ['FRU0300','FRU0400','FRU0500','FRU0600','FRU0700'],
          'hei_wholegrains':
          ['Whole Grains (ounce equivalents)'],
          'hei_dairy':
          ['DMF0100','DMR0100','DML0100','DMN0100','DMF0200','DMR0200','DML0200',
                       'DML0300','DML0400','DCF0100','DCR0100','DCL0100','DCN0100','DYF0100',
                       'DYR0100','DYL0100','DYF0200','DYR0200','DYL0200','DYN0100',
                       'DOT0300','DOT0400','DOT0500','DOT0600','DOT0100'],
          'hei_totproteins':
          ['MRF0100','MRL0100','MRF0200','MRL0200','MRF0300','MRL0300','MRF0400',
                             'MRL0400','MCF0200','MCL0200','MRF0500','MPF0100','MPL0100','MPF0200',
                             'MFF0100','MFL0100','MFF0200','MSL0100',
                             'MSF0100','MCF0100','MCL0100','MOF0100','MOF0200','MOF0300','MOF0400','MOF0500',
                             'MOF0600','MOF0700','VEG0700'],
          'hei_seafoodplantprot':
          ['MFF0100','MFL0100','MFF0200','MSL0100','MSF0100','MOF0500','MOF0600','MOF0700','VEG0700'],
          'hei_sodium':
          ['Sodium (mg)'],
          'hei_refinedgrains':
          ['Refined Grains (ounce equivalents)'],
          'hei_addedsugars':
          ['Added Sugars (by Total Sugars) (g)'],
          'ripctsfa': ['% Calories from SFA','Energy (kcal)'],
         'energy':
         ['Energy (kcal)'],
         'fats':
         ['Total Polyunsaturated Fatty Acids (PUFA) (g)','Total Monounsaturated Fatty Acids (MUFA) (g)',
         'Total Saturated Fatty Acids (SFA) (g)']}

    interest = ['Participant ID','Energy (kcal)', 'hei_totveg', 'hei_greensbeans', 'hei_totfruit', 'hei_wholefruit', 'hei_wholegrains',
            'hei_dairy', 'hei_totproteins', 'hei_seafoodplantprot', 'Total Polyunsaturated Fatty Acids (PUFA) (g)',
            'Total Monounsaturated Fatty Acids (MUFA) (g)', 'Total Saturated Fatty Acids (SFA) (g)',
            'hei_sodium', 'hei_refinedgrains', 'hei_addedsugars', 'ripctsfa','energy','% Calories from SFA']


 # Find the data

    for (dirpath, dirnames, filenames) in os.walk(arglist['BASEPATH']):
        for filename in filenames:
            if filename.endswith('.zip'):
                #print(filename)
                tmppath=os.sep.join([dirpath, filename])
                #print(tmppath)
                with ZipFile(tmppath, 'r') as zipObj:
                   # Get a list of all archived file names from the zip
                   listOfFileNames = zipObj.namelist()
                   # Iterate over the file names
                   for fileName in listOfFileNames:
                       # Check filename endswith csv
                        if fileName.endswith('04.txt'):
                            zipObj.extract(fileName, os.path.join(arglist['BASEPATH'],'temp_txt'))
                        if fileName.endswith('09.txt'):
                            zipObj.extract(fileName, os.path.join(arglist['BASEPATH'],'temp_txt'))
    infile = os.path.join(arglist['BASEPATH'],'temp_txt')

#Get func-y
    x=file_org(infile, arglist, important)
    for key,value in x.items():
        y=make_components(hei_dict, value)
        z=grouper(y, interest)
        for k, item in z.items():
            print(k)
            check(para_dict, item, k, key)

if __name__ == "__main__":
    #commandline parser
    parser=argparse.ArgumentParser(description='Calculating HEI')

    parser.add_argument('-basepath', dest='BASEPATH', action='store',
                        default=False, help='Where dem files at boo?')
    parser.add_argument('-file_names',dest='NAMES', action='store',
                        default=False, help='What do you want the output 04 and 09 called?')
    parser.add_argument('-options',dest='OPTS', nargs='+',
                        default=False, help='Do you have multiple different 04 and 09 files that need to be kept seperate? Please enter strings that can be searched with (this should be in the file path) no commas')
    parser.add_argument('-child',dest='CHILD', action='store',
                        default=False, help='Is this pediatric data? If True, then you need the following other files: ')
    parser.add_argument('-save',dest='SAVE', action='store',
                        default=False, help='Path to save output, if not filled in will default to the basepath')

    args = parser.parse_args()
    arglist={}
    for a in args._get_kwargs():
        arglist[a[0]]=a[1]

    main()
