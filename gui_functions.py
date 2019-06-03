
import tkinter as tk
from tkinter import ttk
import xarray as xr
import config
#from driver import root

def addPages(filenames, nb):
	config.pages = [ttk.Frame(nb) for i in range(len(filenames))]
	for i in range(len(filenames)):
		nb.add(config.pages[i], text = filenames[i])
	nb.grid()
	return config.pages

def trig(event,b,c):
	i = int(event[-1])
	n1 = int(event[4])
	config.spn_box_list[i][2*n1].grid(row = 5+n1, column = 1)
	if (config.chk_var_list[i][n1].get() == 0):
		config.spn_box_list[i][2*n1+1].grid_forget()
	else:
		config.spn_box_list[i][2*n1+1].grid(row = 5+n1, column = 2)
	
def fillPages(pages, xr_dataSet):
	chk_var_array = [None for x in range(len(pages))]
	spinbox_master = [None for x in range(len(pages))]
	for i in range(len(pages)):
		dimension_list = list(xr_dataSet[i].coords.keys())
		chk_var_array[i] = [None for k in range(len(dimension_list))]
		spinbox_master[i] = [tk.Spinbox(pages[i]) for b in range(len(dimension_list)*2)]
		n1 = 0
		for j in dimension_list:	
			createSelRow(pages[i], j, n1, chk_var_array[i], i)
			createSelBox(pages[i], j, n1, spinbox_master[i], list(xr_dataSet[i][j].values))
			n1 += 1
	return chk_var_array,spinbox_master


def createSelRow(page, name, num, chk_var, ind):
	tk.Label(page, text = name).grid(row = num, column = 0)
	chk_var[num] = tk.IntVar(page, name = "var_"+str(num)+ "_" + str(ind))
	r1 = tk.Radiobutton(page, text = 'Single', variable = chk_var[num], value = 0)
	r1.grid(row = num, column = 1)
	r1.deselect()
	r2 = tk.Radiobutton(page, text = 'Range', variable = chk_var[num], value = 1)
	r2.grid(row = num, column = 2)
	r2.deselect()

def createSelBox(page, name, num, spn_box_list, value_list):
	tk.Label(page, text = name).grid(row = num+5, column = 0)
	spn_box_list[2*num].configure(values=value_list)
	spn_box_list[2*num+1].configure(values=value_list)

