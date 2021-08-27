#!/usr/bin/env python

import pandas as pd
import numpy as np
import datetime
import sys
import os
import streamlit as st

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

def get_data():
    data_url = "https://vaccinedata.covid19nearme.com.au/data/air_residence.csv"
    df = pd.read_csv(data_url)
    df.at[3497, 'AIR_RESIDENCE_SECOND_DOSE_COUNT'] = 475180
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
    df.columns = df.columns.str.lower()
    df['date'] = pd.to_datetime(df['date'])

    return df

def age_grouping(df):
    df['age_group'] = df['age_lower'].astype(str) + '-' + df['age_upper'].astype(str)

    m = df['age_group'] != "0-999"
    df['age_group'].where(m, "0_or_above", inplace = True)
    m = df['age_group'] != "16-999"
    df['age_group'].where(m, "16_or_above", inplace = True)
    m = df['age_group'] != "50-999"
    df['age_group'].where(m, "50_or_above", inplace = True)
    m = df['age_group'] != "70-999"
    df['age_group'].where(m, "70_or_above", inplace = True)

    return df

def extra_calculation(a):
    # Grouped extra calculation
    a.sort_values('date', ascending = True, inplace=True)
    a['delta_dose1'] = a['dose1_cnt'].diff()
    a['delta_dose2'] = a['dose2_cnt'].diff()
    a['delta_dose12'] = a['delta_dose1'] + a['delta_dose2']
    a['vac_rate'] = round(a['delta_dose12'] / a['abspop_jun2020'] * 100, 2)
    a['vac_rate'] = a['vac_rate'].clip(0)


    # modified delta, cap the minus values in delta into 0.
    # this is to handle days where for some reason or another the delta count is negative (i.e. there are less people getting vaccinated compared to the day before, probably due to data error
    # or change in data entry policy, e.g. classifying 96% to >95% -- see data notes in README
    a['delta_dose1_mod'] = a['delta_dose1'].clip(0)
    a['delta_dose2_mod'] = a['delta_dose2'].clip(0)
    # replacing 0 in moving average with small values to make sure we're not predicting infinity
    a['ma7_dose1'] = a['delta_dose1_mod'].rolling(7).mean().replace(0, 0.001)
    a['ma7_dose2'] = a['delta_dose2_mod'].rolling(7).mean().replace(0, 0.001)
    a['unvac'] = a['abspop_jun2020'] - a['dose1_cnt']
    a['unvac_pct'] = round(a['unvac']/a['abspop_jun2020'] *100, 2)

    # eta to hit double-vaxx at 70 and 80% rate using MA calculation
    a['eta_dose2_70'] = (0.7 * a['abspop_jun2020'] - a['dose2_cnt']) / a['ma7_dose2']
    a['eta_dose2_80'] = (0.8 * a['abspop_jun2020'] - a['dose2_cnt']) / a['ma7_dose2']

    return a

def save_data(df):
    overall_state_df = df[df['age_group'].str.endswith('_or_above')].copy(deep = True)
    overall_ag_df = df[~df['age_group'].str.endswith('_or_above')].copy(deep = True)
    sag_df = df[~df['age_group'].str.endswith('_or_above')].copy(deep = True)

    # further preprocessing for overall_state_df
    overall_state_df.drop(columns=['dose1_cnt', 'dose2_cnt'], inplace=True)
    overall_state_df.rename(columns={'first_dose_count': 'dose1_cnt',
                                     'second_dose_count': 'dose2_cnt'}, inplace=True)
    overall_state_df = overall_state_df.query('age_group == "16_or_above"')
    overall_state_df = overall_state_df.groupby('state').apply(lambda d: extra_calculation(d))

    # further preprocessing for overall_ag_df
    overall_ag_df.drop(columns = ['first_dose_count', 'second_dose_count'], inplace = True)
    overall_ag_df = overall_ag_df.groupby(['date', 'age_group'])[['dose1_cnt', 'dose2_cnt', 'abspop_jun2020']].sum().reset_index()
    overall_ag_df['dose1_pct'] = round(100 * overall_ag_df['dose1_cnt']/ overall_ag_df['abspop_jun2020'], 3)
    overall_ag_df['dose2_pct'] = round(100 * overall_ag_df['dose2_cnt']/ overall_ag_df['abspop_jun2020'], 3)
    overall_ag_df = overall_ag_df.groupby('age_group').apply(lambda d: extra_calculation(d))

    # further preprocessing for sag_df
    sag_df.drop(columns = ['first_dose_count', 'second_dose_count'], inplace = True)
    sag_df = sag_df.groupby(['state', 'age_group']).apply(lambda d: extra_calculation(d))

    # overall_state_df.to_parquet('overall_state_df.parquet')
    # overall_ag_df.to_parquet('overall_ag_df.parquet')
    # sag_df.to_parquet('sag_df.parquet')

    return (overall_state_df, overall_ag_df, sag_df)

@st.cache(suppress_st_warning=True, ttl=600)
def update_data():
    df = get_data()
    df = age_grouping(df)
    return save_data(df)

if __name__ == '__main__':
    df = get_data()
    df = age_grouping(df)
    save_data(df)
