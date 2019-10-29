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

### these functions are specific for BCP data, other data may not need these
def path_finder(arglist):
    #read in the data
    df1=os.path.join(arglist['BASEPATH'],arglist['XTRA'][0])
    df2=os.path.join(arglist['BASEPATH'],arglist['XTRA'][1])
    print(df1)
    demo_df=pd.read_csv(df1, sep=',')
    infant_df=pd.read_csv(df2, sep=',', encoding='latin1')
    return(demo_df,infant_df )

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


def combo(infant_df, demo_df, diet_df):
    infant_df_un=infant_df.drop_duplicates(['PSCID'])
    infant_df_un=infant_df_un.set_index('CandID')
    infant_dict=infant_df_un.to_dict('index')
    infant_dict = {str(k):v for k,v in infant_dict.items()}

    demo_df_un=demo_df.drop_duplicates(['PSCID'])
    demo_df_un=demo_df_un.set_index(str('CandID'))
    demo_dict=demo_df_un.to_dict('index')
    demo_dict = {str(k):v for k,v in demo_dict.items()}
    alldiet_dict=diet_df.to_dict('index')
    return(infant_dict, demo_dict, alldiet_dict)

def ager(alldiet_dict, demo_dict, infant_dict):
    # Get the age in months of each recall
    for key, item in alldiet_dict.items():
        print('this is the key %s'%key)
        print(item['Date of Intake'])
        print(item['Participant ID'])
        ID = item['Participant ID']
        date=datetime.strptime(item['Date of Intake'], '%m/%d/%Y')
        if ID in demo_dict:
            print('present!')
            birthday=datetime.strptime(demo_dict[ID]['DoB'], '%m/%d/%y')
            age = (date-birthday)
            print('this is the number of days %s'%age.days)
            alldiet_dict[key]['age']=float(age.days)/12
        else:
            print('NOPE')
    # Sort the data by age at input (within 1 year of diet recall)
    data = {}
    count=0
    for key, item in alldiet_dict.items():
        ID = item['Participant ID']
        if ID in demo_dict and infant_dict:
            print('GOT IT!')
            if (abs(item['age'] - infant_dict[ID]['Candidate_Age'])) < 12:
                print('SAME YEAR %s'%ID)
                count=count+1
                data[count]={'ID':ID,'demo':demo_dict[ID], 'infant':infant_dict[ID], 'diet':item}
        else:
            print('NO DICE')
    return(data)

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

def BCP(diet_df, arglist):
    #read in the data
    demo_df, infant_df = path_finder(arglist)
    #refactor
    infant_df=refactor(infant_df)
    #check similarity
    demo_df, infant_df = samesies(demo_df, infant_df)

    infant_dict, demo_dict, alldiet_dict = combo(infant_df, demo_df, diet_df)
    data=ager(alldiet_dict, demo_dict, infant_dict)
    DATA_dict=BCPconcat(data)

    DF=total_child_df(DATA_dict, arglist)

    return(DF)
############ end BCP specific #########

#### conversions #######
def cup2oz(cup):
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
    DF_child=DF.query('age >= 12')
    DF_young=DF.query('age < 12 and age >= 8')
    DF_infant=DF.query(' age < 8')
    df={'DF_child':DF_child, 'DF_young':DF_young, 'DF_infant':DF_infant}
    return(df)

