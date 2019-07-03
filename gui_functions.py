# gui_functions.py #

import gl_vars
import file_functions as ffunc
import plot_functions as pfunc

import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename

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
# Create a ffunc. function to read shapefile and get locations.

def getMultiSets(filenames):
	l1 = tk.Label(gl_vars.root, text = "Tick the ones you want to combine:")
	l1.grid(row = 0, column  = 0,ipadx = 10, pady = 10, columnspan = 5, sticky = tk.W)
	chk_vars = dict()
	chk_arr = dict()

	var = tk.StringVar(gl_vars.root)
	var.set("newFile")
	i = 1
	for a in filenames:
		chk_vars[a] = tk.IntVar(gl_vars.root)
		chk_arr[a] = tk.Checkbutton(gl_vars.root, text = a, variable = chk_vars[a])
		chk_arr[a].grid(row = i, column = 0, columnspan = 5, ipadx = 20, sticky = tk.W, pady = 3)
		i+=1
	l2 = tk.Label(gl_vars.root, text='Name for new set: ')
	l2.grid(row = i, column = 0, pady = 8, columnspan = 2, sticky = tk.W, padx = 10)
	filenames2 = filenames
	text = tk.Entry(gl_vars.root, textvariable = var)
	text.grid(row = i, column = 2, pady = 8, columnspan = 3, sticky = tk.W)
	
	b1 = tk.Button(gl_vars.root, text = 'Combine')
	b2 = tk.Button(gl_vars.root, text = 'More (Refresh list)')
	b3 = tk.Button(gl_vars.root, text = 'Done')

	def combine_files():
		nonlocal filenames2
		indxs = [a for a in filenames if chk_vars[a].get() == 1]
		gl_vars.data,filenames2 = ffunc.combineFiles(gl_vars.data, filenames, indxs, var.get())


	def getMore():
		nonlocal l1, l2, b3, b2, b1, text, chk_arr
		l2.destroy()
		l1.destroy()
		b1.destroy()
		b2.destroy()
		b3.destroy()
		text.destroy()
		for a in chk_arr.values():
			a.destroy()
		getMultiSets(filenames2)


	def createGUI():
		nonlocal l1, l2, b2, b3, b1, text, chk_arr
		l2.destroy()
		l1.destroy()
		b1.destroy()
		b2.destroy()
		b3.destroy()
		text.destroy()
		for a in chk_arr.values():
			a.destroy()
		gl_vars.nb = ttk.Notebook(gl_vars.root)
		menu = tk.Menu(gl_vars.root)
		submenu1 = tk.Menu(gl_vars.root)
		submenu1.add_command(label = "Calculator", command = dataSelector)
		submenu1.add_command(label = "Time Series", command = plotGenerator)
		submenu1.add_command(label = "Other plots")
		menu.add_command(label = "Plot on Map", command = plotWindow)
		menu.add_command(label = "Export", command = exportToCSV)
		menu.add_cascade(label = "Statistics", menu = submenu1)

		gl_vars.root.config(menu=menu)
		addPages(filenames2)
		fillPages()
		for i in gl_vars.chk_var_list1.keys():
			for j in gl_vars.chk_var_list1[i].keys():
				gl_vars.chk_var_list1[i][j].trace("w",trig)

	b1.config(command = combine_files)
	b2.config(command = getMore)
	b3.config(command = createGUI)
	b1.grid(row = i+1, column = 0, sticky = tk.W+tk.E)
	b2.grid(row = i+1, column = 2)
	b3.grid(row = i+1, column = 4, sticky = tk.W+tk.E)
	gl_vars.root.grid_columnconfigure(1, minsize=30)
	gl_vars.root.grid_columnconfigure(3, minsize=30)
	gl_vars.root.grid_columnconfigure(0, minsize=150)
	gl_vars.root.grid_columnconfigure(4, minsize=150)

def addPages(filenames):
	gl_vars.pages = dict()
	for i in filenames:
		gl_vars.pages[i] = ttk.Frame(gl_vars.nb)
		gl_vars.nb.add(gl_vars.pages[i], text = i)
	gl_vars.nb.grid(row = 0, column = 0, columnspan=9, sticky = tk.E + tk.W, padx = 5)

def trig(event,b,c):
	dats = event.split('$')		
	n1 = dats[2]
	i = dats[1]
	row_num = int(dats[3])
	if (gl_vars.chk_var_list1[i][n1].get() == 0):
		gl_vars.spn_box_list[i][n1][1].grid_forget() 
	else:
		gl_vars.spn_box_list[i][n1][1].grid(row = row_num, column = 2)
	
