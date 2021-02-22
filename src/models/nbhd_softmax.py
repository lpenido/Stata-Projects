import sqlite3
import os
import rfpimp

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score

# Pretty printing pandas
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

data_directory = "/".join(os.getcwd().split("/")[:-2]) + "/data/"
db_file = data_directory + "housing.db"

#
query = """
SELECT Pin, SalePrice, LandSquareFeet, FullBaths, Age, Bedrooms, NeighborhoodCode
FROM sales
LIMIT 500;
"""

with sqlite3.connect(db_file) as conn:
    df = pd.read_sql(query, conn, index_col="Pin")
    df = df.replace(np.nan, 0)

features = df.columns.to_list()
features.remove('NeighborhoodCode')

X = df["SalePrice"].values.reshape(-1,1)
y = df['NeighborhoodCode'].values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=1)

label_encoder = LabelEncoder()
label_encoder.fit(y)
y_train = label_encoder.transform(y_train)
y_test = label_encoder.transform(y_test)

model = LogisticRegression(max_iter=10000, multi_class="multinomial")
# fit the model
model.fit(X, y)
# get importance
importance = model.coef_[0]
# summarize feature importance
for i,v in enumerate(importance):
	print('Feature: %0d, Score: %.5f' % (i,v))
# plot feature importance
plt.bar([x for x in range(len(importance))], importance)
plt.show()

breakpoint()


# logr = LogisticRegression(max_iter=10000, multi_class="multinomial")
# model = logr.fit(X, y)
# response = model.predict(X)
# score = model.score(X, y)
#
# breakpoint()
