#!/usr/bin/env python

import streamlit as st
import pandas as pd
import numpy as np
import datetime
import sys
import os
import compare
import data

import matplotlib.pyplot as plt
import plotly.express as px

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

st.set_page_config(page_title='It is a race!', layout='wide')

if __name__ == "__main__":
    st.header("Welcome to the Great Australian COVID-19 Vaccine Race!")

    (overall_state_df, sag_df) = data.update_data()
    # overall_state_df = st.cache(pd.read_parquet)('overall_state_df.parquet')
    # sag_df = st.cache(pd.read_parquet)('sag_df.parquet')

    st.subheader("Choose your team")

    list_states = list(sorted(overall_state_df['state'].unique()))
    list_age_group = list(sorted(sag_df['age_group'].unique()))
    list_vac_status = [0,1,2]

    u_state = st.selectbox('Where do you live?', list_states)
    u_age_group = st.selectbox('What is your age group?', list_age_group)
    u_vac = st.selectbox('How many vaccine shots have you had?', list_vac_status)

    user = compare.User(u_state, u_age_group, u_vac)

    st.text("Your team is: {}".format(user))

    st.subheader('Here is how your team is doing so far in the vaccine race (last updated: {})'.format(pd.to_datetime(overall_state_df['date'].max()).date()))

    st.text("You and your state")

    st.text("{}".format(compare.state_comparison(user, overall_state_df)))

    st.text("You and your age group")

    st.text("{}".format(compare.user_age_group_comparison(user, sag_df)))


    #################
    # this one works
    # st.line_chart(overall_state_df.query('state== @user.state') \
    #         .set_index('date')[['unvac_pct', 'dose1_pct', 'dose2_pct']])

    vac_status_dist_chart = px.line(overall_state_df.query('state== @user.state'),\
                            x='date',  y=['dose1_pct','dose2_pct','unvac_pct'])
    vac_status_dist_chart.update_traces({'line' : {'color': 'lightgrey'}})
    vac_status_dist_chart.update_traces(patch={'line' : {'color': 'blue'}}, selector={'legendgroup': 'dose2_pct'})
    st.plotly_chart(vac_status_dist_chart, use_container_width=True)

    vac_rate_chart = px.line(overall_state_df, x='date', y='vac_rate', color = 'state')
    vac_rate_chart.update_traces({'line' : {'color': 'lightgrey'}})
    vac_rate_chart.update_traces(patch={'line' : {'color': 'blue'}}, selector={'legendgroup': user.state})
    st.plotly_chart(vac_rate_chart, use_container_width=True)

    dose1_pp_chart = px.line(overall_state_df, x='date', y='dose1_pct', color = 'state')
    st.plotly_chart(dose1_pp_chart, use_container_width=True)

    dose2_pp_chart = px.line(overall_state_df, x='date', y='dose2_pct', color = 'state')
    st.plotly_chart(dose2_pp_chart, use_container_width=True)

    ############

    ag_in_vac_status_dist_chart = px.line(sag_df.query('state==@user.state & age_group==@user.age_group'),\
                            x='date',  y=['dose1_pct','dose2_pct','unvac_pct'])
    st.plotly_chart(ag_in_vac_status_dist_chart, use_container_width=True)


    ag_in_vac_rate_chart = px.line(sag_df.query('state==@user.state'),\
                            x='date',  y='vac_rate', color='age_group')
    st.plotly_chart(ag_in_vac_rate_chart, use_container_width=True)

    ag_in_dose1_pp_chart= px.line(sag_df.query('state==@user.state'),\
                            x='date',  y='dose1_pct', color='age_group')
    st.plotly_chart(ag_in_dose1_pp_chart, use_container_width=True)

    ag_in_dose2_pp_chart= px.line(sag_df.query('state==@user.state'),\
                            x='date',  y='dose2_pct', color='age_group')
    st.plotly_chart(ag_in_dose2_pp_chart, use_container_width=True)

    ############

    ag_out_vac_rate_chart = px.line(sag_df.query('age_group==@user.age_group'),\
                            x='date',  y='vac_rate', color='state')
    st.plotly_chart(ag_out_vac_rate_chart, use_container_width=True)


    ag_out_dose1_pp_chart = px.line(sag_df.query('age_group==@user.age_group'),\
                            x='date',  y='dose1_pct', color='state')
    st.plotly_chart(ag_out_dose1_pp_chart, use_container_width=True)

    ag_out_dose2_pp_chart = px.line(sag_df.query('age_group==@user.age_group'),\
                            x='date',  y='dose2_pct', color='state')
    st.plotly_chart(ag_out_dose1_pp_chart, use_container_width=True)


    st.subheader('Notes')
    st.markdown('1. Prediction on reaching 70 or 80% fully vaccinated status is based on 7-day moving average')
    st.markdown('2. My source data is from https://github.com/jxeeno/aust-govt-covid19-vaccine-pdf. I might have modified the data to correct any mistakes or errors I perceive or notice')
    st.markdown('3. This page does not aim or claim to be authoritative of vaccine data roll out. I do not guarantee its accuracy. Use at your own risk, and I take no responsibility of any loss that might have occurred.')



