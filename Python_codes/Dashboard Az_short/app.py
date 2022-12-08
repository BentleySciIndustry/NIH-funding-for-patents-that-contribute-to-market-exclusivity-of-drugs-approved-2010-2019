#!/usr/bin/env python
# coding: utf-8

# In[1]:


import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

import pandas as pd
from pandas import DataFrame
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px

import NIH_Funding_TEST3J
from NIH_Funding_TEST3J import NIH_Search_Drug
import json
from datetime import date
from dash_extensions.enrich import Output, DashProxy, Input, MultiplexerTransform

from Bio import Entrez
import csv   
import os

# import NIH_PMID_ID_DRUG
# from NIH_PMID_ID_DRUG import pub_key_entz_drug

# import NIH_PMID_ID_TARGET
# from NIH_PMID_ID_TARGET import pub_key_entz_target


# In[2]:


################## Last Update:: xiaoshuang last 10/8/21 : ED 1/28/22 ###############################################################################


# In[3]:


def pub_key_entz_drug(search_term_drug):
    Entrez.email = "ezhou@bentley.edu"     
    handle = Entrez.esearch(db="pubmed", term=search_term_drug, retmax="1500000")
    record = Entrez.read(handle)
    entz=record["IdList"]
    search_output = DataFrame(entz,columns=['PMID'])
    search_output['search_term']=search_term_drug
    search_output['search_type']='drug'
    search_output.to_csv(r'new_data/search_output_drug.csv', index = None, header=True) 


# In[4]:


def pub_key_entz_target(search_term_target):
    Entrez.email = "ezhou@bentley.edu"     
    handle = Entrez.esearch(db="pubmed", term=search_term_target, retmax="1500000")
    record = Entrez.read(handle)
    entz=record["IdList"]
    search_output = DataFrame(entz,columns=['PMID'])
    search_output['search_term']=search_term_target
    search_output['search_type']='target'
    search_output.to_csv(r'new_data/search_output_target.csv', index = None, header=True) 


# In[5]:


df = pd.read_csv('data/resultUQ_FULL.csv')
df


# In[6]:


df_cost=pd.read_csv('data/resultUQ_APY_COST.csv' )
df_cost


# In[7]:


df_d_cost = df_cost[df_cost.Search_Type == 'Drug']
df_d_cost


# In[8]:


df_t_cost = df_cost[df_cost.Search_Type == 'Target_Only']
df_t_cost


# In[9]:


df_d = df[df.Search_Type == 'Drug']
df_d


# In[10]:


df_t = df[df.Search_Type == 'Target_Only']
df_t


# In[11]:


df_d_pmid = pd.read_csv('data/pmid_drug.csv' )
df_d_pmid


# In[12]:


df_t_pmid = pd.read_csv('data/pmid_target.csv' )
df_t_pmid


# In[13]:


Drug_hold = pd.read_csv('data/Drug_hold.csv' )
Drug_hold=Drug_hold[['PMID']]

Target_hold = pd.read_csv('data/Target_hold.csv' )
Target_hold=Target_hold[['PMID']]


# In[14]:


def unique_pmid(df):
    total = df.PMID.nunique()
#     total = '{:,}'.format(total)
    return total


# In[15]:


def unique_project(df):
    total = df.PROJECT_NUMBER.nunique()
#     total = '{:,}'.format(total)
    return total


# In[16]:


def apy(df):
    total = df.ACTUAL_PROJECT_YEAR.nunique()
#     total = '{:,}'.format(total)
    return total 


# In[17]:


def total_funding(df):
    total = df.drop_duplicates('ACTUAL_PROJECT_YEAR').APY_COST_inf2018.sum()
#     total = '${:,}'.format(total)
    return total


# In[18]:


def pmid_count_year_plot(df):
    new_df = df[df.PROJECT_NUMBER.notnull()].groupby('PUB_YEAR').PMID.nunique().reset_index()
    return new_df  


# In[19]:


def funding_yearly_plot(df):
    new_df = df.drop_duplicates('ACTUAL_PROJECT_YEAR').groupby('APY')['APY_COST_inf2018'].sum().reset_index()
    return new_df    


# In[20]:


def APY_yearly_plot(df):
    new_df = df.groupby('APY')['ACTUAL_PROJECT_YEAR'].nunique().reset_index()
    return new_df 


# In[21]:


def top_10_fund_ins(df):
    top10_cost_ins_total = df.drop_duplicates('ACTUAL_PROJECT_YEAR').groupby('full_institute_name')['APY_COST_inf2018'].sum().reset_index().sort_values(by = 'APY_COST_inf2018',ascending = False)
    return top10_cost_ins_total.head(10)


# In[22]:


def top_10_fund_ins_target_drug(df):
    top10_cost_ins_total_target_drug = df.drop_duplicates('ACTUAL_PROJECT_YEAR').groupby(['full_institute_name', 'Search_Type'])['APY_COST_inf2018'].sum().reset_index()
    in_top10 = top10_cost_ins_total_target_drug[top10_cost_ins_total_target_drug.full_institute_name.isin(top_10_fund_ins(df)['full_institute_name'])]

    top10_list = in_top10.set_index(['full_institute_name', 'Search_Type']).unstack(level=-1).reset_index()
    top10_list.columns = top10_list.columns.map('_'.join)
    top10_list = top10_list.fillna(0)
    top10_list['APY_COST_inf2018_Total'] = top10_list['APY_COST_inf2018_Drug']+top10_list['APY_COST_inf2018_Target_Only']
    top10_list = top10_list.sort_values('APY_COST_inf2018_Total', ascending = False)

    return top10_list.head(10)


# In[23]:


top_10_fund_ins(df)


# In[24]:


top_10_fund_ins_target_drug(df)


# In[25]:


def top_10_productive_ins(df):
    top10_productive_ins_total = df.groupby('full_institute_name')['PMID'].nunique().reset_index().sort_values(by = 'PMID',ascending = False)
    return top10_productive_ins_total.head(10)


# In[26]:


def top_10_productive_ins_target_drug(df,Drug_hold,Target_hold): # prepare data for tab2 barplot 2
    
    SET = pd.merge(Drug_hold, Target_hold, how='outer', indicator=True)

    Target = SET.loc[SET._merge == 'right_only', ['PMID']]
    Target=Target[['PMID']]
    Target = Target.drop_duplicates()


    Drug1 = SET.loc[SET._merge == 'left_only', ['PMID']]
    Drug1=Drug1[['PMID']]
    Drug2 = SET.loc[SET._merge == 'both', ['PMID']]
    Drug2=Drug2[['PMID']]
    Drug_total = pd.merge(Drug1, Drug2, how='outer')
    Drug_total = Drug_total.drop_duplicates()

    target = df[['PMID', 'full_institute_name']].drop_duplicates().merge(Target, how = 'inner', on='PMID')
    target['type'] = 'Target'
    drug = df[['PMID', 'full_institute_name']].drop_duplicates().merge(Drug_total, how = 'inner', on='PMID')
    drug['type'] = 'Drug'
    total_df = target.append(drug).groupby(['full_institute_name', 'type'])['PMID'].nunique().reset_index()

    total_df = total_df.pivot(index="full_institute_name", columns="type", values="PMID").reset_index().fillna(0)
    total_df['Total'] = total_df.Drug +total_df.Target
    total_df = total_df.sort_values('Total', ascending = False)

    return total_df.head(10)


# In[27]:


top_10_productive_ins_target_drug(df,Drug_hold,Target_hold)


# In[28]:


top_10_productive_ins(df)


# In[29]:


def top_10_fund_proj(df):
    top10_cost_proj_total = df.drop_duplicates('ACTUAL_PROJECT_YEAR').groupby('Grant_Type_Name')['APY_COST_inf2018'].sum().reset_index().sort_values(by = 'APY_COST_inf2018',ascending = False)
    return top10_cost_proj_total.head(10)


# In[30]:


df.drop_duplicates('ACTUAL_PROJECT_YEAR').groupby(['Grant_Type_Name', 'Search_Type'])['APY_COST_inf2018'].sum().reset_index().pivot(index="Grant_Type_Name", columns="Search_Type", values="APY_COST_inf2018").reset_index().fillna(0)


# In[31]:


def top_10_fund_proj_target_drug(df):
    top10_cost_proj_total_target_drug = df.drop_duplicates('ACTUAL_PROJECT_YEAR').groupby(['Grant_Type_Name', 'Search_Type'])['APY_COST_inf2018'].sum().reset_index()
    top10_cost_proj_total_target_drug =top10_cost_proj_total_target_drug.pivot(index="Grant_Type_Name", columns="Search_Type", values="APY_COST_inf2018").reset_index().fillna(0)
    top10_cost_proj_total_target_drug['Total'] = top10_cost_proj_total_target_drug['Drug']+top10_cost_proj_total_target_drug['Target_Only']
    top10_cost_proj_total_target_drug = top10_cost_proj_total_target_drug.sort_values('Total', ascending = False)
    top10_cost_proj_total_target_drug

    return top10_cost_proj_total_target_drug.head(10)


# In[32]:


top_10_fund_proj(df)


# In[33]:


top_10_fund_proj_target_drug(df)


# In[34]:


def prepare_data_block2_target(Target_hold, Drug_hold):
    SET = pd.merge(Drug_hold, Target_hold, how='outer', indicator=True)

    Target = SET.loc[SET._merge == 'right_only', ['PMID']]
    Target=Target[['PMID']]
    Target = Target.drop_duplicates()


    Drug1 = SET.loc[SET._merge == 'left_only', ['PMID']]
    Drug1=Drug1[['PMID']]
    Drug2 = SET.loc[SET._merge == 'both', ['PMID']]
    Drug2=Drug2[['PMID']]
    Drug_total = pd.merge(Drug1, Drug2, how='outer')
    Drug_total = Drug_total.drop_duplicates()
    
    return Target


# In[35]:


