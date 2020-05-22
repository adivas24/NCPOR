# NCPOR
Summer Project at NCPOR under the guidance of Dr. Rohit Srivastava

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
3. file_functions.py
Python file containing functions pertaining to reading data from files (both .nc and .shp files) and manipulating them to a format that can be processed further.
4. plot_functions.py
Python file containing functions used to plot maps and graphs using cartopy, based on matplotlib.
5. gui_function.py
Python file contaiing functions which are used to create the GUI. Since a large part of the GUI is based on the content of the NETCDF file, its functions are closely linked to the ones on file_functions.py
6. __init__.py
File that makes this directory a package. Currently empty.
7. __main__.py
File that allows the package to be run directly.
8. cdapack.py
Wrapper that can be executed to run the program. 

This is only a brief description of the contents of each file. Each of them individually has been (or will be) documented extensively (largely over-documented, in fact) and descriptions of functions and their working can be read individually in each file.

# Usage
## 1. Requirements
The code has been written in Python3 (more specifically, 3.7) and hence all packages correspond to those versions. All of them have been installed on the machine of the developer in June 2019, and hence if functions have changed since, they may require updating in the code.
The following Python packages (with currently used versions) are required:
1. xarray (0.12.1) 
2. numpy (1.16.2)
3. pandas (0.24.2)
4. geopandas (0.5.0)
6. shapely (1.6.4.post1)
7. rasterio (1.0.23)
8. affine (2.2.2)
9. Cartopy (0.16.0)
10. matplotlib (3.0.3)
11. tk (8.6.8)
12. netCDF4 (1.4.2)
These libraries may often have internal dependencies, which need to be installed.

## 2. Installation
To install the above packages, I used conda, equivalently, pip can be used. Although for Cartopy, I would recommend using either conda or building from source. pip tends to fail, while installing Cartopy.
'''
pip3 install ...
'''
or 
'''
conda install ...
'''
 are the general syntaxes that can be used to install most packages. I would recommend using online resources until I can create a script which can do it for the user.

## 3. Starting
Once all the above packages have been installed, go to the correct directory and execute:
'''
python3  cdapack.py
''' 
(from the directory containing cdapack.py)
or
'''
python3 -m cdapack
'''
(from the directory that contains the package.)
or 
'''
cdapack
'''
(in any environment where the package has been successfully installed)
The GUI interface should direct you through the remainder of the steps. At a later stage, I'll add screenshots and GIFs explaining the process in detail.

# Project Status
Currently the project is still in a development stage. The code currently can access data from selected ranges, plot maps from a specific instant of time, and export data to CSV. A detailed feature list and how to will be updated on this page in the future. For exact features currently been worked on check the TODO.txt.

# Using the application
On running, a pop-up window prompts the user to select NetCDF file(s).
On selecting the files, a window allows the user to combine multiple files into a single data array and rename the newly formed array.
Once ‘Done’ button has been clicked, the main window is created. In this window, a tapped pages format has been used with each dataset is associated with a ‘page’. Different features can be accessed from this window by using the options in the menu. The ‘Close’ button will close all open Tkinter windows.

# Features
This section describes the various things that can be done from the main window.

Retrieving data

In the main window, the user can decide whether a single point or a range of dimensions is given as input. Once input and output variables are selected, pressing the ‘Retrieve Data’ button results in the selected dimensions being displayed in the left text field and the output data, along with the mean and standard deviation is displayed in the right text field.
If the ‘Use Shapefile’ checkbox has been selected, before displaying the data a pop-up window asks the user to select a shapefile and a specific location from the shapefile. Once the ‘Confirm’ button is pressed, the masked data is displayed. All fields not in the selected lat-lon boundaries, but not within the shapefile region get replaced by nan (not a number).

Plotting Geospatial Maps

If the ‘Plot’ option is selected from the menu bar, a pop-up window allows the user to choose between four different options:

Map Plot (fixed time)

If this option is selected, the user can select the variable, time and projection type. Clicking on the ‘Confirm’ button opens up a plot window
If the Shapefile checkbox is selected, a pop-up window allows the user to select a Shapefile, and on the main window adds a combo box where the user can select the specific location.

