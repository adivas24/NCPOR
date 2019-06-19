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


# PRE-CONDITION
#	filenames: A list of strings corresponding to each NETCDF file containing the full path of the file.
#	gl_vars.root and gl_vars.data should be initialized before function call. 
def getMultiSets(filenames):
	#print(gl_vars.font1.actual())
	l1 = tk.Label(gl_vars.root, text = "Tick the ones you want to combine:")
	l1.grid(row = 0, column  = 0,ipadx = 10, pady = 10, columnspan = 5, sticky = tk.W)
	chk_vars = [tk.IntVar(gl_vars.root) for a in filenames]
	var = tk.StringVar(gl_vars.root)
	i = 1
	chk_arr = [None for a in filenames]
	for a in filenames:
		chk_arr[i-1] = tk.Checkbutton(gl_vars.root, text = a, variable = chk_vars[i-1])
		chk_arr[i-1].grid(row = i, column = 0, columnspan = 5, ipadx = 20, sticky = tk.W, pady = 3)
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
		indxs = [a for a in range(len(filenames)) if chk_vars[a].get() == 1]
		data_mod = [gl_vars.data[a] for a in indxs]
		merged = xr.merge(data_mod)
		filenames2 = [filenames[a] for a in range(len(filenames)) if a not in indxs]
		copy = [gl_vars.data[a] for a in range(len(gl_vars.data)) if a not in indxs]
		copy.append(merged)
		gl_vars.data = copy
		filenames2.append(var.get())
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
		for a in chk_arr:
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
		for a in chk_arr:
			a.destroy()
		gl_vars.nb = ttk.Notebook(gl_vars.root)
		addPages(filenames2)
		fillPages()
		for i in gl_vars.chk_var_list1:
			for j in i:
				j.trace("w",trig)
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
	gl_vars.pages = [ttk.Frame(gl_vars.nb) for i in range(len(filenames))]
	for i in range(len(filenames)):
		gl_vars.nb.add(gl_vars.pages[i], text = filenames[i])
	gl_vars.nb.grid(row = 0, column = 0, columnspan=9, sticky = tk.E + tk.W, padx = 5)
# POST-CONDITION
#	gl_vars.pages is initialised with Tkinter frame widgets, which are then added to the tkinter Notebook. 

# PRE-CONDITION
#	gl_vars.chk_var_list1 and gl_vars.spn_box_list need to be initialised before function call.
def trig(event,b,c):
	dats = event.split('_')
	i = int(dats[2])
	n1 = int(dats[1])
	if (gl_vars.chk_var_list1[i][n1].get() == 0):
		gl_vars.spn_box_list[i][2*n1+1].grid_forget()
	else:
		gl_vars.spn_box_list[i][2*n1+1].grid(row = 5+n1, column = 2)
# POST-CONDITION
#	The specific radio button toggles the visibility of the spinbox.
	
# PRE-CONDITION
#	gl_vars.data and gl_vars.pages need to be initialised before function is called
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
		#gl_vars.selBox = [createOPBox("Selection", i, n1) for l in range(no_of_pages)]
		n2 = 1
		tk.Label(gl_vars.pages[i], text="Choose output variables:").grid(row = n1+1, column = 0)
		for k in variable_list:
			createCheckBox(k, i, n1+1, n2)
			n2 += 1
		#gl_vars.opBox = [createOPBox("Output data", i, n1+2) for l in range(no_of_pages)]
	tk.Label(gl_vars.root, text="Selection:").grid(column = 1, row = 90, sticky = tk.W, padx = 5, pady = 5)
	gl_vars.selBox = tk.Text(gl_vars.root, height = 4, width = 5)
	gl_vars.selBox.grid(row = 90, column = 2, columnspan = 3, sticky = tk.W+tk.E+tk.N+tk.S, pady = 5, padx = 3, rowspan = 4)
	tk.Label(gl_vars.root, text="Output:").grid(column = 5, row = 90, sticky = tk.W, padx = 5, pady = 5)
	gl_vars.opBox = tk.Text(gl_vars.root, height = 4, width = 5)
	gl_vars.opBox.grid(row = 90, column = 6, columnspan = 3, sticky = tk.W+tk.E+tk.N+tk.S, pady = 5, padx = 3, rowspan = 4)
	tk.Button(gl_vars.root, text = 'Retrieve data', command = retrieveData).grid(row = 100, column = 1, sticky = tk.E + tk.W, pady = 5)
	tk.Button(gl_vars.root, text = 'Plot', command = plotWindow).grid(row = 100, column = 3, sticky = tk.E + tk.W, pady = 5)
	tk.Button(gl_vars.root, text = 'Export to CSV', command = exportToCSV).grid(row = 100, column = 5, sticky = tk.E + tk.W, pady = 5)
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
	gl_vars.chk_var_list1[ind][num] = tk.IntVar(gl_vars.pages[ind], name = "var_"+str(num)+ "_" + str(ind))
	r1 = tk.Radiobutton(gl_vars.pages[ind], text = 'Single', variable = gl_vars.chk_var_list1[ind][num], value = 0)
	r1.grid(row = num, column = 1)
	r2 = tk.Radiobutton(gl_vars.pages[ind], text = 'Range (Inclusive)', variable = gl_vars.chk_var_list1[ind][num], value = 1)
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
	gl_vars.spn_box_list[ind][2*num].configure(values=value_list)
	gl_vars.spn_box_list[ind][2*num].grid(row = num+5, column = 1)
	gl_vars.spn_box_list[ind][2*num+1].configure(values=value_list)
