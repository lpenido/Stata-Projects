import glob
import os
import pandas as pd

# Pretty printing pandas
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

data_directory = os.getcwd() + "/data/"

# Shape (72921, 83)
raw_csv = glob.glob(data_directory + "/*.csv")[1]
df = pd.read_csv(raw_csv)

corrMatrix = df.corr()
corrMatrix.sort_values(by=["Sale Price"], inplace=True)
print(corrMatrix["Sale Price"])
