from __future__ import division
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import sklearn.cross_validation
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import metartest

#read the CSV file
df = pd.read_csv('../data/trimmed_february_2017.csv')
airport_codes_df = pd.read_csv('../data/iata_icao_mappings.csv')

#remove the last (empty) column as well as diverted and cancelled flights
df.drop(df.columns[len(df.columns)-1], axis=1, inplace=True)
df.drop(df[df.DIVERTED == 1].index, inplace=True)
df.drop(df[df.CANCELLED == 1].index, inplace=True)

#check for NaN's
print df.isnull().sum()
print "####################################################"

#look at our data frame
print df.dtypes
print df.describe()

#change IATA to ICAO codes
df['Origin'] = df['Origin'].map(airport_codes_df.set_index('IATA')['ICAO'])
df['Dest'] = df['Dest'].map(airport_codes_df.set_index('IATA')['ICAO'])

#calculate percentage of delays >1h and >10h
total = len(df)
print "Total flights: ", total

print "Delay > 1h"
delay1h = len(df[df.ARR_DELAY > 60])
print(str(delay1h) + " - " + str(round(delay1h/total, 30))  +  "% of all flights")

print "Delay > 10h"
delay10h = len(df[df.ARR_DELAY > 600])
print(str(delay10h) + " - " + str(round(delay10h/total, 30))  +  "% of all flights")

print "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"

# ??? TEMP ??? ??? TEMP ??? ??? TEMP ??? ??? TEMP ??? ??? TEMP ??? ??? TEMP ??? ??? TEMP ???

def update_weather_data_for_row(row):
	find_most_accurate_metar(row.ORIGIN_AIRPORT, year, month, day, time)	

df.apply(update_weather_data_for_row, axis=1)

# ??? TEMP ??? ??? TEMP ??? ??? TEMP ??? ??? TEMP ??? ??? TEMP ??? ??? TEMP ??? ??? TEMP ???


#prepare data for linear regression
df2 = df

df2['UNIQUE_CARRIER'] = df2['UNIQUE_CARRIER'].astype('category')
df2['UNIQUE_CARRIER_CODE'] = df2['UNIQUE_CARRIER'].cat.codes
df2 = df2.drop('UNIQUE_CARRIER', axis=1)

#print (df2[ pd.to_numeric(df2['CRS_ARR_TIME'], errors='coerce').isnull()])
#df2['CRS_ARR_TIME_HOUR'] = pd.to_numeric(str(df['CRS_ARR_TIME']), errors='coerce')
#df2['CRS_ARR_TIME_HOUR'] = pd.to_datetime(df2['CRS_ARR_TIME'], format='%H%M').dt.hour
#df2['CRS_ARR_TIME_HOUR'] = int(str(df2.CRS_ARR_TIME)[:2])
#df2['CRS_ARR_TIME_MINS'] = int(str(df2.CRS_ARR_TIME)[2:])
#df2['CRS_DEP_TIME_HOUR'] = int(str(df2.CRS_DEP_TIME)[:2])
#df2['CRS_DEP_TIME_MINS'] = int(str(df2.CRS_DEP_TIME)[2:])

df2 = df2.drop('CRS_DEP_TIME', axis=1)
df2 = df2.drop('CRS_ARR_TIME', axis=1)

X = df2.drop('ARR_DELAY', axis=1)

#################################################################################################
#### GET METARS AND UPDATE WEATHER DATA IN THE DATA FRAME ----> HERE <----                   ####

#### MOVE THE NEXT PART (Linear Regression + other models) to Model_Retrainer component      ####
#################################################################################################

#do the actual Linear Regression
X_train, X_test, Y_train, Y_test = sklearn.cross_validation.train_test_split(X, df2.ARR_DELAY, test_size=0.33, random_state=5)
print "Train & Test datasets shapes:"
print X_train.shape
print X_test.shape
print Y_train.shape
print Y_test.shape

lm = LinearRegression()
lm.fit(X_train, Y_train)
print "Estimated intercept coefficient: ", lm.intercept_
print "Number of coefficients: ", len(lm.coef_)

dfCoef = pd.DataFrame(zip(X.columns, lm.coef_), columns=['feature', 'estimated coefficient'])
print dfCoef

pred_train = lm.predict(X_train)
pred_test = lm.predict(X_test)

for i in range (0, 100):	
	print "pred_test[]: ", pred_test[i]
	print "y_test[]: ", Y_test.iloc[i]

with open('predTest.txt', 'w') as file:
	for x in pred_test:
		file.write(str(x) + "\n")

print "mean of predicted values: ", np.mean(pred_test)

#Assess the results 
print "MSE of train set: ", np.mean((Y_train - lm.predict(X_train)) ** 2)
print "MSE of test set: ", np.mean((Y_test - lm.predict(X_test)) ** 2)
print "RMSE of train set: ", np.sqrt(np.mean((Y_train - lm.predict(X_train)) ** 2))
print "RMSE of test set: ", np.sqrt(np.mean((Y_test - lm.predict(X_test)) ** 2)) 

plt.scatter(lm.predict(X_train), lm.predict(X_train) - Y_train, c='b', s=40, alpha=0.5)
plt.scatter(lm.predict(X_test), lm.predict(X_test) - Y_test, c='g', s=40, alpha=0.51)

plt.hlines(y = 0, xmin = -10, xmax = 30)

plt.show()
