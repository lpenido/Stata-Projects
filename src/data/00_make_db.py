#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Lucas Penido
#   lpenido1@gmail.com

import sqlite3
import os
from functools import reduce

import pandas as pd
import geopandas as gpd

"""
Usually I'd go with a straight forward pd.read_csv but hopefully there'll be
more data to relate to the original.

TODO:
- Add Monthly Fed Rates for Poisson Regression
-
"""

# Setting up constants
root_directory = "/".join(os.getcwd().split("/")[:5])
data_directory = root_directory + "/data/"
layer_directory = root_directory + "/layers/"
db_file = data_directory + "chicago.db"

def format_column_names(df):
    new_names = map(lambda x : x.title(), df.columns)
    new_names = map(lambda x : x.replace(" ",""), new_names)
    df.columns = list(new_names)
    return df

def csv_load(table_name, csv_name, con):
    df = pd.read_csv(data_directory + csv_name)
    df = format_column_names(df)
    df.to_sql(table_name, con=con, if_exists="replace", index=True)

def unpack_location(location):
    try:
        location = location.replace("(", "")
        location = location.replace(")", "")
        location = location.replace(" ", "")
        location = location.split(",")
        return location
    except AttributeError:
        return (None, None)

def load_layers():

    print("Loading layers...")
    tracts = layer_directory + "Boundaries - Census Tracts - 2010/tracts2010.shp"
    areas = layer_directory + "Boundaries - Community Areas (current)/community_areas.shp"
    wards15 = layer_directory + "Boundaries - Wards (2015-)/wards_2015.shp"
    wards03 = layer_directory + "Boundaries - Wards (2003-2015)/wards_2003.shp"

    areas = gpd.read_file(areas)
    tracts = gpd.read_file(tracts)
    wards15 = gpd.read_file(wards15)
    wards03 = gpd.read_file(wards03)
    print("Loaded layers.")

    return (areas, tracts, wards15, wards03)

def geo_load(table_name, csv_name, con, layers=load_layers(), loc_column="Location_1"):

    point_csv = pd.read_csv(data_directory + csv_name)
    point_csv = format_column_names(point_csv)

    assert loc_column in list(point_csv.columns)
    point_csv["Latitude"] = point_csv[loc_column].apply(lambda x: unpack_location(x)[0])
    point_csv["Longitude"] = point_csv[loc_column].apply(lambda x: unpack_location(x)[1])

    points_df = gpd.GeoDataFrame(point_csv, geometry=gpd.points_from_xy(point_csv.Longitude, point_csv.Latitude))
    points_df = points_df.copy().set_crs(epsg=4326)
    clean_points = points_df.dropna(subset=['Longitude', 'Latitude'])

    areas_pins = gpd.sjoin(clean_points, layers[0], op="within")[["Pin", "community"]] # community
    tracts_pins = gpd.sjoin(clean_points, layers[1], op="within")[["Pin", "tractce10"]] # tractce10
    wards15_pins = gpd.sjoin(clean_points, layers[2], op="within")[["Pin", "ward"]]
    wards03_pins = gpd.sjoin(clean_points, layers[3], op="within")[["Pin", "ward"]]

    dfs = [areas_pins, tracts_pins, wards15_pins, wards03_pins]
    df_final = reduce(lambda left,right: pd.merge(left,right,on='Pin'), dfs)
    df_final = df_final.drop_duplicates(subset=['Pin'], keep="first")

    df_final.to_sql(table_name, con=con, if_exists='replace', index=True)


def make_table(table_name, csv_name, geo=False):
    """A quick wrapper for making tables"""
    with sqlite3.connect(db_file) as con:

        c = con.cursor()
        check = "SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{table_name}'".format(table_name=table_name)
        c.execute(check)

        if c.fetchone()[0] != 1:
            # Loading in data with nice column names
            print("Making {table_name}...".format(table_name=table_name))
            if geo:
                geo_load(table_name, csv_name, con)
            else:
                csv_load(table_name, csv_name, con)

        else:
            print("Table {table_name} exists.".format(table_name=table_name))

if __name__ == "__main__":
    make_table("sales", "Residential_Sales_Data.csv")
    make_table("com_areas", "com_areas_demos.csv")
    make_table("tax_annual", "Treasurer_-_Annual_Tax_Sale.csv")
    make_table("tax_annual_lookup", "Treasurer_-_Annual_Tax_Sale.csv", geo=True)
