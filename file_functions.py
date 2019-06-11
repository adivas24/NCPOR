import xarray as xr
import gl_vars
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import geopandas as gpd
import fiona
import shapely.geometry as sgeom
import numpy as np
import pandas as pd
from rasterio import features
from affine import Affine
import re


def openNETCDF(filenames):
	return [xr.open_dataset(i) for i in filenames]

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
	#print(sel_message, output_message)
	return sel_message, output_message

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
