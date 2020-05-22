# gui_functions.py #


from . import file_functions as ffunc
from . import plot_functions as pfunc

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

global data, root, nb, chk_var_list1, chk_var_list2, chk_var_list3, spn_box_list, selBox, opBox

def main():
	global root, data
	root = tk.Tk()
	# Creation of the main tkinter window and starting the tcl/tk interpreter and storing the object reference in the variable present in gl_vars.py.

	root.title('Climate Data Analysis Pack 0.0.4')
	# Sets the title for the window. Later can be replaced by the actual name of the software.

	filenames = askopenfilenames(filetypes=[("NetCDF Files", "*.nc")])
	if (len(filenames) < 1):
		root.destroy()
		exit()
	# This tkinter function creates a pop-up window through which the user can select multiple .nc files. filenames, contains the list of the names (with complete paths) stored in the form of strings, selected by the user.
	# If no file is selected, the program terminates.
	data = ffunc.openNETCDF(filenames)
	# This gets the data from the NETCDF files by utilising the function defined in file_functions.py. It returns a list of xarray Datasets, each corresponding to one of the .nc files selected.

	filenames = [name.split('/')[-1] for name in filenames]
	# Slicing the names so that they contains only the filename, and not the entire path.

	getMultiSets(filenames)
	# This function prompts the user to select files which whose data is part of the same series, allowing queries whose timelines range across different files.
	# Further, in the pop-up window, a button is created which, when pressed, will create the GUI. 

	root.mainloop()
	# This keeps the tkinter widgets active.

	for dataset in list(data.values()):
		dataset.close()
	#Cleanup. Closing files before end of program.


def getMultiSets(filenames):
	
	global root, data, chk_var_list1
	
	l1 = tk.Label(root, text = "Tick the ones you want to combine:")
	l1.grid(row = 0, column  = 0,ipadx = 10, pady = 10, columnspan = 5, sticky = tk.W)
	
	file_chk_vars = dict()
	chk_btn_dict = dict()

	newName = tk.StringVar(root)
	newName.set("newFile")
	
	i = 1
	for filename in filenames:
		file_chk_vars[filename] = tk.BooleanVar(root)
		chk_btn_dict[filename] = tk.Checkbutton(root, text = filename, variable = file_chk_vars[filename])
		chk_btn_dict[filename].grid(row = i, column = 0, columnspan = 5, ipadx = 20, sticky = tk.W, pady = 3)
		i += 1
	
	l2 = tk.Label(root, text='Name for new set: ')
	l2.grid(row = i, column = 0, pady = 8, columnspan = 2, sticky = tk.W, padx = 10)
	
	filenames2 = filenames
	
	text = tk.Entry(root, textvariable = newName)
	text.grid(row = i, column = 2, pady = 8, columnspan = 3, sticky = tk.W)
	
	b1 = tk.Button(root, text = 'Combine')
	b1.grid(row = i+1, column = 0, sticky = tk.W+tk.E)
	
	b2 = tk.Button(root, text = 'Done')
	b2.grid(row = i+1, column = 4, sticky = tk.W+tk.E)

	def combine_files():
		
		nonlocal filenames2, l1, l2, b1,  b2, text, chk_btn_dict
		global data
		
		indxs = [filename for filename in filenames if file_chk_vars[filename].get()]
		if(len(indxs) > 1):
			data,filenames2 = ffunc.combineFiles(data, filenames, indxs, newName.get())
			l1.destroy()
			l2.destroy()
			b1.destroy()
			b2.destroy()
			text.destroy()
			for btn in chk_btn_dict.values():
				btn.destroy()
			getMultiSets(filenames2)

	def createGUI():

		nonlocal l1, l2,  b2, b1, text, chk_btn_dict
		global nb, root, chk_var_list1
		
		l1.destroy()
		l2.destroy()
		b1.destroy()
		b2.destroy()
		text.destroy()
		for btn in chk_btn_dict.values():
			btn.destroy()
		
		nb = ttk.Notebook(root)
		
		menu = tk.Menu(root)
		menu.add_command(label = "Plot on Map", command = plotWindow)
		menu.add_command(label = "Export", command = exportToCSV)
		
		submenu1 = tk.Menu(root)
		submenu1.add_command(label = "Calculator", command = dataSelector)
		submenu1.add_command(label = "Time Series", command = plotGenerator)
		menu.add_cascade(label = "Statistics", menu = submenu1)

		root.config(menu=menu)
		
		pages = addPages(filenames2)
		fillPages(pages)
		
		for filename in chk_var_list1.keys():
			for dim in chk_var_list1[filename].keys():
				chk_var_list1[filename][dim].trace("w",trig)

	b1.config(command = combine_files)
	b2.config(command = createGUI)
	
	root.grid_columnconfigure(0, minsize=150)
	root.grid_columnconfigure(1, minsize=30)
	root.grid_columnconfigure(3, minsize=30)
	root.grid_columnconfigure(4, minsize=150)