def prepare_data_block2_drug(Target_hold, Drug_hold):
    SET = pd.merge(Drug_hold, Target_hold, how='outer', indicator=True)

    Target = SET.loc[SET._merge == 'right_only', ['PMID']]
    Target=Target[['PMID']]
    Target = Target.drop_duplicates()


    Drug1 = SET.loc[SET._merge == 'left_only', ['PMID']]
    Drug1=Drug1[['PMID']]
    Drug2 = SET.loc[SET._merge == 'both', ['PMID']]
    Drug2=Drug2[['PMID']]
    Drug_total = pd.merge(Drug1, Drug2, how='outer')
    Drug_total = Drug_total.drop_duplicates()
    
    return Drug_total


# In[36]:


# def prepare_data_tab2barpmid(df,Target_hold, Drug_hold):
#     target = df[['PMID', 'full_institute_name']].drop_duplicates().merge(prepare_data_block2_target(Target_hold, Drug_hold), how = 'inner', on='PMID')
#     target['type'] = 'Target'
#     drug = df[['PMID', 'full_institute_name']].drop_duplicates().merge(prepare_data_block2_drug(Target_hold, Drug_hold), how = 'inner', on='PMID')
#     drug['type'] = 'Drug'
#     total_df = target.append(drug).groupby(['full_institute_name', 'Search_Type'])['PMID'].nunique().reset_index()
    
#     in_top10 = total_df.full_institute_name.isin(top_10_productive_ins(df)['full_institute_name'])
#     top10_list = in_top10.set_index(['full_institute_name', 'Search_Type']).unstack(level=-1).reset_index()
#     top10_list.columns = top10_list.columns.map('_'.join)
#     top10_list = top10_list.fillna(0)
#     top10_list['PMID_Total'] = top10_list['PMID_Drug']+top10_list['PMID_Target_Only']
#     top10_list.sort_values('PMID_Total')
#     return top10_list.sort_values('PMID_Total')
    
#     return total_df


# In[37]:


# target = df[['PMID', 'full_institute_name']].drop_duplicates().merge(prepare_data_block2_target(Target_hold, Drug_hold), how = 'inner', on='PMID')
# target['type'] = 'Target'
# drug = df[['PMID', 'full_institute_name']].drop_duplicates().merge(prepare_data_block2_drug(Target_hold, Drug_hold), how = 'inner', on='PMID')
# drug['type'] = 'Drug'
# target.append(drug)


# In[38]:


def top_10_productive_proj(df):
    top10_productive_proj_total = df.groupby('Grant_Type_Name')['PMID'].nunique().reset_index().sort_values(by = 'PMID',ascending = False)
    return top10_productive_proj_total.head(10)


# In[39]:


def top_10_productive_proj_target_drug(df,Drug_hold,Target_hold): # prepare data for tab3 barplot 2
    
    SET = pd.merge(Drug_hold, Target_hold, how='outer', indicator=True)

    Target = SET.loc[SET._merge == 'right_only', ['PMID']]
    Target=Target[['PMID']]
    Target = Target.drop_duplicates()


    Drug1 = SET.loc[SET._merge == 'left_only', ['PMID']]
    Drug1=Drug1[['PMID']]
    Drug2 = SET.loc[SET._merge == 'both', ['PMID']]
    Drug2=Drug2[['PMID']]
    Drug_total = pd.merge(Drug1, Drug2, how='outer')
    Drug_total = Drug_total.drop_duplicates()

    target = df[['PMID', 'Grant_Type_Name']].drop_duplicates().merge(Target, how = 'inner', on='PMID')
    target['type'] = 'Target'
    drug = df[['PMID', 'Grant_Type_Name']].drop_duplicates().merge(Drug_total, how = 'inner', on='PMID')
    drug['type'] = 'Drug'
    total_df = target.append(drug).groupby(['Grant_Type_Name', 'type'])['PMID'].nunique().reset_index()

    total_df = total_df.pivot(index="Grant_Type_Name", columns="type", values="PMID").reset_index().fillna(0)
    total_df['Total'] = total_df.Drug +total_df.Target
    total_df = total_df.sort_values('Total', ascending = False)

    return total_df.head(10)


# In[40]:


top_10_productive_proj_target_drug(df,Drug_hold,Target_hold )


# In[41]:


top_10_productive_proj(df)


# In[42]:


def build_banner():
    return html.Div(
            id="header",
            children=[
                html.H3(
                    id='header-title',
                    children="NIH Funded Drug Innovation (NFDI)"),
            ]
        )


# In[43]:


def blocks(df, df_t, df_d, df_t_pmid, df_d_pmid, df_t_cost, df_d_cost,Target_hold, Drug_hold):
    return html.Div(id = 'blocks', children = [ 
                html.Div(id = 'block1', children=[html.P("PMID", style={'textAlign': 'center', 'fontWeight': 'bold', 'color': '#0a0a0a','padding': '1rem','font-size': '16px',},),
                        html.P(style={'color': '#0a0a0a'}, children=['Total: {:,}'.format(df_d_pmid.PMID.nunique() + df_t_pmid.PMID.nunique()),
                                                                     html.Br(),
                                                                      'Target: {:,}'.format(df_t_pmid.PMID.nunique()),
                                                                      html.Br(),
                                                                      'Drug: {:,}'.format(df_d_pmid.PMID.nunique()),

                                                                     ])],
                         className="box2", style={
                            'backgroundColor':'#ceeafc',
                            'height':'200px',
#                             'margin-left':'10px',
                            'text-align':'center',
                            'width':'20%',
                            'display':'inline-block'
                           },
                        
                        ),
 
                html.Div(id = 'block2',children=[html.P("NIH Funded PMID", style={'textAlign': 'center', 'fontWeight': 'bold', 'color': '#4d4d4d','padding': '1rem','font-size': '16px'},),
                        html.P(style={'color': '#4d4d4d'}, children=['Total: {:,}'.format(unique_pmid(prepare_data_block2_target(Target_hold, Drug_hold)) + unique_pmid(prepare_data_block2_drug(Target_hold, Drug_hold))), # target + drug
                                                                     html.Br(),
                                                                      'Target: {:,}'.format(unique_pmid(prepare_data_block2_target(Target_hold, Drug_hold))), # lalala full
                                                                      html.Br(),
                                                                      'Drug: {:,}'.format(unique_pmid(prepare_data_block2_drug(Target_hold, Drug_hold))), # lalala full
                                                                     ])],
                        className="box2", style={
                                'backgroundColor':'#86ccf7',
                                'height':'200px',
#                                 'margin-left':'10px',
                                'text-align':'center',
                                'width':'20%',
                                'display':'inline-block'
                               }),
        
                html.Div(id = 'block3', children=[html.P("Project", style={'textAlign': 'center', 'fontWeight': 'bold', 'color': '#4d4d4d','padding': '1rem','font-size': '16px'},),
                        html.P(style={'color': '#4d4d4d'}, children=['Total: {:,}'.format(unique_project(df_t) + unique_project(df_d)), # target + drug
                                                                     html.Br(),
                                                                      'Target: {:,}'.format(unique_project(df_t)),# lalala full
                                                                      html.Br(),
                                                                      'Drug: {:,}'.format(unique_project(df_d)),# lalala full

                                                                     ])],
                         className="box2", style={
                            'backgroundColor':'#56b8f4',
                            'height':'200px',
#                             'margin-left':'10px',
                            'text-align':'center',
                            'width':'20%',
                            'display':'inline-block'
                           },
                        
                        ),
                html.Div(id = 'block4',children=[html.P("Project Years", style={'textAlign': 'center', 'fontWeight': 'bold', 'color': '#efefef','padding': '1rem','font-size': '16px'},),
                       html.P(style={'color': '#efefef'}, children=[
                                                                   'Total: {:,}'.format(apy(df_t) + apy(df_d)),# target + drug
                                                                    html.Br(),
                                                                   'Target: {:,}'.format(apy(df_t)),# lalala full
                                                                    html.Br(),
                                                                   'Drug: {:,}'.format(apy(df_d)),])# lalala full
                                  ],
                         className="box2", style={
                                'backgroundColor':'#0f9aee',
                                'height':'200px',
#                                 'margin-left':'10px',
                                'text-align':'center',
                                'width':'20%',
                                'display':'inline-block'
                               }),
                html.Div(id = 'block5',children=[html.P("Funding", style={'textAlign': 'center', 'fontWeight': 'bold', 'color': '#fbf8f8','padding': '1rem','font-size': '16px'},),
                        html.P(style={'color': '#fbf8f8'}, children=['Total: {:,}'.format(total_funding(df_t_cost) + total_funding(df_d_cost)), # check if target + drug
                                                                      html.Br(),
                                                                      'Target: {:,}'.format(total_funding(df_t_cost)),# lalala full
                                                                      html.Br(),
                                                                      'Drug: {:,}'.format(total_funding(df_d_cost)),# lalala full 
                                                                     ])],
                        className="box2", style={
                            'backgroundColor':'#098e3b',
                            'height':'200px',
#                             'margin-left':'10px',
                            'width':'20%',
                            'text-align':'center',
                            'display':'inline-block'
                            }),

                            ])


# In[44]:


# tab 1 lineplot

