import sys
import re
from datetime import datetime
from datetime import timedelta

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

#print(all_text)
data = [x.split(',') for x in re.findall("^[0-3][0-9]/[0-1][0-9]/[1-9][0-9][0-9][0-9].*",all_text,re.MULTILINE)]
date_time_format = "%d/%m/%Y %H:%M:%S"
#print(data)

for obj in data:
	#print(obj[0])
	obj[0] =  datetime.strptime(obj[0],date_time_format)
	for i in range(1,len(obj)):
		obj[i] = num_conv(obj[i].strip())
time_interval = timedelta(minutes=2)
curr_time = data[0][0]

curr_array = [data[0]]
curr_arr_data = data[0][1:]
no_of_data = len(curr_arr_data)

for obj in data[1:]:
	if(obj[0]<curr_time+time_interval):
		curr_array.append(obj)
		try:
			for i in range(no_of_data):
				curr_arr_data[i] = curr_arr_data[i]+obj[1:][i]
		except:
			del curr_array[-1]
	else:
		#print(obj[0], curr_time+time_interval, obj[0]<curr_time+time_interval)
		print(curr_time+time_interval)
		while(obj[0]>=curr_time+time_interval):
			curr_time = curr_time+time_interval
		curr_arr_data = obj[1:]
		print(curr_array)
		print(curr_arr_data)
		print('\n\n\n')
		curr_array = [obj]

print(curr_array)
print(curr_arr_data)
