from __future__ import division
from sklearn import datasets
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
#from operator import itemgetter
import operator
import sklearn.cross_validation
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def labelFlightDuration(row):
	if(row[2] == 5):
		print "5"
	duration = row['CRS_ELAPSED_TIME']
	if(duration <= 60):
		row['FLIGHT_DURATION_CAT'] = 0
		return 
	if(duration <= 120):
		row['FLIGHT_DURATION_CAT'] = 1
		return 
	if(duration <= 240):
		row['FLIGHT_DURATION_CAT'] = 2
		return 
	if(duration <= 480):
		row['FLIGHT_DURATION_CAT'] = 3
		return 
	row['FLIGHT_DURATION_CAT'] = 4

#read the CSV file
#../data/test_feb_17_data.csv
#../data/january_2018.csv
df = pd.read_csv('../data/test_feb_17_data.csv', dtype={col: np.float32 for col in ['ARR_DELAY', 'CANCELLED', 'DIVERTED', 'CRS_ELAPSED_TIME', 'DISTANCE', 'ORIGIN_SIZE', 'DEST_SIZE']})

print df.dtypes

airport_codes_df = pd.read_csv('../data/iata_icao_mapping.csv')
airport_codes_df = airport_codes_df.loc[~airport_codes_df.index.duplicated(keep='first')]
airport_codes_df = airport_codes_df.drop_duplicates(['IATA'])

airport_sizes_df = pd.read_csv('../data/airports_operations.csv')

#remove the last (empty) column as well as diverted and cancelled flights
df.drop(df.columns[len(df.columns)-1], axis=1, inplace=True)
df.drop(df[df.DIVERTED == 1].index, inplace=True)
df.drop(df[df.CANCELLED == 1].index, inplace=True)

#remove outliers
df.drop(df[df.ARR_DELAY > 480].index, inplace=True)

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
#durationVsDelay = df
#durationVsDelay = durationVsDelay.sort_values(by='DAY_OF_MONTH', ascending=True)
#durationVsDelay = durationVsDelay.apply(lambda row: labelFlightDuration(row), axis=1)
#durationVsDelay = durationVsDelay.groupby(['FLIGHT_DURATION_CAT'])['ARR_DELAY'].mean()
#durationVsDelay = durationVsDelay.sort_values(ascending=False)
#print durationVsDelay

#departure time vs average delay
print "Departure time vs average delay: "
depVsDelay = df
depVsDelay['CRS_DEP_TIME'] = depVsDelay.CRS_DEP_TIME.astype(str)
depVsDelay['CRS_DEP_TIME'] = depVsDelay['CRS_DEP_TIME'].str.zfill(4) 
depVsDelay['CRS_DEP_TIME'] = depVsDelay['CRS_DEP_TIME'].str.slice(start=0, stop=2)
depDelayResult = depVsDelay.groupby(['CRS_DEP_TIME'])['ARR_DELAY'].mean()
print depDelayResult

#arrival time vs average delay
print "Arrival time vs average delay: "
arrVsDelay = df
arrVsDelay['CRS_ARR_TIME'] = arrVsDelay.CRS_ARR_TIME.astype(str)
arrVsDelay['CRS_ARR_TIME'] = arrVsDelay['CRS_ARR_TIME'].str.zfill(4) 
arrVsDelay['CRS_ARR_TIME'] = arrVsDelay['CRS_ARR_TIME'].str.slice(start=0, stop=2)
arrDelayResult = arrVsDelay.groupby(['CRS_ARR_TIME'])['ARR_DELAY'].mean()
print arrDelayResult

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
print "Month vs average delay: "
monthDelay = df
monthDelay = monthDelay.groupby(['MONTH'])['ARR_DELAY'].mean()
print monthDelay

#day of week vs average delay
print "Day of week vs average delay: "
weekdayDelay = df
weekdayDelay = weekdayDelay.groupby(['DAY_OF_WEEK'])['ARR_DELAY'].mean()
print weekdayDelay