def fillPages():
	xr_dataSet = gl_vars.data
	no_of_pages = len(gl_vars.pages)
	gl_vars.chk_var_list1 = dict()
	gl_vars.chk_var_list2 = dict()
	gl_vars.chk_var_list3 = dict()
	gl_vars.spn_box_list = dict()
	for i in gl_vars.pages.keys():
		dimension_list = list(xr_dataSet[i].coords.keys())
		variable_list = list(xr_dataSet[i].data_vars.keys())
		gl_vars.chk_var_list1[i] = dict()
		gl_vars.chk_var_list2[i] = dict()
		gl_vars.spn_box_list[i] = dict()
		n1 = 0
		gl_vars.chk_var_list3[i] = tk.IntVar(gl_vars.pages[i])
		tk.Checkbutton(gl_vars.pages[i], text = "Use SHAPEFILE", variable = gl_vars.chk_var_list3[i]).grid(row = n1, column = 10)
		for j in dimension_list:	
			createSelRow(j, n1, i)
			createSelBox(j, n1, i, list(xr_dataSet[i][j].values))
			n1 += 1
		n1+=5
		n2 = 1
		tk.Label(gl_vars.pages[i], text="Choose output variables:").grid(row = n1+1, column = 0)
		for k in variable_list:
			createCheckBox(k, i, n1+1, n2)
			n2 += 1
	tk.Label(gl_vars.root, text="Selection:").grid(column = 1, row = 90, sticky = tk.W, padx = 5, pady = 5)
	gl_vars.selBox = tk.Text(gl_vars.root, height = 4, width = 5)
	gl_vars.selBox.grid(row = 90, column = 2, columnspan = 3, sticky = tk.W+tk.E+tk.N+tk.S, pady = 5, padx = 3, rowspan = 4)
	tk.Label(gl_vars.root, text="Output:").grid(column = 5, row = 90, sticky = tk.W, padx = 5, pady = 5)
	gl_vars.opBox = tk.Text(gl_vars.root, height = 4, width = 5)
	gl_vars.opBox.grid(row = 90, column = 6, columnspan = 3, sticky = tk.W+tk.E+tk.N+tk.S, pady = 5, padx = 3, rowspan = 4)
	tk.Button(gl_vars.root, text = 'Retrieve data', command = retrieveData).grid(row = 100, column = 1, sticky = tk.E + tk.W, pady = 5)
	tk.Button(gl_vars.root, text = 'Close', command = gl_vars.root.destroy).grid(row = 100, column = 8, sticky = tk.E+ tk.W, padx = 5, pady = 5)
	gl_vars.root.grid_columnconfigure(0, minsize=30)
	gl_vars.root.grid_columnconfigure(1, minsize=150)
	gl_vars.root.grid_columnconfigure(2, minsize=30)
	gl_vars.root.grid_columnconfigure(3, minsize=150)
	gl_vars.root.grid_columnconfigure(4, minsize=30)
	gl_vars.root.grid_columnconfigure(5, minsize=150)
	gl_vars.root.grid_columnconfigure(6, minsize=30)
	gl_vars.root.grid_columnconfigure(7, minsize=30)
	gl_vars.root.grid_columnconfigure(8, minsize=150)
	#gl_vars.root.grid_rowconfigure(90, minsize=10)
	gl_vars.root.grid_rowconfigure(91, minsize=20)
	gl_vars.root.grid_rowconfigure(92, minsize=20)
	gl_vars.root.grid_rowconfigure(93, minsize=20)

def createSelRow(name, num, ind):
	tk.Label(gl_vars.pages[ind], text = name).grid(row = num, column = 0)
	gl_vars.chk_var_list1[ind][name] = tk.IntVar(gl_vars.pages[ind], name = "var$"+ind+ "$" + name + '$' + str(num+5))
	r1 = tk.Radiobutton(gl_vars.pages[ind], text = 'Single', variable = gl_vars.chk_var_list1[ind][name], value = 0)
	r1.grid(row = num, column = 1)
	r2 = tk.Radiobutton(gl_vars.pages[ind], text = 'Range (Inclusive)', variable = gl_vars.chk_var_list1[ind][name], value = 1)
	r2.grid(row = num, column = 2)

def createSelBox(name, num, ind, value_list):
	value_list.sort()
	tk.Label(gl_vars.pages[ind], text = name).grid(row = num+5, column = 0)
	gl_vars.spn_box_list[ind][name] = [tk.Spinbox(gl_vars.pages[ind]), tk.Spinbox(gl_vars.pages[ind])]
	gl_vars.spn_box_list[ind][name][0].configure(values=value_list)
	gl_vars.spn_box_list[ind][name][0].grid(row = num+5, column = 1)
	gl_vars.spn_box_list[ind][name][1].configure(values=value_list)

def createCheckBox(data_var, ind, num, num2):
	gl_vars.chk_var_list2[ind][data_var] = tk.BooleanVar(gl_vars.pages[ind], name = "var$"+data_var+"$"+ind+"$"+str(num2-1))
	tk.Checkbutton(gl_vars.pages[ind], text = data_var, variable = gl_vars.chk_var_list2[ind][data_var]).grid(row = num, column = num2)

