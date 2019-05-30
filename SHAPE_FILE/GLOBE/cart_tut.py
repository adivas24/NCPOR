import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import geopandas as gpd
import fiona
import shapely.geometry as sgeom
import netCDF4 as nc
import numpy as np
import numpy.ma as ma
import xarray as xr
#plt.figure()
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
	#print(shapes)
	xr_da[coord_name] = rasterize(shapes, xr_da.coords, longitude='longitude', latitude='latitude')

	return xr_da
#ax = plt.axes(projection = ccrs.PlateCarree())
#ax.coastlines()

#shp_gpd = gpd.read_file("world.shp")
#shapes = [shape for n, shape in enumerate(shp_gpd.geometry)]
#ax.add_geometries(shapes[0:2], ccrs.PlateCarree())

ds = nc.Dataset('era_interim_moda_1990.nc')
#print(ds.variables['longitude'].assign_coords(longitude=(((ds.variables['longitude'] +180)%360)-180)))
#ds = ds.assign_coords(longitude=(((ds.variables['longitude'] +180)%360)-180))
#ds.variables['longitude'] = (ds.variables['longitude'] + 180)%360 -180
#ds.coords['longitude'] = (ds.coords['longitude'] + 180) % 360 - 180
lons = ds.variables['longitude'][:]
lons = np.where(lons >180, lons-360, lons)
lats = ds.variables['latitude'][:]
data = ds.variables['t2m'][:]

#data,lons = shiftgrid(180.,data,lons,start=False)

#plt.figure()

pc = ccrs.PlateCarree()

shpfile = 'world.shp'
with fiona.open(shpfile) as records:
    geometries = [sgeom.shape(shp['geometry']) for shp in records]

# ax1 = plt.subplot(211, projection=pc)
# ax1.pcolormesh(xx, yy, data, transform=pc)
# #ax1.coastlines()
# ax1.add_geometries(geometries, pc, edgecolor='gray', facecolor='none')
# ax1.set_global()

# ax2 = plt.subplot(212, projection=pc)
# ax2.contourf(xx, yy, data, transform=pc)
# ax2.coastlines()
# ax2.set_global()

# plt.tight_layout()
# plt.show()
xds = xr.open_dataset('era_interim_moda_1990.nc')
xds = xds.assign_coords(longitude=(((xds.variables['longitude'][:] + 180.0) % 360.0) - 180.0))
da1 =  xds.data_vars['u10'][0,:,:]
da1 = da1.sortby(da1.longitude)
#da1.assign_coords(new_longitude=(((da1.longitude + 180.0) % 360.0) - 180.0))
print(da1)
test = gpd.read_file("world.shp")
da_2 = add_shape_coord_from_data_array(da1, test, 'u10')
#da_2.plot()

#matplotlib.pyplot.show()


plt.figure()
ax = plt.axes(projection=ccrs.PlateCarree())
kwargs = dict(ax=ax, transform=pc, x='longitude', y='latitude', cbar_kwargs=dict(orientation='horizontal'))

#print(da_2)
#print(~np.isnan(da_2.u10))
xds = da_2.where(~np.isnan(da_2.u10),other = np.nan)
xds.plot.pcolormesh(**kwargs)
ax.add_geometries(geometries, pc, edgecolor='gray', facecolor='none')

ax.set_global()

plt.show()
# plt.figure()
# ax = plt.axes(projection=ccrs.PlateCarree())

# ax.set_extent([-180, 180, -90, 90])
# ax.gridlines(draw_labels=True, color='black', alpha=0.2, linestyle='--')

# #ax.imshow(img, origin='upper', extent=[-180, 180, -90, 90], transform=ccrs.PlateCarree())

# plt.show()




#print(da1)
#da1.plot()
#print float(dataSet.data_vars['t2m'][0,0,0])

#print type(test)
#shapes = [(i,j) for (j,i) in enumerate(test.geometry)]
#print shapes






# for lon in range(480):
# 	print(lon)
# 	for lat in range(241):
# 		if(not bool(np.isnan(da_2['u10'][lat][lon]))):
# 			da_2['u10'][lat][lon] = 1.0
# 		else:
# 			da_2['u10'][lat][lon] = 0.0
#print (da_2.t2m)
#test_da = da_2.where(da_2.t2m==0, other=np.nan)
#print test_da