# POST-CONDITION
#	Each function call creates and places one label and creates two spin boxes with the given range for the given variable.

# PRE-CONDITION
#	name: The name of the textbox in question as a string.
#	ind: The index of the page (.nc file) as an integer.
#	num: an integer denoting the row number.
#	gl_vars.pages needs to have been initialised before function call.
# def createOPBox(name, ind, num):
# 	tk.Label(gl_vars.pages[ind], text = name).grid(row = num, column = 0)
# 	textBox = tk.Text(gl_vars.pages[ind], height = 4)
# 	textBox.grid(row = num, column = 1, columnspan = 6)
# 	scroll = tk.Scrollbar(gl_vars.pages[ind])
# 	scroll.grid(row = num,column = 6)
# 	scroll.config(command=textBox.yview)
# 	textBox.config(yscrollcommand=scroll.set)
# 	return textBox
# POST-CONDITION
#	Each function call creates and places a label (of the given name) along with a textbox and scrollbar. Thetkinter instance of the Text widget is returned ny the function.

# PRE-CONDITION
#	data_var: This is a string with the name of the data variable in question.
#	ind: The index of the page (.nc file) as an integer.
#	num: an integer denoting the row number.
#	num2: an integer denoting the column number
#	gl_vars.chk_var_list2 and gl_vars.pages need to have been initialised before function call.
def createCheckBox(data_var, ind, num, num2):
	gl_vars.chk_var_list2[ind][num2-1] = tk.IntVar(gl_vars.pages[ind], name = "var_"+data_var+"_"+str(ind)+"_"+str(num2-1))
	tk.Checkbutton(gl_vars.pages[ind], text = data_var, variable = gl_vars.chk_var_list2[ind][num2-1]).grid(row = num, column = num2)
# POST-CONDITION
#	Each function call creates and places a checkbox in the given page, at the given position, with the appropriate label.
#	gl_vars.chk_var_list2 is completely initialised with with named tkinter IntVar. Each associated with a checkbox.
def getIndexes():
	i = gl_vars.nb.index("current")
	rangeVar = [a.get() for a in gl_vars.chk_var_list1[i]]
	gl_vars.messages = [[None, None] for a in range(len(rangeVar))]
	for x in range(len(rangeVar)):
		gl_vars.messages[x][0] = gl_vars.spn_box_list[i][x*2].get()
		if(rangeVar[x]):
			gl_vars.messages[x][1] = gl_vars.spn_box_list[i][x*2+1].get()
	gl_vars.outVar = [a.get() for a in gl_vars.chk_var_list2[i]]
# PRE-CONDITION
#	gl_vars.nb, gl_vars.spn_box_list, gl_vars.chk_var_list1, and gl_vars.chk_var_list3 need to have been initialised.
#	Whether gl_vars.output is None or not, will affect the function output. 
def retrieveData():
	i = gl_vars.nb.index("current")
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
	printMessages(output_message,sel_message, i)
# POST-CONDITION
#	gl_vars.messages is initialised with the contents of the spinboxes (i.e. the data ranges selected by the user)
#	gl_vars.outVar is initialised with the state of the checkboxes at the time of button pressing.
#	The execution of this function will result in retrieval of the selected data, which is then printed through another function call.

# PRE-CONDITION
#	o_message: This is a string containing the output data.
#	s_message: This is a string which lists out the selected variable ranges. 
#	gl_vars.selBox and gl_vars.opBox needs to have been initialised befire function call.
def printMessages(o_message, s_message, ind):
	gl_vars.selBox.delete(1.0,tk.END)
	gl_vars.selBox.insert(tk.INSERT, s_message)
	gl_vars.opBox.delete(1.0,tk.END)
	gl_vars.opBox.insert(tk.INSERT, o_message)
# POST-CONDITION
#	messages are printed in the appropriate Text boxes.

# PRE-CONDITION
#	No prereqs. Dummy call as argument needed to be passed.
def plotWindow():
	openPlotWindow(0)
# POST-CONDITION
#	openPlotWindow is called with appropriate argument.

