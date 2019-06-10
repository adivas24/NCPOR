
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename
import numpy as np
import pandas as pd
import geopandas as gpd
import xarray as xr
import gl_vars
import fiona
import file_functions as ffunc
import plot_functions as pfunc
from datetime import datetime
import time

def getMultiSets(filenames):
	
	l1 = tk.Label(gl_vars.root, text = "Tick the ones you want to combine:")
	l1.grid(row = 0, column  = 0)
	chk_vars = [tk.IntVar(gl_vars.root) for a in filenames]
	var = tk.StringVar(gl_vars.root)
	i = 1
	chk_arr = [None for a in filenames]
	for a in filenames:
		chk_arr[i-1] = tk.Checkbutton(gl_vars.root, text = a, variable = chk_vars[i-1])
		chk_arr[i-1].grid(row = i, column = 0)
		i+=1
	l2 = tk.Label(gl_vars.root, text='Enter a new name for the set: ')
	l2.grid(row = i, column = 0)
	filenames2 = filenames
	text = tk.Entry(gl_vars.root, textvariable = var)
	text.grid(row = i, column = 1)
	def combine_files():
		nonlocal filenames2
		indxs = [a for a in range(len(filenames)) if chk_vars[a].get() == 1]
		data_mod = [gl_vars.data[a] for a in indxs]
		merged = xr.merge(data_mod)
		filenames2 = [filenames[a] for a in range(len(filenames)) if a not in indxs]
		copy = [gl_vars.data[a] for a in range(len(gl_vars.data)) if a not in indxs]
		copy.append(merged)
		gl_vars.data = copy
		filenames2.append(var.get())

	b1 = tk.Button(gl_vars.root, text = 'Combine', command = combine_files)
	b1.grid(row = i+1, column = 0)
	b2 = tk.Button(gl_vars.root, text = 'More (Refresh list)')
	b3 = tk.Button(gl_vars.root, text = 'Done')
	b3.grid(row = i+1, column = 2)

	def getMore():
		nonlocal l1, l2, b3, b2, b1, text, chk_arr
		l2.destroy()
		l1.destroy()
		b1.destroy()
		b2.destroy()
		b3.destroy()
		text.destroy()
		for a in chk_arr:
			a.destroy()
		getMultiSets(filenames2)

	b2.config(command = getMore)
	b2.grid(row = i+1, column = 1)

	def createGUI():
		nonlocal l1, l2, b2, b3, b1, text, chk_arr
		l2.destroy()
		l1.destroy()
		b1.destroy()
		b2.destroy()
		b3.destroy()
		text.destroy()
		for a in chk_arr:
			a.destroy()
		gl_vars.nb = ttk.Notebook(gl_vars.root)
		addPages(filenames2)
		fillPages()
		for i in gl_vars.chk_var_list1:
			for j in i:
				j.trace("w",trig)
	b3.config(command = createGUI)



def addPages(filenames):
	gl_vars.pages = [ttk.Frame(gl_vars.nb) for i in range(len(filenames))]
	for i in range(len(filenames)):
		gl_vars.nb.add(gl_vars.pages[i], text = filenames[i])
	gl_vars.nb.grid(columnspan=2)

def trig(event,b,c):
	dats = event.split('_')
	i = int(dats[2])
	n1 = int(dats[1])
	gl_vars.spn_box_list[i][2*n1].grid(row = 5+n1, column = 1)
	if (gl_vars.chk_var_list1[i][n1].get() == 0):
		gl_vars.spn_box_list[i][2*n1+1].grid_forget()
	else:
		gl_vars.spn_box_list[i][2*n1+1].grid(row = 5+n1, column = 2)
	
