"""This contains the primary functions used for opening files and 
manipulating the data contained within them.

The functions defined here can be used to get and manipulate data. For 
the purpose of the project, these functions have been called 
specifically in driver.py and gui_functions.py.

See Also
--------
gui_functions
plot_functions
driver

"""

import datetime
from dateutil.relativedelta import *

import xarray as xr
import numpy as np
# Used for data manipulation numerical calculations.

import pandas as pd
import geopandas as gpd
# Used for some data manipulation

import shapely.geometry as sgeom
from rasterio import features
from affine import Affine
# Used for SHAPEFILES

# TODO:
#		Correct a few errors specifically mentioned.
#		Exception, handling and fool-proofing.

def openNETCDF(filenames):
	r"""Opens the files given as arguments.

	Wrapper around an xarray function to open NetCDF files. Opens the
	 files specified in `filenames`.

	Parameters
	----------
	filenames : array_like
		List of strings of filenames (with path).

	Returns
	-------
	dict
		A Python dictionary with filenames (without path) as keys and 
		opened xarray datasets as values.

	See Also
	--------
	xarray.Dataset: Type of values in returned dictionary.
	xarray.open_dataset : Function used internally.

    """
	out = dict()
	for name in filenames:
		mod_name= name.split('/')[-1]
		out[mod_name] = xr.open_dataset(name)
	return out

def getData(dataset, msgs, outVar, variable = None, masked_data = None):
	r"""Retrieves the data specified by the user.

	The function internally calls `getSelectedMessage` and 
	`getOutputMessage` to receieve the data. Depending on arguments, 
	the output message (return value) may vary.

	Parameters
	----------
	dataset: xarray Dataset
		The dataset from which data is to be retrieved. 
	msgs: dict
		A dictionary with dimension names as keys and lists 
		containing indices of the chosen variables as values.
	outVar: dict
		A dictionary with dimension names as keys and a bool as value. 
	variable: str, optional
		Name of variable for which data is to be retrieved. Defaults to None.
		Ignored if masked_data is specified.
	masked_data: dict, optional
		Masked dataset to be used. Stored as a dictionary with variable
		 names as keys. Defaults to None.

	Returns
	-------
	sel_message: str
		A string containing the selected points/ranges of parameters.
		Initialised using call to getSelectedMessage.
	output_message: str or xarray.Dataset
		Output depends on mode. It is either a string containing the 
		retrieved data or the retrieved data. More info in Notes.
	
	Notes
	-----
	Modes of operation

	| 1. If masked_data is specified, that dataset is used for retrieval of the messages required. Output is in the form of a string.
	| 2. If masked_data is not specified, and variable is specified. Dataset for that variable is fetched and returned, after bounds are applied.
	| 3. If neither masked_data nor variable are specified, variables specified by outVar are queried. 

	See Also
	--------
	xarray.Dataset
	getSelectedMessage
	getOutputMessage

    """
	sel_message, mess_ind_2 = getSelectedMessage(dataset, msgs)
	if (masked_data is None):
		if (variable is None):
			output_message = getOutputMessage(dataset, mess_ind_2, outVar)
		else:
			out_ind = tuple([mess_ind_2[a] for a in dataset.variables[variable].dims])
			output_message = dataset.variables[variable][out_ind]
	else:
		output_message = getOutputMessage(dataset, mess_ind_2, outVar, masked_data = masked_data)
	return sel_message, output_message

