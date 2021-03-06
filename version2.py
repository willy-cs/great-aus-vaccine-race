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
import config

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

    cached_df = data.get_data()
    df = cached_df.copy(deep = True)
    age_group_10_flag = True
    df = data.age_grouping(df, age_group_10_flag)
    (overall_state_df, overall_ag_df, sag_df) = data.save_data(df)
    list_states = config.states_rank
    list_age_group = list(sorted(overall_ag_df['age_group'].unique()))

    ############ JURISDICTION CHARTS ####################
    px_settings={'label_value':'',
                 'facet':'',
                 'facet_col_wrap':4,
                 'range_y':None,
            }
    figs =[]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        opt_aa=st.selectbox('Show me charts of', list(config.analysis_options.keys()))

        px_settings['y'] = [i[0] for i in config.analysis_options[opt_aa]]
        px_settings['label_value'] = config.analysis_options[opt_aa][0][1]
        if opt_aa == "Vaccination Status":
            px_settings['range_y'] = [0,100]

    with col2:
        opt_aj=st.selectbox('in ', list_states)

    with col3:
        group_options=config.grouping_options
        if opt_aj != "AUS":
            group_options=config.age_group_only

        opt_as=st.selectbox('across', group_options)

        if opt_as == "Jurisdictions":
            plotly_df = overall_state_df
            px_settings['facet'] = px_settings['color'] = 'state'
            px_settings['facet_col_wrap'] = 9
        elif opt_as == "Age Groups":
            plotly_df = overall_ag_df
            if opt_aj != "AUS":
                plotly_df = sag_df.query('state == @opt_aj')
            px_settings['facet'] = px_settings['color'] = 'age_group'
            px_settings['facet_col_wrap'] = 9
    with col4:
        select_options={'group' : opt_as[:-1].lower(),
                        'measure' : opt_aa.lower()
                        }
        opt_ac=st.selectbox('with each graph is a', config.chart_options,
                            format_func=lambda x: select_options.get(x))

        if opt_ac == "group":
            fig=chart.facet_chart(plotly_df, **px_settings)
            figs.append(fig)
        elif opt_ac == "measure":
            for px_info in config.analysis_options[opt_aa]:
                (px_settings['y'], px_settings['y_label'], px_settings['graph_title']) = px_info
                fig=chart.line_chart(plotly_df, **px_settings)
                figs.append(fig)

    if len(figs) > 1:
        for col, fig in zip(st.columns(len(figs)), figs):
            with col:
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.plotly_chart(fig, use_container_width=True)
    ############ JURISDICTION CHARTS ####################

    ############ AGE GROUP CHARTS ####################

    px_settings={'label_value':'',
                 'facet':'',
                 'facet_col_wrap':4,
                 'range_y':None,
            }
    figs =[]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        opt_ba=st.selectbox('Show me charts of', list(config.analysis_options.keys()), key='21')

        px_settings['y'] = [i[0] for i in config.analysis_options[opt_ba]]
        px_settings['label_value'] = config.analysis_options[opt_ba][0][1]
        if opt_ba == "Vaccination Status":
            px_settings['range_y'] = [0,100]

    with col2:
        opt_bj=st.selectbox('of people aged', list_age_group)

    with col3:
        group_options=config.jur_only
        opt_bs=st.selectbox('across', group_options, key='23')

        if opt_bs == "Jurisdictions":
            plotly_df = sag_df.query('age_group == @opt_bj')
            px_settings['facet'] = px_settings['color'] = 'state'
            px_settings['facet_col_wrap'] = 9

    with col4:
        select_options={'group' : opt_bs[:-1].lower(),
                        'measure' : opt_ba.lower()
                        }
        opt_bc=st.selectbox('with each graph is a', config.chart_options,
                            format_func=lambda x: select_options.get(x),
                            key='24')

        if opt_bc == "group":
            fig=chart.facet_chart(plotly_df, **px_settings)
            figs.append(fig)
        elif opt_bc == "measure":
            for px_info in config.analysis_options[opt_ba]:
                (px_settings['y'], px_settings['y_label'], px_settings['graph_title']) = px_info
                fig=chart.line_chart(plotly_df, **px_settings)
                figs.append(fig)

    if len(figs) > 1:
        for col, fig in zip(st.columns(len(figs)), figs):
            with col:
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.plotly_chart(fig, use_container_width=True)
    ############ AGE GROUP CHARTS ####################


    ############ DAILY VAC CHARTS ####################
    st.markdown('### *Daily vaccination status*')
    col1, col2, col3= st.columns(3)
    with col1:
        opt_p=st.selectbox('Show me the daily vaccination status of', ['people 16 or older'])
    with col2:
        opt_j=st.selectbox('living in ', list_states)
    with col3:
        opt_s=st.selectbox('by', list(config.stats_options.keys()))

    col1, col2 = st.columns([2,1])
    with col1:
        st.plotly_chart(chart.vac_status(overall_state_df, opt_p, opt_j, opt_s), use_container_width=True)
    with col2:
        st.table( (compare.get_latest(overall_state_df))[['state'] + config.stats_options[opt_s]].assign(hack='').set_index('hack'))
    ############ DAILY VAC CHARTS ####################


    ############# ETA CHARTS ###############
    # Dummy user
    user=compare.User()
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### *Prediction date to hit 70% and 80% first dose*")
        eta_df = compare.construct_eta_data(overall_state_df, 'state', user, dose='dose1')
        st.plotly_chart(chart.eta_chart(eta_df, group_col='state',
                                        user=user,
                                        hl=False,
                                        annot=True), use_container_width=True)

    with col2:
        st.markdown("### *Prediction date to hit 70% and 80% fully vaccinated target*")
        pass
        eta_df = compare.construct_eta_data(overall_state_df, 'state', user)
        st.plotly_chart(chart.eta_chart(eta_df, group_col='state',
                                        user=user,
                                        hl=False,
                                        annot=True), use_container_width=True)
    ############# ETA CHARTS ###############


    st.subheader('Notes')
    st.markdown('1. Prediction on reaching 70 or 80% fully vaccinated status is based on 7-day moving average rate. This will be updated daily.')
    st.markdown('2. My source data is from https://github.com/jxeeno/aust-govt-covid19-vaccine-pdf, extracted from [WA Health](https://www.wa.gov.au/sites/default/files/2021-06/COVID-19-Vaccination-Dashboard-Guide-for-Interpretation.pdf) (second dose by state data prior to 1st July 2021) and [Department of Health](https://www.health.gov.au/using-our-websites/copyright) (all other data) by [Ken Tsang](https://github.com/jxeeno/aust-govt-covid19-vaccine-pdf). I might have modified the data to correct any mistakes or errors I perceive or notice.')
    st.markdown('3. This page does not aim or claim to be authoritative of vaccine data roll out. I do not guarantee its accuracy. Use at your own risk, and I take no responsibility of any loss that might have occurred.')





if __name__ == "__main__":
    main()
