#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Healthy Eating Index and NDSR functions
This expects a typical zipfile structure from an NDSR download
Created on Thu Oct  3 16:23:45 2019
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

def file_org(infile, arglist, important):
    # print(infile, arglist, important)
    if arglist['OPTS'] == False:
        arglist['OPTS']=[arglist['NAMES']]
        file_dict = {"set_04": {"%s"%arglist['NAMES']:{}}, "set_09": {"%s"%arglist['NAMES']: {}}}
        file_dict['set_04']["%s"%arglist['NAMES']]["files"] = [x for x in glob.glob(os.path.join(infile,'*04.txt')) if "%s"%arglist['NAMES'] in x]
        file_dict['set_09']["%s"%arglist['NAMES']]["files"] = [x for x in glob.glob(os.path.join(infile,'*09.txt')) if "%s"%arglist['NAMES'] in x]
        arglist['OPTS']=[arglist['NAMES']]

    else:
#        num=len(arglist['OPTS'])
        file_dict={"set_04":{},"set_09":{}}
        for item in arglist['OPTS']:
            print('this is the item %s'%item)
            file_dict["set_04"][item]= {}
            file_dict["set_09"][item]= {}

        for key,value in file_dict.items():
            keys=list(file_dict[key].keys())
            for k in keys:
                print(k)
                file_dict['set_04']["%s"%k]["files"] = [x for x in glob.glob(os.path.join(infile,'*04.txt')) if '%s'%k in x]
                file_dict['set_09']["%s"%k]["files"] = [x for x in glob.glob(os.path.join(infile,'*09.txt')) if '%s'%k in x]

    return_dict={}
    for ki in arglist['OPTS']:
        temp_list = []
        print(ki)
        for file in file_dict["set_04"]["%s"%ki]["files"]:
            temp_df =  pd.read_csv(file, sep="\t", encoding='latin1')
            temp_df=temp_df.drop([0])
            for val in temp_df["Participant ID"]:
                _id = str(val).lstrip("0").split("_")[0]
                temp_df.replace(val, _id, inplace=True)
            temp_list.append(temp_df)
        dfm4_original = pd.concat(temp_list, ignore_index=True)
        print("Final dataframe size: ", dfm4_original.shape)
        dfm4_original = dfm4_original.sort_values(by="Participant ID")

        for col in dfm4_original:
            if dfm4_original[col].dtype == np.object_:
                dfm4_original[col] = (dfm4_original[col].replace(',','.', regex=True))

        temp_list = []
        for file in file_dict["set_09"]["%s"%ki]["files"]:
            temp_df = pd.read_csv(file,encoding='latin1', sep="\t")
            temp_df=temp_df.drop([0])
            for val in temp_df["Participant ID"]:
                _id = str(val).strip("0").strip(".").split("_")[0]
                temp_df.replace(val, _id, inplace=True)
            temp_list.append(temp_df)
        dfm9_original = pd.concat(temp_list, ignore_index=True)
        dfm9_original = dfm9_original.sort_values(by="Participant ID")

        concat_filepath = os.path.join(arglist['SAVE'],'%s_dataset4.txt'%(ki))
        dfm4_original.to_csv(concat_filepath, index=False, sep="\t", header=True)

        concat_filepath = os.path.join(arglist['SAVE'],'%s_dataset9.txt'%(ki))
        dfm9_original.to_csv(concat_filepath, index=False, sep="\t", header=True)

        b=list(dfm9_original['Participant ID'])
        a=list(dfm4_original['Participant ID'])

        common=list(set(a) & set(b))
        missmatch = list(set(a)-set(b))

        common4=dfm4_original[dfm4_original['Participant ID'].isin(common)]
        common9=dfm9_original[dfm9_original['Participant ID'].isin(common)]

        mm4=dfm4_original[dfm4_original['Participant ID'].isin(missmatch)]
        mm9=dfm9_original[dfm9_original['Participant ID'].isin(missmatch)]

        total_df = common4.merge(common9.drop_duplicates(subset=['Project Abbreviation','Date of Intake']), how='left')
        total_df=total_df.dropna(axis=1, how='all')
        complete=total_df[total_df.columns.intersection(important)].dropna()
        cind=list(complete.index)
        complete_df=total_df[total_df.index.isin(cind)]

        missing_df=total_df[~total_df.index.isin(cind)]
        missing_df=missing_df.append(mm4)
        missing_df=missing_df.append(mm9)

        concat_filepath = os.path.join(arglist['SAVE'],'%s_BCP_datasetTOTAL.txt'%(ki))
        complete_df.to_csv(concat_filepath, index=False, sep="\t", header=True)

        missing_filepath = os.path.join(arglist['SAVE'],'%s_BCP_datasetMissing.txt'%(ki))
        missing_df.to_csv(missing_filepath, index=False, sep="\t", header=True)
        return_dict[ki]=complete_df
    return(return_dict)


def make_components(hei_dict, complete_df):
    for key, value in hei_dict.items():