def tab1_fig(df_t, df_d):
    #Tab1 Lineplot target data
    pmid_count_year_plot_target = pmid_count_year_plot(df_t) # PUB_YEAR  PMID
    # pmid_count_year_plot_target
    APY_yearly_plot_target = APY_yearly_plot(df_t) #APY  ACTUAL_PROJECT_YEAR
    # APY_yearly_plot_target
    funding_yearly_plot_target = funding_yearly_plot(df_t) # APY  APY_COST_inf2018
    # funding_yearly_plot_target


    #Tab1 Lineplot drug data
    pmid_count_year_plot_drug = pmid_count_year_plot(df_d) # PUB_YEAR PMID
    # pmid_count_year_plot_drug
    APY_yearly_plot_drug = APY_yearly_plot(df_d)  # APY ACTUAL_PROJECT_YEAR
    # APY_yearly_plot_drug
    funding_yearly_plot_drug =funding_yearly_plot(df_d) # APY  APY_COST_inf2018
    # funding_yearly_plot_drug

    fig = make_subplots(
        rows=2, cols=3, subplot_titles=( "PMID Count by Year (Target)", "Project Year by Year (Target)", "NIH Funded Drug Innovation by Year (Target)",
                                         "PMID Count by Year (Drug)", "Project Year by Year (Drug)", "NIH Funded Drug Innovation by Year (Drug)"), vertical_spacing=0.4
    )

    #pmid
    fig.add_trace(go.Bar(x=pmid_count_year_plot_target['PUB_YEAR'], y=pmid_count_year_plot_target['PMID'], name = 'Target', marker_color='#719FB0', showlegend=False),row=1, col=1)
    fig.add_trace(go.Bar(x=APY_yearly_plot_target['APY'], y=APY_yearly_plot_target['ACTUAL_PROJECT_YEAR'],name = 'Target', marker_color='#719FB0', showlegend=False), row=1, col=2)
    fig.add_trace(go.Bar(x=funding_yearly_plot_target['APY'], y=funding_yearly_plot_target['APY_COST_inf2018'], name = 'Target',marker_color='#719FB0', showlegend=False),row=1, col=3)


    fig.add_trace(go.Bar(x=pmid_count_year_plot_drug['PUB_YEAR'], y=pmid_count_year_plot_drug['PMID'], name = 'Drug', marker_color='#719FB0',  showlegend=False),row=2, col=1)
    fig.add_trace(go.Bar(x=APY_yearly_plot_drug['APY'], y=APY_yearly_plot_drug['ACTUAL_PROJECT_YEAR'],name = 'Drug', marker_color='#719FB0',showlegend=False), row=2, col=2)
    fig.add_trace(go.Bar(x=funding_yearly_plot_drug['APY'], y=funding_yearly_plot_drug['APY_COST_inf2018'], name = 'Drug',marker_color='#719FB0', showlegend=False ),row=2, col=3)


    # Update xaxis properties
    fig.update_xaxes(title_text="Year", tick0 = 2000, dtick=5, row=1, col=1)
    fig.update_xaxes(title_text="Year", tick0 = 2000, dtick=5, row=1, col=2)
    fig.update_xaxes(title_text="Year", tick0 = 2000, dtick=5, row=1, col=3)
    fig.update_xaxes(title_text="Year", tick0 = 2000, dtick=5, row=2, col=1)
    fig.update_xaxes(title_text="Year", tick0 = 2000, dtick=5, row=2, col=2)
    fig.update_xaxes(title_text="Year", tick0 = 2000, dtick=5, row=2, col=3)

    # Update yaxis properties
    fig.update_yaxes(title_text="PMID",rangemode="tozero", row=1, col=1)
    fig.update_yaxes(title_text="Project", rangemode="tozero", row=1, col=2)
    fig.update_yaxes(title_text="USD", rangemode="tozero", row=1, col=3)
    fig.update_yaxes(title_text="PMID",rangemode="tozero", row=2, col=1)
    fig.update_yaxes(title_text="Project", rangemode="tozero", row=2, col=2)
    fig.update_yaxes(title_text="USD", rangemode="tozero", row=2, col=3)
    # fig.update_layout(showlegend=False)

    # Update title and height
    fig.update_layout(paper_bgcolor =  'rgba(0, 0, 0, 0)')
    
    return fig


# In[45]:


top_10_fund_ins_target_drug(df)


# In[46]:


top_10_fund_ins_target_drug(df)


# In[47]:


def tab2_barplot1(df):
    top10_list = top_10_fund_ins_target_drug(df).rename(columns = {'APY_COST_inf2018_Drug': 'Drug', 'APY_COST_inf2018_Target_Only': 'Target', 'APY_COST_inf2018_Total': 'Total'})
    fig2_1_1 = px.bar(top10_list.sort_values('Total'), x=['Drug', 'Target'], y='full_institute_name_', orientation='h', color_discrete_sequence=['#719FB0','#dd6e42'])
    fig2_1_1.update_xaxes(title_text="2018 Inflation USD")
    fig2_1_1.update_yaxes(title_text="")
    fig2_1_1.update_layout(autosize=True,showlegend=True,legend_title_text='', paper_bgcolor =  'rgba(0, 0, 0, 0)', title = 'Top 10 Institutes by Funding')
    return fig2_1_1


# In[48]:


# tab2  overview barplot 1
# def tab2_barplot1(df):
#     fig2_1_1 = go.Figure([go.Bar(y=top_10_fund_ins_target_drug(df).sort_values('APY_COST_inf2018')['full_institute_name'], x=top_10_fund_ins_target_drug(df).sort_values('APY_COST_inf2018')['APY_COST_inf2018'],orientation='h')])
#     fig2_1_1.update_traces(marker_color='#719FB0')
#     fig2_1_1.update_xaxes(title_text="2018 Inflation USD")
#     # fig2_1_1.update_yaxes(automargin=True)
#     fig2_1_1.update_layout(autosize=True,showlegend=False,paper_bgcolor =  'rgba(0, 0, 0, 0)', title = 'Top 10 Institutes by Funding')
    
#     return fig2_1_1


# In[49]:


top_10_productive_ins_target_drug(df,Drug_hold,Target_hold)


# In[50]:


top_10_productive_ins_target_drug(df,Drug_hold,Target_hold).sort_values('Total')


# In[51]:


# tab2  overview barplot 2
def tab2_barplot2(df,Drug_hold,Target_hold):
    top10_list = top_10_productive_ins_target_drug(df,Drug_hold,Target_hold).sort_values('Total')
    fig2_1_2 = px.bar(top10_list, x=['Drug', 'Target'], y='full_institute_name', orientation='h', color_discrete_sequence=['#719FB0','#dd6e42'])
    fig2_1_2.update_xaxes(title_text="PMID Count")
    fig2_1_2.update_yaxes(title_text="")
    fig2_1_2.update_layout(autosize=True,showlegend=True,legend_title_text='', paper_bgcolor =  'rgba(0, 0, 0, 0)', title = 'Top 10 Institutes by PMID')
    return fig2_1_2


# In[52]:


# # tab2  overview barplot 2
# def tab2_barplot2(df):
#     fig2_1_2 = go.Figure([go.Bar(y=top_10_productive_ins(df).sort_values('PMID')['full_institute_name'], x=top_10_productive_ins(df).sort_values('PMID')['PMID'],orientation='h')])
#     fig2_1_2.update_traces(marker_color='#719FB0')
#     fig2_1_2.update_xaxes(title_text="PMID Count")
#     # fig2_1_2.update_yaxes(automargin=True)
#     fig2_1_2.update_layout(autosize=True,showlegend=False,paper_bgcolor =  'rgba(0, 0, 0, 0)', title = 'Top 10 Institutes by PMID')
    
#     return fig2_1_2


# In[53]:


# tab 2 prepare data for selected insitute
ins__checklist =list(df['full_institute_name'].drop_duplicates()[:])
ins_checklist_df_total = df[df.full_institute_name.isin(ins__checklist)]
ins_checklist_df_total


# In[54]:


def tab2_selected_barplot1(df):    
    
    ins__checklist =list(df['full_institute_name'].drop_duplicates()[:])
    ins_checklist_df_total = df[df.full_institute_name.isin(ins__checklist)]
    # tab2  select institue barplot 1
    fig2_2_1 = go.Figure([go.Bar(y=top_10_fund_ins(ins_checklist_df_total).sort_values('APY_COST_inf2018')['full_institute_name'], x=top_10_fund_ins(ins_checklist_df_total).sort_values('APY_COST_inf2018')['APY_COST_inf2018'],orientation='h')])
    fig2_2_1.update_traces(marker_color='#719FB0')
    fig2_2_1.update_xaxes(title_text="2018 Inflation USD")
    # fig2_2_1.update_yaxes(automargin=True)
    fig2_2_1.update_layout(autosize=True,showlegend=False,paper_bgcolor =  'rgba(0, 0, 0, 0)', title = 'Top Institutes by Funding (Selected)')
    
    return fig2_2_1


# In[55]:


# tab2  select institue barplot 2
def tab2_selected_barplot2(df): 
    
    ins__checklist =list(df['full_institute_name'].drop_duplicates()[:])
    ins_checklist_df_total = df[df.full_institute_name.isin(ins__checklist)]
    fig2_2_2 = go.Figure([go.Bar(y=top_10_productive_ins(ins_checklist_df_total).sort_values('PMID')['full_institute_name'], x=top_10_productive_ins(ins_checklist_df_total).sort_values('PMID')['PMID'],orientation='h')])
    fig2_2_2.update_traces(marker_color='#719FB0')
    fig2_2_2.update_xaxes(title_text="PMID Count")
    # fig2_2_2.update_yaxes(automargin=True)
    fig2_2_2.update_layout(autosize=True,showlegend=False,paper_bgcolor =  'rgba(0, 0, 0, 0)', title = 'Top Institutes by PMID (Selected)')
    
    return fig2_2_2


# In[56]:


def tab2_selected_lineplot1(df):
    
    ins__checklist =list(df['full_institute_name'].drop_duplicates()[:])
    ins_checklist_df_total = df[df.full_institute_name.isin(ins__checklist)]
    # tab 2 prepare data for selected ins lineplot 1
    selected_funding_yearly_plot_total = ins_checklist_df_total.drop_duplicates('ACTUAL_PROJECT_YEAR').groupby(by = ['full_institute_name','APY']).APY_COST_inf2018.sum().reset_index()
    # selected_funding_yearly_plot_total

    # tab 2 selected ins lineplot 1
    fig2_3_1 = px.line(selected_funding_yearly_plot_total, x="APY", y="APY_COST_inf2018", color='full_institute_name', title = 'Funding by Year (Selected)', labels={"full_institute_name": ""})
    fig2_3_1.update_xaxes(title_text="Year")
    fig2_3_1.update_yaxes(title_text="2018 Inflation USD")
    fig2_3_1.update_layout(paper_bgcolor =  'rgba(0, 0, 0, 0)')
    #fig2_3_1.show()
    
    return fig2_3_1


# In[57]:


ins__checklist =list(df['full_institute_name'].drop_duplicates()[:])
ins_checklist_df_total = df[df.full_institute_name.isin(ins__checklist)]
ins_checklist_df_total


# In[58]:


def tab2_selected_lineplot2(df):
    
    ins__checklist =list(df['full_institute_name'].drop_duplicates()[:])
    ins_checklist_df_total = df[df.full_institute_name.isin(ins__checklist)]
    # tab 2 prepare data for selected ins lineplot 2
    selected_pmid_count_year_plot_total = ins_checklist_df_total.groupby(by = ['full_institute_name','APY']).PMID.nunique().reset_index()
#     selected_pmid_count_year_plot_total

    # tab 2 selected ins lineplot 2
    fig2_3_2 = px.line(selected_pmid_count_year_plot_total, x="APY", y="PMID", color='full_institute_name', title = 'PMID Count by Year (Selected)', labels={"full_institute_name": ""})
    fig2_3_2.update_xaxes(title_text="Year")
    fig2_3_2.update_yaxes(title_text="PMID Count")
    fig2_3_2.update_layout(paper_bgcolor='rgba(0, 0, 0, 0)')
    #fig2_3_2.show()
    
    return fig2_3_2


# In[59]:


top_10_fund_proj_target_drug(df)


# In[60]:


def tab3_barplot1(df):
    top10_list = top_10_fund_proj_target_drug(df).sort_values('Total')
    fig3_1_1 = px.bar(top10_list, x=['Drug', 'Target_Only'], y='Grant_Type_Name', orientation='h', color_discrete_sequence=['#719FB0','#dd6e42'])
    fig3_1_1.update_xaxes(title_text="2018 Inflation USD")
    fig3_1_1.update_yaxes(title_text="")
    fig3_1_1.update_layout(autosize=True,showlegend=True,legend_title_text='', paper_bgcolor =  'rgba(0, 0, 0, 0)', title = 'Top 10 Project Types by Funding')
    return fig3_1_1


# In[61]:


# def tab3_barplot1(df):
#     # tab3  overview barplot 1
#     fig3_1_1 = go.Figure([go.Bar(y=top_10_fund_proj(df).sort_values('APY_COST_inf2018')['Grant_Type_Name'], x=top_10_fund_proj(df).sort_values('APY_COST_inf2018')['APY_COST_inf2018'], orientation='h')])
#     fig3_1_1.update_traces(marker_color='#719FB0')
#     fig3_1_1.update_xaxes(title_text="2018 Inflation USD")
#     # fig2_1_1.update_yaxes(automargin=True)
#     fig3_1_1.update_layout(autosize=True,showlegend=False,paper_bgcolor =  'rgba(0, 0, 0, 0)', title = 'Top 10 Project Type by Funding')
    
#     return fig3_1_1


# In[62]:


# def tab3_barplot2(df):
#     # tab3  overview barplot 2
#     fig3_1_2 = go.Figure([go.Bar(y=top_10_productive_proj(df).sort_values('PMID')['Grant_Type_Name'], x=top_10_productive_proj(df).sort_values('PMID')['PMID'],orientation='h')])
#     fig3_1_2.update_traces(marker_color='#719FB0')
#     fig3_1_2.update_xaxes(title_text="PMID Count")
#     # fig2_1_1.update_yaxes(automargin=True)
#     fig3_1_2.update_layout(autosize=True,showlegend=False,paper_bgcolor =  'rgba(0, 0, 0, 0)', title = 'Top 10 Project Type by PMID')
    
#     return fig3_1_2


# In[63]:


top_10_productive_proj_target_drug(df,Drug_hold,Target_hold)


# In[64]:


# tab3  overview barplot 2
def tab3_barplot2(df,Drug_hold,Target_hold):
    top10_list = top_10_productive_proj_target_drug(df,Drug_hold,Target_hold).sort_values('Total')
    fig3_1_2 = px.bar(top10_list, x=['Drug', 'Target'], y='Grant_Type_Name', orientation='h', color_discrete_sequence=['#719FB0','#dd6e42'])
    fig3_1_2.update_xaxes(title_text="PMID Count")
    fig3_1_2.update_yaxes(title_text="")
    fig3_1_2.update_layout(autosize=True,showlegend=True,legend_title_text='', paper_bgcolor =  'rgba(0, 0, 0, 0)', title = 'Top 10 Project Types by PMID')
    return fig3_1_2


# In[65]:


# tab 3 prepare data for selected pro 
pro__checklist =list(df['Grant_Type_Name'].drop_duplicates()[:])
pro_checklist_df_total = df[df.Grant_Type_Name.isin(pro__checklist)]
pro_checklist_df_total


# In[66]:


def tab3_selected_barplot1(pro_checklist_df_total):

    # tab3  select pro barplot 1
    fig3_2_1 = go.Figure([go.Bar(y=top_10_fund_proj(pro_checklist_df_total).sort_values('APY_COST_inf2018')['Grant_Type_Name'], x=top_10_fund_proj(pro_checklist_df_total).sort_values('APY_COST_inf2018')['APY_COST_inf2018'], orientation='h')])
    fig3_2_1.update_traces(marker_color='#719FB0')
    fig3_2_1.update_xaxes(title_text="2018 Inflation USD")
    # fig2_2_1.update_yaxes(automargin=True)
    fig3_2_1.update_layout(autosize=True,showlegend=False,paper_bgcolor =  'rgba(0, 0, 0, 0)', title = 'Top Project Type by Funding (Selected)')
    
    return fig3_2_1


# In[67]:


def tab3_selected_barplot2(pro_checklist_df_total):
    
    # tab3  select pro barplot 2
    fig3_2_2 = go.Figure([go.Bar(y=top_10_productive_proj(pro_checklist_df_total).sort_values('PMID')['Grant_Type_Name'], x=top_10_productive_proj(pro_checklist_df_total).sort_values('PMID')['PMID'],orientation='h')])
    fig3_2_2.update_traces(marker_color='#719FB0')
    fig3_2_2.update_xaxes(title_text="PMID Count")
    # fig2_2_1.update_yaxes(automargin=True)
    fig3_2_2.update_layout(autosize=True,showlegend=False,paper_bgcolor =  'rgba(0, 0, 0, 0)', title = 'Top Project Type by PMID (Selected)')
    
    return fig3_2_2


# In[ ]:





# In[ ]:





# In[68]:


def tab3_selected_lineplot1(pro_checklist_df_total):
    
    # tab 3 prepare data for selected pro lineplot1
    selected_pro_funding_yearly_plot_total = pro_checklist_df_total.drop_duplicates('ACTUAL_PROJECT_YEAR').groupby(by = ['Grant_Type_Name','APY']).APY_COST_inf2018.sum().reset_index()
    # selected_pro_funding_yearly_plot_total
    # tab 3 selected pro lineplot 1
    fig3_3_1 = px.line(selected_pro_funding_yearly_plot_total, x="APY", y="APY_COST_inf2018", color='Grant_Type_Name', title = 'Funding by Year (Selected)', labels={"Grant_Type_Name": ""})
    fig3_3_1.update_xaxes(title_text="Year")
    fig3_3_1.update_yaxes(title_text="2018 Inflation USD")
    fig3_3_1.update_layout(paper_bgcolor =  'rgba(0, 0, 0, 0)')
    # fig3_3_1.show()
    
    return fig3_3_1


# In[69]:


def tab3_selected_lineplot2(pro_checklist_df_total):

    # tab 3 prepare data for selected pro lineplot2
    selected_pro_pmid_count_year_plot_total = pro_checklist_df_total.groupby(by = ['Grant_Type_Name','PUB_YEAR']).PMID.nunique().reset_index()
    # selected_pro_pmid_count_year_plot_total

    # tab 3 selected pro lineplot 2
    fig3_3_2 = px.line(selected_pro_pmid_count_year_plot_total, x="PUB_YEAR", y="PMID", color='Grant_Type_Name', title = 'PMID Count by Year (Selected)', labels={"Grant_Type_Name": ""})
    fig3_3_2.update_xaxes(title_text="Year")
    fig3_3_2.update_yaxes(title_text="PMID Count")
    fig3_3_2.update_layout(paper_bgcolor='rgba(0, 0, 0, 0)')
    # fig3_3_2.show()

    return fig3_3_2


# In[70]:


def tab0():                                       
    return  dcc.Tab(id="INTRODUCTION",
                    label="INTRODUCTION",
                    value="tab0",
                    style = {
                            'fontWeight': 'bold',
                            'color': '#646464',
                            'align-items': 'center',
                            'justify-content': 'center',},
                    className="custom-tab",
                    selected_className="custom-tab--selected",
                    
                     children = [
                         html.P("""Methods:""", style={'font-size': '16px','font-weight': 'bold','marginLeft': 100,'marginRight': 100,'marginTop': 100,'marginBottom': 100,}),]
                    )


# In[71]:


