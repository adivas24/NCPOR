# NCPOR
Summer Project at NCPOR under Dr. Rohit Srivastav

# Title
Development of a climate data analysis package in Python

## Author
Aditya Vasudevan, B.E. (Hons) in Computer Science, BITS Pilani, Pilani campus, class of 2021.
Contact: f20170175@pilani.bits-pilani.ac.in

# Description

## Motivation
The NETCDF file format is one of the most widely used formats for storing data gathered by satellites. Large repositories of online data, regarding wind velocity, air temperature, humidity and a number of other factors are available freely online. However, NETCDF files (.nc files) cannot be opened using a simple text editor, or normally used software like MS Excel. While some software is available on the internet (most notably the nco, or Panoply by NASA), they are limited in terms of their features and applications. Hence, under the guidance of Dr. Rohit Srivastava (Scientist at National Centre for Polar and Ocean Research, Goa, India), we are creating a Python package which will contain the features that we feel are missing in the available software, while incorporating the existing features.
Python was chosen as the language as it is rather versatile and contains a number of libraries useful for retrieving, manipulating and representing data. Some libraries used in this project include, numpy, xarray, rasterio, fiona, and Affine. Tkinter has been used to create the graphical user interface.

## Objectives
To develop a Python package which will be able to do the following:
* Read NETCDF files chosen by a user through the GUI.
* From the opened NETCDF file, generate an interface in which the user can select specific dimension values (or ranges) and retrieve specific data from the files.
* Give the user the ability to select which input variables shuld be single points, which should be ranges, and to choose the output variables (if more than one are available)
* In case data is distributed over a number of files, the user should have the ability to combine them and allow queries ranging across files.
* Calculate the mean and standard deviation for selected data, which may span over latitudes, longitudes or time periods.
* Export the data to a comma-separated values (.csv) file which can then be opened and manipulated through Excel of a shell script.
* Plot the data in an interactive chloropleth map, or graph the data as it changes over time.
* Give the user the ability to change various parameters of the data plotted including the map projections, colours used, and zoom level.
* Integrate the above features with the ability to use a SHAPEFILE (.shp) as a filter or mask.
* Shapefile data should be able to mask, the displayed data (restricted by a given lat-lon-time range), data to be exported to a CSV or plotted on a map.
* All the above functions should be integrated within a user-friendly interface.

## Details
The project files have been written in Python3. The package currently contains the following files:
1. README.md
Markdown file containing data about the project.
2. TODO.txt
Text file containing a list of things left to do. Also contains the bugs that need to be resolved.
3. driver.py
Python file containing the main bits of code which initialise the program through function calls.
4. gl_vars.py
Python file containing a list of global variables used throughout the project along with descriptions of their uses and locations of initializations.
5. file_functions.py
Python file containing functions pertaining to reading data from files (both .nc and .shp files) and manipulating them to a format that can be processed further.
6. plot_functions.py
Python file containing functions used to plot maps and graphs using cartopy, based on matplotlib.
7. gui_function.py
Python file contaiing functions which are used to create the GUI. Since a large part of the GUI is based on the content of the NETCDF file, its functions are closely linked to the ones on file_functions.py

This is only a brief description of the contents of each file. Each of them individually has been documented extensively (largely over-documented, in fact) and descriptions of functions and their working can be read individually in each file.

# Usage
## 1. Requirements
The code has been written in Python3 (more specifically, 3.7) and hence all packages correspond to those versions. All of them have been installed on the machine of the developer in June 2019, and hence if functions have changed since, they may require updating in the code.
The following Python packages (with currently used versions) are required:
1. xarray (0.12.1) 
2. numpy (1.16.2)
3. pandas (0.24.2)
4. geopandas (0.5.0)
5. Fiona (1.8.6)
6. shapely (1.6.4.post1)
7. rasterio (1.0.23)
8. affine (2.2.2)
9. Cartopy (0.16.0)
10. matplotlib (3.0.3)
11. tk (8.6.8)
12. netCDF4 (1.4.2)

## 2. Installation
To install the above packages, I used conda, equivalently, pip can be used.
'''
pip3 install ...
'''
or 
'''
conda install ...
'''
 are the general syntaxes that can be used to install most packages. I would recommend using online resources until I can create a requirements.txt or a script which can do it for the user.

## 3. Starting
Once all the above packages have been installed, go to the directory containing the code files and execute the following in your commandline/ terminal
'''python3
python3  driver.py
''' 
The GUI interface should direct you through the remainder of the steps. At a later stage, I'll add screenshots and GIFs explaining the process in detail.

# Project Status
Currently the project is still in a development stage. The code currently can access data from selected ranges, plot maps from a specific instant of time, and export data to CSV. A detailed feature list and how to will be updated on this page in the future. For exact features currently been worked on check the TODO.txt.

# Features
(Incomplete)