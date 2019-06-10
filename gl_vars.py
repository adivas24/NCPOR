# gl_vars.py

# This file stores the variables which need to be accessed and modified across different files. All of them have been initialised to NULL values as they are specifically initialised by functions called in driver.py


data = []
# data is a list containing the data extracted from the NetCDF files opened using xarray.
# Each element in list corresponds to one of the .nc files opened.
# Each element is an xarray DataSet.
# It is initialised in driver.py after calling the function openNETCDF, defined in file_functions.py

root = None
# root is the tkinter master window. All other widgets are hosted on this main window.
# It initialises a tcl/tk interpreter. Read about its importance here: https://stackoverflow.com/questions/24729119/what-does-calling-tk-actually-do 
# It is initialised in driver.py through a direct constructor call.

nb = None
# nb is the Notebook widget defined in the themed tkinter widgets library, ttk. Since a tabbed window format is being used, a notebook to hold pages is created.
# It is the container for all pages as well as widgets that are commonly used by all of the pages, like the buttons for retrieving data, plotting, exporting and closing.
# It is initialised in driver.py through a direct constructor call. 

pages = []
# pages is a list containing a ttk Frame widget corresponding to each .nc file added. Each page is one 'tab' of the tabbed window format that is being used.
# It is the container for all widgets specific to the page, like the input boxes and selection options.
# It is initialised by the function addPages, called in driver.py, defined in gui_functions.py.

chk_var_list1 = []
# chk_var_list1 is a list containing lists of IntVars which are the variables associated with the radio buttons for each input variable.
# Each element is a list corresponding to the radio buttons on a page. It is a jagged 2-d list.
# It is initialised by the function fillPages, called in driver.py, defined in gui_functions.py. The initialisation is in two steps. First a series of null lists corresponding to each page is created. Subsequently, each list is initialised with a variable.

chk_var_list2 = []
# chk_var_list2 is a list containing lists of IntVars which are the variables associated with the checkboxes for each output variable.
# Each element is a list corresponding to the check-box(es) on a page. It is a jagged 2-d list.
# It is initialised by the function fillPages, called in driver.py, defined in gui_functions.py. The initialisation is in two steps. First a series of null lists corresponding to each page is created. Subsequently, each list is initialised with a variable.

chk_var_list3 = []


spn_box_list = []
# spn_box_list is a list containing lists of tkinter Spinboxes used to select the input variables for retrieving data. Two spinboxes for each input variable.
# Each element is a list corresponding to the spinboxes on a page. It is a jagged 2-d list.
# It is initialised by the function fillPages, called in driver.py, defined in gui_functions.py. The initialisation is in two steps. First a series of null lists corresponding to each page is created. Subsequently, each list is initialised with a spinbox constructor.

selBox = []
# selBox is a list containing the tkinter Text widgets, one for each page, used to display the selected variable ranges.
# Each element is a tkinter Text widget. This design should probably be changed to a single text field across all pages.
# It is initialised by the function fillPages, called in driver.py, defined in gui_functions.py. The boxes are actually initialised by the function createOPBox, also defined in gui_functions.py.

opBox = []
# opBox is a list containing the tkinter Text widgets, one for each page, used to display the output data.
# Each element is a tkinter Text widget. This design should probably be changed to a single text field across all pages.
# It is initialised by the function fillPages, called in driver.py, defined in gui_functions.py. The boxes are actually initialised by the function createOPBox, also defined in gui_functions.py.

messages = []
# messages is a list containing the variable limits selected by the user at the time of pressing the 'Retrieve data' button.
# Each element is a list of size two containing the limits of the variables read as strings from the spinboxes.
# It is initialised in the function retrieveData defined in gui_functions.py, which is called whenever the button is pressed.

outVar = []
# outVar is a list containing the status of each checkbox (corresponding to each output variable). It is used to determine which outputs are to be included in the listed output text.
# Each element is an integer corresponding to the status of the checkbox, 0 meaning unselected and 1 meaning selected.
# It is initialised in the function retrieveData defined in gui_functions.py, which is called whenever the button is pressed. 

output = None