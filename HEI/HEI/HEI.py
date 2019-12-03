#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Healthy Eating Index and NDSR functions
This expects a typical zipfile structure from an NDSR download
Can create pediatric (infant) DQI not validated
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
from datetime import datetime



def file_org(infile, arglist, important):
    # will create a dictionary with the file paths to all the data
    if arglist['OPTS'] == False:
        arglist['OPTS']=[arglist['NAMES']]
        file_dict = {"set_04": {"%s"%arglist['NAMES']:{}}, "set_09": {"%s"%arglist['NAMES']: {}}}
        file_dict['set_04']["%s"%arglist['NAMES']]["files"] = [x for x in glob.glob(os.path.join(infile,'*04.txt')) if "%s"%arglist['NAMES'] in x]
        file_dict['set_09']["%s"%arglist['NAMES']]["files"] = [x for x in glob.glob(os.path.join(infile,'*09.txt')) if "%s"%arglist['NAMES'] in x]
        arglist['OPTS']=[arglist['NAMES']]

    else:
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

    return(file_dict)

def file_reader(arglist, file_dict):
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

        concat_filepath = os.path.join(arglist['SAVE'],'%s_dataset4.csv'%(ki))
        dfm4_original.to_csv(concat_filepath, index=False, sep=",", header=True)

        concat_filepath = os.path.join(arglist['SAVE'],'%s_dataset9.csv'%(ki))
        dfm9_original.to_csv(concat_filepath, index=False, sep=",", header=True)
    return(dfm9_original, dfm4_original)

def diet_maker(dfm9_original,dfm4_original, ki):
    mer = pd.merge(b,c, on=['Participant ID','Date of Intake','Project Abbreviation'])
    mer.drop_duplicates(subset=['Participant ID', 'Date of Intake'], inplace=True)

    total_df=mer.dropna(axis=1, how='all')
    complete_df=total_df[total_df.columns.intersection(important)].dropna()

    concat_filepath = os.path.join(arglist['SAVE'],'%s_BCP_datasetTOTAL.csv'%(ki))
    total_df.to_csv(concat_filepath, index=False, sep=",", header=True)

    concat_filepath = os.path.join(arglist['SAVE'],'%s_BCP_datasetINTEREST.csv'%(ki))
    complete_df.to_csv(concat_filepath, index=False, sep=",", header=True)
    return(complete_df)


def make_components(hei_dict, complete_df):
    for key, value in hei_dict.items():
        if key in ['hei_totveg','hei_greensbeans','hei_totfruit', 'hei_wholefruit']:
            #these are in cups
            x=value
            complete_df[key] = complete_df[x].astype('float').sum(axis=1)
            complete_df[key] = complete_df[key]/2
        if key in ['hei_wholegrains','hei_refinedgrains']:
            # these are in oz
            x=value
            complete_df[key] = complete_df[x].astype('float')
        if key in ['hei_dairy']:
            # these are in cups
            x=value
            tmp= complete_df[x].astype('float').sum(axis=1)
            y=value[-1]
            if y == 'DOT0100':
                tmp2=complete_df[y].astype('float')/3
                complete_df[key]=tmp+tmp2
            else:
                print('NO DAIRY MISSING DOT0100, needs to be last in list')
        if key in ['hei_totproteins']:
            # these are in oz
            x=value
            tmp= complete_df[x].astype('float').sum(axis=1)
            y=value[-1]
            if y == 'VEG0700':
                tmp2=complete_df[y].astype('float')*2 # this is normally 1/2
                complete_df[key]=tmp+tmp2
            else:
                print('NO TOTAL PROTEIN MISSING VEG0700, needs to be last in list')
        if key in ['hei_seafoodplantprot']:
            # these are in oz
            x=value
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



def make_hei(complete_df, make_hei_dict):
    print('START')
    print(make_hei_dict)
    for k, value in make_hei_dict.items():
        x=value
        complete_df[k] = complete_df[x].astype('float').sum(axis=1)
    return(complete_df)


def adeq_check(df,inputt, output, parameter):
    # fruit, vegetables, greens and beans, dairy are in cup/1000cal
    # grains, protein are in oz
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

def grouper(complete_df, interest, arglist):
    data_dict={}
    if arglist['CHILD'] == False:
        dailyhei0409=complete_df[complete_df.columns.intersection(interest)].groupby(['Participant ID']).mean()
        dailyhei0409['Participant ID'] = dailyhei0409.index
        data_dict['hei0409']=complete_df
        data_dict['dailyhei0409']=dailyhei0409
        return(data_dict)

def check(dic, data, name, option, arglist):
    df=data
    toSum=['HEIX1_TOTALVEG','HEIX2_GREEN_AND_BEAN' , 'HEIX3_TOTALFRUIT' , 'HEIX4_WHOLEFRUIT' ,
           'HEIX5_WHOLEGRAIN' , 'HEIX6_TOTALDAIRY' , 'HEIX7_TOTPROT' , 'HEIX8_SEAPLANT_PROT' , 'HEIX9_FATTYACID' ,
           'HEIX10_SODIUM' , 'HEIX11_REFINEDGRAIN' , 'HEIX12_ADDEDSUGARS' , 'HEIX13_SATFATS']
    for key,values in dic.items():
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
    concat_filepath = os.path.join(arglist['SAVE'],'%s_%s_HEI.csv'%(option, name))
    df.to_csv(concat_filepath, index=False, sep=",", header=True)
