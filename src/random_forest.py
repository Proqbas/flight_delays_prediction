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

#change IATA to ICAO codes
df['ORIGIN'] = df['ORIGIN'].map(airport_codes_df.set_index('IATA')['ICAO'])
df['DEST'] = df['DEST'].map(airport_codes_df.set_index('IATA')['ICAO'])

#replace airport codes with airport sizes category (0-4)
df['ORIGIN_SIZE'] = df['ORIGIN'].map(airport_sizes_df.set_index('ICAO')['AIRPORT_SIZE'])
df['DEST_SIZE'] = df['DEST'].map(airport_sizes_df.set_index('ICAO')['AIRPORT_SIZE'])
df['ORIGIN_SIZE'] = df['ORIGIN_SIZE'].astype('float32')
df['DEST_SIZE'] = df['DEST_SIZE'].astype('float32')

#prepare data for random forest
df2 = df

df2['UNIQUE_CARRIER'] = df2['UNIQUE_CARRIER'].astype('category')
df2['UNIQUE_CARRIER_CODE'] = df2['UNIQUE_CARRIER'].cat.codes

#drop redundant columns
df2 = df2.drop('UNIQUE_CARRIER', axis=1)
#df2 = df2.drop('CRS_DEP_TIME', axis=1)
#df2 = df2.drop('CRS_ARR_TIME', axis=1)
df2 = df2.drop('ORIGIN', axis=1)
df2 = df2.drop('DEST', axis=1)

# remove INF and NaN's from the dataframe
print df2.isnull().values.any()
df2 = df2.replace([np.inf, -np.inf], np.nan)
df2 = df2.fillna(0)
print df2.isnull().values.any()

print df2.describe()
print "###############################################"
print df2.dtypes
print "###############################################"
print np.where(np.isnan(df2))

# assign final dataFrame to X, which will be used as a basis for train/test split
X = df2.drop('ARR_DELAY', axis=1)

#################################################################################################
#### GET METARS AND UPDATE WEATHER DATA IN THE DATA FRAME ----> HERE <----                   ####

#### MOVE THE NEXT PART (Linear Regression + other models) to Model_Retrainer component      ####
#################################################################################################

#split the set into train and test subsets
X_train, X_test, Y_train, Y_test = sklearn.cross_validation.train_test_split(X, df2.ARR_DELAY, test_size=0.33, random_state=5)
print "Train & Test datasets shapes:"
print X_train.shape
print X_test.shape
print Y_train.shape
print Y_test.shape

#plt.hlines(y = 0, xmin = -10, xmax = 30)
#plt.show()

#do the actual Linear Regression
regr = RandomForestRegressor(max_depth=2, random_state=0)
regr.fit(X_train, Y_train)

print "features coefficients (importances): \n",  regr.feature_importances_

regr.predict(X_test)

print "train set R^2 error: ", regr.score(X_train, Y_train)
print "test set R^2 error: ", regr.score(X_test, Y_test)

#linear regression for comparison
lm = LinearRegression()
lm.fit(X_train, Y_train)
lm_result = lm.predict(X_test)

#Assess the LM's results 
print "MSE of train set: ", np.mean((Y_train - lm.predict(X_train)) ** 2)
print "MSE of test set: ", np.mean((Y_test - lm.predict(X_test)) ** 2)
print "RMSE of train set: ", np.sqrt(np.mean((Y_train - lm.predict(X_train)) ** 2))
print "RMSE of test set: ", np.sqrt(np.mean((Y_test - lm.predict(X_test)) ** 2))
