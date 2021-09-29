#!/usr/bin/env python

import pandas as pd
import numpy as np
import datetime
import sys
import os
import streamlit as st
import config

import matplotlib.pyplot as plt

from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = "all"

pd.set_option("display.max_columns", 500)
pd.set_option("display.max_rows", 100)
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', None)
pd.set_option('display.float_format', lambda x: '%.3f' % x)
pd.set_option('max_columns', None)
pd.options.mode.chained_assignment = None  # default='warn'

np.set_printoptions(suppress=True)

@st.cache(suppress_st_warning=True, ttl=600)
def get_data():
    data_url = "https://vaccinedata.covid19nearme.com.au/data/air_residence.csv"
    df = pd.read_csv(data_url)
    df.at[3497, 'AIR_RESIDENCE_SECOND_DOSE_PCT'] = 24.41 # according to ABC
    df.at[3497, 'AIR_RESIDENCE_SECOND_DOSE_COUNT'] = 516266
    df = df.query('VALIDATED == "Y"')
    df.drop(columns = ['URL', 'VALIDATED'], inplace = True)
    cols= {'DATE_AS_AT' : 'DATE',
           'AIR_RESIDENCE_FIRST_DOSE_PCT' : 'DOSE1_PCT',
           'AIR_RESIDENCE_SECOND_DOSE_PCT' : 'DOSE2_PCT',
           'AIR_RESIDENCE_FIRST_DOSE_COUNT' : 'FIRST_DOSE_COUNT',
           'AIR_RESIDENCE_SECOND_DOSE_COUNT' : 'SECOND_DOSE_COUNT',
           'AIR_RESIDENCE_FIRST_DOSE_APPROX_COUNT' : 'DOSE1_CNT',
           'AIR_RESIDENCE_SECOND_DOSE_APPROX_COUNT' : 'DOSE2_CNT',
           'ABS_ERP_JUN_2020_POP' : 'ABSPOP_JUN2020'
          }

    df.rename(columns = cols, inplace = True)
    df['FIRST_DOSE_COUNT']=df['FIRST_DOSE_COUNT'].fillna(0).astype(int)
    df['SECOND_DOSE_COUNT']=df['SECOND_DOSE_COUNT'].fillna(0).astype(int)
    df['DOSE1_CNT']=df['DOSE1_CNT'].fillna(0).astype(int)
    df['DOSE2_CNT']=df['DOSE2_CNT'].fillna(0).astype(int)
    df['DOSE1_CNT']=df[['DOSE1_CNT', 'FIRST_DOSE_COUNT']].max(axis=1)
    df['DOSE2_CNT']=df[['DOSE2_CNT', 'SECOND_DOSE_COUNT']].max(axis=1)
    df.drop(columns=['FIRST_DOSE_COUNT', 'SECOND_DOSE_COUNT'], inplace=True)
    df.columns = df.columns.str.lower()
    df['date'] = pd.to_datetime(df['date'])
    aus_df=get_national_data()
    twelveplus_df=create_12plus_data(df, aus_df)
    df=pd.concat([df,aus_df,twelveplus_df], ignore_index=True)
    df['state'] = pd.Categorical(df['state'], config.states_rank)
    df['dose1_cnt'] = df['dose1_cnt'].astype(int)
    df['dose2_cnt'] = df['dose2_cnt'].astype(int)
    df['abspop_jun2020'] = df['abspop_jun2020'].astype(int)
    df=df.sort_values(['date', 'state', 'age_lower'], ascending=True)
    # The day where we have data for each individual states
    df=df.query('date > "27-07-2021"')

    return df

