import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilenames

import file_functions as ffunc
import gui_functions as gfunc
import plot_functions as pfunc
import gl_vars

gl_vars.root = tk.Tk()
filenames = askopenfilenames(filetypes=[("NetCDF Files", "*.nc")])

#Add function here to make multisets.
# Multiset <- 

gl_vars.data = ffunc.openNETCDF(filenames)

gl_vars.root.title('NetCDF file reader')

gl_vars.nb = ttk.Notebook(gl_vars.root)

file_names = [a.split('/')[-1] for a in filenames]
gfunc.addPages(file_names)
gfunc.fillPages()
for i in gl_vars.chk_var_list1:
	for j in i:
		j.trace("w", gfunc.trig)

gl_vars.root.mainloop()

