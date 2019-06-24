# gui_functions.py #

import gl_vars
import file_functions as ffunc
import plot_functions as pfunc

import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfilename

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

#THE ENTIRE PLOT WINDOW PART NEEDS RESTRUCTURING

# PRE-CONDITION
#	filenames: A list of strings corresponding to each NETCDF file containing the full path of the file.
#	gl_vars.root and gl_vars.data should be initialized before function call. 
def getMultiSets(filenames):
	#print(gl_vars.font1.actual())
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
	
	# PRE-CONDITION
	#	gl_vars.data needs to have been initialised earlier.
	#	var (The text Entry widget) should have a valid string.
	def combine_files():
		nonlocal filenames2
		indxs = [a for a in filenames if chk_vars[a].get() == 1]
		data_mod = [gl_vars.data[a] for a in indxs]
		merged = xr.merge(data_mod)
		filenames2 = [a for a in filenames if a not in indxs]
		copy = dict()
		for a in filenames2:
			copy[a] = gl_vars.data[a]
		newName =var.get()
		copy[newName] = merged
		gl_vars.data = copy
		filenames2.append(newName)
	# POST-CONDITION
	#	gl_vars.data and filenames2 now contain a smaller list after combining the selected Datasets.

	b1 = tk.Button(gl_vars.root, text = 'Combine')
	b2 = tk.Button(gl_vars.root, text = 'More (Refresh list)')
	b3 = tk.Button(gl_vars.root, text = 'Done')

	# PRE-CONDITION
	#	No-prereqs as such. Outer function needs to work and should not form cyclic calls.
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
	# POST-CONDITION
	#	Cleans the current window and refreshes everything after resetting the filenames.


	# PRE-CONDITION
	#	Outer function should be working. gl_vars.root needs to have been initialised.	
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
		menu.add_command(label = "Plot", command = plotWindow)
		menu.add_command(label = "Export", command = exportToCSV)
		menu.add_command(label = "Statistics", command = exportToCSV)

		gl_vars.root.config(menu=menu)
		addPages(filenames2)
		fillPages()
		for i in gl_vars.chk_var_list1.keys():
			for j in gl_vars.chk_var_list1[i].keys():
				gl_vars.chk_var_list1[i][j].trace("w",trig)
	# POST-CONDITION
	#	Initializes the first steps towards creating the GUI. Destroys the previous widget setup and creates a notebook, with each page corresponding to the datasets in gl_var.data after combining.
	# 	Function calls to create and add the pages are done and one set of IntVars (correspoding to the radio buttons) are bound to the function trigger.
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
# POST-CONDITION
#	Initially, a pop-up window to allow the user to combine the selected files is shown. After all the combining, the user can then press a button to generate the next interface of the GUI, which is used to actually retrieve and visualise the data.
# 	The tkinter notebook is initialised in an inner function.

# PRE-CONDITION
#	filenames: A list of strings corresponding to each NETCDF file containing the full path of the file.
#	gl_vars.nb must be initialised before the function call.
def addPages(filenames):
	gl_vars.pages = dict()
	for i in filenames:
		gl_vars.pages[i] = ttk.Frame(gl_vars.nb)
		gl_vars.nb.add(gl_vars.pages[i], text = i)
	gl_vars.nb.grid(row = 0, column = 0, columnspan=9, sticky = tk.E + tk.W, padx = 5)
# POST-CONDITION
#	gl_vars.pages is initialised with Tkinter frame widgets, which are then added to the tkinter Notebook. 

# PRE-CONDITION
#	gl_vars.chk_var_list1 and gl_vars.spn_box_list need to be initialised before function call.
def trig(event,b,c):
	dats = event.split('$')		#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	n1 = dats[2]
	i = dats[1]
	row_num = int(dats[3])
	if (gl_vars.chk_var_list1[i][n1].get() == 0):
		gl_vars.spn_box_list[i][n1][1].grid_forget()   #***# This requires changes
	else:
		gl_vars.spn_box_list[i][n1][1].grid(row = row_num, column = 2)
# POST-CONDITION
#	The specific radio button toggles the visibility of the spinbox.
	
# PRE-CONDITION
#	gl_vars.data and gl_vars.pages need to be initialised before function is called
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
# POST-CONDITION
#	Each page is filled with Radio-buttons, Spinboxes, Checkboxes, Buttons and appropriate labels.
#	The global variables, chk_var_list1, chk_var_list2, chk_var_list3, and spn_box_list are initialised. 