def tab1(df_d_pmid, df_t_pmid, df_t, df_d, df, df_d_cost, df_t_cost,Target_hold, Drug_hold):
    return dcc.Tab(
            id="OVERVIEW",
            label="Funding Analysis",
            value="tab1",   
            style = {
                    'fontWeight': 'bold',
                    'color': '#646464',
                    'align-items': 'center',
                    'justify-content': 'center',},
            className="custom-tab",
            selected_className="custom-tab--selected",
            children=[
                html.Br(),
                html.Div([
                    
                    html.Div([
                        html.P("Please input Target below:", style={'font-size': '16px','textAlign': 'center','font-weight': 'bold','display': 'inline', "margin-right": "40px"}),
                        html.P("Please input Drug below:", style={'font-size': '16px','textAlign': 'center','font-weight': 'bold','display': 'inline'}),
                        dbc.Button("\u2753", id="modal_open1", n_clicks=0, color="link", style={'textAlign': 'center', 'align-items': 'center', 'justify-content': 'center'}),
                        dbc.Modal([
                                 dbc.ModalHeader("Header"),
                                 dbc.ModalBody(
                                     html.Div([html.P("This is the content of the modal"),
                                            dcc.Link("This is a link", href='https://www.google.com/', target="link"),
                                               html.Br(),
                                               html.Img(src=app.get_asset_url("diginex.png"))])
                                                 ),
                                dbc.ModalFooter(
                                        dbc.Button("Close", id="modal_close1", className="ml-auto", n_clicks=0)
                                    ),
                             ],id="modal1", is_open=False,size="xl", scrollable=True,style={'display': 'inline-block', 'align-items': 'center', 'justify-content': 'center',})]
                        
        
                        ,style={'display': 'inline-block', 'align-items': 'center', 'justify-content': 'center',}),
                    
                    html.Br(),
                    
                    html.Div([
                        dcc.Input(id="input Target", type='text', debounce=True, placeholder="Acetylcholinesterase or AD and amyloid or amyloid beta-protein precursor or Amyloid plaques or amyloid precursor protein or secretases or apolipoproteins-e or Presenilins or receptors, n-methyl-d-aspartate or tau proteins or TDP-43",style={ 'font-size': '16px','display': 'inline-block',"margin-right": "20px"}, ),
                        dcc.Store(id='target_output'),
                        dcc.Input(id="input Drug", type='text', debounce=True, placeholder="Aducanumab or Bapineuzumab or Crenezumab or Gantenerumab or Solanezumab",style={ 'font-size': '16px','display': 'inline-block'} ),
                        dcc.Store(id='drug_output'),                     
                             ], style={'display': 'inline-block',"margin-left": "20px",} ),
#                     html.Div(id='drug_output'), 
#                     html.Div(id='target_output'),
                    html.Br(),
                    html.Br(),
                    html.Div([html.Button(id='tab1_submit', type='submit', children='Submit'), ],style={'display': 'inline-block', 'align-items': 'center', 'justify-content': 'center',},
                            ),
                    dcc.Store(id='new_data'),
                    ], style={'textAlign': 'center','align-items': 'center', 'justify-content': 'center',}),
                    
                html.Br(),
                html.Br(),
                html.P("""Notes1:""", style={'font-size': '16px','font-weight': 'bold'}),
                blocks(df, df_t, df_d, df_t_pmid, df_d_pmid, df_t_cost, df_d_cost,Target_hold, Drug_hold),
#                 blocks(df, df_t, df_d, df_t_pmid, df_d_pmid, df_t_cost, df_d_cost),
                html.P("""Notes2:Target represents the basic science before a compound has a drug name/designation. Drug is any research after an official name is acknowledged representing later development.   PMID this is the PubMed reference number that is given to each paper published on NCBI, each PMID represent a unique publication.  NIH funded PMID are the government grant supported PMIDs. Project is the number of unique grants involved in all PMIDs discovered.  Project Year is the year that the PMID is published or within 4 years after the end of a grant funding duration, this locks all PMID to funding of a single year and allows for more accurate interpretation of total grant involvement without significant inflation caused by larger grants supporting multiple PMID publications. Funding is the interpreted Project Years from before as totals for each stage of drug development in million 2018 inflation USD.""", style={'font-size': '16px','font-weight': 'bold','margin-left':'15%'}),
                html.Br(),
                dcc.Graph(id='lineplots',figure = tab1_fig(df_t, df_d),), 

                html.Footer(['© 2021 by Center for Analytics and Data Science (CADS) - Data Analytics Research Team (DART), Bentley University are licensed under ',
                        dcc.Link('CC BY 4.0', href='https://creativecommons.org/licenses/by/4.0/?ref=chooser-v1', target='CC BY 4.0'),
                        html.Img(src=app.get_asset_url("1.png")),
                        html.Img(src=app.get_asset_url("2.png"))])
            ]
    )      


# In[72]:


def tab2(df,Drug_hold,Target_hold):
    return dcc.Tab(
                    id="INSTITUTE",
                    label="Funding Source",
                    value="tab2",
                    style = {'fontWeight': 'bold',
                            'color': '#646464',
                            'align-items': 'center',
                            'justify-content': 'center',},
                    className="custom-tab",
                    selected_className="custom-tab--selected",
                    children=[
                        html.Div([
                            html.P("Overview", style={'textAlign': 'center','font-weight': 'bold', 'font-size': '16px', 'display': 'inline',}),
                            dbc.Button("\u2753", id="modal_open2", n_clicks=0, color="link", style={'textAlign': 'center', 'align-items': 'center', 'justify-content': 'center'}),
                             dbc.Modal([
                                 dbc.ModalHeader("Header"),
                                 dbc.ModalBody(
                                     html.Div([html.P("This is the content of the modal"),
                                            dcc.Link("This is a link", href='https://www.google.com/', target="link"),
                                               html.Br(),
                                               html.Img(src=app.get_asset_url("4.jpg"))])
                                                 ),
                                dbc.ModalFooter(
                                        dbc.Button("Close", id="modal_close2", className="ml-auto", n_clicks=0)
                                    ),
                             ],id="modal2", is_open=False,size="xl", scrollable=True,style={'display': 'inline-block', 'align-items': 'center', 'justify-content': 'center',})
                        ], style={'textAlign': 'center','align-items': 'center', 'justify-content': 'center',}) ,   
                        
                            html.Hr(),  
                            html.Div([dcc.Graph(id="top_10_ins_barplot1", figure = tab2_barplot1(df))], style = {'width': '70%', 'display': 'block', 'margin-left':'15%','margin-right':'15%'}),
                            html.Div([dcc.Graph(id="top_10_ins_barplot2", figure = tab2_barplot2(df,Drug_hold,Target_hold))], style = {'width': '70%', 'display': 'block', 'margin-left':'15%','margin-right':'15%'}),
                            html.Br(),
                            html.P("Select Institutes", style={'textAlign': 'center','font-weight': 'bold', 'font-size': '16px'}),
                            html.Hr(), 
                            html.Div([
                                dcc.Dropdown(
                                        id="ins_selected",
                                        options=[{"label": i, "value": i} for i in ins__checklist],
                                        value=ins__checklist[0:10],
                                        multi=True,
                                         ),], 
                                     style = {'width': '50%', 'display': 'inline-block', 'align-items': 'center', 'justify-content': 'center', 'margin-left':'25%','margin-right':'25%'}
                                         ),

                            html.Div([ 
                    
                                    dcc.Graph(id="selected_ins_barplot1", figure = tab2_selected_barplot1(df)),],
                                    style = {'width': '70%', 'display': 'block', 'margin-left':'15%','margin-right':'15%'}),
                            html.Div([ 
                    
                                    dcc.Graph(id="selected_ins_barplot2", figure = tab2_selected_barplot2(df)),],
                                    style = {'width': '70%', 'display': 'block', 'margin-left':'15%','margin-right':'15%'}),
                            html.Div([ 
                                    dcc.Graph(id="selected_ins_lineplot1", figure = tab2_selected_lineplot1(df)),
                            ],
                                    style = {'width': '70%', 'display': 'block', 'margin-left':'15%','margin-right':'15%'}),

                            html.Div([ 
                                     dcc.Graph(id="selected_ins_lineplot2", figure = tab2_selected_lineplot2(df)),  
                            ],style = {'width': '70%', 'display': 'block', 'margin-left':'15%','margin-right':'15%'}
                                    ),

                            html.Footer(['© 2021 by Center for Analytics and Data Science (CADS) - Data Analytics Research Team (DART), Bentley University are licensed under ',
                                        dcc.Link('CC BY 4.0', href='https://creativecommons.org/licenses/by/4.0/?ref=chooser-v1', target='CC BY 4.0'),
                                        html.Img(src=app.get_asset_url("1.png")),
                                        html.Img(src=app.get_asset_url("2.png"))])

                        ],
#         style = {'margin':'auto','width': "50%"},
                    )
#                                     ]
#                                         )
# #                     ])


# In[73]:


def tab3(df, pro_checklist_df_total,Drug_hold,Target_hold):                                       
    return  dcc.Tab(id="PROJECT",
                    label="Funding Type",
                    value="tab3",
                    style = {
                            'fontWeight': 'bold',
                            'color': '#646464',
                            'align-items': 'center',
                            'textAlign': 'center',
                            'justify-content': 'center',},
                    
                    className="custom-tab",
                    selected_className="custom-tab--selected",
                    children = [
                        html.Div([
                            html.P("Overview", style={'textAlign': 'center','font-weight': 'bold', 'font-size': '16px', 'display': 'inline',}),
                            dbc.Button("\u2753", id="modal_open3", n_clicks=0, color="link", style={'textAlign': 'center', 'align-items': 'center', 'justify-content': 'center'}),
                             dbc.Modal([
                                 dbc.ModalHeader("Header"),
                                 dbc.ModalBody(
                                     html.Div([html.P("This is the content of the modal"),
                                            dcc.Link("This is a link", href='https://www.google.com/', target="link"),
                                               html.Br(),
                                               html.Img(src=app.get_asset_url("4.jpg"))])
                                                 ),
                                dbc.ModalFooter(
                                        dbc.Button("Close", id="modal_close3", className="ml-auto", n_clicks=0)
                                    ),
                             ],id="modal3", is_open=False,size="xl", scrollable=True,style={'display': 'inline-block', 'align-items': 'center', 'justify-content': 'center',})
                        ], style={'textAlign': 'center','align-items': 'center', 'justify-content': 'center',}) , 
                        
                        
                        html.Hr(), 
                        html.Div([
                            dcc.Graph(id='tab3_barplots1',figure = tab3_barplot1(df))],
                            style = {'width': '70%', 'display': 'inline-block', 'margin-left':'15%','margin-right':'15%'}),
                        html.Div([
                            dcc.Graph(id='tab3_barplots2',figure = tab3_barplot2(df,Drug_hold,Target_hold))],
                            style = {'width': '70%', 'display': 'inline-block', 'margin-left':'15%','margin-right':'15%'}),
                        
                        
#                         dcc.Graph(id='tab3_barplots1',figure = fig3_1_1),
#                         dcc.Graph(id='tab3_barplots2',figure = fig3_1_2),
                         html.Br(),
                            html.P("Select Project Type", style={'textAlign': 'center','font-weight': 'bold', 'font-size': '16px'}),
                            html.Hr(), 
                            html.Div([
                                dcc.Dropdown(
                                        id="pro_selected",
                                        options=[{"label": i, "value": i} for i in pro__checklist],
                                        value=pro__checklist[0:10],
                                        multi=True,
                                         ),], 
                                     style = {'width': '50%', 'display': 'inline-block', 'align-items': 'center', 'justify-content': 'center', 'margin-left':'25%','margin-right':'25%'}
                                         ),

                            html.Div([ 
                    
                                    dcc.Graph(id="selected_pro_barplot1", figure = tab3_selected_barplot1(pro_checklist_df_total)),],
                                    style = {'width': '70%', 'display': 'block', 'margin-left':'15%','margin-right':'15%'}),
                         html.Div([ 
                    
                                    dcc.Graph(id="selected_pro_barplot2", figure = tab3_selected_barplot2(pro_checklist_df_total)),],
                                    style = {'width': '70%', 'display': 'block', 'margin-left':'15%','margin-right':'15%'}),
                            html.Div([ 
                                    dcc.Graph(id="selected_pro_lineplot1", figure = tab3_selected_lineplot1(pro_checklist_df_total)),
                            ],
                                    style = {'width': '70%', 'display': 'block', 'margin-left':'15%','margin-right':'15%'}),

                        html.Div([ 
                                     dcc.Graph(id="selected_pro_lineplot2", figure = tab3_selected_lineplot2(pro_checklist_df_total)),  
                            ],style = {'width': '70%', 'display': 'block', 'margin-left':'15%','margin-right':'15%'}
                                    ),
                        html.Footer(['© 2021 by Center for Analytics and Data Science (CADS) - Data Analytics Research Team (DART), Bentley University are licensed under ',
                                    dcc.Link('CC BY 4.0', href='https://creativecommons.org/licenses/by/4.0/?ref=chooser-v1', target='CC BY 4.0'),
                                    html.Img(src=app.get_asset_url("1.png")),
                                    html.Img(src=app.get_asset_url("2.png"))])
                    ],
                        
                    )


