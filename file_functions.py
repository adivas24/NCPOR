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

import datetime
from dateutil.relativedelta import *
# TODO:
#		Correct a few errors specifically mentioned.
#		Exception, handling and fool-proofing.

# PRE-CONDITION
#	filenames: A list of strings corresponding to each NETCDF file containing the full path of the file.
def openNETCDF(filenames):
	out = dict()
	for i in filenames:
		i_mod = i.split('/')[-1]
		out[i_mod] = xr.open_dataset(i)
	return out
# POST-CONDITION
#	return value: an array containing xarray DataFrames, each corresponding to one NETCDF file.

# PRE-CONDITION
#	ind: the index of the current page.
#	org: Selects the mode of operation. 0 signifying the use of all the data, 1 signifying the use of masked data (provided as an argument).
#	args: Additional arguments that may be supplied. In this case, in mode 0, it is the variable name (as a string), if None, all variables are selected. In mode 1, it is the masked data in the form of a xarray DataFrame.
#	gl_vars.data must be initialised before function call.
def getData(ind, org, *args):
	dimension_list = list(gl_vars.data[ind].coords.keys())
	sel_message, mess_ind_2 = getSelectedMessage(ind)
	if (org == 0):
		if (args[0] is None):
			output_message = getOutputMessage(ind, mess_ind_2, args[0])
		else:
			var_name = args[0]
			out_ind = tuple([mess_ind_2[a] for a in gl_vars.data[ind].variables[var_name].dims])
			output_message = gl_vars.data[ind].variables[var_name][out_ind]
	elif(org == 1):
		output_message = getOutputMessage(ind, mess_ind_2, args[0])
	return sel_message, output_message
# POST-CONDITION
#	return value: a 2-tuple. The first element is a string containing the message with selected data ranges. The second is a string containing the output ranges, except when a single variable name is provided in mode 1, in that case, it returns the entire xarray DataArray.

# PRE-CONDITION
#	ind: The index of the page currently active, from which data is to be retrieved.
#	gl_vars.data and gl_vars.messages need to have been initialized before function call.
def getSelectedMessage(ind):
	dimension_list = list(gl_vars.data[ind].coords.keys())
	mess_ind = dict()
	mess_ind_2 = dict()
	sel_message = "You have selected:\n"
	for x in dimension_list:
		arr = [str(a) for a in gl_vars.data[ind].variables[x].values]
		if (a == "time"):
			arr = [str(pd.to_datetime(a).date()) for a in gl_vars.data[i].variables[a].values]
		mess_ind[x] = [arr.index(gl_vars.messages[x][0])]
		sel_message += x + ' ' + str(gl_vars.data[ind].variables[x].values[mess_ind[x][0]])
		if (gl_vars.messages[x][1] is not None):
			mess_ind[x].append(arr.index(gl_vars.messages[x][1]))
			sel_message += ' : ' + str(gl_vars.data[ind].variables[x].values[mess_ind[x][1]])
			mess_ind[x].sort()
			mess_ind_2[x] = slice(mess_ind[x][0],mess_ind[x][1]+1)
		else:
			mess_ind_2[x] = mess_ind[x][0]
		sel_message += '\n'
	return sel_message, mess_ind_2
# POST-CONDITION
#	return value: a 2-tuple containing a string with a message containing the data ranges selected and a list containing the actual ranges (as slices)/values (as integers) that can be fed as array indices to retrieve the data.

# PRE-CONDITION
#	ind: the index of the current page
#	mess_ind_2: A list containing the output ranges, either as values (integers) or slices.
#	org: specifies the mode of operation. If None, we use all the data. Otherwise, it is expected that org contains the masked data, in the form of a list.
def getOutputMessage(ind, mess_ind_2, org):
	variable_list = list(gl_vars.data[ind].data_vars.keys())
	dimension_list = list(gl_vars.data[ind].coords.keys())
	ord_arr = None
	output_message = ""
	for x in variable_list:
		if(org == None):
			test_array = gl_vars.data[ind].variables[x].values
		else:
			test_array = np.array(org[x])
		if(gl_vars.outVar[x]):
			out_ind = tuple([mess_ind_2[a] for a in gl_vars.data[ind].variables[x].dims])
			temp = test_array[out_ind]
			output_message += x + '\n' + str(temp) +'\nMean: '+str(np.nanmean(temp))+' Standard Deviation: '+str(np.nanstd(temp))+'\n'
	return output_message
# POST-CONDITION
#	return value: A string containing the output data, ready for display, along with the mean and standard deviations.

# PRE-CONDITION
#	ind: The index of the current page as an integer
#	var_name: The name of the output variable in question as a string. If None, all are iterated through.
#	time_index: The index of the time of required data as an integer. If None, all are iterated through
#	shpfile: The name of the shapefile as a string. If None, no filters are aplied to the map.
#	plac_ind: An integer specifying the shape that is finally selected. As of now, it is an integer, should be made an array in the future. None implies all shapes selected.
#	gl_vars.data should have been initialised before function call.
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
# POST-CONDITION
#	return variables: out is the xarray DataArray (or a list of it), ready for plotting or further processing.
#					lon_var and lat_var are the strings which are the names of the variables corresponding to latitude and longitude in the NETCDF file in question.
#					geometries is the list containing the shapes selected. If no shapefile was used, it is None.

