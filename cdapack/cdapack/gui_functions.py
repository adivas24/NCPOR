# gui_functions.py #

from file_functions import FileHandler, combineFiles
from plot_functions import PlotMaps, plotLines

import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename, askopenfilenames, asksaveasfilename

# Used for creating the GUI.

import numpy as np
import pandas as pd
import geopandas as gpd
import xarray as xr
# Used for data retrieval and manipulation.

from datetime import datetime
#Used for converting datetime to date. 

# TODO	Go through and clean up code.
#		Exception and error handling needs to be done. Input and pre-condition validation are important.

class PlotGenerator(object):
	def __init__(self, parent):
		self.parent = parent
		self.filename = self.parent.nb.tab(self.parent.nb.select(), "text")
		self.dataset = self.parent.file_handler.data[self.filename]
		window = tk.Toplevel(self.parent.root)
		self.time_range = [str(pd.to_datetime(a).date()) for a in list(self.dataset.variables['time'].values)]
		tk.Label(window, text = "Time range: ").grid(row = 0, column = 0)
		self.varSpin = tk.StringVar(window)
		self.varSpin_o = tk.StringVar(window)
		tk.Spinbox(window, values = self.time_range, textvariable = self.varSpin).grid(row = 0, column = 1)
		tk.Spinbox(window, values = self.time_range, textvariable = self.varSpin_o).grid(row = 0, column = 2)
		tk.Label(window, text = "Select time interval for x axis: ").grid(row = 1, column = 0)
		self.varSpin1 = tk.StringVar(window)
		self.varSpin2 = tk.StringVar(window)
		self.spbox = tk.Spinbox(window, textvariable = self.varSpin1)
		self.spbox.grid(row = 1, column = 1)
		ttk.Combobox(window, textvariable = self.varSpin2, values = ["years", "months", "days"]).grid(row = 1, column = 2)
		tk.Label(window, text = "Select filters:").grid(row = 25, column = 0)
		self.val_filt = tk.IntVar(window)
		tk.Radiobutton(window, variable = self.val_filt, value = 0, text = "No filters").grid(row = 26, column = 0)
		tk.Radiobutton(window, variable = self.val_filt, value = 1, text = "Lat-Lon bounds").grid(row = 26, column = 1)
		tk.Radiobutton(window, variable = self.val_filt, value = 2, text = "ShapeFile").grid(row = 26, column = 2)

		self.varSpin2.trace("w", self.fillValues)
		
		lon_var,lat_var = None, None
		for a in list(self.parent.file_handler.data[self.filename].dims):
			if (a.lower().startswith("lon")):
				lon_var = a
			if (a.lower().startswith("lat")):
				lat_var = a
		
		lat_arr = list(self.dataset.variables[lat_var].values)
		self.lat_arr2 = [str(a) for a in lat_arr]
		lat_arr.sort()
		lon_arr = list(self.dataset.variables[lon_var].values)
		self.lon_arr2 = [str(a) for a in lon_arr]
		lon_arr.sort()
		self.lbl1 = tk.Label(window, text = "Latitude Range:")
		self.spn_box1 = tk.Spinbox(window, values = lat_arr)
		self.spn_box2 = tk.Spinbox(window, values = lat_arr)
		self.lbl2 = tk.Label(window, text = "Longitude Range:")
		self.spn_box3 = tk.Spinbox(window, values = lon_arr)
		self.spn_box4 = tk.Spinbox(window, values = lon_arr)
		self.filename = None
		self.lbl3 = tk.Label(window)
		self.lbl4 = tk.Label(window, text = "Select place:")
		self.plc_var = tk.StringVar(window)
		self.cmb1 = ttk.Combobox(window, textvariable = self.plc_var)
		self.places = None

		self.val_filt.trace("w", self.selectFilter)

		tk.Label(window, text = "Select variables:" ).grid(row = 20,column = 0)
		self.var_var = dict()
		num = 0
		for x in list(self.dataset.data_vars.keys()):
			self.var_var[x] = tk.IntVar(window)
			tk.Checkbutton(window, text = x, variable = self.var_var[x]).grid(row = 21, column = num)
			num += 1
		b1 = tk.Button(window, text = "Plot")
		b1.grid(row = 100, column = 1)
		b1.config(command = self.dataPlot)

	def dataPlot(self):
		start_time_index = self.time_range.index(self.varSpin.get())
		end_time_index = self.time_range.index(self.varSpin_o.get())
		time_interval = (int(self.varSpin1.get()), self.varSpin2.get())
		variables = [(key,self.dataset.variables[key].attrs['units']) for key,value in self.var_var.items() if value.get() == 1]
		if (self.val_filt.get() == 0):
			output_mean, output_std, time_array = self.parent.file_handler.plotData(self.dataset, start_time_index, end_time_index, time_interval, variables)
		elif(self.val_filt.get() == 1):
			lat_r = [self.lat_arr2.index(self.spn_box1.get()),self.lat_arr2.index(self.spn_box2.get())]
			lon_r = [self.lon_arr2.index(self.spn_box3.get()),self.lon_arr2.index(self.spn_box4.get())]
			lat_r.sort()
			lon_r.sort()
			output_mean, output_std, time_array = self.parent.file_handler.plotData(self.dataset, start_time_index, end_time_index, time_interval, variables, filt = "bounds", lat_range = slice(lat_r[0], lat_r[1]), lon_range = slice(lon_r[0], lon_r[1]))
		elif(self.val_filt.get() == 2):
			if(self.plc_var.get() == "ALL"):
				plac_ind = None
			else:
				plac_ind = self.places.index(self.plc_var.get())
			output_mean, output_std, time_array = self.parent.file_handler.plotData(self.dataset, start_time_index, end_time_index, time_interval, variables, filt = "shapefile", filename = self.filename, place = plac_ind)
		plotLines(output_mean, output_std, time_array, variables)

	def fillValues(self, event, b, c):
		#IDEALLY THIS IS NOT REQUIRED, USER SHOULD BE ABLE TO ENTER WHATEVER THEY WANT.
		if (self.varSpin2.get() == "years"):
			arr = [a for a in range(1,21)]
		elif (self.varSpin2.get() == "months"):
			arr = [a for a in range(1,13)]
		elif (self.varSpin2.get() == "days"):
			arr = [a for a in range(1,32)]
		self.spbox.config(values = arr)
	
	def selectFilter(self,event, b, c):
		if (self.val_filt.get() == 0):
			self.lbl1.grid_forget()
			self.spn_box1.grid_forget()
			self.spn_box2.grid_forget()
			self.lbl2.grid_forget()
			self.spn_box3.grid_forget()
			self.spn_box4.grid_forget()
			self.lbl3.grid_forget()
			self.lbl4.grid_forget()
			self.cmb1.grid_forget()
			self.filename = None

		elif (self.val_filt.get() == 1):
			self.lbl1.grid(row = 27, column = 0)
			self.spn_box1.grid(row = 27, column = 1)
			self.spn_box2.grid(row = 27, column = 2)
			self.lbl2.grid(row = 28, column = 0)
			self.spn_box3.grid(row = 28, column = 1)
			self.spn_box4.grid(row = 28, column = 2)
			self.lbl3.grid_forget()
			self.lbl4.grid_forget()
			self.cmb1.grid_forget()
			self.filename = None

		elif(self.val_filt.get() == 2):
			self.lbl1.grid_forget()
			self.spn_box1.grid_forget()
			self.spn_box2.grid_forget()
			self.lbl2.grid_forget()
			self.spn_box3.grid_forget()
			self.spn_box4.grid_forget()
			self.filename = askopenfilename(filetypes=[("SHAPEFILE", "*.shp")])
			if (self.filename == ""):
				self.filename = None
				self.val_filt.set(0)
			else:
				shp = gpd.read_file(self.filename)
				#print(list(shp.columns))
				# Searching in this above list and selecting the name variable seems like a good idea.
				try:
					self.places = list(shp['NAME'])
				except:
					self.places = list(shp['ST_NAME'])
				## THIS IS VERY VERY BAD, NEEDS TO BE GENERALIZED BETTER.
				#[Need to modify the selector to allow multiple places to be selected.]
				places2 = [i for i in self.places if i is not None]
				places2.append("ALL")
				places2.sort()
				self.lbl3.config(text=self.filename.split('/')[-1])
				self.lbl3.grid(row = 27, column = 0)
				self.lbl4.grid(row = 28, column = 0)
				self.cmb1.config(values = places2)
				self.cmb1.grid(row = 28, column = 1)

