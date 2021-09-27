import plotly.express as px
import plotly.figure_factory as ff
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from itertools import cycle
import config
import compare
import datetime

VAC_STATUS_PP = ['unvac_pct', 'dose1_pct', 'dose2_pct']
HL_FADE_COLOUR = 'lightgrey'
HL_HL_COLOUR = 'blue'


def all_charts_style(fig):
    fig.update_traces(mode="markers+lines")
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
                        category_orders={"state": config.states_rank},
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


def dose1_vs_dose2_rate_facet(df, facet='state'):
    fig=px.line(df,
                x='date',
                y=['ma7_dose1_vac_rate', 'ma7_dose2_vac_rate'],
                labels={'value': 'MA-7 vaccination rate', 'variable': 'dose type'},
                facet_col=facet,
                facet_col_wrap=4)

    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.1, xanchor="left", x=0),
                      margin=dict(l=0,r=0, t=50, b=20))
    fig.update_layout({'legend_title_text': ''})
    # fig = all_charts_style(fig)

    return fig

def vac_rate_facet(df, cols, label, facet='state'):
    fig=px.line(df,
                x='date',
                # y=['ma7_vac_rate', 'ma7_dose1_vac_rate', 'ma7_dose2_vac_rate'],
                y=cols,
                labels={'value': label, 'variable': 'dose type'},
                facet_col=facet,
                facet_col_wrap=3,
                category_orders={"state": config.states_rank},
                color_discrete_sequence = px.colors.qualitative.Dark2
                )

    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.1, xanchor="left", x=0),
                      margin=dict(l=0,r=0, t=50, b=20))
    fig.update_layout({'legend_title_text': ''})
    # fig = all_charts_style(fig)

    return fig


def vac_rate_chart(df, col, col_label, grouping):
    """
        col: dataframe's column name
                e.g. 'vac_rate', 'dose1_pct', 'dose2_pct'
        col_label: the printed column name in graph
        grouping: 'state' or 'age_group'
    """

    fig = px.line(df, x='date', y=col, color=grouping,
                category_orders={"state": config.states_rank},
                labels={'date':'date', col:col_label},
                color_discrete_sequence = px.colors.qualitative.Set1
        )

    fig = all_charts_style(fig)
    fig.update_traces(mode="lines")

    return fig


def line_chart(df, **kwargs):
    """
        col: dataframe's column name
                e.g. 'vac_rate', 'dose1_pct', 'dose2_pct'
        col_label: the printed column name in graph
        grouping: 'state' or 'age_group'
    """

    fig = px.line(df, x='date', y=kwargs['y'], color=kwargs['color'],
                category_orders={"state": config.states_rank},
                labels={'date':'date', kwargs['y']:kwargs['y_label']},
                range_y=kwargs['range_y'],
                color_discrete_sequence = px.colors.qualitative.Set1
        )

    fig = all_charts_style(fig)
    fig.update_traces(mode="lines")

    # line annotations
    ann=[]
    latest_df = compare.get_latest(df)
    grouping=kwargs['color']
    for i in latest_df[kwargs['color']].unique():
        ann.append(
                {'x': df['date'].max() + datetime.timedelta(days=2),
                'y': latest_df[latest_df[grouping] == i][kwargs['y']].max(),
                'text': i,
                'showarrow': False
                }
        )
    # ann.append({'x': df['date'].min()+datetime.timedelta(days=7),
    #                 'y':1, 'yanchor':'top', 'yref':'paper',
    #                 'text': 'watermark text', 'showarrow': False})
    fig.update_layout(
            title=dict(font=dict(size=18),
                        text=kwargs['graph_title'],
                        xanchor='center',
                        yanchor='top',
                        x=0.5,
                        y=1,
                    ),
            annotations=ann,
            xaxis=dict(fixedrange=True),
            yaxis=dict(fixedrange=True),
            hoverlabel=dict(
                bgcolor="white",
                font_size=16,
                font_family="Rockwell"
            ),
            hovermode='x',
        )

    fig.update_traces(
        hovertemplate='%{y}'
    )

    if kwargs['y_label'] == "coverage (%)":
        add_target_hline(fig)
    # newnames=dict(latest_df[[kwargs['color'], kwargs['y']]].to_records(index=False))
    # fig.for_each_trace(lambda t: t.update(name = t.name + "(" + str(round(newnames[t.name], 1)) + ")"))

    return fig

def add_target_hline(fig):
    fig.add_hline(y=70, line_dash="dot",
              annotation_text="70%",
              annotation_position="bottom left")
    fig.add_hline(y=80, line_dash="dot",
              annotation_text="80%",
              annotation_position="bottom left")


