import xarray as xr


def openNETCDF(filenames):
	return [xr.open_dataset(i) for i in filenames]