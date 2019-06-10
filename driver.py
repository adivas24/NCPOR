import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilenames

import file_functions as ffunc
import gui_functions as gfunc
import plot_functions as pfunc
import gl_vars

gl_vars.root = tk.Tk()
gl_vars.root.title('NetCDF file reader')
filenames = askopenfilenames(filetypes=[("NetCDF Files", "*.nc")])


gl_vars.data = ffunc.openNETCDF(filenames)
#Add function here to make multisets.
file_names = [a.split('/')[-1] for a in filenames]
gfunc.getMultiSets(file_names)


#print(file_names)


gl_vars.root.mainloop()

