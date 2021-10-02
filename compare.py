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

vaccine_count_colname = {0: ('unvac', 'unvac_pct', 'are not yet vaccinated'),
                         1: ('dose1_cnt', 'dose1_pct', 'have had their first jab'),
                         2: ('dose2_cnt', 'dose2_pct', 'are fully vaccinated')}

def state_comparison(user, overall_state_df):
    as_df = get_latest(overall_state_df)
    as_df = rank_columns(as_df)
    # print(as_df)
    # print(user)
    s = as_df.query('state== @user.state').to_dict(orient = 'records')[0]
    user_state_vac_count, user_state_vac_pp, user_state_vac_count_str = vaccine_count_colname[user.vac_status]

    comment = dict()
    comment['state_vac_status'] = f"""{int(s[user_state_vac_count]):,} ({s[user_state_vac_pp]}%) out of the {int(s['abspop_jun2020']):,} over 16 population in {user.state} {user_state_vac_count_str}."""
    comment['state_vac_rate'] = f"""{user.state} administered {int(s['delta_dose12']):,} vaccines -- {s['vac_rate']}% of its over 16 population. {user.state} current 7-day moving average vaccination rate is at {s['ma7_vac_rate']}%. It is ranked #{s['ma7_vac_rate_rank']}."""
    comment['state_dose1'] = f"""{s['dose1_pct']}% of {user.state} over 16 population has had their first jab. It is ranked #{s['dose1_rank']}."""
    comment['state_dose2'] = f"""{s['dose2_pct']}% of {user.state} over 16 population has been fully vaccinated. It is ranked #{s['dose2_rank']}."""

    return comment


def ag_comparison(user, overall_ag_df):
    aag_df = get_latest(overall_ag_df)
    aag_df = rank_columns(aag_df)
    s = aag_df.query('age_group==@user.age_group').to_dict(orient = 'records')[0]
    user_ag_vac_count, user_ag_vac_pp, user_ag_vac_count_str = vaccine_count_colname[user.vac_status]

    comment = dict()
    comment['ag_vac_status'] = f"""{int(s[user_ag_vac_count]):,} ({s[user_ag_vac_pp]}%) out of the {int(s['abspop_jun2020']):,} people in the [{user.age_group}] age group nationally {user_ag_vac_count_str}."""
    comment['ag_vac_rate'] = f"""Nationally, {s['vac_rate']}% of [{user.age_group}] age group was administered a jab. [{user.age_group}] age group current 7-day moving average vaccination rate is at {s['ma7_vac_rate']}%. It is ranked #{s['ma7_vac_rate_rank']} across all other age groups."""
    comment['ag_dose1'] = f"""Nationally, {s['dose1_pct']}% of [{user.age_group}] age group has had their first jab. It is ranked #{s['dose1_rank']}."""
    comment['ag_dose2'] = f"""Nationally, {s['dose2_pct']}% of [{user.age_group}] age group has been fully vaccinated. It is ranked #{s['dose2_rank']}."""

    return comment


def state_age_group_comparison(user, sag_df):
    ag_df = get_latest(sag_df)
    ag_df = ag_df.query('state == @user.state | age_group == @user.age_group')

    ag_in_state_df = rank_columns(ag_df.query('state == @user.state').copy(deep=True))
    ag_out_state_df = rank_columns(ag_df.query('age_group == @user.age_group').copy(deep=True))
    total_ag = ag_in_state_df.shape[0]

    s = ag_in_state_df.query('state== @user.state & age_group == @user.age_group').to_dict(orient = 'records')[0]
    s_out = ag_out_state_df.query('state== @user.state & age_group == @user.age_group').to_dict(orient = 'records')[0]

    user_vac_count, user_vac_pp, user_vac_count_str = vaccine_count_colname[user.vac_status]

    comment = dict()
    comment['sag_in_vac_status'] = f"""{int(s[user_vac_count]):,} ({s[user_vac_pp]}%) out of the {int(s['abspop_jun2020']):,} people in the [{user.age_group}] age group living in {user.state} {user_vac_count_str}."""

    comment['sag_in_vac_rate'] = f"""In {user.state}, {s['vac_rate']}% of [{user.age_group}] age group was administered a jab. [{user.age_group}] age group current 7-day moving average vaccination rate is at {s['ma7_vac_rate']}%. It is ranked #{s['ma7_vac_rate_rank']} across all other age groups."""
    comment['sag_in_dose1'] = f"""{s['dose1_pct']}% of [{user.age_group}] age group in {user.state} has had their first jab. It is ranked #{s['dose1_rank']} across all other age groups."""
    comment['sag_in_dose2'] = f"""{s['dose2_pct']}% of [{user.age_group}] age group in {user.state} has been fully vaccinated. It is ranked #{s['dose2_rank']} across all other age groups."""

    comment['sag_out_vac_rate'] = f"""{s_out['vac_rate']}% of [{user.age_group}] age group in {user.state} were administered a jab. [{user.age_group}] in {user.state} current 7-day moving average vaccination rate is at {s_out['ma7_vac_rate']}%. It is ranked #{s_out['ma7_vac_rate_rank']}, compared to other states and territories."""
    comment['sag_out_dose1'] = f"""{s_out['dose1_pct']}% of [{user.age_group}] age group in {user.state} has had their first jab. It is ranked #{s_out['dose1_rank']}, compared to other states and territories."""
    comment['sag_out_dose2'] = f"""{s_out['dose2_pct']}% of [{user.age_group}] age group in {user.state} has been fully vaccinated. It is ranked #{s_out['dose2_rank']}, compared to other states and territories."""

    return comment


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
    def get(self, item):
        return getattr(self, item)

