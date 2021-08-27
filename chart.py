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
                labels={'date':'date', col:col_label}
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
