#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dietary Quality Index and NDSR functions
This expects a typical zipfile structure from an NDSR download
Created on Tue Dec  2 11:29:45 2019
Updated on Wed July 15 12:50   2020
Built with python 3.6
@author: gracer
"""



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

def file_reader(basepath, arglist['XTRA'], file_dict, demo_interest):
    data_dict={"set_04":{},"set_09":{},"demo":{}}
df_demo=pd.read_csv(os.path.join(basepath,arglist['XTRA']), sep=",")

df_demo['Participant ID'] = df_demo['Participant ID'].astype('int32')
df_demo['Identifiers_visit']=df_demo['Identifiers_visit'].astype('int32')
df_demo['child_feeding_practice-breastfed']=df_demo['child_feeding_practice-breastfed'].astype('category')

data_dict["demo"]= df_demo[demo_interest]

for key, value in file_dict.items():
    print(key)
    for k,v, in value.items():
        print(k)
        temp_list = []
        for file in v["files"]:
            print(file)
            temp_df =  pd.read_csv(file, sep="\t", encoding='latin1')
            if key == 'set_09':
                temp_df=temp_df.drop([0]) #drops extra row
            for val in temp_df["Participant ID"]:
                _id = str(val).lstrip("0").split("_")[0]
                temp_df.replace(val, _id, inplace=True)
            temp_list.append(temp_df)
        dfm_original = pd.concat(temp_list, ignore_index=True)
        print("Final dataframe size: ", dfm_original.shape)
        dfm_original = dfm_original.sort_values(by="Participant ID")

        del_cols=set(dfm_original.columns) - set(important)
        dfm_original.drop(del_cols, axis=1, inplace=True)
        for col in dfm_original:
            if dfm_original[col].dtype == np.object_:
                dfm_original[col] = (dfm_original[col].replace(',','.', regex=True))

        concat_filepath = os.path.join(arglist['SAVE'],'%s_dataset_%s.csv'%(k,key))

        dfm_original['Participant ID'] = dfm_original['Participant ID'].astype('float').astype('int32')
        _sub=pd.merge(data_dict['demo'][['Participant ID','DoB']], dfm_original[['Participant ID','Date of Intake']],on='Participant ID')
        _sub['age at intake']=ager(_sub['Date of Intake'], _sub['DoB'])
        dfm_original=pd.merge(dfm_original,_sub, on=['Participant ID','Date of Intake'])
        dfm_original = dfm_original.groupby(['Participant ID', 'Date of Intake'])
#         dfm_original.to_csv(concat_filepath, index=False, sep=",", header=True)

        data_dict[key]= dfm_original


            return(data_dict)


def ager(date1,date2):
    # Get the age in months of each recall
    diff_time = pd.to_datetime(date1)-pd.to_datetime(date2)
    diff_time= diff_time/ np.timedelta64(1, 'M')
    return(diff_time)
