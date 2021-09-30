stats_options={'Cumulative percentage' : ['dose1_pct', 'dose2_pct', 'unvac_pct'],
                'Cumulative number' : ['dose1_cnt', 'dose2_cnt', 'unvac']
                }

hover_template={'Cumulative percentage': '%{y}%',
                'Cumulative number': '%{y}'}

states_rank = ['AUS', 'NSW', 'VIC', 'QLD', 'WA', 'SA', 'TAS', 'ACT', 'NT']
states_rank_heatmap = ['AUS', 'ACT', 'NSW', 'VIC', 'TAS', 'SA', 'NT', 'QLD', 'WA']

ag_rank = ['12-15', '16-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80+']

graph_max_scale = 1.1
# col_name, col_label, col_title
vac_rate_info = [['ma7_dose1_vac_rate', 'MA-7 vac growth rate', 'Dose 1 growth rate'],
                ['ma7_dose2_vac_rate', 'MA-7 vac growth rate', 'Dose 2 growth rate'],
                ['ma7_vac_rate', 'MA-7 vac growth rate', 'Dose 1 + 2 growth rate']]

vac_status_info = [['dose1_pct', 'coverage (%)', 'Dose 1 coverage'],
                    ['dose2_pct', 'coverage (%)', 'Dose 2 coverage']]

vac_rawvol_info = [['delta_dose1', 'volume', 'Dose 1 volume'],
                    ['delta_dose2', 'volume', 'Dose 2 volume'],
                    ['delta_dose12', 'volume', 'Dose 1 + Dose 2 volume']]

vac_volprop_info = [['dose1_prop', 'proportion (%)', 'Dose 1 Proportion'],
                    ['dose2_prop', 'proportion (%)', 'Dose 2 Proportion']]

analysis_options={'Growth Rate' : vac_rate_info,
                   'Coverage' : vac_status_info,
                   'Dose 1 vs 2 Proportion' : vac_volprop_info,
                   # 'Vac Vol Raw' : vac_rawvol_info,
                    }


chart_options=['measure', 'group']

grouping_options=['Jurisdictions', 'Age Groups']
age_group_only=['Age Groups']
jur_only=['Jurisdictions']

MIN_AGE=16
MAX_AGE=999
