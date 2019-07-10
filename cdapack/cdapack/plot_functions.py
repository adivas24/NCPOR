"""This contains the primary functions used for plotting.

The functions defined here call on matplotlib and cartopy to generrate
different types of plots. As of now, most functions simply implement 
the default options, more features still need to be added. Colorbars
and general colour choices need to still be given to the user.


See Also
--------
gui_functions
file_functions
driver

"""
import xarray as xr
import numpy as np

import cartopy 
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.animation import FuncAnimation
import matplotlib as mpl
import matplotlib.cm as cm

global proj_dict

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


# TODO	Plot only in a rectangular/polar range?
#		Figure out how to modify the size of maps and maybe make it dynamic?

def plotMapShape(proj_string, xds, lon_var, lat_var, geometries):
	r"""Plots the data on a cartopy map.

	Plots the map depending on the specifications provided by the user.
	The mean and standard deviation of the data is printed on the 
	window as well.	Currently, choice is limited to projection.Future 
	updates should contain at least colour and window frame option.

	Parameters
	----------
	proj_string: str
		The name of the selected projection (must be from avaiable 
		Cartopy options).
	xds: xarray Dataset
		The dataset from which data is to be plotted.
	lon_var: str
		The name of the variable corresponding to longitude.
	lat_var: str
		The name of the variable corresponding to latitude.
	geometries: array_like
		An array of shapely geometries, which form the outline of the 
		map. If None, default coastlines are created.

	See Also
	--------
	matplotlib.pyplot.show

    """
	pc = ccrs.PlateCarree()
	proj = getProjection(proj_string)
	fig = plt.figure(str(xds.name)+ ' ('+proj_string+') ')
	ax = plt.axes(projection=proj)
	xds.plot.pcolormesh(ax=ax, transform=pc, x=lon_var, y=lat_var, cbar_kwargs=dict(orientation='horizontal'))
	if (geometries is not None):
		ax.add_geometries(geometries, pc, edgecolor='gray', facecolor='none')
	else: # geometries is None means that no SHAPEFILE was used, hence using default coastlines.
		ax.coastlines()
	ax.set_global()
	fig.text(0,0, "Mean: "+ str(np.nanmean(np.array(xds)))+ " Standard Deviation: "+ str(np.nanstd(np.array(xds))))
	plt.show()

def getProjection(proj_string):
	r"""Returns a cartopy projection object, given a string.

	Takes in a string as input, and returns an instance of cartopy 
	projection, corresponding to the string. Some projections have
	additional options, which need to be incorporated in a later update.

	Parameters
	----------
	proj_string: str
		The name of the selected projection (must be from avaiable 
		Cartopy options).
	
	Returns
	-------
	Cartopy projection instance.

	See Also
	--------
	Cartopy.crs

	"""
	global proj_dict
	return proj_dict[proj_string]

def animation(length, proj_string, show, save, savename, lon_var, lat_var,frameRate, getDat):
	r"""Creates an animated gif that can be viewed or saved.

	Plots the map depending on the specifications provided by the user.
	Combines individual images into a gif, if save is selected.
	Currently only works for variables with only three dimensions, and
	animates only along the time axis.

	Parameters
	----------
	length:	int
		The number of frames that will be present in the animation.
	proj_string: str
		The name of the selected projection (must be from avaiable 
		Cartopy options).
	show: bool
		Whether the animation needs to be displayed.
	save: bool
		Whether the animation should be saved as a gif.
	savename: str
		The name of the saved gif.
	lon_var: str
		The name of the variable corresponding to longitude.
	lat_var: str
		The name of the variable corresponding to latitude.
	frameRate: int
		The millisecond interval between frames.
	getDat: callable
		An lambda instance of getShapeData, which takes time index 
		offset as input. 

	See Also
	--------
	matplotlib.animation
	"""
	pc = ccrs.PlateCarree()
	proj = getProjection(proj_string)
	fig = plt.figure()
	ax = plt.axes(projection=proj)
	xds, geometries = getDat(0)
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
		nonlocal cl, ax
		ax.set_title(str(xds.name)+ ' ('+proj_string+ ')')
		if (geometries is None):
			cl.set_visible(True)
		return cl,

	def animate(i):
		nonlocal  mesh,cl,textvar1
		xds, geometries = getDat(i)
		mesh = xds.plot.pcolormesh(ax=ax, transform=pc, x=lon_var, y=lat_var, add_colorbar = False)
		print(message+'['+str(i+1)+'/'+str(length+1)+']')
		textvar1.set_text(ax.title.get_text()+ "\nMean: "+ str(np.nanmean(np.array(xds)))+ "\nStandard Deviation: "+ str(np.nanstd(np.array(xds))))
		cl.set_visible(True)
		if(i == length and show == 1):
			print("To continue, close the window.")
		return mesh,cl,textvar1


	anim = FuncAnimation(fig, animate, frames=length+1, interval=frameRate, blit=True, repeat=False, init_func = init)
	
	if(show):
		message = "Displaying "
		plt.show()
	if(save):
		message = "Saving "
		anim.save(savename+'.gif', writer='imagemagick')
	

