#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
from pandas import DataFrame
from Bio import Entrez
# from Bio.Entrez import efetch
import csv   
import os


# In[69]:


def NIH_Search_Drug(search_term_drug,search_term_target):
    # global J_Drug_pmid_UQ
    # global J_Target_pmid_UQ
    # global J_resultUQ_APY_COST
    # global J_resultUQ_FULL
    # global J_Target_hold
    # global J_Drug_hold
###################### Ref Table Load ##################    
    time_short = pd.read_csv('function_data/reporter_pub_time_cut_6_9_21.csv',dtype=str)
    core_set=pd.read_csv('function_data/Reporter_project_cut_6_10.csv')
    pub_key = pd.read_csv('function_data/reporter_pub_key_6_9_21.csv',dtype=str)
    Inflation_key_V2018 = pd.read_csv('function_data/inf2018_key.csv')
    IC_Key = pd.read_csv('function_data/institute_key.csv',dtype=str)
    
###################### Inflation ##################
    core_set = core_set.loc[core_set['FY'] >=1999]
    core_set_2018=pd.merge(core_set,Inflation_key_V2018, how='outer')
    core_set_2018['inf_2018_costs']=core_set_2018['TOTAL_COST']*core_set_2018['inf_2018']
    core_set_2018.drop('TOTAL_COST', inplace=True, axis=1)
    core_set_2018.drop('inf_2018', inplace=True, axis=1)
    core_set_2018.rename(columns = {"inf_2018_costs": "TOTAL_COST"}, 
              inplace = True)
    core_set=core_set_2018
    core_set_2018=1
    
###################### Drug search ##############################
#     Entrez.email = "ezhou@bentley.edu"     
#     handle = Entrez.esearch(db="pubmed", term=search_term_drug, retmax="1500000")
#     record = Entrez.read(handle)
#     entz=record["IdList"]
#     search_output = DataFrame(entz,columns=['PMID'])
#     search_output['search_term']=search_term_drug
#     search_output['search_type']='Drug'
#     search_output.to_csv(r'new_data/2search_output_drug.csv', index = None, header=True) 
# ###################### Target search ############################    
#     Entrez.email = "ezhou@bentley.edu"     
#     handle = Entrez.esearch(db="pubmed", term=search_term_target, retmax="1500000")
#     record = Entrez.read(handle)
#     entz=record["IdList"]
#     search_output = DataFrame(entz,columns=['PMID'])
#     search_output['search_term']=search_term_target
#     search_output['search_type']='target'
#     search_output.to_csv(r'new_data/2search_output_target.csv', index = None, header=True) 
    
###################### Drug NIH Funding ########################################################################### 

###################### PMID ##################    
    read_pmid = pd.read_csv('new_data/search_output_drug.csv')
    read_pmid_pmid_UQ=read_pmid[['PMID']]
    read_pmid_pmid_UQ=read_pmid_pmid_UQ.drop_duplicates()
    read_pmid_pmid_UQ.to_csv('new_data/pmid_drug.csv',index=None)
    J_Drug_pmid_UQ = read_pmid_pmid_UQ
    os.remove("new_data/search_output_drug.csv")
###################### NIH_Funding_filter ##################     
    NIH_PMID=pd.merge(read_pmid_pmid_UQ.astype(str),pub_key.astype(str), how='inner')
    NIH_PMID=NIH_PMID.drop_duplicates()
    NIH_PMID_time=pd.merge(NIH_PMID.astype(str),time_short.astype(str), how='inner')
    NIH_PMID_time_core=pd.merge(core_set,NIH_PMID_time, how='inner')
    NIH_PMID_time_core=NIH_PMID_time_core.fillna(0)
    NIH_PMID_time_core=NIH_PMID_time_core.drop_duplicates()
    
###################### Pubyear_fixer    
    Type_Fix_Drug_pubyear=NIH_PMID_time_core[['PMID','PUB_YEAR']]
    Type_Fix_Drug_pubyear=Type_Fix_Drug_pubyear.drop_duplicates()
    PB_d = Type_Fix_Drug_pubyear.groupby('PMID')['PUB_YEAR'].max().reset_index()
    PB_d.columns = ['PMID', 'PUB_YEAR']
    NIH_PMID_time_core.drop('PUB_YEAR', inplace=True, axis=1)
    NIH_PMID_time_core=NIH_PMID_time_core.drop_duplicates()
    NIH_PMID_time_core=NIH_PMID_time_core.merge(PB_d, how='inner')
    
    nih_test_start=NIH_PMID_time_core
    nih_test_Last=NIH_PMID_time_core
    nih_test1=NIH_PMID_time_core
    nih_test_start=NIH_PMID_time_core
    nih_test_Last=NIH_PMID_time_core
    nih_test1=NIH_PMID_time_core
    
