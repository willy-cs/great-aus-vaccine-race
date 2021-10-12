import plotly.express as px
import plotly.figure_factory as ff
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from itertools import cycle
import config
import compare
import datetime
import math

VAC_STATUS_PP = ['unvac_pct', 'dose1_pct', 'dose2_pct']
HL_FADE_COLOUR = 'lightgrey'
HL_HL_COLOUR = 'blue'


def all_charts_style(fig):
    # fig.update_traces(mode="markers+lines")
    # fig.update_layout(hovermode='x')
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="left", x=0),
                      margin=dict(l=0,r=0, t=80, b=20),
            )
    fig.update_layout({'legend_title_text': ''})
    fig.update_xaxes(showspikes=True)
    fig.update_yaxes(showspikes=True)

    return fig

def vac_status_dist_chart(df, user, hl=True):
    fig = px.line(df,
            x='date', y=['dose1_pct','dose2_pct','unvac_pct'],
            labels={'date':'date', 'value':'percentage point', 'variable': 'vac status'}
            # hover_data=['dose1_cnt', 'dose2_cnt', 'unvac']
        )
    if hl:
        fig.update_traces({'line' : {'color': HL_FADE_COLOUR}})
        fig.update_traces(patch={'line' : {'color': HL_HL_COLOUR}},
                        selector={'legendgroup': VAC_STATUS_PP[user.vac_status]})

    legends = cycle(['1st dose', '2nd dose', 'unvac'])
    fig.for_each_trace(lambda t: t.update(name=next(legends)))
    fig = all_charts_style(fig)

    return fig


def pp_chart(df, user, col, col_label, grouping, hl=True):
    """
        col: dataframe's column name
                e.g. 'vac_rate', 'dose1_pct', 'dose2_pct'
        col_label: the printed column name in graph
        grouping: 'state' or 'age_group'
    """

    fig = px.line(df, x='date', y=col, color=grouping,
                labels={'date':'date', col:col_label},
                color_discrete_sequence = px.colors.qualitative.Dark24
        )

    lg = user.state
    if grouping == 'state':
        lg = user.state
    elif grouping == 'age_group':
        lg = user.age_group

    if hl:
        fig.update_traces({'line' : {'color': HL_FADE_COLOUR}})
        fig.update_traces(patch={'line' : {'color': HL_HL_COLOUR}},
                        selector={'legendgroup': lg})

    fig = all_charts_style(fig)

    return fig

def eta_chart(df, group_col, user, hl=False, annot=False):
    color_80_default = 'rgb(141,160,203)'
    color_70_default = 'rgb(117,112,179)'
    color_80_hl = 'blue'
    color_70_hl = 'rgb(47,138,196)'
    discrete_map_task = { '70%': color_70_default, '80%': color_80_default }
    fig = px.timeline(df, x_start="date", x_end="est_target_date", y=group_col,
                        color='eta', color_discrete_map=discrete_map_task,
                        category_orders={"state": config.states_rank, "age_group": config.ag_rank},
                        )
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="left", x=0, traceorder='reversed'),
                        margin=dict(l=0,r=0, t=50, b=20),
                  )
    fig.update_layout({'legend_title_text': ''})
    fig.data[0].hovertemplate='80% Target Est=%{x}<br>' + group_col + '=%{y}<extra></extra>'
    fig.data[1].hovertemplate='70% Target Est=%{x}<br>' + group_col + '=%{y}<extra></extra>'

    if hl:
        array_size = int(df[group_col].nunique())
        query = user.get(group_col)
        hl_index = df[df[group_col] == query]['annot_y'].iloc[0]
        default_markers_0 = [color_80_default] * array_size
        default_markers_1 = [color_70_default] * array_size
        default_markers_0[hl_index] = color_80_hl
        default_markers_1[hl_index] = color_70_hl
        fig.data[0].marker={'color' : default_markers_0}
        fig.data[1].marker={'color' : default_markers_1}
    # print(fig.data)
    # for i, d in enumerate(fig.data):
    #     d.width = df[df['Task']==d.name]['width']

    if annot:
        annots=[]
        for idx, i in df.iterrows():
            an = dict()
            if (i['est_target_date'] <= i['date']):
                an['x'] = i['annot_x']
                an['text'] = ''
            else:
                an['x'] = i['annot_x']
                an['text'] = i['est_target_date'].strftime('%b %d')
            an['y'] = df[group_col].nunique() - 1 - i['annot_y']

            an['showarrow'] = False
            # an['font'] = {'color' : 'White'}
            an['font'] = {'color' : 'Black'}
            annots.append(an)

        fig.update_layout(annotations=annots)

    # fig.update_yaxes(autorange="reversed")
    return fig


