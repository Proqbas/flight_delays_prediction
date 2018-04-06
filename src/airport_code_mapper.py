from __future__ import division
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv('../data/airports.csv')

col_list = ['IATA', 'ICAO']
df2 = df[col_list]

print df2.head()

df2.drop(df2[df2.IATA == "\N"].index, inplace=True)
df2.to_csv('../data/iata_icao_mapping.csv', index=False)
print "IATA-ICAO mapping file created successfully"