def addPages(filenames):
	global nb
	pages = dict()
	for filename in filenames:
		pages[filename] = ttk.Frame(nb)
		nb.add(pages[filename], text = filename)
	nb.grid(row = 0, column = 0, columnspan=9, sticky = tk.E + tk.W, padx = 5)
	return pages

def trig(event,b,c):
	global chk_var_list1, spn_box_list 
	variable_name = event.split('$')
	dim = variable_name[2]
	filename = variable_name[1]
	row_num = int(variable_name[3])
	if (chk_var_list1[filename][dim].get() == 0):
		spn_box_list[filename][dim][1].grid_forget() 
	else:
		spn_box_list[filename][dim][1].grid(row = row_num, column = 2)
	
def fillPages(pages):

	global root, data, chk_var_list1, chk_var_list2, chk_var_list3, spn_box_list, selBox, opBox

	chk_var_list1 = dict()
	chk_var_list2 = dict()
	chk_var_list3 = dict()
	spn_box_list = dict()

	for filename in pages.keys():
		
		dimension_list = list(data[filename].coords.keys())
		variable_list = list(data[filename].data_vars.keys())
		
		dim_count = len(dimension_list)

		chk_var_list1[filename] = dict()
		chk_var_list2[filename] = dict()
		spn_box_list[filename] = dict()
		
		row_num = 0
		chk_var_list3[filename] = tk.IntVar(pages[filename])
		tk.Checkbutton(pages[filename], text = "Use SHAPEFILE", variable = chk_var_list3[filename]).grid(row = row_num, column = 10)
		
		for dim in dimension_list:	
			chk_var_list1[filename][dim] = createSelRow(pages[filename], dim, row_num, filename, row_num+dim_count)
			spn_box_list[filename][dim] = createSelBox(pages[filename],dim, row_num+dim_count, list(data[filename][dim].values))
			row_num += 1
		
		row_num+=dim_count
		
		tk.Label(pages[filename], text="Choose output variables:").grid(row = row_num+1, column = 0)
		
		col_num = 1
		for data_var in variable_list:
			chk_var_list2[filename][data_var] = createCheckBox(pages[filename],data_var, row_num+1, col_num)
			col_num += 1
	
	tk.Label(root, text="Selection:").grid(column = 1, row = 90, sticky = tk.W, padx = 5, pady = 5)
	selBox = tk.Text(root, height = 4, width = 5)
	selBox.grid(row = 90, column = 2, columnspan = 3, sticky = tk.W+tk.E+tk.N+tk.S, pady = 5, padx = 3, rowspan = 4)
	
	tk.Label(root, text="Output:").grid(column = 5, row = 90, sticky = tk.W, padx = 5, pady = 5)
	opBox = tk.Text(root, height = 4, width = 5)
	opBox.grid(row = 90, column = 6, columnspan = 3, sticky = tk.W+tk.E+tk.N+tk.S, pady = 5, padx = 3, rowspan = 4)
	
	tk.Button(root, text = 'Retrieve data', command = retrieveData).grid(row = 100, column = 1, sticky = tk.E + tk.W, pady = 5)
	tk.Button(root, text = 'Close', command = root.destroy).grid(row = 100, column = 8, sticky = tk.E+ tk.W, padx = 5, pady = 5)
	
	root.grid_columnconfigure(0, minsize=30)
	root.grid_columnconfigure(1, minsize=150)
	root.grid_columnconfigure(2, minsize=30)
	root.grid_columnconfigure(3, minsize=150)
	root.grid_columnconfigure(4, minsize=30)
	root.grid_columnconfigure(5, minsize=150)
	root.grid_columnconfigure(6, minsize=30)
	root.grid_columnconfigure(7, minsize=30)
	root.grid_columnconfigure(8, minsize=150)
	root.grid_rowconfigure(91, minsize=20)
	root.grid_rowconfigure(92, minsize=20)
	root.grid_rowconfigure(93, minsize=20)

