import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

directory = '/Users/lucaspenido/Desktop/house_price_model/data'
file = 'ChicagoPropertiesSample.csv'
os.chdir(directory)
df = pd.read_csv(file)

print(df.shape)
print(df.columns)
print(df.head())
