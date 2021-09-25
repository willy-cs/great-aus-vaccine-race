stats_options={'Cumulative percentage' : ['dose1_pct', 'dose2_pct', 'unvac_pct'],
                'Cumulative number' : ['dose1_cnt', 'dose2_cnt', 'unvac']
                }

hover_template={'Cumulative percentage': '%{y}%',
                'Cumulative number': '%{y}'}

states_rank = ['AUS', 'NSW', 'VIC', 'QLD', 'WA', 'SA', 'TAS', 'ACT', 'NT']

# col_name, col_label, col_title
vac_rate_info = [['ma7_dose1_vac_rate', 'MA-7 vac rate', 'Dose 1 vac rate'],
                ['ma7_dose2_vac_rate', 'MA-7 vac rate', 'Dose 2 vac rate'],
                ['ma7_vac_rate', 'MA-7 vac rate', 'Dose 1 + Dose 2 vac rate']]

vac_status_info = [['dose1_pct', 'coverage (%)', 'Dose 1 coverage'],
                    ['dose2_pct', 'coverage (%)', 'Dose 2 coverage']]

analysis_options={'Vaccination Rate' : vac_rate_info,
                   'Vaccination Status' : vac_status_info,
                    }


chart_options=['measure', 'group']

grouping_options=['Jurisdictions', 'Age Groups']
age_group_only=['Age Groups']
jur_only=['Jurisdictions']

MIN_AGE=16
MAX_AGE=999
