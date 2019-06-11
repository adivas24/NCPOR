# plot_functions.py #

import gl_vars

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


# TODO	Merge the common parts of the two functions into a map init called at the start of both functions?
#		Look into time-varying graphs and how they can be plotted.
# 		Write code for non-map graphs.
#		Figure out how to modify the size of maps and maybe make it dynamic?

# PRE-CONDITION
#	ind: The index of the page, represents the NETCDF file being queried as an integer.
#	var_name: The name of the variable being queried, in the form of a string.
#	time_index: The index (as an integer) of the time point selected, at which the shape is being generated. If None, data across the entire range is returned as a list.
#	gl_vars.data needs to have been initialized before function call.
def plotMapFull(ind, var_name, time_index):
	
	pc = ccrs.PlateCarree() #Later this needs to be user-input.

	xds = gl_vars.data[ind]
	lon_var = None
	lat_var = None
	for a in list(xds.dims):
		if (a.lower().startswith("lon")):
			lon_var = a
		if (a.lower().startswith("lat")):
			lat_var = a
	if (lon_var is None or lat_var is None):
		return
	xds.assign_coords(longitude=(((xds.variables[lon_var][:] + 180.0) % 360.0) - 180.0))
	da1 =  xds.data_vars[var_name][time_index,:,:]  #THIS IS WRONG. NEEDS TO BE READ FROM NC DATA
	da1 = da1.sortby(da1[lon_var])
	plt.figure()
	ax = plt.axes(projection=pc)
	kwargs = dict(ax=ax, transform=pc, x=lon_var, y=lat_var, cbar_kwargs=dict(orientation='horizontal'))
	da1.plot.pcolormesh(**kwargs)
	ax.set_global()
	ax.coastlines()
	plt.show()
# POST-CONDITION
#	The map is displayed in a new window, basic zoom functionality is inbuilt through the matplotlib window.

#PRE-CONDITION
#	ind: The index of the page, represents the NETDCF file being queried as an integer.
#	var_name: The name of the variable being queried, in the form of a string. If None, it indicates all variables slected should be considered.
#	time_index: The index (as an integer) of the time point selected, at which the shape is being generated. If None, data across the entire range is returned as a list.
#	shpfile: A string containing the name and path of the SHAPEFILE(.shp) being used.
#	plac_ind: As of now, it is a single integer containing the index of the place (specific geometry) selected by the user from the SHAPEFILE. None indicates the entire file being used. In the future a list should be passed, which can accurately select multiple but not all the places present. Maybe through a clickable-map interface.
#	gl_vars.data should be initialized before the function call.
def plotMapShape(ind,var_name, time_index, shpfile, plac_ind):

	# A significant portion of this function can be replaced by a functions call to the one in file functions. Might reduce the number of imports at the top too.
	pc = ccrs.PlateCarree()  #Needs to be user input in the future.
	xds = gl_vars.data[ind]
	for a in list(xds.dims):
		if (a.lower().startswith("lon")):
			lon_var = a
		if (a.lower().startswith("lat")):
			lat_var = a
	if (lon_var is None or lat_var is None):
		return
	xds = xds.assign_coords(longitude=(((xds.variables[lon_var][:] + 180.0) % 360.0) - 180.0))
	da1 =  xds.data_vars[var_name][time_index,:,:]   #THIS IS WRONG. NEEDS TO BE READ FROM NC DATA
	da1 = da1.sortby(da1[lon_var])
	test = gpd.read_file(shpfile)
	with fiona.open(shpfile) as records:
		geometries = [sgeom.shape(shp['geometry']) for shp in records]
	shapes = [(shape, n) for n,shape in enumerate(test.geometry)]
	lat = np.asarray(da1.coords[lat_var])
	lon = np.asarray(da1.coords[lon_var])
	trans = Affine.translation(lon[0], lat[0])
	scale = Affine.scale(lon[1]- lon[0], lat[1] - lat[0])
	transform = trans*scale
	out_shape = (len(da1.coords[lat_var]), len(da1.coords[lon_var]))
	if (plac_ind is not None):
		shape_i = [shapes[plac_ind]]
	else:
		shape_i = shapes
	raster = features.rasterize(shape_i, out_shape=out_shape, fill = np.nan, transform = transform, dtype=float)
	spatial_coords = {lat_var: da1.coords[lat_var], lon_var: da1.coords[lon_var]}
	da1[var_name] = xr.DataArray(raster, coords=spatial_coords, dims=(lat_var, lon_var))
	da_2 = da1

	fig = plt.figure()
	ax = plt.axes(projection=ccrs.PlateCarree())
	kwargs = dict(ax=ax, transform=pc, x=lon_var, y=lat_var, cbar_kwargs=dict(orientation='horizontal'))

	xds = da_2.where(~np.isnan(da_2[var_name]),other = np.nan)
	xds.plot.pcolormesh(**kwargs)
	ax.add_geometries(geometries, pc, edgecolor='gray', facecolor='none')

	ax.set_global()
	cid = fig.canvas.mpl_connect('button_press_event', onclick)
	plt.show()
# POST-CONDITION
#	The map is displayed in a new window, basic zoom functionality is inbuilt through the matplotlib window.

def onclick(event):
		print(event.button, event.x, event.y, event.xdata, event.ydata)