#        print(key)
        if key in ['hei_totveg','hei_greensbeans','hei_totfruit', 'hei_wholefruit']:
            x=value
            complete_df[key] = complete_df[x].astype('float').sum(axis=1)
            complete_df[key] = complete_df[key]/2
        if key in ['hei_wholegrains','hei_refinedgrains']:
            x=value
            complete_df[key] = complete_df[x].astype('float')
        if key in ['hei_dairy']:
            x=value[:-1]
            tmp= complete_df[x].astype('float').sum(axis=1)
            y=value[-1]
            if y == 'DOT0100':
                tmp2=complete_df[y].astype('float')/3
                complete_df[key]=tmp+tmp2
            else:
                print('NO DAIRY MISSING DOT0100, needs to be last in list')
        if key in ['hei_totproteins']:
            x=value[:-1]
            tmp= complete_df[x].astype('float').sum(axis=1)
            y=value[-1]
            if y == 'VEG0700':
                tmp2=complete_df[y].astype('float')*2
                complete_df[key]=tmp+tmp2
            else:
                print('NO TOTAL PROTEIN MISSING VEG0700, needs to be last in list')
        if key in ['hei_seafoodplantprot']:
            x=value[:-1]
            tmp= complete_df[x].astype('float').sum(axis=1)
            y=value[-1]
            if y == 'VEG0700':
                tmp2=complete_df[y].astype('float')*2
                complete_df[key]=tmp+tmp2
            else:
                print('NO SEAFOOD AND PLANT PROTEIN MISSING VEG0700, needs to be last in list')
        if key in ['hei_sodium']:
            x=value
            complete_df[key] = complete_df[x].astype('float')/1000
        if key in ['hei_addedsugars']:
            x=value
            complete_df[key] = complete_df[x].astype('float')*4
        if key in ['ripctsfa']:
            x=value[0]
            y=value[1]
            complete_df[key] = complete_df[x].astype('float')*complete_df[y].astype('float')
        if key in ['energy']:
            x=value
            complete_df[key] = complete_df[x].astype('float')/1000
    return(complete_df)

def grouper(complete_df, interest):
    data_dict={}
    dailyhei0409=complete_df[complete_df.columns.intersection(interest)].groupby(['Participant ID']).mean()
    dailyhei0409['Participant ID'] = dailyhei0409.index
    data_dict['hei0409']=complete_df
    data_dict['dailyhei0409']=dailyhei0409
    return(data_dict)


def adeq_check(df,inputt, output, parameter):
    if inputt in ['hei_totveg','hei_greensbeans', 'hei_totfruit', 'hei_wholefruit', 'hei_totproteins', 'hei_seafoodplantprot']:
        tmp = df[inputt]/df['energy']
        df[output] = [5 if x >= parameter else 5*(x/parameter) for x in tmp]
    elif inputt in ['hei_wholegrains', 'hei_dairy']:
        if inputt == 'hei_wholegrains':
            tmp = df[inputt]/df['energy']
            df[output] = [10 if x >= parameter else 10*(x/parameter) for x in tmp]
        else:
            tmp = df[inputt]/df['energy']
            df[output] = [10 if x >= parameter else 10*(x/parameter) for x in tmp]
    elif inputt in ['Fats']:
        FARMIN=parameter[0]
        FARMAX=parameter[1]
        tmp=df['Total Polyunsaturated Fatty Acids (PUFA) (g)']+df['Total Monounsaturated Fatty Acids (MUFA) (g)']
        tmp2=tmp/df['Total Saturated Fatty Acids (SFA) (g)']
        df[output] = [10 if x > FARMAX else 0 if x <= FARMIN else 10*((x-FARMIN)/(FARMAX-FARMIN)) for x in tmp2]

def mod_check(df,inputt, output, parameter):
    if inputt in ['hei_sodium','hei_refinedgrains']:
        tmp = df[inputt]/df['energy']
        df[output] = [0 if x >= parameter[1] else 10 if x <= parameter[0] else 10-(10*((x-parameter[0])/(parameter[1]-parameter[0]))) for x in tmp]
    if inputt in ['hei_addedsugars']:
        tmp= 100*df[inputt]/df['energy']
        df[output] = [0 if x >= parameter[1] else 10 if x < parameter[0] else 10-(10*((x-parameter[0])/(parameter[1]-parameter[0]))) for x in tmp]
    if inputt in ['hei_SFA']:
        tmp= df['% Calories from SFA']
        df[output] = [0 if x > parameter[1] else 10 if x < parameter[0] else 10-(10*((x-parameter[0])/(parameter[1]-parameter[0]))) for x in tmp]

def check(x, data, name, option, arglist):
    df=data
    toSum=['HEIX1_TOTALVEG','HEIX2_GREEN_AND_BEAN' , 'HEIX3_TOTALFRUIT' , 'HEIX4_WHOLEFRUIT' ,
           'HEIX5_WHOLEGRAIN' , 'HEIX6_TOTALDAIRY' , 'HEIX7_TOTPROT' , 'HEIX8_SEAPLANT_PROT' , 'HEIX9_FATTYACID' ,
           'HEIX10_SODIUM' , 'HEIX11_REFINEDGRAIN' , 'HEIX12_ADDEDSUGARS' , 'HEIX13_SATFATS']
    for key,values in x.items():
        print('Calculating score for %s'%key)
        if key in ['hei_totveg','hei_greensbeans', 'hei_totfruit', 'hei_wholefruit', 'hei_totproteins', 'hei_seafoodplantprot',
                    'hei_wholegrains', 'hei_dairy','Fats']:
            if key == 'Fats':
                adeq_check(df, key, values['name'], values['parameters'])
            else:
                adeq_check(df, key, values['name'], values['parameters'][0])
        if key in ['hei_sodium','hei_refinedgrains','hei_addedsugars','hei_SFA']:
            mod_check(df, key, values['name'], values['parameters'])

    df['HEI2015_TOTAL_SCORE']=df[df.columns.intersection(toSum)].sum(axis=1)
    print(list(df.columns))
    concat_filepath = os.path.join(arglist['SAVE'],'%s_%s_HEI.txt'%(option, name))
    df.to_csv(concat_filepath, index=False, sep="\t", header=True)


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
