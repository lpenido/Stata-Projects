import sqlite3
import os

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

# Pretty printing pandas
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

data_directory = "/".join(os.getcwd().split("/")[:-2]) + "/data/"
db_file = data_directory + "housing.db"

query = """
SELECT COUNT(Pin) AS PinCount, SaleDate, NeighborhoodCode, SUM(SalePrice) AS SalePriceSum
FROM sales
GROUP BY NeighborhoodCode
ORDER BY SaleDate, NeighborhoodCode;
"""

all_q = """
SELECT *
FROM sales
LIMIT 500;
"""

with sqlite3.connect(db_file) as conn:
    df = pd.read_sql(query, conn)
    all = pd.read_sql(all_q, conn)

df = df.replace(np.nan, 0)
df["SaleDate"] = df["SaleDate"].astype("datetime64")

def make_count_plot():
    df = df.groupby("SaleDate").agg({
            "PinCount" : "sum",
            "SalePriceSum": "sum"})

    fig, ax = plt.subplots()
    df['PinCount'].plot(ax=ax)
    ax.set_xlabel('Sale Date')
    ax.set_ylabel('Number of Sales')
    ax.set_title('Chicago Housing Sales')
    plt.show()


def make_corr_matrix(df):

    # Numeric columns of the dataset
    numeric_col = ['temp','atemp','hum','windspeed']
    # corr_matrix = df.loc[:,numeric_col].corr()

    # Correlation Matrix formation
    corr_matrix = df.corr()
    print(corr_matrix)

    # Fireplaces                     0.393591
    # CondoStrata                    0.517080
    # Estimate(Land)                 0.588660
    # Estimate(Building)             0.695387
    # TotalBuildingSquareFeet        0.992434

    #Using heatmap to visualize the correlation matrix
    # sns.heatmap(corr_matrix, annot=True)
    # plt.show()

make_corr_matrix(all)
breakpoint()
