import xarray as xr
import config

def openNETCDF(filenames):
	return [xr.open_dataset(i) for i in filenames]

def getData(ind):
	dimension_list = list(config.data[ind].coords.keys())
	variable_list = list(config.data[ind].data_vars.keys())
	mess_ind = [[None, None] for i in dimension_list]
	mess_ind_2 = [None for i in dimension_list] 
	sel_message = "You have selected:\n"
	j = 0
	for x in dimension_list:
		arr = [str(a) for a in config.data[ind].variables[x].values]
		mess_ind[j][0] = arr.index(config.messages[j][0])
		sel_message += x + ' ' + str(config.data[ind].variables[x].values[mess_ind[j][0]])
		if (config.messages[j][1] is not None):
			mess_ind[j][1] = arr.index(config.messages[j][1])
			mess_ind[j].sort()
			mess_ind_2[j] = slice(mess_ind[j][0],mess_ind[j][1])
			sel_message += ' : ' + str(config.data[ind].variables[x].values[mess_ind[j][1]])
		else:
			mess_ind_2[j] = mess_ind[j][0]
		sel_message += '\n'
		j += 1
	j = 0
	ord_arr = None
	output_message = ""
	for x in variable_list:
		if(config.outVar[j]):
			ord_arr = [dimension_list.index(a) for a in config.data[ind].variables[x].dims]
			out_ind = tuple([mess_ind_2[a] for a in ord_arr])
			output_message += x + '\n' + str(config.data[ind].variables[x].values[out_ind]) + '\n'
		j += 1
	return sel_message, output_message

def getData2(ind, var_name):
	dimension_list = list(config.data[ind].coords.keys())
	mess_ind = [[None, None] for i in dimension_list]
	mess_ind_2 = [None for i in dimension_list]
	sel_message = "You have selected:\n"
	#print(config.messages)
	j = 0
	for x in dimension_list:
		arr = [str(a) for a in config.data[ind].variables[x].values]
		mess_ind[j][0] = arr.index(config.messages[j][0])
		sel_message += x + ' ' + str(config.data[ind].variables[x].values[mess_ind[j][0]])
		if (config.messages[j][1] is not None):
			mess_ind[j][1] = arr.index(config.messages[j][1])
			mess_ind[j].sort()
			mess_ind_2[j] = slice(mess_ind[j][0],mess_ind[j][1])
			sel_message += ' : ' + str(config.data[ind].variables[x].values[mess_ind[j][1]])
		else:
			mess_ind_2[j] = mess_ind[j][0]
		sel_message += '\n'
		j += 1
	ord_arr = [dimension_list.index(a) for a in config.data[ind].variables[var_name].dims]
	out_ind = tuple([mess_ind_2[a] for a in ord_arr])

	return sel_message, config.data[ind].variables[var_name].values[out_ind]