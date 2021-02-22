#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Lucas Penido
#   lpenido1@gmail.com
import os
import sqlite3

import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import geopandas as gpd
import mapclassify as mc
from pysal.lib import weights
from pysal.lib import cg as geometry
import contextily
from shapely.geometry import Polygon

# Constants
root_directory = "/".join(os.getcwd().split("/")[:5])
fig_directory = root_directory + "/figures/"
data_directory = root_directory + "/data/"
layer_directory = root_directory + "/layers/"
db_file = data_directory + "chicago.db"

# Polygon Layer
areas = layer_directory + "Boundaries - Community Areas (current)/community_areas.shp"
areas = gpd.read_file(areas)

# Polygon shaped data
com_area = """
SELECT UPPER(GEOG) AS community, Medinc AS MedInc
FROM com_areas;
"""
with sqlite3.connect(db_file) as conn:
    df = pd.read_sql(com_area, conn, index_col="community") # THE LOOP / O'HARE

df.index = df.index.str.replace("THE LOOP", "LOOP")
df.index = df.index.str.replace("O'HARE", "OHARE")

def connectivity_plot(gdf, figname):
    """ """
    wq = weights.contiguity.Queen.from_dataframe(gdf)

    fig1, ax1 = plt.subplots(1, figsize=(9, 9))
    wq.plot(gdf, ax=ax1)
    gdf.plot(facecolor='w', edgecolor='k', ax=ax1)

    fig2, ax2 = plt.subplots(1, figsize=(9, 9))
    neighbors = pd.Series(wq.cardinalities, name="Neighbors")
    sns.histplot(data=neighbors)

    fig1.savefig(fig_directory + figname + "_con_plot.png")
    fig2.savefig(fig_directory + figname + "_nbrs_plot.png")

def get_counts_bins(series, bins):
    """Helper function"""
    # "counts" stores how many observations
    # "bin" stores break points
    h = sns.histplot(series, bins=bins)
    counts, bins, patches = h.hist(series, bins=bins)
    return counts, bins, patches

def classifier_comps(df, series, bins=5, figname=""):
    """ """

    series = df[series]
    counts, bins, patches = get_counts_bins(series, bins)

    ei = mc.EqualInterval(series, k=5)
    q = mc.Quantiles(series, k=5)
    msd = mc.StdMean(series)
    mb = mc.MaximumBreaks(series, k=5)
    ht = mc.HeadTailBreaks(series)
    jc = mc.JenksCaspall(series, k=5)
    fj = mc.FisherJenks(series, k=5)
    mp = mc.MaxP(series, k=5)

    # ADCM is “absolute deviation around class medians”, it provides a measure
    # of fit to compare classifiers for the same value of 𝑘
    classifiers = ei, q, msd, mb, ht, jc, fj, mp
    fits = np.array([ c.adcm for c in classifiers])
    data = pd.DataFrame(fits)
    data['classifier'] = [c.name for c in classifiers]
    data.columns = ['ADCM', 'Classifier']

    fig1, ax1 = plt.subplots(1, figsize=(9, 13))
    ax1 = sns.barplot(y='Classifier', x='ADCM', data=data)
    fig1.savefig(fig_directory + figname + "_class_adcm.png")

def chloro_plot(gdf, df, figname="", scheme="equalinterval"):
    """ """
    gdf = gdf.merge(df, on='community')

    fig, ax = plt.subplots(1, figsize=(9, 9))
    gdf.plot(ax=ax,
             column='MedInc',
             scheme=scheme,
             edgecolor='black',
             linewidth=0.4,
             legend=True,
             legend_kwds={'title': 'Median Income',
                          'loc': 'lower left',
                          'fontsize': 8})
    ax.set_axis_off()
    ax.set_title('Median Income in Chicago Neighborhoods')
    plt.axis('equal')

    fig.savefig(fig_directory + figname + "_{scheme}.png".format(scheme=scheme))

if __name__ == "__main__":
    connectivity_plot(areas, figname="com_areas")
    classifier_comps(df, "MedInc", figname="med_inc")
    chloro_plot(areas, df, figname="com_areas_med_inc")
