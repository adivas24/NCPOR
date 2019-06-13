# plot_functions.py #

import gl_vars
import file_functions as ffunc

import xarray as xr
import numpy as np
import pandas as pd
import geopandas as gpd
# Used for data manipulation and numerical calculations. 

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
# Used for plotting

import fiona
import shapely.geometry as sgeom
from rasterio import features
from affine import Affine
# Used for reading and applying shapefile mask.


# TODO	Plot only in a rectangular/polar range?
#		Look into time-varying graphs and how they can be plotted.
# 		Write code for non-map graphs.
#		Figure out how to modify the size of maps and maybe make it dynamic?


def onclick(event):
		print(event.button, event.x, event.y, event.xdata, event.ydata)


# PRE-CONDITION
#	ind: The index of the page selected as an integer.
#	var_name: The name of the variable in question as a String.
#	time_index: The index of the time we are plotting the data for, as an integer.
#	shpfile: The name of the shapefile as a string. If None, no shape filters are applied.
#	plac_ind: The index of the place (shape selected from the Shapefile) as an integer. If None, not All are chosen
def plotMapShape(ind,var_name, time_index, shpfile, plac_ind):
	pc = ccrs.PlateCarree() #Later this needs to be user-input.
	xds, lon_var, lat_var, geometries = ffunc.getShapeData(ind, var_name, time_index, shpfile, plac_ind)
	fig = plt.figure()
	ax = plt.axes(projection=pc)
	kwargs = dict(ax=ax, transform=pc, x=lon_var, y=lat_var, cbar_kwargs=dict(orientation='horizontal'))
	xds.plot.pcolormesh(**kwargs)
	if (geometries is not None):
		ax.add_geometries(geometries, pc, edgecolor='gray', facecolor='none')
	else:
		ax.coastlines()
	ax.set_global()
	plt.show()
# POST-CONDITION
#	The map with the specified variable, time, and shape is plotted in a matplotlib pop-up window.