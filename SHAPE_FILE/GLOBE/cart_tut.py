import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import geopandas as gpd
import fiona
import shapely.geometry as sgeom
import netCDF4 as nc
import numpy as np
import numpy.ma as ma
import xarray as xr
import pandas as pd
from rasterio import features
from affine import Affine

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
	xr_da[coord_name] = rasterize([shapes[135]], xr_da.coords, longitude='longitude', latitude='latitude')
	return xr_da

pc = ccrs.PlateCarree()

xds = xr.open_dataset('era_interim_moda_1990.nc')
xds = xds.assign_coords(longitude=(((xds.variables['longitude'][:] + 180.0) % 360.0) - 180.0))
da1 =  xds.data_vars['t2m'][0,:,:]
da1 = da1.sortby(da1.longitude)
shpfile = 'world.shp'
test = gpd.read_file(shpfile)
with fiona.open(shpfile) as records:
    geometries = [sgeom.shape(shp['geometry']) for shp in records]
da_2 = add_shape_coord_from_data_array(da1, test, 't2m')



plt.figure()
ax = plt.axes(projection=ccrs.PlateCarree())
kwargs = dict(ax=ax, transform=pc, x='longitude', y='latitude', cbar_kwargs=dict(orientation='horizontal'))

xds = da_2.where(~np.isnan(da_2.t2m),other = np.nan)
xds.plot.pcolormesh(**kwargs)
ax.add_geometries(geometries, pc, edgecolor='gray', facecolor='none')

ax.set_global()

plt.show()
