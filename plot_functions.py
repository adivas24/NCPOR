import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import geopandas as gpd
import fiona
import shapely.geometry as sgeom
import numpy as np
import xarray as xr
import pandas as pd
from rasterio import features
from affine import Affine
import gl_vars
import re

##TODO. Merge the common parts of the two functions into a map init called at the start of both functions?
##Look into time-varying graphs and how they can be plotted.
## Write code for non-mapping graphs.

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

def plotMapShape(ind,var_name, time_index, shpfile, plac_ind):

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

	plt.figure()
	ax = plt.axes(projection=ccrs.PlateCarree())
	kwargs = dict(ax=ax, transform=pc, x=lon_var, y=lat_var, cbar_kwargs=dict(orientation='horizontal'))

	xds = da_2.where(~np.isnan(da_2[var_name]),other = np.nan)
	xds.plot.pcolormesh(**kwargs)
	ax.add_geometries(geometries, pc, edgecolor='gray', facecolor='none')

	ax.set_global()

	plt.show()