def getSelectedMessage(dataset, msgs):
	r"""Creates a string containing the bounds selected by the user.

	The function takes in a dictionary of indices and converts it to a 
	string format and a dictionary of slices, which can then be fed as 
	array indices. 

	Parameters
	----------
	dataset: xarray Dataset
		The dataset from which data is to be retrieved.
	msgs: dict
		Contains a dictionary with dimension names as keys and lists 
		containing indices of the chosen variables as values.

	Returns
	-------
	sel_message: str
		A string containing the selected points/ranges of parameters.
	mess_ind_o: dict
		A dictionary with the dimensions as keys and the index or slice
		of indices as values. This object is passed to 
		getOutputMessage to finally retrieve the data.
	
	See Also
	--------
	getData
	getOutputMessage

	"""
	dimension_list = list(dataset.coords.keys())
	mess_ind = dict()
	mess_ind_o = dict()
	sel_message = "You have selected:\n"
	for x in dimension_list:
		arr = [str(a) for a in dataset.variables[x].values]
		mess_ind[x] = [arr.index(msgs[x][0])]
		sel_message += x + ' ' + str(dataset.variables[x].values[mess_ind[x][0]])
		if (msgs[x][1] is not None):
			mess_ind[x].append(arr.index(msgs[x][1]))
			sel_message += ' : ' + str(dataset.variables[x].values[mess_ind[x][1]])
			mess_ind[x].sort()
			mess_ind_o[x] = slice(mess_ind[x][0],mess_ind[x][1]+1)
		else:
			mess_ind_o[x] = mess_ind[x][0]
		sel_message += '\n'
	return sel_message, mess_ind_o

def getOutputMessage(dataset, mess_ind, outVar, masked_data = None):
	r"""Returns a string containing the output data.

	The function takes in the ranges and output variables required and 
	generates a string with data in the form of nested arrays. The 
	string also contains the mean and std deviation for each variable.

	Parameters
	----------
	dataset: xarray Dataset
		The dataset from which data is to be retrieved.
	mess_ind: dict
		A dictionary with the dimensions as keys and the index or slice
		of indices as values. This object is generated by  
		getSelectedMessage.
	outVar: dict
		A dictionary with dimension names as keys and a bool as value.
	masked_data: dict, optional
		Masked dataset to be used. Stored as a dictionary with variable
		names as keys. Defaults to None.

	Returns
	-------
	output_message: str
		A string containing the output data with some statistics.
	
	See Also
	--------
	getData
	getSelectedMessage

    """

	variable_list = list(dataset.data_vars.keys())
	output_message = ""
	for x in variable_list:
		if(masked_data is None):
			test_array = dataset.variables[x].values
		else:
			test_array = np.array(masked_data[x])
		if(outVar[x]):
			out_ind = tuple([mess_ind[a] for a in dataset.variables[x].dims])
			temp = test_array[out_ind]
			output_message += x + '\n' + str(temp) +'\nMean: '+str(np.nanmean(temp))+' Standard Deviation: '+str(np.nanstd(temp))+'\n'
	return output_message

