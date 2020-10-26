import glob
import os
import pandas as pd

seed = 1234
sample_number = 8
data_directory = os.getcwd() + "/data/"

#
raw_csv = glob.glob(data_directory + "/*.csv")[0]
df = pd.read_csv(raw_csv)

# Sample
sample = df.sample(frac=(1/sample_number), random_state=seed)
sample_name = data_directory + "01_sample.csv"
sample.to_csv(sample_name, index=False)
