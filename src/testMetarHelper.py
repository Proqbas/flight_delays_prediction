from __future__ import division
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from classmetartest import MetarHelper
import sklearn.cross_validation
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#read the CSV files
df = pd.read_csv('../data/january_2018.csv')
airport_codes_df = pd.read_csv('../data/iata_icao_mapping.csv')
airport_codes_df = airport_codes_df.loc[~airport_codes_df.index.duplicated(keep='first')]
airport_codes_df = airport_codes_df.drop_duplicates(['IATA'])

#remove the last (empty) column as well as diverted and cancelled flights
df.drop(df.columns[len(df.columns)-1], axis=1, inplace=True)
df.drop(df[df.DIVERTED == 1].index, inplace=True)
df.drop(df[df.CANCELLED == 1].index, inplace=True)

#change IATA to ICAO codes
df['ORIGIN'] = df['ORIGIN'].map(airport_codes_df.set_index('IATA')['ICAO'])
df['DEST'] = df['DEST'].map(airport_codes_df.set_index('IATA')['ICAO'])

print "With NaN's: ", df.shape
df = df.dropna()
print "Without NaN's: ", df.shape

metarHelper = MetarHelper()
metarHelper.read_metar_dict_from_csv()
#metarHelper.get_weather_data_for_airports(df['ORIGIN'].unique())
#metarHelper.write_metar_dict_to_csv()

print "Finished!" 

#def update_weather_data_for_row(row):
#	find_most_accurate_metar(row.ORIGIN_AIRPORT, year, month, day, time)	

#df.apply(update_weather_data_for_row, axis=1)