def fillPages():
	xr_dataSet = gl_vars.data
	no_of_pages = len(gl_vars.pages)
	gl_vars.chk_var_list1 = [None for x in range(no_of_pages)]
	gl_vars.chk_var_list2 = [None for x in range(no_of_pages)]
	gl_vars.chk_var_list3 = [None for x in range(no_of_pages)]
	gl_vars.spn_box_list = [None for x in range(no_of_pages)]
	for i in range(no_of_pages):
		dimension_list = list(xr_dataSet[i].coords.keys())
		variable_list = list(xr_dataSet[i].data_vars.keys())
		gl_vars.chk_var_list1[i] = [None for k in range(len(dimension_list))]
		gl_vars.chk_var_list2[i] = [None for k in range(len(variable_list))]
		gl_vars.spn_box_list[i] = [tk.Spinbox(gl_vars.pages[i]) for b in range(len(dimension_list)*2)]
		n1 = 0
		gl_vars.chk_var_list3[i] = tk.IntVar(gl_vars.pages[i])
		tk.Checkbutton(gl_vars.pages[i], text = "Use SHAPEFILE", variable = gl_vars.chk_var_list3[i]).grid(row = n1, column = 10)
		for j in dimension_list:	
			createSelRow(j, n1, i)
			createSelBox(j, n1, i, list(xr_dataSet[i][j].values))
			n1 += 1
		n1+=5
		gl_vars.selBox = [createOPBox("Selection", i, n1) for l in range(no_of_pages)]
		n2 = 1
		tk.Label(gl_vars.pages[i], text="Choose output variables:").grid(row = n1+1, column = 0)
		for k in variable_list:
			createCheckBox(k, i, n1+1, n2)
			n2 += 1
		gl_vars.opBox = [createOPBox("Output data", i, n1+2) for l in range(no_of_pages)]
	tk.Button(gl_vars.root, text = 'Retrieve data', command = retrieveData).grid(row = 100, column = 0)
	tk.Button(gl_vars.root, text = 'Plot', command = plotWindow).grid(row = 100, column = 1)
	tk.Button(gl_vars.root, text = 'Export to CSV', command = exportToCSV).grid(row = 100, column = 2)
	tk.Button(gl_vars.root, text = 'Close', command = gl_vars.root.destroy).grid(row = 100, column = 3)


def createSelRow(name, num, ind):
	tk.Label(gl_vars.pages[ind], text = name).grid(row = num, column = 0)
	gl_vars.chk_var_list1[ind][num] = tk.IntVar(gl_vars.pages[ind], name = "var_"+str(num)+ "_" + str(ind))
	r1 = tk.Radiobutton(gl_vars.pages[ind], text = 'Single', variable = gl_vars.chk_var_list1[ind][num], value = 0)
	r1.grid(row = num, column = 1)
	r1.deselect()
	r2 = tk.Radiobutton(gl_vars.pages[ind], text = 'Range', variable = gl_vars.chk_var_list1[ind][num], value = 1)
	r2.grid(row = num, column = 2)
	r2.deselect()

def createSelBox(name, num, ind, value_list):
	value_list.sort()
	tk.Label(gl_vars.pages[ind], text = name).grid(row = num+5, column = 0)
	gl_vars.spn_box_list[ind][2*num].configure(values=value_list)
	gl_vars.spn_box_list[ind][2*num+1].configure(values=value_list)

def createOPBox(name, ind, num):
	tk.Label(gl_vars.pages[ind], text = name).grid(row = num, column = 0)
	textBox = tk.Text(gl_vars.pages[ind], height = 4)
	textBox.grid(row = num, column = 1, columnspan = 6)
	scroll = tk.Scrollbar(gl_vars.pages[ind])
	scroll.grid(row = num,column = 6)
	scroll.config(command=textBox.yview)
	textBox.config(yscrollcommand=scroll.set)
	return textBox

def createCheckBox(data_var, ind, num, num2):
	gl_vars.chk_var_list2[ind][num2-1] = tk.IntVar(gl_vars.pages[ind], name = "var_"+data_var+"_"+str(ind)+"_"+str(num2-1))
	tk.Checkbutton(gl_vars.pages[ind], text = data_var, variable = gl_vars.chk_var_list2[ind][num2-1]).grid(row = num, column = num2)

def retrieveData():
	i = gl_vars.nb.index("current")
	rangeVar = [a.get() for a in gl_vars.chk_var_list1[i]]
	gl_vars.messages = [[None, None] for a in range(len(rangeVar))]
	for x in range(len(rangeVar)):
		gl_vars.messages[x][0] = gl_vars.spn_box_list[i][x*2].get()
		if(rangeVar[x]):
			gl_vars.messages[x][1] = gl_vars.spn_box_list[i][x*2+1].get()
	gl_vars.outVar = [a.get() for a in gl_vars.chk_var_list2[i]]
	if (gl_vars.chk_var_list3[i].get() == 1 and gl_vars.output is None):
		openPlotWindow(2)
	elif (gl_vars.chk_var_list3[i].get() == 1):
		masked_data = gl_vars.output
		ffunc.getData3(i, masked_data)
		gl_vars.output = None
	else:
		sel_message, output_message = ffunc.getData(i)
		printMessages(output_message,sel_message, i)