# PRE-CONDITION
#	name: The name of the dimension in question as a string.
#	num: an integer denoting the row number and index of the variable in the list.
#	ind: The index of the page (.nc file) as an integer.
#	gl_vars.pages and gl_vars.chk_var_list1 should have been initialised before function call.
def createSelRow(name, num, ind):
	tk.Label(gl_vars.pages[ind], text = name).grid(row = num, column = 0)
	gl_vars.chk_var_list1[ind][name] = tk.IntVar(gl_vars.pages[ind], name = "var$"+ind+ "$" + name + '$' + str(num+5))
	r1 = tk.Radiobutton(gl_vars.pages[ind], text = 'Single', variable = gl_vars.chk_var_list1[ind][name], value = 0)
	r1.grid(row = num, column = 1)
	r2 = tk.Radiobutton(gl_vars.pages[ind], text = 'Range (Inclusive)', variable = gl_vars.chk_var_list1[ind][name], value = 1)
	r2.grid(row = num, column = 2)
# POST-CONDITION
#	Each call of the function generates one label, and two radio buttons which are placed and then deselected.
#	chk_var_list1 is initialised with actual vars.

# PRE-CONDITION
#	name: The name of the dimension in question as a string.
#	num: an integer denoting the row number and index of the variable in the list.
#	ind: The index of the page (.nc file) as an integer.
#	value_list: The range of possible values that the variable in question can take in the form of a list.
#	gl_vars.pages and gl_vars.spn_box_list should have been initialised prior to function call.
def createSelBox(name, num, ind, value_list):
	value_list.sort()
	tk.Label(gl_vars.pages[ind], text = name).grid(row = num+5, column = 0)
	gl_vars.spn_box_list[ind][name] = [tk.Spinbox(gl_vars.pages[ind]), tk.Spinbox(gl_vars.pages[ind])]
	gl_vars.spn_box_list[ind][name][0].configure(values=value_list)
	gl_vars.spn_box_list[ind][name][0].grid(row = num+5, column = 1)
	gl_vars.spn_box_list[ind][name][1].configure(values=value_list)
# POST-CONDITION
#	Each function call creates and places one label and creates two spin boxes with the given range for the given variable.

# PRE-CONDITION
#	data_var: This is a string with the name of the data variable in question.
#	ind: The index of the page (.nc file) as an integer.
#	num: an integer denoting the row number.
#	num2: an integer denoting the column number
#	gl_vars.chk_var_list2 and gl_vars.pages need to have been initialised before function call.
def createCheckBox(data_var, ind, num, num2):
	gl_vars.chk_var_list2[ind][data_var] = tk.IntVar(gl_vars.pages[ind], name = "var$"+data_var+"$"+ind+"$"+str(num2-1))
	tk.Checkbutton(gl_vars.pages[ind], text = data_var, variable = gl_vars.chk_var_list2[ind][data_var]).grid(row = num, column = num2)
# POST-CONDITION
#	Each function call creates and places a checkbox in the given page, at the given position, with the appropriate label.
#	gl_vars.chk_var_list2 is completely initialised with with named tkinter IntVar. Each associated with a checkbox.
def getIndexes():
	i = gl_vars.nb.tab(gl_vars.nb.select(), "text")
	rangeVar = dict()
	for a in gl_vars.chk_var_list1[i].keys():
		rangeVar[a] = gl_vars.chk_var_list1[i][a].get()
	gl_vars.messages = dict()
	dimension_list = list(gl_vars.data[i].coords.keys())
	for x in dimension_list:
		gl_vars.messages[x] = [gl_vars.spn_box_list[i][x][0].get()]
		if(rangeVar[x]):
			gl_vars.messages[x].append(gl_vars.spn_box_list[i][x][1].get())
		else:
			gl_vars.messages[x].append(None)
	gl_vars.outVar = dict()
	for a in gl_vars.chk_var_list2[i].keys():
		gl_vars.outVar[a] = gl_vars.chk_var_list2[i][a].get()

# PRE-CONDITION
#	gl_vars.nb, gl_vars.spn_box_list, gl_vars.chk_var_list1, and gl_vars.chk_var_list3 need to have been initialised.
#	Whether gl_vars.output is None or not, will affect the function output. 
def retrieveData():
	i = gl_vars.nb.tab(gl_vars.nb.select(), "text")
	getIndexes()
	if (gl_vars.chk_var_list3[i].get() == 1 and gl_vars.output is None):
		openPlotWindow(2)
		return
	if (gl_vars.chk_var_list3[i].get() == 1):
		masked_data = gl_vars.output
		sel_message, output_message = ffunc.getData(i, 1, masked_data)
		gl_vars.output = None
	else:
		sel_message, output_message = ffunc.getData(i, 0, None)
	printMessages(output_message,sel_message)