def getShapeData(xds, var_name, time_index, shpfile, plac_ind):
	r"""Returns data and some auxiliary information after applying a ShapeFile filter.

	This function takes in a dataset and applies a Shapefile filter to 
	the data. Some specific inputs can result in distinct behaviour and
	is discussed under Notes. This function calls applyShape.

	Parameters
	----------
	xds: xarray Dataset
		The dataset from which data is to be retrieved.  
	var_name: str
		Variable name. None if all are selected.
	time_index: int
		The index if the time for which data is to be retrieved. None 
		if all are selected. 
	shpfile: str
		The name of the shapefile in use.
	plac_ind: int
		The index of the geometry being selected. None if all are selected.

	Returns
	-------
	out: dataset or dict or numpy.array
		The output data. The type depends on the parameters passed to 
		the function. More information in Notes
	geometries: array_like
		A list containing the geometries generated by the shape file.
		
	Notes
	-----
	Behaviour of the Function

	The data passed in `xds`, must contain unique variables beginning 
	with 'lat' and 'lon' corresponding to latitude and longitude for 
	the function to work.

	If a `shapefile` has not been specified, no filters are applied and
	the unmasked data is returned. `geometries` is set to None.

	If a `shapefile` has been specified, and both `time_index` and 
	`var_name` have been specified, the appropriate filters are applied
	and a numpy array containing the masked data is returned.

	If `shapefile` has been specified, but either one of `time_index` 
	and	`var_name` were not, then shapefile masked data for all 
	variables across all avaiable time periods is returned as a dict
	with variable names as keys and lists of data as values.

	See Also
	--------
	applyShape
	
    """	
	lon_var,lat_var = getLatLon(xds)
	xds = xds.assign_coords(longitude=(((xds.variables[lon_var][:] + 180.0) % 360.0) - 180.0),lon=(((xds.variables[lon_var][:] + 180.0) % 360.0) - 180.0))
	if (shpfile == None):
		da1 =  xds.data_vars[var_name][time_index,:,:]  #THIS IS WRONG. NEEDS TO BE READ FROM NC DATA
		da1 = da1.sortby(da1[lon_var])
		geometries = None
		out = da1
	elif(time_index is not None and var_name is not None):
		da1 =  xds.data_vars[var_name][time_index,:,:]   #THIS IS WRONG. NEEDS TO BE READ FROM NC DATA
		da1 = da1.sortby(da1[lon_var])
		raster, geometries = applyShape(da1, lat_var, lon_var, shpfile, plac_ind)
		spatial_coords = {lat_var: da1.coords[lat_var], lon_var: da1.coords[lon_var]}
		da1[var_name] = xr.DataArray(raster, coords=spatial_coords, dims=(lat_var, lon_var))
		out =  da1.where(~np.isnan(da1[var_name]), other = np.nan)
	else:
		fin_arr = dict()
		for a in list(xds.data_vars):
			out_arr = []
			da1 =  xds.data_vars[a][:]
			da1 = da1.sortby(da1[lon_var])
			raster, geometries = applyShape(da1, lat_var, lon_var, shpfile, plac_ind)
			for c in range(len(da1.coords['time'])):
				da_1 = da1[c,:,:]
				spatial_coords = {lat_var: da_1.coords[lat_var], lon_var: da_1.coords[lon_var]}
				da_1[a] = xr.DataArray(raster, coords=spatial_coords, dims=(lat_var, lon_var))
				out_arr.append(da_1.where(~np.isnan(da_1[a]), other = np.nan).values)
			fin_arr[a] = out_arr
		out = fin_arr
	return out, geometries

def applyShape(da1, lat_var, lon_var, shpfile, plac_ind, lat_r = None, lon_r = None):
	r"""Returns data and some auxiliary information after applying a ShapeFile filter.

	This function takes in a dataset and applies a Shapefile filter to 
	the data. Some specific inputs can result in distinct behaviour and
	is discussed under Notes. This function calls applyShape.

	Parameters
	----------
	da1: xarray Dataset or numpy.array
		The dataset from which data is to be retrieved.  
	lat_var: str
		The variable corresponding to the latitude dimension. 
	lon_var: str
		The variable corresponding to the longitude dimension. 
	shpfile: str
		The name of the shapefile in use.
	plac_ind: int
		The index of the geometry being selected. None if all are selected.
	lat_r: array_like, optional
		The range of latitudes. Required if passing a numpy array.
	lon_r: array_like, optional
		The range of longitudes. Required if passing a numpy array.

	Returns
	-------
	raster: array_like
		Raster object created using rasterio.features.rasterize
	geometries: array_like
		A list containing the geometries generated using shapely.

	See Also
	--------
	shapely.geometry.shape
	rasterio.features.rasterize
	Affine.translation
	Affine.scale

	"""	

	open_file = gpd.read_file(shpfile)	
	shapes = [(shape, n) for n,shape in enumerate(open_file.geometry)]
	geometries = [sgeom.shape(a[0]) for a in shapes]
	try:
		lat = np.asarray(da1.coords[lat_var])
		lon = np.asarray(da1.coords[lon_var])
	except:
		lat = np.asarray(lat_r)
		lon = np.asarray(lon_r)		
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

