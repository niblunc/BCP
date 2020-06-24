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
import pdb
import HEI
import DQI
import sys

def main(arglist):
    if arglist['SAVE'] == False:
        print('Hi')
        arglist.pop('SAVE')
        arglist['SAVE']=arglist['BASEPATH']
    print(arglist)
    print('Using python version:', sys.version[:5])

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
           'Total Saturated Fatty Acids (SFA) (g)','FRU0100','FRU0200','DMF0200','DMR0200','DML0200','DML0300',
           'SWT0600','BVS0400','BVS0300','BVS0500','BVS0100','BVS0200','BVS0600','BVS0700', 'SWT0600','SWT0100',
           'SWT0200','SWT0300','SWT0700' , 'SWT0800','SWT0400','SWT0500','DOT0300' , 'DOT0400',
           'DOT0100','DOT0200','GRR0800' , 'GRS0800',  'GRW0800','GRW0900' ,'GRS0900' , 'GRR0900' ,
           'GRW1100' , 'GRW1200', 'GRW0400' ,'GRS0400' ,'GRR0400','VEG0800','FMC0100', 'FMC0200','DMF0100',
           'DMR0100','DML0100','DMN0100' ,'DMF0200','DMR0200','DML0200','DOT0500', 'DOT0600','DOT0700',
           'DOT0800','GRW0600','GRS0600','GRR0600','GRW0700','GRS0700','GRR0700','GRW1300','GRS1300']

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

    ped811_dict = {
        'hei_vegetables': {'parameters':[0.1,1.9], 'name': 'HEIX1_VEGETABLES'},
        'hei_totfruit': {'parameters':[0.1,1.9], 'name': 'HEIX2_TOTALFRUIT'},
        'hei_wholegrains': {'parameters':[1.0,3.5,0.0 , 8.0], 'name': 'HEIX3_WHOLEGRAIN'},
        'hei_milk': {'parameters':[20,28,8,35], 'name': 'HEIX4_TOTALDAIRY'},
        'hei_proteins': {'parameters':[2.5,6.0,0,10.0], 'name': 'HEIX5_PROTEIN'},
        'hei_refinedgrains': {'parameters':[1.6,3.5], 'name': 'HEIX6_REFINEDGRAIN'},
        'hei_fruitjuice': {'parameters':[0.1,6.0], 'name': 'HEIX7_FRUITJUICE'},
        'hei_SSB': {'parameters':[0.1,4.0], 'name': 'HEIX8_SSB'},
        'hei_sweets': {'parameters':[0.1,1.0], 'name': 'HEIX9_SWEETS'},
        'hei_salty': {'parameters':[0.1,1.0], 'name': 'HEIX10_SALTY'}
            }

    ped1224_dict = {
        'hei_vegetables': {'parameters':[0.1,7.9], 'name': 'HEIX1_VEGETABLES'},
        'hei_totfruit': {'parameters':[0.1,7.9], 'name': 'HEIX2_TOTALFRUIT'},
        'hei_wholegrains': {'parameters':[1.5, 5.5, 0, 8.0], 'name': 'HEIX3_WHOLEGRAIN'},
        'hei_milk': {'parameters':[14.0,18.0,8.0,24.0], 'name': 'HEIX4_TOTALDAIRY'},
        'hei_proteins': {'parameters':[2.0,3.0,0,6.0], 'name': 'HEIX5_PROTEIN'},
        'hei_refinedgrains': {'parameters':[1.9, 4.2], 'name': 'HEIX6_REFINEDGRAIN'},
        'hei_fruitjuice': {'parameters':[4.1,6.0], 'name': 'HEIX7_FRUITJUICE'},
        'hei_SSB': {'parameters':[0.1,4.0], 'name': 'HEIX8_SSB'},
        'hei_sweets': {'parameters':[0.1,1.0], 'name': 'HEIX9_SWEETS'},
        'hei_salty': {'parameters':[0.1,1.0], 'name': 'HEIX10_SALTY'}
            }

    ped08_dict = {
        'hei_vegetables': {'parameters':[0,0], 'name': 'HEIX1_VEGETABLES'},
        'hei_totfruit': {'parameters':[0,0], 'name': 'HEIX2_TOTALFRUIT'},
        'hei_wholegrains': {'parameters':[0,0,0,0], 'name': 'HEIX3_WHOLEGRAIN'},
        'hei_dairy': {'parameters':[0,0,0,0], 'name': 'HEIX4_TOTALDAIRY'},
        'hei_proteins': {'parameters':[0,0,0,0], 'name': 'HEIX5_PROTEIN'},
        'hei_refinedgrains': {'parameters':[0,0], 'name': 'HEIX6_REFINEDGRAIN'},
        'hei_fruitjuice': {'parameters':[0,0], 'name': 'HEIX7_FRUITJUICE'},
        'hei_SSB': {'parameters':[0,0], 'name': 'HEIX8_SSB'},
        'hei_sweets': {'parameters':[0,0], 'name': 'HEIX9_SWEETS'},
        'hei_salty': {'parameters':[0,0], 'name': 'HEIX10_SALTY'},
        'hei_cereal': {'parameters':[0,0], 'name': 'HEIX11_CEREAL'}
    }
    ped_dict={'young': ped811_dict,
        'child':ped1224_dict,
        'infant':ped08_dict
    }


    hei_dict={
          'hei_totveg':
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
          'ripctsfa':
          ['% Calories from SFA','Energy (kcal)'],
         'energy':
         ['Energy (kcal)'],
         'fats':
         ['Total Polyunsaturated Fatty Acids (PUFA) (g)','Total Monounsaturated Fatty Acids (MUFA) (g)',
         'Total Saturated Fatty Acids (SFA) (g)']
         }

    hei_ped_dict={'hei_totveg':
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
            'hei_refinedgrains':
            ['Refined Grains (ounce equivalents)'],
           'energy':
           ['Energy (kcal)'],
            'hei_fruitjuice':
            ['FRU0100','FRU0200'],
            'hei_SSB':
            ['DMF0200','DMR0200','DML0200','DML0300','SWT0600','BVS0400','BVS0300','BVS0500','BVS0100','BVS0200','BVS0600','BVS0700', 'SWT0600'],
            'chocolate_candies':
            ['SWT0100'],
            'candies':
            ['SWT0200'],
            'frosting':
            ['SWT0300'],
            'sweet_sauce':
            ['SWT0700' , 'SWT0800' ],
            'sugar':
            ['SWT0400' ],
            'syrups':
            ['SWT0500' ],
            'Pudding':
            ['DOT0300' , 'DOT0400'],
            'icecream':
            ['DOT0100' ],
            'nondairy_treat':
            ['DOT0200' ],
            'baked_good':
            ['GRR0800' , 'GRS0800',  'GRW0800' ],
            'chips':
            ['GRW0900' ,'GRS0900' , 'GRR0900' , 'GRW1100' , 'GRW1200', 'GRW0400' ,'GRS0400' ,'GRR0400' ],
            'fries':
            ['VEG0800' ],
            'other_fried':
            ['FMC0100', 'FMC0200' ],
            'milk':
            ['DMF0100','DMR0100','DML0100','DMN0100' ,'DMF0200','DMR0200','DML0200','DOT0500', 'DOT0600'],
            'formula_foz':
            ['DOT0700', 'DOT0800'],
            'cereal_oz':
            ['GRW0600','GRS0600','GRR0600','GRW0700','GRS0700','GRR0700'],
            'bbcereal_hcup':
            ['GRW1300','GRS1300']
            }

    conv_dict={
    'hei_fruitjuice':4,
    'hei_SSB':8,
    'chocolate_candies':40,
    'candies':15,
    'frosting':35,
    'sugar':4,
    'syrups':.25,
    'Pudding':1,
    'icecream':.5,
    'nondairy_treat':85,
    'baked_good':55,
    'fries': 70,
    'formula_foz':5,
    'bbcereal_hcup':.5
    }

    make_hei_dict={
    'hei_sweets' :
    ['chocolate_candies','candies','frosting','sweet_sauce','sugar','syrups','Pudding', 'icecream','nondairy_treat','baked_good'],
    'hei_salty' :
    ['chips','other_fried','fries'],
    'hei_vegetables':
    ['hei_totveg', 'hei_greensbeans'],
    'hei_proteins':
    ['hei_totproteins','hei_seafoodplantprot'],
    'hei_milk':
    ['hei_dairy','formula_foz'],
    'hei_cereal':
    ['cereal_oz', 'bbcereal_hcup']
    }

    interest = ['Participant ID','Energy (kcal)', 'hei_totveg', 'hei_greensbeans', 'hei_totfruit', 'hei_wholefruit', 'hei_wholegrains','hei_dairy', 'hei_totproteins', 'hei_seafoodplantprot', 'Total Polyunsaturated Fatty Acids (PUFA) (g)',
            'Total Monounsaturated Fatty Acids (MUFA) (g)', 'Total Saturated Fatty Acids (SFA) (g)',
            'hei_sodium', 'hei_refinedgrains', 'hei_addedsugars', 'ripctsfa','energy','% Calories from SFA']

    ped_interest = ['Participant ID','Energy (kcal)', 'hei_totveg', 'hei_greensbeans', 'hei_totfruit', 'hei_wholefruit', 'hei_wholegrains','hei_dairy', 'hei_totproteins', 'hei_seafoodplantprot',
            'hei_refinedgrains', 'hei_addedsugars', 'ripctsfa','energy','chocolate_candies','candies','frosting','sweet_sauce','sugar','syrups','Pudding', 'icecream','nondairy_treat','baked_good',
            'chips','other_fried','fries']


 # Find the data

    for (dirpath, dirnames, filenames) in os.walk(basepath):
        for filename in filenames:
            if filename.endswith('.zip'):
                tmppath=os.sep.join([dirpath, filename])
                with ZipFile(tmppath, 'r') as zipObj:
                   # Get a list of all archived file names from the zip
                   listOfFileNames = zipObj.namelist()
                   # Iterate over the file names
                   for fileName in listOfFileNames:
                       # Check filename endswith txt
                        if fileName.endswith('04.txt'):
                            zipObj.extract(fileName, os.path.join(basepath,'temp_txt'))
                        if fileName.endswith('09.txt'):
                            zipObj.extract(fileName, os.path.join(basepath,'temp_txt'))
    infile = os.path.join(basepath,'temp_txt')

    if arglist['CHILD'] == False:
        x=HEI.file_org(infile, arglist, important)
        for key,value in x.items():
            y=HEI.make_components(hei_dict, value)
            test=['hei_totveg','hei_greensbeans','hei_totfruit','hei_wholefruit','hei_wholegrains','hei_dairy','hei_totproteins','hei_seafoodplantprot','hei_refinedgrains','hei_addedsugars','hei_sodium']
            y=y[(y[test] > 0).all(1)]
            z=HEI.grouper(y, interest, arglist)
            for k, item in z.items():
                HEI.check(para_dict, item, k, key, arglist)
    else:
        a=HEI.file_org(infile, arglist, important)
        df0=a[arglist['OPTS'][0]]
        b,c=HEI.file_reader(arglist, df0)
        e = HEI.diet_maker(b,c, arglist['NAMES'])
        df_demo=pd.read_csv(os.path.join(basepath,arglist['XTRA']), sep=",")
        e['Participant ID'] = e['Participant ID'].astype('int32')
        df_demo['Participant ID'] = df_demo['Participant ID'].astype('int32')
        df = pd.merge(e,df_demo, on=['Participant ID'])
        df['Age_at_Intake']=DQI.ager(df['Date of Intake'], df['DoB'])
        x=DQI.BCP(df, arglist)
        y=DQI.make_ped_components(hei_ped_dict, x, conv_dict)
        que=HEI.make_hei(y, make_hei_dict)
        split_dict=DQI.splitter(que)
        for key, value in split_dict.items():
            if key == 'DF_child':
                DQI.DQI_BF(value, 'HEIX0_BREASTFEEDING', 'child')
                DQI.check(ped_dict['child'], value, 'child', key, arglist)
            elif key == 'DF_young':
                DQI.DQI_BF(value, 'HEIX0_BREASTFEEDING', 'young')
                DQI.check(ped_dict['young'], value, 'young', key, arglist)
            else:
                DQI.DQI_BF(value, 'HEIX0_BREASTFEEDING', 'infant')
                DQI.check(ped_dict['infant'], value, 'infant', key, arglist)



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
                        default=False, help='Is this pediatric data? If True, then you need the following other files in xtra: demographics (with birthday) and then infant feeding data')
    # Need to change this! New outline#####################################################################################
    parser.add_argument('-xtra', dest='XTRA', nargs='+',
                        default=False, help='demographics and feeding behaviors')
    ########################################################################################################################
    parser.add_argument('-save',dest='SAVE', action='store',
                        default=False, help='Path to save output, if not filled in will default to the basepath')

    args = parser.parse_args()
    arglist={}
    for a in args._get_kwargs():
        arglist[a[0]]=a[1]

    main(arglist)
