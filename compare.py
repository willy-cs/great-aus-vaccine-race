#!/usr/bin/env python

import pandas as pd
import numpy as np
import datetime
import sys
import os

import matplotlib.pyplot as plt

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

def state_comparison(user, overall_state_df):
    as_df = get_latest(overall_state_df)
    as_df = rank_columns(as_df)
    # print(as_df)
    # print(user)
    s = as_df.query('state== @user.state').to_dict(orient = 'records')[0]
    vaccine_count_colname = {0: ('unvac', 'unvac_pct', 'are not yet vaccinated'),
                             1: ('dose1_cnt', 'dose1_pct', 'have received 1 dose of vaccine'),
                             2: ('dose2_cnt', 'dose2_pct', 'have been fully vaccinated')}
    user_state_vac_count, user_state_vac_pp, user_state_vac_count_str = vaccine_count_colname[user.vac_status]

    best_state = as_df[['state', 'vac_rate']].to_dict(orient = 'records')[0] # first elem of a sorted df, always gives you the best state
    best_state_vac_rate_str = f"""Keep it up!""" if best_state['state'] == user.state else f"""The best state is {best_state['state']}, which administered vaccines to {best_state['vac_rate']}% of its population."""

    (best_state_vac_rate_str, best_state_dose1_str, best_state_dose2_str, best_state_eta_str) = best_state_strs(user, s, as_df)
    latest_date = pd.to_datetime(s['date']).date()

    output_str = f"""
As of {latest_date}, you are one of the {int(s[user_state_vac_count])} ({s[user_state_vac_pp]}%) who {user_state_vac_count_str} out of the {s['abspop_jun2020']} over 16 population in {user.state}
On {latest_date}, {user.state} administered {int(s['delta_dose12'])} vaccines -- {s['vac_rate']}% of its over 16 population. It is ranked #{s['vac_rate_rank']}. {best_state_vac_rate_str}
            {s['dose1_pct']}% of {user.state} over 16 population has had their first vaccine. It is ranked #{s['dose1_rank']}. {best_state_dose1_str}
            {s['dose2_pct']}% of {user.state} over 16 population has been fully vaccinated. It is ranked #{s['dose2_rank']}. {best_state_dose2_str}
"""
    if (s['eta_dose2_70_y'] <= s['date'] and s['eta_dose2_80_y'] > s['date']): # reached 70%, but not 80%
        output_str+=f"""{user.state} has reached the 70% fully vaccinated mark on {pd.to_datetime(s['eta_dose2_70_y']).date()}, and will reach the 80% mark on {pd.to_datetime(s['eta_dose2_80_y']).date()}. {best_state_eta_str}"""
    elif (s['eta_dose2_80_y'] <= s['date']): # reached both 70% and 80%
        output_str+=f"""{user.state} has reached the 70% fully vaccinated mark on {pd.to_datetime(s['eta_dose2_70_y']).date()}, and the 80% mark on {pd.to_datetime(s['eta_dose2_80_y']).date()}. {best_state_eta_str}"""
    else: # not reached 70%
        output_str+=f"""Using 7-day moving average second dose rate, {user.state} will reach the 70% mark on {pd.to_datetime(s['eta_dose2_70_y']).date()}, and 80% mark on {pd.to_datetime(s['eta_dose2_80_y']).date()}. It is ranked #{s['eta_dose2_70_rank']}. {best_state_eta_str}
"""
    return output_str