def get_latest(df):
    date_max = df['date'].max()
    return df.query('date == @date_max')

def rank_columns(df):
    df['vac_rate_rank'] = df['vac_rate'].rank(method='first', ascending=False).astype(int)
    df['ma7_vac_rate_rank'] = df['ma7_vac_rate'].rank(method='first', ascending=False).astype(int)
    df['dose1_rank'] = df['dose1_pct'].rank(method='first', ascending=False).astype(int)
    df['dose2_rank'] = df['dose2_pct'].rank(method='first', ascending=False).astype(int)
    df = sort_eta(df)
    df['eta_dose2_70_rank'] = df['eta_dose2_70_y'].rank(method='min', ascending=True).astype(int)
    df['eta_dose2_80_rank'] = df['eta_dose2_80_y'].rank(method='min', ascending=True).astype(int)
    df['eta_dose2_95_rank'] = df['eta_dose2_95_y'].rank(method='min', ascending=True).astype(int)
    df.sort_values('vac_rate_rank', ascending=True, inplace=True)
    return df

def sort_eta(c_df):
    reach_70=c_df[c_df['dose2_pct'] >= 70]['date'].min()
    reach_80=c_df[c_df['dose2_pct'] >= 80]['date'].min()
    reach_95=c_df[c_df['dose2_pct'] >= 95]['date'].min()

    c_df['eta_dose2_70_y'] = ((c_df['date'] + pd.to_timedelta(c_df['eta_dose2_70'],unit='days')).dt.ceil(freq='D')).dt.date
    c_df['eta_dose2_80_y'] = ((c_df['date'] + pd.to_timedelta(c_df['eta_dose2_80'],unit='days')).dt.ceil(freq='D')).dt.date
    c_df['eta_dose2_95_y'] = ((c_df['date'] + pd.to_timedelta(c_df['eta_dose2_95'],unit='days')).dt.ceil(freq='D')).dt.date
    c_df['eta_dose2_70_y'] = np.where(c_df['dose2_pct'] < 70, c_df['eta_dose2_70_y'], pd.to_datetime(reach_70))
    c_df['eta_dose2_80_y'] = np.where(c_df['dose2_pct'] < 80, c_df['eta_dose2_80_y'], pd.to_datetime(reach_80))
    c_df['eta_dose2_95_y'] = np.where(c_df['dose2_pct'] < 95, c_df['eta_dose2_95_y'], pd.to_datetime(reach_95))

    reach_70_dose1=c_df[c_df['dose1_pct'] >= 70]['date'].min()
    reach_80_dose1=c_df[c_df['dose1_pct'] >= 80]['date'].min()
    reach_95_dose1=c_df[c_df['dose1_pct'] >= 95]['date'].min()

    c_df['eta_dose1_70_y'] = ((c_df['date'] + pd.to_timedelta(c_df['eta_dose1_70'],unit='days')).dt.ceil(freq='D')).dt.date
    c_df['eta_dose1_80_y'] = ((c_df['date'] + pd.to_timedelta(c_df['eta_dose1_80'],unit='days')).dt.ceil(freq='D')).dt.date
    c_df['eta_dose1_95_y'] = ((c_df['date'] + pd.to_timedelta(c_df['eta_dose1_95'],unit='days')).dt.ceil(freq='D')).dt.date
    c_df['eta_dose1_70_y'] = np.where(c_df['dose1_pct'] < 70, c_df['eta_dose1_70_y'], pd.to_datetime(reach_70_dose1))
    c_df['eta_dose1_80_y'] = np.where(c_df['dose1_pct'] < 80, c_df['eta_dose1_80_y'], pd.to_datetime(reach_80_dose1))
    c_df['eta_dose1_95_y'] = np.where(c_df['dose1_pct'] < 95, c_df['eta_dose1_95_y'], pd.to_datetime(reach_95_dose1))

    return c_df

def construct_eta_data(df, group_col, user, dose='dose2'):
    # group_col is either 'state' or 'age_group'

    eta_70_col = 'eta_' + dose +  '_70_y'
    eta_80_col = 'eta_' + dose +  '_80_y'
    eta_95_col = 'eta_' + dose +  '_95_y'

    cols=['date', group_col , eta_70_col, eta_80_col, eta_95_col]
    eta_df = get_latest(df)
    eta_df = rank_columns(eta_df)
    eta_df = eta_df[cols].reset_index(drop=True).sort_values(group_col)
    eta_df = eta_df.sort_values(group_col)
    eta_df['annot_y'] = eta_df[group_col].reset_index(drop=True).index.astype(int)


    eta_df.rename(columns = {eta_70_col : '70%', eta_80_col : '80%', eta_95_col : '95%' }, inplace=True)
    eta_df = pd.melt(eta_df, id_vars=['date', group_col, 'annot_y'], value_vars=['70%', '80%', '95%'],
                        var_name='eta', value_name='est_target_date')

    eta_df['annot_x'] = eta_df['est_target_date'] - datetime.timedelta(days=3)
    eta_df.sort_values(['eta', group_col], ascending=[False, True], inplace=True)

    if dose == 'dose2':
        eta_df = eta_df.query("eta!= '95%'")

    return eta_df
