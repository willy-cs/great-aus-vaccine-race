#!/usr/bin/env python

import streamlit as st
import pandas as pd
import numpy as np
import datetime
import sys
import os
import compare
import data
import chart

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

def main():
    st.header("Welcome to the Great Australian COVID-19 Vaccine Race!")

    (overall_state_df, overall_ag_df, sag_df) = data.update_data()
    # overall_state_df = st.cache(pd.read_parquet)('overall_state_df.parquet')
    # overall_ag_df = st.cache(pd.read_parquet)('overall_ag_df.parquet')
    # sag_df = st.cache(pd.read_parquet)('sag_df.parquet')

    list_states = list(sorted(overall_state_df['state'].unique()))
    list_age_group = list(sorted(sag_df['age_group'].unique()))
    list_vac_status = [0,1,2]

    with st.form('user_form'):
        st.subheader("Choose your team")
        u_state = st.selectbox('Where do you live?', list_states)
        u_age_group = st.selectbox('What is your age group?', list_age_group)
        u_vac = st.selectbox('How many vaccine shots have you had?', list_vac_status)
        hl_graph = st.selectbox('Highlight your team performance?', [True, False])

        submitted = st.form_submit_button('Race on!')

    if not submitted:
        return

    user = compare.User(u_state, u_age_group, u_vac)
    latest_date = pd.to_datetime(overall_state_df['date'].max()).date()

    st.text("Your team is: {}".format(user))

    st.subheader('Here is how your team is doing so far in the vaccine race')
    st.subheader('Data last updated: {}'.format(pd.to_datetime(overall_state_df['date'].max()).date()))

    st.markdown("### *You and your state*")
    long_com, short_com = compare.state_comparison(user, overall_state_df)

    state_df=overall_state_df.query('state==@user.state')
    # 1. state vaccination status
    st.markdown("> {}".format(short_com['state_vac_status']))
    st.plotly_chart(chart.vac_status_dist_chart(state_df, user, hl=hl_graph), use_container_width=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        # 2. state vaccination rate
        st.markdown("> {}".format(short_com['state_vac_rate']))
        st.plotly_chart(chart.pp_chart(overall_state_df, user,
                                        col='vac_rate',
                                        col_label='vaccination rate',
                                        grouping='state',
                                        hl=hl_graph), use_container_width=True)
    with col2:
        # 3. state dose1
        st.markdown("> {}".format(short_com['state_dose1']))
        st.plotly_chart(chart.pp_chart(overall_state_df, user,
                                        col='dose1_pct',
                                        col_label='1st dose pct',
                                        grouping='state',
                                        hl=hl_graph), use_container_width=True)

    with col3:
        # 4. state dose2
        st.markdown("> {}".format(short_com['state_dose2']))
        st.plotly_chart(chart.pp_chart(overall_state_df, user,
                                        col='dose2_pct',
                                        col_label='2nd dose pct',
                                        grouping='state',
                                        hl=hl_graph), use_container_width=True)

    # 5. eta race
    # st.markdown("> {}".format(short_com['state_dose2']))
    eta_df = compare.construct_eta_data(overall_state_df, 'state', user)
    st.plotly_chart(chart.eta_chart(eta_df, group_col='state',
                                    user=user,
                                    hl=hl_graph,
                                    annot=True), use_container_width=True)


    st.markdown("### *You and your age group*")
    short_com = compare.ag_comparison(user, overall_ag_df)
    ag_df=overall_ag_df.query('age_group==@user.age_group')

    # 1. age group vaccination status
    st.markdown("> {}".format(short_com['ag_vac_status']))
    st.plotly_chart(chart.vac_status_dist_chart(ag_df, user, hl=hl_graph), use_container_width=True)

    # 2. age group vaccination rate
    st.markdown("> {}".format(short_com['ag_vac_rate']))
    st.plotly_chart(chart.pp_chart(overall_ag_df, user,
                                    col='vac_rate',
                                    col_label='vaccination rate',
                                    grouping='age_group',
                                    hl=hl_graph), use_container_width=True)
    # 3. age group dose1
    st.markdown("> {}".format(short_com['ag_dose1']))
    st.plotly_chart(chart.pp_chart(overall_ag_df, user,
                                    col='dose1_pct',
                                    col_label='1st dose pct',
                                    grouping='age_group',
                                    hl=hl_graph), use_container_width=True)
    # 4. age group dose2
    st.markdown("> {}".format(short_com['ag_dose2']))
    st.plotly_chart(chart.pp_chart(overall_ag_df, user,
                                    col='dose2_pct',
                                    col_label='2nd dose pct',
                                    grouping='age_group',
                                    hl=hl_graph), use_container_width=True)

    # 5. eta race
    eta_df = compare.construct_eta_data(overall_ag_df, 'age_group', user)
    st.plotly_chart(chart.eta_chart(eta_df, group_col='age_group',
                                    user=user,
                                    hl=hl_graph,
                                    annot=False), use_container_width=True)
    #################

    st.markdown("### *Your age group vs other age group within your state*")
    long_com, short_com = compare.state_age_group_comparison(user, sag_df)
    comp_sag_df=sag_df.query('state==@user.state & age_group==@user.age_group')
    comp_s_df=sag_df.query('state==@user.state')
    comp_ag_df=sag_df.query('age_group==@user.age_group')

    # 1. sag vaccination status
    st.markdown("> {}".format(short_com['sag_in_vac_status']))
    st.plotly_chart(chart.vac_status_dist_chart(comp_sag_df, user, hl=hl_graph), use_container_width=True)

    # 2. sag in vaccination rate
    st.markdown("> {}".format(short_com['sag_in_vac_rate']))
    st.plotly_chart(chart.pp_chart(comp_s_df, user,
                                    col='vac_rate',
                                    col_label='vaccination rate',
                                    grouping='age_group',
                                    hl=hl_graph), use_container_width=True)
    # 3. sag in dose1
    st.markdown("> {}".format(short_com['sag_in_dose1']))
    st.plotly_chart(chart.pp_chart(overall_ag_df, user,
                                    col='dose1_pct',
                                    col_label='1st dose pct',
                                    grouping='age_group',
                                    hl=hl_graph), use_container_width=True)

    # 4. sag in dose2
    st.markdown("> {}".format(short_com['sag_in_dose2']))
    st.plotly_chart(chart.pp_chart(overall_ag_df, user,
                                    col='dose2_pct',
                                    col_label='2nd dose pct',
                                    grouping='age_group',
                                    hl=hl_graph), use_container_width=True)

    ############

    st.markdown("### *On {}, [{}] in {} is ...*".format(latest_date, user.age_group, user.state))
    # 1. sag out vaccination rate
    st.markdown("> {}".format(short_com['sag_out_vac_rate']))
    st.plotly_chart(chart.pp_chart(comp_ag_df, user,
                                    col='vac_rate',
                                    col_label='vaccination rate',
                                    grouping='state',
                                    hl=hl_graph), use_container_width=True)

    # 2. sag out dose1
    st.markdown("> {}".format(short_com['sag_out_dose1']))
    st.plotly_chart(chart.pp_chart(comp_ag_df, user,
                                    col='dose1_pct',
                                    col_label='1st dose pct',
                                    grouping='state',
                                    hl=hl_graph), use_container_width=True)

    # 3. sag out dose2
    st.markdown("> {}".format(short_com['sag_out_dose2']))
    st.plotly_chart(chart.pp_chart(comp_ag_df, user,
                                    col='dose2_pct',
                                    col_label='2nd dose pct',
                                    grouping='state',
                                    hl=hl_graph), use_container_width=True)



    st.subheader('Notes')
    st.markdown('1. Prediction on reaching 70 or 80% fully vaccinated status is based on 7-day moving average. This will be updated daily.')
    st.markdown('2. My source data is from https://github.com/jxeeno/aust-govt-covid19-vaccine-pdf. I might have modified the data to correct any mistakes or errors I perceive or notice.')
    st.markdown('3. This page does not aim or claim to be authoritative of vaccine data roll out. I do not guarantee its accuracy. Use at your own risk, and I take no responsibility of any loss that might have occurred.')





if __name__ == "__main__":
    main()
