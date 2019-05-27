import numpy as np
import numpy.ma as ma
from netCDF4 import Dataset
#import fun
import sys
import Tkinter as tk
import math
# e$$0+nc@0r

num_files = len(sys.argv)-1
nc_array = []
for i in range(num_files):
	nc_array.append(Dataset(sys.argv[i+1], 'r'))

dim_no = 0
dim_set = [x for x in nc_array[0].dimensions.keys() if x != u'time' and x != u'Time']
dime_info = dict()
time_range = []

for a in dim_set:
	array = [None, None, None]
	array[0] = nc_array[0].variables[a][:]
	array[1] = float(np.amin(array[0]))
	array[2] = float(np.amax(array[0]))
	dime_info[a] = array
	dim_no += 1

for x in nc_array:
	time_range = np.append(time_range, x.variables['time'][:])
year_min = int(np.amin(time_range)//(24*365))+1900
year_max = int(np.amax(time_range)//(24*365))+1900

# lon = dime_info['longitude'][0]
#lon = nc_array[1].variables['longitude'][:]
#lon_min = float(np.amin(dime_info['longitude'][0]))
#lon_max = float(np.amax(dime_info['longitude'][0]))

# lat = dime_info['latitude'][0]
#lat = nc_array[1].variables['latitude'][:]
#lat_min = float(np.amin(dime_info['latitude'][0]))
#lat_max = float(np.amax(dime_info['latitude'][0]))


vars_array =[x for x in nc_array[0].variables.keys() if x not in dim_set and x != u'time' and x!= u'Time']
var_data_array = dict()
for i in range(num_files):
	for a in vars_array:
		var_data_array[a] = ma.concatenate([var_data_array.get(a,ma.empty(nc_array[i].variables[a][:].shape)),nc_array[i].variables[a][:]], 0)
		#var_data_array[a] = var_data_array.get(a,ma.zeros(nc_array[i].variables[a][:].shape)) + nc_array[i].variables[a][:]
# print len(var_data_array['t2m'])
# u10 = nc_array[1].variables['u10'][:]
# v10 = nc_array[1].variables['v10'][:]
#t2m = nc_array[1].variables['t2m'][:]
dataset = []
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
for b in range(year_min,year_max+1):
	for a in months:
		dataset.append(a+' '+ str(b))

def trig(event,b,c):
	chk_i = int(event[4])		#This will fail if number of dimensions is more than a single digit number
	spinbox_array[2*chk_i].grid(row = 3+chk_i, column = 1)
	if (chk_var[chk_i].get() % 2 == 0):
		spinbox_array[2*chk_i+1].grid_forget()
	else:
		spinbox_array[2*chk_i+1].grid(row = 3+chk_i, column = 2)


# def trig1(event, b, c):
# 	spinbox_array[0].grid(row = 3, column = 1)
# 	if (v_lon.get() is 1):
# 		spinbox_array[1].grid_forget()
# 	if (v_lon.get() is 2):
# 		spinbox_array[1].grid(row = 3, column = 2)

# def trig2(event, b, c):
# 	spinbox_array[2].grid(row = 4, column = 1)
# 	if (v_lat.get() is 1):
# 		spinbox_array[3].grid_forget()
# 	if (v_lat.get() is 2):
# 		spinbox_array[3].grid(row = 4, column = 2)

# def trig3(event, b, c):
# 	ent4.grid(row = 5, column = 1)
#	if (v_tim.get() is 1):
#		ent5.grid_forget()
#	if (v_tim.get() is 2):
#		ent5.grid(row = 5, column = 2)

# def validate1(data, widget):
# 	key = math.modf(float(data)/0.75)
# 	if (float(data) >= 0.0 and float(data) <=359.5 and key[0] < 0.0000001):
# 		return True
# 	return False

def retrieveData():
	getData(messageBox1, messageBox2)

def getData(msg1, msg2):
	test_var = 0
	for i in chk_var:
		test_var += i.get()	
		index_vars = dict()
	if (test_var == 0):
		x = 0
		for i in dim_set:
			index_vars[i] = np.argmin(np.abs(dime_info[i][0]-float(spinbox_array[x*2].get())))
			x+=1
		#lon_i = np.argmin(np.abs(dime_info['longitude'][0]-float(ent0.get())))
		#lat_i = np.argmin(np.abs(dime_info['latitude'][0]-float(ent2.get())))
		year = spinbox_array[2*len(dim_set)].get()
		month = months.index(year[0:3])
		yr = int(year[3:8])
		index_vars['time'] = month + (yr-year_min)*12
		message1 = 'You have selected: Longitude: '+str(dime_info['longitude'][0][index_vars['longitude']])+' Latitude: '+str(dime_info['latitude'][0][index_vars['latitude']])+ ' Time: '+year
		message2 = 'u10: '+ str(var_data_array['u10'][index_vars['time'],index_vars['latitude'],index_vars['longitude']]) + ' m/s\n' + 'v10: '+ str(var_data_array['v10'][index_vars['time'],index_vars['latitude'],index_vars['longitude']]) + ' m/s\n' +  't2m: ' + str(var_data_array['t2m'][index_vars['time'],index_vars['latitude'],index_vars['longitude']]) + ' K'
		msg1.config(text = message1)
		msg2.config(text = message2)

	else:
		x = 0
		for i in dim_set:
			index_vars[i] = [np.argmin(np.abs(dime_info[i][0]-float(spinbox_array[x*2].get()))), np.argmin(np.abs(dime_info[i][0]-float(spinbox_array[x*2].get())))+1]
			if (chk_var[x].get() == 1):
				index_vars[i][1] = np.argmin(np.abs(dime_info[i][0]-float(spinbox_array[x*2].get()))) +1
			x += 1
		# lon_i1 = np.argmin(np.abs(dime_info['longitude'][0]-float(ent0.get())))
		# if (v_lon.get() is 2):
		# 	lon_i2 = np.argmin(np.abs(dime_info['longitude'][0]-float(ent1.get())))
		# else:
		# 	lon_i2 = lon_i1+1
		# lat_i1 = np.argmin(np.abs(dime_info['latitude'][0]-float(ent2.get())))
		# if (v_lat.get() is 2):
		# 	lat_i2 = np.argmin(np.abs(dime_info['latitude'][0]-float(ent3.get())))
		# else:
		# 	lat_i2 = lat_i1-1
		
		year1 = spinbox_array[2*len(dim_set)].get()
		month1 = months.index(year1[0:3])
		yr1 = int(year1[3:8])
		index_vars['time'] = [month1 + (yr1-year_min)*12,month1 + (yr1-year_min)*12 +1] 
		if (chk_var[x].get() == 1):
			year2 = spinbox_array[len(dim_set)*2+1].get()
			month2 = months.index(year2[0:3])
			yr2 = int(year2[3:8])
			index_vars['time'][1] = month2 + (yr2-year_min)*12
		#else:
		#	year2 = year1
		#	month2 = month1
		#	tim_i2 = tim_i1+1
		message1 = 'Longitude: '+str(dime_info['longitude'][0][index_vars])+':'+str(dime_info['longitude'][0][lon_i2])+'\nLatitude: '+str(dime_info['latitude'][0][lat_i1])+':'+str(dime_info['latitude'][0][lat_i2])+'\nTime: '+ year1 + ' to '+ year2
		message2 = 'u10: '+str(var_data_array['u10'][tim_i1:tim_i2,lat_i2:lat_i1,lon_i1:lon_i2]) + '\nv10: '+str(var_data_array['v10'][tim_i1:tim_i2,lat_i2:lat_i1,lon_i1:lon_i2])+ '\nt2m: '+str(var_data_array['t2m'][tim_i1:tim_i2,lat_i2:lat_i1,lon_i1:lon_i2])
		msg1.config(text = message1)
		msg2.config(text = message2)


global m, messageBox1, messageBox2, chk_var

m = tk.Tk()
m.title('Read NC')


#check_var = tk.IntVar()
#check_var.trace("w",trig)
spinbox_array = [tk.Spinbox(m) for i in range(2*len(dim_set)+2)]
chk_var = [tk.IntVar(name = 'var_'+str(i)) for i in range(len(dim_set)+1)]
for i in chk_var:
	i.trace("w", trig)
# v_lon = tk.IntVar()
# v_lon.trace("w", trig1)

n1 = 0
for i in dim_set:
	tk.Label(m,text = i).grid(row = n1,column = 0)
	tk.Radiobutton(m, text = 'Single', variable = chk_var[n1], value = 0).grid(row = n1, column = 1)
	tk.Radiobutton(m, text = 'Range', variable = chk_var[n1], value = 1).grid(row = n1, column = 2)
	tk.Label(m, text = i).grid(row = n1+3,column = 0)
	spinbox_array[2*n1].configure(from_ = dime_info[i][1], to_ = dime_info[i][2], increment = 0.75, format = '%5.2f')
	spinbox_array[2*n1 + 1].configure(from_ = dime_info[i][1], to_ = dime_info[i][2], increment = 0.75, format = '%5.2f')
	n1+=1
# tk.Label(m,text = 'Longitude').grid(row = 0, column = 0)
# tk.Radiobutton(m, text = 'Single', variable = v_lon, value = 1).grid(row = 0, column = 1)
# tk.Radiobutton(m, text = 'Range', variable = v_lon, value = 2).grid(row = 0, column = 2)

# v_lat = tk.IntVar()
# v_lat.trace("w", trig2)
# tk.Label(m,text = 'Latitude').grid(row = 1, column = 0)
# tk.Radiobutton(m, text = 'Single', variable = v_lat, value = 1).grid(row = 1, column = 1)
# tk.Radiobutton(m, text = 'Range', variable = v_lat, value = 2).grid(row = 1, column = 2)

tk.Label(m,text = 'time').grid(row = n1, column = 0)
tk.Radiobutton(m, text = 'Single', variable = chk_var[n1], value = 0).grid(row = n1, column = 1)
tk.Radiobutton(m, text = 'Range', variable = chk_var[n1], value = 1).grid(row = n1, column = 2)


# tk.Label(m, text = 'Lon').grid(row = 3,column = 0)
# ent0 = tk.Spinbox(m, from_ = 0.00, to_ = 359.50, increment = 0.75, format = '%5.2f', validate = 'all')
# ent0['vcmd'] = (ent0.register(validate1), '%s', '%W')
# #ent0.grid(row = 3, column = 1)

# ent1 = tk.Spinbox(m, from_ = 0.00, to_ = 359.50, increment = 0.75, format = '%5.2f', validate = 'all')
# ent1['vcmd'] = (ent1.register(validate1), '%s', '%W')
# #ent1.grid(row = 3, column = 2)


# tk.Label(m, text = 'Lat').grid(row = 4,column = 0)
# ent2 = tk.Spinbox(m, from_ = -90.00, to_ = 90.00, increment = 0.75, format = '%4.2f', validate = 'all')
# ent2['vcmd'] = (ent2.register(validate1), '%s', '%W')
# #ent2.grid(row = 4, column = 1)

# ent3 = tk.Spinbox(m, from_ = -90.00, to_ = 90.00, increment = 0.75, format = '%4.2f', validate = 'all')
# ent3['vcmd'] = (ent3.register(validate1), '%s', '%W')
# #ent3.grid(row = 4, column = 2)
tk.Label(m, text = 'Time').grid(row = n1+3,column = 0)
spinbox_array[2*n1].configure(values=dataset)
spinbox_array[2*n1+1].configure(values = dataset)
#ent4 = tk.Spinbox(m, values = dataset)
#ent4.grid(row = 5, column = 1)

#ent5 = tk.Spinbox(m,values = dataset)
#ent5.grid(row = 5, column = 2)
n1 += 4
messageBox1 = tk.Message(m, text = ' ')
messageBox1.grid(row = n1, column = 0, columnspan = 10)
messageBox2 = tk.Message(m, text = ' ')
messageBox2.grid(row = n1+1, column = 0, columnspan = 10)

n1+=2
tk.Button(m,text = 'Retrieve data', command = retrieveData).grid(row = n1, column = 0)
tk.Button(m,text = 'Close', command = m.destroy).grid(row = n1, column = 1)
m.mainloop()

for dat in nc_array:
	dat.close()


#Grid point Querying

# t = fun.getInput('longitude', lon_min, lon_max)
# lon_i  = np.argmin(np.abs(lon-t))

# t = fun.getInput('latitude',lat_min,lat_max)
# lat_i  = np.argmin(np.abs(lat-t))

# t = int(fun.getInput('year', year_min,year_max))
# mon = int(fun.getInput('month',1,12))

# tim_i = (t-year_min)*12 + (mon - 1)

# print 'You have selected:\n Longitude: '+str(lon[lon_i])+'\n Latitude: '+str(lat[lat_i])+ '\n Time: '+str(mon)+'/'+str(t)
# print 'u10: '+ str(u10[tim_i,lat_i,lon_i]) + ' m/s ' + 'v10: '+ str(v10[tim_i,lat_i,lon_i]) + ' m/s ' +  't2m: ' + str(t2m[tim_i,lat_i,lon_i]) + ' K'

# Range Querying

# t = fun.getRange('longitude', lon_min, lon_max)
# lon_i1 = np.argmin(np.abs(lon-t[0]))
# lon_i2 = np.argmin(np.abs(lon-t[1]))

# t = fun.getRange('latitude', lat_min, lat_max)
# lat_i1 = np.argmin(np.abs(lat-t[0]))
# lat_i2 = np.argmin(np.abs(lat-t[1]))

# t = fun.getDateRange(year_min, year_max)
# tim_i1 = (t[1]-year_min)*12 + (t[0]-1)
# tim_i2 = (t[3]-year_min)*12 + (t[2]-1)

# print lon_i1, lon_i2, lat_i1, lat_i2, tim_i1, tim_i2
# print u10[tim_i1:tim_i2,lat_i2:lat_i1,lon_i1:lon_i2]