def facet_chart(df, **kwargs):
    fig=px.line(df,
                x='date',
                y=kwargs['y'],
                labels={'value': kwargs['label_value'], 'variable': 'dose type', 'dose1_pct': 'dose1', 'ma7_vac_rate' : 'vac_rate'},
                facet_col=kwargs['facet'],
                facet_col_wrap=kwargs['facet_col_wrap'],
                category_orders={"state": config.states_rank},
                color_discrete_sequence = px.colors.qualitative.Dark2
                )

    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.1, xanchor="center", x=0.5),
                      margin=dict(l=0,r=0, t=50, b=20))
    fig.update_layout({'legend_title_text': ''})
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    legendnames = {'dose1_pct': 'dose1', 'dose2_pct': 'dose2',
                    'ma7_vac_rate' : 'dose1+dose2', 'ma7_dose1_vac_rate' : 'dose1',
                    'ma7_dose2_vac_rate' : 'dose2'
            }
    fig.for_each_trace(lambda t: t.update(name = legendnames[t.name],
                                  legendgroup = legendnames[t.name],
                                     )
                    )

    fig.update_traces(
        hovertemplate='%{y}'
    )

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

    add_target_hline(fig)

    return fig


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

    # for twelve or above
    total_12plus_df['dose1_pct'] = round(total_12plus_df['dose1_cnt']/total_12plus_df['abspop_jun2020'] * 100, 2)
    total_12plus_df['dose2_pct'] = round(total_12plus_df['dose2_cnt']/total_12plus_df['abspop_jun2020'] * 100, 2)
    total_12plus_df['age_group'] = 'tot 12+'
    l_df=pd.concat([l_df, total_12plus_df[['state', 'age_group', 'dose1_pct', 'dose2_pct']]])

    # for total population
    total_population_df=total_12plus_df.copy(deep=True)
    total_population_df.drop(columns=['abspop_jun2020'], inplace=True) # reset the population
    state_pop = pd.read_csv('state_total_pop.csv')
    state_pop['state'] = pd.Categorical(state_pop['state'], config.states_rank)
    total_population_df=total_population_df.merge(state_pop, on='state')
    total_population_df['dose1_pct'] = round(total_population_df['dose1_cnt']/total_population_df['abspop_jun2020'] * 100, 2)
    total_population_df['dose2_pct'] = round(total_population_df['dose2_cnt']/total_population_df['abspop_jun2020'] * 100, 2)
    total_population_df['age_group'] = 'tot pop'
    l_df=pd.concat([l_df, total_population_df[['state', 'age_group', 'dose1_pct', 'dose2_pct']]])


    return l_df

