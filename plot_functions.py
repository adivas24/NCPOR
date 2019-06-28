# plot_functions.py #

import gl_vars

import xarray as xr
import numpy as np
import pandas as pd
import geopandas as gpd
# Used for data manipulation and numerical calculations. 
import cartopy 
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
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
#		Figure out how to modify the size of maps and maybe make it dynamic?

# PRE-CONDITION
def plotMapShape(proj_string, xds, lon_var, lat_var, geometries):

	pc = ccrs.PlateCarree()
	proj = getProjection(proj_string)
	fig = plt.figure()
	ax = plt.axes(projection=proj)
	xds.plot.pcolormesh(ax=ax, transform=pc, x=lon_var, y=lat_var, cbar_kwargs=dict(orientation='horizontal'))
	if (geometries is not None):
		ax.add_geometries(geometries, pc, edgecolor='gray', facecolor='none')
	else: # geometries is None means that no SHAPEFILE was used.
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

def animation(length, proj_string, show, save, savename, getDat):
	pc = ccrs.PlateCarree()
	proj = getProjection(proj_string)
	plt.style.use('seaborn-pastel')
	fig = plt.figure()
	ax = plt.axes(projection=proj)
	xds, lon_var, lat_var, geometries = getDat(0)
	mesh = xds.plot.pcolormesh(ax=ax, transform=pc, x=lon_var, y=lat_var, cbar_kwargs=dict(orientation='horizontal'))
	cl = None
	if (geometries is not None):
		ax.add_geometries(geometries, pc, edgecolor='black', facecolor='none')
	else:
		cl = ax.coastlines()
	ax.set_global()
	textvar1 = ax.text(-175, -60,ax.title.get_text() + "\nMean: "+ str(np.nanmean(np.array(xds)))+ "\nStd Dev: "+ str(np.nanstd(np.array(xds))), size = "xx-small")
	# Placement depends on projection, gets messed up for all but the PlateCarree projection.
	message = None
	def init():
		nonlocal cl
		if (geometries is None):
			cl.set_visible(True)
		return cl,ax.title

	def animate(i):
		nonlocal  mesh,cl,textvar1
		xds, lon_var, lat_var, geometries = getDat(i)
		mesh = xds.plot.pcolormesh(ax=ax, transform=pc, x=lon_var, y=lat_var, add_colorbar = False)
		print(message+'['+str(i+1)+'/'+str(length+1)+']')
		textvar1.set_text(ax.title.get_text()+ "\nMean: "+ str(np.nanmean(np.array(xds)))+ "\nStandard Deviation: "+ str(np.nanstd(np.array(xds))))
		cl.set_visible(True)
		if(i == length and show == 1):
			print("To continue, close the window.")
		return mesh,cl,textvar1


	anim = FuncAnimation(fig, animate, frames=length+1, interval=20, blit=True, repeat=False, init_func = init)
	
	if(show == 1):
		message = "Displaying "
		plt.show()
	if(save == 1):
		message = "Saving "
		anim.save(savename+'.gif', writer='imagemagick')
	

def vectorMap(proj_string, lon_arr, lat_arr, u_arr, v_arr, velocity):
	pc = ccrs.PlateCarree()
	proj = getProjection(proj_string) 
	plt.clf()
	fig = plt.figure()
	ax = plt.axes(projection = proj)
	ax.coastlines()
	plt.quiver(lon_arr,lat_arr,u_arr, v_arr, velocity, transform = pc, regrid_shape = 30)
	plt.colorbar(orientation = 'horizontal')
	plt.show()

def vectorAnim(length, proj_string, show, save, savename, getU, getV, lon_arr,lat_arr,u_arr, v_arr, velocity, time_array):
	pc = ccrs.PlateCarree() #Later this needs to be user-input.
	proj = getProjection(proj_string) 
	fig = plt.figure()
	ax = plt.axes(projection = proj)
	ax.coastlines()
	ax.quiver(lon_arr,lat_arr,u_arr, v_arr, velocity, transform = pc, regrid_shape = 30)

	def init():
		ax.coastlines()
		return ax.title
	
	def animate(i):
		plt.clf()
		ax = plt.axes(projection = proj)
		ax.coastlines()
		ax.set_title(time_array[i])
		xds1, lon_var, lat_var, geometries = getU(i)
		xds2, lon_var, lat_var, geometries = getV(i)
		u_arr = np.array(xds1)
		v_arr = np.array(xds2)
		velocity = np.sqrt(u_arr*u_arr+v_arr*v_arr)
		ax.quiver(lon_arr,lat_arr,u_arr, v_arr, velocity, transform = pc, regrid_shape = 30)
		print(message+'['+str(i+1)+'/'+str(length+1)+']')
		if(i == length and show == 1):
			print("To continue, close current plot window.") 
		if(save == 1):
			plt.savefig("temp"+ str(i).zfill(4)+'.png', dpi = 'figure')
		plt.draw()
	
	anim = FuncAnimation(fig, animate, frames=length+1, interval=1, blit=False, repeat=False, init_func = init)
	message = "Displaying "
	if(show == 1):
		plt.show()
	

	message = "Saving "
	if(save == 1):
		if(show != 1):
			for i in range(length+1):
		 		animate(i)
		import subprocess
		import os
		subprocess.call("convert -delay 40 temp*.png "+savename+".gif", shell=True)
		for i in range(length+1):
			os.remove("temp"+str(i).zfill(4)+'.png')

def plotLines(output_mean, output_std, time_array, variables):
	x = mdates.date2num(time_array)
	for b in variables:
		plt.errorbar(x,output_mean[b], yerr=output_std[b])
	plt.xticks(x,time_array, rotation = 65, fontsize = "xx-small")
	plt.tight_layout()
	plt.show()