def createSelRow(page, dim_name, row_num, filename, space):
	tk.Label(page, text = dim_name).grid(row = row_num, column = 0)
	var_radio = tk.IntVar(page, name = "var$"+filename+ "$" + dim_name + '$' + str(space))
	tk.Radiobutton(page, text = 'Single'           , variable = var_radio, value = 0).grid(row = row_num, column = 1)
	tk.Radiobutton(page, text = 'Range (Inclusive)', variable = var_radio, value = 1).grid(row = row_num, column = 2)
	return var_radio

def createSelBox(page, dim_name, row_num, value_list):
	value_list.sort()
	tk.Label(page, text = dim_name).grid(row = row_num, column = 0)
	spn_box_list = [tk.Spinbox(page, values = value_list), tk.Spinbox(page, values = value_list)]
	spn_box_list[0].grid(row = row_num, column = 1)
	return spn_box_list

def createCheckBox(page, data_var, row_num, col_num):
	data_var_var = tk.BooleanVar(page)
	tk.Checkbutton(page, text = data_var, variable = data_var_var).grid(row = row_num, column = col_num)
	return data_var_var

def getIndexes():
	global nb, chk_var_list1, chk_var_list2, data, spn_box_list
	
	filename = nb.tab(nb.select(), "text")
	messages = dict()
	outVar = dict()
	
	for dim in chk_var_list1[filename].keys():
		messages[dim] = [spn_box_list[filename][dim][0].get()]
		if(chk_var_list1[filename][dim].get()):
			messages[dim].append(spn_box_list[filename][dim][1].get())
		else:
			messages[dim].append(None)
	
	for data_var in chk_var_list2[filename].keys():
		outVar[data_var] = chk_var_list2[filename][data_var].get()
	return messages,outVar


def printMessages(o_message, s_message):
	global selBox, opBox
	selBox.delete(1.0, tk.END)
	selBox.insert(tk.INSERT, s_message)
	opBox.delete(1.0, tk.END)
	opBox.insert(tk.INSERT, o_message)

