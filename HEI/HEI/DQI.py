#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dietary Quality Index and NDSR functions
This expects a typical zipfile structure from an NDSR download
Created on Tue Dec  2 11:29:45 2019
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


### these functions are specific for BCP data, other data may not need these
def path_finder(arglist):
    #read in the data
    df1=os.path.join(arglist['BASEPATH'],arglist['SAVE'],arglist['XTRA'])
    print(df1)
    demo_df=pd.read_csv(df1, sep=',',encoding='latin1')
    return(demo_df)

def refactor(infant_df):
    infant_df['breastfed']=infant_df['breastfed'].replace({'no': 0, 'yes': 1})
    infant_df['any_formula']=infant_df['any_formula'].replace({'no': 0, 'yes': 1,'NaN':'NA'})
    infant_df['regular_formula']=infant_df['regular_formula'].replace({'no': 0, 'yes': 1,'NaN':'NA','not_answered':'NA'})
    infant_df['age_fed_dropdown']=infant_df['age_fed_dropdown'].replace({'no': 0, 'yes': 1,'NaN':'NA','not_answered':'NA','never_not_yet':0})
    infant_df['age_stop_dropdown']=infant_df['age_stop_dropdown'].replace({'no': 0, 'yes': 1,'NaN':'NA','not_answered':'NA','never_not_yet':0})
    return(infant_df)

def samesies(demo_df, infant_df):
    b=list(demo_df['PSCID'])
    a=list(infant_df['PSCID'])

    common=list(set(a) & set(b))
    #find unique elements, set the index to be the ID, make into dictionary
    demo_df=demo_df[demo_df['PSCID'].isin(common)]
    infant_df=infant_df[infant_df['PSCID'].isin(common)]
    return(demo_df, infant_df)


def ager(date1,date2):
    # Get the age in months of each recall
    diff_time = pd.to_datetime(date1)-pd.to_datetime(date2)
    diff_time= diff_time/ np.timedelta64(1, 'M')
    return(diff_time)

def BCPconcat(data):
    columns = list(data[1]['demo'].keys())
    df_ = pd.DataFrame(index=[0], columns=columns)
    cols=list(data[1].keys())
    DATA_dict={}
    for i in cols[1:]:
        print(i)
        df_ = pd.DataFrame(index=[0], columns=columns)
        for k,v in data.items():
            tmp=pd.DataFrame(data[k][i], index=[data[k]['ID']])
            df_=pd.concat([df_,tmp], axis=0)
        DATA_dict[i]=df_
    return(DATA_dict)

def total_child_df(DATA_dict, arglist):
    DF=DATA_dict['diet'].merge(DATA_dict['infant'].drop_duplicates(), left_index=True, right_index=True)
    DF=DF.merge(DATA_dict['demo'].drop_duplicates(), left_index=True, right_index=True)

    concat_filepath = os.path.join(arglist['SAVE'],'test_childimd_datasetTOTAL.csv')
    DF.to_csv(concat_filepath, index=True, sep=",", header=True)
    return(DF)

def BCP(df, arglist):

    demo_df = path_finder(arglist)

    df['PID']=df['Participant ID'].astype('int32')
    df['Date of Intake']=pd.to_datetime(df['Date of Intake'])
    df['DoB']=pd.to_datetime(df['DoB'])
    diet_df=df

    demo_df['PID']=demo_df['Participant ID'].astype('int32')
    demo_df['DoB']=pd.to_datetime(demo_df['DoB'])
    demo_df['Date_taken']=pd.to_datetime(demo_df['Date_taken'])
    demo_df['Age_taken']=ager(demo_df['Date_taken'],demo_df['DoB'])


    all_data=pd.merge(diet_df, demo_df, on=['PID','DoB'])

    all_data['Identifiers_visit']=all_data['Identifiers_visit'].astype('int32')
    all_data['child_feeding_practice-breastfed']=all_data['child_feeding_practice-breastfed'].astype('category')
    return(all_data)