def line_chart(df, **kwargs):
    """
        col: dataframe's column name
                e.g. 'vac_rate', 'dose1_pct', 'dose2_pct'
        col_label: the printed column name in graph
        grouping: 'state' or 'age_group'
    """

    fig = px.line()
    ann = []
    latest_df = compare.get_latest(df)
    grouping=kwargs['color']

    if kwargs['opt_aa'] == 'Growth Rate vs Coverage':
        # special case of handling this type of chart, where x-axis is not date
        (x, y) = kwargs['y']
        x_label, y_label = kwargs['y_label']
        markers=True
        for i in latest_df[grouping].unique():
            ann.append(
                    {'x': latest_df[latest_df[grouping] == i][x].max() + 1,
                    'y': latest_df[latest_df[grouping] == i][y].max(),
                    'text': i,
                    'showarrow': False
                    }
            )
    else:
        x = x_label = 'date'
        y = kwargs['y']
        y_label = kwargs['y_label']
        markers=False
        for i in latest_df[grouping].unique():
            ann.append(
                    {'x': df[x].max() + datetime.timedelta(days=2),
                    'y': latest_df[latest_df[grouping] == i][y].max(),
                    'text': i,
                    'showarrow': False
                    }
            )

    fig = px.line(df, x=x, y=y, color=kwargs['color'],
                category_orders={"state": config.states_rank, "age_group": config.ag_rank},
                labels={y:y_label, x:x_label},
                range_y=kwargs['range_y'],
                markers=markers,
                color_discrete_sequence = px.colors.qualitative.Set1,
        )

    fig = all_charts_style(fig)
    # fig.update_traces(mode="lines")

    layout_style(fig, **kwargs)
    fig.update_layout(annotations=ann)

    fig.update_traces(
        hovertemplate='%{y}'
    )
    if y_label == "coverage (%)":
        add_target_hline(fig)

    # if kwargs['opt_aa'] == "Growth Rate vs Coverage":
    #     disable_hover(fig)

    return fig

    # annotations labelling
    # add_annot_vrect(fig, latest_df[[grouping, kwargs['y']]])
    # newnames=dict(latest_df[[kwargs['color'], kwargs['y']]].to_records(index=False))
    # fig.for_each_trace(lambda t: t.update(name = t.name + "(" + str(round(newnames[t.name], 1)) + ")"))


def add_target_hline(fig):
    fig.add_hline(y=70, line_dash="dot",
              annotation_text="70%",
              annotation_position="bottom left")
    fig.add_hline(y=80, line_dash="dot",
              annotation_text="80%",
              annotation_position="bottom left")

    return

def add_target_hline_mid(fig):
    fig.add_hline(y=30, line_dash="dot",
              annotation_text="30%",
              opacity=0.3,
              annotation_position="bottom left")
    fig.add_hline(y=40, line_dash="dot",
              annotation_text="40%",
              opacity=0.3,
              annotation_position="bottom left")
    fig.add_hline(y=50, line_dash="dot",
              annotation_text="50%",
              opacity=0.3,
              annotation_position="bottom left")
    fig.add_hline(y=60, line_dash="dot",
              annotation_text="60%",
              opacity=0.3,
              annotation_position="bottom left")
    fig.add_hline(y=70, line_dash="dot",
              annotation_text="70%",
              opacity=0.3,
              annotation_position="bottom left")

    return

def add_annot_vrect(fig, df):
    list_annot = ["{}: {}".format(g, v) for (g, v) in list(df.to_records(index=False)) ]
    annot_str = '<br>'.join(list_annot[:math.ceil(len(list_annot)/2)])
    annot_str2 = '<br>'.join(list_annot[math.ceil(len(list_annot)/2):])
    fig.add_vrect(x0='2021-08-29', x1='2021-09-26',
                    annotation_text=annot_str,
                    annotation_position="bottom left",
                    # fillcolor="green",
                    # opacity=0.25,
                    line_width=0)
    fig.add_vrect(x0='2021-09-12', x1='2021-09-26',
                    annotation_text=annot_str2,
                    annotation_position="bottom left",
                    # fillcolor="green",
                    # opacity=0.25,
                    line_width=0)