def openWindow(org):
	global root, nb, data
	filename = nb.tab(nb.select(), "text")
	dataset = data[filename]
	lon_var, lat_var = ffunc.getLatLon(dataset)
	window = tk.Toplevel(root)
	var2 = tk.IntVar(window) # shape file toggle
	var_list = list(data[filename].data_vars.keys())
	time_range = [str(pd.to_datetime(a).date()) for a in list(data[filename].variables['time'].values)]
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
	if (org == 0):
		#Map plot
		var = tk.StringVar(window) # variable selector
		varn = tk.StringVar(window) # projection selector
		varSpin1= tk.StringVar(window) #time range1
		varSpin2 = tk.StringVar(window) # time range 2
		varSave = tk.BooleanVar(window) # save file checkbutton
		varShow = tk.BooleanVar(window) # show plot checkbutton
		varSaveName = tk.StringVar(window) # newfile name
		varFrameRate = tk.StringVar(window)
		var.set(var_list[0])
		varn.set("PlateCarree")
		varFrameRate.set("150")
		tk.Label(window, text = "Select type graph:").grid(row = 1, column = 0)
		varRadio = tk.IntVar(window)
		tk.Radiobutton(window, text = 'Map plot (fixed time)', variable = varRadio, value = 0).grid(row = 2, column = 0)
		tk.Radiobutton(window, text = 'Animated map', variable = varRadio, value = 1).grid(row = 3, column = 0)
		tk.Radiobutton(window, text = 'Vector plot (if available)', variable = varRadio, value = 2).grid(row = 4, column = 0)
		tk.Radiobutton(window, text = 'Animated vector plot', variable = varRadio, value = 3).grid(row = 5, column = 0)

		proj_list = ["PlateCarree","AlbersEqualArea","AzimuthalEquidistant","EquidistantConic","LambertConformal","LambertCylindrical","Mercator","Miller","Mollweide","Orthographic","Robinson","Sinusoidal","Stereographic","TransverseMercator","UTM","InterruptedGoodeHomolosine","RotatedPole","OSGB","EuroPP","Geostationary","NearsidePerspective","EckertI","EckertII","EckertIII","EckertIV","EckertV","EckertVI","EqualEarth","Gnomonic","LambertAzimuthalEqualArea","NorthPolarStereo","OSNI","SouthPolarStereo"]
		proj_list_reduced = ["PlateCarree","AlbersEqualArea","AzimuthalEquidistant","EquidistantConic","LambertCylindrical","Miller","Mollweide","Robinson","Sinusoidal","InterruptedGoodeHomolosine","RotatedPole","EckertI","EckertII","EckertIII","EckertIV","EckertV","EckertVI","EqualEarth","NorthPolarStereo","SouthPolarStereo"]
		l1 = tk.Label(window, text = "Select variable: ")
		l2 = tk.Label(window, text = "Select time: ")
		l3 = tk.Label(window, text = "Select projection: ")
		l4 = tk.Label(window, text = "Select time range: ")
		l5 = tk.Label(window, text = ".gif")
		l6 = tk.Label(window, text = "Frame rate")
		l7 = tk.Label(window, text = "microseconds")
		om1 = tk.OptionMenu(window, var, *var_list)
		sb1 = tk.Spinbox(window, values = time_range, textvariable = varSpin1)
		sb2 = tk.Spinbox(window, values = time_range, textvariable = varSpin2)
		cb1 = ttk.Combobox(window, textvariable = varn, values = proj_list)
		chb1 = tk.Checkbutton(window, text = "Use SHP file", variable = var2)
		chb2 = tk.Checkbutton(window, text = "Savefile as", variable = varSave)
		chb3 = tk.Checkbutton(window, text = "Display plot", variable = varShow)

		ent1 = tk.Entry(window, textvariable = varSaveName)
		ent2 = tk.Entry(window, textvariable = varFrameRate)
		def plotSelect(event, a, b):
			nonlocal l1, l2, l3, l4,l5,l6,l7, om1, sb1, sb2, cb1, chb1, chb2, chb3, ent1, ent2
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
				l6.grid_forget()
				l7.grid_forget()
				ent2.grid_forget()
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
				l6.grid(row = 17, column = 0)
				ent2.grid(row = 17, column = 1)
				l7.grid(row = 17, column = 2)
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
				l6.grid_forget()
				l7.grid_forget()
				ent2.grid_forget()
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
				l6.grid(row = 17, column = 0)
				ent2.grid(row = 17, column = 1)
				l7.grid(row = 17, column = 2)
				varShow.set(1)
				varSaveName.set('default')
				# More option wrt animation to be added here.
			b1.config(command = callPlotFunction)
		

		def callPlotFunction():
			nonlocal plac_ind
			global data
			var_name = var.get()
			proj_string = varn.get()
			t1 = time_range.index(varSpin1.get())
			t2 = time_range.index(varSpin2.get())
			show = varShow.get()
			save = varSave.get()
			save_name = varSaveName.get()
			frameRate = int(varFrameRate.get())
			if(var2.get() == 1 and var3.get() != "ALL"):
				plac_ind = places.index(var3.get())
			elif(var3.get() == "ALL"):
				plac_ind = None
			org = varRadio.get()
			if (org == 0):
				xds, geometries = ffunc.getShapeData(dataset, var_name, t1, filename, plac_ind)
				pfunc.plotMapShape(proj_string, xds, lon_var, lat_var, geometries)
			elif (org == 1):
				pfunc.animation(t2-t1, proj_string,show, save, save_name,lon_var,lat_var,frameRate, ffunc.animate_aux(dataset,var_name, t1, filename, plac_ind))
			elif (org == 2):
				xds1, geometries = ffunc.getShapeData(dataset, 'u10', t1, filename, plac_ind)
				xds2, geometries = ffunc.getShapeData(dataset, 'v10', t1, filename, plac_ind)
				lon_arr = np.sort(((np.array(data[filename].coords[lon_var]) + 180) % 360) -180)
				lat_arr = np.array(data[filename].coords[lat_var])
				u_arr = np.array(xds1)
				v_arr = np.array(xds2)
				velocity = np.sqrt(u_arr*u_arr+v_arr*v_arr)
				pfunc.vectorMap(proj_string, lon_arr, lat_arr, u_arr, v_arr, velocity,varSpin1.get())
			elif (org == 3):
				getU,getV = ffunc.animate_aux(dataset,'u10',t1,filename,plac_ind), ffunc.animate_aux(dataset,'v10',t1,filename,plac_ind)
				xds1, geometries = getU(0)
				xds2, geometries = getV(0)
				lon_arr = np.sort(((np.array(dataset.coords[lon_var]) + 180) % 360) -180)
				lat_arr = np.array(dataset.coords[lat_var])
				u_arr = np.array(xds1)
				v_arr = np.array(xds2)
				velocity = np.sqrt(u_arr*u_arr+v_arr*v_arr)
				pfunc.vectorAnim(t2-t1, proj_string,show, save, save_name, getU,getV, frameRate, lon_arr,lat_arr,u_arr, v_arr, velocity, time_range)
		
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
			lon_var,lat_var = ffunc.getLatLon(dataset)
			lat_range = [str(a) for a in dataset.variables[lat_var].values]
			lon_range = [str(a) for a in dataset.variables[lon_var].values]
			t1 = time_range.index(varSpin1.get())
			t2 = time_range.index(varSpin2.get())
			time_t = [t1,t2]
			time_t.sort()
			t3 = slice(time_t[0], time_t[1]+1)
			if(varBnd.get() == 0):
				msgs,outVar = getIndexes()
				lat_range = lat_range[lat_range.index(msgs[lat_var][1]):lat_range.index(msgs[lat_var][0])+1]
				lon_range = lon_range[lon_range.index(msgs[lon_var][0]):lon_range.index(msgs[lon_var][1])+1]
				data_arr = ffunc.getData(dataset,msgs,outVar,variable = var_name)[1]
				if (filename is not None):
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
				resized_array = np.array(out)
			text = asksaveasfilename(filetypes=[("Comma-separated Values", "*.csv")]).split('.')
			index = 0
			lon_range.insert(0,'lat/lon')
			for index in range(resized_array.shape[0]):
				temp_array = np.empty((resized_array[index].shape[0],resized_array[index].shape[1]+1))
				for i in range(resized_array[index].shape[0]):
					temp_array[i][0] = lat_range[i]
					temp_array[i][1:] = resized_array[index][i]
				name = text[0]+str(time_range[t1+index])+'.'+text[1]
				pd.DataFrame(temp_array).to_csv(name, header = lon_range, index = False, na_rep = "NaN")
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
	global nb, chk_var_list3, data
	filename = nb.tab(nb.select(), "text")
	if (chk_var_list3[filename].get() == 1):
		openWindow(2)
	else:
		msgs,outVar = getIndexes()
		sel_message, output_message = ffunc.getData(data[filename], msgs,outVar)
		printMessages(output_message,sel_message)

