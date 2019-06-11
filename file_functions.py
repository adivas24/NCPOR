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

# TODO: Merge and rearrange the content of these functions, there seems to be a lot of redundancy.
#		Correct a few errors speciifically mentioned.
#		Exception, handling and fool-proofing.

# PRE-CONDITION
#	filenames: A list of strings corresponding to each NETCDF file containing the full path of the file.
def openNETCDF(filenames):
	return [xr.open_dataset(i) for i in filenames]
# POST-CONDITION
#	return value: an array containing xarray DataFrames, each corresponding to one NETCDF file.

# PRE-CONDITION
#	ind: The index of the page, represents the NETCDF file being queried as an integer.
#	gl_vars.data, gl_vars.outVar, and gl_vars.messages must be initialized before function call.
def getData(ind):
	dimension_list = list(gl_vars.data[ind].coords.keys())
	variable_list = list(gl_vars.data[ind].data_vars.keys())
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
			mess_ind[j].sort()
			mess_ind_2[j] = slice(mess_ind[j][0],mess_ind[j][1])
			sel_message += ' : ' + str(gl_vars.data[ind].variables[x].values[mess_ind[j][1]])
		else:
			mess_ind_2[j] = mess_ind[j][0]
		sel_message += '\n'
		j += 1
	j = 0
	ord_arr = None
	output_message = ""
	for x in variable_list:
		if(gl_vars.outVar[j]):
			ord_arr = [dimension_list.index(a) for a in gl_vars.data[ind].variables[x].dims]
			out_ind = tuple([mess_ind_2[a] for a in ord_arr])
			temp = gl_vars.data[ind].variables[x].values[out_ind]
			output_message += x + '\n' + str(temp) +'\nMean: '+str(np.nanmean(temp))+' Standard Deviation: '+str(np.nanstd(temp))+'\n'
		j += 1
	return sel_message, output_message
# POST-CONDITION
#	return values: A 2-tuple containing the ranges/values selected by the user and the output data in the form of strings. 

# PRE-CONDITION
#	ind: The index of the page, represents the NETDCF file being queried as an integer.
#	var_name: The name of the variable being queried, in the form of a string.
#	gl_vars.data and gl_vars.messages must be initialized before function call.
def getData2(ind, var_name):
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
			mess_ind[j].sort()
			mess_ind_2[j] = slice(mess_ind[j][0],mess_ind[j][1])
			sel_message += ' : ' + str(gl_vars.data[ind].variables[x].values[mess_ind[j][1]])
		else:
			mess_ind_2[j] = mess_ind[j][0]
		sel_message += '\n'
		j += 1
	ord_arr = [dimension_list.index(a) for a in gl_vars.data[ind].variables[var_name].dims]
	out_ind = tuple([mess_ind_2[a] for a in ord_arr])
	return sel_message, gl_vars.data[ind].variables[var_name].values[out_ind]
# POST-CONDITION
#	return values: A string containing the selected value ranges and the output, but in the form of an numpy array as a 2-tuple.

# PRE-CONDITION
#	i: The index of the page, represents the NETDCF file being queried as an integer.
#	masked_data: The masked data after applying the SHAPEFILE restrictions. It is a dictioinary of a list containing xarray DataArrays.
#	gl_vars.data, gl_vars.outVar, and gl_vars.messages must be initialized before function call.
def getData3(i, masked_data):
	dimension_list = list(gl_vars.data[i].coords.keys())
	variable_list = list(masked_data.keys())
	mess_ind = [[None, None] for i in dimension_list]
	mess_ind_2 = [None for i in dimension_list] 
	sel_message = "You have selected:\n"
	j = 0
	for x in dimension_list:
		arr = [str(a) for a in gl_vars.data[i].variables[x].values]
		mess_ind[j][0] = arr.index(gl_vars.messages[j][0])
		sel_message += x + ' ' + str(gl_vars.data[i].variables[x].values[mess_ind[j][0]])
		if (gl_vars.messages[j][1] is not None):
			mess_ind[j][1] = arr.index(gl_vars.messages[j][1])
			sel_message += ' : ' + str(gl_vars.data[i].variables[x].values[mess_ind[j][1]])
			mess_ind[j].sort()
			mess_ind_2[j] = slice(mess_ind[j][0],mess_ind[j][1])
		else:
			mess_ind_2[j] = mess_ind[j][0]
		sel_message += '\n'
		j += 1
	j = 0
	ord_arr = None
	output_message = ""
	for x in variable_list:
		if(gl_vars.outVar[j]):
			ord_arr = [dimension_list.index(a) for a in gl_vars.data[i].variables[x].dims]
			out_ind = tuple([mess_ind_2[a] for a in ord_arr])
			temp = np.array(masked_data[x])[out_ind]
			output_message += x + '\n' + str(temp) +'\nMean: '+str(np.nanmean(temp))+' Standard Deviation: '+str(np.nanstd(temp))+'\n'
		j += 1
	return sel_message, output_message
# POST-CONDITION
#	return values: A 2-tuple containing the ranges/values selected by the user and the output data in the form of strings. 

# PRE-CONDITION
#	ind: The index of the page, represents the NETDCF file being queried as an integer.
#	var_name: The name of the variable being queried, in the form of a string. If None, it indicates all variables slected should be considered.
#	time_index: The index (as an integer) of the time point selected, at which the shape is being generated. If None, data across the entire range is returned as a list.
#	shpfile: A string containing the name and path of the SHAPEFILE(.shp) being used.
#	plac_ind: As of now, it is a single integer containing the index of the place (specific geometry) selected by the user from the SHAPEFILE. None indicates the entire file being used. In the future a list should be passed, which can accurately select multiple but not all the places present. Maybe through a clickable-map interface.
#	gl_vars.data should be initialized before the function call.
def getShapeData(ind,var_name, time_index, shpfile, plac_ind):
	
	xds = gl_vars.data[ind]
	for a in list(xds.dims):
		if (a.lower().startswith("lon")):
			lon_var = a
		if (a.lower().startswith("lat")):
			lat_var = a
	if (lon_var is None or lat_var is None):
		return
	xds = xds.assign_coords(longitude=(((xds.variables[lon_var][:] + 180.0) % 360.0) - 180.0))
	if(time_index  is not None and var_name is not None):
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
		return da1.where(~np.isnan(da1[var_name]),other = np.nan)
	else:
		fin_arr = dict()
		for a in list(gl_vars.data[ind].data_vars):
			out_arr = []
			da1 =  xds.data_vars[a][:]   #THIS IS WRONG. NEEDS TO BE READ FROM NC DATA
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
			for c in range(len(da1.coords['time'])):
				da_1 = da1[c,:,:]
				spatial_coords = {lat_var: da_1.coords[lat_var], lon_var: da_1.coords[lon_var]}
				da_1[a] = xr.DataArray(raster, coords=spatial_coords, dims=(lat_var, lon_var))
				out_arr.append(da_1.where(~np.isnan(da_1[a]),other = np.nan).values)
			fin_arr[a] = out_arr
		return fin_arr
# POST-CONDITION
#	return value: If both var_name and time_index are supplied as None, the function will return a dictionary where keys are the variables and each value is a list of xarray dataArrays corresponding to each time point, after masking the data using the SHAPEFILE geometry.
#		Else, it returns the specific (for that variable, at that time) masked xarray DataArray.