def vac_status(df, people, jur, stats):
    chart_df = df.query('state==@jur')

    label={'date':'date', 'value':'{} of vaccination status'.format(stats), 'variable': 'vac status'}

    ry = None
    if stats == 'Cumulative percentage':
        ry = [0,100]

    fig = px.line(chart_df,
            x='date', y=config.stats_options[stats],
            range_y=ry,
            labels=label,
        )

    dose1_m, dose2_m, unvac_m = config.stats_options[stats]

    legends = cycle(['1st dose', '2nd dose', 'unvac'])
    ann=[]
    # dose1 annot
    ann.append(
            {'x': chart_df['date'].max(),
            'y': chart_df[dose1_m].max(),
            'text': '{:,}'.format(chart_df[dose1_m].max())
            }
    )
    # dose2 annot
    ann.append(
            {'x': chart_df['date'].max(),
            'y': chart_df[dose2_m].max(),
            'text': '{:,}'.format(chart_df[dose2_m].max())
            }
    )

    fig.update_layout(
            title=dict(font=dict(size=25),
                        text='Vaccination Status in {}'.format(jur),
                        xanchor='center',
                        yanchor='top',
                        x=0.5,
                        y=1,
                    ),
            annotations=ann,
            hoverlabel=dict(
                bgcolor="white",
                font_size=16,
                font_family="Rockwell"
            ),
            hovermode='x unified',
        )

    fig.for_each_trace(lambda t: t.update(name=next(legends)))
    fig = all_charts_style(fig)

    fig.update_traces(
        hovertemplate=config.hover_template[stats],
    )

    return fig

def add_custom_age_groups(l_df, total_12plus_df):
    # for total population
    total_population_df=total_12plus_df.copy(deep=True)
    total_population_df.drop(columns=['abspop_jun2020'], inplace=True) # reset the population
    state_pop = pd.read_csv('state_total_pop.csv')
    state_pop['state'] = pd.Categorical(state_pop['state'], config.states_rank)
    total_population_df=total_population_df.merge(state_pop, on='state')
    total_population_df['dose1_pct'] = round(total_population_df['dose1_cnt']/total_population_df['abspop_jun2020'] * 100, 2)
    total_population_df['dose2_pct'] = round(total_population_df['dose2_cnt']/total_population_df['abspop_jun2020'] * 100, 2)
    total_population_df['age_group'] = 'tot pop'
    # hack to create empty row in heatmap table
    l_df=pd.concat([l_df, total_population_df[['state', 'age_group', 'dose1_pct', 'dose2_pct']]])
    total_population_df['age_group']='empty row'
    total_population_df['dose1_pct']=0
    total_population_df['dose2_pct']=0
    l_df=pd.concat([l_df, total_population_df[['state', 'age_group', 'dose1_pct', 'dose2_pct']]], ignore_index=True)

    return l_df

def heatmap_delta_data_dynamic(df, opt_ag, opt_aj, opt_as, headline_only=False):
    a = compare.get_latest(df)

    a['delta_dose1pp']=round(a['delta_dose1']/a['abspop_jun2020'] * 100, 2)
    a['delta_dose2pp']=round(a['delta_dose2']/a['abspop_jun2020'] * 100, 2)
    a['delta_dose1pp_7d']=round(a['delta_dose1_7d']/a['abspop_jun2020'] * 100, 1)
    a['delta_dose2pp_7d']=round(a['delta_dose2_7d']/a['abspop_jun2020'] * 100, 1)
    a['delta_dose1pp_30d']=round(a['delta_dose1_30d']/a['abspop_jun2020'] * 100, 1)
    a['delta_dose2pp_30d']=round(a['delta_dose2_30d']/a['abspop_jun2020'] * 100, 1)

    col_groups = [ ['delta_dose1pp', 'delta_dose2pp'],
                    ['delta_dose1pp_7d', 'delta_dose2pp_7d'],
                    ['delta_dose1pp_30d', 'delta_dose2pp_30d'] ]

    if headline_only:
        col_groups = [ col_groups[0] ]

    xaxis = 'state' if opt_as == 'Jurisdictions' else 'age_group'

    figs = []
    for y in col_groups:
        x = a[xaxis].unique()

        if xaxis == 'state':
            a['state'] = pd.Categorical(a['state'], config.states_rank_heatmap)
            x = config.states_rank_heatmap

        z = []
        for i in y:
            row = np.ndarray.flatten(a.sort_values(xaxis)[i].values)
            z.append(row)

        y = ['Dose 1 ', 'Dose 2 ']
        fig = ff.create_annotated_heatmap(z,x=list(x),y=list(y), colorscale='pubu')

        figs.append(fig)

    if headline_only:
        fig.update_xaxes(side='top')
        fig.update_yaxes(autorange='reversed')
        fig.update_layout(
            title=dict(font=dict(size=18),
                        text='% coverage growth (16+) since yesterday',
                        xanchor='center',
                        yanchor='top',
                        x=0.5,
                        y=1,
                    ),
            margin=dict(l=0,r=0, t=40, b=20),
        )

        return fig

    subfig = make_subplots(rows=3, cols=1,
                            subplot_titles=("since yesterday", "in the last week", "in the last 30 days"),
                            vertical_spacing=0.1)
    subfig.add_trace(figs[0].data[0],1,1)
    subfig.add_trace(figs[1].data[0],2,1)
    subfig.add_trace(figs[2].data[0],3,1)
    annot0 = list(figs[0].layout.annotations)
    annot1 = list(figs[1].layout.annotations)
    annot2 = list(figs[2].layout.annotations)
    for i in range(len(annot1)):
        annot1[i]['xref'] = 'x2'
        annot1[i]['yref'] = 'y2'
    for i in range(len(annot2)):
        annot2[i]['xref'] = 'x3'
        annot2[i]['yref'] = 'y3'
    subfig.update_layout(annotations=list(subfig['layout']['annotations'])+annot0+annot1+annot2)

    if opt_aj == '':
        atext='% coverage growth of {}'.format(opt_ag)
    else:
        atext='% coverage growth of {} in {}'.format(opt_ag, opt_aj)

    subfig.update_layout(
            title=dict(font=dict(size=18),
                        text=atext,
                        xanchor='center',
                        yanchor='top',
                        x=0.5,
                        y=1,
                ),
            margin=dict(l=0,r=0,t=40,b=20),
            # height=390 #260
            )
    # place the xlabel at the top of the table
    subfig.update_xaxes(side='top')
    subfig.update_yaxes(autorange='reversed')
    subfig['layout']['yaxis']['domain'] = [0.7333,0.9333]
    subfig['layout']['yaxis2']['domain'] = [0.3667,0.5667]
    subfig['layout']['yaxis3']['domain'] = [0,0.2]
    return subfig