###################### NIH_Funding_APY ##################  
    nih_test_start2 = nih_test_start[nih_test_start.groupby('PROJECT_NUMBER')['FY'].transform('min') == nih_test_start['FY']]
    nih_test_start2 = nih_test_start2[['PROJECT_NUMBER','FY']]
    nih_test_start2=nih_test_start2.drop_duplicates()
    nih_test_start2.rename(columns = {"FY": "FY_Start"}, 
              inplace = True)
    nih_test_Last2 = nih_test_Last[nih_test_Last.groupby('PROJECT_NUMBER')['FY'].transform('max') == nih_test_start['FY']]
    nih_test_Last2 = nih_test_Last2[['PROJECT_NUMBER','FY']]
    nih_test_Last2=nih_test_Last2.drop_duplicates()
    nih_test_Last2.rename(columns = {"FY": "FY_Last"}, 
              inplace = True)

    nih_target_home = pd.merge(nih_test1, nih_test_start2,  how='left', left_on=['PROJECT_NUMBER'], right_on = ['PROJECT_NUMBER'])
    nih_target_home=nih_target_home.drop_duplicates()
    nih_target_home = pd.merge(nih_target_home, nih_test_Last2,  how='left', left_on=['PROJECT_NUMBER'], right_on = ['PROJECT_NUMBER'])
    nih_target_home=nih_target_home.drop_duplicates()
    
    nih_target_home_sl=nih_target_home[['PROJECT_NUMBER','FY_Start','FY_Last','PMID','PUB_YEAR','TOTAL_COST','FY']]
    nih_target_home_sl['FY_Last'] = nih_target_home_sl['FY_Last'].astype(int)
    nih_target_home_sl['FY_Start'] = nih_target_home_sl['FY_Start'].astype(int)
    nih_target_home_sl['PUB_YEAR'] = nih_target_home_sl['PUB_YEAR'].astype(int)
    nih_target_home_sl['Pub_V_Start']=nih_target_home_sl['PUB_YEAR'] - nih_target_home_sl['FY_Start']
    nih_target_home_sl['Pub_V_Last']=nih_target_home_sl['PUB_YEAR'] - nih_target_home_sl['FY_Last']
    nih_target_home_sl = nih_target_home_sl.loc[nih_target_home_sl['Pub_V_Last'] <=4]
    nih_target_home_sl = nih_target_home_sl.loc[nih_target_home_sl['Pub_V_Start'] >=0]
    nih_target_home_sl.drop('Pub_V_Last', inplace=True, axis=1)
    nih_target_home_sl.drop('Pub_V_Start', inplace=True, axis=1)
    
    APY_Cost_index=nih_target_home_sl[['PROJECT_NUMBER','TOTAL_COST','FY']]
    APY_Cost_index=APY_Cost_index.drop_duplicates()
    APY_Cost_index['TOTAL_COST'] = APY_Cost_index['TOTAL_COST'].astype(int)
    g = APY_Cost_index.groupby(['PROJECT_NUMBER','FY'])['TOTAL_COST'].sum()
    j = APY_Cost_index.groupby(['PROJECT_NUMBER','FY']).size().to_frame('count')
    NIH_base=pd.merge(g, j, left_index=True, right_index=True).reset_index()
    NIH_base.rename(columns = {"FY": "APY"}, 
              inplace = True)
    
    nih_test2=nih_target_home_sl
    nih_test2['PUB_YEAR'] = nih_test2['PUB_YEAR'].astype(int)
    nih_test2['FY_Last'] = nih_test2['FY_Last'].astype(int)
    nih_test2['APY'] = nih_test2[['PUB_YEAR','FY_Last']].min(axis=1)
    nih_test2['APY'] = nih_test2['APY'].astype(str)
    nih_test2['PROJECT_NUMBER'] = nih_test2['PROJECT_NUMBER'].astype(str)
    nih_test2["ACTUAL_PROJECT_YEAR"] = nih_test2["APY"] + nih_test2["PROJECT_NUMBER"]
    nih_test2.drop('TOTAL_COST', inplace=True, axis=1)
    nih_test2.drop('FY', inplace=True, axis=1)

    NIH_base['APY'] = NIH_base['APY'].astype(str)
    nih_test2=pd.merge(nih_test2,NIH_base, how='inner')
    nih_test2=nih_test2.drop_duplicates()  
    
    nih_test2.rename(columns = {"count": "Project_Count"}, 
          inplace = True)
    nih_test2.rename(columns = {"TOTAL_COST": "APY_COST_inf2018"}, 
              inplace = True)
    nih_test2=nih_test2.assign(Activity_Code=nih_test2['PROJECT_NUMBER'].str[:3])
    nih_test2=nih_test2.assign(Institute_Code=nih_test2['PROJECT_NUMBER'].str[3:5])
    nih_test2=pd.merge(nih_test2,IC_Key, how='inner')
    nih_test2=nih_test2.drop_duplicates()
    nih_test2['Search__ID']=search_term_drug
    nih_test2['Search_Type']='Drug'

    nih_test2=nih_test2[['Search__ID','Search_Type','PMID','PUB_YEAR','PROJECT_NUMBER','FY_Start','FY_Last','APY','ACTUAL_PROJECT_YEAR','APY_COST_inf2018','Activity_Code','Institute_Code','Acronym_institute_name','full_institute_name','Compressed Names','Project_Count']]
    nih_test2.to_csv('new_data/Drug_hold.csv',index=None)
    J_Drug_hold=nih_test2
    
    
    
    
    
