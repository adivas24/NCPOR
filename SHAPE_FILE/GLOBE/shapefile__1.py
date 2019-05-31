import fiona
from rasterio import features
from affine import Affine
import numpy as np
import pandas as pd
import xarray as xr
import geopandas as gpd
import matplotlib
import cartopy.crs as ccrs

dataSet = xr.open_dataset("era_interim_moda_1990.nc")

da1 =  dataSet.data_vars['u10'][0,:,:]

test = gpd.read_file("world.shp")

def transform_from_latlon(lat, lon):

	lat = np.asarray(lat)
	lon = np.asarray(lon)
	trans = Affine.translation(lon[0], lat[0])
	scale = Affine.scale(lon[1] - lon[0], lat[1] - lat[0])
	return trans * scale

def rasterize(shapes, coords, latitude='latitude', longitude='longitude', fill=np.nan, **kwargs):

	transform = transform_from_latlon(coords[latitude], coords[longitude])
	out_shape = (len(coords[latitude]), len(coords[longitude]))
	raster = features.rasterize(shapes, out_shape=out_shape, fill=fill, transform=transform, dtype=float, **kwargs)
	spatial_coords = {latitude: coords[latitude], longitude: coords[longitude]}
	return xr.DataArray(raster, coords=spatial_coords, dims=(latitude, longitude))

def add_shape_coord_from_data_array(xr_da, shp_path, coord_name):

	shp_gpd = gpd.read_file("world.shp")
	shapes = [(shape, n) for n, shape in enumerate(shp_gpd.geometry)]
	xr_da[coord_name] = rasterize(shapes, xr_da.coords, longitude='longitude', latitude='latitude')
	return xr_da

da_2 = add_shape_coord_from_data_array(da1, test, 'u10')


# Output this to a text file for a cool visualization.
# for lon in range(480):
# 	for lat in range(241):
# 		if(not bool(np.isnan(da_2['u10'][lat][lon]))):
# 			da_2['u10'][lat][lon] = 1.0
# 		else:
# 			da_2['u10'][lat][lon] = 0.0
da_2.plot()
print(da_2)
matplotlib.pyplot.show()