def heatmap_data(sag_df, overall_state_df, col='dose1_pct', headline_only=False):
    sixteen_plus_df = overall_state_df.query('age_group == "16_or_above"')
    twelve_plus_df = overall_state_df.query('age_group == "12_or_above"')

    states_df = compare.get_latest(sixteen_plus_df)
    l_df = compare.get_latest(sag_df)

    # This is for each age group coverage, for 16+
    l_df = pd.concat([states_df, l_df])[['state', 'age_group', 'dose1_pct', 'dose2_pct']]
    l_df['age_group'] = np.where(l_df['age_group'] == '16_or_above', 'tot 16+' ,l_df['age_group'])
    # l_df[col] = np.where(l_df[col] >= 94.99, 95, l_df[col])

    # Adding the 12+ population
    l_df = pd.concat([compare.get_latest(twelve_plus_df), l_df])[['state', 'age_group', 'dose1_pct', 'dose2_pct']]
    l_df['age_group'] = np.where(l_df['age_group'] == '12_or_above', 'tot 12+' ,l_df['age_group'])

    # adding the total population, using the dose counts from 12+ population
    l_df = add_custom_age_groups(l_df, compare.get_latest(twelve_plus_df))
    l_df = l_df.sort_values(['state', 'age_group'])

    l_df['state'] = pd.Categorical(l_df['state'], config.states_rank_heatmap)
    if headline_only:
        l_df = l_df[l_df['age_group'].isin(['tot 12+', 'tot 16+', 'tot pop'])]

    x = config.states_rank_heatmap
    y = l_df['age_group'].unique()
    #z = [[state1, age_group1, state1_agegroup2...
    #     [state2]
    z = []
    for i in y:
        # convert all values into a single decimal digit for better readibility
        row = round(l_df.query('age_group==@i').sort_values('state')[col], 1).to_list()
        z.append(row)

    return x, y, z

def coverage_heatmap(sag_df, overall_state_df, c='dose1_pct', headline_only=False):
    """
    Need to prepare data for easy plotting
    """

    figs = []

    for (c, _, title) in config.vac_status_info:
        x, y, z = heatmap_data(sag_df, overall_state_df, col=c, headline_only=headline_only)
        # can try earth, or blues for colorscale
        fig = ff.create_annotated_heatmap(z,x=list(x),y=list(y), colorscale='pubu', zmin=0, zmax=100)
        # Hack of creating an illusion of an empty row between age groups and total populations
        for i in fig.layout.annotations:
            if i['y'] == "empty row":
                i['text'] = ''
        fig.data[0]['y'] = np.where(np.array(fig.data[0]['y']) == 'empty row', '', fig.data[0]['y'])
        ####
        fig.update_yaxes(autorange='reversed')
        fig.update_layout(
            title=dict(font=dict(size=18),
                        text=title,
                        xanchor='center',
                        yanchor='top',
                        x=0.5,
                        y=1,
                    ),
            margin=dict(l=0,r=0, t=40, b=20),
    )
        # No hover effect
        fig.update_traces(hoverinfo='skip')

        figs.append(fig)

    return figs


