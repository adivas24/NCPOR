import sys
import re
from datetime import datetime
from datetime import timedelta
import numpy as np

def num_conv(number):
	try:
		return int(number)
	except:
		try:
			return float(number)
		except:
			return number


filename = sys.argv[1]
f = open(filename, "r")
all_text = f.read()
line_data = all_text.split('\n')
format_line = None
firstline = None
fin_1 = False
fin_2 = False
for i in line_data:
	if(i.startswith("Date") and not fin_1):
		format_line = i
		fin_1 = True

if (format_line is None):
	print("No format line found. Please ensure that your format line begins with the word Date")
headers = [x[:-1] for x in format_line.rstrip().split(' ')]

date_format = re.search('[(](.*)[)]',headers[0]).group(1).replace('yyyy','%Y').replace('MM','%m').replace('dd','%d')
time_format = re.search('[(](.*)[)]',headers[1]).group(1).replace('hh','%H').replace('mm','%M').replace('ss','%S')
data = [x.split(' ') for x in re.findall("^[1-9][0-9][0-9][0-9]/[0-9][0-9]/[1-3][0-9].*",all_text,re.MULTILINE)]
ind = 0
for obj in data:
	obj[0] =  datetime.strptime(data[ind][0]+data[ind][1],date_format+time_format)
	del obj[1]
	for i in range(1,len(obj)):
		obj[i] = num_conv(obj[i])
	ind = ind + 1

time_interval = timedelta(minutes=10)
curr_time = data[0][0]

curr_array = [data[0][1:]]
curr_arr_data = data[0][1:]
no_of_data = len(curr_arr_data)

for obj in data[1:]:
	if(obj[0]<curr_time+time_interval):
		curr_array.append(obj[1:])
		for i in range(no_of_data):
			curr_arr_data[i] = curr_arr_data[i]+obj[1:][i]
	else:
		#print(curr_array)
		#print(curr_arr_data)
		#print('\n\n\n')
		curr_arr_data = obj[1:]
		curr_time = curr_time+time_interval
		curr_array = [obj[1:]]
