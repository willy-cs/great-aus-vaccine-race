# great-aus-vaccine-race

### Goal
Make the COVID vaccine roll out a race!
Compare how you are doing with other Australians living in different state or in different age groups!


### Data Notes
1. Data from: https://vaccinedata.covid19nearme.com.au/data/air_residence.csv -- Ken Tsang
2. FIRST_DOSE_PCT: 'at least one dose'
3. SECOND_DOSE_PCT: 'fully vaccinated'
2. As of 20 Aug 2021, the Department of Health doesn't publish any percentage dose in an age group if it's above 95%. Instead it simply labels them > 95%. Very frustrating.
3. I've fixed data for WA 16-999 age group for 2021-08-17 'dose2_cnt', by removing the leading '1' (index 3497), correcting  it from 1475180 to 475180. Personally I think it's a typo..

### Attribution
Source: [WA Health](https://www.wa.gov.au/sites/default/files/2021-06/COVID-19-Vaccination-Dashboard-Guide-for-Interpretation.pdf) (second dose by state data prior to 1st July 2021) and [Department of Health](https://www.health.gov.au/using-our-websites/copyright) (all other data); Data extracted by [Ken Tsang](https://github.com/jxeeno/aust-govt-covid19-vaccine-pdf)