def subplot_practice(overall_state_df, overall_ag_df, sag_df):
    overall_state_df['total_vac'] = overall_state_df['dose1_cnt'] + overall_state_df['dose2_cnt']
    twelve_plus_df = overall_state_df.query('age_group == "12_or_above"')
    df = twelve_plus_df.query('state == "NSW"')
    df['dose1_prop'] = round(df['delta_dose1'] / df['delta_dose12'] * 100, 2)
    df['dose2_prop'] = round(df['delta_dose2'] / df['delta_dose12'] * 100, 2)

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # fig = px.line(df,
    #         x='date', y=['delta_dose12'],
    #         labels={'date':'date', 'value':'percentage point', 'variable': 'vac status'}
    #     )
    # fig.add_trace(go.Scatter(x=df['date'].unique(), y=df['delta_dose12'], fill='tozeroy'),
                    # secondary_y=False)
    # print(df)
    fig.add_bar(x=df['date'].unique(),
                y=df['dose2_prop'], alignmentgroup='date', secondary_y=True, opacity=0.4)
    fig.add_bar(x=df['date'].unique(),
                y=df['dose1_prop'], alignmentgroup='date', secondary_y=True, opacity=0.4)
    fig.update_layout(barmode='stack')
    # fig.add_trace(go.Scatter(x=df['date'].unique(), y=df['dose1_prop']), secondary_y=True)
    # fig.add_trace(go.Scatter(x=df['date'].unique(), y=df['dose2_prop']), secondary_y=True)
    # fig.update_layout(yaxis_range=[0,500000])
    # fig.update_layout(yaxis2_range=[0,400])


    return fig


def volume_chart(df, **kwargs):
    # determine if we're cutting by age_group or state
    max_dose=df['delta_dose12'].max() * config.graph_max_scale
    if kwargs['facet'] == "state":
        # If we're grouping by states, we want to exclude 'state == AUS'
        df = df.query('state != "AUS"')
    else:
        # If we're grouping by age-group...
        max_dose=df.groupby('date')['delta_dose12'].sum().reset_index()['delta_dose12'].max()\
                        * config.graph_max_scale

    df['delta_dose1_prop'] = round(100 * df['delta_dose1_mod'] / df.groupby('date')['delta_dose1_mod'].transform(sum), 2)
    df['delta_dose2_prop'] = round(100 * df['delta_dose2_mod'] / df.groupby('date')['delta_dose2_mod'].transform(sum), 2)
    df['delta_dose12_prop'] = round(100 * df['delta_dose12_mod'] / df.groupby('date')['delta_dose12_mod'].transform(sum), 2)


    fig = px.bar(df, x='date', y=kwargs['y'], color=kwargs['color'],
                category_orders={"state": config.states_rank, "age_group": config.ag_rank},
                labels={'date':'date', kwargs['y']:kwargs['y_label']},
                # range_y=[0,max_dose],
                color_discrete_sequence = px.colors.qualitative.Set1
        )
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="left", x=0),
                      margin=dict(l=0,r=0, t=80, b=20),
                      legend_title_text='',
            )
    totals=df.groupby('date')[kwargs['y']].sum().reset_index()[kwargs['y']]

    layout_style(fig, **kwargs)

    if kwargs['y_label'] == "# administered":
        fig.update_traces(
            hovertemplate='%{y:10,.0f}'+' %{hovertext}',
            hovertext=['out of {:,.0f}'.format(i) for i in totals]
        )
    else:
        fig.update_traces(
            hovertemplate='%{y:.2f}%'+' %{hovertext}',
            hovertext=['out of 100%'] * len(totals)
        )

    return fig


