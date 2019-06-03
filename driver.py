import tkinter as tk
from tkinter.filedialog import askopenfilenames
from tkinter import ttk
import gui_functions as gfunc
import file_functions as ffunc
import config

filenames = askopenfilenames(filetypes=[("NetCDF Files", "*.nc")])

#Add function here to make multisets.
# Multiset <- 

xr_dataSetArr = ffunc.openNETCDF(filenames)

root = tk.Tk()

root.title('NetCDF file reader')

nb = ttk.Notebook(root)

config.pages = gfunc.addPages(filenames, nb)
(config.chk_var_list,config.spn_box_list) = gfunc.fillPages(config.pages, xr_dataSetArr)
for i in config.chk_var_list:
	for j in i:
		j.trace("w", gfunc.trig)
root.mainloop()

