
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename
import numpy as np
import pandas as pd
import geopandas as gpd
import xarray as xr
import config
import fiona
import file_functions as ffunc
import plot_functions as pfunc
from datetime import datetime

def addPages(filenames):
	config.pages = [ttk.Frame(config.nb) for i in range(len(filenames))]
	for i in range(len(filenames)):
		config.nb.add(config.pages[i], text = filenames[i])
	config.nb.grid(columnspan=2)

def trig(event,b,c):
	dats = event.split('_')
	i = int(dats[2])
	n1 = int(dats[1])
	config.spn_box_list[i][2*n1].grid(row = 5+n1, column = 1)
	if (config.chk_var_list1[i][n1].get() == 0):
		config.spn_box_list[i][2*n1+1].grid_forget()
	else:
		config.spn_box_list[i][2*n1+1].grid(row = 5+n1, column = 2)
	
def fillPages():
	xr_dataSet = config.data
	no_of_pages = len(config.pages)
	config.chk_var_list1 = [None for x in range(no_of_pages)]
	config.chk_var_list2 = [None for x in range(no_of_pages)]
	config.spn_box_list = [None for x in range(no_of_pages)]
	config.chk_box_list = [None for x in range(no_of_pages)]
	for i in range(no_of_pages):
		dimension_list = list(xr_dataSet[i].coords.keys())
		variable_list = list(xr_dataSet[i].data_vars.keys())
		config.chk_var_list1[i] = [None for k in range(len(dimension_list))]
		config.chk_var_list2[i] = [None for k in range(len(variable_list))]
		config.spn_box_list[i] = [tk.Spinbox(config.pages[i]) for b in range(len(dimension_list)*2)]
		n1 = 0
		for j in dimension_list:	
			createSelRow(j, n1, i)
			createSelBox(j, n1, i, list(xr_dataSet[i][j].values))
			n1 += 1
		n1+=5
		config.selBox = [createOPBox("Selection", i, n1) for l in range(no_of_pages)]
		n2 = 1
		tk.Label(config.pages[i], text="Choose output variables:").grid(row = n1+1, column = 0)
		for k in variable_list:
			createCheckBox(k, i, n1+1, n2)
			n2 += 1
		config.opBox = [createOPBox("Output data", i, n1+2) for l in range(no_of_pages)]
	tk.Button(config.root, text = 'Retrieve data', command = retrieveData).grid(row = 100, column = 0)
	tk.Button(config.root, text = 'Plot', command = openPlotWindow).grid(row = 100, column = 1)
	tk.Button(config.root, text = 'Export to CSV', command = exportToCSV).grid(row = 100, column = 2)
	tk.Button(config.root, text = 'Close', command = config.root.destroy).grid(row = 100, column = 3)


def createSelRow(name, num, ind):
	tk.Label(config.pages[ind], text = name).grid(row = num, column = 0)
	config.chk_var_list1[ind][num] = tk.IntVar(config.pages[ind], name = "var_"+str(num)+ "_" + str(ind))
	r1 = tk.Radiobutton(config.pages[ind], text = 'Single', variable = config.chk_var_list1[ind][num], value = 0)
	r1.grid(row = num, column = 1)
	r1.deselect()
	r2 = tk.Radiobutton(config.pages[ind], text = 'Range', variable = config.chk_var_list1[ind][num], value = 1)
	r2.grid(row = num, column = 2)
	r2.deselect()

def createSelBox(name, num, ind, value_list):
	value_list.sort()
	tk.Label(config.pages[ind], text = name).grid(row = num+5, column = 0)
	config.spn_box_list[ind][2*num].configure(values=value_list)
	config.spn_box_list[ind][2*num+1].configure(values=value_list)

def createOPBox(name, ind, num):
	tk.Label(config.pages[ind], text = name).grid(row = num, column = 0)
	textBox = tk.Text(config.pages[ind], height = 4)
	textBox.grid(row = num, column = 1, columnspan = 10)
	scroll = tk.Scrollbar(config.pages[ind])
	scroll.grid(row = num,column = 10)
	scroll.config(command=textBox.yview)
	textBox.config(yscrollcommand=scroll.set)
	return textBox