def dose1v2_prop_chart(df, **kwargs):
    df = compare.get_latest(df)
    renamed = ['dose1_prop', 'dose2_prop']
    if kwargs['y'] == '1':
        cols = ['delta_dose1_mod', 'delta_dose2_mod']
    elif kwargs['y'] == '7':
        cols = ['delta_dose1_7d', 'delta_dose2_7d']
    elif kwargs['y'] == '30':
        cols = ['delta_dose1_30d', 'delta_dose2_30d']

    df['dose1_prop'] = round(100 * df[cols[0]] / (df[cols[0]] + df[cols[1]]), 2)
    df['dose2_prop'] =  100 - df['dose1_prop']

    w_df = df[['date', kwargs['facet'], 'dose1_prop', 'dose2_prop']]
    df_melted = pd.melt(w_df, id_vars=['date', kwargs['facet']], value_vars=['dose1_prop', 'dose2_prop'], var_name='dose', value_name='prop')
    df_melted['proportion']=np.where(df_melted['dose']=='dose1_prop',
                                        -1*df_melted['prop'],
                                        df_melted['prop'])
    range_max = df_melted['proportion'].abs().max() * 1.1

    # rename the negative ticks and you're all set
    fig= px.bar(df_melted, x='proportion', y=kwargs['facet'], barmode='group',
                color='dose',
                text='prop',
                labels={kwargs['facet']: '' },
                range_x=[-range_max,range_max],
                color_discrete_sequence = px.colors.qualitative.Dark2,
                category_orders={"state": config.states_rank_heatmap, "age_group": config.ag_rank},
                hover_data={'prop': False, kwargs['facet']:False, 'dose':False, 'proportion':False},
                orientation='h')

    fig.update_layout(
        barmode='relative',
        bargap=0, # gap between bars of adjacent location coordinates.
        bargroupgap=0.2, # gap between bars of the same location coordinate.
        legend_title_text='',
        legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="center", x=0.5),
        margin=dict(l=0,r=0, t=80, b=20),
        xaxis = dict(
            tickmode = 'array',
            tickvals = [-100, -75, -50, -25, 0, 25, 50, 75, 100],
            ticktext = [100, 75, 50, 25, 0, 25, 50, 75, 100]
        )
    )

    layout_style(fig, **kwargs)

    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    legendnames = { 'dose1_prop' : 'dose1',
                    'dose2_prop' : 'dose2',
            }

    fig.for_each_trace(lambda t: t.update(name = legendnames[t.name],
                                  legendgroup = legendnames[t.name],
                     ))

    fig.update_traces(
        texttemplate='%{text:.2f}%', textposition='inside',
        # hovertemplate='%{x}',
    )

    disable_hover(fig)

    return fig

def disable_hover(fig):
    fig.update_traces(hoverinfo='skip', hovertemplate=None)

    return fig

def layout_style(fig, **kwargs):
    fig.update_layout(
            title=dict(font=dict(size=18),
                        text=kwargs['graph_title'],
                        xanchor='center',
                        yanchor='top',
                        x=0.5,
                        y=1,
                    ),
            xaxis=dict(fixedrange=True),
            yaxis=dict(fixedrange=True),
            hoverlabel=dict(
                bgcolor="white",
                font_size=16,
                font_family="Rockwell"
            ),
            hovermode='x',
        )

    return fig


def facet_chart(df, opt_aa, **kwargs):
    pkwargs={}
    if opt_aa=='Dose 1 vs 2 Proportion':
        pxtype=px.bar
        pkwargs['opacity']=1,
        pkwargs['range_y']=[0,100]
        df['dose1_prop'] = round(100 * df['delta_dose1_mod'] / df['delta_dose12_mod'], 2)
        df['dose2_prop'] =  100 - df['dose1_prop']
    else:
        pxtype=px.line

    if kwargs['facet'] == "state" and opt_aa in ['Dose administered *est*', 'Dose administered (proportion) *est*']:
        # If we're grouping by states, we want to exclude 'state == AUS'
        df = df.query('state != "AUS"')
    else:
        # If we're grouping by age-group...
        max_dose=df.groupby('date')['delta_dose12'].sum().reset_index()['delta_dose12'].max()\
                        * config.graph_max_scale

    df['delta_dose1_prop'] = round(100 * df['delta_dose1_mod'] / df.groupby('date')['delta_dose1_mod'].transform(sum), 2)
    df['delta_dose2_prop'] = round(100 * df['delta_dose2_mod'] / df.groupby('date')['delta_dose2_mod'].transform(sum), 2)
    df['delta_dose12_prop'] = round(100 * df['delta_dose12_mod'] / df.groupby('date')['delta_dose12_mod'].transform(sum), 2)

    fig=pxtype(df,
                x='date',
                y=kwargs['y'],
                labels={'value': kwargs['label_value'], 'variable': 'dose type', 'dose1_pct': 'dose1', 'ma7_vac_rate' : 'vac_rate'},
                facet_col=kwargs['facet'],
                facet_col_wrap=kwargs['facet_col_wrap'],
                # category_orders={"state": config.states_rank, "age_group": config.ag_rank},
                color_discrete_sequence = px.colors.qualitative.Dark2,
                **pkwargs
                )

    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.1, xanchor="center", x=0.5),
                      margin=dict(l=0,r=0, t=50, b=20),
                      legend_title_text='')
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    legendnames = {'dose1_pct': 'dose1', 'dose2_pct': 'dose2',
                    'ma7_vac_rate' : 'dose1+dose2', 'ma7_dose1_vac_rate' : 'dose1',
                    'ma7_dose2_vac_rate' : 'dose2',
                    'delta_dose1_mod' : 'dose1',
                    'delta_dose2_mod' : 'dose2',
                    'delta_dose12_mod' : 'dose1+dose2',
                    'dose1_prop' : 'dose1',
                    'dose2_prop' : 'dose2',
                    'delta_dose1_prop' : 'dose1',
                    'delta_dose2_prop' : 'dose2',
                    'delta_dose12_prop' : 'dose1+dose2',
            }
    fig.for_each_trace(lambda t: t.update(name = legendnames[t.name],
                                  legendgroup = legendnames[t.name],
                                     )
                    )

    fig.update_traces(hovertemplate='%{y}')

    fig.update_layout(
            hoverlabel=dict(
                bgcolor="white",
                font_size=16,
                font_family="Rockwell"
            ),
            hovermode='x unified',
            xaxis=dict(fixedrange=True),
            yaxis=dict(fixedrange=True),
        )

    # WIP to add trendlines of vaccination rate
    # aus = df.query('state == "AUS"')['ma7_vac_rate'] * 20
    # aus = df.query('age_group == "16-29"')['ma7_vac_rate'] * 20
    # trace = go.Scatter(x=df["date"].unique(), y=aus, line_color="black", name="AUS", hoverinfo='skip')
    # fig.add_trace(trace, row=1, col=1)
    # trace.update(legendgroup="trendline", showlegend=False)
    # nsw = df.query('state == "NSW"')['ma7_vac_rate'] * 20
    # nsw = df.query('age_group == "80+"')['ma7_vac_rate'] * 20
    # trace = go.Scatter(x=df["date"].unique(), y=nsw, line_color="black", name="NSW", hoverinfo='skip')
    # fig.add_trace(trace, row=1, col=6)
    # trace.update(legendgroup="trendline", showlegend=False)
    # fig.update_traces(selector=-2, showlegend=False)
    # fig.update_traces(selector=-1, showlegend=False)

    if kwargs['label_value'] == "coverage (%)":
        add_target_hline(fig)
    elif kwargs['label_value'] == 'proportion (%)' and opt_aa == 'Dose 1 vs 2 Proportion':
        add_target_hline_mid(fig)

    return fig


