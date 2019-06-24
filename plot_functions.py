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
from matplotlib.animation import FuncAnimation
import matplotlib as mpl
import matplotlib.cm as cm
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

#if __name__ == "__main__":
	#import numpy as np
	#from matplotlib import pyplot as plt
# def onclick(event):
# 		print(event.button, event.x, event.y, event.xdata, event.ydata)


# PRE-CONDITION
#	ind: The index of the page selected as an integer.
#	var_name: The name of the variable in question as a String.
#	time_index: The index of the time we are plotting the data for, as an integer.
#	shpfile: The name of the shapefile as a string. If None, no shape filters are applied.
#	plac_ind: The index of the place (shape selected from the Shapefile) as an integer. If None, not All are chosen
def plotMapShape(ind,var_name, time_index, shpfile, plac_ind, proj_string):

	#proj_list = ["PlateCarree","AlbersEqualArea","AzimuthalEquidistant","EquidistantConic","LambertConformal","LambertCylindrical","Mercator","Miller","Mollweide","Orthographic","Robinson","Sinusoidal","Stereographic","TransverseMercator","UTM","InterruptedGoodeHomolosine","RotatedPole","OSGB","EuroPP","Geostationary","NearsidePerspective","EckertI","EckertII","EckertIII","EckertIV","EckertV","EckertVI","EqualEarth","Gnomonic","LambertAzimuthalEqualArea","NorthPolarStereo","OSNI","SouthPolarStereo"]
	pc = ccrs.PlateCarree()
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

def animation(ind,var_name, time_range, shpfile, plac_ind, proj_string, show, save, savename):
	pc = ccrs.PlateCarree() #Later this needs to be user-input.
	plt.style.use('seaborn-pastel')
	fig = plt.figure()
	proj = getProjection(proj_string)
	ax = plt.axes(projection=proj)
	xds, lon_var, lat_var, geometries = ffunc.getShapeData(ind, var_name, time_range[0], shpfile, plac_ind)
	kwargs = dict(ax=ax, transform=pc, x=lon_var, y=lat_var, cbar_kwargs=dict(orientation='horizontal'))
	mesh = xds.plot.pcolormesh(**kwargs)
	cl = None
	if (geometries is not None):
		ax.add_geometries(geometries, pc, edgecolor='black', facecolor='none')
	else:
		cl = ax.coastlines()
	ax.set_global()
	textvar1 = ax.text(-175, -60,ax.title.get_text() + "\nMean: "+ str(np.nanmean(np.array(xds)))+ "\nStd Dev: "+ str(np.nanstd(np.array(xds))), size = "xx-small")
	# Placement depends on position, gets messed up for all but the PlateCarree projection.
	message = None
	def init():
		nonlocal cl
		if (geometries is None):
			cl.set_visible(True)
		return cl,ax.title

	def animate(i):
		nonlocal  mesh,cl,textvar1
		xds, lon_var, lat_var, geometries = ffunc.getShapeData(ind,var_name, time_range[0]+i, shpfile, plac_ind)
		mesh = xds.plot.pcolormesh(ax=ax, transform=pc, x=lon_var, y=lat_var, add_colorbar = False)
		print(message+'['+str(i+1)+'/'+str(time_range[1]-time_range[0]+1)+']')
		textvar1.set_text(ax.title.get_text()+ "\nMean: "+ str(np.nanmean(np.array(xds)))+ "\nStandard Deviation: "+ str(np.nanstd(np.array(xds))))
		cl.set_visible(True)
		if(i == time_range[1]-time_range[0] and show == 1):
			print("To continue, close the window.")
		return mesh,cl,textvar1


	anim = FuncAnimation(fig, animate, frames=time_range[1]-time_range[0]+1, interval=20, blit=True, repeat=False, init_func = init)
	
	if(show == 1):
		message = "Displaying "
		plt.show()
	if(save == 1):
		message = "Saving "
		anim.save(savename+'.gif', writer='imagemagick')
# 	