def create_12plus_data(df, aus_df):
    ### data from gov separates between 12-15 and 16+
    ### We want to merge them here
    ### Generate 12_or_above age group
    new_df = pd.DataFrame()
    for x in [df, aus_df]:
        new_12plus_df = x.query('(age_lower == 12 & age_upper == 15) | (age_lower == 16 & age_upper == 999)').groupby(['date', 'state'])[['dose1_cnt', 'dose2_cnt', 'abspop_jun2020']].sum().reset_index()
        new_12plus_df['age_lower'] = 12
        new_12plus_df['age_upper'] = 999
        # so for older dates, the population for 12-15 would be empty, as we don't have the data for it
        #   and as we aggregate by summing them, then the population will only consist of 16+
        # we're just going to overwrite those population with the 'max', which will sum up 12-15 and 16+
        new_12plus_df['abspop_jun2020']=new_12plus_df.groupby('state')['abspop_jun2020'].transform('max')
        new_12plus_df['dose1_pct'] = round(new_12plus_df['dose1_cnt'] / new_12plus_df['abspop_jun2020'] * 100, 2)
        new_12plus_df['dose2_pct'] = round(new_12plus_df['dose2_cnt'] / new_12plus_df['abspop_jun2020'] * 100, 2)
        new_df = pd.concat([new_df, new_12plus_df])

    return new_df

def get_national_data():
    data_url = "https://vaccinedata.covid19nearme.com.au/data/air.csv"
    df = pd.read_csv(data_url)
    national_pop_df = pd.read_csv('national_pop.csv')
    age_prefix=['AIR_12_15_', 'AIR_AUS_16_PLUS_', 'AIR_AUS_50_PLUS_', 'AIR_AUS_70_PLUS_', 'AIR_95_PLUS_']
    attr_suffix=['FIRST_DOSE_PCT', 'SECOND_DOSE_PCT', 'FIRST_DOSE_COUNT', 'SECOND_DOSE_COUNT', 'POPULATION']
    rename_cols = ['date', 'dose1_pct', 'dose2_pct', 'dose1_cnt', 'dose2_cnt', 'abspop_jun2020', 'age_lower', 'age_upper']
    adf=pd.DataFrame()
    for p in age_prefix:
        sub_df=pd.DataFrame()
        cols=['DATE_AS_AT'] + [p+s for s in attr_suffix]
        if p=="AIR_95_PLUS_":
            cols=cols[:-1] # 95 plus doesn't have population information
            sub_df = df[cols]
            sub_df['POPULATION'] = 52912
            sub_df['AGE_LOWER'] = 95
            sub_df['AGE_UPPER'] = 999
        elif p=="AIR_12_15_":
            cols=cols[:-1] # 12-15 doesn't have population information
            sub_df = df[cols]
            sub_df['POPULATION'] = 1243990
            sub_df['AGE_LOWER'] = 12
            sub_df['AGE_UPPER'] = 15
        else:
            sub_df = df[cols]
            sub_df['AGE_LOWER'] = int(p.split('_')[2])
            sub_df['AGE_UPPER'] = 999

        sub_df.columns = rename_cols
        adf=pd.concat([adf, sub_df])

    # special cases for 5 year ranges
    attr_suffix=['FIRST_DOSE_PCT', 'SECOND_DOSE_PCT', 'FIRST_DOSE_COUNT', 'SECOND_DOSE_COUNT']
    for i in [16] + list(range(20,95,5)):
        lower=i
        upper=i+4 if i != 16 else 19
        ar=str(lower) + "-"+ str(upper)
        col='AIR_{}_{}_'.format(lower,upper)
        cols=['DATE_AS_AT'] + [col+s for s in attr_suffix]
        sub_df = df[cols]
        sub_df['POPULATION'] = national_pop_df.query('age_range==@ar')['pop'].iloc[0]
        sub_df['AGE_LOWER'] = lower
        sub_df['AGE_UPPER'] = upper
        sub_df.columns = rename_cols
        adf=pd.concat([adf, sub_df])

    adf['state'] = 'AUS'
    adf['date'] = pd.to_datetime(adf['date'])

    adf=adf.dropna()
    return adf

