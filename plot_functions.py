# plot_functions.py #

import gl_vars
import file_functions as ffunc

import xarray as xr
import numpy as np
import pandas as pd
import geopandas as gpd
# Used for data manipulation and numerical calculations. 
import cartopy 
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
def plotMapShape(ind,var_name, time_index, shpfile, plac_ind, proj_string):

	proj_list = ["PlateCarree","AlbersEqualArea","AzimuthalEquidistant","EquidistantConic","LambertConformal","LambertCylindrical","Mercator","Miller","Mollweide","Orthographic","Robinson","Sinusoidal","Stereographic","TransverseMercator","UTM","InterruptedGoodeHomolosine","RotatedPole","OSGB","EuroPP","Geostationary","NearsidePerspective","EckertI","EckertII","EckertIII","EckertIV","EckertV","EckertVI","EqualEarth","Gnomonic","LambertAzimuthalEqualArea","NorthPolarStereo","OSNI","SouthPolarStereo"]
	pc = ccrs.PlateCarree() #Later this needs to be user-input.
	proj = getProjection(proj_string)
	xds, lon_var, lat_var, geometries = ffunc.getShapeData(ind, var_name, time_index, shpfile, plac_ind)
	fig = plt.figure()
	ax = plt.axes(projection=proj)
	kwargs = dict(ax=ax, transform=pc, x=lon_var, y=lat_var, cbar_kwargs=dict(orientation='horizontal'))
	xds.plot.pcolormesh(**kwargs)
	if (geometries is not None):
		ax.add_geometries(geometries, pc, edgecolor='gray', facecolor='none')
	else:
		ax.coastlines()
	ax.set_global()
	fig.text(0,0, "Mean: "+ str(np.nanmean(np.array(xds)))+ " Standard Deviation: "+ str(np.nanstd(np.array(xds))))
	plt.show()
# POST-CONDITION
#	The map with the specified variable, time, and shape is plotted in a matplotlib pop-up window.

def getProjection(proj_string):
	proj_dict = {
	# ALLOW SELECTION OF PARAMETERS TO THE PROJECTION. RIGHT NOW EVERYTHING IS SET TO DEFAULTS (ESPECIALLY UTM)
	"PlateCarree": ccrs.PlateCarree(),
	"AlbersEqualArea":ccrs.AlbersEqualArea(),
	"AzimuthalEquidistant":ccrs.AzimuthalEquidistant(),
	"EquidistantConic":ccrs.EquidistantConic(),
	"LambertConformal":ccrs.LambertConformal(),
	"LambertCylindrical":ccrs.LambertCylindrical(),
	"Mercator":ccrs.Mercator(),
	"Miller":ccrs.Miller(),
	"Mollweide":ccrs.Mollweide(),
	"Orthographic":ccrs.Orthographic(),
	"Robinson":ccrs.Robinson(),
	"Sinusoidal":ccrs.Sinusoidal(),
	"Stereographic":ccrs.Stereographic(),
	"TransverseMercator":ccrs.TransverseMercator(),
	"UTM":ccrs.UTM(5),
	"InterruptedGoodeHomolosine":ccrs.InterruptedGoodeHomolosine(),
	"RotatedPole":ccrs.RotatedPole(),
	"OSGB":ccrs.OSGB(),
	"EuroPP":ccrs.EuroPP(),
	"Geostationary":ccrs.Geostationary(),
	"NearsidePerspective":ccrs.NearsidePerspective(),
	"EckertI":ccrs.EckertI(),
	"EckertII":ccrs.EckertII(),
	"EckertIII":ccrs.EckertIII(),
	"EckertIV":ccrs.EckertIV(),
	"EckertV":ccrs.EckertV(),
	"EckertVI":ccrs.EckertVI(),
	"EqualEarth":ccrs.EqualEarth(),
	"Gnomonic":ccrs.Gnomonic(),
	"LambertAzimuthalEqualArea":ccrs.LambertAzimuthalEqualArea(),
	"NorthPolarStereo":ccrs.NorthPolarStereo(),
	"OSNI":ccrs.OSNI(),
	"SouthPolarStereo":ccrs.SouthPolarStereo()
	}
	return proj_dict[proj_string]