def getIndexes():
	i = gl_vars.nb.tab(gl_vars.nb.select(), "text")
	rangeVar = dict()
	for a in gl_vars.chk_var_list1[i].keys():
		rangeVar[a] = gl_vars.chk_var_list1[i][a].get()
	messages = dict()
	dimension_list = list(gl_vars.data[i].coords.keys())
	for x in dimension_list:
		messages[x] = [gl_vars.spn_box_list[i][x][0].get()]
		if(rangeVar[x]):
			messages[x].append(gl_vars.spn_box_list[i][x][1].get())
		else:
			messages[x].append(None)
	outVar = dict()
	for a in gl_vars.chk_var_list2[i].keys():
		outVar[a] = gl_vars.chk_var_list2[i][a].get()
	return messages,outVar


def printMessages(o_message, s_message):
	gl_vars.selBox.delete(1.0,tk.END)
	gl_vars.selBox.insert(tk.INSERT, s_message)
	gl_vars.opBox.delete(1.0,tk.END)
	gl_vars.opBox.insert(tk.INSERT, o_message)

def openWindow(org):
	i = gl_vars.nb.tab(gl_vars.nb.select(), "text")
	dataset = gl_vars.data[i]
	lon_var, lat_var = ffunc.getLatLon(dataset)
	window = tk.Toplevel(gl_vars.root)
	var2 = tk.IntVar(window) # shape file toggle
	var_list = list(gl_vars.data[i].data_vars.keys())
	time_range = [str(pd.to_datetime(a).date()) for a in list(gl_vars.data[i].variables['time'].values)]
	b1 = tk.Button(window, text = 'Confirm')
	b1.grid(row = 90, column = 1)
	var3 = tk.StringVar(window) #shapefile location selector
	var3.set("ALL")
	filename = None
	plac_ind = None
	places = []
	combo1 = ttk.Combobox(window, textvariable = var3)
	la1 = tk.Label(window)
	la2 = tk.Label(window, text= "Select place:")
	def shapeSelect(event, b, c):
		nonlocal places, filename, var2
		if (var2.get() == 1 or org == 2):
			filename = askopenfilename(filetypes=[("SHAPEFILE", "*.shp")])
			if (filename == ""):
				filename = None
				var2.set(0)
			else:
				shp = gpd.read_file(filename)
				#print(list(shp.columns))
				# Searching in this above list and selecting the name variable seems like a good idea.
				try:
					places = list(shp['NAME'])
				except:
					places = list(shp['ST_NAME'])
				## THIS IS VERY VERY BAD, NEEDS TO BE GENERALIZED BETTER.
				#[Need to modify the selector to allow multiple places to be selected.]
				places2 = [i for i in places if i is not None]
				places2.append("ALL")
				la1.config(text=filename.split('/')[-1])
				la1.grid(row = 24, column = 0)
				places2.sort()
				la2.grid(row = 25, column = 0)
				combo1.config(values = places2)
				combo1.grid(row = 25, column = 1)
		elif(var2.get() == 0):
			filename = None
			plac_ind = None

			combo1.grid_forget()
			la1.grid_forget()
			la2.grid_forget()
	output = None
	if (org == 0):
		#Map plot
		var = tk.StringVar(window) # variable selector
		varn = tk.StringVar(window) # projection selector
		varSpin1= tk.StringVar(window) #time range1
		varSpin2 = tk.StringVar(window) # time range 2
		varSave = tk.BooleanVar(window) # save file checkbutton
		varShow = tk.BooleanVar(window) # show plot checkbutton
		varSaveName = tk.StringVar(window) # newfile name
		var.set(var_list[0])
		varn.set("PlateCarree")
		tk.Label(window, text = "Select type graph:").grid(row = 1, column = 0)
		varRadio = tk.IntVar(window)
		tk.Radiobutton(window, text = 'Map plot (fixed time)', variable = varRadio, value = 0).grid(row = 2, column = 0)
		tk.Radiobutton(window, text = 'Animated map', variable = varRadio, value = 1).grid(row = 3, column = 0)
		tk.Radiobutton(window, text = 'Vector plot (if available)', variable = varRadio, value = 2).grid(row = 4, column = 0)
		tk.Radiobutton(window, text = 'Animated vector plot', variable = varRadio, value = 3).grid(row = 5, column = 0)

		proj_list = ["PlateCarree","AlbersEqualArea","AzimuthalEquidistant","EquidistantConic","LambertConformal","LambertCylindrical","Mercator","Miller","Mollweide","Orthographic","Robinson","Sinusoidal","Stereographic","TransverseMercator","UTM","InterruptedGoodeHomolosine","RotatedPole","OSGB","EuroPP","Geostationary","NearsidePerspective","EckertI","EckertII","EckertIII","EckertIV","EckertV","EckertVI","EqualEarth","Gnomonic","LambertAzimuthalEqualArea","NorthPolarStereo","OSNI","SouthPolarStereo"]
		proj_list_reduced = ["PlateCarree","AlbersEqualArea","AzimuthalEquidistant","EquidistantConic","LambertCylindrical","Miller","Mollweide","Robinson","Sinusoidal","InterruptedGoodeHomolosine","RotatedPole","EckertI","EckertII","EckertIII","EckertIV","EckertV","EckertVI","EqualEarth","NorthPolarStereo","SouthPolarStereo"]
		l1 =tk.Label(window, text = "Select variable: ")
		l2 = tk.Label(window, text = "Select time: ")
		l3 = tk.Label(window, text = "Select projection: ")
		l4 = tk.Label(window, text = "Select time range: ")
		l5 = tk.Label(window, text = ".gif")
		om1 = tk.OptionMenu(window, var, *var_list)
		sb1 = tk.Spinbox(window, values = time_range, textvariable = varSpin1)
		sb2 = tk.Spinbox(window, values = time_range, textvariable = varSpin2)
		cb1 = ttk.Combobox(window, textvariable = varn, values = proj_list)
		chb1 = tk.Checkbutton(window, text = "Use SHP file", variable = var2)
		chb2 = tk.Checkbutton(window, text = "Savefile as", variable = varSave)
		chb3 = tk.Checkbutton(window, text = "Display plot", variable = varShow)
		ent1 = tk.Entry(window, textvariable = varSaveName)
		def plotSelect(event, a, b):
			nonlocal l1, l2, l3, l4, om1, sb1, sb2, cb1, chb1
			var_t = varRadio.get()
			if (var_t == 0):
				l1.grid(row = 10, column = 0)
				om1.grid(row = 10, column = 1)
				l2.grid(row = 12, column = 0)
				sb1.grid(row = 12, column = 1)
				sb2.grid_forget()
				l3.grid(row = 13, column = 0)
				l4.grid_forget()
				cb1.grid(row = 13, column = 1)
				chb1.grid(row = 14, column = 0)
				chb2.grid_forget()
				chb3.grid_forget()
				ent1.grid_forget()
				l5.grid_forget()
			elif (var_t == 1):
				l1.grid(row = 10, column = 0)
				om1.grid(row = 10, column = 1)
				l2.grid_forget()
				l4.grid(row = 12, column = 0)
				sb1.grid(row = 12, column = 1)
				sb2.grid(row = 12, column = 2)
				l3.grid(row = 13, column = 0)
				cb1.grid(row = 13, column = 1)
				chb1.grid(row = 14, column = 0)
				chb2.grid(row = 15, column = 0)
				ent1.grid(row = 15, column = 1)
				l5.grid(row = 15, column = 2)
				chb3.grid(row = 16, column = 0)
				varShow.set(1)
				varSaveName.set("default")
				# More options wrt the animation can be added here.
			elif (var_t == 2):
				l1.grid_forget()
				om1.grid_forget()
				l2.grid(row = 12, column = 0)
				sb1.grid(row = 12, column = 1)
				sb2.grid_forget()
				l3.grid(row = 13, column = 0)
				cb1.config(values = proj_list_reduced)
				cb1.grid(row = 13, column = 1)
				l4.grid_forget()
				chb1.grid(row = 14, column = 0)
				chb2.grid_forget()
				chb3.grid_forget()
				ent1.grid_forget()
				l5.grid_forget()
				# add mods for color selection, maybe even make user-chosen projection style?
			elif(var_t == 3):
				l1.grid_forget()
				om1.grid_forget()
				l2.grid_forget()
				l3.grid_forget()
				cb1.grid_forget()
				l4.grid(row = 12, column = 0)
				sb1.grid(row = 12, column = 1)
				sb2.grid(row = 12, column = 2)
				chb1.grid(row = 14, column = 0)
				chb2.grid(row = 15, column = 0)
				ent1.grid(row = 15, column = 1)
				l5.grid(row = 15, column = 2)
				chb3.grid(row = 16, column = 0)
				varShow.set(1)
				varSaveName.set('default')
				# More option wrt animation to be added here.
			b1.config(command = callPlotFunction)
		

		def callPlotFunction():
			nonlocal plac_ind
			var_name = var.get()
			proj_string = varn.get()
			t1 = time_range.index(varSpin1.get())
			t2 = time_range.index(varSpin2.get())
			show = varShow.get()
			save = varSave.get()
			save_name = varSaveName.get()
			if(var2.get() == 1 and var3.get() != "ALL"):
				plac_ind = places.index(var3.get())
			elif(var3.get() == "ALL"):
				plac_ind = None
			org = varRadio.get()
			if (org == 0):
				xds, geometries = ffunc.getShapeData(dataset, var_name, t1, filename, plac_ind)
				pfunc.plotMapShape(proj_string, xds, lon_var, lat_var, geometries)
			elif (org == 1):
				pfunc.animation(t2-t1, proj_string,show, save, save_name,lon_var,lat_var, ffunc.animate_aux(dataset,var_name, t1, filename, plac_ind))
			elif (org == 2):
				xds1, geometries = ffunc.getShapeData(dataset, 'u10', t1, filename, plac_ind)
				xds2, geometries = ffunc.getShapeData(dataset, 'v10', t1, filename, plac_ind)
				lon_arr = np.sort(((np.array(gl_vars.data[i].coords[lon_var]) + 180) % 360) -180)
				lat_arr = np.array(gl_vars.data[i].coords[lat_var])
				u_arr = np.array(xds1)
				v_arr = np.array(xds2)
				velocity = np.sqrt(u_arr*u_arr+v_arr*v_arr)
				pfunc.vectorMap(proj_string, lon_arr, lat_arr, u_arr, v_arr, velocity)
			elif (org == 3):
				getU,getV = ffunc.animate_aux(dataset,'u10',t1,filename,plac_ind), ffunc.animate_aux(dataset,'v10',t1,filename,plac_ind)
				xds1, geometries = getU(0)
				xds2, geometries = getV(0)
				lon_arr = np.sort(((np.array(dataset.coords[lon_var]) + 180) % 360) -180)
				lat_arr = np.array(dataset.coords[lat_var])
				u_arr = np.array(xds1)
				v_arr = np.array(xds2)
				velocity = np.sqrt(u_arr*u_arr+v_arr*v_arr)
				pfunc.vectorAnim(t2-t1, proj_string,show, save, save_name, getU,getV, lon_arr,lat_arr,u_arr, v_arr, velocity, time_range)
		
		varRadio.trace("w", plotSelect)
		varRadio.set(0)
	
	elif (org == 1):
		#CSV selector
		var = tk.StringVar(window)
		var.set(var_list[0])
		varSpin1 = tk.StringVar(window)
		varSpin2 = tk.StringVar(window)
		varBnd = tk.IntVar(window)
		tk.Label(window, text = "Select variable: ").grid(row = 1, column = 0)
		tk.OptionMenu(window, var, *var_list).grid(row = 1, column = 1)
		tk.Label(window, text = "Select time range: ").grid(row = 2, column = 0)
		tk.Spinbox(window, values = time_range, textvariable = varSpin1).grid(row = 2, column = 1)
		tk.Spinbox(window, values = time_range, textvariable = varSpin2).grid(row = 2, column = 2)
		tk.Label(window, text = "Bounds?").grid(row = 3, column = 0)
		tk.Radiobutton(window, text = "Use bounds specified in previous window", variable = varBnd, value = 0).grid(row = 3, column = 1)
		tk.Radiobutton(window, text = "Apply no bounds", variable = varBnd, value = 1).grid(row = 3, column = 2)
		tk.Checkbutton(window, text = "Use SHP file", variable = var2).grid(row = 4, column = 0)

		def saveCSV():
			var_name = var.get()
			t1 = time_range.index(varSpin1.get())
			t2 = time_range.index(varSpin2.get())
			time_t = [t1,t2]
			time_t.sort()
			t3 = slice(time_t[0], time_t[1]+1)
			if(varBnd.get() == 0):
				msgs,outVar = getIndexes()
				data_arr = ffunc.getData(dataset,msgs,outVar,variable = var_name)[1]
				if (filename is not None):
					lon_var,lat_var = ffunc.getLatLon(dataset)
					lat_rn, lon_rn = dataset.coords[lat_var],dataset.coords[lon_var]
					out = ffunc.applyShape(data_arr, lat_var, lon_var, filename, plac_ind, lat_r = lat_rn, lon_r = lon_rn)[0]
				else:
					out = data_arr
			elif(varBnd.get() == 1):
				if (filename is not None):
					out = [np.array(ffunc.getShapeData(dataset, var_name, time_t[0], filename, plac_ind)[0])]
					for time_i in range(time_t[0], time_t[1]):
						out.append(ffunc.getShapeData(dataset,var_name, time_i+1, filename, plac_ind)[0]) 
					#This segment takes a long long time to execute. Please keep that in mind. Hence, testing is also not thorough.
					out = np.array(out)
				else:
					out = dataset.data_vars[var_name][t3,:,:]
			if(varBnd.get() == 0 and filename is not None):
				resized_array = np.array(out.data)
			else:
				resized_array = np.resize(out, [out.shape[0]* out.shape[1], out.shape[2]])
			pd.DataFrame(resized_array).to_csv(asksaveasfilename(filetypes=[("Comma-separated Values", "*.csv")]), header = None, index = None, na_rep = "NaN")
			tk.Label(window, text = "Done").grid(row = 43, column = 1, columnspan = 2)
		b1.config(command = saveCSV)
	
	elif (org == 2):
		#Retrieve Data, but limited by shape
		shapeSelect(None,None,None)
		def printShapeData():
			nonlocal window
			masked_data = ffunc.getShapeData(dataset,None, None, filename, plac_ind)[0]
			msgs,outVar = getIndexes()
			sel_message, output_message = ffunc.getData(dataset,msgs,outVar, masked_data = masked_data)
			printMessages(output_message,sel_message)
			window.destroy()
		b1.config(command = printShapeData)

	var2.trace("w", shapeSelect)


