import pandas as pd
import numpy as np
import csv
from pandas import Series

# Importing the data:

# IntCal13, Marine13, their difference Rg and errors. Marine13, from 13.9 cal kBP, is IntCal13 offset by 405 yr.

data = pd.read_csv('curves.csv') 

# Rg, being the difference between Marine13 and IntCal13, shows the high freq. components of the latter that need to be removed.
# Filter causes loss of data at beginning and at the end of the timeseries. Reflections at the extremes would avoid this.
# Reflection at the beginning of Rg timeseries: 
# Index was chosen to be [0:100] because this is where the gap is formed when no reflection is applied with the chosen filter window.

Rg = data['Rg'][0:100]
Rg_error = data['error_Rg'][0:100]
year = data['year_mar'][0:100]

Rg_reflected = np.asarray(list(reversed(Rg)))
error_reflected = np.asarray(list(reversed(Rg_error)))
year_reflected = np.asarray(list(reversed(year)))

# Reflection at the end of Rg timeseries:
# Index was chosen to be [4701:4801] because this is where the gap is formed when no reflection is applied with the chosen filter window.

Rg = data['Rg'][4701:4801].reset_index(drop=True)
Rg_error = data['error_Rg'][4701:4801].reset_index(drop=True)
year = data['year_mar'][4701:4801].reset_index(drop=True)

Rg_reflected_end = np.asarray(list(reversed(Rg)))
error_reflected_end = np.asarray(list(reversed(Rg_error)))
year_reflected_end = np.asarray(list(reversed(year)))

# Building the Rg Timeseries: 

df1 = pd.DataFrame({'cal BP': year_reflected, 'Rg': Rg_reflected, 'error_Rg': error_reflected}) 
df2 = pd.DataFrame({'cal BP': data['year_mar'], 'Rg': data['Rg'], 'error_Rg': data['error_Rg']}) 
df3 = pd.DataFrame({'cal BP': year_reflected_end, 'Rg': Rg_reflected_end, 'error_Rg': error_reflected_end}) 
df = pd.concat([df1, df2, df3])

# Filtering high frequency components:

# Window is full width/number of observations falling in the window.

df['trend'] = df['Rg'].rolling(win_type = 'triang', window=201, center=True).mean()
df['error_trend'] = df['error_Rg'].rolling(win_type = 'triang', window=201, center=True).mean()
df['high_freq.'] = df['Rg'] - df['trend']

# Removing blank rows:

# This will remove blank cells created by the filter in the previous step. However, this is just repeated reflected data.

df = df[pd.notnull(df['trend'])]

# Building Marine13 MRA-free:

df['Marine13_detrended'] = data['age_mar'] - df['trend']
df['error_Marine13_detrended'] = df['error_trend']

# Outputing to csv:

df.to_csv('filter.csv', index=False, header=True)


