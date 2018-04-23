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

df2 = df.head(100)
#df2.MONTH = 4
#df2.drop(df2[df2.DAY_OF_MONTH == 31].index, inplace=True)

metarHelper = MetarHelper()
metarHelper.read_metar_dict_from_csv()
#print len(metarHelper.metarDict)
#df2.apply(lambda x: metarHelper.find_most_accurate_metar(x.ORIGIN, x.YEAR, x.MONTH, x.DAY_OF_MONTH, x.CRS_DEP_TIME), axis=1)
df2 = df2.apply(metarHelper.get_origin_weather_data, axis=1)
df2 = df2.apply(metarHelper.get_destination_weather_data, axis=1)
#metarHelper.get_weather_data_for_airports(df['ORIGIN'].unique())
#metarHelper.write_metar_dict_to_csv()

#uniqueIcaos = pd.concat([df2['ORIGIN'], df['DEST']]).unique()
#s = pd.Series(uniqueIcaos)
#s.to_csv('unique_icaos_list.csv', index=False)

df2.to_csv('january_2018_df_with_weather.csv')
print df2.head(100)
print "Finished!" 