def plotWindow():
	openWindow(0)

def exportToCSV():
	openWindow(1)

def retrieveData():
	i = gl_vars.nb.tab(gl_vars.nb.select(), "text")
	if (gl_vars.chk_var_list3[i].get() == 1):
		openWindow(2)
	else:
		msgs,outVar = getIndexes()
		dataset = gl_vars.data[i]
		sel_message, output_message = ffunc.getData(dataset, msgs,outVar)
		printMessages(output_message,sel_message)

def dataSelector():
	window = tk.Toplevel(gl_vars.root)
	#window.maxsize(width=0, height=100)
	## THESE SCROLLBARS ARE UTTERLY USELESS NEED TO CORRECT THAT
	## UPDATE: NOT useless anu
##############################################################
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
	frame = tk.Frame(canvas, width=1000,height=1000)
	canvas.create_window((0,0), window=frame, anchor='nw')
	# vscrollbar = tk.Scrollbar(window)
	# hscrollbar = tk.Scrollbar(window, orient = "horizontal")
	# vscrollbar.pack(side = "right", fill = "y")
	# hscrollbar.pack(side = "bottom", fill = "x")
	# canvas = tk.Canvas(window,yscrollcommand = vscrollbar.set,xscrollcommand = hscrollbar.set)
	# canvas.pack(side = "top", expand = True)
	# vscrollbar.config(command = canvas.yview)
	# hscrollbar.config(command = canvas.xview)
	
