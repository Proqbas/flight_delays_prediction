from __future__ import division
from sklearn.linear_model import LinearRegression
import sklearn.cross_validation
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv('../data/february_2017.csv')

#ax = df['CARRIER_DELAY'].plot(kind='bar')
#ax = df['DAY_OF_MONTH'].plot()
#fig = ax.get_figure() 
#fig.savefig('output.png')i

#remove the last (empty) column as well as diverted and cancelled flights
df.drop(df.columns[len(df.columns)-1], axis=1, inplace=True)
df.drop(df[df.DIVERTED == 1].index, inplace=True)
df.drop(df[df.CANCELLED == 1].index, inplace=True)

#check for NaN's
print df.isnull().sum()
print "####################################################"

#look at our data frame
print df.describe()

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

#prepare data for linear regression
df2 = df
df2['UNIQUE_CARRIER'] = df2['UNIQUE_CARRIER'].astype('category')
df2['UNIQUE_CARRIER_CODE'] = df2['UNIQUE_CARRIER'].cat.codes

df2 = df2.drop('UNIQUE_CARRIER', axis=1)
X = df2.drop('ARR_DELAY', axis=1)

#fit the model
lm = LinearRegression()
lm.fit(X, df2.ARR_DELAY)
print "Estimated intercept coefficient: ", lm.intercept_
print "Number of coefficients: ", len(lm.coef_)

dfCoef = pd.DataFrame(zip(X.columns, lm.coef_), columns=['feature', 'estimated coefficient'])
print dfCoef

#do the actual Linear Regression
#split the set into train & test
X_train, X_test, Y_train, Y_test = sklearn.cross_validation.train_test_split(X, df2.ARR_DELAY, test_size=0.33, random_state=5)
print X_train.shape
print X_test.shape
print Y_train.shape
print Y_test.shape

lm = LinearRegression()
lm.fit(X_train, Y_train)
pred_train = lm.predict(X_train)
pred_test = lm.predict(X_test)

print "Fit a model X_train, and calculate MSE with Y_train:", np.mean((Y_train - lm.predict(X_train)) ** 2)
print "Fit a model X_test, and calculate MSE with Y_test:", np.mean((Y_test - lm.predict(X_test)) ** 2)