def file_org(infile, arglist, important):
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

        concat_filepath = os.path.join(arglist['SAVE'],'%s_dataset4.csv'%(ki))
        dfm4_original.to_csv(concat_filepath, index=False, sep=",", header=True)

        concat_filepath = os.path.join(arglist['SAVE'],'%s_dataset9.csv'%(ki))
        dfm9_original.to_csv(concat_filepath, index=False, sep=",", header=True)

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

        concat_filepath = os.path.join(arglist['SAVE'],'%s_BCP_datasetTOTAL.csv'%(ki))
        complete_df.to_csv(concat_filepath, index=False, sep=",", header=True)

        missing_filepath = os.path.join(arglist['SAVE'],'%s_BCP_datasetMissing.csv'%(ki))
        missing_df.to_csv(missing_filepath, index=False, sep=",", header=True)
        return_dict[ki]=complete_df
    return(return_dict)


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
            x=value[:-1]
            tmp= complete_df[x].astype('float').sum(axis=1)
            y=value[-1]
            if y == 'DOT0100':
                tmp2=complete_df[y].astype('float')/3
                complete_df[key]=tmp+tmp2
            else:
                print('NO DAIRY MISSING DOT0100, needs to be last in list')
        if key in ['hei_totproteins']:
            # these are in oz
            x=value[:-1]
            tmp= complete_df[x].astype('float').sum(axis=1)
            y=value[-1]
            if y == 'VEG0700':
                tmp2=complete_df[y].astype('float')*2 # this is normally 1/2
                complete_df[key]=tmp+tmp2
            else:
                print('NO TOTAL PROTEIN MISSING VEG0700, needs to be last in list')
        if key in ['hei_seafoodplantprot']:
            # these are in oz
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

###############################################################################
#########################pediatric components##################################
def to_fluid(key,x,num, data):
      data[key] = num*(data[x].astype('float').sum(axis=1))
      return(data[key])

def to_ounce(key, x, data):
    data[key] = data[x].astype('float').sum(axis=1)
    data[key] = cup2oz(data[key]/2)
    return(data[key])
# complete_df[key]=cow_stuff(key, value, complete_df)
def cow_stuff(key, value, data):
    x=value[:-1]
    tmp= data[x].astype('float').sum(axis=1)
    y=value[-1]
    if key == 'hei_dairy':
        if y == 'DOT0100':
            tmp2=data[y].astype('float')/3
            data[key]=cup2oz(tmp+tmp2)
        else:
            print('NO DAIRY MISSING DOT0100, needs to be last in list')
    if key == 'hei_totproteins':
        if y == 'VEG0700':
            tmp2=data[y].astype('float')*2 # this is normally 1/2
            data[key]=tmp+tmp2
        else:
            print('NO TOTAL PROTEIN MISSING VEG0700, needs to be last in list')
    if key == 'hei_seafoodplantprot':
        if y == 'VEG0700':
            tmp2=data[y].astype('float')*2
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

def make_ped_components(hei_ped_dict, complete_df, conv_dict):
    for key, value in hei_ped_dict.items():
        print(key)
        if key in ['hei_fruitjuice', 'hei_SSB','formula_foz']:
            complete_df[key]=to_fluid(key, value, conv_dict[key], complete_df)
        if key in ['hei_totveg','hei_greensbeans', 'hei_wholefruit','hei_totfruit']:
            complete_df[key]=to_ounce(key, value, complete_df)
        if key in ['cereal_oz', 'bbcereal_hcup']:
            if key == 'bbcereal_hcup':
                from_cup(key,value, conv_dict[key] , complete_df)
            else:
                x=value
                complete_df[key]= complete_df[x].astype('float').sum(axis=1)
        if key in ['hei_wholegrains','hei_refinedgrains']:
            complete_df[key] = complete_df[value].astype('float')
        if key in ['hei_dairy','hei_totproteins','hei_seafoodplantprot']:
            complete_df[key]=cow_stuff(key, value, complete_df)
        if key in ['chocolate_candies', 'candies', 'frosting', 'sugar','nondairy_treat','baked_good', 'fries']:
            complete_df[key]=grammar(key, value, conv_dict[key], complete_df)
        if key in ['sweet_sauce']:
            x=value
            complete_df[key]= T2oz(complete_df[x].astype('float').sum(axis=1))
        if key in ['syrups','Pudding','icecream']:
            from_cup(key, value, conv_dict[key], complete_df)
        if key in ['chips','other_fried']:
            x=value
            complete_df[key]= complete_df[x].astype('float').sum(axis=1)
    return(complete_df)
###############################################################################
###############################################################################

def make_hei(complete_df, make_hei_dict):
    print('START')
    print(make_hei_dict)
    for k, value in make_hei_dict.items():
        x=value
        complete_df[k] = complete_df[x].astype('float').sum(axis=1)
    return(complete_df)