Animated Map
If this option is selected the user can select the variable, time  ranges (inclusive), projection type. The user can also select options to only display, only save, or do both. At the time of writing, shapefile masked data could not be used for animated plots. When ‘Confirm’ is clicked, the plot is displayed and/or saved depending on the user’s input. The user can also decide the frame rate and the name of the gif.

Vector Plot

If this option is selected, the program searches for ‘u10’ and ‘v10’ parameters (this can later be generalised to allow different variable names, as well) in the dataset and generates a vector plot using the matplotlib quiver function. Like the standard map, users have the ability to select the projection type and time period and have the option to use a Shapefile as a mask. 

Animated Vector Plot

Like the other animation utility, selecting this option will allow the user to select the time range and decide whether to display and/or save the animation. The internal working of this function differs from that of the other animation function. Due to the use of the quiver function, the same function used for animation cannot be used in this case. Each image is first generated as a PNG, which is then combined to form a gif by an embedded terminal command. Hence, this utility, may not be cross-platform in its current form.

Exporting to CSV

When the user selects the ‘Export’ option from the menu bar, a pop-up window is generated, which allows the students to choose a specific variable and the types of bounds they can apply to the data. If ‘Use bounds specified in previous window’ is selected, then the time range selection in the export window is ignored and all bounds are taken from the main window. This option will currently throw exceptions, if proper ranges for latitude and longitude are not given. If the ‘Apply no bounds’ option is selected, it will consider the entire dataset in question, limited by the time range specified in this window. In both cases, a Shapefile filter can be used to mask the data. When the ‘Confirm’ button is pressed, the user is prompted to give a name for the saved file(s). A different CSV file is generated for each time period and the user-given name is appended by the date before saving.


Calculating Statistics

The user can access this feature by clicking on the ‘Calculator’ option which appears on selecting the ‘Statistics’ item in the menu. The first option presented to the user is to select whether year-wise or month-wise statistics are to be calculated. From the array of checkboxes of years (or months), any combination can be chosen. When choosing in ‘month’ mode, the user also has the option to select a set of months or years directly, by selecting the appropriate checkbox. The user can then select a type of filter, and the variables that need to be displayed. While the functionality of the ‘year’ mode can be completely done in the ‘month’ mode, it is advisable to use the former as it is slightly faster.

No filter

If ‘No filter’ is selected, no additional selections are required. Clicking on ‘Get Statistics’ button will result in the mean, standard deviation, maximum and minimum being displayed for each variable in the text field.

Lat-Lon bounds
If ‘Lat-Lon bounds’ is selected, the user can then select the latitude and longitude ranges through spin-boxes. Clicking on ‘Get Statistics’ button will result in the statistics being displayed for each selected variable in the text field.

Shapefile

If ‘Shapefile’ is selected, the user is given the option to select a shapefile through a pop-up window and then a specific location from the geometries present. Once selected, clicking on the ‘Get Statistics’ button will result in the statistics being displayed for each variable in the text field. Since using a shapefile is a time-intensive task, attempting to get statistics in this manner, across large time periods, will take a long time to compute.

Plotting variable-time line graphs

To plot line graphs of any variable(s) against time, the user needs to select ‘Time-series’ option under the ‘Statistics’ item in the menu. In the pop-up window, the user can then select the start time, end time, time interval (in number of years/months/days), the variables to be plotted and the type of filter. The time range (from start time to end time) is divided into time interval-sized segments and the mean of all the data points in each segment is then used as the y-coordinate for that time interval in the graph. The y-coordinate of any point on the graph is the mean of values from the time interval which starts at its x-coordinate. The graphs plotted are error plots, with the standard deviations being used as the vertical error bars.

No filter

If ‘No filter’ is selected, no additional selections are needed. Clicking on the ‘Plot’ button will result in a matplotlib window with the graph being created.
 
Lat-lon bounds

If ‘Lat-lon bounds’ is selected, the user is prompted to provide latitude and longitude ranges through spin-boxes. Clicking on the ‘Plot’ button will open a matplotlib window with the graph.

Shapefile

If ‘Shapefile’ is selected, a pop-up window prompts the user to select a Shapefile and creates a combo-box from which the user can then select the location. On selecting the same, clicking on the ‘Plot’ button will open a matplotlib window with the required graph. Since the shapefile mask needs to be done on every dataset in the interval, creation of this graph is a time-consuming process.
