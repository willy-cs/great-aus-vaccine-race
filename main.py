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

st.set_page_config(page_title='Welcome to the Great Australian COVID-19 Vaccine Race!', layout='wide')
st.write('<style>div.row-widget.stRadio > div{flex-direction:row; border-style:double} #MainMenu {visibility: hidden;} footer {visibility: hidden;} </style>', unsafe_allow_html=True)
st.write('<style>div.row-widget.stRadio > div > label > div {padding-left: 0px; margin-right:5px} </style>', unsafe_allow_html=True)
padding = 0.3
st.markdown(f""" <style>
    .reportview-container .main .block-container{{
        padding-top: 0.1rem;
        padding-right: 2rem;
        padding-left: 0.8rem;
        padding-bottom: 0.2rem;
    }}
    </style> """, unsafe_allow_html=True)

def main():
    (df, overall_state_df, overall_ag_df, sag_df, milestone_df) = data.processing_data()
    list_states = config.states_rank
    list_age_group = list(sorted(overall_ag_df['age_group'].unique()))
    latest_date = df['date'].max().date().strftime('%d %b %Y')
    latest_date_published_dt = (df['date'].max() +datetime.timedelta(days=1)).date()
    latest_date = latest_date_published_dt.strftime('%d %b %Y')

    col1, col2, col3, col4 = st.columns(4)
    figs = chart.coverage_heatmap(sag_df, overall_state_df, c='dose1_pct', headline_only=True)
    with col1:
        st.markdown('#### It is a race!')
        st.markdown('##### ausvacrace.info')
        st.markdown("##### Data is based on reports published on {}".format(latest_date))
    with col2:
        figs[0].update_layout(height=120)
        figs[0].update_layout(title=dict(font=dict(size=15)))
        st.plotly_chart(figs[0], use_container_width=True,\
                        config={'displayModeBar':False, 'staticPlot':True})
    with col3:
        figs[1].update_layout(height=120)
        figs[1].update_layout(title=dict(font=dict(size=15)))
        st.plotly_chart(figs[1], use_container_width=True,\
                        config={'displayModeBar':False, 'staticPlot':True})
    with col4:
        actual_max_date = df['date'].max().date()
        heatmap_df = overall_state_df.query('age_group == "16_or_above" & date == @actual_max_date')
        fig = chart.heatmap_delta_data_dynamic(heatmap_df, "16+ population", "", "Jurisdictions",
                                                headline_only=True)

        fig.update_layout(height=120)
        fig.update_layout(title=dict(font=dict(size=15)))
        st.plotly_chart(fig, use_container_width=True,\
                        config={'displayModeBar':False, 'staticPlot':True})


    ############ MAIN CHARTS ####################
    px_settings={'label_value':'',
                 'facet':'',
                 'facet_col_wrap':4,
                 'range_y':None,
            }
    figs =[]

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    extra_query = ''
    with col1:
        opt_aa=st.radio('Show me charts of COVID-19 vaccination', list(config.analysis_options.keys()))

        px_settings['y'] = [i[0] for i in config.analysis_options[opt_aa]]
        px_settings['label_value'] = config.analysis_options[opt_aa][0][1]
        if opt_aa == "Coverage":
            px_settings['range_y'] = None

    with col2:
        opt_ag=st.radio('of people aged', ['16+ (eligible)'] + ['12+'] + list_age_group)

    with col3:
        if opt_ag != "16+ (eligible)" and opt_ag != '12+':
            opt_aj=st.radio('in ', ['AUS'])
        else:
            opt_aj=st.radio('in ', list_states)

    with col4:
        group_options=config.grouping_options
        if opt_aj != "AUS":
            group_options=config.age_group_only
        elif opt_ag != "16+ (eligible)" and opt_ag != '12+':
            group_options=['Jurisdictions']

        opt_as=st.radio('across', group_options)

        if opt_as == "Jurisdictions":
            plotly_df = overall_state_df
            if opt_ag == "16+ (eligible)":
                extra_query= 'age_group == "16_or_above"'
            elif opt_ag == "12+":
                extra_query= 'age_group == "12_or_above"'

            px_settings['facet'] = px_settings['color'] = 'state'
            px_settings['facet_col_wrap'] = 9
            if opt_ag != '16+ (eligible)' and opt_ag != '12+':
                plotly_df = sag_df.query('age_group == @opt_ag')
        elif opt_as == "Age Groups":
            plotly_df = overall_ag_df
            if opt_ag == "16+ (eligible)":
                extra_query = 'age_group != "12-15"'

            if opt_aj != "AUS":
                plotly_df = sag_df.query('state == @opt_aj')
            px_settings['facet'] = px_settings['color'] = 'age_group'
            px_settings['facet_col_wrap'] = 9
    with col5:
        opt_autoscale = st.radio('Graph y-axis auto-scale?', ['on', 'off'])
    with col6:
        select_options={'group' : opt_as[:-1].lower(),
                        'measure' : opt_aa.lower()
                        }
        options=config.chart_options
        # if opt_aa == 'Dose 1 vs 2 Proportion':
        #     options=['group']
        opt_ac=st.radio('with each graph is a', options, format_func=lambda x: select_options.get(x))

        if extra_query != '':
            plotly_df = plotly_df.query(extra_query)

        if opt_ac == "group":
            if opt_aa == 'Dose 1 vs 2 Proportion':
                setting = config.vac_volprop_facet_info
                px_settings['y'] = [i[0] for i in setting]
                px_settings['label_value'] = setting[0][1]

            if opt_aa == 'Growth Rate vs Coverage':
                fig=chart.exp_facet_chart(plotly_df, opt_aa, **px_settings)
                figs.append(fig)
            else:
                fig=chart.facet_chart(plotly_df, opt_aa, **px_settings)
                figs.append(fig)
        elif opt_ac == "measure":
            for px_info in config.analysis_options[opt_aa]:
                (px_settings['y'], px_settings['y_label'], px_settings['graph_title']) = px_info
                if opt_aa in ['Dose administered *est*', 'Dose administered (proportion) *est*']:
                    px_settings['opt_autoscale'] = opt_autoscale
                    px_settings['opt_aa'] = opt_aa
                    fig=chart.volume_chart(plotly_df, **px_settings)
                elif opt_aa in ['Dose 1 vs 2 Proportion']:
                    fig=chart.dose1v2_prop_chart(plotly_df, **px_settings)
                else:
                    px_settings['opt_aa'] = opt_aa
                    px_settings['opt_autoscale'] = opt_autoscale
                    fig=chart.line_chart(plotly_df, **px_settings)
                figs.append(fig)
            if opt_aa == "Coverage":
                fig3 = chart.heatmap_delta_data_dynamic(plotly_df, opt_ag, opt_aj, opt_as)
                figs.append(fig3)

    if len(figs) > 1:
        for col, fig, i in zip(st.columns(len(figs)), figs, range(0, len(figs))):
            with col:
                p_config={'displayModeBar':False}
                if i == 2 and opt_aa == "Coverage":
                    p_config={'displayModeBar':False, 'staticPlot': True}
                st.plotly_chart(fig, use_container_width=True, config=p_config)
    else:
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar':False} )
    ############ MAIN CHARTS ####################

    ############ HEATMAP CHARTS ##################
    min_date_published_dt = (df['date'].min() +datetime.timedelta(days=1)).date()

    if 'chosen_date' not in st.session_state:
        st.session_state.chosen_date = latest_date_published_dt
    chosen_date_str = st.session_state.chosen_date.strftime('%d %b %Y')
    st.markdown('#### *Vaccination coverage using reports published on {}*'.format(chosen_date_str))
    col1, col2 = st.columns(2)
    with col1:
        chosen_date_dt = st.slider("To see previous vaccination coverage report, use time slider below: (warning, you may get missing information)",
                                    # value=latest_date_published_dt,
                                    min_value=min_date_published_dt,
                                    max_value=latest_date_published_dt,
                                    key='chosen_date')
                                    # on_change=update_latest_date())
        actual_chosen_date_dt = chosen_date_dt - datetime.timedelta(days=1)
        chosen_date = chosen_date_dt.strftime('%d %b %Y')

    heatmap_sag_df = sag_df.query('date == @actual_chosen_date_dt')
    heatmap_overall_state_df = overall_state_df.query('date == @actual_chosen_date_dt')
    fig1, fig2 = chart.coverage_heatmap(heatmap_sag_df, heatmap_overall_state_df)
    heatmap_df = overall_state_df.query('age_group == "16_or_above" & date == @actual_chosen_date_dt')
    fig3 = chart.heatmap_delta_data_dynamic(heatmap_df, "16+ population", "", "Jurisdictions")
    for (col, fig) in zip(st.columns(3), [fig1, fig2, fig3]):
        with col:
            st.plotly_chart(fig, use_container_width=True,\
                            config={'displayModeBar':False, 'staticPlot':True})

    st.markdown('#### *Coverage gap (% point) to the best jurisdiction per age group, using reports published on {}*'.format(chosen_date_str))
    st.write(' ')
    fig1 = chart.gap_heatmap_data(heatmap_sag_df, heatmap_overall_state_df, col='dose1_pct')
    fig2 = chart.gap_heatmap_data(heatmap_sag_df, heatmap_overall_state_df, col='dose2_pct')
    # fig2 = chart.gap_heatmap_data(heatmap_sag_df,col='dose2_pct')
    col1, col2, _ = st.columns(3)
    with col1:
        st.plotly_chart(fig1, use_container_width=True,\
                        config={'displayModeBar':False, 'staticPlot':True})
    with col2:
        st.plotly_chart(fig2, use_container_width=True,\
                        config={'displayModeBar':False, 'staticPlot':True})
    ########### DAILY VAC CHARTS ####################
    # st.markdown('### *Daily vaccination status*')
    # col1, col2, col3= st.columns(3)
    # with col1:
    #     opt_p=st.selectbox('Show me the daily vaccination status of', ['people 16 or older'])
    # with col2:
    #     opt_j=st.selectbox('living in ', list_states)
    # with col3:
    #     opt_s=st.selectbox('by', list(config.stats_options.keys()))

    # col1, col2 = st.columns([2,1])
    # with col1:
    #     st.plotly_chart(chart.vac_status(overall_state_df, opt_p, opt_j, opt_s), use_container_width=True)
    # with col2:
    #     pass
        # st.table( (compare.get_latest(overall_state_df))[['state'] + config.stats_options[opt_s]].assign(hack='').set_index('hack'))
    ############ DAILY VAC CHARTS ####################


    ############# ETA CHARTS ###############
    # Dummy user
    user=compare.User()
    st.markdown("#### *Estimated dates to hit vaccine milestones*")
    opt_eta=st.radio('', ['16+'] + ['12+'])
    eta_src = overall_state_df.query('age_group == "16_or_above"')
    if opt_eta == "12+":
        eta_src = overall_state_df.query('age_group == "12_or_above"')
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('#### *1st dose*')
        res_df=pd.DataFrame()
        for t in [70, 80, 90, 95]:
            temp_0=eta_src.groupby('state').apply(data.predict_target_date_1stdose, t=t).reset_index().rename(columns= {0: "est_date"})
            temp_0['target'] = 'target-' + str(t)
            res_df = pd.concat([res_df, temp_0])

        final=pd.pivot(res_df, index='state', columns=['target'], values='est_date').reset_index()
        final['state']=pd.Categorical(final['state'], config.states_rank_heatmap)
        final=final.sort_values('state')
        st.table(final.assign(hack='').set_index('hack'))

    with col2:
        st.markdown('#### *2nd dose*')
        res_df=pd.DataFrame()
        for t in [70, 80, 90, 95]:
            temp_0=eta_src.groupby('state').apply(data.predict_target_date, t=t).reset_index().rename(columns= {0: "est_date"})
            temp_0['target'] = 'target-' + str(t)
            res_df = pd.concat([res_df, temp_0])

        final=pd.pivot(res_df, index='state', columns=['target'], values='est_date').reset_index()
        final['state']=pd.Categorical(final['state'], config.states_rank_heatmap)
        final=final.sort_values('state')
        st.table(final.assign(hack='').set_index('hack'))

    with col3:
        st.markdown('#### Our methods of estimating vaccine milestone dates:')
        st.markdown('1. For 1st dose targets, we use 7-day MA of 1st dose rate.')
        st.markdown('2. For 2nd dose targets, we calculate two dates: a) 7-day MA of 2nd dose rate, and b) "follow 1st dose" date. The idea with b) is that we assume the time taken to get from a given coverage level to any target in 1st dose is the same for 2nd dose. For example, if a state is currently at 63.7% 2nd dose and we want to estimate how long it will take to reach 80% 2nd dose, we will look at how long it took for that state to get from 63.7% to 80% 1st dose. We will then use this interval as an estimate for 2nd dose.')
        st.markdown('3. Should the jurisdiction has not reached the 1st dose target, then we estimate when the jurisdiction will get to that target using 7-day MA of 1st dose rate when calculating "follow 1st dose" date.')
        st.markdown('4. We present both these dates together. If they differ, we assume that the actual date of reaching the target will be somewhere between the two dates.')
        st.markdown('5. The rule of thumb is that if the vaccination growth rate is picking up, then it will be closer to the 7-day MA dates. Conversely, if the vaccination growth rate is slowing down, then it will be closer to the "follow 1st dose" date.')
        st.markdown('6. The chequered flag ???? indicates that the target has been reached.')
        st.markdown('7. No approach is perfect -- our estimate is dynamic and will be updated daily. However, by giving an interval of dates, we hope that viewers will appreciate the difficulty in predicting the future. We do expect the interval between two dates will shrink as we get closer to the target.')

    st.markdown("#### Vaccination milestone for 16+")
    col1, col2, col3 = st.columns(3)
    with col1:
        fig = chart.vaccine_milestone_chart(milestone_df.query('dose == "dose 1"'))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar':False})
    with col2:
        fig = chart.vaccine_milestone_chart(milestone_df.query('dose == "dose 2"'))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar':False})
    with col3:
        fig = chart.vaccine_milestone_chart(milestone_df)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar':False})

    ############# ETA CHARTS ###############

    st.subheader('Notes')
    st.markdown('1. My source data is from https://github.com/jxeeno/aust-govt-covid19-vaccine-pdf, extracted from [WA Health](https://www.wa.gov.au/sites/default/files/2021-06/COVID-19-Vaccination-Dashboard-Guide-for-Interpretation.pdf) (second dose by state data prior to 1st July 2021) and [Department of Health](https://www.health.gov.au/using-our-websites/copyright) (all other data) by [Ken Tsang](https://github.com/jxeeno/aust-govt-covid19-vaccine-pdf). I might have modified the data to correct any mistakes or errors I perceive or notice. Population data is from [ABS](https://www.abs.gov.au/statistics/people/population/national-state-and-territory-population/sep-2020/31010do002_202009.xls).')
    st.markdown('2. This page does not aim or claim to be authoritative of vaccine data roll out. I do not guarantee its accuracy. Use at your own risk, and I take no responsibility of any loss that might have occurred.')
    st.markdown('3. The numbers for dose administered in this site should be use as a guidance (spotting the trend if you like), rather than the actual number. Interpret the data carefully. Some numbers have been estimated from population data as AUS government did not provide the administered numbers to that level (especially to state and age group combo). There is also this issue as pointed by [Ken on twitter](https://twitter.com/jxeeno/status/1438495304194555907). *USE AT YOUR OWN RISK -- YOU HAVE BEEN WARNED*.')
    st.markdown('4. I built this page for my own purpose. Sorry if it does not meet your expectations.')
    st.markdown('5. This page is hosted on a free server. Please excuse its sluggishness.')
    st.markdown('6. This page is always going to be under development.')
    st.markdown('7. If you find this page useful, feel free to share it.')
    st.markdown('8. This page is optimised for wide screen. If you are viewing this on your phone, you might have better luck if you rotate it 90 degrees.')
    st.markdown('9. Feedback can be sent to [@ausvacrace](https://twitter.com/ausvacrace) on twitter.')
    st.markdown('10. Get jabbed! Check out vaccine availability from [COVID19 Near Me](https://covid19nearme.com.au), or [covid queue](https://covidqueue.com), or [vaccine.wfltaylor.com](https://vaccine.wfltaylor.com)')


if __name__ == "__main__":
    main()
