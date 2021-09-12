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
    df = data.age_grouping(df, False)

    # list_states = list(sorted(df['state'].unique()))
    # if 'AUS' in list_states:
    #     list_states[0] = "AUS"
    #     list_states[1] = "ACT"
    list_states = config.states_rank
    list_age_group = list(sorted(df['age_group'].unique()))
    list_vac_status = [0,1,2]
    age_group_10_flag = False

    # u_age_group=''
    # try:
    #     if u_age == '' or int(u_age) < MIN_AGE or int(u_age) > MAX_AGE:
    #         st.write('Invalid age, please retry.')
    #         return
    #     else:
    #         df = data.age_grouping(df,age_group_10_flag)
    #         (overall_state_df, overall_ag_df, sag_df) = data.save_data(df)
    #         u_age_group = data.find_age_group(overall_ag_df,u_age)
    #         latest_date = pd.to_datetime(overall_state_df['date'].max()).date().strftime('%d %b %Y')
    #         user = compare.User(u_state, u_age_group, u_vac)
    #         s_short_com = compare.state_comparison(user, overall_state_df)
    #         a_short_com = compare.ag_comparison(user, overall_ag_df)
    #         sa_short_com = compare.state_age_group_comparison(user, sag_df)
    #         state_df=overall_state_df.query('state==@user.state')
    #         ag_df=overall_ag_df.query('age_group==@user.age_group')
    #         comp_sag_df=sag_df.query('state==@user.state & age_group==@user.age_group')
    #         comp_s_df=sag_df.query('state==@user.state')
    #         comp_ag_df=sag_df.query('age_group==@user.age_group')
    # except Exception as e:
    #     st.write(e)
    #     return

    cached_df = data.get_data()
    df = cached_df.copy(deep = True)
    df = data.age_grouping(df, True)
    (overall_state_df, overall_ag_df, sag_df) = data.save_data(df)
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
        opt_ac=st.selectbox('with each graph is a', config.chart_options )

        if opt_ac == "group":
            fig=chart.facet_chart(plotly_df, **px_settings)
            figs.append(fig)
        elif opt_ac == "measure":
            for (y, y_label) in [(i[0],i[1]) for i in config.analysis_options[opt_aa]]:
                (px_settings['y'], px_settings['y_label']) = (y, y_label)
                fig=chart.line_chart(plotly_df, **px_settings)
                figs.append(fig)

    if len(figs) > 1:
        for col, fig in zip(st.columns(len(figs)), figs):
            with col:
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.plotly_chart(fig, use_container_width=True)

        ############################################################## BIG ####################

        ############################################################## BIG ####################

    # col1, col2 = st.columns([2,1])
    # with col1:
    #     st.plotly_chart(chart.vac_status(overall_state_df, opt_p, opt_j, opt_s), use_container_width=True)
    # with col2:
    #     st.table( (compare.get_latest(overall_state_df))[['state'] + config.stats_options[opt_s]].assign(hack='').set_index('hack'))

    # col1, col2 = st.columns(2)
    # with col1:
    #     st.markdown("### *1st jab coverage*")
    #     px_settings={'y':'dose1_pct',
    #                 'y_label':'1st jab coverage',
    #                 'color':'state',
    #                 'range_y':[0,100]
    #             }
    #     fig=chart.line_chart(overall_state_df, **px_settings)
    #     st.plotly_chart(fig, use_container_width=True)

    # with col2:
    #     st.markdown("### *2nd jab coverage*")
    #     px_settings={'y':'dose2_pct',
    #                 'y_label':'2nd jab coverage',
    #                 'color':'state',
    #                 'range_y':[0,100]
    #             }
    #     fig=chart.line_chart(overall_state_df, **px_settings)
    #     st.plotly_chart(fig, use_container_width=True)

            #####################

            ################################
    # st.dataframe( (compare.get_latest(overall_state_df))[['state'] + config.stats_options[opt_s]].assign(hack='').set_index('hack'))

    # st.markdown("### *Vaccination rate on {}*".format(latest_date))
    # col1, col2 = st.columns(2)
    # with col1:
    #     st.markdown("> {}".format(s_short_com['state_vac_rate']))
    #     st.plotly_chart(chart.pp_chart(overall_state_df, user,
    #                                     col='ma7_vac_rate',
    #                                     col_label='MA-7 vaccination rate',
    #                                     grouping='state',
    #                                     hl=hl_graph), use_container_width=True)

    #     # st.plotly_chart(chart.pp_chart(overall_state_df, user,
    #     #                                 col='ma7_dose1_vac_rate',
    #     #                                 col_label='MA-7 dose 1 vaccination rate',
    #     #                                 grouping='state',
    #     #                                 hl=hl_graph), use_container_width=True)

    #     st.markdown("> {}".format(a_short_com['ag_vac_rate']))
    #     st.plotly_chart(chart.pp_chart(overall_ag_df, user,
    #                                     col='ma7_vac_rate',
    #                                     col_label='MA-7 vaccination rate',
    #                                     grouping='age_group',
    #                                     hl=hl_graph), use_container_width=True)

    # with col2:
    #     st.markdown("> {}".format(sa_short_com['sag_out_vac_rate']))
    #     st.plotly_chart(chart.pp_chart(comp_ag_df, user,
    #                                     col='ma7_vac_rate',
    #                                     col_label='MA-7 vaccination rate',
    #                                     grouping='state',
    #                                     hl=hl_graph), use_container_width=True)

    #     st.markdown("> {}".format(sa_short_com['sag_in_vac_rate']))
    #     st.plotly_chart(chart.pp_chart(comp_s_df, user,
    #                                     col='ma7_vac_rate',
    #                                     col_label='MA-7 vaccination rate',
    #                                     grouping='age_group',
    #                                     hl=hl_graph), use_container_width=True)

    # st.markdown("### *First jab coverage on {}*".format(latest_date))
    # col1, col2 = st.columns(2)
    # with col1:
    #     st.markdown("> {}".format(s_short_com['state_dose1']))
    #     st.plotly_chart(chart.pp_chart(overall_state_df, user,
    #                                     col='dose1_pct',
    #                                     col_label='1st dose pct',
    #                                     grouping='state',
    #                                     hl=hl_graph), use_container_width=True)

    #     st.markdown("> {}".format(a_short_com['ag_dose1']))
    #     st.plotly_chart(chart.pp_chart(overall_ag_df, user,
    #                                     col='dose1_pct',
    #                                     col_label='1st dose pct',
    #                                     grouping='age_group',
    #                                     hl=hl_graph), use_container_width=True)

    # with col2:
    #     st.markdown("> {}".format(sa_short_com['sag_out_dose1']))
    #     st.plotly_chart(chart.pp_chart(comp_ag_df, user,
    #                                     col='dose1_pct',
    #                                     col_label='1st dose pct',
    #                                     grouping='state',
    #                                     hl=hl_graph), use_container_width=True)


    #     st.markdown("> {}".format(sa_short_com['sag_in_dose1']))
    #     st.plotly_chart(chart.pp_chart(comp_s_df, user,
    #                                     col='dose1_pct',
    #                                     col_label='1st dose pct',
    #                                     grouping='age_group',
    #                                     hl=hl_graph), use_container_width=True)

    # st.markdown("### *Fully vaccinated coverage on {}*".format(latest_date))
    # col1, col2 = st.columns(2)
    # with col1:
    #     st.markdown("> {}".format(s_short_com['state_dose2']))
    #     st.plotly_chart(chart.pp_chart(overall_state_df, user,
    #                                     col='dose2_pct',
    #                                     col_label='2nd dose pct',
    #                                     grouping='state',
    #                                     hl=hl_graph), use_container_width=True)

    #     st.markdown("> {}".format(a_short_com['ag_dose2']))
    #     st.plotly_chart(chart.pp_chart(overall_ag_df, user,
    #                                     col='dose2_pct',
    #                                     col_label='2nd dose pct',
    #                                     grouping='age_group',
    #                                     hl=hl_graph), use_container_width=True)

    # with col2:
    #     st.markdown("> {}".format(sa_short_com['sag_out_dose2']))
    #     st.plotly_chart(chart.pp_chart(comp_ag_df, user,
    #                                     col='dose2_pct',
    #                                     col_label='2nd dose pct',
    #                                     grouping='state',
    #                                     hl=hl_graph), use_container_width=True)

    #     st.markdown("> {}".format(sa_short_com['sag_in_dose2']))
    #     st.plotly_chart(chart.pp_chart(comp_s_df, user,
    #                                     col='dose2_pct',
    #                                     col_label='2nd dose pct',
    #                                     grouping='age_group',
    #                                     hl=hl_graph), use_container_width=True)


    # st.markdown("### *Prediction date to hit 70% and 80% first dose*")
    # col1, col2 = st.columns(2)
    # with col1:
    #     eta_df = compare.construct_eta_data(overall_state_df, 'state', user, dose='dose1')
    #     st.plotly_chart(chart.eta_chart(eta_df, group_col='state',
    #                                     user=user,
    #                                     hl=hl_graph,
    #                                     annot=True), use_container_width=True)

    # with col2:
    #     eta_df = compare.construct_eta_data(overall_ag_df, 'age_group', user, dose='dose1')
    #     st.plotly_chart(chart.eta_chart(eta_df, group_col='age_group',
    #                                     user=user,
    #                                     hl=hl_graph,
    #                                     annot=False), use_container_width=True)

    # st.markdown("### *Prediction date to hit 70% and 80% fully vaccinated target*")
    # col1, col2 = st.columns(2)
    # with col1:
    #     eta_df = compare.construct_eta_data(overall_state_df, 'state', user)
    #     st.plotly_chart(chart.eta_chart(eta_df, group_col='state',
    #                                     user=user,
    #                                     hl=hl_graph,
    #                                     annot=True), use_container_width=True)

    # with col2:
    #     eta_df = compare.construct_eta_data(overall_ag_df, 'age_group', user)
    #     st.plotly_chart(chart.eta_chart(eta_df, group_col='age_group',
    #                                     user=user,
    #                                     hl=hl_graph,
    #                                     annot=False), use_container_width=True)


    # user=compare.User(state='NSW', age_group='30-39', vac_status=1)
    # st.markdown("### *Dose 1 vs Dose 2 vaccination rate in {}, across age groups*".format(user.state))
    # st.plotly_chart(chart.dose1_vs_dose2_rate_facet(sag_df.query('state == @user.state'), facet='age_group'), use_container_width=True)
    #################

    st.subheader('Notes')
    st.markdown('1. Prediction on reaching 70 or 80% fully vaccinated status is based on 7-day moving average rate. This will be updated daily.')
    st.markdown('2. My source data is from https://github.com/jxeeno/aust-govt-covid19-vaccine-pdf, extracted from [WA Health](https://www.wa.gov.au/sites/default/files/2021-06/COVID-19-Vaccination-Dashboard-Guide-for-Interpretation.pdf) (second dose by state data prior to 1st July 2021) and [Department of Health](https://www.health.gov.au/using-our-websites/copyright) (all other data) by [Ken Tsang](https://github.com/jxeeno/aust-govt-covid19-vaccine-pdf). I might have modified the data to correct any mistakes or errors I perceive or notice.')
    st.markdown('3. This page does not aim or claim to be authoritative of vaccine data roll out. I do not guarantee its accuracy. Use at your own risk, and I take no responsibility of any loss that might have occurred.')





if __name__ == "__main__":
    main()