def createCheckBox(data_var, ind, num, num2):
	config.chk_var_list2[ind][num2-1] = tk.IntVar(config.pages[ind], name = "var_"+data_var+"_"+str(ind)+"_"+str(num2-1))
	tk.Checkbutton(config.pages[ind], text = data_var, variable = config.chk_var_list2[ind][num2-1]).grid(row = num, column = num2)

def retrieveData():
	i = config.nb.index("current")
	rangeVar = [a.get() for a in config.chk_var_list1[i]]
	config.messages = [[None, None] for a in range(len(rangeVar))]
	for x in range(len(rangeVar)):
		config.messages[x][0] = config.spn_box_list[i][x*2].get()
		if(rangeVar[x]):
			config.messages[x][1] = config.spn_box_list[i][x*2+1].get()
	config.outVar = [a.get() for a in config.chk_var_list2[i]]
	sel_message, output_message = ffunc.getData(i)
	printMessages(output_message,sel_message, i)

def printMessages(o_message, s_message, ind):
	config.selBox[ind].delete(1.0,tk.END)
	config.selBox[ind].insert(tk.INSERT, s_message)
	config.opBox[ind].delete(1.0,tk.END)
	config.opBox[ind].insert(tk.INSERT, o_message)

def openPlotWindow():
	i = config.nb.index("current")
	var_list = list(config.data[i].data_vars.keys())
	time_range = [str(pd.to_datetime(a).date()) for a in list(config.data[i].variables['time'].values)]
	window = tk.Toplevel(config.root)
	tk.Label(window, text = "Select variable: ").grid(row = 1, column = 0)
	var = tk.StringVar(window)
	var.set(var_list[0])
	tk.OptionMenu(window, var, *var_list).grid(row = 1, column = 1)
	tk.Label(window, text = "Select time: ").grid(row = 2, column = 0)
	spin = tk.Spinbox(window, values = time_range)
	spin.grid(row = 2, column = 1)
	var2 = tk.IntVar(window)
	tk.Checkbutton(window, text = "Use SHP file", variable = var2).grid(row = 3, column = 0)
	filename = ""
	var3 = tk.StringVar(window)
	shp_ind = -1
	places = []
	def shapeSelect(event, b, c):
		if (var2.get() == 1):
			nonlocal places, filename
			filename = askopenfilename(filetypes=[("SHAPEFILE", "*.shp")])
			tk.Label(window, text=filename).grid(row = 3, column = 1)
			shp = gpd.read_file(filename)
			places = list(shp['NAME'])
			places2 = [i for i in places if i is not None]
			places2.append("ALL")
			places2.sort()
			ttk.Combobox(window, textvariable = var3, values = places2).grid(row = 4, column = 1)
	def plotMapFull():
		if (var2.get() == 0):
			pfunc.plotMapFull(i,var.get(), time_range.index(spin.get()))
		else:
			if(var3.get() == "ALL"):
				plac_ind = None
			else:
				plac_ind = places.index(var3.get())
			pfunc.plotMapShape(i,var.get(), time_range.index(spin.get()), filename, plac_ind)
	var2.trace("w", shapeSelect)
	tk.Button(window, text = 'Confirm', command = plotMapFull).grid(row = 10, column = 1)

def exportToCSV():
	i = config.nb.index("current")
	var_list = list(config.data[i].data_vars.keys())
	window = tk.Toplevel(config.root)
	tk.Label(window, text = "Select variable: ").grid(row = 1, column = 0)
	var = tk.StringVar(window)
	var.set(var_list[0])
	tk.OptionMenu(window, var, *var_list).grid(row = 1, column = 1)
	def saveCSV():
		a,b = ffunc.getData2(i, var.get())
		tk.Label(window, text = a).grid(row = 2, column = 0, columnspan = 2)
		c=np.resize(b,[b.shape[0],b.shape[1]*b.shape[2]])
		pd.DataFrame(c).to_csv(var.get() + ".csv", header = None, index = None)
		tk.Label(window, text = "Done").grid(row = 3, column = 1, columnspan = 2)

	tk.Button(window, text = 'Save', command = saveCSV).grid(row = 10, column = 1)
	