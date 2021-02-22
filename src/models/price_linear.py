import sqlite3
import os
import rfpimp

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

# Pretty printing pandas
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

data_directory = "/".join(os.getcwd().split("/")[:-2]) + "/data/"
db_file = data_directory + "housing.db"

query = """
SELECT Pin, SalePrice, LandSquareFeet, FullBaths, Age, Bedrooms, SaleDate
FROM sales
LIMIT 500;
"""

with sqlite3.connect(db_file) as conn:
    df = pd.read_sql(query, conn, index_col="Pin")
    df = df.replace(np.nan, 0)

features = df.columns.to_list()

df_train, df_test = train_test_split(df, test_size=0.20)
X_train, y_train = df_train.drop('SalePrice',axis=1), df_train['SalePrice']
X_test, y_test = df_test.drop('SalePrice',axis=1), df_test['SalePrice']

def make_importance_plot():

    rf = RandomForestRegressor(n_estimators=100, n_jobs=-1)
    rf.fit(X_train, y_train)

    imp = rfpimp.importances(rf, X_test, y_test)

    fig, ax = plt.subplots(figsize=(6, 3))

    ax.barh(imp.index, imp['Importance'], height=0.8, facecolor='grey',
            alpha=0.8, edgecolor='k')
    ax.set_xlabel('Importance score')
    ax.set_title('Permutation feature importance')
    plt.gca().invert_yaxis()

    fig.tight_layout()
    plt.show()

def make_univariate_plot():

    X = df['LandSquareFeet'].values.reshape(-1,1)
    y = df['SalePrice'].values

    ols = LinearRegression()
    model = ols.fit(X, y)
    response = model.predict(X)
    r2 = model.score(X, y)

    plt.style.use('default')
    plt.style.use('ggplot')

    fig, ax = plt.subplots(figsize=(8, 4))

    ax.plot(X, response, color='k', label='Regression model')
    ax.scatter(X, y, edgecolor='k', facecolor='grey', alpha=0.7, label='Sample data')
    ax.set_ylabel('Sale Price', fontsize=14)
    ax.set_xlabel('Land (sq. ft.)', fontsize=14)
    ax.legend(facecolor='white', fontsize=11)
    ax.set_title('$R^2= %.2f$' % r2, fontsize=18)

    fig.tight_layout()
    plt.show()

breakpoint()
# make_importance_plot()
# make_univariate_plot()