# In[74]:


def tab4():                                       
    return  dcc.Tab(id="map",
                    label="Funding Location(WIP)",
                    value="tab4",
                    style = {
                            'fontWeight': 'bold',
                            'color': '#646464',
                            'align-items': 'center',
                            'justify-content': 'center',},
                    className="custom-tab",
                    selected_className="custom-tab--selected",
#                     children = [
#                         dcc.Graph(id='tab3_barplots',figure = fig3),]
                    )


# In[75]:


def tab5():                                       
    return  dcc.Tab(id="download",
                    label="DOWNLOAD",
                    value="tab5",
                    style = {
                            'fontWeight': 'bold',
                            'color': '#646464',
                            'align-items': 'center',
                            'justify-content': 'center',},
                    className="custom-tab",
                    selected_className="custom-tab--selected",
                    children = [
                        html.Div([
                            html.P("Please privide your contact information to download the full dataset as csv", style={'textAlign': 'center','font-weight': 'bold', 'font-size': '16px', 'display': 'inline',}),
                            dbc.Button("\u2753", id="modal_open4", n_clicks=0, color="link", style={'textAlign': 'center', 'align-items': 'center', 'justify-content': 'center'}),
                             dbc.Modal([
                                 dbc.ModalHeader("Header"),
                                 dbc.ModalBody(
                                     html.Div([html.P("This is the content of the modal"),
                                            dcc.Link("This is a link", href='https://www.google.com/', target="link"),
                                               html.Br(),
                                               html.Img(src=app.get_asset_url("4.jpg"))])
                                                 ),
                                dbc.ModalFooter(
                                        dbc.Button("Close", id="modal_close4", className="ml-auto", n_clicks=0)
                                    ),
                             ],id="modal4", is_open=False,size="xl", scrollable=True,style={'display': 'inline-block', 'align-items': 'center', 'justify-content': 'center',}),
                            html.Br(),
                            html.P("We will not use your personal information for commercial purposes.", style={'textAlign': 'center','font-size': '16px', 'display': 'inline',}),
                        ], style={'textAlign': 'center','align-items': 'center', 'justify-content': 'center',}) ,   
                            
                            html.Hr(),  
                        
                        html.Div([
                    
                            html.Div([
                                html.P("Name:", style={'font-size': '16px'}),
                                dcc.Input(id="Name", type='text', placeholder="Name",style={ 'font-size': '16px',} ),
                                dcc.Store(id = 'Name_input')], 
                                style={'display': 'inline-block', "margin-right": "20px"} ),
                            html.Div([
                                html.P("Affiliation:", style={'font-size': '16px',}),
                                dcc.Input(id="Affiliation", type='text', placeholder="Affiliation",style={ 'font-size': '16px',} ),
                                dcc.Store(id = 'Affiliation_input')], 
                                style={'display': 'inline-block', "margin-right": "20px"} ),
                            html.Div([
                                html.P("Email:", style={'font-size': '16px',}),
                                dcc.Input(id="Email", type='text', placeholder="Email",style={ 'font-size': '16px',} ),
                                dcc.Store(id = 'Email_input')], 
                                style={'display': 'inline-block', "margin-right": "20px"} ),
                            html.Div([
                                html.P("Purpose:", style={'font-size': '16px',}),
                                dcc.Checklist(id = 'Purpose_checklist',options=[
                                    {'label': 'Research', 'value': 'Research'},
                                    {'label': 'Teaching', 'value': 'Teaching'},
                                    {'label': 'News/Report', 'value': 'News/Report'},
                                    {'label': 'Government Service', 'value': 'Government Service'},
                                    {'label': 'Other', 'value': 'Other'}
                                ],
                                    value=[],labelStyle={'display': 'inline-block', 'margin-left': '.8rem'}
                                ),
                                dcc.Store(id = 'Purpose_input')
                                
                                ], 
                                style={'display': 'inline-block', } ),
        
                    ], style={'width': '100%', 'display': 'flex', 'justifyContent':'center'}),
                        
                        html.Br(),
                     
                        
                        
                        
                        html.Div([
#                             html.Button("Submit", id="user_info_Submit"),
                            dbc.Button("Submit", id="modal_open5", n_clicks=0, color="link", style={'textAlign': 'center', 'align-items': 'center', 'justify-content': 'center'}),
                             dbc.Modal([
                                 dbc.ModalHeader("Header"),
                                 dbc.ModalBody(
                                     html.Div([dbc.Button("Download", id="btn_csv", className="ml-auto", n_clicks=0),
                                     dcc.Download(id="download-file")])
                                     
                                 ),
                                 dbc.ModalFooter(
                                        dbc.Button("Close", id="modal_close5", className="ml-auto", n_clicks=0)
                                    ),
                             ],id="modal5", is_open=False,size="xl", scrollable=True,style={'display': 'inline-block', 'align-items': 'center', 'justify-content': 'center',})
                        ], style={'width': '100%', 'display': 'flex', 'justifyContent':'center'}),
                        
                        html.Br(),
                        
                        
                        ]
                    )


# In[76]:


def tab6():                                       
    return  dcc.Tab(id="help",
                    label="HELP",
                    value="tab6",
                    style = {
                            'fontWeight': 'bold',
                            'color': '#646464',
                            'align-items': 'center',
                            'justify-content': 'center',},
                    className="custom-tab",
                    selected_className="custom-tab--selected",
                    children = [
                        html.Div([
                            html.P("Search Term", id="help_search", style={'textAlign': 'center','font-weight': 'bold', 'font-size': '16px'}),
                            html.Hr(), 
                        ]),
                        html.Div([
                            html.P("Institute", id="help_institute", style={'textAlign': 'center','font-weight': 'bold', 'font-size': '16px'}),
                            html.Hr(), 
                        ]),
                        html.Div([
                            html.P("Project/Grants", id="help_project", style={'textAlign': 'center','font-weight': 'bold', 'font-size': '16px'}),
                            html.Hr(), 
                        ]),
                        html.Div([
                            html.P("Graph/Plotly usage", id="help_graph", style={'textAlign': 'center','font-weight': 'bold', 'font-size': '16px'}),
                            html.Hr(), 
                        ]),
                        
                        html.Div([
                            html.P("Map", id="help_map", style={'textAlign': 'center','font-weight': 'bold', 'font-size': '16px'}),
                            html.Hr(), 
                        ]),
                        html.Div([
                            html.P("Download", id="help_download", style={'textAlign': 'center','font-weight': 'bold', 'font-size': '16px'}),
                            html.Hr(), 
                        ]),
                        
                        ]
                    )


# In[77]:


def tab7():                                       
    return  dcc.Tab(id="aboutus",
                    label="ABOUT US",
                    value="tab7",
                    style = {
                            'fontWeight': 'bold',
                            'color': '#646464',
                            'align-items': 'center',
                            'justify-content': 'center',},
                    className="custom-tab",
                    selected_className="custom-tab--selected",
                    children = [
                       html.H1("Test", style={'textAlign': 'center','font-weight': 'bold', 'font-size': '16px'}),]
                    )


# In[78]:


app = DashProxy(
    __name__,
    meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=0.3'},
              ],external_stylesheets = [dbc.themes.BOOTSTRAP],
    prevent_initial_callbacks=True, transforms=[MultiplexerTransform()])
app.title = "NIH Funded Drug Innovation (NFDI) "


# In[79]:


def serve_layout(df_d_pmid, df_t_pmid, df_t, df_d, df,pro_checklist_df_total,Drug_hold, Target_hold):
    return html.Div(
    id="big-app-container",
    children=[
        dcc.Store(id="store1"), 
        dcc.Store(id="store2"), 
        dcc.Store(id="store3"), 
        dcc.Store(id="store4"), 
        dcc.Store(id="store5"), 
        dcc.Store(id="store6"),
        dcc.Store(id="store7"), 
        dcc.Store(id="store8"),
        dcc.Store(id="store9"), 
        dcc.Store(id="store10"),
        build_banner(),
#         id="app-container",
#         children=[
            html.Div(
            id="tabs",
            className="tabs",
            children=[
                
                
#                 html.Div(id="trigger"),
                dcc.Tabs(id="app-tabs",
                               value="tab0",
                               className="custom-tabs",
                               colors={"border": "#6B95B", "background": "#ACCCDD"},
                               children=[
                                        tab0(),
                                          tab1(df_d_pmid, df_t_pmid, df_t, df_d, df, df_d_cost, df_t_cost,Target_hold, Drug_hold),
                                          tab2(df,Drug_hold,Target_hold), 
                                          tab3(df, pro_checklist_df_total,Drug_hold,Target_hold),
                                          tab4(), 
                                          tab5(), 
                                          tab6(),
                                          tab7(),],
                                  ),
                html.P(id='placeholder'),
                dcc.Store(id="user_info"), 
                html.Div(id = 'trigger')
                         ]
                )
    ]
#     ]
)