def vectorMap(proj_string, lon_arr, lat_arr, u_arr, v_arr, velocity, timestamp):
	r"""Plots a vector map of teh given data.

	Plots a matplotlib quiver plot, with regrid shape of 30. It is a 
	thin wrapper around pyplot quiver functionality.

	Parameters
	----------
	proj_string: str
		The name of the selected projection (must be from avaiable 
		Cartopy options).
	lon_arr: array_like
		A numpy array of longitudes.
	lat_arr: array_like
		A numpy array of latitudes.
	u_arr: array_like
		A 2-d numpy array of datapoints corresponding to u-component.
	v_arr: array_like
		A 2-d numpy array of datapoints corresponding to v-component.
	velocity: array_like
		A numpy array used for colour.
	timestamp: str
		The timestamp as a string.

	Notes
	-----
	The shapes of the input arrays need to correspond to the 
	specifications of pyplot's quiver. 

	See Also
	--------
	matplotlib.pyplot.quiver
	"""
	pc = ccrs.PlateCarree()
	proj = getProjection(proj_string) 
	fig = plt.figure("Vector Plot: u10,v10 ")
	ax = plt.axes(projection = proj)
	ax.set_title(timestamp)
	ax.coastlines()
	plt.quiver(lon_arr,lat_arr,u_arr, v_arr, velocity, transform = pc, regrid_shape = 30)
	plt.colorbar(orientation = 'horizontal')
	fig.text(0.5,0.09,"m/s")
	plt.show()

def vectorAnim(length, proj_string, show, save, savename, getU, getV, frameRate, lon_arr,lat_arr,u_arr, v_arr, velocity, time_array):
	r"""Creates an animated gif of a vector plot that can be viewed or saved.

	Plots a matplotlib quiver and combines individual images into a gif
	, if save is selected. It combines the functionality of 
	matplotlib.pyplot.quiver and matplotlib.animation.FuncAnimation.

	Parameters
	----------
	length:	int
		The number of frames that will be present in the animation.
	proj_string: str
		The name of the selected projection (must be from avaiable 
		Cartopy options).
	show: bool
		Whether the animation needs to be displayed.
	save: bool
		Whether the animation should be saved as a gif.
	savename: str
		The name of the saved gif.
	getU: callable
		An lambda instance of getShapeData, which takes time index 
		offset as input, corresponding to the u-component.
	getV: callable
		An lambda instance of getShapeData, which takes time index 
		offset as input, corresponding to the v-component.
	frameRate: int
		Milliseconds between each frame.
	lon_arr: array_like
		A numpy array of longitudes.
	lat_arr: array_like
		A numpy array of latitudes.
	u_arr: array_like
		A 2-d numpy array of datapoints corresponding to u-component.
	v_arr: array_like
		A 2-d numpy array of datapoints corresponding to v-component.
	velocity: array_like
		A numpy array used for colour.
	time_array: array_like
		A list containing the timestamps to be used on the animation.

	Notes
	-----
	The shapes of the input arrays need to correspond to the 
	specifications of pyplot's quiver. 

	See Also
	--------
	matplotlib.animation
	matplotlib.pyplot.quiver

	"""
	pc = ccrs.PlateCarree()
	proj = getProjection(proj_string) 
	fig = plt.figure()
	ax = plt.axes(projection = proj)
	ax.coastlines()
	plt.quiver(lon_arr,lat_arr,u_arr, v_arr, velocity, transform = pc, regrid_shape = 30)
	plt.colorbar(orientation ='horizontal')
	fig.text(0.5,0.1,"m/s")
	def init():
		ax.coastlines()
		return ax.title
	
	def animate(i):
		plt.clf()
		ax = plt.axes(projection = proj)
		ax.coastlines()
		ax.set_title(time_array[i])
		xds1, geometries = getU(i)
		xds2, geometries = getV(i)
		u_arr = np.array(xds1)
		v_arr = np.array(xds2)
		velocity = np.sqrt(u_arr*u_arr+v_arr*v_arr)
		plt.quiver(lon_arr,lat_arr,u_arr, v_arr, velocity, transform = pc, regrid_shape = 30)
		plt.colorbar(orientation ='horizontal')
		print(message+'['+str(i+1)+'/'+str(length+1)+']')
		if(i == length and show):
			print("To continue, close current plot window.") 
		if(save):
			plt.savefig("temp"+ str(i).zfill(4)+'.png', dpi = 'figure')
		fig.text(0.5,0.09,"m/s")
		plt.draw()
	
	anim = FuncAnimation(fig, animate, frames=length+1, interval=1, blit=False, repeat=False, init_func = init)
	message = "Displaying "
	if(show):
		plt.show()
	

	message = "Saving "
	if(save):

		if(not show):
			for i in range(length+1):
		 		animate(i)
		print("Save will complete when the application is closed. gifs are saved in directory.")
		import subprocess
		import os
		subprocess.call("convert -delay "+str(frameRate)+" temp*.png "+savename+".gif", shell=True)
		for i in range(length+1):
			os.remove("temp"+str(i).zfill(4)+'.png')

def plotLines(y, yerr, time_array, variables):
	r"""Creates a line graph of certain specifications.

	Plots a line graph, with vertical error bars using given data. It 
	is a loose wrapper around pyplot.errorbar.

	Parameters
	----------
	y:	dict
		A dictionary with variable names as keys and a numpy array 
		containing y-values to be plotted as values.
	yerr: dict
		A dictionary with variable names as keys and a numpy array
		containing the standard deviations to be plotted as values.
	time_array: array_like
		A list of time values to be plotted on the x-axis.
	variables: array_like
		A list of tuples containing the names of the variables and 
		their units as strings that need to be plotted, in the form of
		strings.  
	
	See Also
	--------
	matplotlib.pyplot.errorbar
	matplotlib.pyplot.xticks
	"""
	x = mdates.date2num(time_array)
	for (b,c) in variables:
		plt.errorbar(x,y[b], yerr=yerr[b], label = str(b) + " (in "+ str(c)+")")
	plt.legend()
	if(len(variables) >1):
		plt.ylabel("Variables")
		plt.title("Variables-Time graph")
	else:
		plt.ylabel(variables[0][0])
		plt.title(variables[0][0]+"-Time graph")
	plt.xlabel("Time")
	plt.xticks(x,time_array, rotation = 65, fontsize = "xx-small")
	plt.tight_layout()
	plt.show()