def printMessages(o_message, s_message, ind):
	gl_vars.selBox[ind].delete(1.0,tk.END)
	gl_vars.selBox[ind].insert(tk.INSERT, s_message)
	gl_vars.opBox[ind].delete(1.0,tk.END)
	gl_vars.opBox[ind].insert(tk.INSERT, o_message)

def plotWindow():
	openPlotWindow(0)

def openPlotWindow(org):
	i = gl_vars.nb.index("current")
	window = tk.Toplevel(gl_vars.root)
	var2 = tk.IntVar(window)
	if (org != 2):
		var_list = list(gl_vars.data[i].data_vars.keys())
		time_range = [str(pd.to_datetime(a).date()) for a in list(gl_vars.data[i].variables['time'].values)]
		tk.Label(window, text = "Select variable: ").grid(row = 1, column = 0)
		var = tk.StringVar(window)
		var.set(var_list[0])
		tk.OptionMenu(window, var, *var_list).grid(row = 1, column = 1)
		tk.Label(window, text = "Select time: ").grid(row = 2, column = 0)
		spin = tk.Spinbox(window, values = time_range)
		spin.grid(row = 2, column = 1)
		tk.Checkbutton(window, text = "Use SHP file", variable = var2).grid(row = 3, column = 0)
	b1 = tk.Button(window, text = 'Confirm')
	b1.grid(row = 10, column = 1)
	var3 = tk.StringVar(window)
	filename = ""
	shp_ind = -1
	places = []
	output = None
	def shapeSelect(event, b, c):
		if (var2.get() == 1 or org == 2):
			nonlocal places, filename
			filename = askopenfilename(filetypes=[("SHAPEFILE", "*.shp")])
			shp = gpd.read_file(filename)
			places = list(shp['NAME'])
			places2 = [i for i in places if i is not None]
			places2.append("ALL")
			tk.Label(window, text=filename).grid(row = 3, column = 1)
			places2.sort()
			ttk.Combobox(window, textvariable = var3, values = places2).grid(row = 4, column = 1)
		if (org == 2):
			nonlocal b1
			b1.config(command = shapeData)
	def plotMapFull():
		if (var2.get() == 0):
			pfunc.plotMapFull(i,var.get(), time_range.index(spin.get()))
		else:
			if(var3.get() == "ALL"):
				plac_ind = None
			else:
				plac_ind = places.index(var3.get())
			pfunc.plotMapShape(i,var.get(), time_range.index(spin.get()), filename, plac_ind)
	def shapeData():
		nonlocal window
		if(var3.get() == "ALL"):
			plac_ind = None
		else:
			plac_ind = places.index(var3.get())
		if (org != 2):
			gl_vars.output = ffunc.getShapeData(i,var.get(), time_range.index(spin.get()), filename, plac_ind)
		else:
			gl_vars.output = ffunc.getShapeData(i,None, None, filename, plac_ind)
		if(org == 1):
			window2 = tk.Toplevel(gl_vars.root)
			tk.Label(window2, text = "Press Save again to save the chosen shapefile masked data.").grid(row = 0, column = 0)
		window.destroy()

	var2.trace("w", shapeSelect)
	if(org == 0):
		b1.config(command = plotMapFull)
	elif(org == 1):
		var2.set(1)
		b1.config(command = shapeData)
	elif(org == 2):
		shapeSelect(None,None,None)


def exportToCSV():
	i = gl_vars.nb.index("current")
	var_list = list(gl_vars.data[i].data_vars.keys())
	window = tk.Toplevel(gl_vars.root)
	tk.Label(window, text = "Select variable: ").grid(row = 1, column = 0)
	var = tk.StringVar(window)
	vr2 = tk.IntVar(window)
	var.set(var_list[0])
	tk.OptionMenu(window, var, *var_list).grid(row = 1, column = 1)
	tk.Checkbutton(window, text = "Use SHAPEFILE?", variable = vr2).grid(row = 2, column = 1)
	def saveCSV():
		if (vr2.get() == 0):
			a,b = ffunc.getData2(i, var.get())
			c=np.resize(b,[b.shape[0],b.shape[1]*b.shape[2]])
		else: 
			a = ""
			if(gl_vars.output is not None):
				c = gl_vars.output.values
				gl_vars.output = None
			else:
				openPlotWindow(1)
				return
		tk.Label(window, text = a).grid(row = 2, column = 0, columnspan = 2)
		pd.DataFrame(c).to_csv(var.get() + ".csv", header = None, index = None, na_rep = "NaN")
		tk.Label(window, text = "Done").grid(row = 3, column = 1, columnspan = 2)
	tk.Button(window, text = 'Save', command = saveCSV).grid(row = 10, column = 1)
	