# In[80]:


app.layout = serve_layout(df_d_pmid, df_t_pmid, df_t, df_d, df,pro_checklist_df_total, Drug_hold, Target_hold)


# In[81]:


# @app.callback(
#     Output("loading-output", "figure"),
#     [Input("tab1_submit", "n_clicks"), ],
#     [State("modal1", "is_open")],
# )
# def toggle_modal1(n1, n2, is_open):
#     if n1 or n2:
#         return not is_open
#     return is_open


# In[82]:


# pop-up window  callback


# In[83]:


@app.callback(
    Output("modal1", "is_open"),
    [Input("modal_open1", "n_clicks"), Input("modal_close1", "n_clicks")],
    [State("modal1", "is_open")],
)
def toggle_modal1(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


# In[84]:


@app.callback(
    Output("modal2", "is_open"),
    [Input("modal_open2", "n_clicks"), Input("modal_close2", "n_clicks")],
    [State("modal2", "is_open")],
)
def toggle_modal2(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


# In[85]:


@app.callback(
    Output("modal3", "is_open"),
    [Input("modal_open3", "n_clicks"), Input("modal_close3", "n_clicks")],
    [State("modal3", "is_open")],
)
def toggle_modal3(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


# In[86]:


@app.callback(
    Output("modal4", "is_open"),
    [Input("modal_open4", "n_clicks"), Input("modal_close4", "n_clicks")],
    [State("modal4", "is_open")],
)
def toggle_modal4(n1, n2, is_open):
    if n1 or n2:
        return not is_open


# In[87]:


@app.callback(
    Output("modal5", "is_open"),
    [Input("modal_open5", "n_clicks"), Input("modal_close5", "n_clicks")],
    [State("modal5", "is_open")],
)
def toggle_modal5(n1, n2, is_open):
    if n1 or n2:
        return not is_open


# In[88]:


# tab 2 and tab 3 interaction


# In[89]:


@app.callback(
    Output(component_id = 'selected_ins_barplot1', component_property = 'figure'),
    [Input(component_id = 'ins_selected', component_property = 'value')]
)
def update_2_2_1barplot(ins_selection):
    ins_checklist_df_total = df[df.full_institute_name.isin(ins_selection)]
    
    return tab2_selected_barplot1(ins_checklist_df_total)
    


# In[90]:


@app.callback(
    Output(component_id = 'selected_ins_barplot2', component_property = 'figure'),
    [Input(component_id = 'ins_selected', component_property = 'value')]
)
def update_2_2_2barplot(ins_selection):
    ins_checklist_df_total = df[df.full_institute_name.isin(ins_selection)]

    return tab2_selected_barplot2(ins_checklist_df_total)


# In[91]:


@app.callback(
    Output(component_id = 'selected_ins_lineplot1', component_property = 'figure'),
    [Input(component_id = 'ins_selected', component_property = 'value')]
)
def update_2_3_lineplot1(ins_selection):
    ins_checklist_df_total = df[df.full_institute_name.isin(ins_selection)]

    return tab2_selected_lineplot1(ins_checklist_df_total)


# In[92]:


@app.callback(
    Output(component_id = 'selected_ins_lineplot2', component_property = 'figure'),
    [Input(component_id = 'ins_selected', component_property = 'value')]
)
def update_2_3_lineplot2(ins_selection):
    ins_checklist_df_total = df[df.full_institute_name.isin(ins_selection)]
    
    return tab2_selected_lineplot2(ins_checklist_df_total)


# In[93]:


@app.callback(
    Output(component_id = 'selected_pro_barplot1', component_property = 'figure'),
    [Input(component_id = 'pro_selected', component_property = 'value')]
)
def update_3_2_1barplot(pro_selection):
    pro_checklist_df_total = df[df.Grant_Type_Name.isin(pro_selection)]
    
    return tab3_selected_barplot1(pro_checklist_df_total)


# In[94]:


@app.callback(
    Output(component_id = 'selected_pro_barplot2', component_property = 'figure'),
    [Input(component_id = 'pro_selected', component_property = 'value')]
)
def update_3_2_2barplot(pro_selection):
    
    pro_checklist_df_total = df[df.Grant_Type_Name.isin(pro_selection)]
    
    return tab3_selected_barplot2(pro_checklist_df_total)


# In[ ]:





# In[95]:


@app.callback(
    Output(component_id = 'selected_pro_lineplot1', component_property = 'figure'),
    [Input(component_id = 'pro_selected', component_property = 'value')]
)
def update_3_3_lineplot1(pro_selection):
    pro_checklist_df_total = df[df.Grant_Type_Name.isin(pro_selection)]
    
    return tab3_selected_lineplot1(pro_checklist_df_total)


# In[96]:


@app.callback(
    Output(component_id = 'selected_pro_lineplot2', component_property = 'figure'),
    [Input(component_id = 'pro_selected', component_property = 'value')]
)
def update_3_3_lineplot2(pro_selection):
    pro_checklist_df_total = df[df.Grant_Type_Name.isin(pro_selection)]
    
    return tab3_selected_lineplot2(pro_checklist_df_total)


# In[97]:


user_info= pd.read_csv('function_data/user_info.csv')


# In[98]:


@app.callback(Output('placeholder', 'children'),
              Input('modal_open5', 'n_clicks'),
#               State('Time', 'value'),
              State('Name', 'value'),
              State('Affiliation', 'value'),
              State('Email', 'value'),
              State('Purpose_checklist', 'value'), prevent_initial_call=True)
def update_user_info(n_clicks, Name, Affiliation, Email,Purpose):
    Time = date.today().strftime("%m/%d/%y")
#     print('**********************purpose****************')
#     print(Purpose)
#     print(type(Purpose))
    purpose_str = ', '.join([elem for elem in Purpose])
#     print(purpose_str)
    new_row = pd.DataFrame({'Time': Time, 'Name':Name, 'Affiliation':Affiliation, 'Email':Email, 'Purpose': [purpose_str]})
#     print('**********************new row****************')
#     print(new_row)
#     new_row = {'Name':Name, 'Affiliation':Affiliation, 'Email':Email, 'Purpose':Purpose}
#     user_info = user_info.append(new_row, ignore_index=True)
    new_row.to_csv('function_data/user_info.csv', index = False, mode='a', header=False)
    return user_info


# In[99]:


@app.callback(Output('store1', 'data'),
              Output('store2', 'data'),
              Output('store3', 'data'),
              Output('store4', 'data'),
              Output('store5', 'data'),
              Output('store6', 'data'),
              Output('store7', 'data'),
              Output('store8', 'data'),
              Output('store9', 'data'),
              Output('store10', 'data'),
              [Input('tab1_submit', 'n_clicks')],
              [State('input Target', 'value'),
              State('input Drug', 'value')], 
              prevent_initial_call=True)
def update_data(n_clicks,search_term_target,search_term_drug):

    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    d = {'A': '\"""','search_term_target': [search_term_target],'B': '\"""', 'search_term_drug': [search_term_drug],'C': '\"""',}
    data = pd.DataFrame(data = d)
    data.to_csv('data.csv', index = None)
    
    new_data = pd.read_csv('data.csv')
    search_term_target = new_data.iloc[0]['A'] + new_data.iloc[0]['search_term_target'] + new_data.iloc[0]['B']
    search_term_target
    search_term_drug = new_data.iloc[0]['B']+ new_data.iloc[0]['search_term_drug'] + new_data.iloc[0]['C']
    search_term_drug
    
    ################### input target list #############################
    for search_term_drug in new_data.search_term_drug:
        pub_key_entz_drug(search_term_drug)

    for search_term_target in new_data.search_term_target:
        pub_key_entz_target(search_term_target)
    
    
    print('1 target--------------------------------')
    print(search_term_target)
    print('2 drug--------------------------------')
    print(search_term_drug)
    
    J_resultUQ_FULL, J_Target_hold, J_Drug_hold, J_Target_pmid_UQ, J_Drug_pmid_UQ, J_resultUQ_APY_COST = NIH_Search_Drug(search_term_drug, search_term_target)
#     print('================== store1: full   =================')
#     print(J_resultUQ_FULL.Search_Type.value_counts())
    
    
    df_t_new = J_resultUQ_FULL[J_resultUQ_FULL.Search_Type == 'Target_Only']
#     print('================== store2: df_t_new   =================')
#     print(df_t_new.head())
    
    df_d_new = J_resultUQ_FULL[J_resultUQ_FULL.Search_Type == 'Drug']
#     print('================== store3: df_d_new   =================')
#     print(df_d_new.head())
    
#     print('================== store4: df_t_pmid   =================')
#     print(J_Target_pmid_UQ.head())
    
#     print('================== store5: df_d_pmid   =================')
#     print(J_Drug_pmid_UQ.head())
    
#     print('================== store6: cost   =================')
#     print(J_resultUQ_APY_COST.head())
    
    df_t_cost_new = J_resultUQ_APY_COST[J_resultUQ_APY_COST.Search_Type == 'Target_Only']
#     print('================== store7: df_t_cost_new   =================')
#     print(df_t_cost_new.head())
    
    df_d_cost_new = J_resultUQ_APY_COST[J_resultUQ_APY_COST.Search_Type == 'Drug']
#     print('================== store8: df_d_cost_new   =================')
#     print(df_d_cost_new.head())

#     df_t_cost_new = df_cost_new[df_cost_new.Search_Type == 'Target_Only']
#     df_d_cost_new = df_cost_new[df_cost_new.Search_Type == 'Drug']
#     print('================== store9: J_Target_hold   =================')
#     print(J_Target_hold)
#     print('================== store9: J_Drug_hold   =================')
#     print(J_Drug_hold)
    J_Target_hold=J_Target_hold[['PMID']]
    J_Drug_hold=J_Drug_hold[['PMID']]
#     print('================== store9: J_Target_hold   =================')
#     print(J_Target_hold.head())
#     print('================== store9: J_Drug_hold   =================')
#     print(J_Drug_hold.head())
    
    return J_resultUQ_FULL.to_json('json_file/df_json.json', date_format='iso', orient='split'),             df_t_new.to_json('json_file/df_t_json.json',date_format='iso', orient='split'),             df_d_new.to_json('json_file/df_d_json.json', date_format='iso', orient='split'),             J_Target_pmid_UQ.to_json('json_file/df_t_pmid_json.json', date_format='iso', orient='split'),             J_Drug_pmid_UQ.to_json('json_file/df_d_pmid_json.json', date_format='iso', orient='split'),             J_resultUQ_APY_COST.to_json('json_file/df_cost_json.json', date_format='iso', orient='split'),             df_t_cost_new.to_json('json_file/df_t_cost_new.json', date_format='iso', orient='split'),            df_d_cost_new.to_json('json_file/df_d_cost_new.json', date_format='iso', orient='split'),            J_Drug_hold[['PMID']].to_json('json_file/Drug_hold_new.json', date_format='iso', orient='split'),            J_Target_hold[['PMID']].to_json('json_file/Target_hold_new.json', date_format='iso', orient='split')


# 1: full 
# 2: full_t
# 3: full_d
# 4: t_pmid
# 5: d_pmid
# 6: cost
# 7: cost_t
# 8: cost_d
# 9: J_Drug_hold
#10: J_Target_hold


# In[100]:


# tab1 generating new plots 


# In[101]:


@app.callback(Output('blocks', 'children'), [Input('store1', 'data'),Input('store2', 'data'),Input('store3', 'data'),Input('store4','data'),Input('store5', 'data'),Input('store7', 'data'),Input('store8', 'data'),Input('store9', 'data'),Input('store10', 'data')], prevent_initial_call=True)
def update_tab1_blocks(df_new, df_t_new, df_d_new, df_t_pmid_new, df_d_pmid_new, df_t_cost_new, df_d_cost_new,Target_hold_new, Drug_hold_new):

    df_new = pd.read_json('json_file/df_json.json', orient='split')
    df_t_new = pd.read_json('json_file/df_t_json.json', orient='split')
#     print('==================updating blocks: df_t_new   =================')
#     print(df_t_new)
    df_d_new = pd.read_json('json_file/df_d_json.json', orient='split')
    df_t_pmid_new = pd.read_json('json_file/df_t_pmid_json.json', orient='split')
    df_d_pmid_new = pd.read_json('json_file/df_d_pmid_json.json', orient='split')
    df_t_cost_new = pd.read_json('json_file/df_t_cost_new.json', orient='split')
    df_d_cost_new = pd.read_json('json_file/df_d_cost_new.json', orient='split')
    Target_hold_new= pd.read_json('json_file/Target_hold_new.json', orient='split')
    Drug_hold_new= pd.read_json('json_file/Drug_hold_new.json', orient='split')
#     blocks = blocks(df_d_pmid, df_t_pmid, df_t, df_d, df),
    return blocks(df_new, df_t_new, df_d_new, df_t_pmid_new, df_d_pmid_new, df_t_cost_new, df_d_cost_new, Target_hold_new, Drug_hold_new)


# In[102]:


@app.callback(Output('lineplots', 'figure'), [Input('store2', 'data'),Input('store3', 'data')],prevent_initial_call=True)
def update_tab1_lineplot(df_t_new, df_d_new):
    
    df_t_new = pd.read_json('json_file/df_t_json.json', orient='split')
    df_d_new = pd.read_json('json_file/df_d_json.json', orient='split')

    figure = tab1_fig(df_t_new, df_d_new)

    return figure


# In[103]:


# tab1 generating new plots 


# In[104]:


# generate new
@app.callback(Output('top_10_ins_barplot1', 'figure'), Input('store1', 'data'), prevent_initial_call=True)
def update_tab2_barplot1(df_new):
    df_new = pd.read_json('json_file/df_json.json', orient='split')
    figure = tab2_barplot1(df_new)

    return figure


# In[105]:


# generate new
@app.callback(Output('top_10_ins_barplot2', 'figure'), [Input('store1', 'data'),Input('store9', 'data'),Input('store10', 'data')], prevent_initial_call=True)
def update_tab2_barplot2(df_new,Drug_hold_new,Target_hold_new):
    
    df_new = pd.read_json('json_file/df_json.json', orient='split')
    Drug_hold_new= pd.read_json('json_file/Drug_hold_new.json', orient='split')
    Target_hold_new= pd.read_json('json_file/Target_hold_new.json', orient='split')
    
    figure = tab2_barplot2(df_new, Drug_hold_new, Target_hold_new)
    
    return figure


# In[106]:


# generate new
@app.callback(Output('selected_ins_barplot1', 'figure'),[Input('store1', 'data')], prevent_initial_call=True)
def update_2_2_1barplot_new(df_new):
    df_new = pd.read_json('json_file/df_json.json', orient='split')
    figure = tab2_selected_barplot1(df_new)
    
    return figure


# In[107]:


# generate new
@app.callback(Output('selected_ins_barplot2', 'figure'), [Input('store1', 'data')], prevent_initial_call=True)
def update_2_2_2barplot_new(df_new):
    df_new = pd.read_json('json_file/df_json.json', orient='split')
    figure = tab2_selected_barplot2(df_new)
    
    return figure


# In[108]:


# generate new
@app.callback(Output('selected_ins_lineplot1', 'figure'), [Input('store1', 'data')], prevent_initial_call=True)
def update_2_3_lineplot1_new(df_new):
    df_new = pd.read_json('json_file/df_json.json', orient='split')
    figure = tab2_selected_lineplot1(df_new)
    
    return figure


# In[109]:


# generate new
@app.callback(Output('selected_ins_lineplot2',  'figure'), [Input('store1', 'data')], prevent_initial_call=True)
def update_2_3_2lineplot1_new(df_new):
    df_new = pd.read_json('json_file/df_json.json', orient='split')
    figure = tab2_selected_lineplot2(df_new)
    
    return figure


# In[110]:


# tab3 generating new plots 


# In[111]:


@app.callback(Output('tab3_barplots1', 'figure'), Input('store1', 'data'), prevent_initial_call=True)
def update_tab3_barplot1(df_new):
    df_new = pd.read_json('json_file/df_json.json', orient='split')
    figure = tab3_barplot1(df_new)

    return figure


# In[112]:


@app.callback(Output('tab3_barplots2', 'figure'), [Input('store1', 'data'),Input('store9', 'data'),Input('store10', 'data')], prevent_initial_call=True)
def update_tab3_barplot2(df_new, Drug_hold_new, Target_hold_new):
    
    df_new = pd.read_json('json_file/df_json.json', orient='split')
    Drug_hold_new= pd.read_json('json_file/Drug_hold_new.json', orient='split')
    Target_hold_new= pd.read_json('json_file/Target_hold_new.json', orient='split')
    
    figure = tab3_barplot2(df_new, Drug_hold_new, Target_hold_new)

    return figure


# In[113]:


# generate new 
# @app.callback(Output('selected_pro_barplot1', 'figure'),[Input('store1', 'data')], prevent_initial_call=True)
# def update_2_2_1barplot_new(df_new):
#     df_new = pd.read_json('json_file/df_json.json', orient='split')
#     figure = tab2_selected_barplot1(df_new)
    
#     return figure


# In[114]:


# interaction
@app.callback(Output('selected_pro_barplot1', 'figure'),[Input('store1', 'data')], prevent_initial_call=True)
def update_3_2_1barplot_new(df_new):
    df_new = pd.read_json('json_file/df_json.json', orient='split')
    pro__checklist =list(df['Grant_Type_Name'].drop_duplicates())
    pro_checklist_df_total = df[df.Grant_Type_Name.isin(pro__checklist)]
    figure = tab3_selected_barplot1(pro_checklist_df_total)
    
    return figure


# In[115]:


@app.callback(Output('selected_pro_barplot2', 'figure'),[Input('store1', 'data')], prevent_initial_call=True)
def update_3_2_2barplot_new(df_new):
    df_new = pd.read_json('json_file/df_json.json', orient='split')
    pro__checklist =list(df['Grant_Type_Name'].drop_duplicates())
    pro_checklist_df_total = df[df.Grant_Type_Name.isin(pro__checklist)]
    figure = tab3_selected_barplot2(pro_checklist_df_total)
    
    return figure


# In[116]:


@app.callback(Output('selected_pro_lineplot1', 'figure'),[Input('store1', 'data')], prevent_initial_call=True)
def update_3_2_1lineplot_new(df_new):
    df_new = pd.read_json('json_file/df_json.json', orient='split')
    pro__checklist =list(df['Grant_Type_Name'].drop_duplicates())
    pro_checklist_df_total = df[df.Grant_Type_Name.isin(pro__checklist)]
    figure = tab3_selected_lineplot1(pro_checklist_df_total)
    
    return figure


# In[117]:


@app.callback(Output('selected_pro_lineplot2', 'figure'),[Input('store1', 'data')], prevent_initial_call=True)
def update_3_2_2lineplot_new(df_new):
    df_new = pd.read_json('json_file/df_json.json', orient='split')
    pro__checklist =list(df['Grant_Type_Name'].drop_duplicates())
    pro_checklist_df_total = df[df.Grant_Type_Name.isin(pro__checklist)]
    figure = tab3_selected_lineplot2(pro_checklist_df_total)
    
    return figure


# In[ ]:





# In[ ]:





# In[ ]:





# In[118]:


from dash import dcc


# In[119]:


@app.callback(
    Output("download-file", "data"),
    Input("btn_csv", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    df_new = pd.read_json('json_file/df_json.json', orient='split')
    return dcc.send_data_frame(df_new.to_csv, "mydf.csv", index = None)


# In[120]:


########## data unload ################

J_resultUQ_FULL=1
J_Target_hold=1
J_Drug_hold=1
J_Target_pmid_UQ=1
J_Drug_pmid_UQ=1
J_resultUQ_APY_COST=1


# In[ ]:


server = app.server

# Run the server
if __name__ == "__main__":
    app.run_server(debug=False, host = "0.0.0.0")


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




