import xarray as xr
import config

def openNETCDF(filenames):
	return [xr.open_dataset(i) for i in filenames]

def getData(ind):
	dimension_list = list(config.data[ind].coords.keys())
	variable_list = list(config.data[ind].data_vars.keys())
	dat = [str(a) for a in config.data[ind].variables[dimension_list[2]].values]
	mess_ind = [[None, None] for i in dimension_list]
	j = 0
	mess_ind_2 = [None for i in dimension_list] 
	for x in dimension_list:
		arr = [str(a) for a in config.data[ind].variables[x].values]
		mess_ind[j][0] = arr.index(config.messages[j][0])
		if (config.messages[j][1] is not None):
			mess_ind[j][1] = arr.index(config.messages[j][1])
			mess_ind[j].sort()
			mess_ind_2[j] = slice(mess_ind[j][0],mess_ind[j][1])
		else:
			mess_ind_2[j] = mess_ind[j][0]
		j += 1
	j = 0
	ord_arr = None
	for x in variable_list:
		if(config.outVar[j]):
			ord_arr = [dimension_list.index(a) for a in config.data[ind].variables[x].dims]
			out_ind = tuple([mess_ind_2[a] for a in ord_arr])
			print(x,'\n',config.data[ind].variables[x].values[out_ind])
		j += 1