# PRE-CONDITION
#	da1: The data (as an xarray DataArray) on which the masking needs to take place.
#	lat_var and lon_var: Strings with the name of the latitude variable and longitude vatiable in the NETCDF file
#	shpfile: The name of the shapefile to be used as a string.
#	plac_ind: The integer index of the selected shape. If None, all are selected.
def applyShape(da1, lat_var, lon_var, shpfile, plac_ind):
	test = gpd.read_file(shpfile)
	with fiona.open(shpfile) as records:
		geometries = [sgeom.shape(shp['geometry']) for shp in records]
	shapes = [(shape, n) for n,shape in enumerate(test.geometry)]
	try:
		lat = np.asarray(da1.coords[lat_var])
		lon = np.asarray(da1.coords[lon_var])
	except:
		lat = np.asarray(gl_vars.data[list(gl_vars.data.keys())[0]].coords[lat_var])
		lon = np.asarray(gl_vars.data[list(gl_vars.data.keys())[0]].coords[lon_var])		
	trans = Affine.translation(lon[0], lat[0])
	scale = Affine.scale(lon[1]- lon[0], lat[1] - lat[0])
	transform = trans*scale
	try:
		out_shape = (len(da1.coords[lat_var]), len(da1.coords[lon_var]))
	except:
		out_shape = (da1.shape[0]*da1.shape[1],da1.shape[2])
	if (plac_ind is not None):
		shape_i = [shapes[plac_ind]]
	else:
		shape_i = shapes
	raster = features.rasterize(shape_i, out_shape=out_shape, fill = np.nan, transform = transform, dtype=float)
	return raster, geometries
# POST-CONDITION
#	return values: raster is a feature which can be used to mask the data.
#					geometries contains the shapes selected as a list.

def getStats(ind, year_start, chk_status, variables):
	dataSet = gl_vars.data[ind]
	output = dict()
	final = dict()
	months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
	time_list = [pd.to_datetime(a).date() for a in list(dataSet.variables['time'].values)]
	for a in variables:
		output[a] = []
	if (year_start is not None):
		year_set = set([])
		for a in range(len(chk_status)):
			if (chk_status[a] == 1):
				year_set.add(year_start+a) 
		for a in time_list:
			if a.year in year_set:
				for b in variables:
					output[b].append(dataSet.variables[b].values[time_list.index(a),:,:])
	else:
		time_set = set([])
		for year in list(chk_status.keys()):
			for mon in months:
				if (chk_status[year][mon] == 1):
					time_set.add(str(year)+"_"+str(1 + months.index(mon)))
		for a in time_list:
			if (str(a.year)+"_"+str(a.month)) in time_set:
				for b in variables:
					output[b].append(dataSet.variables[b].values[time_list.index(a),:,:])
	for a in variables:
		output[a] = np.array(output[a])
		final[a] = (np.nanmean(output[a]), np.nanstd(output[a]), np.nanmax(output[a]), np.nanmin(output[a]))
	return final

def plotData(ind, start_time_index, time_interval, variables, filt = None, lat_range = None, lon_range = None, filename = None, place = None):
	dataSet = gl_vars.data[ind]
	time_list = [pd.to_datetime(a).date() for a in list(dataSet.variables['time'].values)]
	startTime = time_list[start_time_index]
	if (time_interval[1] == "years"):
		kwargs = {"years" : time_interval[0]}
	if (time_interval[1] == "months"):
		kwargs = {"months" : time_interval[0]}
	if (time_interval[1] == "days"):
		kwargs = {"days" : time_interval[0]}
	time_step = relativedelta(**kwargs)

	curr_lim = startTime+time_step
	curr_data_set = []
	output_mean = dict()
	output_std = dict()
	temp = dict()
	time_array = []
	flag = False
	for b in variables:
		temp[b] = []
		output_mean[b] = []
		output_std[b] = []
	for a in time_list:
		if (a<startTime):
			continue
		if (a<curr_lim):
			flag = True
			for b in variables:
				if(filt == None):
					temp[b].append(np.array(dataSet.variables[b].values[time_list.index(a),:,:]))
				elif(filt == "bounds"):
					temp[b].append(np.array(dataSet.variables[b].values[time_list.index(a),lat_range,lon_range]))
				elif(filt == "shapefile"):
					temp[b].append(np.array(getShapeData(ind, b, time_list.index(a), filename, place)[0]))
		else:
			if(flag):
				time_array.append(curr_lim-time_step)
				for b in variables:
					arr_temp = np.array(temp[b])
					output_mean[b].append(np.nanmean(arr_temp))
					output_std[b].append(np.nanstd(arr_temp))
			else:
				while(a>curr_lim):
					curr_lim +=time_step
				if(len(temp[variables[0]]) != 0):
					time_array.append(curr_lim)
					for b in variables:
						arr_temp = np.array(temp[b])
						output_mean[b].append(np.nanmean(arr_temp))
						output_std[b].append(np.nanstd(arr_temp))
			curr_lim+=time_step
			for b in variables:
				if(filt == None):
					temp[b] = [np.array(dataSet.variables[b].values[time_list.index(a),:,:])]
				elif(filt == "bounds"):
					temp[b] = [np.array(dataSet.variables[b].values[time_list.index(a),lat_range,lon_range])]
				elif(filt == "shapefile"):
					temp[b] = [np.array(getShapeData(ind, b, time_list.index(a), filename, place)[0])]	
			flag = False
	if(flag):
		time_array.append(curr_lim-time_step)
		for b in variables:
			arr_temp = np.array(temp[b])
			output_mean[b].append(np.nanmean(arr_temp))
			output_std[b].append(np.nanstd(arr_temp))
	return (output_mean, output_std, time_array)