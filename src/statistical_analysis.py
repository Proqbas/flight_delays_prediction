from __future__ import division
from sklearn import datasets
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import sklearn.cross_validation
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#read the CSV file
df = pd.read_csv('../data/test_feb_17_data.csv', dtype={col: np.float32 for col in ['ARR_DELAY', 'CANCELLED', 'DIVERTED', 'CRS_ELAPSED_TIME', 'DISTANCE', 'ORIGIN_SIZE', 'DEST_SIZE']})

airport_codes_df = pd.read_csv('../data/iata_icao_mapping.csv')
airport_codes_df = airport_codes_df.loc[~airport_codes_df.index.duplicated(keep='first')]
airport_codes_df = airport_codes_df.drop_duplicates(['IATA'])

airport_sizes_df = pd.read_csv('../data/airports_operations.csv')

#remove the last (empty) column as well as diverted and cancelled flights
df.drop(df.columns[len(df.columns)-1], axis=1, inplace=True)
df.drop(df[df.DIVERTED == 1].index, inplace=True)
df.drop(df[df.CANCELLED == 1].index, inplace=True)

#check total number of flights, total numberof delays and percentage
print "Total number of flights: ", len(df)
print "Total number of delays: ", len(df[df['ARR_DELAY'] > 0])
print "Percentage of flights delayed", len(df[df['ARR_DELAY'] > 0]) / len(df) * 100, "%"

#change IATA to ICAO codes
df['ORIGIN'] = df['ORIGIN'].map(airport_codes_df.set_index('IATA')['ICAO'])
df['DEST'] = df['DEST'].map(airport_codes_df.set_index('IATA')['ICAO'])

#replace airport codes with airport sizes category (0-4)
df['ORIGIN_SIZE'] = df['ORIGIN'].map(airport_sizes_df.set_index('ICAO')['AIRPORT_SIZE'])
df['DEST_SIZE'] = df['DEST'].map(airport_sizes_df.set_index('ICAO')['AIRPORT_SIZE'])
df['ORIGIN_SIZE'] = df['ORIGIN_SIZE'].astype('float32')
df['DEST_SIZE'] = df['DEST_SIZE'].astype('float32')

#prepare data for random forest
df['UNIQUE_CARRIER'] = df['UNIQUE_CARRIER'].astype('category')
df['UNIQUE_CARRIER_CODE'] = df['UNIQUE_CARRIER'].cat.codes

#worst 10 carriers by average delay
print "Worst 10 carriers by average delay: "
worst10carriers = df
worst10carriers = worst10carriers.groupby(['UNIQUE_CARRIER'])['ARR_DELAY'].mean()
worst10carriers = worst10carriers.sort_values().nlargest(10)
print worst10carriers

#worst 10 carriers by PERCENTAGE of delays
print "Worst 10 carriers by percentage of delays: "
totalCarrierFlights = df
totalCarrierFlights = totalCarrierFlights.groupby(['UNIQUE_CARRIER']).size()
carrierDelays = df[df['ARR_DELAY'] > 0]
carrierDelays = carrierDelays.groupby(['UNIQUE_CARRIER']).size()
print carrierDelays.div(totalCarrierFlights, level='UNIQUE_CARRIER').sort_values().nlargest(10) * 100

#worst 10 airports to depart from (mean of delay)
print "10 worst airports to depart from: (by mean delay)"
worstAirportsDep = df
worstAirportsDep = worstAirportsDep.groupby(['ORIGIN'])['ARR_DELAY'].mean()
print worstAirportsDep.sort_values().nlargest(10)

#worst 10 airports to fly to (% of flights)
print "10 worst airports to fly to: (by percentage of flights delayed)"
airportsFlights = df
airportsFlights = airportsFlights.groupby(['DEST']).size()
airportsDelayed = df[df['ARR_DELAY'] > 0]
airportsDelayed = airportsDelayed.groupby(['DEST']).size()
print airportsDelayed.div(airportsFlights, level='DEST').sort_values().nlargest(10) * 100

#flight duration vs average delay


#departure time vs average delay


#origin airport size vs average delay
print "Origin airport size vs average delay: "
depSizeDelay = df
depSizeDelay = depSizeDelay.groupby(['ORIGIN_SIZE'])['ARR_DELAY'].mean()
depSizeDelay = depSizeDelay.sort_values(ascending=False)
print depSizeDelay

#destination airport size vs average delay
print "Destination airport size vs average delay: "
destSizeDelay = df
destSizeDelay = destSizeDelay.groupby(['DEST_SIZE'])['ARR_DELAY'].mean()
destSizeDelay = destSizeDelay.sort_values(ascending=False)
print destSizeDelay

#month vs average delay


#drop redundant columns
df2 = df2.drop('UNIQUE_CARRIER', axis=1)
df2 = df2.drop('ORIGIN', axis=1)
df2 = df2.drop('DEST', axis=1)
df2 = df2.drop('ORIGIN_AIRPORT_ID', axis=1)
df2 = df2.drop('DEST_AIRPORT_ID', axis=1)
df2 = df2.drop('CANCELLED', axis=1)
df2 = df2.drop('DIVERTED', axis=1)

# remove INF and NaN's from the dataframe
print df2.isnull().values.any()
df2 = df2.replace([np.inf, -np.inf], np.nan)
df2 = df2.fillna(0)
print df2.isnull().values.any()

#print df2.describe()
#print "###############################################"
print df2.dtypes
#print "###############################################"
#print np.where(np.isnan(df2))

# assign final dataFrame to X, which will be used as a basis for train/test split
X = df2.drop('ARR_DELAY', axis=1)

