# file_functions.py #

import gl_vars

import xarray as xr
# Used for manipulation of netCDF files and the data within them.
import numpy as np
# Used for numerical calculations.

import pandas as pd
import geopandas as gpd
# Used for some data manipulation

import fiona
import shapely.geometry as sgeom
from rasterio import features
from affine import Affine
# Used for SHAPEFILES

# TODO:
#		Correct a few errors specifically mentioned.
#		Exception, handling and fool-proofing.

# PRE-CONDITION
#	filenames: A list of strings corresponding to each NETCDF file containing the full path of the file.
def openNETCDF(filenames):
	return [xr.open_dataset(i) for i in filenames]
# POST-CONDITION
#	return value: an array containing xarray DataFrames, each corresponding to one NETCDF file.

def getSelectedMessage(ind):
	dimension_list = list(gl_vars.data[ind].coords.keys())
	mess_ind = [[None, None] for i in dimension_list]
	mess_ind_2 = [None for i in dimension_list]
	sel_message = "You have selected:\n"
	j = 0
	for x in dimension_list:
		arr = [str(a) for a in gl_vars.data[ind].variables[x].values]
		mess_ind[j][0] = arr.index(gl_vars.messages[j][0])
		sel_message += x + ' ' + str(gl_vars.data[ind].variables[x].values[mess_ind[j][0]])
		if (gl_vars.messages[j][1] is not None):
			mess_ind[j][1] = arr.index(gl_vars.messages[j][1])
			sel_message += ' : ' + str(gl_vars.data[ind].variables[x].values[mess_ind[j][1]])
			mess_ind[j].sort()
			mess_ind_2[j] = slice(mess_ind[j][0],mess_ind[j][1])
		else:
			mess_ind_2[j] = mess_ind[j][0]
		sel_message += '\n'
		j += 1
	return sel_message, mess_ind_2

def getData(ind, org, *args):
	sel_message, mess_ind_2 = getSelectedMessage(ind)
	if (org == 0):
		if (args[0] is None):
			output_message = getOutputMessage(ind, mess_ind_2,None)
		else:
			var_name = args[0]
			ord_arr = [dimension_list.index(a) for a in gl_vars.data[ind].variables[var_name].dims]
			out_ind = tuple([mess_ind_2[a] for a in ord_arr])
			output_message = gl_vars.data[ind].variables[var_name].values[out_ind]
	elif(org == 1):
		output_message = getOutputMessage(ind, mess_ind_2, args[0])
	return sel_message, output_message
				
def getOutputMessage(ind, mess_ind_2, org):
	variable_list = list(gl_vars.data[ind].data_vars.keys())
	dimension_list = list(gl_vars.data[ind].coords.keys())
	j = 0 
	ord_arr = None
	output_message = ""
	for x in variable_list:
		if(org == None):
			test_array = gl_vars.data[ind].variables[x].values
		else:
			test_array = np.array(org[x])
		if(gl_vars.outVar[j]):
			ord_arr = [dimension_list.index(a) for a in gl_vars.data[ind].variables[x].dims]
			out_ind = tuple([mess_ind_2[a] for a in ord_arr])
			temp = test_array[out_ind]
			output_message += x + '\n' + str(temp) +'\nMean: '+str(np.nanmean(temp))+' Standard Deviation: '+str(np.nanstd(temp))+'\n'
		j += 1
	return output_message

def getShapeData(ind, var_name, time_index, shpfile, plac_ind):
	
	lon_var, lat_var = None, None
	xds = gl_vars.data[ind]
	for a in list(xds.dims):
		if (a.lower().startswith("lon")):
			lon_var = a
		if (a.lower().startswith("lat")):
			lat_var = a
	if (lon_var is None or lat_var is None):
		# ERROR HANDLING
		return
	xds = xds.assign_coords(longitude=(((xds.variables[lon_var][:] + 180.0) % 360.0) - 180.0),lon=(((xds.variables[lon_var][:] + 180.0) % 360.0) - 180.0))
	if (shpfile == None):
		da1 =  xds.data_vars[var_name][time_index,:,:]  #THIS IS WRONG. NEEDS TO BE READ FROM NC DATA
		da1 = da1.sortby(da1[lon_var])
		geometries = None
		out = da1
	elif(time_index  is not None and var_name is not None):
		da1 =  xds.data_vars[var_name][time_index,:,:]   #THIS IS WRONG. NEEDS TO BE READ FROM NC DATA
		da1 = da1.sortby(da1[lon_var])
		raster, geometries = applyShape(da1, lat_var, lon_var, shpfile, plac_ind)
		spatial_coords = {lat_var: da1.coords[lat_var], lon_var: da1.coords[lon_var]}
		da1[var_name] = xr.DataArray(raster, coords=spatial_coords, dims=(lat_var, lon_var))
		out =  da1.where(~np.isnan(da1[var_name]),other = np.nan)
	else:
		fin_arr = dict()
		for a in list(gl_vars.data[ind].data_vars):
			out_arr = []
			da1 =  xds.data_vars[a][:]
			da1 = da1.sortby(da1[lon_var])
			raster, geometries = applyShape(da1, lat_var, lon_var, shpfile, plac_ind)
			for c in range(len(da1.coords['time'])):
				da_1 = da1[c,:,:]
				spatial_coords = {lat_var: da_1.coords[lat_var], lon_var: da_1.coords[lon_var]}
				da_1[a] = xr.DataArray(raster, coords=spatial_coords, dims=(lat_var, lon_var))
				out_arr.append(da_1.where(~np.isnan(da_1[a]),other = np.nan).values)
			fin_arr[a] = out_arr
		out = fin_arr
	return out, lon_var, lat_var, geometries


def applyShape(da1, lat_var, lon_var, shpfile, plac_ind):
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
	return raster, geometries
