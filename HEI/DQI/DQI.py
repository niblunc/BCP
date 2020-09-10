#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dietary Quality Index and NDSR functions
This expects a typical zipfile structure from an NDSR download
Created on Tue Dec  2 11:29:45 2019
Updated on Thurs Sept 3 16:16  2020
Built with python 3.6
@author: gracer
"""
def ager(date1,date2):
    # Get the age in months of each recall
    diff_time = pd.to_datetime(date1)-pd.to_datetime(date2)
    diff_time= diff_time/ np.timedelta64(1, 'M')
    return(diff_time)

def file_org(infile, arglist):
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


def cup2oz(cup):
    cup=cup.astype('float32')
    oz=cup*8
    return(oz)

def gram2oz(gram):
    gram=gram.astype('float32')
    oz=gram/28.3495
    return(oz)

def T2oz(T):
    T=T.astype('float32')
    oz=T/2
    return(oz)

def egg2oz(egg):
    egg=egg.astype('float32')
    oz=egg*1.6 #about a large egg
    return(oz)

def serv2oz(serv):
    serv=serv.astype('float32')
    return(serv)

def HEI_components(dictio, df):
    for key, value in dictio.items():
        print(key)
        if key in ['HEI_TOTALVEG','HEI_TOTALFRUIT']:
            df.loc[(df[key] >= value['parameters'][0] )& (df[key] <= value['parameters'][1]), value['name']] = 2.5
            df.loc[(df[key] > value['parameters'][1]), value['name']] = 5
            df.loc[(df[key] < value['parameters'][0]), value['name']] = 0
        if key in ['HEI_FRUITJUICE','HEI_SSB','HEI_SWEETS','HEI_SALTY']:
            df.loc[(df[key] >= value['parameters'][0] )& (df[key] <= value['parameters'][1]), value['name']] = 2.5
            df.loc[(df[key] > value['parameters'][1]), value['name']] = 0
            df.loc[(df[key] < value['parameters'][0]), value['name']] = 5
        if key in ['HEI_REFINEDGRAINS']:
            df.loc[(df[key] >= value['parameters'][0] )& (df[key] <= value['parameters'][1]), value['name']] = 1.25
            df.loc[(df[key] > value['parameters'][1]), value['name']] = 0
            df.loc[(df[key] < value['parameters'][0]), value['name']] = 2.5
        if key in ['HEI_WHOLEGRAINS','HEI_MILK']:
            print('low end %f'%value['parameters'][2])
            print('high end %f'%value['parameters'][3])
            df.loc[(df[key] >= value['parameters'][0]) & (df[key] <= value['parameters'][1]), value['name']] = 2.5
            df.loc[(df[key] > value['parameters'][3]) | (df[key] <= value['parameters'][2]) , value['name']] = 0
            df.loc[(df[key] > value['parameters'][2]) & (df[key] < value['parameters'][0]), value['name']] = 1.25
            df.loc[(df[key] > value['parameters'][1]) & (df[key] < value['parameters'][3]), value['name']] = 1.25
        if key in ['HEI_TOTALPROTEINS']:
            print('low end %f'%value['parameters'][2])
            print('high end %f'%value['parameters'][3])
            df.loc[(df[key] >= value['parameters'][0]) & (df[key] <= value['parameters'][1]), value['name']] = 5
            df.loc[(df[key] > value['parameters'][3]) | (df[key] <= value['parameters'][2]) , value['name']] = 0
            df.loc[(df[key] > value['parameters'][2]) & (df[key] < value['parameters'][0]), value['name']] = 2.5
            df.loc[(df[key] > value['parameters'][1]) & (df[key] < value['parameters'][3]), value['name']] = 2.5
    return(df)

def anyFORM(df):
    df.loc[(df['age_regular_formula'].isnull() == True), 'age_formula'] = df['age_any_formula']
    df.loc[(df['age_regular_formula'].isnull() == False), 'age_formula'] = df['age_regular_formula']

def BF_infant(df):
    df.loc[(df['breastfed'] == 'yes') & (df['age_stop'] > df['age at intake']) | (df['age_stop'].isnull() == True) & (df['age_formula'] > df['age at intake']) | df['age_formula'].isnull() == True, 'Infant'] = 'EXBF'
    df.loc[(df['breastfed'] == 'no') & (df['age_stop_formula'] > df['age at intake']), 'Infant'] = 'EXFORM'
    df.loc[(df['age_stop'] == 0) , 'Infant'] = 'EXFORM'
    df.loc[(df['breastfed'] == 'yes') & (df['age_formula'] < df['age at intake']), 'Infant'] = 'MIX'

def BF_young_child(df):
    df.loc[(df['breastfed'] == 'yes') & (df['age_stop'] >= df['age at intake']), 'child_young'] = 'BF'
    df.loc[(df['age_stop'] < df['age at intake']) | (df['age_stop'].isnull() == True), 'child_young'] = 'noBF'

def BF_HEI(df, age):
    if age == 'infant':
        df.loc[(df['Infant'] == 'EXBF'), 'HEIX0_BF'] = 15
        df.loc[(df['Infant'] == 'MIX'), 'HEIX0_BF'] = 10
        df.loc[(df['Infant'] == 'EXFORM'), 'HEIX0_BF'] = 5
    else:
        df.loc[(df['child_young'] == 'noBF'), 'HEIX0_BF'] = 0
        df.loc[(df['child_young'] == 'BF'), 'HEIX0_BF'] = 10
