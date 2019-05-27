import numpy as np
import numpy.ma as ma
from netCDF4 import Dataset
import sys
import Tkinter as tk
import math

num_files = len(sys.argv)-1
nc_array = []
for i in range(num_files):
	nc_array.append(Dataset(sys.argv[i+1], 'r'))

#print nc_array[0].variables['u10'].dimensions
dim_no = 0
dim_set = [x for x in nc_array[0].dimensions.keys() if x != u'time' and x != u'Time']
dime_info = dict()
time_range = []
time_unit = nc_array[0].variables['time'].units.split()
if (time_unit[0] == "hours" and time_unit[1] == "since"):
	year_base = int(time_unit[2].split('-')[0])

for a in dim_set:
	array = [None, None, None]
	array[0] = nc_array[0].variables[a][:]
	array[1] = float(np.amin(array[0]))
	array[2] = float(np.amax(array[0]))
	dime_info[a] = array
	dim_no += 1

for x in nc_array:
	time_range = np.append(time_range, x.variables['time'][:])
year_min = int((np.amin(time_range)//(24*365)))+year_base - int(np.amin(time_range)//(24*365*365*4))
year_max = int((np.amax(time_range)//(24*365)))+year_base - int(np.amin(time_range)//(24*365*365*4))


vars_array =[x for x in nc_array[0].variables.keys() if x not in dim_set and x != u'time' and x!= u'Time']
var_data_array = dict()
for i in range(num_files):
	for a in vars_array:
		var_data_array[a] = ma.concatenate([var_data_array.get(a,ma.empty(nc_array[i].variables[a][:].shape)),nc_array[i].variables[a][:]], 0)

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
		month = months.index(year[0:3])
		yr = int(year[3:8])
		index_vars['time'] = month + (yr-year_min)*12
		message1 = 'You have selected\n'
		message2 = ''
		for x in dim_set:
			message1 = message1 + x + ': ' + str(dime_info[x][0][index_vars[x]])+'\n'
		message1 = message1 + 'time: ' + year

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
		month1 = months.index(year1[0:3])
		yr1 = int(year1[3:8])
		index_vars['time'] = [month1 + (yr1-year_min)*12,month1 + (yr1-year_min)*12 +1] 
		if (chk_var[x].get() == 1):
			year2 = spinbox_array[len(dim_set)*2+1].get()
			month2 = months.index(year2[0:3])
			yr2 = int(year2[3:8])
			index_vars['time'][1] = month2 + (yr2-year_min)*12

		message1 = 'You have selected:\n'
		message2 = ''
		for x in dim_set:
			message1 = message1 + x +': ' +str(dime_info[x][0][index_vars[x][0]]) + ':' + str(dime_info[x][0][index_vars[x][1]])+ '\n'
		message1 = message1 + 'time: ' + year1 +':' + year2
		for y in vars_array:
			ind_array =tuple([slice(min(index_vars[a][0],index_vars[a][1]),max(index_vars[a][0],index_vars[a][1])+1) for a in nc_array[0].variables[y].dimensions])
			print ind_array
			message2 = message2 + y+ ': ' + str(var_data_array[y][ind_array]) + '\n'

	msg1.delete(1.0,tk.END)
	msg2.delete(1.0,tk.END)
	msg1.insert(tk.INSERT, message1)
	msg2.insert(tk.INSERT, message2)

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
	tk.Label(m, text = i).grid(row = n1+3,column = 0)
	spinbox_array[2*n1].configure(from_ = dime_info[i][1], to_ = dime_info[i][2], increment = 0.75, format = '%5.2f')
	spinbox_array[2*n1 + 1].configure(from_ = dime_info[i][1], to_ = dime_info[i][2], increment = 0.75, format = '%5.2f')
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
tk.Label(m, text = 'Time').grid(row = n1+3,column = 0)
spinbox_array[2*n1].configure(values=dataset)
spinbox_array[2*n1+1].configure(values = dataset)

n1 += 4
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