def age_grouping(df, age_group_10_flag):
    df['age_group'] = df['age_lower'].astype(str) + '-' + df['age_upper'].astype(str)
    if age_group_10_flag:
        df = age_grouping_10y(df)

    m = df['age_group'] != "0-999"
    df['age_group'].where(m, "0_or_above", inplace = True)
    m = df['age_group'] != "12-999"
    df['age_group'].where(m, "12_or_above", inplace = True)
    m = df['age_group'] != "16-999"
    df['age_group'].where(m, "16_or_above", inplace = True)
    m = df['age_group'] != "50-999"
    df['age_group'].where(m, "50_or_above", inplace = True)
    m = df['age_group'] != "70-999"
    df['age_group'].where(m, "70_or_above", inplace = True)

    return df

def age_grouping_10y(df):
    """
    Group the data into alternate age groups
    Before going further, we need to aggregate data within these new groups
    """

    df['age_group'] = np.where(df['age_group'].isin(['16-19', '20-24', '25-29']), '16-29',
                        np.where(df['age_group'].isin(['30-34', '35-39']), '30-39',
                        np.where(df['age_group'].isin(['40-44', '45-49']), '40-49',
                        np.where(df['age_group'].isin(['50-54', '55-59']), '50-59',
                        np.where(df['age_group'].isin(['60-64', '65-69']), '60-69',
                        np.where(df['age_group'].isin(['70-74', '75-79']), '70-79',
                        np.where(df['age_group'].isin(['80-84', '85-89']), '80+',
                        np.where(df['age_group'].isin(['90-94', '95-999']), '80+', df['age_group']))))))))

    df=df.groupby(['date', 'state', 'age_group'])[['dose1_cnt', 'dose2_cnt', 'abspop_jun2020']].agg(sum).reset_index()

    return df

def extra_calculation(a):
    # Grouped extra calculation
    a.sort_values('date', ascending = True, inplace=True)
    a['delta_dose1'] = a['dose1_cnt'].diff()
    a['delta_dose2'] = a['dose2_cnt'].diff()
    a['delta_dose1_7d'] = a['dose1_cnt'].diff(7)
    a['delta_dose2_7d'] = a['dose2_cnt'].diff(7)
    a['delta_dose1_30d'] = a['dose1_cnt'].diff(30)
    a['delta_dose2_30d'] = a['dose2_cnt'].diff(30)
    a['delta_dose12'] = a['delta_dose1'] + a['delta_dose2']
    a['vac_rate'] = round(a['delta_dose12'] / a['abspop_jun2020'] * 100, 2)
    a['vac_rate'] = a['vac_rate'].clip(0)
    a['ma7_vac_rate'] = round(a['vac_rate'].rolling(7).mean().replace(0, 0.01), 2)


    # modified delta, cap the minus values in delta into 0.
    # this is to handle days where for some reason or another the delta count is negative (i.e. there are less people getting vaccinated compared to the day before, probably due to data error
    # or change in data entry policy, e.g. classifying 96% to >95% -- see data notes in README
    a['delta_dose1_mod'] = a['delta_dose1'].clip(0)
    a['delta_dose2_mod'] = a['delta_dose2'].clip(0)
    a['delta_dose12_mod'] = a['delta_dose1_mod'] + a['delta_dose2_mod']
    a['dose1_prop'] = round(a['delta_dose1_mod'] / a['delta_dose12_mod'] * 100, 2)
    a['dose2_prop'] = round(a['delta_dose2_mod'] / a['delta_dose12_mod'] * 100, 2)
    # replacing 0 in moving average with small values to make sure we're not predicting infinity
    a['ma7_dose1'] = a['delta_dose1_mod'].rolling(7).mean().replace(0, 0.01)
    a['ma7_dose2'] = a['delta_dose2_mod'].rolling(7).mean().replace(0, 0.01)
    a['unvac'] = a['abspop_jun2020'] - a['dose1_cnt']
    a['unvac_pct'] = round(a['unvac']/a['abspop_jun2020'] *100, 2)

    # eta to hit double-vaxx at 70 and 80% rate using MA calculation
    a['eta_dose2_70'] = (0.7 * a['abspop_jun2020'] - a['dose2_cnt']) / a['ma7_dose2']
    a['eta_dose2_80'] = (0.8 * a['abspop_jun2020'] - a['dose2_cnt']) / a['ma7_dose2']


    a['vac_rate_dose1'] = round(a['delta_dose1'] / a['abspop_jun2020'] * 100, 2)
    a['vac_rate_dose1'] = a['vac_rate_dose1'].clip(0)
    a['ma7_dose1_vac_rate'] = round(a['vac_rate_dose1'].rolling(7).mean().replace(0, 0.001), 2)

    a['vac_rate_dose2'] = round(a['delta_dose2'] / a['abspop_jun2020'] * 100, 2)
    a['vac_rate_dose2'] = a['vac_rate_dose2'].clip(0)
    a['ma7_dose2_vac_rate'] = round(a['vac_rate_dose2'].rolling(7).mean().replace(0, 0.001), 2)

    a['eta_dose1_70'] = (0.7 * a['abspop_jun2020'] - a['dose1_cnt']) / a['ma7_dose1']
    a['eta_dose1_80'] = (0.8 * a['abspop_jun2020'] - a['dose1_cnt']) / a['ma7_dose1']

    return a