##########################
	var_time = tk.IntVar(frame)
	i = gl_vars.nb.tab(gl_vars.nb.select(), "text")
	dataset = gl_vars.data[i]
	tk.Label(frame, text = "Select data points by: ").grid(row = 0,column = 0)
	tk.Radiobutton(frame, variable = var_time, value = 0, text = "Year").grid(row = 0, column = 1)
	tk.Radiobutton(frame, variable = var_time, value = 1, text = "Month").grid(row = 0, column = 2)
	time_range = [pd.to_datetime(a).date() for a in list(dataset.variables['time'].values)]
	time_range.sort()
	tk.Label(frame, text = "Select variables:" ).grid(row = 820,column = 0)
	var_var = dict()
	num = 0
	for x in list(dataset.data_vars.keys()):
		var_var[x] = tk.BooleanVar(frame)
		tk.Checkbutton(frame, text = x, variable = var_var[x]).grid(row = 821, column = num)
		num += 1
	chk = []
	var_rad = None
	var_arr = None
	year_start, year_end = None, None
	tk.Label(frame, text = "Statistics").grid(row = 900, column = 0)
	outField = tk.Text(frame, height = 4, width = 5)
	outField.grid(row = 900, column = 1, columnspan = 3, sticky = tk.W+tk.E+tk.N+tk.S, pady = 5, padx = 3, rowspan = 4)
	months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
	var_month = [tk.BooleanVar(frame, name = "all"+"_"+ mon) for mon in months]
	month_label = [tk.Checkbutton(frame, text = months[d], variable = var_month[d]) for d in range(len(months))]
	year_start = int(time_range[0].year)
	year_end = int(time_range[-1].year)
	var_year = [tk.BooleanVar(frame, name = str(d)+ "_all") for d in range(year_start,year_end+1)]
	year_labels = [tk.Checkbutton(frame, text = str(ind+year_start), variable = var_year[ind]) for ind in range(year_end-year_start+1)]
	var_rad = [tk.BooleanVar(frame) for ind in range(year_end-year_start+1)]
	chk = [tk.Checkbutton(frame, text = str(ind+year_start), variable =  var_rad[ind]) for ind in range(year_end-year_start+1)]
	chk2 = dict()
	for dra in range(year_start,year_end+1):
		chk2[str(dra)] = dict()
		for mon in months:
			chk2[str(dra)][mon] = [tk.BooleanVar(frame, name = str(dra)+"_"+mon)]
			chk2[str(dra)][mon].append(tk.Checkbutton(frame, variable =  chk2[str(dra)][mon][0]))
	def selectGrid(event, b, c):
		nonlocal var_var, var_rad, chk, year_start, year_end
		if(var_time.get() == 0):
			for i in month_label:
				i.grid_forget()
			for i in year_labels:
				i.grid_forget()
			for i in range(0,year_end-year_start+1):
				for m in range(12):
					chk2[str(i+year_start)][months[m]][1].grid_forget() 
			row_max = 10
			for ind in range(year_end-year_start+1):
				chk[ind].grid(row = 1+(ind%row_max), column = 1+ind//row_max)
		elif(var_time.get() == 1):
			for a in chk:
				a.grid_forget()
			for i in range(12):
				month_label[i].grid(row = 1, column = 1+i)
			for ind in range(0,year_end-year_start+1):
				year_labels[ind].grid(row = 2+ind, column = 0)
			for i in range(0,year_end-year_start+1):
				for m in range(12):
					chk2[str(i+year_start)][months[m]][1].grid(row = 2+i, column = m+1)
	def getStats():
		nonlocal var_var, var_arr
		var_arr = [key for key,value in var_var.items() if value.get()]
		if(not var_time.get()):
			chk_status = [a.get() for a in var_rad]
			year_param = year_start
		else:
			chk_status = dict()
			for dra in range(year_start,year_end+1):
				chk_status[str(dra)] = dict()
				for mon in months:
					chk_status[str(dra)][mon] = chk2[str(dra)][mon][0].get()
			year_param = None
		outdict = ffunc.getStats(dataset, year_param, chk_status, var_arr)
		outField.delete(1.0,tk.END)
		outField.insert(tk.INSERT, ffunc.generateMessage(outdict))
	var_time.trace("w", selectGrid)
	var_time.set(0)

	b1 = tk.Button(frame, command = getStats, text = "Get statistics")
	b1.grid(row = 1000, column = 0)
	canvas.config(scrollregion = (0,0,1000,1000))

	def select(event, b, c):
		year = event.split('_')[0]
		mon = event.split('_')[1]
		if(year == "all"):
			for ind in range(year_start, year_end+1):
				chk2[str(ind)][mon][0].set(var_month[months.index(mon)].get())
		elif (mon == "all"):
			for mon in months:
				chk2[year][mon][0].set(var_year[int(year)-year_start].get())
	for a in var_month:
		a.trace("w", select)
	for a in var_year:
		a.trace("w", select)


def plotGenerator():
	i = gl_vars.nb.tab(gl_vars.nb.select(), "text")
	dataset = gl_vars.data[i]
	window = tk.Toplevel(gl_vars.root)
	time_range = [str(pd.to_datetime(a).date()) for a in list(dataset.variables['time'].values)]
	tk.Label(window, text = "Time range: ").grid(row = 0, column = 0)
	varSpin = tk.StringVar(window)
	varSpin_o = tk.StringVar(window)
	tk.Spinbox(window, values = time_range, textvariable = varSpin).grid(row = 0, column = 1)
	tk.Spinbox(window, values = time_range, textvariable = varSpin_o).grid(row = 0, column = 2)
	tk.Label(window, text = "Select time interval for x axis: ").grid(row = 1, column = 0)
	varSpin1 = tk.StringVar(window)
	varSpin2 = tk.StringVar(window)
	spbox = tk.Spinbox(window, textvariable = varSpin1)
	spbox.grid(row = 1, column = 1)
	ttk.Combobox(window, textvariable = varSpin2, values = ["years", "months", "days"]).grid(row = 1, column = 2)
	tk.Label(window, text = "Select filters:").grid(row = 25, column = 0)
	val_filt = tk.IntVar(window)
	tk.Radiobutton(window, variable = val_filt, value = 0, text = "No filters").grid(row = 26, column = 0)
	tk.Radiobutton(window, variable = val_filt, value = 1, text = "Lat-Lon bounds").grid(row = 26, column = 1)
	tk.Radiobutton(window, variable = val_filt, value = 2, text = "ShapeFile").grid(row = 26, column = 2)

	def fillValues(event, b, c):
		#IDEALLY THIS IS NOT REQUIRED, USER SHOULD BE ABLE TO ENTER WHATEVER THEY WANT.
		if (varSpin2.get() == "years"):
			arr = [a for a in range(1,21)]
		elif (varSpin2.get() == "months"):
			arr = [a for a in range(1,13)]
		elif (varSpin2.get() == "days"):
			arr = [a for a in range(1,32)]
		spbox.config(values = arr)
	varSpin2.trace("w", fillValues)
	
	lon_var,lat_var = None, None
	for a in list(gl_vars.data[i].dims):
		if (a.lower().startswith("lon")):
			lon_var = a
		if (a.lower().startswith("lat")):
			lat_var = a
	
	lat_arr = list(dataset.variables[lat_var].values)
	lat_arr2 = [str(a) for a in lat_arr]
	lat_arr.sort()
	lon_arr = list(dataset.variables[lon_var].values)
	lon_arr2 = [str(a) for a in lon_arr]
	lon_arr.sort()
	lbl1 = tk.Label(window, text = "Latitude Range:")
	spn_box1 = tk.Spinbox(window, values = lat_arr)
	spn_box2 = tk.Spinbox(window, values = lat_arr)
	lbl2 = tk.Label(window, text = "Longitude Range:")
	spn_box3 = tk.Spinbox(window, values = lon_arr)
	spn_box4 = tk.Spinbox(window, values = lon_arr)
	filename = None
	lbl3 = tk.Label(window)
	lbl4 = tk.Label(window, text = "Select place:")
	plc_var = tk.StringVar(window)
	cmb1 = ttk.Combobox(window, textvariable = plc_var)
	places = None
	def selectFilter(event, b, c):
		nonlocal places, filename
		if (val_filt.get() == 0):
			lbl1.grid_forget()
			spn_box1.grid_forget()
			spn_box2.grid_forget()
			lbl2.grid_forget()
			spn_box3.grid_forget()
			spn_box4.grid_forget()
			lbl3.grid_forget()
			lbl4.grid_forget()
			cmb1.grid_forget()
			filename = None

		elif (val_filt.get() == 1):
			lbl1.grid(row = 27, column = 0)
			spn_box1.grid(row = 27, column = 1)
			spn_box2.grid(row = 27, column = 2)
			lbl2.grid(row = 28, column = 0)
			spn_box3.grid(row = 28, column = 1)
			spn_box4.grid(row = 28, column = 2)
			lbl3.grid_forget()
			lbl4.grid_forget()
			cmb1.grid_forget()
			filename = None
		elif(val_filt.get() == 2):
			lbl1.grid_forget()
			spn_box1.grid_forget()
			spn_box2.grid_forget()
			lbl2.grid_forget()
			spn_box3.grid_forget()
			spn_box4.grid_forget()
			filename = askopenfilename(filetypes=[("SHAPEFILE", "*.shp")])
			if (filename == ""):
				filename = None
				val_filt.set(0)
			else:
				shp = gpd.read_file(filename)
				#print(list(shp.columns))
				# Searching in this above list and selecting the name variable seems like a good idea.
				try:
					places = list(shp['NAME'])
				except:
					places = list(shp['ST_NAME'])
				## THIS IS VERY VERY BAD, NEEDS TO BE GENERALIZED BETTER.
				#[Need to modify the selector to allow multiple places to be selected.]
				places2 = [i for i in places if i is not None]
				places2.append("ALL")
				places2.sort()
				lbl3.config(text=filename.split('/')[-1])
				lbl3.grid(row = 27, column = 0)
				lbl4.grid(row = 28, column = 0)
				cmb1.config(values = places2)
				cmb1.grid(row = 28, column = 1)

	val_filt.trace("w", selectFilter)

	tk.Label(window, text = "Select variables:" ).grid(row = 20,column = 0)
	var_var = dict()
	num = 0
	for x in list(dataset.data_vars.keys()):
		var_var[x] = tk.IntVar(window)
		tk.Checkbutton(window, text = x, variable = var_var[x]).grid(row = 21, column = num)
		num += 1
	b1 = tk.Button(window, text = "Plot")
	b1.grid(row = 100, column = 1)

	def dataPlot():
		start_time_index = time_range.index(varSpin.get())
		end_time_index = time_range.index(varSpin_o.get())
		time_interval = (int(varSpin1.get()), varSpin2.get())
		variables = [key for key,value in var_var.items() if value.get() == 1]
		if (val_filt.get() == 0):
			output_mean, output_std, time_array = ffunc.plotData(dataset, start_time_index, end_time_index, time_interval, variables)
		elif(val_filt.get() == 1):
			lat_r = [lat_arr2.index(spn_box1.get()),lat_arr2.index(spn_box2.get())]
			lon_r = [lon_arr2.index(spn_box3.get()),lon_arr2.index(spn_box4.get())]
			lat_r.sort()
			lon_r.sort()
			output_mean, output_std, time_array = ffunc.plotData(dataset, start_time_index, end_time_index, time_interval, variables, filt = "bounds", lat_range = slice(lat_r[0], lat_r[1]), lon_range = slice(lon_r[0], lon_r[1]))
		elif(val_filt.get() == 2):
			if(plc_var.get() == "ALL"):
				plac_ind = None
			else:
				plac_ind = places.index(plc_var.get())
			output_mean, output_std, time_array = ffunc.plotData(dataset, start_time_index, end_time_index, time_interval, variables, filt = "shapefile", filename = filename, place = plac_ind)
		pfunc.plotLines(output_mean, output_std, time_array, variables)
	
	b1.config(command = dataPlot)