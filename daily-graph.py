#!/usr/bin/env python

import pandas as pd
import numpy as np
import datetime
import sys
import os
import compare
import data
import chart
import config
from wand.image import Image


(df, overall_state_df, overall_ag_df, sag_df, milestone_df) = data.processing_data()
list_states = config.states_rank
list_age_group = list(sorted(overall_ag_df['age_group'].unique()))
latest_date = df['date'].max().date().strftime('%d %b %Y')
latest_date_published_dt = (df['date'].max() +datetime.timedelta(days=1)).date()
latest_date = latest_date_published_dt.strftime('%d %b %Y')


px_settings={'label_value':'',
             'facet':'',
             'facet_col_wrap':4,
             'range_y':None,
        }
opt_aa='Growth Rate'
opt_ag='16+ (eligible)'
opt_aj='AUS'
opt_as='Jurisdictions'
# opt_as='Age Groups'
opt_ac='measure'

px_settings['y'] = [i[0] for i in config.analysis_options[opt_aa]]
px_settings['label_value'] = config.analysis_options[opt_aa][0][1]
if opt_aa == "Vaccination Status":
    px_settings['range_y'] = None
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
# if opt_ac == "measure":
#     for px_info in config.analysis_options[opt_aa]:
#         (px_settings['y'], px_settings['y_label'], px_settings['graph_title']) = px_info


actual_chosen_date_dt = df['date'].max().date()
heatmap_sag_df = sag_df.query('date == @actual_chosen_date_dt')
heatmap_overall_state_df = overall_state_df.query('date == @actual_chosen_date_dt')
heatmap_df = overall_state_df.query('age_group == "16_or_above" & date == @actual_chosen_date_dt')

fig1, fig2 = chart.coverage_heatmap(heatmap_sag_df, heatmap_overall_state_df)
fig3 = chart.heatmap_delta_data_dynamic(heatmap_df, "16+ population", "", "Jurisdictions")

copyright_text='Based on AUS Department of Health report on {} <br> extracted by Ken Tsang @jxeeno'.format(latest_date)
copyright_text = copyright_text + ', prepared by ausvacrace.info'

# ======================================================

fig1.update_layout(
    margin=dict(l=10,r=10, t=130, b=0),
    title=dict(font=dict(size=18),
               text='<br> {} <br> Dose 1 Coverage'.format(copyright_text),
               xanchor='center', yanchor='top', x=0.5, y=0.95,),
    height=600
)

fig1.update_layout(
    margin=dict(l=10,r=10, t=130, b=0),
    title=dict(font=dict(size=18),
               text='<br> {} <br> Dose 1 Coverage'.format(copyright_text),
               xanchor='center', yanchor='top', x=0.5, y=0.95,),
    height=600
)


fig2.update_layout(margin=dict(l=10,r=10, t=80, b=0),
                   title=dict(text='<br> <br> Dose 2 Coverage', y=1),
                   height=550)


fig3.update_layout(margin=dict(l=10,r=10, t=110, b=20),
                   title=dict(text='<br> <br> % coverage growth of 16+ population', y=0.97))


fig1.write_image('images/fig1-wm-{}.png'.format(latest_date))
fig2.write_image('images/fig2-wm-{}.png'.format(latest_date))
fig3.write_image('images/fig3-wm-{}.png'.format(latest_date))
one = Image(filename='images/fig1-wm-{}.png'.format(latest_date))
two = Image(filename='images/fig2-wm-{}.png'.format(latest_date))
three = Image(filename='images/fig3-wm-{}.png'.format(latest_date))

with one as output:
    output.sequence.append(two)
    output.sequence.append(three)
    output.smush(True, 1)
    output.save(filename='images/wand-123-{}.png'.format(latest_date))


fig1.update_layout(
    margin=dict(l=10,r=10, t=100, b=0),
    title=dict(font=dict(size=18),
               text='<br> <br> Dose 1 Coverage', xanchor='center', yanchor='top', x=0.5, y=0.965,
    ),
    height=600
)

fig2.update_layout(margin=dict(l=10,r=10, t=100, b=0),
                   title=dict(text='<br> {} <br> Dose 2 Coverage'.format(copyright_text), y=1),
                   height=600)