# @st.cache(suppress_st_warning=True, ttl=600)
def save_data(df):
    overall_state_df = df[df['age_group'].str.endswith('_or_above')].copy(deep = True)
    overall_ag_df = df[~df['age_group'].str.endswith('_or_above')].copy(deep = True)
    sag_df = df[~df['age_group'].str.endswith('_or_above')].copy(deep = True)

    # further preprocessing for overall_state_df
    overall_state_df['dose1_pct'] = round(100 * overall_state_df['dose1_cnt']/ overall_state_df['abspop_jun2020'], 2)
    overall_state_df['dose2_pct'] = round(100 * overall_state_df['dose2_cnt']/ overall_state_df['abspop_jun2020'], 2)
    overall_state_df = overall_state_df.query('age_group == "16_or_above" | age_group == "12_or_above"')
    overall_state_df = overall_state_df.groupby(['age_group', 'state']).apply(lambda d: extra_calculation(d))

    # further preprocessing for overall_ag_df
    overall_ag_df = overall_ag_df.query('state == "AUS"')
    overall_ag_df['dose1_pct'] = round(100 * overall_ag_df['dose1_cnt']/ overall_ag_df['abspop_jun2020'], 3)
    overall_ag_df['dose2_pct'] = round(100 * overall_ag_df['dose2_cnt']/ overall_ag_df['abspop_jun2020'], 3)
    overall_ag_df = overall_ag_df.groupby('age_group').apply(lambda d: extra_calculation(d))

    # further preprocessing for sag_df
    sag_df = sag_df.groupby(['state', 'age_group']).apply(lambda d: extra_calculation(d))
    sag_df['dose1_pct'] = round(100 * sag_df['dose1_cnt']/ sag_df['abspop_jun2020'], 2)
    sag_df['dose2_pct'] = round(100 * sag_df['dose2_cnt']/ sag_df['abspop_jun2020'], 2)
    sag_df.sort_values(['date', 'state', 'age_group'], ascending=[True, True, True], inplace=True)

    overall_state_df.to_csv('sample_overall_state_df-20210926.csv', index=False)
    overall_ag_df.to_csv('sample_overall_ag_df-20210926.csv', index=False)
    sag_df.to_csv('sample_sag_df-20210926.csv', index=False)

    return (overall_state_df, overall_ag_df, sag_df)

@st.cache(suppress_st_warning=True, ttl=600)
def update_data():
    df = get_data()
    df = age_grouping(df)
    return save_data(df)

def find_age_group(df, age):
    age_groups = df['age_group'].to_list()

    for i in age_groups:
        upper_age = '999'
        if '+' in i:
            lower_age = i.split('+')[0]
        else:
            lower_age, upper_age = i.split('-')

        if int(age) >= int(lower_age) and int(age) <= int(upper_age):
            return i

    # default returning to the largest group
    return i


if __name__ == '__main__':
    df = get_data()
    aus_df=get_national_data()
    adf = age_grouping(df, True)
    a,b,c = save_data(adf)