###################### Target NIH Funding ########################################################################### 
    
###################### PMID ##################    
    read_pmid = pd.read_csv('new_data/search_output_target.csv')
    read_pmid_pmid_UQ=read_pmid[['PMID']]
    read_pmid_pmid_UQ=read_pmid_pmid_UQ.drop_duplicates()
    read_pmid_pmid_UQ.to_csv('new_data/pmid_target.csv',index=None)
    J_Target_pmid_UQ=read_pmid_pmid_UQ
    os.remove("new_data/search_output_target.csv")
###################### NIH_Funding_filter ##################     
    NIH_PMID=pd.merge(read_pmid_pmid_UQ.astype(str),pub_key.astype(str), how='inner')
    NIH_PMID=NIH_PMID.drop_duplicates()
    NIH_PMID_time=pd.merge(NIH_PMID.astype(str),time_short.astype(str), how='inner')
    NIH_PMID_time_core=pd.merge(core_set,NIH_PMID_time, how='inner')
    NIH_PMID_time_core=NIH_PMID_time_core.fillna(0)
    NIH_PMID_time_core=NIH_PMID_time_core.drop_duplicates()
    
###################### Pubyear_fixer    
    Type_Fix_Target_pubyear=NIH_PMID_time_core[['PMID','PUB_YEAR']]
    Type_Fix_Target_pubyear=Type_Fix_Target_pubyear.drop_duplicates()
    PB_t = Type_Fix_Target_pubyear.groupby('PMID')['PUB_YEAR'].max().reset_index()
    PB_t.columns = ['PMID', 'PUB_YEAR']
    NIH_PMID_time_core.drop('PUB_YEAR', inplace=True, axis=1)
    NIH_PMID_time_core=NIH_PMID_time_core.drop_duplicates()
    NIH_PMID_time_core=NIH_PMID_time_core.merge(PB_t, how='inner')
    
    nih_test_start=NIH_PMID_time_core
    nih_test_Last=NIH_PMID_time_core
    nih_test1=NIH_PMID_time_core
    
