import tkinter as tk
from tkinter.filedialog import askopenfilenames
from tkinter import ttk
import gui_functions as gfunc
import file_functions as ffunc
import plot_functions as pfunc
import config

config.root = tk.Tk()
filenames = askopenfilenames(filetypes=[("NetCDF Files", "*.nc")])

#Add function here to make multisets.
# Multiset <- 

config.data = ffunc.openNETCDF(filenames)

config.root.title('NetCDF file reader')

config.nb = ttk.Notebook(config.root)

gfunc.addPages(filenames)
gfunc.fillPages()
for i in config.chk_var_list1:
	for j in i:
		j.trace("w", gfunc.trig)

config.root.mainloop()