def heatmap_delta_data_static(overall_state_df):
    a = compare.get_latest(overall_state_df)

    a['delta_dose1pp']=round(a['delta_dose1']/a['abspop_jun2020'] * 100, 2)
    a['delta_dose2pp']=round(a['delta_dose2']/a['abspop_jun2020'] * 100, 2)
    a['delta_dose1pp_7d']=round(a['delta_dose1_7d']/a['abspop_jun2020'] * 100, 1)
    a['delta_dose2pp_7d']=round(a['delta_dose2_7d']/a['abspop_jun2020'] * 100, 1)
    a['delta_dose1pp_30d']=round(a['delta_dose1_30d']/a['abspop_jun2020'] * 100, 1)
    a['delta_dose2pp_30d']=round(a['delta_dose2_30d']/a['abspop_jun2020'] * 100, 1)

    col_groups = [ ['delta_dose1pp', 'delta_dose2pp'],
                    ['delta_dose1pp_7d', 'delta_dose2pp_7d'],
                    ['delta_dose1pp_30d', 'delta_dose2pp_30d'] ]

    figs = []
    for y in col_groups:
        x = a['state'].unique()
        z = []
        for i in y:
            row = np.ndarray.flatten(a.sort_values('state')[i].values)
            z.append(row)

        y = ['Dose 1 ', 'Dose 2 ']
        fig = ff.create_annotated_heatmap(z,x=list(x),y=list(y), colorscale='pubu')

        figs.append(fig)

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
    subfig.update_layout(
            title=dict(font=dict(size=18),
                        text='% coverage growth of 16+ (eligible) population',
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

def heatmap_delta_data_dynamic(df, opt_ag, opt_aj, opt_as):
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

    xaxis = 'state' if opt_as == 'Jurisdictions' else 'age_group'

    figs = []
    for y in col_groups:
        x = a[xaxis].unique()
        z = []
        for i in y:
            row = np.ndarray.flatten(a.sort_values(xaxis)[i].values)
            z.append(row)

        y = ['Dose 1 ', 'Dose 2 ']
        fig = ff.create_annotated_heatmap(z,x=list(x),y=list(y), colorscale='pubu')

        figs.append(fig)

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
    subfig.update_layout(
            title=dict(font=dict(size=18),
                        text='% coverage growth of {} in {} across {}'.format(opt_ag,
                                                                                opt_aj,
                                                                                opt_as.lower()),
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

def heatmap_data(sag_df, overall_state_df, col='dose1_pct'):
    states_df = compare.get_latest(overall_state_df)

    l_df = compare.get_latest(sag_df)

    # This is for each age group coverage, all good here
    l_df = pd.concat([states_df, l_df])[['state', 'age_group', 'dose1_pct', 'dose2_pct']]
    l_df['age_group'] = np.where(l_df['age_group'] == '16_or_above', 'tot 16+' ,l_df['age_group'])
    l_df[col] = np.where(l_df[col] >= 94.99, 95, l_df[col])


    # We need to sum up vaccines for 12-15 and 16_or_above
    extra_doses_1215_df=compare.get_latest(sag_df).query('age_group == "12-15"')[['state', 'age_group','dose1_cnt', 'dose2_cnt', 'abspop_jun2020']]
    total_12plus_df=pd.concat([states_df, extra_doses_1215_df])[['state', 'age_group', 'dose1_cnt', 'dose2_cnt', 'abspop_jun2020']].groupby('state')[['dose1_cnt', 'dose2_cnt', 'abspop_jun2020']].sum().reset_index()
    l_df = add_custom_age_groups(l_df, total_12plus_df)
    l_df = l_df.sort_values(['state', 'age_group'])

    x = l_df['state'].unique()
    y = l_df['age_group'].unique()
    #z = [[state1, age_group1, state1_agegroup2...
    #     [state2]
    z = []
    for i in y:
        # convert all values into a single decimal digit for better readibility
        row = round(l_df.query('age_group==@i').sort_values('state')[col], 1).to_list()
        z.append(row)

    return x, y, z

def coverage_heatmap(sag_df, overall_state_df):
    """
    Need to prepare data for easy plotting
    """

    figs = []

    for (c, _, title) in config.vac_status_info:
        x, y, z = heatmap_data(sag_df, overall_state_df, col=c)
        # can try earth, or blues for colorscale
        fig = ff.create_annotated_heatmap(z,x=list(x),y=list(y), colorscale='pubu', zmin=0, zmax=100)
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


def facet_chart_bar(df, **kwargs):
    df['dose1_fake_pct']=df['dose1_pct'] - df['dose2_pct']
    # kwargs['y'] = ['dose2_pct', 'dose1_pct']
    kwargs['y'] = ['dose2_pct', 'dose1_fake_pct']
    fig=px.bar(df,
                y='state',
                x=kwargs['y'],
                barmode='stack',
                orientation='h',
                text='dose1_pct',
                labels={'value': kwargs['label_value'], 'variable': 'dose type', 'dose1_pct': 'dose1', 'ma7_vac_rate' : 'vac_rate'},
                facet_col=kwargs['facet'],
                facet_col_wrap=kwargs['facet_col_wrap'],
                # range_x=[0,110],
                category_orders={"state": config.states_rank},
                color_discrete_sequence = px.colors.qualitative.Dark2
                )

    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.1, xanchor="center", x=0.5),
                      margin=dict(l=0,r=0, t=50, b=20),
                      height=800)
    fig.update_layout({'legend_title_text': ''})
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    legendnames = {'dose1_pct': 'dose1', 'dose2_pct': 'dose2', 'dose1_fake_pct': 'dose1',
                    'ma7_vac_rate' : 'dose1+dose2', 'ma7_dose1_vac_rate' : 'dose1',
                    'ma7_dose2_vac_rate' : 'dose2'
            }

    fig.for_each_trace(lambda t: t.update(name = legendnames[t.name],
                                  legendgroup = legendnames[t.name],
                            )
                    )

    fig.update_traces(texttemplate='%{text:.2}%', textposition='outside')
    fig.for_each_yaxis(lambda yaxis: yaxis.update(showticklabels=True))
    fig.for_each_xaxis(lambda xaxis: xaxis.update(showticklabels=True))

    # fig['layout']['yaxis2'] = {'anchor': 'x2', 'domain': [0.0, 0.2866666666666666], 'matches': 'y', 'showticklabels': True}
    # fig['layout']['yaxis3'] = {'anchor': 'x3', 'domain': [0.0, 0.2866666666666666], 'matches': 'y', 'showticklabels': True}
    # fig['layout']['yaxis6'] = {'anchor': 'x6', 'domain': [0.35666666666666663, 0.6433333333333333], 'matches': 'y', 'showticklabels': True, 'annotations': {'x' : 4, 'y': 'ACT', 'text': 'tried' }}

    for i in fig['data']:
        if i['legendgroup'] == 'dose2':
            i['text'] = []
            i['texttemplate'] = []

    return fig