############ end BCP specific #########

#### conversions #######
def cup2oz(cup):
    cup=cup.astype('float32')
    oz=cup*8
    return(oz)

def gram2oz(gram):
    oz=gram/28.3495
    return(oz)

def T2oz(T):
    oz=T/2
    return(oz)
####################

def splitter(DF):
    DF_child=DF.query('Age_taken >= 12 & Age_at_Intake >= 12 & Identifiers_visit >= 12')

    DF_young=DF.query('Age_taken < 12 & Age_at_Intake < 12 & Identifiers_visit< 12 and Age_taken >= 8 & Age_at_Intake >= 8 & Identifiers_visit >= 8')

    DF_infant=DF.query('Age_taken < 8 & Age_at_Intake < 8 & Identifiers_visit < 8')
    df={'DF_child':DF_child, 'DF_young':DF_young, 'DF_infant':DF_infant}
    return(df)
###############################################################################
#########################pediatric components##################################
def to_fluid(key,x,num, data):
      data[key] = num*(data[x].astype('float').sum(axis=1))
      return(data[key])

def to_ounce(key, x, data):
    data[key] = data[x].astype('float').sum(axis=1)
    data[key] = cup2oz(data[key]/2)
    return(data[key])

def cow_stuff(key, value, data):
    x=value[:-1]
    tmp= data[x].astype('float32').sum(axis=1)
    y=value[-1]
    if key == 'hei_dairy':
        if y == 'DOT0100':
            tmp2=data[y].astype('float32')/3
            tmp3=tmp+tmp2
            data[key]=HEI.cup2oz(tmp3)
        else:
            print('NO DAIRY MISSING DOT0100, needs to be last in list')
    if key == 'hei_totproteins':
        if y == 'VEG0700':
            tmp2=data[y].astype('float32')*2 # this is normally 1/2
            data[key]=tmp+tmp2
        else:
            print('NO TOTAL PROTEIN MISSING VEG0700, needs to be last in list')
    if key == 'hei_seafoodplantprot':
        if y == 'VEG0700':
            tmp2=data[y].astype('float32')*2
            data[key]=tmp+tmp2
        else:
            print('NO SEAFOOD AND PLANT PROTEIN MISSING VEG0700, needs to be last in list')
    return(data[key])


def grammar(key,x,num, data):
    data[key] = gram2oz(num*(data[x].astype('float').sum(axis=1)))
    return(data[key])

def from_cup(key,x,num, data):
    data[key] = cup2oz(num*(data[x].astype('float').sum(axis=1)))
    return(data[key])



###############################################################################
###############################################################################

def DQI(df, inputt, output, parameter):
    if inputt in ['hei_salty','hei_sweets','hei_SSB','hei_fruitjuice']:
        print('now calculating %s'%output)
        temp=df[inputt]
        MIN=parameter[0]
        MAX=parameter[1]
        df[output]=[2.5 if MIN < x <= MAX else 0 if x > MAX else 5 for x in temp]
    # No limit
    elif inputt in ['hei_vegetables', 'hei_totfruit']:
        print('now calculating %s'%output)
        temp=df[inputt]
        MIN=parameter[0]
        MAX=parameter[1]
        df[output]=[2.5 if MIN < x <= MAX else 0 if x == MIN else 5 for x in temp]
    # Upper limit
    elif inputt in ['hei_milk','hei_proteins']:
        print('now calculating %s'%output)
        temp=df[inputt]
        FARMIN = parameter[0]
        FARMAX = parameter[1]
        MIN = parameter[2]
        MAX = parameter[3]
        df[output]=[5 if MIN < x <= MAX else 2.5 if MIN < x <= FARMIN or MAX < x <=FARMAX else 0 for x in temp]
    elif inputt in ['hei_wholegrains']:
        print('now calculating %s'%output)
        temp=df[inputt]
        FARMIN = parameter[0]
        FARMAX = parameter[1]
        MIN = parameter[2]
        MAX = parameter[3]
        df[output]=[2.5 if MIN < x <= MAX else 1.5 if MIN < x <= FARMIN or MAX < x <=FARMAX else 0 for x in temp]
    elif inputt in ['hei_refinedgrains']:
        print('now calculating %s'%output)
        temp=df[inputt]
        MIN=parameter[0]
        MAX=parameter[1]
        df[output]=[1.5 if MIN < x <= MAX else 0 if x > MAX else 2.5 for x in temp]
    return(df)