def grouper(complete_df, interest, arglist):
    data_dict={}
    if arglist['CHILD'] == False:
        dailyhei0409=complete_df[complete_df.columns.intersection(interest)].groupby(['Participant ID']).mean()
        dailyhei0409['Participant ID'] = dailyhei0409.index
        data_dict['hei0409']=complete_df
        data_dict['dailyhei0409']=dailyhei0409
    else:
        data_dict['hei0409']=complete_df
    return(data_dict)


def DQI(df, inputt, output, parameter):
    if inputt in ['hei_salty','hei_sweets','hei_SSB','hei_fruitjuice','hei_refinedgrains']:
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
    elif inputt in ['hei_wholegrains','hei_milk','hei_proteins']:
        print('now calculating %s'%output)
        temp=df[inputt]
        FARMIN = parameter[0]
        FARMAX = parameter[1]
        MIN = parameter[2]
        MAX = parameter[3]
        df[output]=[5 if MIN < x <= MAX else 2.5 if MIN < x <= FARMIN or MAX < x <=FARMAX else 0 for x in temp]
    return(df)

def infant_DQI(df, inputt, output, parameter):
    #inputt, output, parameter
    MIN=0
    if inputt in ['hei_salty','hei_sweets','hei_SSB','hei_fruitjuice','hei_refinedgrains','hei_vegetables', 'hei_totfruit',
    'hei_wholegrains','hei_dairy','hei_proteins', 'hei_cereal']:
        print('now calculating %s'%output)
        temp=df[inputt]
        df[output]=[5 if x == MIN else 0 for x in temp]
    return(df)

def DQI_BF(df, output, age_group):
    if age_group == 'infant':
        df[output]=[15 if row['four_month_ratio'] == 'exclusively_breastfed' else 5 if row['four_month_ratio'] == 'exclusively_formula' else 10 for index, row in df.iterrows()]
    else:
        df[output]=[10 if row['age_stop_dropdown'] == 0 and row['breastfed'] == 1 else 0 for index, row in df.iterrows()]


# https://epi.grants.cancer.gov/hei/developing.html#2010
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

def check(dic, data, name, option, arglist):
    if arglist['CHILD'] == False:
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
    else:
        df=data
        for key,values in dic.items():
            if key in ['hei_vegetables','hei_totfruit','hei_wholegrains','hei_dairy','hei_milk','hei_proteins','hei_refinedgrains',
            'hei_fruitjuice','hei_SSB','hei_sweets','hei_salty']:
                print('Calculating score for %s'%key)
                if name != 'infant':
                    toSum=['HEIX0_BREASTFEEDING','HEIX1_VEGETABLES','HEIX2_TOTALFRUIT' , 'HEIX3_WHOLEGRAIN' , 'HEIX4_TOTALDAIRY' ,
                           'HEIX5_PROTEIN' , 'HEIX6_REFINEDGRAIN' , 'HEIX7_FRUITJUICE' , 'HEIX8_SSB', 'HEIX9_SWEETS',
                           'HEIX10_SALTY']
                    DQI(df,key, values['name'], values['parameters'])
                    df['HEI2015_TOTAL_SCORE']=df[df.columns.intersection(toSum)].sum(axis=1)
                    concat_filepath = os.path.join(arglist['SAVE'],'%s_%s_HEI.csv'%(option, name))
                    df.to_csv(concat_filepath, index=False, sep=",", header=True)
                else:
                    toSum=['HEIX0_BREASTFEEDING','HEIX1_VEGETABLES','HEIX2_TOTALFRUIT'  ,
                           'HEIX5_PROTEIN' ,  'HEIX7_FRUITJUICE' , 'HEIX8_SSB', 'HEIX9_SWEETS',
                           'HEIX10_SALTY', 'HEIX11_CEREAL']
                    infant_DQI(df,key, values['name'], values['parameters'])
                    df['HEI2015_TOTAL_SCORE']=df[df.columns.intersection(toSum)].sum(axis=1)
                    concat_filepath = os.path.join(arglist['SAVE'],'%s_%s_HEI.csv'%(option, name))
                    df.to_csv(concat_filepath, index=False, sep=",", header=True)