#most delayed routes for American Airlines
#step 1 - create list of all routes and delays on that route
df1 = df
df1 = df1[df1['UNIQUE_CARRIER']=='AA'][['ORIGIN', 'DEST', 'ARR_DELAY']]
routes = dict()
for ind, row in df1.iterrows():
	if pd.isnull(row['ARR_DELAY']) : continue
	route = str(row['ORIGIN']) + '-' + str(row['DEST'])
	if route in routes.keys():
		routes[route].append(row['ARR_DELAY'])
	else:
		routes[route] = [row['ARR_DELAY']]

#step 2 - calculate mean delay for each route
routes_list = []
mean_values = []
for key, value in routes.items():
	routes_list.append([key, value])
	value2 = [min(90, v) for v in value]
	mean_values.append([key, np.mean(value2)])
routes_list.sort()
mean_values.sort(key=operator.itemgetter(1), reverse=True)
for val in mean_values[:20]:
	print val[0], ": ", val[1]

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!#

#weather conditions vs delay
df2 = pd.read_csv('january_2018_df_with_weather.csv')
totalDelays = df2[df2.ARR_DELAY > 0]
extremeFlights = df2[(df2.ORIGIN_HAS_EXTREME == 1) | (df2.DEST_HAS_EXTREME == 1)]
extremeDelays = totalDelays[(totalDelays.ORIGIN_HAS_EXTREME == 1) | (totalDelays.DEST_HAS_EXTREME == 1)]
precipitationFlights = df2[(df2.ORIGIN_HAS_PRECIPITATION == 1) | (df2.DEST_HAS_PRECIPITATION == 1)]
precipitationDelays = totalDelays[(totalDelays.ORIGIN_HAS_PRECIPITATION == 1) | (totalDelays.DEST_HAS_PRECIPITATION == 1)]
print "Flights delayed when extreme conditions upon departure/arrival: ", extremeDelays.size / totalDelays.size * 100, "%"
print "Percentage of flights delayed when extreme conditions occure: ", extremeDelays.size / extremeFlights.size * 100, "%"
print "Flights delayed when precipitation upon departure/arrival: ", precipitationDelays.size / totalDelays.size * 100, "%"
print "Percentage of flights delayed when precipitation occures: ", precipitationDelays.size / precipitationFlights.size * 100, "%"

#landing wind speed vs delays
print "Landing wind speed (1-weak 5-strong) vs delay:"
windDf = df2
smallest = np.min(windDf['DEST_WIND_SPEED'])
largest = np.max(windDf['DEST_WIND_SPEED'])
num_edges = 5
windDf['BINNED_DEST_WIND_SPEED'] = np.digitize(windDf['DEST_WIND_SPEED'], np.linspace(smallest, largest, num_edges))
print np.linspace(smallest, largest, num_edges)
windDf = windDf.groupby(['BINNED_DEST_WIND_SPEED'])['ARR_DELAY'].mean()
windDf = windDf.sort_values()
print windDf

#drop redundant columns
#df2 = df2.drop('UNIQUE_CARRIER', axis=1)
#df2 = df2.drop('ORIGIN', axis=1)
#df2 = df2.drop('DEST', axis=1)
#df2 = df2.drop('ORIGIN_AIRPORT_ID', axis=1)
#df2 = df2.drop('DEST_AIRPORT_ID', axis=1)
#df2 = df2.drop('CANCELLED', axis=1)
#df2 = df2.drop('DIVERTED', axis=1)

# remove INF and NaN's from the dataframe
#print df2.isnull().values.any()
#df2 = df2.replace([np.inf, -np.inf], np.nan)
#df2 = df2.fillna(0)
#print df2.isnull().values.any()

#print df2.describe()
#print "###############################################"
#print df2.dtypes
#print "###############################################"
#print np.where(np.isnan(df2))

# assign final dataFrame to X, which will be used as a basis for train/test split
#X = df2.drop('ARR_DELAY', axis=1)

