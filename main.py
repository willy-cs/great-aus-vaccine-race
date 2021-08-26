#!/usr/bin/env python

import streamlit as st
import pandas as pd
import numpy as np
import datetime
import sys
import os
import compare
import data

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

st.set_page_config(page_title='It is a race!', layout='wide')

if __name__ == "__main__":
    st.header("Welcome to the Great Australian COVID Vaccine Race!")

    # while True:
    #     data.update_data()
    #     time.sleep()

    overall_state_df = st.cache(pd.read_parquet)('overall_state_df.parquet')
    sag_df = st.cache(pd.read_parquet)('sag_df.parquet')

    st.subheader("Choose your team")

    list_states = list(sorted(overall_state_df['state'].unique()))
    list_age_group = list(sorted(sag_df['age_group'].unique()))
    list_vac_status = [0,1,2]

    u_state = st.selectbox('Where do you live?', list_states)
    u_age_group = st.selectbox('What is your age group?', list_age_group)
    u_vac = st.selectbox('How many vaccine shots have you had?', list_vac_status)

    user = compare.User(u_state, u_age_group, u_vac)

    st.text("Your team is: {}".format(user))

    st.subheader('Here is how your team is doing so far in the vaccine race (last updated: {})'.format(pd.to_datetime(overall_state_df['date'].max()).date()))

    st.text("You and your state")

    st.text("{}".format(compare.state_comparison(user, overall_state_df)))

    st.text("You and your age group")

    st.text("{}".format(compare.user_age_group_comparison(user, sag_df)))

    st.subheader('Notes')
    st.markdown('1. Prediction on reaching 70 or 80% fully vaccinated status is based on 7-day moving average')
    st.markdown('2. Data is taken from ..')
