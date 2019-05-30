import numpy as np
import numpy.ma as ma
from netCDF4 import Dataset
import sys
import tkinter as tk
import math
from datetime import datetime, timedelta
from netCDF4 import num2date, date2num
import pandas as pd

num_files = len(sys.argv)-1
nc_array = []
for i in range(num_files):
	nc_array.append(Dataset(sys.argv[i+1], 'r'))

dim_no = 1
dim_set = [x for x in nc_array[0].dimensions.keys() if x != u'time' and x != u'Time']
dime_info = dict()
for a in dim_set:
	array = [None, None, None]
	array[0] = nc_array[0].variables[a][:]
	array[1] = float(np.amin(array[0]))
	array[2] = float(np.amax(array[0]))
	dime_info[a] = array
	dim_no += 1


time_range = []
for x in nc_array:
	time_range = np.append(time_range, x.variables['time'][:])


time_unit = nc_array[0].variables['time'].units
try:
	time_calendar = nc_array[0].variables['time'].time_calendar
except:
	time_calendar = "standard"

time_array = [num2date(a,time_unit,time_calendar) for a in time_range]
time_array_2 = [a.strftime("%m")+"/"+a.strftime("%Y") for a in time_array]

year_min = int(min(time_array).strftime("%Y"))
year_max = int(max(time_array).strftime("%Y"))


vars_array =[x for x in nc_array[0].variables.keys() if x not in dim_set and x != u'time' and x!= u'Time']
var_data_array = dict()
for i in range(num_files):
	for a in vars_array:
		if (a in var_data_array.keys()):
			var_data_array[a] = ma.concatenate([var_data_array[a],nc_array[i].variables[a][:]],0)
		else:
			var_data_array[a] = nc_array[i].variables[a][:]

def trig(event,b,c):
	chk_i = int(event[4])		#This will fail if number of dimensions is more than a single digit number
	spinbox_array[2*chk_i].grid(row = 3+chk_i, column = 1)
	if (chk_var[chk_i].get() % 2 == 0):
		spinbox_array[2*chk_i+1].grid_forget()
	else:
		spinbox_array[2*chk_i+1].grid(row = 3+chk_i, column = 2)


def retrieveData():
	getData(textBox1, textBox2)

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
		year = spinbox_array[2*len(dim_set)].get()
		index_vars['time'] = np.argmin(np.abs(time_range-date2num(datetime(int(year[3:7]),int(year[0:2]),1),time_unit, time_calendar)))
	
		message1 = 'You have selected\n'
		message2 = ''
	
		for x in dim_set:
			message1 = message1 + x + ': ' + str(dime_info[x][0][index_vars[x]])+'\n'
		message1 = message1 + 'time: ' + time_array_2[index_vars['time']]
	
		for y in vars_array:
			ind_array = tuple([np.array(index_vars[a]) for a in nc_array[0].variables[y].dimensions])
			message2 = message2 + y +': ' + str(var_data_array[y][ind_array]) +'\n'

	else:
		x = 0
		for i in dim_set:
			index_vars[i] = [np.argmin(np.abs(dime_info[i][0]-float(spinbox_array[x*2].get()))), np.argmin(np.abs(dime_info[i][0]-float(spinbox_array[x*2].get())))+1]
			if (chk_var[x].get() == 1):
				index_vars[i][1] = np.argmin(np.abs(dime_info[i][0]-float(spinbox_array[x*2+1].get()))) +1
			x += 1
		
		year1 = spinbox_array[2*len(dim_set)].get()
		index_vars['time'] = [np.argmin(np.abs(time_range-date2num(datetime(int(year1[3:7]),int(year1[0:2]),1),time_unit, time_calendar))) for i in range(2)]
		index_vars['time'][1] += 1

		if (chk_var[x].get() == 1):
			year2 = spinbox_array[len(dim_set)*2+1].get()
			index_vars['time'][1] = np.argmin(np.abs(time_range-date2num(datetime(int(year2[3:7]),int(year2[0:2]),1),time_unit, time_calendar)))
	
		message1 = 'You have selected:\n'
		message2 = ''
		for x in dim_set:
			message1 = message1 + x +': ' +str(dime_info[x][0][index_vars[x][0]]) + ':' + str(dime_info[x][0][index_vars[x][1]])+ '\n'
		message1 = message1 + 'time: ' + time_array_2[index_vars['time'][0]] +':' + time_array_2[index_vars['time'][1]]
		for y in vars_array:
			ind_array =tuple([slice(min(index_vars[a][0],index_vars[a][1]),max(index_vars[a][0],index_vars[a][1])+1) for a in nc_array[0].variables[y].dimensions])
			#print ind_array
			message2 = message2 + y+ ': ' + str(var_data_array[y][ind_array]) + '\n'

	msg1.delete(1.0,tk.END)
	msg2.delete(1.0,tk.END)
	msg1.insert(tk.INSERT, message1)
	msg2.insert(tk.INSERT, message2)
	#pd.DataFrame(var_data_array['u10'][ind_array]).to_csv("testcsvfile.csv")