###################### NIH_Funding_APY ##################  
    nih_test_start2 = nih_test_start[nih_test_start.groupby('PROJECT_NUMBER')['FY'].transform('min') == nih_test_start['FY']]
    nih_test_start2 = nih_test_start2[['PROJECT_NUMBER','FY']]
    nih_test_start2=nih_test_start2.drop_duplicates()
    nih_test_start2.rename(columns = {"FY": "FY_Start"}, 
              inplace = True)
    nih_test_Last2 = nih_test_Last[nih_test_Last.groupby('PROJECT_NUMBER')['FY'].transform('max') == nih_test_start['FY']]
    nih_test_Last2 = nih_test_Last2[['PROJECT_NUMBER','FY']]
    nih_test_Last2=nih_test_Last2.drop_duplicates()
    nih_test_Last2.rename(columns = {"FY": "FY_Last"}, 
              inplace = True)

    nih_target_home = pd.merge(nih_test1, nih_test_start2,  how='left', left_on=['PROJECT_NUMBER'], right_on = ['PROJECT_NUMBER'])
    nih_target_home=nih_target_home.drop_duplicates()
    nih_target_home = pd.merge(nih_target_home, nih_test_Last2,  how='left', left_on=['PROJECT_NUMBER'], right_on = ['PROJECT_NUMBER'])
    nih_target_home=nih_target_home.drop_duplicates()
    
    nih_target_home_sl=nih_target_home[['PROJECT_NUMBER','FY_Start','FY_Last','PMID','PUB_YEAR','TOTAL_COST','FY']]
    nih_target_home_sl['FY_Last'] = nih_target_home_sl['FY_Last'].astype(int)
    nih_target_home_sl['FY_Start'] = nih_target_home_sl['FY_Start'].astype(int)
    nih_target_home_sl['PUB_YEAR'] = nih_target_home_sl['PUB_YEAR'].astype(int)
    nih_target_home_sl['Pub_V_Start']=nih_target_home_sl['PUB_YEAR'] - nih_target_home_sl['FY_Start']
    nih_target_home_sl['Pub_V_Last']=nih_target_home_sl['PUB_YEAR'] - nih_target_home_sl['FY_Last']
    nih_target_home_sl = nih_target_home_sl.loc[nih_target_home_sl['Pub_V_Last'] <=4]
    nih_target_home_sl = nih_target_home_sl.loc[nih_target_home_sl['Pub_V_Start'] >=0]
    nih_target_home_sl.drop('Pub_V_Last', inplace=True, axis=1)
    nih_target_home_sl.drop('Pub_V_Start', inplace=True, axis=1)
    
    APY_Cost_index=nih_target_home_sl[['PROJECT_NUMBER','TOTAL_COST','FY']]
    APY_Cost_index=APY_Cost_index.drop_duplicates()
    APY_Cost_index['TOTAL_COST'] = APY_Cost_index['TOTAL_COST'].astype(int)
    g = APY_Cost_index.groupby(['PROJECT_NUMBER','FY'])['TOTAL_COST'].sum()
    j = APY_Cost_index.groupby(['PROJECT_NUMBER','FY']).size().to_frame('count')
    NIH_base=pd.merge(g, j, left_index=True, right_index=True).reset_index()
    NIH_base.rename(columns = {"FY": "APY"}, 
              inplace = True)
    
    nih_test2=nih_target_home_sl
    nih_test2['PUB_YEAR'] = nih_test2['PUB_YEAR'].astype(int)
    nih_test2['FY_Last'] = nih_test2['FY_Last'].astype(int)
    nih_test2['APY'] = nih_test2[['PUB_YEAR','FY_Last']].min(axis=1)
    nih_test2['APY'] = nih_test2['APY'].astype(str)
    nih_test2['PROJECT_NUMBER'] = nih_test2['PROJECT_NUMBER'].astype(str)
    nih_test2["ACTUAL_PROJECT_YEAR"] = nih_test2["APY"] + nih_test2["PROJECT_NUMBER"]
    nih_test2.drop('TOTAL_COST', inplace=True, axis=1)
    nih_test2.drop('FY', inplace=True, axis=1)

    NIH_base['APY'] = NIH_base['APY'].astype(str)
    nih_test2=pd.merge(nih_test2,NIH_base, how='inner')
    nih_test2=nih_test2.drop_duplicates()  
    
    nih_test2.rename(columns = {"count": "Project_Count"}, 
          inplace = True)
    nih_test2.rename(columns = {"TOTAL_COST": "APY_COST_inf2018"}, 
              inplace = True)
    nih_test2=nih_test2.assign(Activity_Code=nih_test2['PROJECT_NUMBER'].str[:3])
    nih_test2=nih_test2.assign(Institute_Code=nih_test2['PROJECT_NUMBER'].str[3:5])
    nih_test2=pd.merge(nih_test2,IC_Key, how='inner')
    nih_test2=nih_test2.drop_duplicates()
    nih_test2['Search__ID']=search_term_target
    nih_test2['Search_Type']='target'

    nih_test2=nih_test2[['Search__ID','Search_Type','PMID','PUB_YEAR','PROJECT_NUMBER','FY_Start','FY_Last','APY','ACTUAL_PROJECT_YEAR','APY_COST_inf2018','Activity_Code','Institute_Code','Acronym_institute_name','full_institute_name','Compressed Names','Project_Count']]
    nih_test2.to_csv('new_data/Target_hold.csv',index=None)
    J_Target_hold=nih_test2
    
