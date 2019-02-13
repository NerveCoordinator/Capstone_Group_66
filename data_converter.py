#usr/bin/python
import csv
import time
import math
import string

print("This program is meant to change the csv file to output for training predictor")
print("Remember to include .csv in file name")
infile  = input("Input file name: ")
outfile = input("Output file name: ")

def printcsvfile(infile):
	with open(infile) as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=',')
		line_count = 0
		for row in csv_reader:
			if line_count == 0:
				print(f'Column names are {", ".join(row)}')
			if line_count != 0:
				print(f'{", ". join(row)}')
			line_count += 1
		print(f'Processed {line_count} lines.')

def convert_Norcom(infile, outfile):
	with open(infile) as csv_file:
		formated = open(outfile, "w") 
		fieldnames = ['Priority', 'Emergency_num', 'Hospital_num', 'Distance_Away', 'Since_Epoch',
			'Time_to_inc', 'Time_to_dest', 'Year', 'Year_day', 'Month', 'Week_day', 'Hour']
		writer = csv.writer(formated, delimiter=',', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
		csv_reader = csv.reader(csv_file, delimiter=',')
		line_count = 0
		types_of_emergency = []
		names_of_hospitals = []
		writer.writerow(fieldnames)
		for row in csv_reader:
			if line_count > 0:

				#Distance until destiantion
				lat1 = row[3]
				lat2 = row[10]
				lon1 = row[4]
				lon2 = row[11]
				distance_to_incident = get_distance_from_coordinates(lat1, lat2, lon1, lon2)


				#reference list of emergencies/hospitals and assigns a number to them
				emergency_num  = verify_in_list_or_append([row[5]], types_of_emergency)
				hospitals_num  = verify_in_list_or_append([row[9]], names_of_hospitals)

				#time since epoch
				try:
					time_first_assigned  = time.mktime(convert_Norcom_date([row[7]]))				
					time_depart_scene    = time.mktime(convert_Norcom_date([row[12]]))
					time_arrived_dest    = time.mktime(convert_Norcom_date([row[13]]))
					time_cleared_dest    = time.mktime(convert_Norcom_date([row[14]]))
				except:
					time_first_assigned = None
					time_depart_scene 	= None
					time_arrived_dest 	= None
					time_cleared_dest 	= None

				#derrived time values
				if(time_first_assigned != None):
					time_travled_to   = time_depart_scene - time_first_assigned 
					time_travled_from = time_arrived_dest - time_depart_scene 
					if((time_travled_to > 10000) or (time_travled_from > 10000)):
						time_travled_to   = None
						time_travled_from = None
				else:
					time_travled_to   = None
					time_travled_from = None

				#date details
				date = convert_Norcom_date([row[7]])
				year = date.tm_year
				yday = date.tm_yday
				mday = date.tm_mday
				wday = date.tm_wday
				hour = date.tm_hour

				writer.writerow([row[6], emergency_num, hospitals_num, distance_to_incident,
					time_first_assigned, time_travled_to, time_travled_from, year, yday, mday, wday, hour]) 
			line_count += 1


		print("The types of emergency: ")
		print(types_of_emergency)
		print("The names of hospitals: ")
		print(names_of_hospitals)
		print("Done")

def get_distance_from_coordinates(lat1, lat2, lon1, lon2):
	try:
		vala = pow((float(lat1) - float(lat2)), 2)
		valb = pow((float(lon1) - float(lon2)), 2)
		valc = (math.sqrt(vala + valb))
		valc * 69 # Conversion to miles from lat/lon
		if(valc > 100):
			return None
		else:
			return valc
	except:
		return None

def verify_in_list_or_append(string_to_check, list_of_strings):
	i = 0
	for x in list_of_strings:
		if x == string_to_check:
			return i
		i += 1	
	list_of_strings.append(string_to_check)
	return len(list_of_strings) - 1	


def convert_Norcom_date(original_date):
	try: 
		return(time.strptime(original_date[0], "%m/%d/%Y %H:%M"))
	except:
		return None

convert_Norcom(infile, outfile)

	