def vectorMap(ind, time_index, shpfile, plac_ind, proj_string):
	pc = ccrs.PlateCarree()
	proj = getProjection(proj_string) 
	plt.clf()
	fig = plt.figure()
	ax = plt.axes(projection = proj)
	ax.coastlines()
	xds1, lon_var, lat_var, geometries = ffunc.getShapeData(ind, 'u10', time_index, shpfile, plac_ind)
	xds2, lon_var, lat_var, geometries = ffunc.getShapeData(ind, 'v10', time_index, shpfile, plac_ind)
	lon_arr = np.sort(((np.array(gl_vars.data[ind].coords[lon_var]) + 180) % 360) -180)
	lat_arr = np.array(gl_vars.data[ind].coords[lat_var])
	u_arr = np.array(xds1)
	v_arr = np.array(xds2)
	velocity = np.sqrt(u_arr*u_arr+v_arr*v_arr)
	plt.quiver(lon_arr,lat_arr,u_arr, v_arr, velocity, transform = pc, regrid_shape = 30)
	plt.colorbar(orientation = 'horizontal')
	plt.show()

def vectorAnim(ind,time_range,shpfile, plac_ind, proj_string, show, save, savename):
	pc = ccrs.PlateCarree() #Later this needs to be user-input.
	proj = getProjection(proj_string) 
	fig = plt.figure()
	ax = plt.axes(projection = proj)
	ax.coastlines()
	xds1, lon_var, lat_var, geometries = ffunc.getShapeData(ind, 'u10', time_range[0], shpfile, plac_ind)
	xds2, lon_var, lat_var, geometries = ffunc.getShapeData(ind, 'v10', time_range[0], shpfile, plac_ind)
	lon_arr = np.sort(((np.array(gl_vars.data[ind].coords[lon_var]) + 180) % 360) -180)
	lat_arr = np.array(gl_vars.data[ind].coords[lat_var])
	u_arr = np.array(xds1)
	v_arr = np.array(xds2)
	velocity = np.sqrt(u_arr*u_arr+v_arr*v_arr)
	ax.quiver(lon_arr,lat_arr,u_arr, v_arr, velocity, transform = pc, regrid_shape = 30)
	#plt.colorbar(orientation = 'horizontal')
	#plt.show()
	def init():
		ax.coastlines()
		return ax.title
	
	def animate(i):
		time_array = [str(pd.to_datetime(a).date()) for a in list(gl_vars.data[ind].variables['time'].values)]
		plt.clf()
		ax = plt.axes(projection = proj)
		ax.coastlines()
		ax.set_title(time_array[i])
		xds1, lon_var, lat_var, geometries = ffunc.getShapeData(ind, 'u10', i, shpfile, plac_ind)
		xds2, lon_var, lat_var, geometries = ffunc.getShapeData(ind, 'v10', i, shpfile, plac_ind)
		u_arr = np.array(xds1)
		v_arr = np.array(xds2)
		velocity = np.sqrt(u_arr*u_arr+v_arr*v_arr)
		ax.quiver(lon_arr,lat_arr,u_arr, v_arr, velocity, transform = pc, regrid_shape = 30)
		print(message+'['+str(i+1)+'/'+str(time_range[1]-time_range[0]+1)+']')
		if(i == time_range[1]-time_range[0] and show == 1):
			print("To continue, close current plot window.") 
		if(save == 1):
			plt.savefig("temp"+ str(i).zfill(4)+'.png', dpi = 'figure')
		plt.draw()
	
	anim = FuncAnimation(fig, animate, frames=time_range[1]-time_range[0]+1, interval=1, blit=False, repeat=False, init_func = init)
	message = "Saving "
	if(show == 1):
		plt.show()
	

	if(save == 1):
		for i in range(time_range[0], time_range[1]+1):
		 	animate(i)
		import subprocess
		import os
		subprocess.call("convert -delay 40 temp*.png "+savename+".gif", shell=True)
		for i in range(time_range[0], time_range[1]+1):
			os.remove("temp"+str(i).zfill(4)+'.png')
	