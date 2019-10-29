# file_org
A function that is reading in all the 04 and 09 dataset and creating a single dataset called _datasetTOTAL
The other functions in HEI expect this structure
OUTPUT = dictionary of the options (ex. mom and child or just mom)
# make_components
A function that take the hei_dict (what elements are in each hei component) and the

# make_ped_components
A function that is gathering the NDSR output into the HEI or DQI components
OUTPUT = dataframe

# make_hei
This is specific for the pediatric because they have non-standard components, need to create protein, sweets, vegetables, and salty groups.
OUTPUT - dataframe

# grouper
makes both the daily and overall all hei scores. For the pediatric only want to use the daily 