def infant_DQI(df, inputt, output, parameter):
    #inputt, output, parameter
    MIN=0
    if inputt in ['hei_salty','hei_sweets','hei_SSB','hei_fruitjuice','hei_refinedgrains','hei_vegetables', 'hei_totfruit',
    'hei_wholegrains','hei_dairy','hei_proteins', 'hei_cereal']:
        print('now calculating infant %s'%output)
        temp=df[inputt]
        df[output]=[5 if x == MIN else 0 for x in temp]
    return(df)

def DQI_BF(df, output, age_group):
    if age_group == 'infant':
        df[output]=[15 if row['child_feeding_practice-breastfed'] == 'yes' and row['child_feeding_practice-any_formula'] != 'yes' else 10 if row['child_feeding_practice-breastfed'] == 'yes' and row['child_feeding_practice-any_formula'] == 'yes'else 5 if row['child_feeding_practice-breastfed'] == 'no' else 'NA' for index, row in df.iterrows()]
    else:
        df[output]=[10 if row['child_feeding_practice-age_stop_dropdown'] != 'yes' and row['child_feeding_practice-breastfed'] == 'yes' else 0 for index, row in df.iterrows()]

def check(dic, data, name, option, arglist):
    df=data
    for key,values in dic.items():
        if key in ['hei_vegetables','hei_totfruit','hei_wholegrains','hei_dairy','hei_milk','hei_proteins','hei_refinedgrains',
        'hei_fruitjuice','hei_SSB','hei_sweets','hei_salty','hei_cereal']:
            print('Calculating score for %s'%key)
            if name != 'infant':
                toSum=['HEIX0_BREASTFEEDING','HEIX1_VEGETABLES','HEIX2_TOTALFRUIT' , 'HEIX3_WHOLEGRAIN' , 'HEIX4_TOTALDAIRY' ,
                       'HEIX5_PROTEIN' , 'HEIX6_REFINEDGRAIN' , 'HEIX7_FRUITJUICE' , 'HEIX8_SSB', 'HEIX9_SWEETS',
                       'HEIX10_SALTY']
                DQI(df,key, values['name'], values['parameters'])
                df['HEI2015_TOTAL_SCORE']=df[df.columns.intersection(toSum)].sum(axis=1)
                concat_filepath = os.path.join(arglist['SAVE'],'%s_%s_HEI.csv'%(option, name))
                df=df.drop_duplicates(subset=['Participant ID_x', 'Date of Intake', 'Identifiers'])
                df.to_csv(concat_filepath, index=False, sep=",", header=True)
            else:
                toSum=['HEIX0_BREASTFEEDING','HEIX1_VEGETABLES','HEIX2_TOTALFRUIT'  ,
                       'HEIX5_PROTEIN' ,  'HEIX7_FRUITJUICE' , 'HEIX8_SSB', 'HEIX9_SWEETS',
                       'HEIX10_SALTY', 'HEIX11_CEREAL']
                infant_DQI(df,key, values['name'], values['parameters'])
                df['HEI2015_TOTAL_SCORE']=df[df.columns.intersection(toSum)].sum(axis=1)
                concat_filepath = os.path.join(arglist['SAVE'],'%s_%s_HEI.csv'%(option, name))
                df=df.drop_duplicates(subset=['Participant ID_x', 'Date of Intake', 'Identifiers'])
                print(df['Age_at_Intake'])
                df.to_csv(concat_filepath, index=False, sep=",", header=True)