def user_age_group_comparison(user, sag_df):
    ag_df = get_latest(sag_df)
    ag_df = ag_df.query('state == @user.state | age_group == @user.age_group')

    ag_in_state_df = rank_columns(ag_df.query('state == @user.state').copy(deep=True))
    ag_out_state_df = rank_columns(ag_df.query('age_group == @user.age_group').copy(deep=True))
    total_ag = ag_in_state_df.shape[0]

    s = ag_in_state_df.query('state== @user.state & age_group == @user.age_group').to_dict(orient = 'records')[0]
    s_out = ag_out_state_df.query('state== @user.state & age_group == @user.age_group').to_dict(orient = 'records')[0]

    vaccine_count_colname = {0: ('unvac', 'unvac_pct', 'are not yet vaccinated'),
                             1: ('dose1_cnt', 'dose1_pct', 'have received 1 dose of vaccine'),
                             2: ('dose2_cnt', 'dose2_pct', 'have been fully vaccinated')}
    user_state_vac_count, user_state_vac_pp, user_state_vac_count_str = vaccine_count_colname[user.vac_status]
    #print(ag_in_state_df)
    # print(ag_out_state_df)

    (best_state_vac_rate_str, best_state_dose1_str, best_state_dose2_str, best_state_eta_str) = best_state_strs(user, s_out, ag_out_state_df, age_group=True)
    latest_date = pd.to_datetime(s['date']).date()

    output_str = f"""
As of {latest_date}, you are one of the {int(s[user_state_vac_count])} ({s[user_state_vac_pp]}%) who {user_state_vac_count_str} in the {user.age_group} age group living in {user.state}.
On {latest_date}, {s['vac_rate']}% of {user.age_group} in {user.state} got a jab. It is ranked #{s['vac_rate_rank']} out of {total_ag}.
           {s['dose1_pct']}% of {user.age_group} in {user.state} has had their first vaccine. It is ranked #{s['dose1_rank']} out of {total_ag}.
           {s['dose2_pct']}% of {user.age_group} in {user.state} has been fully vaccinated. It is ranked #{s['dose1_rank']} out of {total_ag}.

Comparing to the same age group in other states and territories, {user.age_group} in {user.state}:
    Rank #{s_out['vac_rate_rank']} ({s['vac_rate']}%) on the speed of vaccine rollout. {best_state_vac_rate_str}
    Rank #{s_out['dose1_rank']} ({s['dose1_pct']}%) of being half vaccinated. {best_state_dose1_str}
    Rank #{s_out['dose1_rank']} ({s['dose2_pct']}%) of being fully vaccinated. {best_state_dose2_str}
"""
    if (s['eta_dose2_70_y'] <= s['date'] and s['eta_dose2_80_y'] > s['date']): # reached 70%, but not 80%
        output_str+=f"""    Rank #{s_out['eta_dose2_70_rank']} in terms of reaching the 70/80% mark of being fully vaccinated. You have reached the 70% fully vaccinated mark on {pd.to_datetime(s['eta_dose2_70_y']).date()}, and will reach the 80% mark on {pd.to_datetime(s['eta_dose2_80_y']).date()}. {best_state_eta_str}"""
    elif (s['eta_dose2_80_y'] <= s['date']): # reached both 70% and 80%
        output_str+=f"""    Rank #{s_out['eta_dose2_70_rank']} in terms of reaching the 70/80% mark of being fully vaccinated. You have reached the 70% fully vaccinated mark on {pd.to_datetime(s['eta_dose2_70_y']).date()}, and the 80% mark on {pd.to_datetime(s['eta_dose2_80_y']).date()}. {best_state_eta_str}"""
    else: # not reached 70%
        output_str+=f"""    Rank #{s_out['eta_dose2_70_rank']} in terms of reaching the 70/80% mark of being fully vaccinated. You are predicted to reach 70% mark on {pd.to_datetime(s['eta_dose2_70_y']).date()}, 80% mark on {pd.to_datetime(s['eta_dose2_80_y']).date()}. {best_state_eta_str}"""

    return output_str