global m, textBox1,textBox2, chk_var

m = tk.Tk()
m.title('Read NC')


spinbox_array = [tk.Spinbox(m) for i in range(2*len(dim_set)+2)]
chk_var = [tk.IntVar(name = 'var_'+str(i)) for i in range(len(dim_set)+1)]

n1 = 0
for i in dim_set:
	tk.Label(m,text = i).grid(row = n1,column = 0)
	r1 = tk.Radiobutton(m, text = 'Single', variable = chk_var[n1], value = 0)
	r1.grid(row = n1, column = 1)
	r1.deselect()
	r2 = tk.Radiobutton(m, text = 'Range', variable = chk_var[n1], value = 1)
	r2.grid(row = n1, column = 2)
	r2.deselect()
	tk.Label(m, text = i).grid(row = n1+dim_no,column = 0)
	spinbox_array[2*n1].configure(values = tuple(dime_info[i][0]), format = '%5.2f')
	spinbox_array[2*n1 + 1].configure(values = tuple(dime_info[i][0]), format = '%5.2f')
	n1+=1


tk.Label(m,text = 'time').grid(row = n1, column = 0)
r1 = tk.Radiobutton(m, text = 'Single', variable = chk_var[n1], value = 0)
r1.grid(row = n1, column = 1)
r1.deselect()
r2 = tk.Radiobutton(m, text = 'Range', variable = chk_var[n1], value = 1)
r2.grid(row = n1, column = 2)
r2.deselect()
for i in chk_var:
	i.trace("w", trig)
tk.Label(m, text = 'Time').grid(row = n1+dim_no,column = 0)
spinbox_array[2*n1].configure(values=time_array_2)
spinbox_array[2*n1+1].configure(values = time_array_2)

n1 += 1+dim_no
textBox1 = tk.Text(m, height = 4)
textBox1.grid(row = n1, column = 0, columnspan = 10)
scroll1 = tk.Scrollbar(m)
scroll1.grid(row = n1,column = 10)
scroll1.config(command=textBox1.yview)
textBox1.config(yscrollcommand=scroll1.set)
textBox2 = tk.Text(m, height = 4)
textBox2.grid(row = n1+1, column = 0, columnspan = 10)
scroll2 = tk.Scrollbar(m)
scroll2.grid(row = n1+1,column = 10)
scroll2.config(command=textBox2.yview)
textBox2.config(yscrollcommand=scroll2.set)

n1+=2
tk.Button(m,text = 'Retrieve data', command = retrieveData).grid(row = n1, column = 0)
tk.Button(m,text = 'Close', command = m.destroy).grid(row = n1, column = 1)
m.mainloop()

for dat in nc_array:
	dat.close()