# POST-CONDITION
#	gl_vars.messages is initialised with the contents of the spinboxes (i.e. the data ranges selected by the user)
#	gl_vars.outVar is initialised with the state of the checkboxes at the time of button pressing.
#	The execution of this function will result in retrieval of the selected data, which is then printed through another function call.

# PRE-CONDITION
#	o_message: This is a string containing the output data.
#	s_message: This is a string which lists out the selected variable ranges. 
#	gl_vars.selBox and gl_vars.opBox needs to have been initialised befire function call.
def printMessages(o_message, s_message):
	gl_vars.selBox.delete(1.0,tk.END)
	gl_vars.selBox.insert(tk.INSERT, s_message)
	gl_vars.opBox.delete(1.0,tk.END)
	gl_vars.opBox.insert(tk.INSERT, o_message)
# POST-CONDITION
#	messages are printed in the appropriate Text boxes.

def openWindow(org):
	i = gl_vars.nb.tab(gl_vars.nb.select(), "text")
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
		varSave = tk.IntVar(window) # save file checkbutton
		varShow = tk.IntVar(window) # show plot checkbutton
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
			org = varRadio.get()
			if (org == 0):
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
			elif (org == 1):
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
			elif (org == 2):
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
			elif(org == 3):
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
			#print(plac_ind)
			if (org == 0):
				pfunc.plotMapShape(i,var_name, t1, filename, plac_ind, proj_string)
			elif (org == 1):
				pfunc.animation(i,var_name,(t1,t2), filename, plac_ind, proj_string,show, save, save_name)
			elif (org == 2):
				pfunc.vectorMap(i,t1, filename, plac_ind, proj_string)
			elif (org == 3):
				pfunc.vectorAnim(i,(t1,t2),filename, plac_ind, proj_string,show, save, save_name)
		
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
				getIndexes()
				data_arr = ffunc.getData(i,0,var_name)[1]
				if (filename is not None):
					temp, lon_var, lat_var, temp2 = ffunc.getShapeData(i, var_name, t1, filename, plac_ind)
					out = ffunc.applyShape(data_arr, lat_var, lon_var, filename, plac_ind)[0]
				else:
					out = data_arr
			elif(varBnd.get() == 1):
				if (filename is not None):
					out = [np.array(ffunc.getShapeData(i, var_name, time_t[0], filename, plac_ind)[0])]
					for time_i in range(time_t[0], time_t[1]):
						out.append(ffunc.getShapeData(i, var_name, time_i+1, filename, plac_ind)[0]) 
					#This segment takes a long long time to execute. Please keep that in mind. Hence, testing is also not thorough.
					out = np.array(out)
				else:
					out = gl_vars.data[i].data_vars[var_name][t3,:,:]
			#print(out)
			#print("Hey")
			if(varBnd.get() == 0 and filename is not None):
				resized_array = np.array(out.data)
			else:
				resized_array = np.resize(out, [out.shape[0]* out.shape[1], out.shape[2]])
			#print(resized_array, resized_array.shape)
			pd.DataFrame(resized_array).to_csv(asksaveasfilename(filetypes=[("Comma-separated Values", "*.csv")]), header = None, index = None, na_rep = "NaN")
			tk.Label(window, text = "Done").grid(row = 43, column = 1, columnspan = 2)
		b1.config(command = saveCSV)
	
	elif (org == 2):
		#Retrieve Data, but limited by shape
		shapeSelect(None,None,None)
		def printShapeData():
			nonlocal window
			masked_data = ffunc.getShapeData(i,None, None, filename, plac_ind)[0]
			sel_message, output_message = ffunc.getData(i, 1, masked_data)
			printMessages(output_message,sel_message)
			window.destroy()
		b1.config(command = printShapeData)

	var2.trace("w", shapeSelect)

	# PRE-CONDITION
	#	Function is checkbox triggered. Arguments are required dummies.
	#	gl_vars.root needs to have been initialised at the start.


def plotWindow():
	openWindow(0)

def exportToCSV():
	openWindow(1)

def retrieveData():
	i = gl_vars.nb.tab(gl_vars.nb.select(), "text")
	getIndexes()
	if (gl_vars.chk_var_list3[i].get() == 1):
		openWindow(2)
	else:
		sel_message, output_message = ffunc.getData(i, 0, None)
		printMessages(output_message,sel_message)