def getStats(dataSet, year_start, chk_status, variables):
	r"""Retrieves statistics for data from specifc periods.

	This function takes in information about the times for which the 
	data is requested and outputs the statistics for each variable.

	Parameters
	----------
	dataSet: xarray Dataset
		The dataset from which data is to be retrieved.  
	year_start: int
		The base year. If None, it is operating in month mode.
	chk_status: array_like or dict
		In year mode, it expects a list of boolean values. In month 
		mode, it expects a dictionary of dictionary of boolean values, 
		with year being the key for the outer dictionary and month, for
		the inner dictionary.
	variables: array_like
		The list of variable names (as strings) that are being queried. 

	Returns
	-------
	final: dict
		A dictionary where the keys are the variable names and the
		values are tuples with the required statistics.

	See Also
	--------
	numpy.nanmean
	numpy.nanstd
	numpy.nanmax
	numpy.nanmin

	"""	
	output = dict()
	final = dict()
	months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
	time_list = [pd.to_datetime(a).date() for a in list(dataSet.variables['time'].values)]
	for a in variables:
		output[a] = []
	if (year_start is not None):
		year_set = set([])
		for a in range(len(chk_status)):
			if (chk_status[a]):
				year_set.add(year_start+a) 
		for a in time_list:
			if a.year in year_set:
				for b in variables:
					#THIS presumes that it has only three dimensions which is not true.
					output[b].append(dataSet.variables[b].values[time_list.index(a),:,:])
	else:
		time_set = set([])
		for year in list(chk_status.keys()):
			for mon in months:
				if (chk_status[year][mon]):
					time_set.add(str(year)+"_"+str(1 + months.index(mon)))
		for a in time_list:
			if (str(a.year)+"_"+str(a.month)) in time_set:
				for b in variables:
					output[b].append(dataSet.variables[b].values[time_list.index(a),:,:])
	for a in variables:
		output[a] = np.array(output[a])
		final[a] = (np.nanmean(output[a]), np.nanstd(output[a]), np.nanmax(output[a]), np.nanmin(output[a]))
	return final

def plotData(dataSet, start_time_index, end_time_index, time_interval, variables, filt = None, lat_range = None, lon_range = None, filename = None, place = None):
	r"""Retrieves data required for plotting time series graphs.

	This function generates the data required to plot graphs for 
	variables in a discrete user-specified time interval, taking 
	average over each smaller user-specified period. The data used can
	be masked, or bounded by using the right keyword arguments. Uses
	a call to getShapeData for shapefile bounds.

	Parameters
	----------
	dataSet: xarray Dataset
		The dataset from which data is to be retrieved.  
	start_time_index: int
		The index for the first time on the graph.
	end_time_index: int
		The index for the last time on the graph.
	time_interval: tuple
		This needs to be a tuple with an integer specifying a number 
		and a string specifying the time period, namely 'years', 
		'months', or 'days'.
	variables: array_like
		The list of variable names (as strings) that are being queried.
	filt: str,optional
		If None (default), no filters are used.
		If "bounds", then lat-lon bounds are used.
		If "shapefile", then a shapefile geometry is used.
	lat_range: slice
		A slice containing the index bounds for latitude. Required for 
		"bounds" mode, ignored in others.
	lon_range: slice
		A slice containing the index bounds for longitude. Required for
		"bounds" mode, ignored in others.
	filename: str
		The name of the shapefile being used. Required for "shapefile"
		mode, ignored in others.
	place: int
		The index of the place being selected. None, in case of all.
		Required for "shapefile" mode, ignored in others.

	Returns
	-------
	tuple
		A tuple of two dictionaries, one with data, one with error and
		a list containing the time intervals. The dictionaries have 
		variable names as keys and a list of data as values.

	See Also
	--------
	numpy.nanmean
	numpy.nanstd
	dateutil.relativedata

	"""	
	time_list = [pd.to_datetime(a).date() for a in list(dataSet.variables['time'].values)]
	startTime = time_list[start_time_index]
	endTime = time_list[end_time_index]
	if (time_interval[1] == "years"):
		kwargs = {"years" : time_interval[0]}
	if (time_interval[1] == "months"):
		kwargs = {"months" : time_interval[0]}
	if (time_interval[1] == "days"):
		kwargs = {"days" : time_interval[0]}
	time_step = relativedelta(**kwargs)

	curr_lim = startTime+time_step
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
		if (a>endTime):
			break
		if (a<curr_lim):
			flag = True
			for b in variables:
				if(filt == None):
					temp[b].append(np.array(dataSet.variables[b].values[time_list.index(a),:,:]))
				elif(filt == "bounds"):
					temp[b].append(np.array(dataSet.variables[b].values[time_list.index(a),lat_range,lon_range]))
				elif(filt == "shapefile"):
					temp[b].append(np.array(getShapeData(dataSet, b, time_list.index(a), filename, place)[0]))
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
					temp[b] = [np.array(getShapeData(dataSet, b, time_list.index(a), filename, place)[0])]	
			flag = False
	if(len(temp[variables[0]]) != 0):
		time_array.append(curr_lim-time_step)
		for b in variables:
			arr_temp = np.array(temp[b])
			output_mean[b].append(np.nanmean(arr_temp))
			output_std[b].append(np.nanstd(arr_temp))
	return (output_mean, output_std, time_array)