def dataSelector():
	global root, nb, data
	window = tk.Toplevel(root)
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
	frame = tk.Frame(canvas, width=1000,height=2000)
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
	filename = nb.tab(nb.select(), "text")
	dataset = data[filename]
	tk.Label(frame, text = "Select data points by: ").grid(row = 0,column = 0)
	tk.Radiobutton(frame, variable = var_time, value = 0, text = "Year").grid(row = 0, column = 1)
	tk.Radiobutton(frame, variable = var_time, value = 1, text = "Month").grid(row = 0, column = 2)
	time_range = [pd.to_datetime(a).date() for a in list(dataset.variables['time'].values)]
	time_range.sort()
	tk.Label(frame, text = "Select filters:").grid(row = 625, column = 0)
	val_filt = tk.IntVar(frame)
	tk.Radiobutton(frame, variable = val_filt, value = 0, text = "No filters").grid(row = 626, column = 0)
	tk.Radiobutton(frame, variable = val_filt, value = 1, text = "Lat-Lon bounds").grid(row = 626, column = 1)
	tk.Radiobutton(frame, variable = val_filt, value = 2, text = "ShapeFile").grid(row = 626, column = 2)
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
	lon_var,lat_var = ffunc.getLatLon(dataset)
	lat_arr = list(dataset.variables[lat_var].values)
	lat_arr2 = [str(a) for a in lat_arr]
	lat_arr.sort()
	lon_arr = list(dataset.variables[lon_var].values)
	lon_arr2 = [str(a) for a in lon_arr]
	lon_arr.sort()
	lbl1 = tk.Label(frame, text = "Latitude Range:")
	spn_box1 = tk.Spinbox(frame, values = lat_arr)
	spn_box2 = tk.Spinbox(frame, values = lat_arr)
	lbl2 = tk.Label(frame, text = "Longitude Range:")
	spn_box3 = tk.Spinbox(frame, values = lon_arr)
	spn_box4 = tk.Spinbox(frame, values = lon_arr)
	filename = None
	lbl3 = tk.Label(frame)
	lbl4 = tk.Label(frame, text = "Select place:")
	plc_var = tk.StringVar(frame)
	cmb1 = ttk.Combobox(frame, textvariable = plc_var)
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
			lbl1.grid(row = 727, column = 0)
			spn_box1.grid(row = 727, column = 1)
			spn_box2.grid(row = 727, column = 2)
			lbl2.grid(row = 728, column = 0)
			spn_box3.grid(row = 728, column = 1)
			spn_box4.grid(row = 728, column = 2)
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
				lbl3.grid(row = 727, column = 0)
				lbl4.grid(row = 728, column = 0)
				cmb1.config(values = places2)
				cmb1.grid(row = 728, column = 1)

	val_filt.trace("w", selectFilter)



	def getStats():
		nonlocal var_var, var_arr
		var_arr = [key for key,value in var_var.items() if value.get()]
		filt = val_filt.get()
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
		if(val_filt.get() == 0):
			outdict = ffunc.getStats(dataset, year_param, chk_status, var_arr)
		elif(val_filt.get() == 1):
			lat_r = [lat_arr2.index(spn_box1.get()),lat_arr2.index(spn_box2.get())]
			lon_r = [lon_arr2.index(spn_box3.get()),lon_arr2.index(spn_box4.get())]
			lat_r.sort()
			lon_r.sort()
			outdict = ffunc.getStats(dataset, year_param, chk_status, var_arr, filt = "bounds", lat_range = slice(lat_r[0], lat_r[1]), lon_range = slice(lon_r[0], lon_r[1]))
		elif(val_filt.get() == 2):
			if(plc_var.get() == "ALL"):
				plac_ind = None
			else:
				plac_ind = places.index(plc_var.get())
			outdict = ffunc.getStats(dataset, year_param, chk_status, var_arr, filt = "shapefile", filename = filename, place = plac_ind)
		outField.delete(1.0,tk.END)
		outField.insert(tk.INSERT, ffunc.generateMessage(outdict))
	var_time.trace("w", selectGrid)
	var_time.set(0)

	b1 = tk.Button(frame, command = getStats, text = "Get statistics")
	b1.grid(row = 1000, column = 0)
	canvas.config(scrollregion = (0,0,2000,2000))

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
	global nb,data, root
	filename = nb.tab(nb.select(), "text")
	dataset = data[filename]
	window = tk.Toplevel(root)
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
		global data
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
	for a in list(data[filename].dims):
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

		variables = [(key,dataset.variables[key].attrs['units']) for key,value in var_var.items() if value.get() == 1]
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