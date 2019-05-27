#File containing functions
import numpy as np

def getInput(name, range_l,range_u):
	print 'Which '+name+' would you like to query?\nPlease enter a value between '+str(range_l)+' and '+str(range_u)
	t = float(raw_input())
	if (t<range_l):
		t = range_l
	if (t > range_u):
		t = range_u
	return t

def getRange(name, range_l, range_u):
	x = True
	while (x):
		print 'Enter lower bound and upper bound of '+name+' separated by a space.\nMaximum range allowed is from '+str(range_l)+ ' to '+ str(range_u)
		t = [float(a) for a in raw_input().split(' ')]
		if (len(t) != 2 or t[1] <= t[0]):
			print 'Enter exactly two space-separated values. Lower first, and then higher'
		else:
			x = False
	if (t[0] < range_l):
		t[0] = range_l
	if (t[1] > range_u):
		t[1] = range_u
	return t

def getDateRange(year_min, year_max):
	print 'Enter starting year and month in mm yyyy'
	s = [int(a) for a in raw_input().split(' ')]
	if(s[0] < 1):
		s[0] = 1
	if(s[0] > 12):
		s[0] = 12
	if (s[1] < year_min):
		s[1] = year_min
	if (s[1] > year_max):
		s[1] = year_max
	print 'Enter ending year and month in mm yyyy'
	t = [int(a) for a in raw_input().split(' ')]
	if (t[0] < 1):
		t[0] = 1
	if (t[0] > 12):
		t[0] = 12
	if (t[1] < year_min):
		t[1] = year_min
	if (t[1] > year_max):
		t[1] = year_max
	return s+t