###########################Drug vs Target Analysis########################################################

#################### Search Terms ############################
    Drug_hold=pd.read_csv('new_data/Drug_hold.csv')
    Target_hold=pd.read_csv('new_data/Target_hold.csv')
    
    Drug_hold_full=Drug_hold
    Target_hold_full=Target_hold
    Drug_hold=Drug_hold[['ACTUAL_PROJECT_YEAR']]
    Target_hold=Target_hold[['ACTUAL_PROJECT_YEAR']]
    Target_hold['search']='Target'
    Drug_hold['search2']='Drug'
    Drug_UQ_FULL=pd.merge(Drug_hold,Target_hold, how='outer')
    Drug_UQ_FULL=Drug_UQ_FULL.fillna('only')
    Drug_UQ_FULL['search_term']=Drug_UQ_FULL['search2']+Drug_UQ_FULL['search']
    Drug_UQ_FULL_join=Drug_UQ_FULL[['ACTUAL_PROJECT_YEAR','search_term']]
    Drug_UQ_FULL_join=Drug_UQ_FULL_join.drop_duplicates()
    result = Drug_hold_full.append(Target_hold_full)
    resultUQ_FULL=pd.merge(result,Drug_UQ_FULL_join, how='outer')
    resultUQ_FULL=resultUQ_FULL.drop_duplicates()
    resultUQ_FULL['search_term'] = resultUQ_FULL['search_term'].replace({'DrugTarget':'Drug', 'Drugonly':'Drug'})
    resultUQ_FULL['search_term'] = resultUQ_FULL['search_term'].replace({'onlyTarget':'Target_Only', 'Drugonly':'Drug'})

############# Project/Grant ID ##############################
    Grant_code=pd.read_csv('function_data/Grant_Types.csv')
    Grant_code=Grant_code.assign(Activity_Code=Grant_code['Activity_Code'].str[:3])
    resultUQ_GT=pd.merge(resultUQ_FULL,Grant_code,how='outer')
    resultUQ_GT = resultUQ_GT.dropna(axis=0, subset=['Search_Type'])
    resultUQ_GT["Grant_Type_Name"][resultUQ_GT['Activity_Code'].str.contains("Z")] = "Intramural Programs"
    resultUQ_GT=resultUQ_GT.fillna('Others')
    resultUQ_GT=resultUQ_GT.drop_duplicates()
    resultUQ_FULL=resultUQ_GT
    
    
############# Cost per APY ##################################    
    resultUQ_FULL=resultUQ_FULL[['Search__ID','Search_Type','search_term','PMID','PUB_YEAR','PROJECT_NUMBER','FY_Start','FY_Last','APY','ACTUAL_PROJECT_YEAR','APY_COST_inf2018','Activity_Code','Institute_Code','Acronym_institute_name','full_institute_name','Compressed Names','Project_Count','Grant_Type_Name']]
    resultUQ_FULL.rename(columns = {"Search_Type": "Source_Search_Type"}, 
          inplace = True)
    resultUQ_FULL.rename(columns = {"search_term": "Search_Type"}, 
          inplace = True)

    resultUQ_FULL.to_csv('new_data/resultUQ_FULL.csv',index=None)
    resultUQ_APY_COST=resultUQ_FULL[['APY','ACTUAL_PROJECT_YEAR','APY_COST_inf2018','Search_Type']]
    resultUQ_APY_COST=resultUQ_APY_COST.drop_duplicates()
    resultUQ_APY_COST.to_csv('new_data/resultUQ_APY_COST.csv',index=None)
    J_resultUQ_APY_COST=resultUQ_APY_COST
    J_resultUQ_FULL=resultUQ_FULL


    
########### Debug Cleanup  ####################    
    core_set=1
    time = 1
    key = 1
    NIH_PMID=1
    time_short=1
    
    return J_resultUQ_FULL, J_Target_hold, J_Drug_hold, J_Target_pmid_UQ, J_Drug_pmid_UQ, J_resultUQ_APY_COST
    
    # df = pd.read_csv('new_data/resultUQ_FULL.csv' )
    # df_t = pd.read_csv('new_data/Target_hold.csv' )
    # df_d = pd.read_csv('new_data/Drug_hold.csv' )
    # df_t_pmid = pd.read_csv('new_data/pmid_target.csv' )    
    # df_d_pmid = pd.read_csv('new_data/pmid_drug.csv' )


    # return df, df_t, df_d, df_t_pmid, df_d_pmid

