import plotly.express as px
import plotly.figure_factory as ff
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
    #                 'text': 'vaccine.willy-is.me', 'showarrow': False})
    fig.update_layout(
            title=dict(font=dict(size=20),
                        text=kwargs['graph_title'],
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
            hovermode='x',
        )

    fig.update_traces(
        hovertemplate='%{y}'
    )


    return fig


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
        )

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

def add_custom_age_groups(l_df, df):

    # for twelve or above
    df['dose1_pct'] = round(df['dose1_cnt']/df['abspop_jun2020'] * 100, 2)
    df['dose2_pct'] = round(df['dose2_cnt']/df['abspop_jun2020'] * 100, 2)
    df['age_group'] = 'tot 12+'
    l_df=pd.concat([l_df, df[['state', 'age_group', 'dose1_pct', 'dose2_pct']]])

    # for total population
    df.drop(columns=['abspop_jun2020'], inplace=True) # reset the population
    state_pop = pd.read_csv('state_total_pop.csv')
    state_pop['state'] = pd.Categorical(state_pop['state'], config.states_rank)
    df=df.merge(state_pop, on='state')
    df['dose1_pct'] = round(df['dose1_cnt']/df['abspop_jun2020'] * 100, 2)
    df['dose2_pct'] = round(df['dose2_cnt']/df['abspop_jun2020'] * 100, 2)
    df['age_group'] = 'tot pop'
    l_df=pd.concat([l_df, df[['state', 'age_group', 'dose1_pct', 'dose2_pct']]])

    return l_df


def heatmap_data(sag_df, overall_state_df, col='dose1_pct'):
    states_df = compare.get_latest(overall_state_df)

    l_df = compare.get_latest(sag_df)

    # Vacine count per state
    vaccine_count_df=l_df.\
                    groupby(['state'])\
                    [['dose1_cnt', 'dose2_cnt', 'abspop_jun2020']].sum().reset_index()

    l_df = pd.concat([states_df, l_df])[['state', 'age_group', 'dose1_pct', 'dose2_pct']]
    l_df['age_group'] = np.where(l_df['age_group'] == '16_or_above', 'tot 16+' ,l_df['age_group'])
    l_df[col] = np.where(l_df[col] >= 94.99, 95, l_df[col])

    l_df = add_custom_age_groups(l_df, vaccine_count_df)
    l_df = l_df.sort_values(['state', 'age_group'])

    x = l_df['state'].unique()
    y = l_df['age_group'].unique()
    #z = [[state1, age_group1, state1_agegroup2...
    #     [state2]
    z = []
    for i in y:
        row = l_df.query('age_group==@i').sort_values('state')[col].to_list()
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
            title=dict(font=dict(size=20),
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