def best_state_strs(user, s, c_df, age_group=False):
    """
    user is a dict
    c_df stands for comparison_df
    """
    _, best_state_vac_rate, best_state_vac_rate_pp = list(rank_columns(get_latest(c_df)).query('vac_rate_rank==1')[['state', 'vac_rate']].to_records())[0]
    _, best_state_dose1, best_state_dose1_pp = list(rank_columns(get_latest(c_df)).query('dose1_rank==1')[['state', 'dose1_pct']].to_records())[0]
    _, best_state_dose2, best_state_dose2_pp = list(rank_columns(get_latest(c_df)).query('dose2_rank==1')[['state', 'dose2_pct']].to_records())[0]
    _, best_state_eta_70, best_state_eta_70_time, best_state_70_reached = list(rank_columns(get_latest(c_df)).query('eta_dose2_70_rank==1')[['state', 'eta_dose2_70', 'eta_dose2_70_y']].to_records())[0]
    _, best_state_eta_80, best_state_eta_80_time, best_state_80_reached = list(rank_columns(get_latest(c_df)).query('eta_dose2_70_rank==1')[['state', 'eta_dose2_80', 'eta_dose2_80_y']].to_records())[0]

    best_state_70_reached = pd.to_datetime(best_state_70_reached).date()
    best_state_80_reached = pd.to_datetime(best_state_80_reached).date()

    age_group_padding=""
    if age_group:
        age_group_padding = user.age_group + " in "

    best_state_vac_rate_str = "Keep it up!" if best_state_vac_rate == user.state \
                                         else f"""{age_group_padding}{best_state_vac_rate} is the fastest with {best_state_vac_rate_pp}%."""

    best_state_dose1_str = "Woohoo! you beauty!" if best_state_dose1 == user.state \
                                         else f"""{age_group_padding}{best_state_dose1} ({best_state_dose1_pp}%) leads the way."""

    best_state_dose2_str = "You are closest to freedom!" if best_state_dose2 == user.state \
                                         else f"""{age_group_padding}{best_state_dose2} ({best_state_dose2_pp}%) is closest to freedom."""


        # "Using 7-day moving average second dose rate, [user.state] will reach the 70% mark on 2021-10-02, and 80% mark on 2021-10-14."
    best_state_eta_str = ''
    if (best_state_eta_70 == user.state) and best_state_70_reached > s['date']: # best state, and hasn't reached 70% or 80%
        best_state_eta_str = "Mark that date :)"
    elif (best_state_eta_70 == user.state) and best_state_70_reached <= s['date'] and best_state_80_reached > s['date']: # best state, has reached 70%, but not 80%
                best_state_eta_str = f"""Keep it going!"""
    elif (best_state_eta_80 == user.state) and best_state_80_reached <= s['date']: # best state, has reached 80%
        best_state_eta_str = f"""Well done!."""
    elif (best_state_eta_70 != user.state) and s['eta_dose2_70_y'] > s['date'] and best_state_70_reached > s['date']: # not the best state, and the best state hasn't reached 70% yet
        best_state_eta_str = f"""{age_group_padding}{best_state_eta_70} will reach the 70% on {best_state_70_reached} and 80% on {best_state_80_reached}"""
    elif (best_state_eta_70 != user.state) and s['eta_dose2_70_y'] > s['date'] and best_state_70_reached <= s['date'] and best_state_80_reached > s['date']: # not the best state, but the best state has reached 70% mark, but not 80%
        best_state_eta_str = f"""{age_group_padding}{best_state_eta_70} have reached 70% on {best_state_70_reached} and will reach 80% on {best_state_80_reached}"""
    elif (best_state_eta_70 != user.state) and s['eta_dose2_70_y'] > s['date'] and best_state_70_reached <= s['date'] and best_state_80_reached <= s['date']: # not the best state, but the best state has reached 70% and 80% mark.
        best_state_eta_str = f"""{age_group_padding}{best_state_eta_70} have reached 70% on {best_state_70_reached} and 80% on {best_state_80_reached}"""
    else:
        best_state_eta_str = ""

    # s['date'] = datetime.date(2021,11,1)
    # print(best_state_70_reached)
    # print(s['date'])

    return (best_state_vac_rate_str, best_state_dose1_str, best_state_dose2_str, best_state_eta_str)

class User:
    def __init__(self, state='VIC', age_group='35-39', vac_status=1):
        self.state=state
        self.age_group=age_group
        self.vac_status=vac_status
    def __repr__(self):
        return f"""State: {self.state}; Age Group: {self.age_group} ; Number of COVID vaccine dose received: {self.vac_status} """
def get_latest(df):
    date_max = df['date'].max()
    return df.query('date == @date_max')

def rank_columns(df):
    df['vac_rate_rank'] = df['vac_rate'].rank(method='first', ascending=False).astype(int)
    df['dose1_rank'] = df['dose1_pct'].rank(method='first', ascending=False).astype(int)
    df['dose2_rank'] = df['dose2_pct'].rank(method='first', ascending=False).astype(int)
    df = sort_eta(df)
    df['eta_dose2_70_rank'] = df['eta_dose2_70_y'].rank(method='min', ascending=True).astype(int)
    df['eta_dose2_80_rank'] = df['eta_dose2_80_y'].rank(method='min', ascending=True).astype(int)
    df.sort_values('vac_rate_rank', ascending=True, inplace=True)
    return df

def sort_eta(c_df):
    eta_rank, eta_calc, eta_new_col = 'eta_dose2_70_rank', 'eta_dose2_70', 'eta_dose2_70_y'
    eta_rank, eta_calc, eta_new_col = 'eta_dose2_70_rank', 'eta_dose2_80', 'eta_dose2_80_y'

    reach_70=c_df[c_df['dose2_pct'] >= 70]['date'].min()
    reach_80=c_df[c_df['dose2_pct'] >= 80]['date'].min()

    c_df['eta_dose2_70_y'] = (c_df['date'] + pd.to_timedelta(c_df['eta_dose2_70'],unit='days')).dt.date
    c_df['eta_dose2_80_y'] = (c_df['date'] + pd.to_timedelta(c_df['eta_dose2_80'],unit='days')).dt.date
    c_df['eta_dose2_70_y'] = np.where(c_df['dose2_pct'] < 70, c_df['eta_dose2_70_y'], pd.to_datetime(reach_70))
    c_df['eta_dose2_80_y'] = np.where(c_df['dose2_pct'] < 80, c_df['eta_dose2_80_y'], pd.to_datetime(reach_80))
    return c_df