# PRE-CONDITION
#	org: An integer value which selects the mode. 0 corresponds to plotting by a map, 1 corresponds to using a shapefile to export to csv and 2 corresponds to using a shapefile and biunding ranges to output in the GUI.
#	gl_vars.nb, gl_vars.data, and gl_vars.root need to have been initialised before function call.
def openPlotWindow(org):
	i = gl_vars.nb.index("current")
	window = tk.Toplevel(gl_vars.root)
	var2 = tk.IntVar(window)
	varn = tk.StringVar(window)
	varn.set("PlateCarree")
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
		if(org != 1):
			tk.Label(window, text = "Select projection: ").grid(row = 3, column = 0)
			proj_list = ["PlateCarree","AlbersEqualArea","AzimuthalEquidistant","EquidistantConic","LambertConformal","LambertCylindrical","Mercator","Miller","Mollweide","Orthographic","Robinson","Sinusoidal","Stereographic","TransverseMercator","UTM","InterruptedGoodeHomolosine","RotatedPole","OSGB","EuroPP","Geostationary","NearsidePerspective","EckertI","EckertII","EckertIII","EckertIV","EckertV","EckertVI","EqualEarth","Gnomonic","LambertAzimuthalEqualArea","NorthPolarStereo","OSNI","SouthPolarStereo"]
			ttk.Combobox(window, textvariable = varn, values = proj_list).grid(row = 3, column = 1)
		tk.Checkbutton(window, text = "Use SHP file", variable = var2).grid(row = 4, column = 0)
	b1 = tk.Button(window, text = 'Confirm')
	b1.grid(row = 10, column = 1)
	var3 = tk.StringVar(window)
	var3.set("ALL")
	filename = None
	plac_ind = None
	places = []
	output = None

	# PRE-CONDITION
	#	Function is button triggered. Arguments are required dummies.
	#	gl_vars.root needs to have been initialised at the start.
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
				places2 = [i for i in places if i is not None]
				places2.append("ALL")
				tk.Label(window, text=filename).grid(row = 4, column = 1)
				places2.sort()
				ttk.Combobox(window, textvariable = var3, values = places2).grid(row = 5, column = 1)
		if (org == 2):
			nonlocal b1
			b1.config(command = shapeData)
	# POST-CONDITION
	#	This creates a pop-up window allowing the user to select a shape file and a place from the SHAPEFILE storing thrm in local function variables.
	#	In mode 2, it also changes the button functionality for futher operation.
	
	# PRE-CONDITION
	#	places and filename need to be initialised to appropriate values before function call.
	def plotMap():
		proj_string = varn.get()
		nonlocal plac_ind
		if(var2.get() == 1 and var3.get() != "ALL"):
			plac_ind = places.index(var3.get())
		#pfunc.plotMapShape(i,var.get(), time_range.index(spin.get()), filename, plac_ind, proj_string)
		#pfunc.animation(i,var.get(), time_range.index(spin.get()), filename, plac_ind, proj_string)
		pfunc.vectorMap(i,var.get(), time_range.index(spin.get()), filename, plac_ind, proj_string)

	# POST-CONDITION
	#	Appropriate map is generated through a function call, depending on whether SHPAPEFILE has been used or not.

	# PRE-CONDITION
	#	places filename, and window should be initialised before function call.
	def shapeData():
		nonlocal window
		if(var3.get() == "ALL"):
			plac_ind = None
		else:
			plac_ind = places.index(var3.get())
		if (org != 2):
			gl_vars.output = ffunc.getShapeData(i,var.get(), time_range.index(spin.get()), filename, plac_ind)[0]
		else:
			gl_vars.output = ffunc.getShapeData(i,None, None, filename, plac_ind)[0]
			window2 = tk.Toplevel(gl_vars.root)
			tk.Label(window2, text = "Press RetrieveData again to display the chosen shapefile masked data.").grid(row = 0, column = 0)
		if(org == 1):
			window2 = tk.Toplevel(gl_vars.root)
			tk.Label(window2, text = "Press Save again to save the chosen shapefile masked data.").grid(row = 0, column = 0)
		window.destroy()
	# POST-CONDITION
	#	Function to mask data is called and gl_vars.output is initialised and can now be accesed via button press.

	var2.trace("w", shapeSelect)
	if(org == 0):
		b1.config(command = plotMap)
	elif(org == 1):
		var2.set(1)
		b1.config(command = shapeData)
	elif(org == 2):
		shapeSelect(None,None,None)
# POST-CONDITION
#	Creates a pop-up window that allows the user to select a SHAPEFILE and subsequently a place for masking purposes.
#	Additional widgets are used in some cases. More detail can be gathered from the nested functions.

# PRE-CONDITION
#	gl_vars.nb, gl_vars.data, and gl_vars.root need to be initialised.
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
	
	# PRE-CONDITION
	#	vr2, window and var need to be initialised prior to function call.
	def saveCSV():
		if (vr2.get() == 0):
			getIndexes()
			a,b = ffunc.getData(i, 0, var.get())
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
		pd.DataFrame(c).to_csv(asksaveasfilename(filetypes=[("Comma-separated Values", "*.csv")]), header = None, index = None, na_rep = "NaN")
		tk.Label(window, text = "Done").grid(row = 3, column = 1, columnspan = 2)
	# POST-CONDITION
	#	File is saved in csv format, after user-has been prompted for a name.

	tk.Button(window, text = 'Save', command = saveCSV).grid(row = 10, column = 1)
# POST-CONDITION
#	A pop-up window for CSV saving is created, with the option of filtering using a shapefile.
#	A button is created and placed, which can be used to save the file.