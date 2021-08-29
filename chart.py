import plotly.express as px
import pandas as pd
import numpy as np
from itertools import cycle

VAC_STATUS_PP = ['unvac_pct', 'dose1_pct', 'dose2_pct']
HL_FADE_COLOUR = 'lightgrey'
HL_HL_COLOUR = 'blue'


def all_charts_style(fig):
    fig.update_traces(mode="markers+lines")
    # fig.update_layout(hovermode='x')
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="left", x=0),
                      margin=dict(l=0,r=0, t=50, b=20),
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
                color_discrete_sequence = px.colors.qualitative.Alphabet
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
                        color='eta', color_discrete_map=discrete_map_task)
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="left", x=0, traceorder='reversed'),
                        margin=dict(l=0,r=0, t=50, b=20),
                  )
    fig.update_layout({'legend_title_text': ''})
    fig.update_yaxes(autorange="reversed")
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
            an['x'] = i['annot_x']
            an['y'] = i['annot_y']
            an['text'] = i['est_target_date'].strftime('%b %d')

            an['showarrow'] = False
            an['font'] = {'color' : 'White'}
            annots.append(an)

        fig.update_layout(annotations=annots)

    return fig