class DataSelector(object):

	
	def __init__(self,parent):
		self.parent = parent
		window = tk.Toplevel(self.parent.root)

		window.grid_rowconfigure(0, weight=1)
		window.grid_columnconfigure(0, weight=1)

		xscrollbar = tk.Scrollbar(window, orient="horizontal")
		xscrollbar.grid(row=1, column=0, sticky=tk.E+tk.W)

		yscrollbar = tk.Scrollbar(window)
		yscrollbar.grid(row=0, column=1, sticky=tk.N+tk.S)

		canvas = tk.Canvas(window, bd=0,
	                xscrollcommand=xscrollbar.set,
	                yscrollcommand=yscrollbar.set)

		canvas.grid(row=0, column=0, sticky=tk.N+tk.S+tk.E+tk.W)

		xscrollbar.config(command=canvas.xview)
		yscrollbar.config(command=canvas.yview)
		frame = tk.Frame(canvas, width=1000,height=2000)
		canvas.create_window((0,0), window=frame, anchor='nw')

		self.var_time = tk.IntVar(frame)
		self.filename = self.parent.nb.tab(self.parent.nb.select(), "text")
		self.dataset = self.parent.file_handler.data[self.filename]
		tk.Label(frame, text = "Select data points by: ").grid(row = 0,column = 0)
		tk.Radiobutton(frame, variable = self.var_time, value = 0, text = "Year").grid(row = 0, column = 1)
		tk.Radiobutton(frame, variable = self.var_time, value = 1, text = "Month").grid(row = 0, column = 2)
		time_range = [pd.to_datetime(a).date() for a in list(self.dataset.variables['time'].values)]
		time_range.sort()
		tk.Label(frame, text = "Select filters:").grid(row = 625, column = 0)
		self.val_filt = tk.IntVar(frame)
		tk.Radiobutton(frame, variable = self.val_filt, value = 0, text = "No filters").grid(row = 626, column = 0)
		tk.Radiobutton(frame, variable = self.val_filt, value = 1, text = "Lat-Lon bounds").grid(row = 626, column = 1)
		tk.Radiobutton(frame, variable = self.val_filt, value = 2, text = "ShapeFile").grid(row = 626, column = 2)
		tk.Label(frame, text = "Select variables:" ).grid(row = 820,column = 0)
		self.var_var = dict()
		num = 0
		for x in list(self.dataset.data_vars.keys()):
			self.var_var[x] = tk.BooleanVar(frame)
			tk.Checkbutton(frame, text = x, variable = self.var_var[x]).grid(row = 821, column = num)
			num += 1
		self.chk = []
		self.var_rad = None
		self.year_start, self.year_end = None, None
		tk.Label(frame, text = "Statistics").grid(row = 900, column = 0)
		self.outField = tk.Text(frame, height = 4, width = 5)
		self.outField.grid(row = 900, column = 1, columnspan = 3, sticky = tk.W+tk.E+tk.N+tk.S, pady = 5, padx = 3, rowspan = 4)
		self.months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
		self.var_month = [tk.BooleanVar(frame, name = "all"+"_"+ mon) for mon in self.months]
		self.month_label = [tk.Checkbutton(frame, text = self.months[d], variable = self.var_month[d]) for d in range(len(self.months))]
		self.year_start = int(time_range[0].year)
		self.year_end = int(time_range[-1].year)
		self.var_year = [tk.BooleanVar(frame, name = str(d)+ "_all") for d in range(self.year_start,self.year_end+1)]
		self.year_labels = [tk.Checkbutton(frame, text = str(ind+self.year_start), variable = self.var_year[ind]) for ind in range(self.year_end-self.year_start+1)]
		self.var_rad = [tk.BooleanVar(frame) for ind in range(self.year_end-self.year_start+1)]
		self.chk = [tk.Checkbutton(frame, text = str(ind+self.year_start), variable =  self.var_rad[ind]) for ind in range(self.year_end-self.year_start+1)]
		self.chk2 = dict()
		for dra in range(self.year_start,self.year_end+1):
			self.chk2[str(dra)] = dict()
			for mon in self.months:
				self.chk2[str(dra)][mon] = [tk.BooleanVar(frame, name = str(dra)+"_"+mon)]
				self.chk2[str(dra)][mon].append(tk.Checkbutton(frame, variable =  self.chk2[str(dra)][mon][0]))
		lon_var,lat_var = self.parent.file_handler.getLatLon(self.dataset)
		lat_arr = list(self.dataset.variables[lat_var].values)
		self.lat_arr2 = [str(a) for a in lat_arr]
		lat_arr.sort()
		lon_arr = list(self.dataset.variables[lon_var].values)
		self.lon_arr2 = [str(a) for a in lon_arr]
		lon_arr.sort()
		self.lbl1 = tk.Label(frame, text = "Latitude Range:")
		self.spn_box1 = tk.Spinbox(frame, values = lat_arr)
		self.spn_box2 = tk.Spinbox(frame, values = lat_arr)
		self.lbl2 = tk.Label(frame, text = "Longitude Range:")
		self.spn_box3 = tk.Spinbox(frame, values = lon_arr)
		self.spn_box4 = tk.Spinbox(frame, values = lon_arr)
		self.filename = None
		self.lbl3 = tk.Label(frame)
		self.lbl4 = tk.Label(frame, text = "Select place:")
		self.plc_var = tk.StringVar(frame)
		self.cmb1 = ttk.Combobox(frame, textvariable = self.plc_var)
		self.places = None

		self.val_filt.trace("w", self.selectFilter)
		
		self.var_time.trace("w", self.selectGrid)
		self.var_time.set(0)

		b1 = tk.Button(frame, command = self.getStats, text = "Get statistics")
		b1.grid(row = 1000, column = 0)
		canvas.config(scrollregion = (0,0,2000,2000))

		for a in self.var_month:
			a.trace("w", self.select)
		for a in self.var_year:
			a.trace("w", self.select)

	def getStats(self):

		var_arr = [key for key,value in self.var_var.items() if value.get()]
		filt = self.val_filt.get()
		if(not self.var_time.get()):
			chk_status = [a.get() for a in self.var_rad]
			year_param = self.year_start
		else:
			chk_status = dict()
			for dra in range(self.year_start,self.year_end+1):
				chk_status[str(dra)] = dict()
				for mon in self.months:
					chk_status[str(dra)][mon] = self.chk2[str(dra)][mon][0].get()
			year_param = None
		if(self.val_filt.get() == 0):
			outdict = self.parent.file_handler.getStats(self.dataset, year_param, chk_status, var_arr)
		elif(self.val_filt.get() == 1):
			lat_r = [self.lat_arr2.index(self.spn_box1.get()),self.lat_arr2.index(self.spn_box2.get())]
			lon_r = [self.lon_arr2.index(self.spn_box3.get()),self.lon_arr2.index(self.spn_box4.get())]
			lat_r.sort()
			lon_r.sort()
			outdict = self.parent.file_handler.getStats(self.dataset, year_param, chk_status, var_arr, filt = "bounds", lat_range = slice(lat_r[0], lat_r[1]), lon_range = slice(lon_r[0], lon_r[1]))
		elif(self.val_filt.get() == 2):
			if(self.plc_var.get() == "ALL"):
				plac_ind = None
			else:
				plac_ind = self.places.index(self.plc_var.get())
			outdict = self.parent.file_handler.getStats(self.dataset, year_param, chk_status, var_arr, filt = "shapefile", filename = self.filename, place = plac_ind)
		self.outField.delete(1.0,tk.END)
		self.outField.insert(tk.INSERT, self.parent.file_handler.generateMessage(outdict))

	def select(self,event, b, c):
		year_mon = event.split('_')
		year = year_mon[0]
		mon = year_mon[1]
		if(year == "all"):
			for ind in range(self.year_start, self.year_end+1):
				self.chk2[str(ind)][mon][0].set(self.var_month[self.months.index(mon)].get())
		elif (mon == "all"):
			for mon in self.months:
				self.chk2[year][mon][0].set(self.var_year[int(year)-self.year_start].get())

	def selectFilter(self,event, b, c):
		if (self.val_filt.get() == 0):
			self.lbl1.grid_forget()
			self.spn_box1.grid_forget()
			self.spn_box2.grid_forget()
			self.lbl2.grid_forget()
			self.spn_box3.grid_forget()
			self.spn_box4.grid_forget()
			self.lbl3.grid_forget()
			self.lbl4.grid_forget()
			self.cmb1.grid_forget()
			self.filename = None

		elif (self.val_filt.get() == 1):
			self.lbl1.grid(row = 727, column = 0)
			self.spn_box1.grid(row = 727, column = 1)
			self.spn_box2.grid(row = 727, column = 2)
			self.lbl2.grid(row = 728, column = 0)
			self.spn_box3.grid(row = 728, column = 1)
			self.spn_box4.grid(row = 728, column = 2)
			self.lbl3.grid_forget()
			self.lbl4.grid_forget()
			self.cmb1.grid_forget()
			self.filename = None
		elif(self.val_filt.get() == 2):
			self.lbl1.grid_forget()
			self.spn_box1.grid_forget()
			self.spn_box2.grid_forget()
			self.lbl2.grid_forget()
			self.spn_box3.grid_forget()
			self.spn_box4.grid_forget()
			self.filename = askopenfilename(filetypes=[("SHAPEFILE", "*.shp")])
			if (self.filename == ""):
				self.filename = None
				self.val_filt.set(0)
			else:
				shp = gpd.read_file(self.filename)
				#print(list(shp.columns))
				# Searching in this above list and selecting the name variable seems like a good idea.
				try:
					self.places = list(shp['NAME'])
				except:
					self.places = list(shp['ST_NAME'])
				## THIS IS VERY VERY BAD, NEEDS TO BE GENERALIZED BETTER.
				#[Need to modify the selector to allow multiple places to be selected.]
				places2 = [i for i in self.places if i is not None]
				places2.append("ALL")
				places2.sort()
				self.lbl3.config(text=self.filename.split('/')[-1])
				self.lbl3.grid(row = 727, column = 0)
				self.lbl4.grid(row = 728, column = 0)
				self.cmb1.config(values = places2)
				self.cmb1.grid(row = 728, column = 1)
	
	def selectGrid(self,event, b, c):
		if(self.var_time.get() == 0):
			for i in self.month_label:
				i.grid_forget()
			for i in self.year_labels:
				i.grid_forget()
			for i in range(0,self.year_end-self.year_start+1):
				for m in range(12):
					self.chk2[str(i+self.year_start)][self.months[m]][1].grid_forget() 
			row_max = 10
			for ind in range(self.year_end-self.year_start+1):
				self.chk[ind].grid(row = 1+(ind%row_max), column = 1+ind//row_max)
		elif(self.var_time.get() == 1):
			for a in self.chk:
				a.grid_forget()
			for i in range(12):
				self.month_label[i].grid(row = 1, column = 1+i)
			for ind in range(0,self.year_end-self.year_start+1):
				self.year_labels[ind].grid(row = 2+ind, column = 0)
			for i in range(0,self.year_end-self.year_start+1):
				for m in range(12):
					self.chk2[str(i+self.year_start)][self.months[m]][1].grid(row = 2+i, column = m+1)


class FirstGUI(object):

	def __init__(self, parent_object, filenames):
		self.parent = parent_object
		self.filenames = filenames

	def getMultiSets(self):
			
		self.l1 = tk.Label(self.parent.root, text = "Tick the ones you want to combine:")
		self.l1.grid(row = 0, column  = 0,ipadx = 10, pady = 10, columnspan = 5, sticky = tk.W)
		
		self.file_chk_vars = dict()
		self.chk_btn_dict = dict()

		self.newName = tk.StringVar(self.parent.root)
		self.newName.set("newFile")
		
		i = 1
		for filename in self.filenames:
			self.file_chk_vars[filename] = tk.BooleanVar(self.parent.root)
			self.chk_btn_dict[filename] = tk.Checkbutton(self.parent.root, text = filename, variable = self.file_chk_vars[filename])
			self.chk_btn_dict[filename].grid(row = i, column = 0, columnspan = 5, ipadx = 20, sticky = tk.W, pady = 3)
			i += 1
		
		self.l2 = tk.Label(self.parent.root, text='Name for new set: ')
		self.l2.grid(row = i, column = 0, pady = 8, columnspan = 2, sticky = tk.W, padx = 10)
		
		
		self.text = tk.Entry(self.parent.root, textvariable = self.newName)
		self.text.grid(row = i, column = 2, pady = 8, columnspan = 3, sticky = tk.W)
		
		self.b1 = tk.Button(self.parent.root, text = 'Combine')
		self.b1.grid(row = i+1, column = 0, sticky = tk.W+tk.E)
		
		self.b2 = tk.Button(self.parent.root, text = 'Done')
		self.b2.grid(row = i+1, column = 4, sticky = tk.W+tk.E)

		self.b1.config(command = self.combine_files)
		self.b2.config(command = self.createGUI)
		
		self.parent.root.grid_columnconfigure(0, minsize=150)
		self.parent.root.grid_columnconfigure(1, minsize=30)
		self.parent.root.grid_columnconfigure(3, minsize=30)
		self.parent.root.grid_columnconfigure(4, minsize=150)
	
	def combine_files(self):
					
		indxs = [filename for filename in self.filenames if self.file_chk_vars[filename].get()]
		if(len(indxs) > 1):
			self.parent.file_handler.data,self.filenames = combineFiles(self.parent.file_handler.data, self.filenames, indxs, self.newName.get())
			self.cleanFirstGUI()
			self.getMultiSets()
	
	def createGUI(self):
		self.cleanFirstGUI()
		self.parent.createCoreGUI(self.filenames)	
	
	def cleanFirstGUI(self):
		
		self.l1.destroy()
		self.l2.destroy()
		self.b1.destroy()
		self.b2.destroy()
		self.text.destroy()
		for btn in self.chk_btn_dict.values():
			btn.destroy()

class MapPlots(object):
	def __init__(self,parent):
		self.parent = parent
		self.filename = self.parent.nb.tab(self.parent.nb.select(), "text")
		self.dataset = self.parent.file_handler.data[self.filename]
		self.lon_var, self.lat_var = self.parent.file_handler.getLatLon(self.dataset)
		self.window = tk.Toplevel(self.parent.root)
		self.var2 = tk.IntVar(self.window) # shape file toggle
		var_list = list(self.parent.file_handler.data[self.filename].data_vars.keys())
		self.time_range = [str(pd.to_datetime(a).date()) for a in list(self.parent.file_handler.data[self.filename].variables['time'].values)]
		self.b1 = tk.Button(self.window, text = 'Confirm')
		self.b1.grid(row = 90, column = 1)
		self.var3 = tk.StringVar(self.window) #shapefile location selector
		self.var3.set("ALL")
		self.filename = None
		self.plac_ind = None
		self.places = []
		self.combo1 = ttk.Combobox(self.window, textvariable = self.var3)
		self.la1 = tk.Label(self.window)
		self.la2 = tk.Label(self.window, text= "Select place:")
		self.var = tk.StringVar(self.window) # variable selector
		self.varn = tk.StringVar(self.window) # projection selector
		self.varSpin1= tk.StringVar(self.window) #time range1
		self.varSpin2 = tk.StringVar(self.window) # time range 2
		self.varSave = tk.BooleanVar(self.window) # save file checkbutton
		self.varShow = tk.BooleanVar(self.window) # show plot checkbutton
		self.varSaveName = tk.StringVar(self.window) # newfile name
		self.varFrameRate = tk.StringVar(self.window)
		self.var.set(var_list[0])
		self.varn.set("PlateCarree")
		self.varFrameRate.set("150")
		tk.Label(self.window, text = "Select type graph:").grid(row = 1, column = 0)
		self.varRadio = tk.IntVar(self.window)
		tk.Radiobutton(self.window, text = 'Map plot (fixed time)', variable = self.varRadio, value = 0).grid(row = 2, column = 0)
		tk.Radiobutton(self.window, text = 'Animated map', variable = self.varRadio, value = 1).grid(row = 3, column = 0)
		tk.Radiobutton(self.window, text = 'Vector plot (if available)', variable = self.varRadio, value = 2).grid(row = 4, column = 0)
		tk.Radiobutton(self.window, text = 'Animated vector plot', variable = self.varRadio, value = 3).grid(row = 5, column = 0)

		proj_list = ["PlateCarree","AlbersEqualArea","AzimuthalEquidistant","EquidistantConic","LambertConformal","LambertCylindrical","Mercator","Miller","Mollweide","Orthographic","Robinson","Sinusoidal","Stereographic","TransverseMercator","UTM","InterruptedGoodeHomolosine","RotatedPole","OSGB","EuroPP","Geostationary","NearsidePerspective","EckertI","EckertII","EckertIII","EckertIV","EckertV","EckertVI","EqualEarth","Gnomonic","LambertAzimuthalEqualArea","NorthPolarStereo","OSNI","SouthPolarStereo"]
		proj_list_reduced = ["PlateCarree","AlbersEqualArea","AzimuthalEquidistant","EquidistantConic","LambertCylindrical","Miller","Mollweide","Robinson","Sinusoidal","InterruptedGoodeHomolosine","RotatedPole","EckertI","EckertII","EckertIII","EckertIV","EckertV","EckertVI","EqualEarth","NorthPolarStereo","SouthPolarStereo"]
		self.l1 = tk.Label(self.window, text = "Select variable: ")
		self.l2 = tk.Label(self.window, text = "Select time: ")
		self.l3 = tk.Label(self.window, text = "Select projection: ")
		self.l4 = tk.Label(self.window, text = "Select time range: ")
		self.l5 = tk.Label(self.window, text = ".gif")
		self.l6 = tk.Label(self.window, text = "Frame rate")
		self.l7 = tk.Label(self.window, text = "microseconds")
		self.om1 = tk.OptionMenu(self.window, self.var, *var_list)
		self.sb1 = tk.Spinbox(self.window, values = self.time_range, textvariable = self.varSpin1)
		self.sb2 = tk.Spinbox(self.window, values = self.time_range, textvariable = self.varSpin2)
		self.cb1 = ttk.Combobox(self.window, textvariable = self.varn, values = proj_list)
		self.chb1 = tk.Checkbutton(self.window, text = "Use SHP file", variable = self.var2)
		self.chb2 = tk.Checkbutton(self.window, text = "Savefile as", variable = self.varSave)
		self.chb3 = tk.Checkbutton(self.window, text = "Display plot", variable = self.varShow)

		self.ent1 = tk.Entry(self.window, textvariable = self.varSaveName)
		self.ent2 = tk.Entry(self.window, textvariable = self.varFrameRate)
		
		self.varRadio.trace("w", self.plotSelect)
		self.varRadio.set(0)
		self.var2.trace("w", self.shapeSelect)

	def plotSelect(self,event, a, b):
		var_t = self.varRadio.get()
		if (var_t == 0):
			self.l1.grid(row = 10, column = 0)
			self.om1.grid(row = 10, column = 1)
			self.l2.grid(row = 12, column = 0)
			self.sb1.grid(row = 12, column = 1)
			self.sb2.grid_forget()
			self.l3.grid(row = 13, column = 0)
			self.l4.grid_forget()
			self.cb1.grid(row = 13, column = 1)
			self.chb1.grid(row = 14, column = 0)
			self.chb2.grid_forget()
			self.chb3.grid_forget()
			self.ent1.grid_forget()
			self.l5.grid_forget()
			self.l6.grid_forget()
			self.l7.grid_forget()
			self.ent2.grid_forget()
		elif (var_t == 1):
			self.l1.grid(row = 10, column = 0)
			self.om1.grid(row = 10, column = 1)
			self.l2.grid_forget()
			self.l4.grid(row = 12, column = 0)
			self.sb1.grid(row = 12, column = 1)
			self.sb2.grid(row = 12, column = 2)
			self.l3.grid(row = 13, column = 0)
			self.cb1.grid(row = 13, column = 1)
			self.chb1.grid(row = 14, column = 0)
			self.chb2.grid(row = 15, column = 0)
			self.ent1.grid(row = 15, column = 1)
			self.l5.grid(row = 15, column = 2)
			self.chb3.grid(row = 16, column = 0)
			self.varShow.set(1)
			self.varSaveName.set("default")
			self.l6.grid(row = 17, column = 0)
			self.ent2.grid(row = 17, column = 1)
			self.l7.grid(row = 17, column = 2)
			# More options wrt the animation can be added here.
		elif (var_t == 2):
			self.l1.grid_forget()
			self.om1.grid_forget()
			self.l2.grid(row = 12, column = 0)
			self.sb1.grid(row = 12, column = 1)
			self.sb2.grid_forget()
			self.l3.grid(row = 13, column = 0)
			self.cb1.config(values = proj_list_reduced)
			self.cb1.grid(row = 13, column = 1)
			self.l4.grid_forget()
			self.chb1.grid(row = 14, column = 0)
			self.chb2.grid_forget()
			self.chb3.grid_forget()
			self.ent1.grid_forget()
			self.l5.grid_forget()
			self.l6.grid_forget()
			self.l7.grid_forget()
			self.ent2.grid_forget()
			# add mods for color selection, maybe even make user-chosen projection style?
		elif(var_t == 3):
			self.l1.grid_forget()
			self.om1.grid_forget()
			self.l2.grid_forget()
			self.l3.grid_forget()
			self.cb1.grid_forget()
			self.l4.grid(row = 12, column = 0)
			self.sb1.grid(row = 12, column = 1)
			self.sb2.grid(row = 12, column = 2)
			self.chb1.grid(row = 14, column = 0)
			self.chb2.grid(row = 15, column = 0)
			self.ent1.grid(row = 15, column = 1)
			self.l5.grid(row = 15, column = 2)
			self.chb3.grid(row = 16, column = 0)
			self.l6.grid(row = 17, column = 0)
			self.ent2.grid(row = 17, column = 1)
			self.l7.grid(row = 17, column = 2)
			self.varShow.set(1)
			self.varSaveName.set('default')
			# More option wrt animation to be added here.
		self.b1.config(command = self.callPlotFunction)
					
	def callPlotFunction(self):
		plot_maps = PlotMaps()
		var_name = self.var.get()
		proj_string = self.varn.get()
		t1 = self.time_range.index(self.varSpin1.get())
		t2 = self.time_range.index(self.varSpin2.get())
		show = self.varShow.get()
		save = self.varSave.get()
		save_name = self.varSaveName.get()
		frameRate = int(self.varFrameRate.get())
		if(self.var2.get() == 1 and self.var3.get() != "ALL"):
			self.plac_ind = self.places.index(self.var3.get())
		elif(self.var3.get() == "ALL"):
			self.plac_ind = None
		self.org = self.varRadio.get()
		if (self.org == 0):
			xds, geometries = self.parent.file_handler.getShapeData(self.dataset, var_name, t1, self.filename, self.plac_ind)
			plot_maps.plotMapShape(proj_string, xds, self.lon_var, self.lat_var, geometries)
		elif (self.org == 1):
			plot_maps.animation(t2-t1, proj_string,show, save, save_name,self.lon_var,self.lat_var,frameRate, self.file_handler.animate_aux(self.dataset,var_name, t1, self.filename, self.plac_ind))
		elif (self.org == 2):
			xds1, geometries = self.parent.file_handler.getShapeData(self.dataset, 'u10', t1, self.filename, self.plac_ind)
			xds2, geometries = self.parent.file_handler.getShapeData(self.dataset, 'v10', t1, self.filename, self.plac_ind)
			lon_arr = np.sort(((np.array(self.parent.file_handler.data[self.filename].coords[self.lon_var]) + 180) % 360) -180)
			lat_arr = np.array(self.parent.file_handler.data[self.filename].coords[self.lat_var])
			u_arr = np.array(xds1)
			v_arr = np.array(xds2)
			velocity = np.sqrt(u_arr*u_arr+v_arr*v_arr)
			plot_maps.vectorMap(proj_string, lon_arr, lat_arr, u_arr, v_arr, velocity,self.varSpin1.get())
		elif (self.org == 3):
			getU,getV = self.parent.file_handler.animate_aux(self.dataset,'u10',t1,self.filename,self.plac_ind), self.parent.file_handler.animate_aux(self.dataset,'v10',t1,self.filename,self.plac_ind)
			xds1, geometries = getU(0)
			xds2, geometries = getV(0)
			lon_arr = np.sort(((np.array(self.dataset.coords[self.lon_var]) + 180) % 360) -180)
			lat_arr = np.array(self.dataset.coords[self.lat_var])
			u_arr = np.array(xds1)
			v_arr = np.array(xds2)
			velocity = np.sqrt(u_arr*u_arr+v_arr*v_arr)
			plot_maps.vectorAnim(t2-t1, proj_string,show, save, save_name, getU,getV, frameRate, lon_arr,lat_arr,u_arr, v_arr, velocity, self.time_range)

	def shapeSelect(self, event, b, c):
		if (self.var2.get() == 1 or self.org == 2):
			self.filename = askopenfilename(filetypes=[("SHAPEFILE", "*.shp")])
			if (self.filename == ""):
				self.filename = None
				self.var2.set(0)
			else:
				shp = gpd.read_file(self.filename)
				#print(list(shp.columns))
				# Searching in this above list and selecting the name variable seems like a good idea.
				try:
					self.places = list(shp['NAME'])
				except:
					self.places = list(shp['ST_NAME'])
				## THIS IS VERY VERY BAD, NEEDS TO BE GENERALIZED BETTER.
				#[Need to modify the selector to allow multiple places to be selected.]
				places2 = [i for i in self.places if i is not None]
				places2.append("ALL")
				self.la1.config(text=self.filename.split('/')[-1])
				self.la1.grid(row = 24, column = 0)
				places2.sort()
				self.la2.grid(row = 25, column = 0)
				self.combo1.config(values = places2)
				self.combo1.grid(row = 25, column = 1)
		elif(self.var2.get() == 0):
			self.filename = None
			self.plac_ind = None
			self.combo1.grid_forget()
			self.la1.grid_forget()
			self.la2.grid_forget()

class CSVSelector(object):
	def __init__(self,parent):
		self.parent = parent
		self.filename = self.parent.nb.tab(self.parent.nb.select(), "text")
		self.dataset = self.parent.file_handler.data[self.filename]
		self.lon_var, self.lat_var = self.parent.file_handler.getLatLon(self.dataset)
		self.window = tk.Toplevel(self.parent.root)
		self.var2 = tk.IntVar(self.window) # shape file toggle
		var_list = list(self.parent.file_handler.data[self.filename].data_vars.keys())
		self.time_range = [str(pd.to_datetime(a).date()) for a in list(self.parent.file_handler.data[self.filename].variables['time'].values)]
		self.b1 = tk.Button(self.window, text = 'Confirm')
		self.b1.grid(row = 90, column = 1)
		self.var3 = tk.StringVar(self.window) #shapefile location selector
		self.var3.set("ALL")
		self.filename = None
		self.plac_ind = None
		self.places = []
		self.combo1 = ttk.Combobox(self.window, textvariable = self.var3)
		self.la1 = tk.Label(self.window)
		self.la2 = tk.Label(self.window, text= "Select place:")
		self.var = tk.StringVar(self.window)
		self.var.set(var_list[0])
		self.varSpin1 = tk.StringVar(self.window)
		self.varSpin2 = tk.StringVar(self.window)
		self.varBnd = tk.IntVar(self.window)
		tk.Label(self.window, text = "Select variable: ").grid(row = 1, column = 0)
		tk.OptionMenu(self.window, self.var, *var_list).grid(row = 1, column = 1)
		tk.Label(self.window, text = "Select time range: ").grid(row = 2, column = 0)
		tk.Spinbox(self.window, values = self.time_range, textvariable = self.varSpin1).grid(row = 2, column = 1)
		tk.Spinbox(self.window, values = self.time_range, textvariable = self.varSpin2).grid(row = 2, column = 2)
		tk.Label(self.window, text = "Bounds?").grid(row = 3, column = 0)
		tk.Radiobutton(self.window, text = "Use bounds specified in previous self.window", variable = self.varBnd, value = 0).grid(row = 3, column = 1)
		tk.Radiobutton(self.window, text = "Apply no bounds", variable = self.varBnd, value = 1).grid(row = 3, column = 2)
		tk.Checkbutton(self.window, text = "Use SHP file", variable = self.var2).grid(row = 4, column = 0)

		self.b1.config(command = self.saveCSV)
		self.var2.trace("w", self.shapeSelect)
	
	def shapeSelect(self, event, b, c):
		if (self.var2.get() == 1 or self.org == 2):
			self.filename = askopenfilename(filetypes=[("SHAPEFILE", "*.shp")])
			if (self.filename == ""):
				self.filename = None
				self.var2.set(0)
			else:
				shp = gpd.read_file(self.filename)
				#print(list(shp.columns))
				# Searching in this above list and selecting the name variable seems like a good idea.
				try:
					self.places = list(shp['NAME'])
				except:
					self.places = list(shp['ST_NAME'])
				## THIS IS VERY VERY BAD, NEEDS TO BE GENERALIZED BETTER.
				#[Need to modify the selector to allow multiple places to be selected.]
				places2 = [i for i in self.places if i is not None]
				places2.append("ALL")
				self.la1.config(text=self.filename.split('/')[-1])
				self.la1.grid(row = 24, column = 0)
				places2.sort()
				self.la2.grid(row = 25, column = 0)
				self.combo1.config(values = places2)
				self.combo1.grid(row = 25, column = 1)
		elif(self.var2.get() == 0):
			self.filename = None
			self.plac_ind = None
			self.combo1.grid_forget()
			self.la1.grid_forget()
			self.la2.grid_forget()

	def saveCSV(self):
		var_name = self.var.get()
		lon_var,lat_var = self.parent.file_handler.getLatLon(self.dataset)
		lat_range = [str(a) for a in self.dataset.variables[lat_var].values]
		lon_range = [str(a) for a in self.dataset.variables[lon_var].values]
		t1 = self.time_range.index(self.varSpin1.get())
		t2 = self.time_range.index(self.varSpin2.get())
		time_t = [t1,t2]
		time_t.sort()
		t3 = slice(time_t[0], time_t[1]+1)
		if(self.varBnd.get() == 0):
			msgs,outVar = self.parent.getIndexes()
			lat_range = lat_range[lat_range.index(msgs[lat_var][1]):lat_range.index(msgs[lat_var][0])+1]
			lon_range = lon_range[lon_range.index(msgs[lon_var][0]):lon_range.index(msgs[lon_var][1])+1]
			data_arr = self.parent.file_handler.getData(self.dataset,msgs,outVar,variable = var_name)[1]
			if (self.filename is not None):
				lat_rn, lon_rn = self.dataset.coords[lat_var],self.dataset.coords[lon_var]
				out = self.parent.file_handler.applyShape(data_arr, lat_var, lon_var, self.filename, self.plac_ind, lat_r = lat_rn, lon_r = lon_rn)[0]
			else:
				out = data_arr
		elif(self.varBnd.get() == 1):
			if (self.filename is not None):
				out = [np.array(self.parent.file_handler.getShapeData(self.dataset, var_name, time_t[0], self.filename, self.plac_ind)[0])]
				for time_i in range(time_t[0], time_t[1]):
					out.append(self.parent.file_handler.getShapeData(self.dataset,var_name, time_i+1, self.filename, self.plac_ind)[0])
				#This segment takes a long long time to execute. Please keep that in mind. Hence, testing is also not thorough.
				out = np.array(out)
			else:
				out = self.dataset.data_vars[var_name][t3,:,:]
		if(self.varBnd.get() == 0 and self.filename is not None):
			resized_array = np.array(out.data)
		else:
			resized_array = np.array(out)
		text = asksaveasfilename(filetypes=[("Comma-separated Values", "*.csv")]).split('.')
		index = 0
		lon_range.insert(0,'lat/lon')
		for index in range(resized_array.shape[0]):
			temp_array = np.empty((resized_array[index].shape[0],resized_array[index].shape[1]+1))
			for i in range(resized_array[index].shape[0]):
				temp_array[i][0] = lat_range[i]
				temp_array[i][1:] = resized_array[index][i]
			name = text[0]+str(self.time_range[t1+index])+'.'+text[1]
			pd.DataFrame(temp_array).to_csv(name, header = lon_range, index = False, na_rep = "NaN")
		tk.Label(self.window, text = "Done").grid(row = 43, column = 1, columnspan = 2)

class ShapeData(object):
	def __init__(self,parent):
		self.parent = parent
		self.filename = self.parent.nb.tab(self.parent.nb.select(), "text")
		self.dataset = self.parent.file_handler.data[self.filename]
		self.lon_var, self.lat_var = self.parent.file_handler.getLatLon(self.dataset)
		self.window = tk.Toplevel(self.parent.root)
		self.var2 = tk.IntVar(self.window) # shape file toggle
		var_list = list(self.parent.file_handler.data[self.filename].data_vars.keys())
		self.time_range = [str(pd.to_datetime(a).date()) for a in list(self.parent.file_handler.data[self.filename].variables['time'].values)]
		self.b1 = tk.Button(self.window, text = 'Confirm')
		self.b1.grid(row = 90, column = 1)
		self.var3 = tk.StringVar(self.window) #shapefile location selector
		self.var3.set("ALL")
		self.filename = None
		self.plac_ind = None
		self.places = []
		self.combo1 = ttk.Combobox(self.window, textvariable = self.var3)
		self.la1 = tk.Label(self.window)
		self.la2 = tk.Label(self.window, text= "Select place:")
		
			#Retrieve Data, but limited by shape
		self.shapeSelect(None,None,None)
		self.b1.config(command = self.printShapeData)

		self.var2.trace("w", self.shapeSelect)


	def printShapeData(self):
		masked_data = self.parent.file_handler.getShapeData(self.dataset,None, None, self.filename, self.plac_ind)[0]
		msgs,outVar = self.parent.getIndexes()
		sel_message, output_message = self.parent.file_handler.getData(self.dataset,msgs,outVar, masked_data = masked_data)
		self.parent.printMessages(output_message,sel_message)
		self.window.destroy()

	def shapeSelect(self, event, b, c):
		if (self.var2.get() == 1 or self.org == 2):
			self.filename = askopenfilename(filetypes=[("SHAPEFILE", "*.shp")])
			if (self.filename == ""):
				self.filename = None
				self.var2.set(0)
			else:
				shp = gpd.read_file(self.filename)
				#print(list(shp.columns))
				# Searching in this above list and selecting the name variable seems like a good idea.
				try:
					self.places = list(shp['NAME'])
				except:
					self.places = list(shp['ST_NAME'])
				## THIS IS VERY VERY BAD, NEEDS TO BE GENERALIZED BETTER.
				#[Need to modify the selector to allow multiple places to be selected.]
				places2 = [i for i in self.places if i is not None]
				places2.append("ALL")
				self.la1.config(text=self.filename.split('/')[-1])
				self.la1.grid(row = 24, column = 0)
				places2.sort()
				self.la2.grid(row = 25, column = 0)
				self.combo1.config(values = places2)
				self.combo1.grid(row = 25, column = 1)
		elif(self.var2.get() == 0):
			self.filename = None
			self.plac_ind = None
			self.combo1.grid_forget()
			self.la1.grid_forget()
			self.la2.grid_forget()

class CDAPack(object):
	file_handler = None
	root = None
	nb = None
	chk_var_list1 = None
	chk_var_list2 = None
	chk_var_list3 = None
	spn_box_list = None
	selBox = None
	opBox = None

	def __init__(self):
		pass

	def main(self):
		
		# Creation of the main tkinter window and starting the tcl/tk interpreter and storing the object reference in the variable present in gl_vars.py.
		self.root = tk.Tk()

		# Sets the title for the window. Later can be replaced by the actual name of the software.
		self.root.title('Climate Data Analysis Pack 0.0.4')

		# This tkinter function creates a pop-up window through which the user can select multiple .nc files. filenames, contains the list of the names (with complete paths) stored in the form of strings, selected by the user.
		# If no file is selected, the program terminates.
		filenames = askopenfilenames(filetypes=[("NetCDF Files", "*.nc")])
		if (len(filenames) < 1):
			self.root.destroy()
			exit()

		# Creates a file_handler object which allows us to use various file-related functionalities.
		self.file_handler = FileHandler(filenames)
		

		# This function prompts the user to select files which whose data is part of the same series, allowing queries whose timelines range across different files.
		# Further, in the pop-up window, a button is created which, when pressed, will create the GUI.
		gui_class = FirstGUI(self,self.file_handler.filenames)
		gui_class.getMultiSets()
		#self.getMultiSets(self.file_handler.filenames)

		# This keeps the tkinter widgets active.
		self.root.mainloop()

		#Cleanup. Closing files before end of program.
		for dataset in list(self.file_handler.data.values()):
			dataset.close()

	def createCoreGUI(self,filenames):
		self.nb = ttk.Notebook(self.root)
		
		menu = tk.Menu(self.root)
		menu.add_command(label = "Plot on Map", command = self.plotWindow)
		menu.add_command(label = "Export", command = self.exportToCSV)
		
		submenu1 = tk.Menu(self.root)
		submenu1.add_command(label = "Calculator", command = self.dataSelector)
		submenu1.add_command(label = "Time Series", command = self.plotGenerator)
		menu.add_cascade(label = "Statistics", menu = submenu1)

		self.root.config(menu=menu)
		
		pages = self.addPages(filenames)
		self.fillPages(pages)
		
		for filename in self.chk_var_list1.keys():
			for dim in self.chk_var_list1[filename].keys():
				self.chk_var_list1[filename][dim].trace("w",self.trig)

	def addPages(self,filenames):
		pages = dict()
		for filename in filenames:
			pages[filename] = ttk.Frame(self.nb)
			self.nb.add(pages[filename], text = filename)
		self.nb.grid(row = 0, column = 0, columnspan=9, sticky = tk.E + tk.W, padx = 5)
		return pages

	def trig(self,event,b,c): 
		variable_name = event.split('$')
		dim = variable_name[2]
		filename = variable_name[1]
		row_num = int(variable_name[3])
		if (self.chk_var_list1[filename][dim].get() == 0):
			self.spn_box_list[filename][dim][1].grid_forget() 
		else:
			self.spn_box_list[filename][dim][1].grid(row = row_num, column = 2)
	
	def fillPages(self,pages):

		self.chk_var_list1 = dict()
		self.chk_var_list2 = dict()
		self.chk_var_list3 = dict()
		self.spn_box_list = dict()

		for filename in pages.keys():
			
			dimension_list = list(self.file_handler.data[filename].coords.keys())
			variable_list = list(self.file_handler.data[filename].data_vars.keys())
			
			dim_count = len(dimension_list)

			self.chk_var_list1[filename] = dict()
			self.chk_var_list2[filename] = dict()
			self.spn_box_list[filename] = dict()
			
			row_num = 0
			self.chk_var_list3[filename] = tk.IntVar(pages[filename])
			tk.Checkbutton(pages[filename], text = "Use SHAPEFILE", variable = self.chk_var_list3[filename]).grid(row = row_num, column = 10)
			
			for dim in dimension_list:	
				self.chk_var_list1[filename][dim] = self.createSelRow(pages[filename], dim, row_num, filename, row_num+dim_count)
				self.spn_box_list[filename][dim] = self.createSelBox(pages[filename],dim, row_num+dim_count, list(self.file_handler.data[filename][dim].values))
				row_num += 1
			
			row_num+=dim_count
			
			tk.Label(pages[filename], text="Choose output variables:").grid(row = row_num+1, column = 0)
			
			col_num = 1
			for data_var in variable_list:
				self.chk_var_list2[filename][data_var] = self.createCheckBox(pages[filename],data_var, row_num+1, col_num)
				col_num += 1
		
		tk.Label(self.root, text="Selection:").grid(column = 1, row = 90, sticky = tk.W, padx = 5, pady = 5)
		self.selBox = tk.Text(self.root, height = 4, width = 5)
		self.selBox.grid(row = 90, column = 2, columnspan = 3, sticky = tk.W+tk.E+tk.N+tk.S, pady = 5, padx = 3, rowspan = 4)
		
		tk.Label(self.root, text="Output:").grid(column = 5, row = 90, sticky = tk.W, padx = 5, pady = 5)
		self.opBox = tk.Text(self.root, height = 4, width = 5)
		self.opBox.grid(row = 90, column = 6, columnspan = 3, sticky = tk.W+tk.E+tk.N+tk.S, pady = 5, padx = 3, rowspan = 4)
		
		tk.Button(self.root, text = 'Retrieve data', command = self.retrieveData).grid(row = 100, column = 1, sticky = tk.E + tk.W, pady = 5)
		tk.Button(self.root, text = 'Close', command = self.root.destroy).grid(row = 100, column = 8, sticky = tk.E+ tk.W, padx = 5, pady = 5)
		
		self.root.grid_columnconfigure(0, minsize=30)
		self.root.grid_columnconfigure(1, minsize=150)
		self.root.grid_columnconfigure(2, minsize=30)
		self.root.grid_columnconfigure(3, minsize=150)
		self.root.grid_columnconfigure(4, minsize=30)
		self.root.grid_columnconfigure(5, minsize=150)
		self.root.grid_columnconfigure(6, minsize=30)
		self.root.grid_columnconfigure(7, minsize=30)
		self.root.grid_columnconfigure(8, minsize=150)
		self.root.grid_rowconfigure(91, minsize=20)
		self.root.grid_rowconfigure(92, minsize=20)
		self.root.grid_rowconfigure(93, minsize=20)

	def createSelRow(self, page, dim_name, row_num, filename, space):
		tk.Label(page, text = dim_name).grid(row = row_num, column = 0)
		var_radio = tk.IntVar(page, name = "var$"+filename+ "$" + dim_name + '$' + str(space))
		tk.Radiobutton(page, text = 'Single'           , variable = var_radio, value = 0).grid(row = row_num, column = 1)
		tk.Radiobutton(page, text = 'Range (Inclusive)', variable = var_radio, value = 1).grid(row = row_num, column = 2)
		return var_radio

	def createSelBox(self, page, dim_name, row_num, value_list):
		value_list.sort()
		tk.Label(page, text = dim_name).grid(row = row_num, column = 0)
		spn_box_list = [tk.Spinbox(page, values = value_list), tk.Spinbox(page, values = value_list)]
		spn_box_list[0].grid(row = row_num, column = 1)
		return spn_box_list

	def createCheckBox(self,page, data_var, row_num, col_num):
		data_var_var = tk.BooleanVar(page)
		tk.Checkbutton(page, text = data_var, variable = data_var_var).grid(row = row_num, column = col_num)
		return data_var_var

	def getIndexes(self):	
		filename = self.nb.tab(self.nb.select(), "text")
		messages = dict()
		outVar = dict()
		
		for dim in self.chk_var_list1[filename].keys():
			messages[dim] = [self.spn_box_list[filename][dim][0].get()]
			if(self.chk_var_list1[filename][dim].get()):
				messages[dim].append(self.spn_box_list[filename][dim][1].get())
			else:
				messages[dim].append(None)
		
		for data_var in self.chk_var_list2[filename].keys():
			outVar[data_var] = self.chk_var_list2[filename][data_var].get()
		return messages,outVar

	def printMessages(self,o_message, s_message):
		self.selBox.delete(1.0, tk.END)
		self.selBox.insert(tk.INSERT, s_message)
		self.opBox.delete(1.0, tk.END)
		self.opBox.insert(tk.INSERT, o_message)

	def plotWindow(self):
		plot = MapPlots(self)

	def exportToCSV(self):
		csv = CSVSelector(self)

	def retrieveData(self):
		filename = self.nb.tab(self.nb.select(), "text")
		if (self.chk_var_list3[filename].get() == 1):
			shdata = ShapeData(self)
		else:
			msgs,outVar = self.getIndexes()
			sel_message, output_message = self.file_handler.getData(self.file_handler.data[filename],msgs,outVar)
			self.printMessages(output_message,sel_message)

	def dataSelector(self):
		data_sel = DataSelector(self)

	def plotGenerator(self):
		plot = PlotGenerator(self)