def exp_facet_chart(df, opt_aa, **kwargs):
    if opt_aa == 'Growth Rate vs Coverage':
        # special case of handling this type of chart, where x-axis is not date
        (x, y) = kwargs['y']
        x_label, y_label = ('coverage', 'rate')
        markers=True

    subset_df = df[[kwargs['facet'], 'dose1_pct', 'ma7_dose1_vac_rate']]
    subset2_df = df[[kwargs['facet'], 'dose2_pct', 'ma7_dose2_vac_rate']]
    subset2_df.rename(columns = {'dose2_pct' : 'dose1_pct'}, inplace=True)
    xdf=pd.concat([subset_df, subset2_df])
    xdf.rename(columns={'dose1_pct': 'coverage'}, inplace=True)

    fig=px.line(xdf,
                x='coverage',
                y=['ma7_dose1_vac_rate', 'ma7_dose2_vac_rate'],
                labels={'value': 'MA-7 vac growth rate', 'coverage' : 'coverage (%)'},
                facet_col=kwargs['facet'],
                facet_col_wrap=kwargs['facet_col_wrap'],
                # category_orders={"state": config.states_rank, "age_group": config.ag_rank},
                color_discrete_sequence = px.colors.qualitative.Dark2,
                )


    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.1, xanchor="center", x=0.5),
                      margin=dict(l=0,r=0, t=50, b=20),
                      legend_title_text='')
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    legendnames = {'dose1_pct': 'dose1', 'dose2_pct': 'dose2',
                    'ma7_dose1_vac_rate' : 'dose1',
                    'ma7_dose2_vac_rate' : 'dose2',
            }
    fig.for_each_trace(lambda t: t.update(name = legendnames[t.name],
                                  legendgroup = legendnames[t.name],
                                     )
                    )

    fig.update_traces(hovertemplate='%{y}')

    fig.update_layout(
            hoverlabel=dict(
                bgcolor="white",
                font_size=16,
                font_family="Rockwell"
            ),
            hovermode='x',
            xaxis=dict(fixedrange=True),
            yaxis=dict(fixedrange=True),
        )

    return fig

