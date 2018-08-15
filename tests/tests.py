import os
import re
import math

'''
Test flow guide:
This test flow goes through all final spice simulation results and compares the rise and fall delays with a given reference.
Its objective is making sure that:
	1) Different features in COFFE are not broken after code changes.
	2) All spice simulations are completed without error.
	3) delay values of individual components are within reasonable range of reference.
'''

def test_flow(ref_file, test_dir, err_margin):

	# the difference allowed between reference and target
	margin = err_margin
	# the reference file
	referencefile = os.path.expanduser(ref_file)
	# the target test directory
	test_directory = os.path.expanduser(test_dir)


	# get the list of all directories in this folder
	list_directory = [dI for dI in os.listdir(test_directory) if os.path.isdir(os.path.join(test_directory,dI))]

	#lists used to store file names and directory
	target_file_list = []  # Full path and filename to the spice output files we're checking
	target_file_names = []  # Short name (no path) of the spice output files we're checking

	# change directory to target
	os.chdir(test_directory)

	#get all the lis files underneath the test directory. These are the final spice output files from a COFFE run.
	for directory in list_directory:
		for file in os.listdir(directory):
			if file.endswith(".lis"):
				target_file_list.append(test_directory+'/' +directory +'/'+ file)
				target_file_names.append(file)

	# dictionary used to store rise and fall delays			
	rise_and_fall_time_dictionary = {}

	for index, item in enumerate(target_file_list):
	# Look for delay values in the file, store them in a dictionary
		with open(item) as search_target:

			# look for rise and fall time delays in the file, add to the dictionary if found
			for line in search_target:
				if 'meas_total_tfall' in line:
					rise_and_fall_time_dictionary[target_file_names[index]+"tfall"] = re.findall("\d+\.\d+", line)
				if 'meas_total_trise' in line:
					rise_and_fall_time_dictionary[target_file_names[index]+"trise"] = re.findall("\d+\.\d+", line)
				

				


	# Open the reference file
	with open(referencefile) as search_target:

		rise_and_fall_time_dictionary_reference = {}
		# look for rise and fall time delays in the file and load the reference dictionary
		for line in search_target:
			theindex, thevalue = line.split('..')  # Our reference file has one delay entry per line <name>..<delay>
			rise_and_fall_time_dictionary_reference[theindex] = thevalue
			
	# for all items in the reference dictionary, check the difference with target dictionary
	for i in rise_and_fall_time_dictionary_reference.keys():
				# print a message and let the user know this component failed the test
			if (abs(float(rise_and_fall_time_dictionary_reference[i]) - float(rise_and_fall_time_dictionary[i][0]))/ float(rise_and_fall_time_dictionary_reference[i])) > margin:
				print "**FAIL in: " + str(i) + "Difference from reference: " + str((abs(float(rise_and_fall_time_dictionary_reference[i][0]) - float(rise_and_fall_time_dictionary[i][0]))/ float(rise_and_fall_time_dictionary_reference[i][0]))*100) + '%' 
			else:
				# print and let the user know that this component passed the test
				print "Passed test: "+ str(i) 


# Function to print a new reference file to screen. test_dir is the directory in which COFFE put its output. All SPICE output files
# test_dir will be parsed, rise and fall delays are extracted, and printed to the screen (pipe to a file to store) in the format
# expected by the tester.
def generate_reference(test_dir):


	# the target test directory
	test_directory = os.path.expanduser(test_dir)


	# get the list of all directories in this folder
	list_directory = [dI for dI in os.listdir(test_directory) if os.path.isdir(os.path.join(test_directory,dI))]

	#lists used to store file names and directory
	target_file_list = []
	target_file_names = []

	# change directory to target
	os.chdir(test_directory)

	#get all the lis files in the test directory
	for directory in list_directory:
		for file in os.listdir(directory):
			if file.endswith(".lis"):
				target_file_list.append(test_directory+'/' +directory +'/'+ file)
				target_file_names.append(file)

	# directionary used to store rise and fall delays			
	rise_and_fall_time_dictionary = {}

	for index, item in enumerate(target_file_list):
	# Look for delay values in the file, store them in a dictionary
		with open(item) as search_target:

			# look for rise and fall time delays in the file, add to the dictionary if found
			for line in search_target:
				if 'meas_total_tfall' in line:
					rise_and_fall_time_dictionary[target_file_names[index]+"tfall"] = re.findall("\d+\.\d+", line)
				if 'meas_total_trise' in line:
					rise_and_fall_time_dictionary[target_file_names[index]+"trise"] = re.findall("\d+\.\d+", line)

			
	for item in rise_and_fall_time_dictionary:
		print item + ".." + rise_and_fall_time_dictionary[item][0]
	
