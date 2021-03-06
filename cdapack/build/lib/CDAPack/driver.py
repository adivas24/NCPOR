"""This is the driver script. It is the file that needs to be run to start the program.
It contains some initialisations and function calls.

"""

if __name__ == '__main__':
	import tkinter as tk
	from tkinter import ttk
	from tkinter.filedialog import askopenfilenames
	# The tkinter library family is used to create various widgets for the GUI.

	import file_functions as ffunc
	import gui_functions as gfunc
	import plot_functions as pfunc
	import gl_vars
	# These are python files in the same directory which contain relevant functions. Although, not all have directly been used here, all have been imported.

	gl_vars.root = tk.Tk()
	# Creation of the main tkinter window and starting the tcl/tk interpreter and storing the object reference in the variable present in gl_vars.py.

	gl_vars.root.title('NetCDF file reader')
	# Sets the title for the window. Later can be replaced by the actual name of the software.

	filenames = askopenfilenames(filetypes=[("NetCDF Files", "*.nc")])
	try:
		temp= filenames[0]
	except:
		gl_vars.root.destroy()
		exit()
	# This tkinter function creates a pop-up window through which the user can select multiple .nc files. filenames, contains the list of the names (with complete paths) stored in the form of strings, selected by the user.
	# If no file is selected, the program terminates.

	gl_vars.data = ffunc.openNETCDF(filenames)
	# This gets the data from the NETCDF files by utilising the function defined in file_functions.py. It returns a list of xarray Datasets, each corresponding to one of the .nc files selected.

	file_names = [a.split('/')[-1] for a in filenames]
	# Slicing the names so that they contains only the filename, and not the entire path.

	gfunc.getMultiSets(file_names)
	# This function prompts the user to select files which whose data is part of the same series, allowing queries whose timelines range across different files.
	# Further, in the pop-up window, a button is created which, when pressed, will create the GUI. 

	gl_vars.root.mainloop()
	# This keeps the tkinter widgets active.

	for a in list(gl_vars.data.values()):
		a.close()
	#Cleanup. Closing files before end of program.