fig3.update_layout(margin=dict(l=10,r=10, t=100, b=0),
                   title=dict(text='<br> <br> % coverage growth of 16+ population', y=0.965),
                   height=600)

fig1.write_image('images/fig4-wm-{}.png'.format(latest_date))
fig2.write_image('images/fig5-wm-{}.png'.format(latest_date))
fig3.write_image('images/fig6-wm-{}.png'.format(latest_date))
one = Image(filename='images/fig4-wm-{}.png'.format(latest_date))
two = Image(filename='images/fig5-wm-{}.png'.format(latest_date))
three = Image(filename='images/fig6-wm-{}.png'.format(latest_date))

with one as output:
    output.sequence.append(two)
    output.sequence.append(three)
    output.smush(False, 1)
    output.save(filename='images/wand-456-{}.png'.format(latest_date))
###################################################


growth_figs=[]
if extra_query != '':
    plotly_df = plotly_df.query(extra_query)

for px_info in config.analysis_options[opt_aa]:
    (px_settings['y'], px_settings['y_label'], px_settings['graph_title']) = px_info
    px_settings['opt_aa'] = opt_aa
    fig=chart.line_chart(plotly_df, **px_settings)
    growth_figs.append(fig)

fig1, fig2, fig3 = growth_figs

fig1.update_layout(
    margin=dict(l=0,r=0, t=140, b=0),
    title=dict(font=dict(size=18),
               text='<br> {} <br> Dose 1 Growth Rate'.format(copyright_text),
               xanchor='center',
               yanchor='top',
               x=0.5,
               y=0.95,
    ),
    height=640, width=900, xaxis_title=None,
)

fig2.update_layout(margin=dict(l=0,r=0, t=100, b=0),
                   title=dict(text='<br> <br> Dose 2 Growth Rate', y=0.99),
                   height=640, width=900, xaxis_title=None)

fig3.update_layout(margin=dict(l=0,r=0, t=100, b=0),
                   title=dict(text='<br> <br> Dose 1 + 2 Growth Rate', y=0.99),
                   height=640, width=900, xaxis_title=None)

fig1.write_image('images/fig1-growth-{}.png'.format(latest_date))
fig2.write_image('images/fig2-growth-{}.png'.format(latest_date))
fig3.write_image('images/fig3-growth-{}.png'.format(latest_date))
one = Image(filename='images/fig1-growth-{}.png'.format(latest_date))
two = Image(filename='images/fig2-growth-{}.png'.format(latest_date))
three = Image(filename='images/fig3-growth-{}.png'.format(latest_date))

with one as output:
    output.sequence.append(two)
    output.sequence.append(three)
    output.smush(True, 1)
    output.save(filename='images/growth-123-{}.png'.format(latest_date))


fig1.update_layout(
    margin=dict(l=0,r=0, t=120, b=0),
    title=dict(font=dict(size=18),
               text='<br>  <br> Dose 1 Growth Rate',
               xanchor='center',
               yanchor='top',
               x=0.5,
               y=0.96,
    ),
    height=640, width=900, xaxis_title=None,
)
fig2.update_layout(margin=dict(l=0,r=0, t=120, b=0),
                   title=dict(text='<br> {} <br> Dose 2 Growth Rate'.format(copyright_text), y=1),
                   height=640, width=900, xaxis_title=None)
fig3.update_layout(margin=dict(l=0,r=0, t=120, b=0),
                   title=dict(text='<br> <br> Dose 1 + 2 Growth Rate', y=0.96),
                   height=640, width=900, xaxis_title=None)

fig1.write_image('images/fig4-growth-{}.png'.format(latest_date))
fig2.write_image('images/fig5-growth-{}.png'.format(latest_date))
fig3.write_image('images/fig6-growth-{}.png'.format(latest_date))
one = Image(filename='images/fig4-growth-{}.png'.format(latest_date))
two = Image(filename='images/fig5-growth-{}.png'.format(latest_date))
three = Image(filename='images/fig6-growth-{}.png'.format(latest_date))

with one as output:
    output.sequence.append(two)
    output.sequence.append(three)
    output.smush(False, 1)
    output.save(filename='images/growth-456-{}.png'.format(latest_date))
#####################################################