def gap_heatmap_data(sag_df, overall_state_df, col='dose1_pct'):
    l_df = compare.get_latest(sag_df)
    l_df = l_df.query('state != "AUS"')

    states_rank_heatmap = ['ACT', 'NSW', 'VIC', 'TAS', 'SA', 'NT', 'QLD', 'WA']
    # print(sorted(l_df['dose1_pct'])[-10:])
    l_df[col] = np.where(l_df[col] >= 94.99, 95, l_df[col])

    sixteen_plus_df = overall_state_df.query('age_group == "16_or_above"')
    twelve_plus_df = overall_state_df.query('age_group == "12_or_above"')

    states_df = compare.get_latest(sixteen_plus_df)
    l_df = compare.get_latest(sag_df)

    # This is for each age group coverage, for 16+
    l_df = pd.concat([states_df, l_df])[['state', 'age_group', 'dose1_pct', 'dose2_pct']]
    l_df['age_group'] = np.where(l_df['age_group'] == '16_or_above', 'tot 16+' ,l_df['age_group'])
    l_df[col] = np.where(l_df[col] >= 94.99, 95, l_df[col])

    # Adding the 12+ population
    l_df = pd.concat([compare.get_latest(twelve_plus_df), l_df])[['state', 'age_group', 'dose1_pct', 'dose2_pct']]
    l_df['age_group'] = np.where(l_df['age_group'] == '12_or_above', 'tot 12+' ,l_df['age_group'])

    # adding the total population, using the dose counts from 12+ population
    l_df = add_custom_age_groups(l_df, compare.get_latest(twelve_plus_df))
    l_df = l_df.sort_values(['state', 'age_group'])
    l_df = l_df.query('state != "AUS"')
    l_df['dose1_pct'] = np.where(l_df['age_group'] == "empty row", np.nan, l_df['dose1_pct'])
    l_df['dose2_pct'] = np.where(l_df['age_group'] == "empty row", np.nan, l_df['dose2_pct'])
    ####

    l_df['gap'] = l_df.groupby('age_group')[col].transform(lambda x: x.max() - x)

    l_df['state'] = pd.Categorical(l_df['state'], states_rank_heatmap)
    x = states_rank_heatmap
    y = l_df['age_group'].unique()
    #z = [[state1, age_group1, state1_agegroup2...
    #     [state2]
    z = []
    for i in y:
        # convert all values into a single decimal digit for better readibility
        row = round(l_df.query('age_group==@i').sort_values('state')['gap'], 1).to_list()
        z.append(row)

    text_label = 'Dose 1 coverage gap'
    if col=='dose2_pct':
        text_label = 'Dose 2 coverage gap'

    fig = ff.create_annotated_heatmap(z,x=list(x),y=list(y), colorscale='temps')
    for i in fig.layout.annotations:
        if i['y'] == "empty row":
            i['text'] = ''
    fig.data[0]['y'] = np.where(np.array(fig.data[0]['y']) == 'empty row', '', fig.data[0]['y'])
    fig.update_yaxes(autorange='reversed')
    fig.update_layout(
            title=dict(font=dict(size=18),
                        text=text_label,
                        xanchor='center',
                        yanchor='top',
                        x=0.5,
                        y=1,
                    ),
        margin=dict(l=0,r=0, t=40, b=20),
    )
        # No hover effect
    fig.update_traces(hoverinfo='skip')

    return fig


def vaccine_milestone_chart(df):
    df['dose']=pd.Categorical(df['dose'])
    df.sort_values('date', inplace=True)
    df=df.reset_index(drop=True)
    ps = list(df['plot_size'])

    fig = px.scatter(df, x='state', y='date',
            color='dose',
            size=ps,
            # size='plot_size',
            text='milestone',
            color_discrete_sequence = px.colors.qualitative.Dark2,
            category_orders={'state': config.states_rank_heatmap},
            size_max=10,
            # hover_data={'dose':False,
            #             'target':True,
            #             'target_rel':False,
            #             'date':False
            #             },
            custom_data=['text_label', 'state'],
            height=600
            )
    kwargs = {'graph_title' : 'Vaccination Milestone 16+ population'}
    layout_style(fig, **kwargs)
    fig.update_layout(legend_title_text='',
                      legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="center", x=0.5),
                      margin=dict(l=0,r=0, t=50, b=20),
                      hovermode=None,
                      xaxis_title=None,
                      yaxis_title=None,
                    )
    fig.update_traces(textposition='middle right')
    fig['data'][0]['textposition'] = 'middle left'

    # remove the text label from legend symbol
    def add_trace_copy(trace):
        fig.add_traces(trace)
        new_trace = fig.data[-1]
        # new_trace.update(mode="text", showlegend=False)
        new_trace.update(showlegend=False)
        trace.update(mode="markers")
    fig.for_each_trace(add_trace_copy)

    fig.update_yaxes(tickangle=-90)
    fig.update_traces(marker_symbol='circle-open', selector=dict(type='scatter'))
    fig.update_traces(hovertemplate='%{customdata[1]}<br>%{customdata[0]}')

    return fig