def animate_aux(dataset, var_name, time, shpfile, plac_ind):
	r"""Used to generate a function used in the animate functions.

	This function returns a function which takes a integer as an index
	offset and returns the same output as getShapeData.

	Parameters
	----------
	dataset: xarray Dataset
		The dataset from which data is to be retrieved.  
	var_name: str
		Variable name. None if all are selected.
	time: int
		The index of the base time. 
	shpfile: str
		The name of the shapefile in use.
	plac_ind: int
		The index of the geometry being selected. None if all are selected.
	Returns
	-------
	callable
		A function which accepts an integer as a time index offset.

	"""
	return lambda i: getShapeData(dataset,var_name, time + i, shpfile, plac_ind)

def combineFiles(dataSet, filenames, indxs, newName):
	r"""Combines compatible NETCDF files.

	The functions combines specified files into a merged dataset.
	Modifies both the dataset and the filename array. As of now,
	the function does not check for compatibility.

	Parameters
	----------
	dataSet: xarray Dataset
		The dataset from which data is to be retrieved.  
	filenames: array_like
		A list of all existing opened files.
	indxs: array_like
		List of indexes of files that need to be combined.
	newName: str
		Name of merged dataset.
	
	Returns
	-------
	copy: xarray Dataset
		The modified dataset.
	filenames2: array_like
		Modified list of files.

	See Also
	--------
	xarray.merge

	"""	
	data_mod = [dataSet[a] for a in indxs]
	merged = xr.merge(data_mod)
	filenames2 = [a for a in filenames if a not in indxs]
	copy = dict()
	for a in filenames2:
		copy[a] = dataSet[a]
	copy[newName] = merged
	filenames2.append(newName)
	return copy, filenames2

def generateMessage(data_dict):
	r"""Converts a dictionary of stats to a string.

	The functions takes in a dictionary with variable names as keys and
	a tuple of stats as values and returns a string containing the same.

	Parameters
	----------
	data_dict: dict
		A dictionary with variable name as key and tuples of (mean, 
		stddev, max, min) as values.

	Returns
	-------
	outMessage: str
		A string with the stats

	"""	

	outMessage = ""
	for a in list(data_dict.keys()):
		outMessage += a + '\n'
		outMessage += "Mean: " + str(data_dict[a][0]) + '\n' 
		outMessage += "Std Dev: " + str(data_dict[a][1]) + '\n' 
		outMessage += "Max: " + str(data_dict[a][2]) + '\n' 
		outMessage += "Min: " + str(data_dict[a][3]) + '\n' 
		outMessage += '\n'
	return outMessage

def getLatLon(xds):
	r"""Retrieves the variable names for latitude and longitude.

	The functions queries the dataset for the variable names
	corresponding to the latitude and longitude. It assumes that the 
	respective variables begin with 'lat' and 'lon'.

	Parameters
	----------
	xds: xarray Dataset
		The dataset in question.  
		
	Returns
	-------
	lon_var: str
		The name of the variable corresponding to longitude.
	lat_var: str
		The name of the variable corresponding to latitude.

	See Also
	--------
	startswith

	"""	
	lon_var, lat_var = None, None
	for a in list(xds.dims):
		if (a.lower().startswith("lon")):
			lon_var = a
		elif (a.lower().startswith("lat")):
			lat_var = a
		if (lat_var is not None and lon_var is not None):
			break
	return lon_var,lat_var
