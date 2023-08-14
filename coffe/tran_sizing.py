# This module contains functions to perform FPGA transistor sizing
#
# The most important function is 'size_fpga_transisors' located
# at the bottom of this file. It performs transistor sizing on the
# 'fpga' object passed as an argument and performs transistor sizing
# on that FPGA based on certain transistor sizing settings, which are
# also passed as arguments.

import os
import math
import time
from . import spice
from itertools import product
import sys

# This flag controls whether or not to print a bunch of ERF messages to the terminal
ERF_MONITOR_VERBOSE = True

# This is the ERF error tolerance. E.g. 0.01 means 1%.
ERF_ERROR_TOLERANCE = 0.1
# Maximum number of times the algorithm will try to meet ERF_ERROR_TOLERANCE before quitting.
ERF_MAX_ITERATIONS = 4



def expand_ranges(sizing_ranges):
	""" The input to this function is a dictionary that describes the SPICE sweep
		ranges. dict = {"name": (start_value, stop_value, increment)}
		To make it easy to run all the described SPICE simulations, this function
		creates a list of all possible combinations in the ranges.
		It also produces a 'name' list that matches the order of 
		the parameters for each combination."""
	
	# Use a copy of sizing ranges
	sizing_ranges_copy = sizing_ranges.copy()
	
	# Expand the ranges into full list of values    
	for key, values in list(sizing_ranges_copy.items()):
		# Initialization
		start_value = values[0]
		end_value = values[1]
		increment = values[2]
		current_value = start_value
		value_list = []
		# Loop till current values is larger than end value
		while current_value <= end_value:
			value_list.append(current_value)
			current_value = current_value + increment
		# Replace the range with a list
		sizing_ranges_copy[key] = value_list
									 
	# Now we want to make a list of all possible combinations
	sizing_combinations = [] 
	for combination in product(*[sizing_ranges_copy[i] for i in sorted(sizing_ranges_copy.keys())]):
		sizing_combinations.append(combination)

	# Make a list of sorted parameter names to go with the list of
	# combinations. The sorted list of names will match the order of 
	# items in each combinations of the list. 
	parameter_names = sorted(sizing_ranges_copy.keys())

	return parameter_names, sizing_combinations


def get_middle_value_config(param_names, spice_ranges):
	""" """
	
	# Initialize config as a tuple
	config = ()

	# For each parameter, find the mid value and create a config tuple
	for name in param_names:
		# Replaced code with unexpdanded.
		#range_len = len(spice_expanded_ranges[name])
		#mid_val = spice_expanded_ranges[name][range_len/2]
		#config = config + (mid_val,)
		range = spice_ranges[name]
		min = range[0]
		max = range[1]
		mid = math.ceil((max-min)/2 + min)
		config = config + (mid,)
		
	return config
   

def find_best_config(spice_results, area_exp, delay_exp):
	""" """
	
	# Find best area, delay and area_delay configs
	best_area = spice_results[0][2]
	best_delay = spice_results[0][3]
	best_area_delay = spice_results[0][4]
	best_area_config = 0
	best_delay_config = 0
	best_area_delay_config = 0
	for i in range(len(spice_results)):
		if spice_results[i][2] < best_area:
			best_area = spice_results[i][2]
			best_area_config = i
		if spice_results[i][3] < best_delay:
			best_delay = spice_results[i][3]
			best_delay_config = i
		if spice_results[i][4] < best_area_delay:
			best_area_delay = spice_results[i][4]
			best_area_delay_config = i 
			
	return best_area_delay_config

	
def export_spice_configs(results_filename, spice_param_names, spice_configs, lvl_rest_names, lvl_rest_configs):
	""" Export all transistor sizing combinations to a file """
	
	print("Exporting all configurations to: " + results_filename)

	# Open file for writing
	results_file = open(results_filename, 'a')
	results_file.write("TRANSISTOR SIZING COMBINATIONS\n")
	
	# Write Header
	header_str = "Config\t"
	for name in lvl_rest_names:
		header_str = header_str + name + "\t"
	for name in spice_param_names:
		header_str = header_str + name + "\t"
	results_file.write(header_str + "\n")

	# Write all configs
	config_number = 0
	for lvl_rest_config in lvl_rest_configs:
		config_str2 = ""
		for j in range(len(lvl_rest_names)):
			config_str2 = config_str2 + str(lvl_rest_config[j]) + "\t\t\t"
		for config in spice_configs:
			config_str = ""
			config_number = config_number + 1
			config_str = config_str + str(config_number) + "\t\t" + config_str2
			for i in range(len(spice_param_names)):
				config_str = config_str + str(config[i]) + "\t\t\t"
			results_file.write(config_str + "\n")
	
	# Close file
	results_file.write("\n\n\n")
	results_file.close()   

def export_transistor_sizes(filename, transistor_sizes):

	tran_size_file = open(filename, 'w')
	
	for tran_name, tran_size in transistor_sizes.items():
		tran_size_file.write(tran_name + "   " + str(tran_size) + "\n")
	
	tran_size_file.close()
	
	
def export_all_results(results_filename, element_names, sizing_combos, cost_list, area_list, eval_delay_list, tfall_trise_list):
	""" Write all area and delay results to a file. """
	
	# Open file for writing
	results_file = open(results_filename, 'w')
	
	# Make header string
	header_str = "Rank,"
	for name in element_names:
		header_str += name + ","
	header_str += "Cost,Area,EvalDelay,tfall,trise,"
	
	# Write header string to the file
	results_file.write(header_str + "\n")
	
	# Write out all results
	for i in range(len(cost_list)):
		# Get the combo index
		combo_index = cost_list[i][1]
		# Write rank
		results_file.write(str(i+1) + ",")
		# Write transistor sizes
		for j in range(len(element_names)):
			results_file.write(str(sizing_combos[combo_index][j]) + ",")
		# Write Cost, area, delay, tfall, trise, erf_error
		results_file.write(str(cost_list[i][0]) + ",")
		results_file.write(str(area_list[combo_index]) + ",")
		results_file.write(str(eval_delay_list[combo_index]) + ",")
		results_file.write(str(tfall_trise_list[combo_index][0]) + ",")
		results_file.write(str(tfall_trise_list[combo_index][1]) + ",")
		results_file.write("\n")
	
	# Close file
	results_file.close()
	

def export_erf_results(results_filename, element_names, sizing_combos, best_results):
	""" Export the post-erfed results to a CSV file.
		best_results is a tuple: (cost, combo_index, area, delay, tfall, trise, erf_ratios)"""
	
	# Open file for writing
	results_file = open(results_filename, 'w')
	
	# Make header string
	header_str = "Rank,"
	for name in element_names:
		header_str += name + ","
	header_str += "Cost,Area,EvalDelay,tfall,trise,erf_error,"
	erf_ratios_names = list(best_results[0][6].keys())
	for name in erf_ratios_names:
		header_str += name + ","
	
	# Write header string to the file
	results_file.write(header_str + "\n")
	
	# Write out all results
	rank_counter = 1
	for cost, combo_index, area, delay, tfall, trise, erf_ratios in best_results:
		# Write rank
		results_file.write(str(rank_counter) + ",")
		# Write transistor sizes
		for j in range(len(element_names)):
			results_file.write(str(sizing_combos[combo_index][j]) + ",")
		# Write Cost, area, delay, tfall, trise, erf_error
		results_file.write(str(cost) + ",")
		results_file.write(str(area) + ",")
		results_file.write(str(delay) + ",")
		results_file.write(str(tfall) + ",")
		results_file.write(str(trise) + ",")
		erf_error = abs(tfall - trise)/min(tfall, trise)
		results_file.write(str(erf_error) + ",")
		# Add ERF ratios
		for name in erf_ratios_names:
			results_file.write(str(erf_ratios[name]) + ",")
		results_file.write("\n")
		
		rank_counter += 1
		
	# Close file
	results_file.close()
	
	
def get_eval_area(fpga_inst, opt_type, subcircuit, is_ram_component, is_cc_component):

	# Get area based on optimization type (subcircuit if local optimization, tile if global)
	if opt_type == "local":
		area = fpga_inst.area_dict[subcircuit.name]
	# If the block being sized is part of the memory component, return ram size
	# Otherwise, the block size is returned
	elif "hard_block" in subcircuit.name:
		return subcircuit.area
	elif is_cc_component == 1:
		return fpga_inst.area_dict["total_carry_chain"]
	elif is_ram_component == 0 or fpga_inst.specs.enable_bram_block == 0:
		return fpga_inst.area_dict["tile"] 
	else:
		return fpga_inst.area_dict["ram_core"]
		
	
def get_final_area(fpga_inst, opt_type, subcircuit, is_ram_component, is_cc_component):
	# Get area based on optimization type (subcircuit if local optimization, tile if global)
	if opt_type == "local":
		area = fpga_inst.area_dict[subcircuit.name]
	# If the block being sized is part of the memory component, return ram size
	# Otherwise, the block size is returned
	elif "hard_block" in subcircuit.name:
		return subcircuit.area
	elif is_cc_component == 1:
		return fpga_inst.area_dict["total_carry_chain"]
	elif is_ram_component == 0 or fpga_inst.specs.enable_bram_block == 0:
		return fpga_inst.area_dict["tile"] 
	else:
		return fpga_inst.area_dict["ram_core"]
		
	
def get_eval_delay(fpga_inst, opt_type, subcircuit, tfall, trise, low_voltage, is_ram_component, is_cc_component):

	# omit measurements that are negative or doesn't reach Vgnd
	if tfall < 0 or trise < 0 or low_voltage > 4.0e-1:
		return 100

	# omit measurements that are too large
	if tfall > 5e-9 or trise > 5e-9 :
		return 100

	# Use average delay for evaluation
	delay = (tfall + trise)/2

	skip_size = 5

	if "hard_block" in subcircuit.name:
		delaywrost = 0.0
		if tfall > trise:
			delayworst = tfall
		else:
			delayworst = trise

		subcircuit.delay = delay
		subcircuit.trise = trise
		subcircuit.tfall = tfall

		if delayworst > subcircuit.lowerbounddelay:
			return subcircuit.delay + 10* (delayworst - subcircuit.lowerbounddelay)
		else:
			return subcircuit.delay

	if is_cc_component:
		subcircuit.delay = delay
		if fpga_inst.specs.carry_chain_type == "ripple":
			path_delay =  (fpga_inst.specs.N * fpga_inst.specs.FAs_per_flut - 2) * fpga_inst.carrychain.delay + fpga_inst.carrychainperf.delay + fpga_inst.carrychaininter.delay
			# The skip is pretty much dependent on size, I'll just assume 4 skip stages for now. However, it should work for any number of bits.
		elif fpga_inst.specs.carry_chain_type == "skip":
			# The critical path is the ripple path and the skip of the first one + the skip path of blocks in between, and the ripple and sum of the last block + the time it takes to load the wire in between
			path_delay = (fpga_inst.carrychain.delay * skip_size  + fpga_inst.carrychainand.delay + fpga_inst.carrychainskipmux.delay) + 2 * fpga_inst.carrychainskipmux.delay + fpga_inst.carrychain.delay * skip_size + fpga_inst.carrychainperf.delay +  (3 - fpga_inst.specs.FAs_per_flut) * fpga_inst.carrychaininter.delay
		return path_delay

		
	if opt_type == "local":
		return delay
	else:
		# We need to get the delay of a representative critical path
		# Let's first set the delay for this subcircuit
		subcircuit.delay = delay
		
		path_delay = 0
		
		# Switch block
		path_delay += fpga_inst.sb_mux.delay*fpga_inst.sb_mux.delay_weight
		# Connection block
		path_delay += fpga_inst.cb_mux.delay*fpga_inst.cb_mux.delay_weight
		# Local mux
		path_delay += fpga_inst.logic_cluster.local_mux.delay*fpga_inst.logic_cluster.local_mux.delay_weight
		# LUT
		path_delay += fpga_inst.logic_cluster.ble.lut.delay*fpga_inst.logic_cluster.ble.lut.delay_weight
		# LUT input drivers

		for lut_input_name, lut_input in fpga_inst.logic_cluster.ble.lut.input_drivers.items():
			path_delay += lut_input.driver.delay*lut_input.driver.delay_weight
			path_delay += lut_input.not_driver.delay*lut_input.not_driver.delay_weight
		# Local BLE output
		path_delay += fpga_inst.logic_cluster.ble.local_output.delay*fpga_inst.logic_cluster.ble.local_output.delay_weight
		# General BLE output
		path_delay += fpga_inst.logic_cluster.ble.general_output.delay*fpga_inst.logic_cluster.ble.general_output.delay_weight
		if fpga_inst.specs.use_fluts:
			path_delay += fpga_inst.logic_cluster.ble.fmux.delay *fpga_inst.logic_cluster.ble.lut.delay_weight

		if fpga_inst.specs.enable_carry_chain == 1:
			path_delay += fpga_inst.carrychainmux.delay *fpga_inst.logic_cluster.ble.lut.delay_weight

		#print path_delay
		#path_delay +=fpga_inst.carrychain.delay *fpga_inst.logic_cluster.ble.lut.delay_weight

		if fpga_inst.specs.enable_bram_block == 0:
			return path_delay
		# Memory block components begin here
		# set RAM individual constant delays here:
		# Memory block local mux
		ram_delay = fpga_inst.RAM.RAM_local_mux.delay

		# Row decoder
		ram_decoder_stage1_delay = 0

		# Obtian the average of NAND2 and NAND3 paths if they are both valid
		count_1 = 0 
		if fpga_inst.RAM.valid_row_dec_size2 == 1:
			ram_decoder_stage1_delay += fpga_inst.RAM.rowdecoder_stage1_size2.delay
			count_1 +=1

		if fpga_inst.RAM.valid_row_dec_size3 == 1:
			ram_decoder_stage1_delay += fpga_inst.RAM.rowdecoder_stage1_size3.delay
			count_1 +=1

		if count_1 !=0:
			fpga_inst.RAM.estimated_rowdecoder_delay = ram_decoder_stage1_delay/count_1
		fpga_inst.RAM.estimated_rowdecoder_delay += fpga_inst.RAM.rowdecoder_stage3.delay
		ram_decoder_stage0_delay = fpga_inst.RAM.rowdecoder_stage0.delay
		fpga_inst.RAM.estimated_rowdecoder_delay += ram_decoder_stage0_delay

		ram_delay = ram_delay + fpga_inst.RAM.estimated_rowdecoder_delay
		# wordline driver
		ram_delay += fpga_inst.RAM.wordlinedriver.delay 
		# column decoder
		ram_delay +=  fpga_inst.RAM.columndecoder.delay

		# add some other components depending on the technology:
		if fpga_inst.RAM.memory_technology == "SRAM":
			ram_delay += fpga_inst.RAM.writedriver.delay + fpga_inst.RAM.samp.delay + fpga_inst.RAM.samp_part2.delay + fpga_inst.RAM.precharge.delay 
		else:
			ram_delay +=fpga_inst.RAM.bldischarging.delay + fpga_inst.RAM.blcharging.delay + fpga_inst.RAM.mtjsamp.delay
		
		# first stage of the configurable deocoder
		ram_delay += fpga_inst.RAM.configurabledecoderi.delay
		# second stage of the configurable decoder
		# if there are two, I'll just add both since it doesn't really matter.
		if fpga_inst.RAM.cvalidobj1 ==1:
			ram_delay += fpga_inst.RAM.configurabledecoder3ii.delay
		if fpga_inst.RAM.cvalidobj2 ==1:
			ram_delay += fpga_inst.RAM.configurabledecoder2ii.delay

		# last stage of the configurable decoder
		ram_delay += fpga_inst.RAM.configurabledecoderiii.delay

		# outputcrossbar
		ram_delay +=fpga_inst.RAM.pgateoutputcrossbar.delay

		if is_ram_component == 0:
			return path_delay
		else:
			return ram_delay


def get_current_delay(fpga_inst, is_ram_component):


	path_delay = 0
		
	# Switch block
	path_delay += fpga_inst.sb_mux.delay*fpga_inst.sb_mux.delay_weight
	# Connection block
	path_delay += fpga_inst.cb_mux.delay*fpga_inst.cb_mux.delay_weight
	# Local mux
	path_delay += fpga_inst.logic_cluster.local_mux.delay*fpga_inst.logic_cluster.local_mux.delay_weight
	# LUT
	path_delay += fpga_inst.logic_cluster.ble.lut.delay*fpga_inst.logic_cluster.ble.lut.delay_weight
	# LUT input drivers
	#print path_delay
	for lut_input_name, lut_input in fpga_inst.logic_cluster.ble.lut.input_drivers.items():
		path_delay += lut_input.driver.delay*lut_input.driver.delay_weight
		path_delay += lut_input.not_driver.delay*lut_input.not_driver.delay_weight
	# Local BLE output
	#print path_delay
	path_delay += fpga_inst.logic_cluster.ble.local_output.delay*fpga_inst.logic_cluster.ble.local_output.delay_weight
	# General BLE output
	path_delay += fpga_inst.logic_cluster.ble.general_output.delay*fpga_inst.logic_cluster.ble.general_output.delay_weight

	#path_delay +=fpga_inst.carrychain.delay *fpga_inst.logic_cluster.ble.lut.delay_weight

	# Memory block components begin here
	# set RAM individual constant delays here:
	# Memory block local mux
	ram_delay = fpga_inst.RAM.RAM_local_mux.delay

	# Row decoder
	ram_decoder_stage1_delay = 0

	# Obtian the average of NAND2 and NAND3 paths if they are both valid
	count_1 = 0 
	if fpga_inst.RAM.valid_row_dec_size2 == 1:
		ram_decoder_stage1_delay += fpga_inst.RAM.rowdecoder_stage1_size2.delay
		count_1 +=1

	if fpga_inst.RAM.valid_row_dec_size3 == 1:
		ram_decoder_stage1_delay += fpga_inst.RAM.rowdecoder_stage1_size3.delay
		count_1 +=1

	if count_1 !=0:
		fpga_inst.RAM.estimated_rowdecoder_delay = ram_decoder_stage1_delay/count_1
	fpga_inst.RAM.estimated_rowdecoder_delay += fpga_inst.RAM.rowdecoder_stage3.delay
	ram_decoder_stage0_delay = fpga_inst.RAM.rowdecoder_stage0.delay
	fpga_inst.RAM.estimated_rowdecoder_delay += ram_decoder_stage0_delay

	ram_delay = ram_delay + fpga_inst.RAM.estimated_rowdecoder_delay
	# wordline driver
	ram_delay += fpga_inst.RAM.wordlinedriver.delay 
	# column decoder
	ram_delay +=  fpga_inst.RAM.columndecoder.delay

	# add some other components depending on the technology:
	if fpga_inst.RAM.memory_technology == "SRAM":
		ram_delay += fpga_inst.RAM.writedriver.delay + fpga_inst.RAM.samp.delay + fpga_inst.RAM.samp_part2.delay + fpga_inst.RAM.precharge.delay 
	else:
		ram_delay +=fpga_inst.RAM.bldischarging.delay + fpga_inst.RAM.blcharging.delay + fpga_inst.RAM.mtjsamp.delay
		
	# first stage of the configurable deocoder
	ram_delay += fpga_inst.RAM.configurabledecoderi.delay
	# second stage of the configurable decoder
	# if there are two, I'll just add both since it doesn't really matter.
	if fpga_inst.RAM.cvalidobj1 ==1:
		ram_delay += fpga_inst.RAM.configurabledecoder3ii.delay
	if fpga_inst.RAM.cvalidobj2 ==1:
		ram_delay += fpga_inst.RAM.configurabledecoder2ii.delay

	# last stage of the configurable decoder
	ram_delay += fpga_inst.RAM.configurabledecoderiii.delay

	# outputcrossbar
	ram_delay +=fpga_inst.RAM.pgateoutputcrossbar.delay

	if is_ram_component == 0:
		return path_delay
	else:
		return ram_delay

def get_final_delay(fpga_inst, opt_type, subcircuit, tfall, trise, is_ram_component, is_cc_component):



	# Use largest delay for final results
	if tfall > trise:
		delay = tfall
	else:
		delay = trise

	# final delay should not be negative, something went wrong :(
	if delay < 0 :
			print("ERROR: final delat is negative")
			print("***Negative delay: " + str(delay) + " in " + subcircuit.name + " ***")
			exit(2)
	subcircuit.delay = delay
	subcircuit.trise = trise
	subcircuit.tfall = tfall
	if "hard_block" in subcircuit.name:
		return subcircuit.delay

	skip_size = 5
	if is_cc_component:
		if fpga_inst.specs.carry_chain_type == "ripple":
			path_delay =  (fpga_inst.specs.N * fpga_inst.specs.FAs_per_flut - 2) * fpga_inst.carrychain.delay + fpga_inst.carrychainperf.delay + fpga_inst.carrychaininter.delay
			# The skip is pretty much dependent on size, I'll just assume 4 skip stages for now. However, it should work for any number of bits.
		elif fpga_inst.specs.carry_chain_type == "skip":
			# The critical path is the ripple path and the skip of the first one + the skip path of blocks in between, and the ripple and sum of the last block + the time it takes to load the wire in between
			path_delay = (fpga_inst.carrychain.delay * skip_size  + fpga_inst.carrychainand.delay + fpga_inst.carrychainskipmux.delay) + 2 * fpga_inst.carrychainskipmux.delay + fpga_inst.carrychain.delay * skip_size + fpga_inst.carrychainperf.delay +  (3 - fpga_inst.specs.FAs_per_flut) * fpga_inst.carrychaininter.delay
		return path_delay


	if opt_type == "local":
		return delay
	else:
		# We need to get the delay of a representative critical path
		# Let's first set the delay for this subcircuit
		subcircuit.delay = delay
		
		path_delay = 0
		
		# Switch block
		path_delay += fpga_inst.sb_mux.delay*fpga_inst.sb_mux.delay_weight
		# Connection block
		path_delay += fpga_inst.cb_mux.delay*fpga_inst.cb_mux.delay_weight
		# Local mux
		path_delay += fpga_inst.logic_cluster.local_mux.delay*fpga_inst.logic_cluster.local_mux.delay_weight
		# LUT
		path_delay += fpga_inst.logic_cluster.ble.lut.delay*fpga_inst.logic_cluster.ble.lut.delay_weight
		# LUT input drivers
		for lut_input_name, lut_input in fpga_inst.logic_cluster.ble.lut.input_drivers.items():
			path_delay += lut_input.driver.delay*lut_input.driver.delay_weight
			path_delay += lut_input.not_driver.delay*lut_input.not_driver.delay_weight
		# Local BLE output
		path_delay += fpga_inst.logic_cluster.ble.local_output.delay*fpga_inst.logic_cluster.ble.local_output.delay_weight
		# General BLE output
		path_delay += fpga_inst.logic_cluster.ble.general_output.delay*fpga_inst.logic_cluster.ble.general_output.delay_weight

		# final delay should not be negative, something went wrong :(
		if path_delay < 0 :
			print("***Negative path delay: " + str(path_delay) + " in " + subcircuit.name + " ***")
			exit(2)
		
		return path_delay
		
	
def cost_function(area, delay, area_opt_weight, delay_opt_weight):

	return pow(area,area_opt_weight)*pow(delay,delay_opt_weight)
	

def erf_inverter_balance_trise_tfall(sp_path,
									 inv_name,
									 inv_size,
									 target_tran_name,
									 parameter_dict,
									 fpga_inst,
									 spice_interface):
	"""
	This function will balance the rise and fall delays of an inverter by either making the 
	NMOS bigger or the PMOS bigger.

	sp_path 
		Path to the top-level spice file for the inverter that we want to size.
	inv_name
		Name of the inverter that we want to ERF
	inv_size
		Size of the inverter that we want to ERF. The size of an inverter 
		refers to the size of the smallest between NMOS and PMOS. So if we need to make
		the PMOS bigger to ERF, than nmos size would be = inv_size and pmos size would
		end up being something bigger than inv_size by the end of this function!
		inv_size refers to something different depending on whether we are dealing with 
		FinFETs or not. In a FinFET FPGA, inv_size refers to the number of fins in the
		transistor. For bulk, inv_size refers to the diffusion width in units of nanometers.
	target_tran_name
		Name of the transistor that needs to have it's size increased (i.e. the NMOS or PMOS
		of inv_name).
	fpga_inst
		An FPGA object.
	spice_interface
		A spice interface object.

	Returns: target_tran_size, which is the size for target_tran_name that gives ERF
	"""

	# This function will balance the rise and fall times of an inverter by either making 
	# the NMOS bigger or the PMOS bigger. If ever I speak in terms of the PMOS or NMOS only
	# when I explain things in the comments, just know that the same logic applies to the 
	# other transistor type as well. Just substitute PMOS<->NMOS and tfall<->trise.
		
	# Update the parameter dict needed by the spice_interface. 
	# The parameter dict contains the sizes of all transistors and RC of all wires.
	if not fpga_inst.specs.use_finfet:
		# For bulk, we are dealing with nanometers
		parameter_dict[inv_name + "_nmos"] = [1e-9*inv_size]
		parameter_dict[inv_name + "_pmos"] = [1e-9*inv_size]
	else :
		# For FinFETs, we are dealing with number of fins
		parameter_dict[inv_name + "_nmos"] = [inv_size]
		parameter_dict[inv_name + "_pmos"] = [inv_size]

	# The first thing we are going to do is increase the PMOS size in fixed increments
	# to get an upper bound on the PMOS size. We also monitor trise. We expect that 
	# increasing the PMOS size will decrease trise and increase tfall (because we are making
	# the pull up stronger). If at any time, we see that increasing the PMOS is increasing 
	# trise, we should stop increasing the PMOS size. We might be self-loading the inverter.
	if ERF_MONITOR_VERBOSE:
		print("Looking for " + target_tran_name + " size upper bound")
	upper_bound_not_found = True
	self_loading = False
	bulk_multiplication_factor = 1
	finfet_num_fins = inv_size
	valid_delays = True

	previous_tfall = 1
	previous_trise = 1
	while upper_bound_not_found and not self_loading:
		# Increase the target transistor size, update parameter dict and run HSPICE
		# The target transistor size is in nm for bulk and number of fins for FinFETs
		if not fpga_inst.specs.use_finfet :
			target_tran_size = bulk_multiplication_factor*inv_size
			parameter_dict[target_tran_name][0] = 1e-9*target_tran_size
			spice_meas = spice_interface.run(sp_path, parameter_dict)
		else :
			target_tran_size = finfet_num_fins
			parameter_dict[target_tran_name][0] = target_tran_size
			spice_meas = spice_interface.run(sp_path, parameter_dict)
		
		# Get the rise and fall measurements for our inverter out of 'spice_meas'
		# This was a single HSPICE run, so the value we want is at index 0
		tfall_str = spice_meas["meas_" + inv_name + "_tfall"][0]
		trise_str = spice_meas["meas_" + inv_name + "_trise"][0]

		# Check if the HSPICE measurement failed. If it did, this might mean that the level
		# restorers are too strong which messes up one of the transitions. Making the gate
		# length for the level restorers larger could solve this problem.
		# Note that it's also possible that something else is causing the failure...
		if tfall_str == "failed" or trise_str == "failed":
			print("ERROR: HSPICE measurement failed.")
			print("Consider increasing level-restorers gate length by increasing the 'rest_length_factor' parameter in the input file.")
			exit(1)

		tfall = float(tfall_str)
		trise = float(trise_str)

		# Sometimes we increase the transistor to a point where the delay
		# would be negative. I.e. the transition at the output is faster than the transition
		# at the input. This can cause COFFE to measure a 'negative' delay.
		# In this case, we stop ERF attempt.
		if tfall < 0 or trise < 0 :
			print("Negative delay detected during ERF. Output transition may be faster than input transition. Stopping upper bound search.")
			upper_bound_not_found = False
			valid_delays = False


		if ERF_MONITOR_VERBOSE:
			if "_pmos" in target_tran_name:
				sizing_bounds_str = ("NMOS=" + str(inv_size) + 
									 "  PMOS=" + str(target_tran_size))
			else:
				sizing_bounds_str = ("NMOS=" + str(target_tran_size) + 
									 "  PMOS=" + str(inv_size))
			print((sizing_bounds_str + ": tfall=" + tfall_str + " trise=" + trise_str + 
				   " diff=" + str(tfall-trise)))

		# We accept negative delays on the first inverter in a driver.
		if "_1_" not in target_tran_name and "_0_" not in target_tran_name and "_2_" not in target_tran_name:
			if tfall < 0 or trise < 0 :
				print("ERROR: Unexpected negative delay.")
				if not fpga_inst.specs.use_finfet:
					exit(1)
				else:
					# Hack to fix finfets becoming to strong (weird things were happening to the waveforms)
					if finfet_num_fins != inv_size:
						finfet_num_fins -= 1
						

		# Figure out if we have found the upper bound by looking at tfall and trise. 
		# For a PMOS, upper bound is found if tfall > trise
		# For an NMOS, upper bound is found if tfall < trise 
		# We use the transistor name to figure out if our target tran is an NMOS or PMOS
		if "_pmos" in target_tran_name:
			if tfall > trise:
				upper_bound_not_found = False
				if ERF_MONITOR_VERBOSE:
					print("Upper bound found, PMOS=" + str(target_tran_size))
			else:
				# Check if trise is increasing or decreasing by comparing to previous trise
				if trise >= previous_trise or target_tran_size/inv_size > 4:
					self_loading = True
					if ERF_MONITOR_VERBOSE:
						print("Increasing PMOS is no longer decreasing trise")
						print(("or the ratio is too large, using PMOS=" + 
							   str(target_tran_size)))
						print("")
				previous_trise = trise    
		else:
			if trise > tfall:
				upper_bound_not_found = False
				if ERF_MONITOR_VERBOSE:
					print("Upper bound found, NMOS=" + str(target_tran_size))
			else:
				# Check if tfall is increasing or decreasing by comparing to previous tfall
				if tfall >= previous_tfall or target_tran_size/inv_size > 4:
					self_loading = True
					if ERF_MONITOR_VERBOSE:
						print("Increasing NMOS is no longer decreasing tfall ")
						print(("or the ratio is too large, using NMOS=" + 
							   str(target_tran_size)))
				previous_tfall = tfall   

		# For bulk, this will increment the target transistor size by another 'inv_size'
		bulk_multiplication_factor += 1
		# For FinFETs, this will increment the target transistor size by one fin
		finfet_num_fins += 1

	# At this point, we have found an upper bound for our target transistor. If the 
	# inverter is self-loaded, we are just going to use whatever transistor size we 
	# currently have as the target transistor size. But if the inverter is not self-loaded,
	# we are going to find the precise transistor size that gives balanced rise/fall.
	# This step is only done for bulk transistors because FinFETs have "fin granularity".
	# That is, once we find the upper bound, there isn't much more we can do to balance
	# the rise and fall for FinFETs (we are limited by number of fins). With bulk on the 
	# other hand, we have "nanometer granularity" so we can refine the ERF more.
	if valid_delays and not self_loading and not fpga_inst.specs.use_finfet:      

		# The trise/tfall equality occurs in [target_tran_size-inv_size, target_tran_size]
		# To find it, we'll sweep this range in two steps. In the first step, we'll sweep
		# it in increments of min_tran_width. This will allow us to narrow down the range
		# where equality occurs. In the second step, we'll sweep the new smaller range with
		# a 1 nm granularity. This two step approach is meant to reduce runtime, but I have
		# no data proving that it actually does reduce runtime.
		nm_size_lower_bound = target_tran_size - inv_size
		nm_size_upper_bound = target_tran_size
		interval = fpga_inst.specs.min_tran_width

		# Create a list of transistor sizes we want to try
		nm_size_list = []
		current_nm_size = nm_size_lower_bound
		while current_nm_size <= nm_size_upper_bound:
			nm_size_list.append(current_nm_size)
			current_nm_size += interval
		 
		# Normally when we change transistor sizes, we should recalculate areas
		# and wire RC to account for the change. In this case, however, we are going
		# to make the simplifying assumption that the changes we are making will not
		# have a significant impact on area and on wire lengths. Thus, we save CPU time
		# and just use the same wire RC for this part of the algorithm. 
		#
		# So what we are going to do here is use the parameter_dict that we defined earlier
		# in this function to populate a new parameter dict for the HSPICE sweep that we
		# want to do. All parameters will keep the same value as the one in parameter_dict
		# except for the target transistor that we want to sweep.
		sweep_parameter_dict = {}
		for i in range(len(nm_size_list)):
			for name in list(parameter_dict.keys()):
				# Get the value from the existing dictionary and only change it if it's our
				# target transistor.
				value = parameter_dict[name][0]
				if name == target_tran_name:
					value = 1e-9*nm_size_list[i]

				# On the first iteration, we have to add the lists themselves, but every 
				# other iteration we can just append to the lists.
				if i == 0:
					sweep_parameter_dict[name] = [value]
				else:
					sweep_parameter_dict[name].append(value)

		# Run HSPICE sweep
		if ERF_MONITOR_VERBOSE:
			print("Running HSPICE sweep on: " + sp_path + "")

		spice_meas = spice_interface.run(sp_path, sweep_parameter_dict)
		
		# Find the new interval where the tfall trise equality occurs.
		for i in range(len(nm_size_list)):
			tfall_str = spice_meas["meas_" + inv_name + "_tfall"][i]
			trise_str = spice_meas["meas_" + inv_name + "_trise"][i]
			tfall = float(tfall_str)
			trise = float(trise_str)
		 
			# We are making the PMOS bigger, that means that initially, tfall was smaller
			# than trise. At some point, making the PMOS larger will make trise smaller 
			# than tfall. That's what we use to identify our ERF transistor size interval. 
			if "_pmos" in target_tran_name:
				if tfall > trise:
					nm_size_upper_bound = nm_size_list[i]
					nm_size_lower_bound = nm_size_list[i-1]
					break
			# We are making the NMOS bigger, that means that initially, trise was smaller 
			# than tfall. At some point, making the NMOS larger will make tfall smaller
			# than trise. That's what we use to identify our ERF transistor size interval.
			else:
				if trise > tfall:
					nm_size_upper_bound = nm_size_list[i]
					nm_size_lower_bound = nm_size_list[i-1]
					break
			   
		# checks to see if indicies are swapped
		# this was a work around when there was bug and was not too clear as to what was happening 
		# it should no longer be necessary, but there's not harm in checking anyways
		# if the lower bound is larger than the upper bound, the lower bound becomes the upper bound
		# and vice versa. The net effect is that in the 1nm sweep, we'll just sweep more sizes.
		if nm_size_lower_bound > nm_size_upper_bound:
			print("***WARNING: ERF boundaries were swapped.***")
			temp_size = nm_size_upper_bound
			nm_size_upper_bound = nm_size_lower_bound
			nm_size_lower_bound = temp_size

		if ERF_MONITOR_VERBOSE:
			if "_pmos" in target_tran_name:
				print(("ERF PMOS size in range: [" + 
					   str(int(nm_size_lower_bound)) + ", " + 
					   str(int(nm_size_upper_bound)) + "]"))
			else:
				print(("ERF NMOS size in range: [" + 
					   str(int(nm_size_lower_bound)) + ", " + 
					   str(int(nm_size_upper_bound)) + "]"))
		
		# We know that ERF is in between nm_size_lower_bound and nm_size_upper_bound
		# Now we'll sweep this interval with a 1 nm step.
		interval = 1
		# Create a list of transistor sizes we want to try
		nm_size_list = []
		current_nm_size = nm_size_lower_bound
		while current_nm_size <= nm_size_upper_bound:
			nm_size_list.append(current_nm_size)
			current_nm_size += interval
		
		# Make a new sweep parameter dict
		sweep_parameter_dict = {}
		for i in range(len(nm_size_list)):
			for name in list(parameter_dict.keys()):
				# Get the value from the existing dictionary and only change it if it's our
				# target transistor.
				value = parameter_dict[name][0]
				if name == target_tran_name:
					value = 1e-9*nm_size_list[i]

				# On the first iteration, we have to add the lists themselves, but every 
				# other iteration we can just append to the lists.
				if i == 0:
					sweep_parameter_dict[name] = [value]
				else:
					sweep_parameter_dict[name].append(value)

		# Run HSPICE sweep
		if ERF_MONITOR_VERBOSE:
			print("Running HSPICE sweep on: " + sp_path + "")
		spice_meas = spice_interface.run(sp_path, sweep_parameter_dict)

		# This time around, we want to select the PMOS size that makes the difference
		# between trise and tfall as small as possible. (we know that the minimum
		# was in the interval we just swept)
		current_best_tfall_trise_balance = 1
		best_index = 0
		for i in range(len(nm_size_list)):
			tfall_str = spice_meas["meas_" + inv_name + "_tfall"][i]
			trise_str = spice_meas["meas_" + inv_name + "_trise"][i]
			# For some reason I occasionally see a failure due to "internal timestep being too small" The following shall avoid the program
			# from crashing but it will throw away that part of the results
			try:
				tfall = float(tfall_str)
			except ValueError:
				tfall = 1;
			try:
				trise = float(trise_str)
			except ValueError:
				trise = 2;
			diff = abs(tfall-trise)
			if diff < current_best_tfall_trise_balance:
				current_best_tfall_trise_balance = diff
				best_index = i
		target_tran_size = nm_size_list[best_index]

		if ERF_MONITOR_VERBOSE:
			print("ERF PMOS size is " + str(target_tran_size) + "\n")
			
	# End of the "if not self_loading"

	sys.stdout.flush()

	return target_tran_size


def erf_inverter(sp_path, 
				 inv_name, 
				 inv_drive_strength, 
				 parameter_dict,
				 fpga_inst, 
				 spice_interface):
	""" 
	Equalize the rise and fall delays of an inverter by increasing the size of either the
	NMOS or the PMOS transistor.

	sp_path 
		The path to the top level spice file for this inverter

	inv_name 
		The name of the inverter

	inv_drive_strength
		The drive strength of the smallest transistor in the inverter.
		The other transistor will be made bigger to balance rise and fall delays.

	fpga_inst
		An FPGA object

	spice_interface
		A spice interface object
	"""        
	
	if ERF_MONITOR_VERBOSE:
		print("ERF MONITOR: " + inv_name) 
	 
	pmos_name = inv_name + "_pmos"
	nmos_name = inv_name + "_nmos"

	# The pmos and nmos size are different depending on whether we are dealing with FinFETs 
	# or bulk. For bulk, the sizes are the transistor diffusion width in nanometers.
	# For FinFETs, the size refers to the number of fins.
	if not fpga_inst.specs.use_finfet :
		inv_size = inv_drive_strength*fpga_inst.specs.min_tran_width
		nmos_size = inv_size
		pmos_size = inv_size
	else :
		inv_size = inv_drive_strength
		nmos_size = inv_size
		pmos_size = inv_size

	# Modify the parameter dict with the size of this inverter
	if not fpga_inst.specs.use_finfet :
		parameter_dict[nmos_name][0] = 1e-9*inv_size
		parameter_dict[pmos_name][0] = 1e-9*inv_size
	else :
		parameter_dict[nmos_name][0] = inv_size
		parameter_dict[pmos_name][0] = inv_size

	# The NMOS and PMOS sizes of this inverter are both equal to 'inv_size' right now.
	# That is, they are equal. We'll run HSPICE on the circuit to get initial rise and fall
	# delays. Then, we'll use these delays to figure out if it's the NMOS we need to 
	# make bigger to balance rise/fall or the PMOS.
	spice_meas = spice_interface.run(sp_path, parameter_dict)
	
	# Get the rise and fall measurements for our inverter out of 'spice_meas'
	# This was a single HSPICE run, so the value we want is at index 0


	inv_tfall_str = spice_meas["meas_" + inv_name + "_tfall"][0]
	inv_trise_str = spice_meas["meas_" + inv_name + "_trise"][0]
	
	# Check if the HSPICE measurement failed. If it did, this might mean that the level
	# restorers are too strong which messes up one of the transitions. Making the gate
	# length for the level restorers larger could solve this problem.
	# Note that it's also possible that something else is causing the failure...
	if inv_tfall_str == "failed" or inv_trise_str == "failed":
		print("ERROR: HSPICE measurement failed.")
		print("Consider increasing level-restorers gate length by increasing the 'rest_length_factor' parameter in the input file.")
		exit(1)

	inv_tfall = float(inv_tfall_str)
	inv_trise = float(inv_trise_str)

	# If the rise time is faster, nmos must be made bigger.
	# If the fall time is faster, pmos must be made bigger. 
	if inv_trise > inv_tfall:
		# ERF by increasing PMOS size
		pmos_size = erf_inverter_balance_trise_tfall(sp_path,
													 inv_name,
													 inv_size,
													 pmos_name,
													 parameter_dict,
													 fpga_inst,
													 spice_interface)
																   
	else:    
		# ERF by increasing NMOS size 
		nmos_size = erf_inverter_balance_trise_tfall(sp_path,
													 inv_name,
													 inv_size,
													 nmos_name,
													 parameter_dict,
													 fpga_inst,
													 spice_interface)  
	 
	# Update the parameter dict
	if not fpga_inst.specs.use_finfet :
		parameter_dict[nmos_name][0] = 1e-9*nmos_size
		parameter_dict[pmos_name][0] = 1e-9*pmos_size
	else :
		parameter_dict[nmos_name][0] = nmos_size
		parameter_dict[pmos_name][0] = pmos_size

	# Update fpga_inst transistor sizes with new NMOS & PMOS sizes
	if not fpga_inst.specs.use_finfet :
		fpga_inst.transistor_sizes[nmos_name] = (nmos_size/fpga_inst.specs.min_tran_width)
		fpga_inst.transistor_sizes[pmos_name] = (pmos_size/fpga_inst.specs.min_tran_width)
	else :
		fpga_inst.transistor_sizes[nmos_name] = (nmos_size)
		fpga_inst.transistor_sizes[pmos_name] = (pmos_size)

	sys.stdout.flush()
		 
	return 
   

def erf(sp_path, 
		element_names, 
		element_sizes, 
		fpga_inst, 
		spice_interface):
	""" 
	Equalize rise and fall times of all inverters listed in 'element_names' for the  
	transistor sizes in 'config'.

	Returns the inverter ratios that give equal rise and fall. 
	"""

	# This function will equalize rise and fall times on all inverters in the input 
	# 'element_names'. It iteratively finds P/N ratios that equalize the rise and fall times 
	# of each inverter. Iteration stops if tfall and trise are found to be sufficiently 
	# equal or if a maximum number of iterations have been performed.
   
	# Generate the parameter dict needed by the spice_interface. 
	# The parameter dict contains the sizes of all transistors and RC of all wires.
	parameter_dict = {}
	if not fpga_inst.specs.use_finfet :
		for tran_name, tran_size in fpga_inst.transistor_sizes.items():
			parameter_dict[tran_name] = [1e-9*tran_size*fpga_inst.specs.min_tran_width]
		for wire_name, rc_data in fpga_inst.wire_rc_dict.items():
			parameter_dict[wire_name + "_res"] = [rc_data[0]]
			parameter_dict[wire_name + "_cap"] = [rc_data[1]*1e-15]
	else :
		for tran_name, tran_size in fpga_inst.transistor_sizes.items():
			parameter_dict[tran_name] = [tran_size]
		for wire_name, rc_data in fpga_inst.wire_rc_dict.items():
			parameter_dict[wire_name + "_res"] = [rc_data[0]]
			parameter_dict[wire_name + "_cap"] = [rc_data[1]*1e-15]

	# Set ERF tolerance flag to False so that we can enter the while loop
	erf_tolerance_met = False
	erf_iteration = 1
	while not erf_tolerance_met:
		# Start by assuming that ERF tolerance will be met.
		erf_tolerance_met = True

		# ERF each inverter in the circuit
		for i in range(len(element_names)):
			circuit_element = element_names[i]
			element_size = element_sizes[i]
	
			# If the element is an inverter, equalize its rise and fall delays
			# 'erf_inverter' will mutate parameter dict and the fpga object with ERFed sizes.
			if element_names[i].startswith("inv_"):
				erf_inverter(sp_path, 
							 circuit_element, 
							 element_size, 
							 parameter_dict, 
							 fpga_inst, 
							 spice_interface)
				
	
		# At this point, all inverters have been ERFed.
		# Parameter dict, and the FPGA object itself both contain the ERFed transistor sizes.
		# Let's see how we did by running HSPICE on the circuit and comparing the rise and
		# fall delays for each inverter.
		spice_meas = spice_interface.run(sp_path, parameter_dict)
	
		if ERF_MONITOR_VERBOSE:
			print("ERF SUMMARY (iteration " + str(erf_iteration) + "):")
		
		# Check the trise/tfall error of all inverters and if at least one of them 
		# doesn't meet the ERF tolerance, we'll set the erf_tolerance_met flag to false
		for circuit_element in element_names:
			# We are only interested in inverters
			if not circuit_element.startswith("inv_"):
				continue

			# Get the tfall and trise delays for the inverter from the spice measurements
			tfall = float(spice_meas["meas_" + circuit_element + "_tfall"][0])
			trise = float(spice_meas["meas_" + circuit_element + "_trise"][0])
			erf_error = abs((tfall - trise)/tfall)
	
			if not fpga_inst.specs.use_finfet :
				nmos_nm_size = int(parameter_dict[circuit_element + "_nmos"][0]/1e-9)
				pmos_nm_size = int(parameter_dict[circuit_element + "_pmos"][0]/1e-9)
			else :
				nmos_nm_size = int(parameter_dict[circuit_element + "_nmos"][0])
				pmos_nm_size = int(parameter_dict[circuit_element + "_pmos"][0])
   
			# Check to see if the ERF tolerance is met for this inverter
			if erf_error > ERF_ERROR_TOLERANCE:
				erf_tolerance_met = False
	
			if ERF_MONITOR_VERBOSE:
				print((circuit_element + " (N=" + str(nmos_nm_size) + " P=" + 
					   str(pmos_nm_size) + ", tfall=" + str(tfall) + ", trise=" + 
					   str(trise) + ", erf_err=" + str(100*round(erf_error,3)) + "%)"))
		
		if ERF_MONITOR_VERBOSE:
			if not erf_tolerance_met:
				print("One or more inverter(s) failed to meet ERF tolerance")
			else:
				print("All inverters met ERF tolerance")
   
		# Stop ERFing even if tolerance not met if max number of ERF iterations performed.
		if erf_iteration >= ERF_MAX_ITERATIONS:
			if ERF_MONITOR_VERBOSE:
				print("Stopping ERF because max iterations reached")
				print()
			break

		erf_iteration += 1

		if ERF_MONITOR_VERBOSE:
			print("")

	# Get the ERF ratios
	erf_ratios = {}
	for circuit_element in element_names:
		if circuit_element.startswith("inv_"):
			nmos_size = fpga_inst.transistor_sizes[circuit_element + "_nmos"]
			pmos_size = fpga_inst.transistor_sizes[circuit_element + "_pmos"]
			erf_ratios[circuit_element] = float(pmos_size)/nmos_size

	return erf_ratios
				  

def erf_combo(fpga_inst, 
			  sp_path, 
			  element_names, 
			  combo,
			  spice_interface):
	""" Equalize the rise and fall of all inverters in a transistor sizing combination.
		Returns the inverter ratios that give equal rise and fall for this combo. """
   
	# We want to ERF a transistor sizing combination
	# Update transistor sizes
	fpga_inst._update_transistor_sizes(element_names, combo, fpga_inst.specs.use_finfet)
	# Calculate area of everything
	fpga_inst.update_area()
	# Re-calculate wire lengths
	fpga_inst.update_wires()
	# Update wire resistance and capacitance
	fpga_inst.update_wire_rc()
	# Find ERF ratios
	erf_ratios = erf(sp_path, 
					 element_names, 
					 combo, 
					 fpga_inst, 
					 spice_interface)
	
	return erf_ratios
	
	
def run_combo(fpga_inst, sp_path, element_names, combo, erf_ratios, spice_interface):
	""" Run HSPICE to measure delay for this transistor sizing combination.
		Returns tfall, trise """
	
	# Update transistor sizes
	fpga_inst._update_transistor_sizes(element_names, combo, fpga_inst.specs.use_finfet, erf_ratios)
	# Calculate area of everything
	fpga_inst.update_area()
	# Re-calculate wire lengths
	fpga_inst.update_wires()
	# Update wire resistance and capacitance
	fpga_inst.update_wire_rc()
	# Update wire R and C SPICE file
	#fpga_inst.update_wire_rc_file()

	# Make parameter dict
	parameter_dict = {}
	if not fpga_inst.specs.use_finfet :
		for tran_name, tran_size in fpga_inst.transistor_sizes.items():
			parameter_dict[tran_name] = [1e-9*tran_size*fpga_inst.specs.min_tran_width]
		for wire_name, rc_data in fpga_inst.wire_rc_dict.items():
			parameter_dict[wire_name + "_res"] = [rc_data[0]]
			parameter_dict[wire_name + "_cap"] = [rc_data[1]*1e-15]
	else :
		for tran_name, tran_size in fpga_inst.transistor_sizes.items():
			parameter_dict[tran_name] = [tran_size]
		for wire_name, rc_data in fpga_inst.wire_rc_dict.items():
			parameter_dict[wire_name + "_res"] = [rc_data[0]]
			parameter_dict[wire_name + "_cap"] = [rc_data[1]*1e-15]

	# Run HSPICE with the current transistor size
	spice_meas = spice_interface.run(sp_path, parameter_dict)                                           

	# run returns a dict of measurements. For each key, we have a list of meaasurements. 
	# That;s why we add the [0] 
	# Extract total delay from measurements
	tfall = float(spice_meas["meas_total_tfall"][0])
	trise = float(spice_meas["meas_total_trise"][0])
	
	return tfall, trise

	
def search_ranges(sizing_ranges, fpga_inst, sizable_circuit, opt_type, re_erf, area_opt_weight, 
				  delay_opt_weight, outer_iter, inner_iter, bunch_num, spice_interface, is_ram_component, is_cc_component):
	""" 
		Function for searching a range of transistor sizes. 
		The first thing we do is determine P/N ratios to use for these size ranges.
		Then, we calculate area and wire loads for each transistor sizing combination.
		An HSPICE simulation is performed for each transistor sizing combination with the
		appropriate wire loading.
		With the area and delay of each sizing combination we calculate the cost of each
		and we sort based on cost to find the least cost transistor sizing within the 
		sizing ranges. 
		We re-balance the rise and fall times of M top transistor sizing combinations 
		(M = the 're_erf' argument). This re-balancing might change the final ranking. 
		So, we sort by cost again and choose the lowest cost sizing combination as the
		best transistor sizing for the given ranges.
	"""
	
	# Export current transistor sizes
	# TODO: Turning this off for now
	#tran_sizes_filename = (spice_filedir + 
	#                       "sizes_" + sizable_circuit.name + 
	#                       "_o" + str(outer_iter) + 
	#                       "_i" + str(inner_iter) + 
	#                       "_b" + str(bunch_num) + ".txt")
	#export_transistor_sizes(tran_sizes_filename, fpga_inst.transistor_sizes)
	
	# Expand ranges to get a list of all possible sizing combinations from ranges
	element_names, sizing_combos = expand_ranges(sizing_ranges)

	# Find the combo that is near the middle of all ranges
	middle_combo = get_middle_value_config(element_names, sizing_ranges)
		
	print("Determining initial inverter P/N ratios...")
	if ERF_MONITOR_VERBOSE:
		print("")

	# Find ERF ratios for middle combo
	erf_ratios = erf_combo(fpga_inst, 
						   sizable_circuit.top_spice_path, 
						   element_names, 
						   middle_combo,
						   spice_interface)
	
	# For each transistor sizing combination, we want to calculate area, wire sizes, 
	# and wire R and C
	print("Calculating area and wire data for all transistor sizing combinations...")
	
	area_list = []
	wire_rc_list = []
	eval_delay_list = []

	for combo in sizing_combos:
		# Update FPGA transistor sizes
		fpga_inst._update_transistor_sizes(element_names, combo, fpga_inst.specs.use_finfet, erf_ratios)
		# Calculate area of everything
		fpga_inst.update_area()
		# Get evaluation area
		area_list.append(get_eval_area(fpga_inst, opt_type, sizable_circuit, is_ram_component, is_cc_component))
		# Re-calculate wire lengths
		fpga_inst.update_wires()
		# Update wire resistance and capacitance
		fpga_inst.update_wire_rc()
		wire_rc = fpga_inst.wire_rc_dict
		wire_rc_list.append(wire_rc)

	
	# We have to make a parameter dict for HSPICE
	current_tran_sizes = {}
	if not fpga_inst.specs.use_finfet :
		for tran_name, tran_size in fpga_inst.transistor_sizes.items():
			current_tran_sizes[tran_name] = 1e-9*tran_size*fpga_inst.specs.min_tran_width
	else :
		for tran_name, tran_size in fpga_inst.transistor_sizes.items():
			current_tran_sizes[tran_name] = tran_size

	# Initialize the parameter dict to all empty lists
	parameter_dict = {}
	for tran_name in list(current_tran_sizes.keys()):
		parameter_dict[tran_name] = []
	for wire_name in list(wire_rc_list[0].keys()):
		parameter_dict[wire_name + "_res"] = []
		parameter_dict[wire_name + "_cap"] = []

	for i in range(len(sizing_combos)):
		for tran_name, tran_size in current_tran_sizes.items():
			# We need this temp value to compare agains 'element_names'
			tmp_tran_name = tran_name.replace("_nmos", "")
			tmp_tran_name = tmp_tran_name.replace("_pmos", "")
		   
			# If this transistor is one of the transistor sizes that we are sweeping,
			# we have to properly compute the size, if we aren't sweeping it, just add
			# the current size to the list.
			if tmp_tran_name in element_names:
				# We need this id to pick the right data from sizing combo
				element_id = element_names.index(tmp_tran_name)

				# Let's calculate the size of this transistor
				if not fpga_inst.specs.use_finfet :
					tran_size = 1e-9*(sizing_combos[i][element_id]*fpga_inst.specs.min_tran_width)
				else :
					tran_size = (sizing_combos[i][element_id])

				# If transistor is an inverter, we need to do some stuff to calc sizes for
				# both the NMOS and PMOS, if it is anything else (eg. ptran), we can just add 
				# it directly.
				if tran_name.startswith("inv_"):
					if tran_name.endswith("_nmos"):
						# If the NMOS is bigger than the PMOS
						if erf_ratios[tmp_tran_name] < 1:
							nmos_size = tran_size/erf_ratios[tmp_tran_name]
						# If the PMOS is bigger than the NMOS
						else:
							nmos_size = tran_size
						parameter_dict[tran_name].append(nmos_size)
					else:
						# If the NMOS is bigger than the PMOS
						if erf_ratios[tmp_tran_name] < 1:
							pmos_size = tran_size
						# If the PMOS is bigger than the NMOS
						else:
							pmos_size = tran_size*erf_ratios[tmp_tran_name]
						parameter_dict[tran_name].append(pmos_size)

				else: 
					parameter_dict[tran_name].append(tran_size) 
			else:
				parameter_dict[tran_name].append(tran_size)
	
		# Now add the wire information for this wire
		for wire_name, rc_data in wire_rc_list[i].items():
			parameter_dict[wire_name + "_res"].append(rc_data[0])
			parameter_dict[wire_name + "_cap"].append(rc_data[1]*1e-15)
   
	# Run HSPICE data sweep
	print(("Running HSPICE for " + str(len(sizing_combos)) + 
		   " transistor sizing combinations..."))
	spice_meas = spice_interface.run(sizable_circuit.top_spice_path, parameter_dict)

	# Now we need to create a list of tfall_trise to be compatible with old code
	tfall_trise_list = []
	meas_logic_low_voltage = []
	for i in range(len(sizing_combos)):
		tfall_str = spice_meas["meas_total_tfall"][i]
		trise_str = spice_meas["meas_total_trise"][i]
		if spice_meas["meas_logic_low_voltage"][i] == "failed" :
			meas_logic_low_voltage.append(1)
		else :
			meas_logic_low_voltage.append(float(spice_meas["meas_logic_low_voltage"][i]))

		if tfall_str == "failed":
			tfall = 1
		else:
			tfall = float(tfall_str)
		if trise_str == "failed":
			trise = 1
		else:
			trise = float(trise_str)
		tfall_trise_list.append((tfall, trise))
  
	# Get delay metric used for evaluation for each transistor sizing combo as well as 
	# ERF error
	for i in range(len(tfall_trise_list)):    
		# Calculate evaluation delay
		tfall_trise = tfall_trise_list[i]


		delay = get_eval_delay(fpga_inst, opt_type, sizable_circuit, tfall_trise[0], tfall_trise[1], meas_logic_low_voltage[i], is_ram_component, is_cc_component)


		eval_delay_list.append(delay)
		
	# len(area_list) should be equal to len(delay_list), make sure...
	assert len(area_list) == len(eval_delay_list)
	
	# Calculate cost for each combo (area-delay product)
	# Results list holds a tuple, (cost, combo_index, area, delay)
	print("Calculating cost for each transistor sizing combinations...")
	print("")
	cost_list = []
	for i in range(len(eval_delay_list)):
		area = area_list[i]
		delay = eval_delay_list[i]
		cost = cost_function(area, delay, area_opt_weight, delay_opt_weight)
		cost_list.append((cost, i))
		
	# Sort based on cost
	cost_list.sort()
	
	# Print top 10 results
	print("TOP 10 BEST COST RESULTS")
	print("------------------------")
	
	for i in range(min(10, len(cost_list))):
		combo_index = cost_list[i][1]
		print(("Combo #" + str(combo_index).ljust(6) + 
			   "cost=" + str(round(cost_list[i][0],6)).ljust(9) + 
			   "area=" + str(round(area_list[combo_index]/1000000,3)).ljust(8) + 
			   "delay=" + str(round(eval_delay_list[combo_index],13)).ljust(10) + 
			   "tfall=" + str(round(tfall_trise_list[combo_index][0],13)).ljust(10) + 
			   "trise=" + str(round(tfall_trise_list[combo_index][1],13)).ljust(10)))
	print("")
	
	# Write results to file
	# TODO: Turning this off for now
	#export_filename = (spice_filedir + 
	#                   sizable_circuit.name + 
	#                   "_o" + str(outer_iter) + 
	#                   "_i" + str(inner_iter) + 
	#                   "_b" + str(bunch_num) + ".csv")
	#export_all_results(export_filename, 
	#                   element_names, 
	#                   sizing_combos, 
	#                   cost_list, 
	#                   area_list, 
	#                   eval_delay_list, 
	#                   tfall_trise_list)

	# Re-ERF some of the top results
	# This is the number of top results to re-ERF
	re_erf_num = min(re_erf, len(cost_list))
	best_results = []
	for i in range(re_erf_num):
		# Re-ERF i-th best combo
		print(("Re-equalizing rise and fall times on combo #" + str(cost_list[i][1]) + 
			   " (ranked #" + str(i+1) + ")\n"))
		erf_ratios = erf_combo(fpga_inst, 
							   sizable_circuit.top_spice_path, 
							   element_names, 
							   sizing_combos[cost_list[i][1]], 
							   spice_interface)

		# Measure delay for combo
		trise, tfall = run_combo(fpga_inst, 
								 sizable_circuit.top_spice_path, 
								 element_names, 
								 sizing_combos[cost_list[i][1]], 
								 erf_ratios,
								 spice_interface)

		# Get final delay (we use final because ERFing is done for each combo)
		delay = get_final_delay(fpga_inst, opt_type, sizable_circuit, tfall, trise, is_ram_component, is_cc_component)
		# Get area (run_combo will have updated the area numbers for us so we can get it 
		# directly)
		area = get_final_area(fpga_inst, opt_type, sizable_circuit, is_ram_component, is_cc_component)
		# Calculate cost
		cost = cost_function(area, delay, area_opt_weight, delay_opt_weight)
		# Add to best results (cost, combo_index, area, delay, tfall, trise, erf_ratios)
		best_results.append((cost, cost_list[i][1], area, delay, tfall, trise, erf_ratios))
		
	# Sort the newly ERF results
	best_results.sort()
	
	print("BEST COST RESULTS AFTER RE-BALANCING")
	print("------------------------------------")
	for result in best_results:
		print(("Combo #" + str(result[1]).ljust(6) + 
			   "cost=" + str(round(result[0],6)).ljust(9) + 
			   "area=" + str(round(result[2]/1000000,3)).ljust(8) + 
			   "delay=" + str(round(result[3],13)).ljust(10) + 
			   "tfall=" + str(round(result[4],13)).ljust(10) + 
			   "trise=" + str(round(result[5],13)).ljust(10)))
	print("")

	# Write post-erf results to file
	# TODO: Turn this off for now
	#erf_export_filename = (spice_filedir + 
	#                       sizable_circuit.name + 
	#                       "_o" + str(outer_iter) + 
	#                       "_i" + str(inner_iter) + 
	#                       "_b" + str(bunch_num) + "_erf.csv")
	#export_erf_results(erf_export_filename, 
	#                   element_names, 
	#                   sizing_combos, 
	#                   best_results)
	
	# Update transistor sizes file as well as area and wires to best combo
	best_combo = sizing_combos[best_results[0][1]]
	best_combo_erf_ratios = best_results[0][6]
	# Update transistor sizes
	fpga_inst._update_transistor_sizes(element_names, best_combo, fpga_inst.specs.use_finfet, best_combo_erf_ratios)
	# Calculate area of everything
	fpga_inst.update_area()
	# Re-calculate wire lengths
	fpga_inst.update_wires()
	# Update wire resistance and capacitance
	fpga_inst.update_wire_rc()
	
	# We want to return the best combo, this must contain all NMOS and PMOS values
	best_combo_detailed = {}
	best_combo_dict = {}
	for i in range(len(element_names)):
		name = element_names[i]
		if "ptran_" in name:
			best_combo_dict[name] = best_combo[i]
			best_combo_detailed[name + "_nmos"] = best_combo[i]
		elif "tgate_" in name:
			best_combo_dict[name] = best_combo[i]
			best_combo_detailed[name + "_nmos"] = best_combo[i]
			best_combo_detailed[name + "_pmos"] = best_combo[i]
		elif "rest_" in name:
			best_combo_dict[name] = best_combo[i]
			best_combo_detailed[name + "_pmos"] = best_combo[i]
		elif "inv_" in name:
			best_combo_dict[name] = best_combo[i]
			# If the NMOS is bigger than the PMOS
			if best_combo_erf_ratios[name] < 1:
				best_combo_detailed[name + "_nmos"] = best_combo[i]/best_combo_erf_ratios[name]
				best_combo_detailed[name + "_pmos"] = best_combo[i]
			# If the PMOS is bigger than the NMOS
			else:
				best_combo_detailed[name + "_nmos"] = best_combo[i]
				best_combo_detailed[name + "_pmos"] = best_combo[i]*best_combo_erf_ratios[name]
		
	return (best_combo_dict, best_combo_detailed, best_results[0])
  
	
def format_transistor_names_to_basic_subcircuits(transistor_names):
	""" The input is a list of transistor names with the '_nmos' and '_pmos' tags.
		The output is a list of element names without tags. """

	format_names = []
	for tran_name in transistor_names:
		stripped_name = tran_name.replace("_nmos", "")
		stripped_name = stripped_name.replace("_pmos", "")
		if stripped_name not in format_names:
			format_names.append(stripped_name)
			
	return format_names   
	
	
def format_transistor_sizes_to_basic_subciruits(transistor_sizes):
	""" This takes a dictionary of transistor sizes and removes the _nmos and _pmos tags.
		Also, inverters and transmission gates are given a single size. """
	  
	format_sizes = {}  
	for tran_name, size in transistor_sizes.items():
		stripped_name = tran_name.replace("_nmos", "")
		stripped_name = stripped_name.replace("_pmos", "")
		if "inv_" in stripped_name or "tgate_" in stripped_name:
			if stripped_name in list(format_sizes.keys()):
				if size < format_sizes[stripped_name]:
					format_sizes[stripped_name] = size
			else:
				format_sizes[stripped_name] = size
		else:
			format_sizes[stripped_name] = size
	   
	return format_sizes
	
	
def _print_sizing_ranges(subcircuit_name, sizing_ranges_list):
	""" Print the sizing ranges for this subcircuit. """

	print("Transistor size ranges for " + subcircuit_name + ":")

	# Calculate column width for each name
	name_len = []
	sizing_strings = {}
	for name in list(sizing_ranges_list[0].keys()):
		name_len.append(len(name))
		sizing_strings[name] = ""
	
	# Find biggest name
	col_width = max(name_len) + 2
	
	# Make sizing strings
	for sizing_ranges in sizing_ranges_list:
		for name, size_range in sizing_ranges.items():
			sizing_strings[name] = sizing_strings[name] + ("[" + str(size_range[0]) + " -> " + str(size_range[1]) + "]").ljust(11)
	
	# Print sizing ranges for each subcircuit/transistor
	for name, size_string in sizing_strings.items():
		print("".join(name.ljust(col_width)) + ": " + size_string)
		
	print("")

	
def print_sizing_results(subcircuit_name, sizing_results_list):
	""" """
	
	print("Sizing results for " + subcircuit_name + ":")
	
	# Calculate column width for each name
	name_list = list(sizing_results_list[0].keys())
	name_list.sort()
	name_len = []
	sizing_strings = {}
	for name in name_list:
		name_len.append(len(name))
		sizing_strings[name] = ""
	
	# Find biggest name
	col_width = max(name_len) + 1
	
	# Make results strings
	for sizing_results in sizing_results_list:
		for name in name_list:
			size = sizing_results[name]
			sizing_strings[name] = sizing_strings[name] + (str(round(size,1))).ljust(4)
	
	# Print sizing results for each subcircuit/transistor
	for name, size_string in sizing_strings.items():
		print("".join(name.ljust(col_width)) + ": " + size_string)
		
	print("")

	
def _divide_problem_into_sets(transistor_names):
	""" If there are too many elements to size, the number of different combinations to try will quickly blow up on us.
		However, we want to size transistors together in as large groups as possible as this produces a more thorough search. 
		In general, groups of 5-6 transistors yields a good balance between these two competing factors.  
		This function looks at the 'transistor_names' argument and figures out how to divide the transistors to size in 
		more manageable groups (if indeed they do need to be divided up).
	"""

	# The first thing we are going to do is count how many elements we need to size. 
	# We don't count level restorers because we always set them to minimum size.
	count = 0
	for tran_name in transistor_names:
		if "rest_" not in tran_name:
				count = count + 1
	
	print("Found " + str(count) + " elements to size")
		
	# Create the transistor groups
	tran_names_set_list = []
	if count > 6:
		print("Too many elements to size at once...")
		# Let's divide this into sets of 5, the last set might have less than 5 elements.       
		tran_counter = 0
		tran_names_set = []
		for tran_name in transistor_names:
			if tran_counter >= 5:
				tran_names_set_list.append(tran_names_set)
				tran_names_set = []
				tran_names_set.append(tran_name)
				tran_counter = 1
			else:
				tran_names_set.append(tran_name)
				if "rest_" not in tran_name:
						tran_counter = tran_counter + 1
		
		# Add the last set to the set list
		tran_names_set_list.append(tran_names_set)
		
		# Print out the sets
		print("Creating the following groups:\n")
		for i in range(len(tran_names_set_list)):
			set = tran_names_set_list[i]
			print("GROUP " + str(i+1)) 
			for tran_name in set:
				if "rest_" not in tran_name:
						print(tran_name)
			print("")
	
	else:
		# We only have one item in the set list
		tran_names_set_list.append(transistor_names)
		for i in range(len(tran_names_set_list)):
			set = tran_names_set_list[i]
			for tran_name in set:
				if "rest_" not in tran_name:
						print(tran_name)
			print("")
	 
	return tran_names_set_list
			

def _find_initial_sizing_ranges(transistor_names, transistor_sizes):
	""" This function finds the initial transistor sizing ranges.
		The initial ranges are determined based on 'transistor_sizes'
		I think it's a good idea for the initial transistor size ranges to be smaller
		than subsequent ranges. We can look at the initial transistor sizing ranges as more of a test
		that determines whether the sizes of these transistors will change or not. If we keep the 
		ranges smaller, we can more quickly perform this test. If we find 
		that we don't need to change these transistor sizes much, we didn't waste time exploring a 
		larger range of sizes. If we find that transistor sizes do need to change a lot, we can make 
		the next transistor size ranges larger.
	"""
  
	# We have to figure out what ranges to use.
	set_length = len(transistor_names)
	if set_length >= 6:
		sizes_per_element = 4
	elif set_length == 5:
		sizes_per_element = 6
	else:
		sizes_per_element = 8
		
	# Figure out sizing ranges
	# If the transistor is a level-restorer, keep the size at 1.
	# If the transistor is anything else, create a transistor size range 
	# that keeps the current size near the center.
	sizing_ranges = {}
	for name in transistor_names:
		#if "precharge" in name:
			#sizes_per_element = 20
		# Current size of this transistor
		#print transistor_sizes
		#size = transistor_sizes[name]
		defaultsize = 1
		size = transistor_sizes.get(name, defaultsize)

		if "rest_" in name:
			max = 1
			min = 1
			incr = 1
			sizing_ranges[name] = (min, max, incr)
		elif "inv_nand" in name:
			max = 1 
			min = 1
			incr = 1
			sizing_ranges[name] = (min, max, incr)
		else:
			# Grow the range on both sides of the current size (i.e. both larger sizes and smaller sizes)
			max = size + (sizes_per_element/2)
			min = size - (sizes_per_element/2)
			incr = 1
			# Transistor sizes smaller than 1 are not legal sizes.
			# If this happens, make the min 1, and increase the size of max (to keep the same range size).
			if min < 1:
				max = max - min
				min = 1
			sizing_ranges[name] = (min, max, incr)
		
	return sizing_ranges
	
		
def update_sizing_ranges(sizing_ranges, sizing_results):
	""" 
		This function does two things. First, it checks whether the transistor sizing results are valid.
		That is, if the results are on the boundaries of the ranges, they are not valid. In this case, 
		the function will adjust 'sizing_ranges' around the 'sizing_results'.
		
		Returns: True if 'sizing_results' are valid, False otherwise.
	"""

	# Note: There are two tricks built into this function.
	#
	# Trick 1: When we evaluate whether a transistor size is on the range boundary or not, we also 
	#          find out whether it is on the lower or upper boundary. So, when we adjust the transistor
	#          size range, we skew it towards one direction more than the other. 
	#          For example, if tran_1_range = [3 -> 8] and we found that tran_1_size = 8.
	#          This would imply that we might need to increase the size of tran_1 because it is on the
	#          upper boundary. So when we adjust tran_1_range, it makes sense to do tran_1_range = [6 -> 13]
	#          rather than [5 -> 12]. That is, we skew the range towards growing the transistor size.
	#
	# Trick 2: The algorithms for skewing transistor sizing ranges for growing and for shrinking transistor
	#          sizes is not symmetrical. The reason for this is to avoid oscillation. We found that in some 
	#          cases, the algorithm would get stuck in a state where it would want to grow a transistor size
	#          so it would adjust the transistor size ranges to RANGE_GROW (for example) then when it evaluated
	#          validity, if found that it now had to shrink transistor sizes, so it would adjust the ranges to
	#          RANGE_SHRINK. Because the adjustment was symmetrical, the algorithm would oscillate between these
	#          two ranges.

	
	print("Validating transistor sizes")
	
	# The first thing we are going to do is count how many elements we need to size. 
	count = 0
	for tran_name in list(sizing_results.keys()):
		if "rest_" not in tran_name:
			count = count + 1
	
	# Get a rough estimate on the number of sizes per element based on some target maximum number of transistor sizing combinations.
	# The real number of transistor sizing combinations may end up being larger than this max due to some of the sizing range 
	# adjustments we make below.
	max_combinations = 4000
	sizes_per_element = int(math.pow(max_combinations, 1.0/count))
	
	# Now, we need to have an upper limit on sizing ranges. For example, if we only have one transistor,
	# we might try thousands of sizes, which doesnt really make sense to do.
	if sizes_per_element > 20:
		sizes_per_element = 20
	
	if sizes_per_element < 3:
		sizes_per_element = 3
	
	# Check each element for boundaries condition
	valid = True
	for name, size in sizing_results.items():
		# Skip rest_ because we fix these at minimum size.
		if "rest_" in name:
			continue
		# The nand gates in the row decoder are best set to minimum size
		# This also improves run-time greatly
		if "inv_nand" in name:
			max = 1
			min = 1
			incr = 1
			sizing_ranges[name] = (min, max, incr)
			continue
		# Check if equal to upper bound
		if size == sizing_ranges[name][1]:
			print(name + " is on upper bound")
			valid = False
			# Update the ranges
			max = size + sizes_per_element - 1
			min = size - 2
			incr = 1
			if min < 1:
				max = max - min
				min = 1
			sizing_ranges[name] = (min, max, incr)
		# Check if equal to lower bound
		elif size == sizing_ranges[name][0]:
			# If lower bound = 1, can't make it any smaller. This is not a violation.
			if sizing_ranges[name][0] != 1:
				print(name + " is on lower bound")
				valid = False
				# Update the ranges
				max = size + 3
				min = size - sizes_per_element + 2
				incr = 1
				if min < 1:
					max = max - min
					min = 1
				sizing_ranges[name] = (min, max, incr)
				
	if not valid:
		print("Sizing results not valid, computing new sizing ranges\n")
	else:
		print("Sizing results are valid\n")
   
	return valid
	   

def size_subcircuit_transistors(fpga_inst, 
								subcircuit, 
								opt_type, 
								re_erf, 
								area_opt_weight, 
								delay_opt_weight, 
								outer_iter, 
								initial_transistor_sizes, 
								spice_interface,
								is_ram_component,
								is_cc_component):
	"""
		Size transistors for one subcircuit.
	"""
	
	print("|------------------------------------------------------------------------------|")
	print("|    Transistor sizing on subcircuit: " + subcircuit.name.ljust(41) + "|")
	print("|------------------------------------------------------------------------------|")
	print("")
	
	# Get a list of element names in this subcircuit (ptran, inv, etc.). 
	# We expect this list to be sorted in the order in which things should be sized.
	tran_names = format_transistor_names_to_basic_subcircuits(subcircuit.transistor_names)
	
	# Create groups of transistors to size to keep number of HSPICE sims manageable
	tran_names_set_list = _divide_problem_into_sets(tran_names)
	
	sizing_ranges_set_list = []
	sizing_ranges_complete = {}

	# Find initial transistor sizing ranges for each set of transistors
	for tran_names_set in tran_names_set_list:
		sizing_ranges_set = _find_initial_sizing_ranges(tran_names_set, 
														initial_transistor_sizes)
		sizing_ranges_set_list.append(sizing_ranges_set.copy())
		sizing_ranges_complete.update(sizing_ranges_set)

	# Get the SPICE file name and the directory name
	spice_filename = os.path.basename(subcircuit.top_spice_path)
	spice_filedir = os.path.dirname(subcircuit.top_spice_path)
	
	# If there is more than one set to size, we should first ERF everything.
	# Once that is done, we can work on individual sets.
	if len(sizing_ranges_set_list) > 1:    
		element_names = sorted(sizing_ranges_complete.keys())
		print("Determining initial inverter P/N ratios for all transistor groups...")
		# Find the combo that is near the middle of all ranges
		middle_combo = get_middle_value_config(element_names, sizing_ranges_complete)
		# ERF mid-range transistor sizing combination
		erf_ratios = erf_combo(fpga_inst,
							   subcircuit.top_spice_path,
							   element_names, 
							   middle_combo, 
							   spice_interface)

	# Perform transistor sizing on each set of transistors
	sizing_results = {}
	sizing_results_detailed = {}
	for set_num in range(len(sizing_ranges_set_list)):
		sizing_ranges = sizing_ranges_set_list[set_num]
		
		# Keep a list of the sizing ranges we tried.
		sizing_ranges_list = []
		sizing_ranges_list.append(sizing_ranges.copy())

		# Keep sizing until sizes are valid (i.e. not on the boundaries)
		sizes_are_valid = False
		sizing_results_list = []
		sizing_results_detailed_list = []
		area_delay_results_list = []
		inner_iter = 1
		while not sizes_are_valid:
		
			# Print past and current sizing ranges to terminal
			_print_sizing_ranges(subcircuit.name, sizing_ranges_list)
			
			# Make a copy of the sizing ranges. size_ranges modifies the contents of the sizing_ranges dict.
			# So we keep an unmodified copy up here (the original).
			sizing_ranges_copy = sizing_ranges.copy()
		
			# Perform transistor sizing on ranges
			search_ranges_return = search_ranges(sizing_ranges_copy,            
												 fpga_inst, 
												 subcircuit, 
												 opt_type, 
												 re_erf, 
												 area_opt_weight, 
												 delay_opt_weight, 
												 outer_iter, 
												 inner_iter, 
												 set_num, 
												 spice_interface,
												 is_ram_component,
												 is_cc_component)
										 
			sizing_results_set = search_ranges_return[0]
			sizing_results_set_detailed = search_ranges_return[1]
			area_delay_results = search_ranges_return[2]
			
			sizing_results_list.append(sizing_results_set)
			sizing_results_detailed_list.append(sizing_results_set_detailed)
			area_delay_results_list.append(area_delay_results)
			print_sizing_results(subcircuit.name, sizing_results_detailed_list)
			
			# Update results so that we have results for all sets in one place
			sizing_results.update(sizing_results_set)
			sizing_results_detailed.update(sizing_results_set_detailed)
			
			# Now we need to check if this is a valid sizing (is it on the boundaries or not).
			# If it is on the boundaries, we need to adjust the boundaries and do the sizing again.
			# If it isn't on the boundaries, its a valid sizing, we store the results and move on to the next subcircuit.
			sizes_are_valid = update_sizing_ranges(sizing_ranges, sizing_results_set)
			
			# Add a copy of sizing ranges to list
			sizing_ranges_list.append(sizing_ranges.copy())
			
			inner_iter += 1

	sys.stdout.flush()
	return sizing_results, sizing_results_detailed

	
def print_results(opt_type, sizing_results_list, area_results_list, delay_results_list):
	""" Print sizing results to terminal """
	
	print("FPGA TRANSISTOR SIZING RESULTS")
	print("------------------------------")

	subcircuit_names = sorted(sizing_results_list[0].keys())
	
	for subcircuit_name in subcircuit_names:
		print(subcircuit_name + ":")
		
		# Let's make the element names column such that everything lines up
		# We'll also initialize the strings that will contain the sizing results
		sizing_strings = {}
		element_names = list(sizing_results_list[0][subcircuit_name].keys())
		element_name_lengths = []
		for name in element_names:
			element_name_lengths.append(len(name))
			sizing_strings[name] = ""
		
		# The length of the biggest element name is our minimum column width
		col_width = max(element_name_lengths) + 1

		# Create the sizing strings
		for results in sizing_results_list:
			subcircuit_results = results[subcircuit_name]
			for name in element_names:
				size = subcircuit_results[name]
				sizing_strings[name] = sizing_strings[name] + str(size).ljust(4)
		 
		# Now print the results
		for name, size_string in sizing_strings.items():
			print("".join(name.ljust(col_width)) + ": " + size_string)
		
		print("")  
		
		if opt_type == "local":
			print("Area\t\tDelay\t\tArea-Delay Product")
			area_delay_strings = []
			for i in range(len(area_results_list)):
				area_results = area_results_list[i]
				delay_results = delay_results_list[i]
				subcircuit_area = area_results[subcircuit_name]
				subcircuit_delay = delay_results[subcircuit_name]
				subcircuit_cost = subcircuit_area*subcircuit_delay
				area_delay_strings.append(str(round(subcircuit_area,3)) + "\t" + str(round(subcircuit_delay,14)) + "\t" + str(round(subcircuit_cost,5)))
			
			# Print results
			for area_delay_str in area_delay_strings:
				print(area_delay_str)
			print("\n")
			
	print("")        
	print("TOTALS:")
	print("Area\t\tDelay\t\tCost")
	totals_strings = []
	for i in range(len(area_results_list)):
		area_results = area_results_list[i]
		delay_results = delay_results_list[i]
		total_area = area_results["tile"]
		total_delay = delay_results["rep_crit_path"]
		total_cost = total_area*total_delay
		totals_strings.append(str(round(total_area/1000000,3)) + "\t" + str(round(total_delay,14)) + "\t" + str(round(total_cost,5)))
	for total_str in totals_strings:
		print(total_str)
	print("")


def export_sizing_results(results_filename, sizing_results_list, area_results_list, delay_results_list):
	""" """
	
	results_file = open(results_filename, 'w')

	subcircuit_names = sorted(sizing_results_list[0].keys())

	
	for subcircuit_name in subcircuit_names:
		results_file.write(subcircuit_name + ":\n")
		
		# Let's make the element names column such that everything lines up
		# We'll also initialize the strings that will contain the sizing results
		sizing_strings = {}
		element_names = list(sizing_results_list[0][subcircuit_name].keys())
		element_name_lengths = []
		for name in element_names:
			element_name_lengths.append(len(name))
			sizing_strings[name] = ""
		
		# The length of the biggest element name is our minimum column width
		col_width = max(element_name_lengths) + 1

		# Create the sizing strings
		for results in sizing_results_list:
			subcircuit_results = results[subcircuit_name]
			for name in element_names:
				size = subcircuit_results[name]
				sizing_strings[name] = sizing_strings[name] + str(size).ljust(4)
		 
		# Now write the results
		for name, size_string in sizing_strings.items():
			results_file.write("".join(name.ljust(col_width)) + ": " + size_string + "\n")
		results_file.write("\n")
		
		results_file.write(("Area").ljust(20) + ("Delay").ljust(20) + ("APD").ljust(20) + "\n")
		area_delay_strings = []
		for i in range(len(area_results_list)):
			area_results = area_results_list[i]
			delay_results = delay_results_list[i]
			subcircuit_area = area_results[subcircuit_name]
			subcircuit_delay = delay_results[subcircuit_name]
			subcircuit_cost = subcircuit_area*subcircuit_delay
			area_delay_strings.append((str(subcircuit_area)).ljust(20) + (str(subcircuit_delay)).ljust(20) + (str(subcircuit_cost)).ljust(20))
		
		# Write results
		for area_delay_str in area_delay_strings:
			results_file.write(area_delay_str + "\n")
		results_file.write("\n")
				  
	results_file.write("TOTALS:\n")
	results_file.write(("Area").ljust(20) + ("Delay").ljust(20) + ("APD").ljust(20) + "\n")
	totals_strings = []
	for i in range(len(area_results_list)):
		area_results = area_results_list[i]
		delay_results = delay_results_list[i]
		total_area = area_results["tile"]
		total_delay = delay_results["rep_crit_path"]
		total_cost = total_area*total_delay
		totals_strings.append((str(total_area)).ljust(20) + (str(total_delay)).ljust(20) + (str(total_cost)).ljust(20))
	for total_str in totals_strings:
		results_file.write(total_str + "\n")
	results_file.write("\n")

	results_file.close()
	
	
def check_if_done(sizing_results_list, area_results_list, delay_results_list, area_opt_weight, delay_opt_weight):
	""" Check if the transistor sizing algorithm is done.
		Returns true if done, false if not done.
	"""
	
	print("Evaluating termination conditions...")
	
	# If the list has only one set of results, we've only done one iteration, 
	# we can't possibly know if the sizes are stable or not.
	if len(sizing_results_list) <= 1:
		print("Cannot terminate based on cost: at least one more FPGA sizing iteration required")
		return False, 0
	 
	# Let's look at the cost of each iteration.
	# What we are looking for as a terminating is an increase in the cost.   
	# Normally, that should never happen, the algorithm should always move 
	# to a solution with better cost. The reason that it does happen is that 
	# we are sometimes using stale data (or approximations) when we evaluate 
	# transistor sizes (for example: pre-computed P/N ratios for inverters, 
	# delays of subcircuits other than the one we are sizing, etc.). So, 
	# solution i might look better than solution i-1 during sizing, but in 
	# the end, when we update delays and re-balance P/N ratios, we find that
	# i is actually a little bit worse than i-1. These 2 solutions will 
	# generally have very similar cost, and I think this suggests that we 
	# have a fairly minimal solution, but it's not necessarily globally 
	# minimal as we can't guarantee that with this algorithm.
	
	previous_cost = -1
	best_iteration = 0
	for i in range(len(area_results_list)):
		# Get tile area and critical path for this sizing iteration
		area_results = area_results_list[i]
		delay_results = delay_results_list[i]
		total_area = area_results["tile"]
		total_delay = delay_results["rep_crit_path"]
		# Calculate cost.
		total_cost = cost_function(total_area, total_delay, area_opt_weight, delay_opt_weight)

		# First iteration, just update previous cost
		if previous_cost == -1:
			previous_cost = total_cost
			continue
		
		# Sadegh: I have decided not to include this part to be able to observe how cost function is changed over time
		# It also facilitiates having quick mode.
		# The user should probably have an idea of how many iterations to run the tool with after using the quick mode.

		# If we are moving to a higher cost solution,
		# Stop, and choose the one with smaller cost (the previous one)
		#if total_cost >= previous_cost:
			#print "Algorithm is terminating: cost has stopped decreasing\n"
			#best_iteration = i - 1
			#return True, best_iteration
		#else:
		previous_cost = total_cost
		best_iteration = i

	return False, 0

	

def size_fpga_transistors(fpga_inst, run_options, spice_interface):
	""" Size FPGA transistors. 
	
		Inputs: fpga_inst - fpga object instance
				run_options which include:
					opt_type         - optimization type (global or local)
					re_erf           - number of sizing combos to re-erf
					max_iterations   - maximum number of 'FPGA sizing iterations' (see [1])
					area_opt_weight  - the 'b' in (cost = area^b * delay^c)
					delay_opt_weight - the 'c' in (cost = area^b * delay^c)
				spice_interface - an object that is used to run HSPICE and parse its outputs
		
		One 'FPGA sizing iteration' means sizing each subcircuits once.
		We perform multiple sizing iterations. Stopping criteria is that
		we have performed the 'max_iterations' or we found a minimum in cost.
		A minimum cost is found when we observe that the cost of solution i
		is larger than the cost of solution i-1. Now normally, that should
		never happen, the algorithm should always move to a solution with better 
		cost. The reason that it does happen is that we are sometimes using stale 
		data (or approximations) when we evaluate transistor sizes (for example:
		pre-computed P/N ratios for inverters, delays of subcircuits other than the
		one we are sizing, etc.). So, solution i might look better than solution i-1
		during sizing, but in the end, when we update delays and re-balance P/N
		ratios, we find that i is actually worse than i-1. These solutions will
		generally have very similar cost, and I think this suggests that we have a 
		fairly minimal solution, but it's not necessarily globally minimal as we can't
		guarantee that with this algorithm.
		
		[1] C. Chiasson and V.Betz, "COFFE: Fully-Automated Transistor Sizing for FPGAs", FPT2013
		
		"""

	opt_type         = run_options.opt_type 
	re_erf           = run_options.re_erf
	max_iterations   = run_options.max_iterations 
	area_opt_weight  = run_options.area_opt_weight 
	delay_opt_weight = run_options.delay_opt_weight
	size_hb_interfaces = run_options.size_hb_interfaces
   
	# Create results folder if it doesn't exist
	if not os.path.exists("sizing_results"):
		os.makedirs("sizing_results")
	
	# Initialize FPGA subcircuit delays
	fpga_inst.update_delays(spice_interface)
	
	print("Starting transistor sizing...\n")
	
	# These lists store transistor sizing, area and delay results for each FPGA sizing
	# iteration. Each entry in the list represents an FPGA sizing iteration.
	# For example, area_results_list[0] has area results for the first FPGA sizing iteration.
	sizing_results_list = []
	sizing_results_detailed_list = []
	area_results_list = []
	delay_results_list = []
	quick_mode_dict = {}
	# Keep performing FPGA sizing iterations until algorithm terminates
	# Two conditions can make it terminate:
	# 1 - Cost stops improving ('is_done')
	# 2 - The max number of iterations of this while loop have been performed (max_iterations)
	is_done = False
	iteration = 1
	while not is_done:
	
		if iteration > max_iterations:
			print(("Algorithm is terminating: maximum number of iterations has been " +
				   "reached (" + str(max_iterations) + ")\n"))
			break
	
		print("FPGA TRANSISTOR SIZING ITERATION #" + str(iteration) + "\n")

		sizing_results_dict = {}
		sizing_results_detailed_dict = {}

		# Now we are going to size the transistors of each subcircuit.
		# The order we do this has an importance due to rise-fall balancing. 
		# We want the input signal to be rise-fall balanced as much as possible. 
		# So we start in the general routing, and move gradually deeper into the logic
		# cluster, finally emerging back into the general routing when we reach the cluster 
		# outputs. This code is all basically the same, just repeated for each subcircuit.

		print("determining a floorplan for this sizing iteration")
		
		
		fpga_inst.update_area()
		if fpga_inst.lb_height == 0.0:
			fpga_inst.lb_height = math.sqrt(fpga_inst.area_dict["tile"])
			fpga_inst.update_area()

		fpga_inst.update_wires()
		fpga_inst.update_wire_rc()
		#fpga_inst.determine_height()
		fpga_inst.update_area()
		fpga_inst.compute_distance()
		fpga_inst.update_wires()
		fpga_inst.update_wire_rc()
		fpga_inst.update_delays(spice_interface)
		
		
		print("Sizing will begin now.")
		# Useful for debugging
		# tmp_area = get_eval_area(fpga_inst, "global", fpga_inst.sb_mux, 0, 0)
		# tmp_delay = get_current_delay(fpga_inst, 0)
		# print(tmp_area,tmp_delay)
		current_cost = cost_function(get_eval_area(fpga_inst, "global", fpga_inst.sb_mux, 0, 0), get_current_delay(fpga_inst, 0), area_opt_weight, delay_opt_weight)
		print("Current Cost: " + str(current_cost))
		time_before_sizing = time.time()

		# For quick mode:
		# In the first iteration, I assume everything is useful and should be sized in the future iterations.
		# I check if it resulted in an improvement equal to or greater than the specified threshold.
		# If that's not the case, the module will not be resized again. 
		# Note: Please enable quick mode only for global optimization
		# Also, note that quickmode may slightly degrade (~3-4%) logic optimization while it will not have much of an impact on BRAM (>1%)
		# hence, after figuring out the best architecture or changing the code, consider running without quicmode for a better logic result. (if needed)

		for hardblock in fpga_inst.hardblocklist:
			############################################
			## Size hard block custom components
			############################################
			if hardblock.parameters['num_dedicated_outputs'] > 0:
				name = hardblock.dedicated.name
				# If this is the first iteration, use the 'initial_transistor_sizes' as the starting sizes. 
				# If it's not the first iteration, we use the transistor sizes of the previous iteration as the starting sizes.
				if iteration == 1:
					quick_mode_dict[name] = 1
					starting_transistor_sizes = format_transistor_sizes_to_basic_subciruits(hardblock.dedicated.initial_transistor_sizes)
				else:
					starting_transistor_sizes = sizing_results_list[len(sizing_results_list)-1][name]
				
				# Size the transistors of this subcircuit
				if quick_mode_dict[name] == 1:
					sizing_results_dict[name], sizing_results_detailed_dict[name] = size_subcircuit_transistors(fpga_inst, hardblock.dedicated, opt_type, re_erf, area_opt_weight, delay_opt_weight, iteration, starting_transistor_sizes, spice_interface, 0, 0)
				else:
					sizing_results_dict[name]= sizing_results_list[len(sizing_results_list)-1][name]
					sizing_results_detailed_dict[name] = sizing_results_detailed_list[len(sizing_results_list)-1][name]   

			name = hardblock.mux.name
			# If this is the first iteration, use the 'initial_transistor_sizes' as the starting sizes. 
			# If it's not the first iteration, we use the transistor sizes of the previous iteration as the starting sizes.
			if iteration == 1:
				quick_mode_dict[name] = 1
				starting_transistor_sizes = format_transistor_sizes_to_basic_subciruits(hardblock.mux.initial_transistor_sizes)
			else:
				starting_transistor_sizes = sizing_results_list[len(sizing_results_list)-1][name]
			
			# Size the transistors of this subcircuit
			if quick_mode_dict[name] == 1:
				sizing_results_dict[name], sizing_results_detailed_dict[name] = size_subcircuit_transistors(fpga_inst, hardblock.mux, opt_type, re_erf, area_opt_weight, delay_opt_weight, iteration, starting_transistor_sizes, spice_interface, 0, 0)
			else:
				sizing_results_dict[name]= sizing_results_list[len(sizing_results_list)-1][name]
				sizing_results_detailed_dict[name] = sizing_results_detailed_list[len(sizing_results_list)-1][name]   

			time_before_sizing = time.time()



		if size_hb_interfaces == 0.0:
			############################################
			## Size switch block mux transistors
			############################################
			name = fpga_inst.sb_mux.name
			# If this is the first iteration, use the 'initial_transistor_sizes' as the 
			# starting sizes. If it's not the first iteration, we use the transistor sizes 
			# of the previous iteration as the starting sizes.
			if iteration == 1:
				quick_mode_dict[name] = 1
				starting_transistor_sizes = format_transistor_sizes_to_basic_subciruits(
												fpga_inst.sb_mux.initial_transistor_sizes)
			else:
				starting_transistor_sizes = sizing_results_list[len(sizing_results_list)-1][name]

			# Size the transistors of this subcircuit
			if quick_mode_dict[name] == 1:
				sizing_results_dict[name], sizing_results_detailed_dict[name] = size_subcircuit_transistors(fpga_inst, fpga_inst.sb_mux, opt_type, re_erf, area_opt_weight, delay_opt_weight, iteration, starting_transistor_sizes, spice_interface, 0, 0)
			else:
				sizing_results_dict[name]= sizing_results_list[len(sizing_results_list)-1][name]
				sizing_results_detailed_dict[name] = sizing_results_detailed_list[len(sizing_results_list)-1][name]

				# update quick mode status and display duration
			if quick_mode_dict[name] == 1:
				time_after_sizing = time.time()
				
				past_cost = current_cost
				current_cost =  cost_function(get_eval_area(fpga_inst, "global", fpga_inst.sb_mux, 0, 0), get_current_delay(fpga_inst, 0), area_opt_weight, delay_opt_weight)   
				if (past_cost - current_cost)/past_cost <fpga_inst.specs.quick_mode_threshold:
					quick_mode_dict[name] = 0

				print("Duration: " + str(time_after_sizing - time_before_sizing))
				print("Current Cost: " + str(current_cost))

			time_before_sizing = time.time()

			############################################
			## Size connection block mux transistors
			############################################
			name = fpga_inst.cb_mux.name
			# If this is the first iteration, use the 'initial_transistor_sizes' as the starting sizes. 
			# If it's not the first iteration, we use the transistor sizes of the previous iteration as the starting sizes.
			if iteration == 1:
				quick_mode_dict[name] = 1
				starting_transistor_sizes = format_transistor_sizes_to_basic_subciruits(fpga_inst.cb_mux.initial_transistor_sizes)
			else:
				starting_transistor_sizes = sizing_results_list[len(sizing_results_list)-1][name]
				
			# Size the transistors of this subcircuit
			if quick_mode_dict[name] == 1:
				sizing_results_dict[name], sizing_results_detailed_dict[name] = size_subcircuit_transistors(fpga_inst, fpga_inst.cb_mux, opt_type, re_erf, area_opt_weight, delay_opt_weight, iteration, starting_transistor_sizes, spice_interface, 0, 0)
			else:
				sizing_results_dict[name]= sizing_results_list[len(sizing_results_list)-1][name]
				sizing_results_detailed_dict[name] = sizing_results_detailed_list[len(sizing_results_list)-1][name]
		
				# update quick mode status and display duration
			if quick_mode_dict[name] == 1:
				time_after_sizing = time.time()
				
				past_cost = current_cost
				current_cost =  cost_function(get_eval_area(fpga_inst, "global", fpga_inst.sb_mux, 0, 0), get_current_delay(fpga_inst, 0), area_opt_weight, delay_opt_weight)   
				if (past_cost - current_cost)/past_cost <fpga_inst.specs.quick_mode_threshold:
					quick_mode_dict[name] = 0

				print("Duration: " + str(time_after_sizing - time_before_sizing))
				print("Current Cost: " + str(current_cost))

			time_before_sizing = time.time()


			############################################
			## Size local routing mux transistors
			############################################
			name = fpga_inst.logic_cluster.local_mux.name
			# If this is the first iteration, use the 'initial_transistor_sizes' as the starting sizes. 
			# If it's not the first iteration, we use the transistor sizes of the previous iteration as the starting sizes.
			if iteration == 1:
				quick_mode_dict[name] = 1
				starting_transistor_sizes = format_transistor_sizes_to_basic_subciruits(fpga_inst.logic_cluster.local_mux.initial_transistor_sizes)
			else:
				starting_transistor_sizes = sizing_results_list[len(sizing_results_list)-1][name]
			
			# Size the transistors of this subcircuit
			if quick_mode_dict[name] == 1:
				sizing_results_dict[name], sizing_results_detailed_dict[name] = size_subcircuit_transistors(fpga_inst, fpga_inst.logic_cluster.local_mux, opt_type, re_erf, area_opt_weight, delay_opt_weight, iteration, starting_transistor_sizes, spice_interface, 0, 0)
			else:
				sizing_results_dict[name]= sizing_results_list[len(sizing_results_list)-1][name]
				sizing_results_detailed_dict[name] = sizing_results_detailed_list[len(sizing_results_list)-1][name]        

				# update quick mode status and display duration
			if quick_mode_dict[name] == 1:
				time_after_sizing = time.time()
				
				past_cost = current_cost
				current_cost =  cost_function(get_eval_area(fpga_inst, "global", fpga_inst.sb_mux, 0, 0), get_current_delay(fpga_inst, 0), area_opt_weight, delay_opt_weight)   
				if (past_cost - current_cost)/past_cost <fpga_inst.specs.quick_mode_threshold:
					quick_mode_dict[name] = 0

				print("Duration: " + str(time_after_sizing - time_before_sizing))
				print("Current Cost: " + str(current_cost))

			time_before_sizing = time.time()


			############################################
			## Size LUT
			############################################
			# We actually size the LUT before the LUT drivers even if this means going out of the normal signal propagation order because
			# LUT driver sizing depends on LUT transistor sizes, and also, LUT rise-fall balancing doesn't depend on LUT drivers.
			name = fpga_inst.logic_cluster.ble.lut.name
			# If this is the first iteration, use the 'initial_transistor_sizes' as the starting sizes. 
			# If it's not the first iteration, we use the transistor sizes of the previous iteration as the starting sizes.
			if iteration == 1:
				quick_mode_dict[name] = 1
				starting_transistor_sizes = format_transistor_sizes_to_basic_subciruits(fpga_inst.logic_cluster.ble.lut.initial_transistor_sizes)
			else:
				starting_transistor_sizes = sizing_results_list[len(sizing_results_list)-1][name]
			
			# Size the transistors of this subcircuit
			if quick_mode_dict[name] == 1:
				sizing_results_dict[name], sizing_results_detailed_dict[name] = size_subcircuit_transistors(fpga_inst, fpga_inst.logic_cluster.ble.lut, opt_type, re_erf, area_opt_weight, delay_opt_weight, iteration, starting_transistor_sizes, spice_interface, 0, 0)
			else:
				sizing_results_dict[name]= sizing_results_list[len(sizing_results_list)-1][name]
				sizing_results_detailed_dict[name] = sizing_results_detailed_list[len(sizing_results_list)-1][name]      

				# update quick mode status and display duration
			if quick_mode_dict[name] == 1:
				time_after_sizing = time.time()
				
				past_cost = current_cost
				current_cost =  cost_function(get_eval_area(fpga_inst, "global", fpga_inst.sb_mux, 0, 0), get_current_delay(fpga_inst, 0), area_opt_weight, delay_opt_weight)   
				if (past_cost - current_cost)/past_cost <fpga_inst.specs.quick_mode_threshold:
					quick_mode_dict[name] = 0

				print("Duration: " + str(time_after_sizing - time_before_sizing))
				print("Current Cost: " + str(current_cost))

			time_before_sizing = time.time()

			############################################
			## Size FLUT internal mux
			############################################
			if fpga_inst.specs.use_fluts:
				name = fpga_inst.logic_cluster.ble.fmux.name
				# If this is the first iteration, use the 'initial_transistor_sizes' as the starting sizes. 
				# If it's not the first iteration, we use the transistor sizes of the previous iteration as the starting sizes.
				if iteration == 1:
					quick_mode_dict[name] = 1
					starting_transistor_sizes = format_transistor_sizes_to_basic_subciruits(fpga_inst.logic_cluster.ble.fmux.initial_transistor_sizes)
				else:
					starting_transistor_sizes = sizing_results_list[len(sizing_results_list)-1][name]
				
				# Size the transistors of this subcircuit
				if quick_mode_dict[name] == 1:
					sizing_results_dict[name], sizing_results_detailed_dict[name] = size_subcircuit_transistors(fpga_inst, fpga_inst.logic_cluster.ble.fmux, opt_type, re_erf, area_opt_weight, delay_opt_weight, iteration, starting_transistor_sizes, spice_interface, 0, 0)
				else:
					sizing_results_dict[name]= sizing_results_list[len(sizing_results_list)-1][name]
					sizing_results_detailed_dict[name] = sizing_results_detailed_list[len(sizing_results_list)-1][name]      

					# update quick mode status and display duration
				if quick_mode_dict[name] == 1:
					time_after_sizing = time.time()
					
					past_cost = current_cost
					current_cost =  cost_function(get_eval_area(fpga_inst, "global", fpga_inst.sb_mux, 0, 0), get_current_delay(fpga_inst, 0), area_opt_weight, delay_opt_weight)   
					if (past_cost - current_cost)/past_cost <fpga_inst.specs.quick_mode_threshold:
						quick_mode_dict[name] = 0

					print("Duration: " + str(time_after_sizing - time_before_sizing))
					print("Current Cost: " + str(current_cost))

				time_before_sizing = time.time()
				
			############################################
			## Size LUT input drivers
			############################################
			for input_driver_name, input_driver in fpga_inst.logic_cluster.ble.lut.input_drivers.items():
				# Driver
				# If this is the first iteration, use the 'initial_transistor_sizes' as the starting sizes. 
				# If it's not the first iteration, we use the transistor sizes of the previous iteration as the starting sizes.
				if iteration == 1:
					quick_mode_dict["input_drivers"] = 1
					starting_transistor_sizes = format_transistor_sizes_to_basic_subciruits(input_driver.driver.initial_transistor_sizes)
				else:
					starting_transistor_sizes = sizing_results_list[len(sizing_results_list)-1][input_driver.driver.name]
				
				# Size the transistors of this subcircuit
				if quick_mode_dict["input_drivers"] == 1:
					sizing_results_dict[input_driver.driver.name], sizing_results_detailed_dict[input_driver.driver.name] = size_subcircuit_transistors(fpga_inst, input_driver.driver, opt_type, re_erf, area_opt_weight, delay_opt_weight, iteration, starting_transistor_sizes, spice_interface, 0, 0)
				else:
					sizing_results_dict[input_driver.driver.name]= sizing_results_list[len(sizing_results_list)-1][input_driver.driver.name]
					sizing_results_detailed_dict[input_driver.driver.name] = sizing_results_detailed_list[len(sizing_results_list)-1][input_driver.driver.name]   

				# Not driver
				# If this is the first iteration, use the 'initial_transistor_sizes' as the starting sizes. 
				# If it's not the first iteration, we use the transistor sizes of the previous iteration as the starting sizes.
				if iteration == 1:
					starting_transistor_sizes = format_transistor_sizes_to_basic_subciruits(input_driver.not_driver.initial_transistor_sizes)
				else:
					starting_transistor_sizes = sizing_results_list[len(sizing_results_list)-1][input_driver.not_driver.name]
				
				# Size the transistors of this subcircuit
				if quick_mode_dict["input_drivers"] == 1:
					sizing_results_dict[input_driver.not_driver.name], sizing_results_detailed_dict[input_driver.not_driver.name] = size_subcircuit_transistors(fpga_inst, input_driver.not_driver, opt_type, re_erf, area_opt_weight, delay_opt_weight, iteration, starting_transistor_sizes, spice_interface, 0, 0)
				else:
					sizing_results_dict[input_driver.not_driver.name]= sizing_results_list[len(sizing_results_list)-1][input_driver.not_driver.name]
					sizing_results_detailed_dict[input_driver.not_driver.name] = sizing_results_detailed_list[len(sizing_results_list)-1][input_driver.not_driver.name]      

			if quick_mode_dict["input_drivers"] == 1:
				time_after_sizing = time.time()
				
				past_cost = current_cost
				current_cost =  cost_function(get_eval_area(fpga_inst, "global", fpga_inst.sb_mux, 0, 0), get_current_delay(fpga_inst, 0), area_opt_weight, delay_opt_weight)   
				if (past_cost - current_cost)/past_cost < fpga_inst.specs.quick_mode_threshold:
					quick_mode_dict["input_drivers"] = 0

				print("Duration: " + str(time_after_sizing - time_before_sizing))
				print("Current Cost: " + str(current_cost))

			time_before_sizing = time.time()

			############################################        
			## Size local ble output transistors
			############################################
			name = fpga_inst.logic_cluster.ble.local_output.name
			# If this is the first iteration, use the 'initial_transistor_sizes' as the starting sizes. 
			# If it's not the first iteration, we use the transistor sizes of the previous iteration as the starting sizes.
			if iteration == 1:
				quick_mode_dict[name] = 1
				starting_transistor_sizes = format_transistor_sizes_to_basic_subciruits(fpga_inst.logic_cluster.ble.local_output.initial_transistor_sizes)
			else:
				starting_transistor_sizes = sizing_results_list[len(sizing_results_list)-1][name]
			
			# Size the transistors of this subcircuit
			if quick_mode_dict[name] == 1:
				sizing_results_dict[name], sizing_results_detailed_dict[name] = size_subcircuit_transistors(fpga_inst, fpga_inst.logic_cluster.ble.local_output, opt_type, re_erf, area_opt_weight, delay_opt_weight, iteration, starting_transistor_sizes, spice_interface, 0, 0)
			else:
				sizing_results_dict[name]= sizing_results_list[len(sizing_results_list)-1][name]
				sizing_results_detailed_dict[name] = sizing_results_detailed_list[len(sizing_results_list)-1][name]   
			
			if quick_mode_dict[name] == 1:
				time_after_sizing = time.time()
				
				past_cost = current_cost
				current_cost =  cost_function(get_eval_area(fpga_inst, "global", fpga_inst.sb_mux, 0, 0), get_current_delay(fpga_inst, 0), area_opt_weight, delay_opt_weight)   
				if (past_cost - current_cost)/past_cost < fpga_inst.specs.quick_mode_threshold:
					quick_mode_dict[name] = 0

				print("Duration: " + str(time_after_sizing - time_before_sizing))
				print("Current Cost: " + str(current_cost))

			time_before_sizing = time.time()

			############################################
			## Size general ble output transistors
			############################################
			name = fpga_inst.logic_cluster.ble.general_output.name
			# If this is the first iteration, use the 'initial_transistor_sizes' as the starting sizes. 
			# If it's not the first iteration, we use the transistor sizes of the previous iteration as the starting sizes.
			if iteration == 1:
				quick_mode_dict[name] = 1
				starting_transistor_sizes = format_transistor_sizes_to_basic_subciruits(fpga_inst.logic_cluster.ble.general_output.initial_transistor_sizes)
			else:
				starting_transistor_sizes = sizing_results_list[len(sizing_results_list)-1][name]
			
			# Size the transistors of this subcircuit
			if quick_mode_dict[name] == 1:
				sizing_results_dict[name], sizing_results_detailed_dict[name] = size_subcircuit_transistors(fpga_inst, fpga_inst.logic_cluster.ble.general_output, opt_type, re_erf, area_opt_weight, delay_opt_weight, iteration, starting_transistor_sizes, spice_interface, 0, 0)
			else:
				sizing_results_dict[name]= sizing_results_list[len(sizing_results_list)-1][name]
				sizing_results_detailed_dict[name] = sizing_results_detailed_list[len(sizing_results_list)-1][name]   

			if quick_mode_dict[name] == 1:
				time_after_sizing = time.time()
				
				past_cost = current_cost
				current_cost =  cost_function(get_eval_area(fpga_inst, "global", fpga_inst.sb_mux, 0, 0), get_current_delay(fpga_inst, 0), area_opt_weight, delay_opt_weight)   
				if (past_cost - current_cost)/past_cost < fpga_inst.specs.quick_mode_threshold:
					quick_mode_dict[name] = 0

				print("Duration: " + str(time_after_sizing - time_before_sizing))
				print("Current Cost: " + str(current_cost))

				current_cost =  cost_function(get_eval_area(fpga_inst, "global", fpga_inst.sb_mux, 1, 0), get_current_delay(fpga_inst, 1), area_opt_weight, delay_opt_weight)   

			time_before_sizing = time.time()

			
			if fpga_inst.specs.enable_carry_chain == 1:
				############################################
				## Size Carry Chain
				############################################
				name = fpga_inst.carrychain.name
				# If this is the first iteration, use the 'initial_transistor_sizes' as the starting sizes. 
				# If it's not the first iteration, we use the transistor sizes of the previous iteration as the starting sizes.
				if iteration == 1:
					quick_mode_dict[name] = 1
					starting_transistor_sizes = format_transistor_sizes_to_basic_subciruits(fpga_inst.carrychain.initial_transistor_sizes)
				else:
					starting_transistor_sizes = sizing_results_list[len(sizing_results_list)-1][name]
				
				# Size the transistors of this subcircuit
				if quick_mode_dict[name] == 1:
					sizing_results_dict[name], sizing_results_detailed_dict[name] = size_subcircuit_transistors(fpga_inst, fpga_inst.carrychain, opt_type, re_erf, area_opt_weight, delay_opt_weight, iteration, starting_transistor_sizes, spice_interface, 0, 1)
				else:
					sizing_results_dict[name]= sizing_results_list[len(sizing_results_list)-1][name]
					sizing_results_detailed_dict[name] = sizing_results_detailed_list[len(sizing_results_list)-1][name]   

				if quick_mode_dict[name] == 1:
					time_after_sizing = time.time()
					
					past_cost = current_cost
					current_cost =  cost_function(get_eval_area(fpga_inst, "global", fpga_inst.sb_mux, 1, 1), get_current_delay(fpga_inst, 0), area_opt_weight, delay_opt_weight)   
					if (past_cost - current_cost)/past_cost < fpga_inst.specs.quick_mode_threshold:
						quick_mode_dict[name] = 0

					print("Duration: " + str(time_after_sizing - time_before_sizing))
					print("Current Cost: " + str(current_cost))

					current_cost =  cost_function(get_eval_area(fpga_inst, "global", fpga_inst.sb_mux, 1, 1), get_current_delay(fpga_inst, 1), area_opt_weight, delay_opt_weight)   

				time_before_sizing = time.time()


				############################################
				## Size Carry Chain Sum Path
				############################################
				name = fpga_inst.carrychainperf.name
				# If this is the first iteration, use the 'initial_transistor_sizes' as the starting sizes. 
				# If it's not the first iteration, we use the transistor sizes of the previous iteration as the starting sizes.
				if iteration == 1:
					quick_mode_dict[name] = 1
					starting_transistor_sizes = format_transistor_sizes_to_basic_subciruits(fpga_inst.carrychainperf.initial_transistor_sizes)
				else:
					starting_transistor_sizes = sizing_results_list[len(sizing_results_list)-1][name]
				
				# Size the transistors of this subcircuit
				if quick_mode_dict[name] == 1:
					sizing_results_dict[name], sizing_results_detailed_dict[name] = size_subcircuit_transistors(fpga_inst, fpga_inst.carrychainperf, opt_type, re_erf, area_opt_weight, delay_opt_weight, iteration, starting_transistor_sizes, spice_interface, 0, 1)
				else:
					sizing_results_dict[name]= sizing_results_list[len(sizing_results_list)-1][name]
					sizing_results_detailed_dict[name] = sizing_results_detailed_list[len(sizing_results_list)-1][name]   

				if quick_mode_dict[name] == 1:
					time_after_sizing = time.time()
					
					past_cost = current_cost
					current_cost =  cost_function(get_eval_area(fpga_inst, "global", fpga_inst.sb_mux, 1, 1), get_current_delay(fpga_inst, 0), area_opt_weight, delay_opt_weight)   
					if (past_cost - current_cost)/past_cost < fpga_inst.specs.quick_mode_threshold:
						quick_mode_dict[name] = 0

					print("Duration: " + str(time_after_sizing - time_before_sizing))
					print("Current Cost: " + str(current_cost))

					current_cost =  cost_function(get_eval_area(fpga_inst, "global", fpga_inst.sb_mux, 1, 1), get_current_delay(fpga_inst, 1), area_opt_weight, delay_opt_weight)   

				time_before_sizing = time.time()


				############################################
				## Size Carry Inter Cluster Path
				############################################
				name = fpga_inst.carrychaininter.name
				# If this is the first iteration, use the 'initial_transistor_sizes' as the starting sizes. 
				# If it's not the first iteration, we use the transistor sizes of the previous iteration as the starting sizes.
				if iteration == 1:
					quick_mode_dict[name] = 1
					starting_transistor_sizes = format_transistor_sizes_to_basic_subciruits(fpga_inst.carrychaininter.initial_transistor_sizes)
				else:
					starting_transistor_sizes = sizing_results_list[len(sizing_results_list)-1][name]
				
				# Size the transistors of this subcircuit
				if quick_mode_dict[name] == 1:
					sizing_results_dict[name], sizing_results_detailed_dict[name] = size_subcircuit_transistors(fpga_inst, fpga_inst.carrychaininter, opt_type, re_erf, area_opt_weight, delay_opt_weight, iteration, starting_transistor_sizes, spice_interface, 0, 1)
				else:
					sizing_results_dict[name]= sizing_results_list[len(sizing_results_list)-1][name]
					sizing_results_detailed_dict[name] = sizing_results_detailed_list[len(sizing_results_list)-1][name]   

				if quick_mode_dict[name] == 1:
					time_after_sizing = time.time()
					
					past_cost = current_cost
					current_cost =  cost_function(get_eval_area(fpga_inst, "global", fpga_inst.sb_mux, 1, 1), get_current_delay(fpga_inst, 0), area_opt_weight, delay_opt_weight)   
					if (past_cost - current_cost)/past_cost < fpga_inst.specs.quick_mode_threshold:
						quick_mode_dict[name] = 0

					print("Duration: " + str(time_after_sizing - time_before_sizing))
					print("Current Cost: " + str(current_cost))

					current_cost =  cost_function(get_eval_area(fpga_inst, "global", fpga_inst.sb_mux, 1, 1), get_current_delay(fpga_inst, 1), area_opt_weight, delay_opt_weight)   

				time_before_sizing = time.time()


				############################################
				## Size Carry Chain (SKIP) components
				############################################
				if fpga_inst.specs.carry_chain_type == "skip":
					name = fpga_inst.carrychainand.name
					# If this is the first iteration, use the 'initial_transistor_sizes' as the starting sizes. 
					# If it's not the first iteration, we use the transistor sizes of the previous iteration as the starting sizes.
					if iteration == 1:
						quick_mode_dict[name] = 1
						starting_transistor_sizes = format_transistor_sizes_to_basic_subciruits(fpga_inst.carrychainand.initial_transistor_sizes)
					else:
						starting_transistor_sizes = sizing_results_list[len(sizing_results_list)-1][name]
					
					# Size the transistors of this subcircuit
					if quick_mode_dict[name] == 1:
						sizing_results_dict[name], sizing_results_detailed_dict[name] = size_subcircuit_transistors(fpga_inst, fpga_inst.carrychainand, opt_type, re_erf, area_opt_weight, delay_opt_weight, iteration, starting_transistor_sizes, spice_interface, 0, 1)
					else:
						sizing_results_dict[name]= sizing_results_list[len(sizing_results_list)-1][name]
						sizing_results_detailed_dict[name] = sizing_results_detailed_list[len(sizing_results_list)-1][name]   

					if quick_mode_dict[name] == 1:
						time_after_sizing = time.time()
						
						past_cost = current_cost
						current_cost =  cost_function(get_eval_area(fpga_inst, "global", fpga_inst.sb_mux, 1, 1), get_current_delay(fpga_inst, 0), area_opt_weight, delay_opt_weight)   
						if (past_cost - current_cost)/past_cost < fpga_inst.specs.quick_mode_threshold:
							quick_mode_dict[name] = 0

						print("Duration: " + str(time_after_sizing - time_before_sizing))
						print("Current Cost: " + str(current_cost))

						current_cost =  cost_function(get_eval_area(fpga_inst, "global", fpga_inst.sb_mux, 1, 1), get_current_delay(fpga_inst, 1), area_opt_weight, delay_opt_weight)   

					time_before_sizing = time.time()

				if fpga_inst.specs.carry_chain_type == "skip":
					name = fpga_inst.carrychainskipmux.name
					# If this is the first iteration, use the 'initial_transistor_sizes' as the starting sizes. 
					# If it's not the first iteration, we use the transistor sizes of the previous iteration as the starting sizes.
					if iteration == 1:
						quick_mode_dict[name] = 1
						starting_transistor_sizes = format_transistor_sizes_to_basic_subciruits(fpga_inst.carrychainskipmux.initial_transistor_sizes)
					else:
						starting_transistor_sizes = sizing_results_list[len(sizing_results_list)-1][name]
					
					# Size the transistors of this subcircuit
					if quick_mode_dict[name] == 1:
						sizing_results_dict[name], sizing_results_detailed_dict[name] = size_subcircuit_transistors(fpga_inst, fpga_inst.carrychainskipmux, opt_type, re_erf, area_opt_weight, delay_opt_weight, iteration, starting_transistor_sizes, spice_interface, 0, 1)
					else:
						sizing_results_dict[name]= sizing_results_list[len(sizing_results_list)-1][name]
						sizing_results_detailed_dict[name] = sizing_results_detailed_list[len(sizing_results_list)-1][name]   

					if quick_mode_dict[name] == 1:
						time_after_sizing = time.time()
						
						past_cost = current_cost
						current_cost =  cost_function(get_eval_area(fpga_inst, "global", fpga_inst.sb_mux, 1, 1), get_current_delay(fpga_inst, 0), area_opt_weight, delay_opt_weight)   
						if (past_cost - current_cost)/past_cost < fpga_inst.specs.quick_mode_threshold:
							quick_mode_dict[name] = 0

						print("Duration: " + str(time_after_sizing - time_before_sizing))
						print("Current Cost: " + str(current_cost))

						current_cost =  cost_function(get_eval_area(fpga_inst, "global", fpga_inst.sb_mux, 1, 1), get_current_delay(fpga_inst, 1), area_opt_weight, delay_opt_weight)   

					time_before_sizing = time.time()


				############################################
				## Size Carry Chain Additional Mux
				############################################
				name = fpga_inst.carrychainmux.name
				# If this is the first iteration, use the 'initial_transistor_sizes' as the starting sizes. 
				# If it's not the first iteration, we use the transistor sizes of the previous iteration as the starting sizes.
				if iteration == 1:
					quick_mode_dict[name] = 1
					starting_transistor_sizes = format_transistor_sizes_to_basic_subciruits(fpga_inst.carrychainmux.initial_transistor_sizes)
				else:
					starting_transistor_sizes = sizing_results_list[len(sizing_results_list)-1][name]
				
				# Size the transistors of this subcircuit
				if quick_mode_dict[name] == 1:
					sizing_results_dict[name], sizing_results_detailed_dict[name] = size_subcircuit_transistors(fpga_inst, fpga_inst.carrychainmux, opt_type, re_erf, area_opt_weight, delay_opt_weight, iteration, starting_transistor_sizes, spice_interface, 0, 0)
				else:
					sizing_results_dict[name]= sizing_results_list[len(sizing_results_list)-1][name]
					sizing_results_detailed_dict[name] = sizing_results_detailed_list[len(sizing_results_list)-1][name]   

				if quick_mode_dict[name] == 1:
					time_after_sizing = time.time()
					
					past_cost = current_cost
					current_cost =  cost_function(get_eval_area(fpga_inst, "global", fpga_inst.sb_mux, 0, 0), get_current_delay(fpga_inst, 0), area_opt_weight, delay_opt_weight)   
					if (past_cost - current_cost)/past_cost < fpga_inst.specs.quick_mode_threshold:
						quick_mode_dict[name] = 0

					print("Duration: " + str(time_after_sizing - time_before_sizing))
					print("Current Cost: " + str(current_cost))

					current_cost =  cost_function(get_eval_area(fpga_inst, "global", fpga_inst.sb_mux, 0, 0), get_current_delay(fpga_inst, 1), area_opt_weight, delay_opt_weight)   

				time_before_sizing = time.time()




			if fpga_inst.specs.enable_bram_block == 1:
				############################################
				## Size RAM output crossbar
				############################################hsa

				name = fpga_inst.RAM.pgateoutputcrossbar.name
				# If this is the first iteration, use the 'initial_transistor_sizes' as the starting sizes. 
				# If it's not the first iteration, we use the transistor sizes of the previous iteration as the starting sizes.
				if iteration == 1:
					quick_mode_dict[name] = 1
					starting_transistor_sizes = format_transistor_sizes_to_basic_subciruits(fpga_inst.RAM.pgateoutputcrossbar.initial_transistor_sizes)
				else:
					starting_transistor_sizes = sizing_results_list[len(sizing_results_list)-1][name]
				
				# Size the transistors of this subcircuit
				if quick_mode_dict[name] == 1:
					sizing_results_dict[name], sizing_results_detailed_dict[name] = size_subcircuit_transistors(fpga_inst, fpga_inst.RAM.pgateoutputcrossbar, opt_type, re_erf, area_opt_weight, delay_opt_weight, iteration, starting_transistor_sizes, spice_interface, 1, 0)
				else:
					sizing_results_dict[name]= sizing_results_list[len(sizing_results_list)-1][name]
					sizing_results_detailed_dict[name] = sizing_results_detailed_list[len(sizing_results_list)-1][name]   

				if quick_mode_dict[name] == 1:
					time_after_sizing = time.time()
				
					past_cost = current_cost
					current_cost =  cost_function(get_eval_area(fpga_inst, "global", fpga_inst.sb_mux, 1, 0), get_current_delay(fpga_inst, 1), area_opt_weight, delay_opt_weight)   
					if (past_cost - current_cost)/past_cost < fpga_inst.specs.quick_mode_threshold:
						quick_mode_dict[name] = 0

					print("Duration: " + str(time_after_sizing - time_before_sizing))
					print("Current Cost: " + str(current_cost))

				time_before_sizing = time.time()

				############################################
				## Size RAM wordline driver
				############################################

				name = fpga_inst.RAM.wordlinedriver.name
				# If this is the first iteration, use the 'initial_transistor_sizes' as the starting sizes. 
				# If it's not the first iteration, we use the transistor sizes of the previous iteration as the starting sizes.
				if iteration == 1:
					quick_mode_dict[name] = 1
					starting_transistor_sizes = format_transistor_sizes_to_basic_subciruits(fpga_inst.RAM.wordlinedriver.initial_transistor_sizes)
				else:
					starting_transistor_sizes = sizing_results_list[len(sizing_results_list)-1][name]
					
				# Size the transistors of this subcircuit
				if quick_mode_dict[name] == 1:
					sizing_results_dict[name], sizing_results_detailed_dict[name] = size_subcircuit_transistors(fpga_inst, fpga_inst.RAM.wordlinedriver, opt_type, re_erf, area_opt_weight, delay_opt_weight, iteration, starting_transistor_sizes, spice_interface, 1, 0)
				else:
					sizing_results_dict[name]= sizing_results_list[len(sizing_results_list)-1][name]
					sizing_results_detailed_dict[name] = sizing_results_detailed_list[len(sizing_results_list)-1][name]   

				if quick_mode_dict[name] == 1:
					time_after_sizing = time.time()
				
					past_cost = current_cost
					current_cost =  cost_function(get_eval_area(fpga_inst, "global", fpga_inst.sb_mux, 1, 0), get_current_delay(fpga_inst, 1), area_opt_weight, delay_opt_weight)   
					if (past_cost - current_cost)/past_cost < fpga_inst.specs.quick_mode_threshold:
						quick_mode_dict[name] = 0

					print("Duration: " + str(time_after_sizing - time_before_sizing))
					print("Current Cost: " + str(current_cost))

				time_before_sizing = time.time()

				#######################################################
				## Size SRAM bitline precharge or MTJ bitline discharge
				#######################################################
				
				if fpga_inst.RAM.memory_technology =="SRAM":

					name = fpga_inst.RAM.precharge.name
					# If this is the first iteration, use the 'initial_transistor_sizes' as the starting sizes. 
					# If it's not the first iteration, we use the transistor sizes of the previous iteration as the starting sizes.
					if iteration == 1:
						quick_mode_dict[name] = 1
						starting_transistor_sizes = format_transistor_sizes_to_basic_subciruits(fpga_inst.RAM.precharge.initial_transistor_sizes)
					else:
						starting_transistor_sizes = sizing_results_list[len(sizing_results_list)-1][name]
					
					# Size the transistors of this subcircuit
					if quick_mode_dict[name] == 1:
						sizing_results_dict[name], sizing_results_detailed_dict[name] = size_subcircuit_transistors(fpga_inst, fpga_inst.RAM.precharge, opt_type, re_erf, area_opt_weight, delay_opt_weight, iteration, starting_transistor_sizes, spice_interface, 1, 0)
					else:
						sizing_results_dict[name]= sizing_results_list[len(sizing_results_list)-1][name]
						sizing_results_detailed_dict[name] = sizing_results_detailed_list[len(sizing_results_list)-1][name]   
				else:

					name = fpga_inst.RAM.bldischarging.name
					# If this is the first iteration, use the 'initial_transistor_sizes' as the starting sizes. 
					# If it's not the first iteration, we use the transistor sizes of the previous iteration as the starting sizes.
					if iteration == 1:
						quick_mode_dict[name] = 1
						starting_transistor_sizes = format_transistor_sizes_to_basic_subciruits(fpga_inst.RAM.bldischarging.initial_transistor_sizes)
					else:
						starting_transistor_sizes = sizing_results_list[len(sizing_results_list)-1][name]
					
					# Size the transistors of this subcircuit
					if quick_mode_dict[name] == 1:
						sizing_results_dict[name], sizing_results_detailed_dict[name] = size_subcircuit_transistors(fpga_inst, fpga_inst.RAM.bldischarging, opt_type, re_erf, area_opt_weight, delay_opt_weight, iteration, starting_transistor_sizes, spice_interface, 1, 0)
					else:
						sizing_results_dict[name]= sizing_results_list[len(sizing_results_list)-1][name]
						sizing_results_detailed_dict[name] = sizing_results_detailed_list[len(sizing_results_list)-1][name]   

				if quick_mode_dict[name] == 1:
					time_after_sizing = time.time()
				
					past_cost = current_cost
					current_cost =  cost_function(get_eval_area(fpga_inst, "global", fpga_inst.sb_mux, 1, 0), get_current_delay(fpga_inst, 1), area_opt_weight, delay_opt_weight)   
					if (past_cost - current_cost)/past_cost < fpga_inst.specs.quick_mode_threshold:
						quick_mode_dict[name] = 0

					print("Duration: " + str(time_after_sizing - time_before_sizing))
					print("Current Cost: " + str(current_cost))

				time_before_sizing = time.time()

				#######################################################
				## Size Row decoder, starting from the last stage backwards
				#######################################################

				name = fpga_inst.RAM.rowdecoder_stage3.name
				# If this is the first iteration, use the 'initial_transistor_sizes' as the starting sizes. 
				# If it's not the first iteration, we use the transistor sizes of the previous iteration as the starting sizes.
				if iteration == 1:
					quick_mode_dict["rowdecoder"] = 1
					starting_transistor_sizes = format_transistor_sizes_to_basic_subciruits(fpga_inst.RAM.rowdecoder_stage3.initial_transistor_sizes)
				else:
					starting_transistor_sizes = sizing_results_list[len(sizing_results_list)-1][name]
					
				# Size the transistors of this subcircuit
				if quick_mode_dict["rowdecoder"] == 1:
					sizing_results_dict[name], sizing_results_detailed_dict[name] = size_subcircuit_transistors(fpga_inst, fpga_inst.RAM.rowdecoder_stage3, opt_type, re_erf, area_opt_weight, delay_opt_weight, iteration, starting_transistor_sizes, spice_interface, 1, 0)
				else:
					sizing_results_dict[name]= sizing_results_list[len(sizing_results_list)-1][name]
					sizing_results_detailed_dict[name] = sizing_results_detailed_list[len(sizing_results_list)-1][name]   

				if fpga_inst.RAM.valid_row_dec_size3 == 1:
					name = fpga_inst.RAM.rowdecoder_stage1_size3.name
					# If this is the first iteration, use the 'initial_transistor_sizes' as the starting sizes. 
					# If it's not the first iteration, we use the transistor sizes of the previous iteration as the starting sizes.
					if iteration == 1:
						starting_transistor_sizes = format_transistor_sizes_to_basic_subciruits(fpga_inst.RAM.rowdecoder_stage1_size3.initial_transistor_sizes)
					else:
						starting_transistor_sizes = sizing_results_list[len(sizing_results_list)-1][name]
					
					# Size the transistors of this subcircuit
					if quick_mode_dict["rowdecoder"] == 1:
						sizing_results_dict[name], sizing_results_detailed_dict[name] = size_subcircuit_transistors(fpga_inst, fpga_inst.RAM.rowdecoder_stage1_size3, opt_type, re_erf, area_opt_weight, delay_opt_weight, iteration, starting_transistor_sizes, spice_interface, 1, 0)
					else:
						sizing_results_dict[name]= sizing_results_list[len(sizing_results_list)-1][name]
						sizing_results_detailed_dict[name] = sizing_results_detailed_list[len(sizing_results_list)-1][name]   

				if fpga_inst.RAM.valid_row_dec_size2 == 1:
					name = fpga_inst.RAM.rowdecoder_stage1_size2.name
					# If this is the first iteration, use the 'initial_transistor_sizes' as the starting sizes. 
					# If it's not the first iteration, we use the transistor sizes of the previous iteration as the starting sizes.
					if iteration == 1:
						starting_transistor_sizes = format_transistor_sizes_to_basic_subciruits(fpga_inst.RAM.rowdecoder_stage1_size2.initial_transistor_sizes)
					else:
						starting_transistor_sizes = sizing_results_list[len(sizing_results_list)-1][name]
					
					# Size the transistors of this subcircuit
					if quick_mode_dict["rowdecoder"] == 1:
						sizing_results_dict[name], sizing_results_detailed_dict[name] = size_subcircuit_transistors(fpga_inst, fpga_inst.RAM.rowdecoder_stage1_size2, opt_type, re_erf, area_opt_weight, delay_opt_weight, iteration, starting_transistor_sizes, spice_interface, 1, 0)
					else:
						sizing_results_dict[name]= sizing_results_list[len(sizing_results_list)-1][name]
						sizing_results_detailed_dict[name] = sizing_results_detailed_list[len(sizing_results_list)-1][name]   

				name = fpga_inst.RAM.rowdecoder_stage0.name
				# If this is the first iteration, use the 'initial_transistor_sizes' as the starting sizes. 
				# If it's not the first iteration, we use the transistor sizes of the previous iteration as the starting sizes.
				if iteration == 1:
					starting_transistor_sizes = format_transistor_sizes_to_basic_subciruits(fpga_inst.RAM.rowdecoder_stage0.initial_transistor_sizes)
				else:
					starting_transistor_sizes = sizing_results_list[len(sizing_results_list)-1][name]
				
				# Size the transistors of this subcircuit
				if quick_mode_dict["rowdecoder"] == 1:
					sizing_results_dict[name], sizing_results_detailed_dict[name] = size_subcircuit_transistors(fpga_inst, fpga_inst.RAM.rowdecoder_stage0, opt_type, re_erf, area_opt_weight, delay_opt_weight, iteration, starting_transistor_sizes, spice_interface, 1, 0)
				else:
					sizing_results_dict[name]= sizing_results_list[len(sizing_results_list)-1][name]
					sizing_results_detailed_dict[name] = sizing_results_detailed_list[len(sizing_results_list)-1][name]   



				if quick_mode_dict["rowdecoder"] == 1:
					time_after_sizing = time.time()
				
					past_cost = current_cost
					current_cost =  cost_function(get_eval_area(fpga_inst, "global", fpga_inst.sb_mux, 1, 0), get_current_delay(fpga_inst, 1), area_opt_weight, delay_opt_weight)   
					if (past_cost - current_cost)/past_cost < fpga_inst.specs.quick_mode_threshold:
						quick_mode_dict["rowdecoder"] = 0

					print("Duration: " + str(time_after_sizing - time_before_sizing))
					print("Current Cost: " + str(current_cost))

				time_before_sizing = time.time()

				#######################################################
				## Size Writedriver
				#######################################################

				# Write driver is no longer automatically sized since fixed values are provided by kosuke.
				# it can however be sized with minor changes. (check the other files where write driver is defined)
				#name = fpga_inst.RAM.writedriver.name
				# If this is the first iteration, use the 'initial_transistor_sizes' as the starting sizes. 
				# If it's not the first iteration, we use the transistor sizes of the previous iteration as the starting sizes.
				#if iteration == 1:
					#starting_transistor_sizes = format_transistor_sizes_to_basic_subciruits(fpga_inst.RAM.writedriver.initial_transistor_sizes)
				#else:
					#starting_transistor_sizes = sizing_results_list[len(sizing_results_list)-1][name]
				
				# Size the transistors of this subcircuit
				#sizing_results_dict[name], sizing_results_detailed_dict[name] = size_subcircuit_transistors(fpga_inst, fpga_inst.RAM.writedriver, opt_type, re_erf, area_opt_weight, delay_opt_weight, iteration, starting_transistor_sizes, spice_interface)

				############################################
				## Size memory local mux
				############################################

				name = fpga_inst.RAM.RAM_local_mux.name
				# If this is the first iteration, use the 'initial_transistor_sizes' as the starting sizes. 
				# If it's not the first iteration, we use the transistor sizes of the previous iteration as the starting sizes.
				if iteration == 1:
					quick_mode_dict[name] = 1
					starting_transistor_sizes = format_transistor_sizes_to_basic_subciruits(fpga_inst.RAM.RAM_local_mux.initial_transistor_sizes)
				else:
					starting_transistor_sizes = sizing_results_list[len(sizing_results_list)-1][name]
				
				# Size the transistors of this subcircuit
				if quick_mode_dict[name] == 1:
					sizing_results_dict[name], sizing_results_detailed_dict[name] = size_subcircuit_transistors(fpga_inst, fpga_inst.RAM.RAM_local_mux, opt_type, re_erf, area_opt_weight, delay_opt_weight, iteration, starting_transistor_sizes, spice_interface, 1, 0)
				else:
					sizing_results_dict[name]= sizing_results_list[len(sizing_results_list)-1][name]
					sizing_results_detailed_dict[name] = sizing_results_detailed_list[len(sizing_results_list)-1][name] 

				if quick_mode_dict[name] == 1:
					time_after_sizing = time.time()
				
					past_cost = current_cost
					current_cost =  cost_function(get_eval_area(fpga_inst, "global", fpga_inst.sb_mux, 1, 0), get_current_delay(fpga_inst, 1), area_opt_weight, delay_opt_weight)   
					if (past_cost - current_cost)/past_cost < fpga_inst.specs.quick_mode_threshold:
						quick_mode_dict[name] = 0

					print("Duration: " + str(time_after_sizing - time_before_sizing))
					print("Current Cost: " + str(current_cost))

				time_before_sizing = time.time()

				############################################
				## Size configurable decoder elements backwards
				############################################
				
				name = fpga_inst.RAM.configurabledecoderiii.name
				# If this is the first iteration, use the 'initial_transistor_sizes' as the starting sizes. 
				# If it's not the first iteration, we use the transistor sizes of the previous iteration as the starting sizes.
				if iteration == 1:
					quick_mode_dict["confdec"] = 1
					starting_transistor_sizes = format_transistor_sizes_to_basic_subciruits(fpga_inst.RAM.configurabledecoderiii.initial_transistor_sizes)
				else:
					starting_transistor_sizes = sizing_results_list[len(sizing_results_list)-1][name]
				
				# Size the transistors of this subcircuit
				if quick_mode_dict["confdec"] == 1:
					sizing_results_dict[name], sizing_results_detailed_dict[name] = size_subcircuit_transistors(fpga_inst, fpga_inst.RAM.configurabledecoderiii, opt_type, re_erf, area_opt_weight, delay_opt_weight, iteration, starting_transistor_sizes, spice_interface, 1, 0)
				else:
					sizing_results_dict[name]= sizing_results_list[len(sizing_results_list)-1][name]
					sizing_results_detailed_dict[name] = sizing_results_detailed_list[len(sizing_results_list)-1][name] 


				if fpga_inst.RAM.cvalidobj1 ==1:
					name = fpga_inst.RAM.configurabledecoder3ii.name
					# If this is the first iteration, use the 'initial_transistor_sizes' as the starting sizes. 
					# If it's not the first iteration, we use the transistor sizes of the previous iteration as the starting sizes.
					if iteration == 1:
						starting_transistor_sizes = format_transistor_sizes_to_basic_subciruits(fpga_inst.RAM.configurabledecoder3ii.initial_transistor_sizes)
					else:
						starting_transistor_sizes = sizing_results_list[len(sizing_results_list)-1][name]
				
					# Size the transistors of this subcircuit
					if quick_mode_dict["confdec"] == 1:
						sizing_results_dict[name], sizing_results_detailed_dict[name] = size_subcircuit_transistors(fpga_inst, fpga_inst.RAM.configurabledecoder3ii, opt_type, re_erf, area_opt_weight, delay_opt_weight, iteration, starting_transistor_sizes, spice_interface, 1, 0)
					else:
						sizing_results_dict[name]= sizing_results_list[len(sizing_results_list)-1][name]
						sizing_results_detailed_dict[name] = sizing_results_detailed_list[len(sizing_results_list)-1][name] 

				if fpga_inst.RAM.cvalidobj2 ==1:
					name = fpga_inst.RAM.configurabledecoder2ii.name
					# If this is the first iteration, use the 'initial_transistor_sizes' as the starting sizes. 
					# If it's not the first iteration, we use the transistor sizes of the previous iteration as the starting sizes.
					if iteration == 1:
						starting_transistor_sizes = format_transistor_sizes_to_basic_subciruits(fpga_inst.RAM.configurabledecoder2ii.initial_transistor_sizes)
					else:
						starting_transistor_sizes = sizing_results_list[len(sizing_results_list)-1][name]
				
					# Size the transistors of this subcircuit
					if quick_mode_dict["confdec"] == 1:
						sizing_results_dict[name], sizing_results_detailed_dict[name] = size_subcircuit_transistors(fpga_inst, fpga_inst.RAM.configurabledecoder2ii, opt_type, re_erf, area_opt_weight, delay_opt_weight, iteration, starting_transistor_sizes, spice_interface, 1, 0)
					else:
						sizing_results_dict[name]= sizing_results_list[len(sizing_results_list)-1][name]
						sizing_results_detailed_dict[name] = sizing_results_detailed_list[len(sizing_results_list)-1][name] 

				name = fpga_inst.RAM.configurabledecoderi.name
				# If this is the first iteration, use the 'initial_transistor_sizes' as the starting sizes. 
				# If it's not the first iteration, we use the transistor sizes of the previous iteration as the starting sizes.
				if iteration == 1:
					starting_transistor_sizes = format_transistor_sizes_to_basic_subciruits(fpga_inst.RAM.configurabledecoderi.initial_transistor_sizes)
				else:
					starting_transistor_sizes = sizing_results_list[len(sizing_results_list)-1][name]
				
				# Size the transistors of this subcircuit
				if quick_mode_dict["confdec"] == 1:
					sizing_results_dict[name], sizing_results_detailed_dict[name] = size_subcircuit_transistors(fpga_inst, fpga_inst.RAM.configurabledecoderi, opt_type, re_erf, area_opt_weight, delay_opt_weight, iteration, starting_transistor_sizes, spice_interface, 1, 0)
				else:
					sizing_results_dict[name]= sizing_results_list[len(sizing_results_list)-1][name]
					sizing_results_detailed_dict[name] = sizing_results_detailed_list[len(sizing_results_list)-1][name] 

				if quick_mode_dict["confdec"] == 1:
					time_after_sizing = time.time()
				
					past_cost = current_cost
					current_cost =  cost_function(get_eval_area(fpga_inst, "global", fpga_inst.sb_mux, 1, 0), get_current_delay(fpga_inst, 1), area_opt_weight, delay_opt_weight)   
					if (past_cost - current_cost)/past_cost < fpga_inst.specs.quick_mode_threshold:
						quick_mode_dict["confdec"] = 0

					print("Duration: " + str(time_after_sizing - time_before_sizing))
					print("Current Cost: " + str(current_cost))

				time_before_sizing = time.time()

				############################################
				## Size column decoder
				############################################
				
				name = fpga_inst.RAM.columndecoder.name
				# If this is the first iteration, use the 'initial_transistor_sizes' as the starting sizes. 
				# If it's not the first iteration, we use the transistor sizes of the previous iteration as the starting sizes.
				if iteration == 1:
					quick_mode_dict[name] = 1
					starting_transistor_sizes = format_transistor_sizes_to_basic_subciruits(fpga_inst.RAM.columndecoder.initial_transistor_sizes)
				else:
					starting_transistor_sizes = sizing_results_list[len(sizing_results_list)-1][name]
				
				if quick_mode_dict[name] == 1:
					sizing_results_dict[name], sizing_results_detailed_dict[name] = size_subcircuit_transistors(fpga_inst, fpga_inst.RAM.columndecoder, opt_type, re_erf, area_opt_weight, delay_opt_weight, iteration, starting_transistor_sizes, spice_interface, 1, 0)
				else:
					sizing_results_dict[name]= sizing_results_list[len(sizing_results_list)-1][name]
					sizing_results_detailed_dict[name] = sizing_results_detailed_list[len(sizing_results_list)-1][name] 

				if quick_mode_dict[name] == 1:
					time_after_sizing = time.time()
				
					past_cost = current_cost
					current_cost =  cost_function(get_eval_area(fpga_inst, "global", fpga_inst.sb_mux, 1, 0), get_current_delay(fpga_inst, 1), area_opt_weight, delay_opt_weight)   
					if (past_cost - current_cost)/past_cost < fpga_inst.specs.quick_mode_threshold:
						quick_mode_dict[name] = 0

					print("Duration: " + str(time_after_sizing - time_before_sizing))
					print("Current Cost: " + str(current_cost))

				time_before_sizing = time.time()

			############################################
			## Done sizing, update results lists
			############################################

		print("FPGA transistor sizing iteration complete!\n")
		
		sizing_results_list.append(sizing_results_dict.copy())
		sizing_results_detailed_list.append(sizing_results_detailed_dict.copy())
		
		#print "Current Cost: " + str(get_current_delay(fpga_inst, 0) * get_eval_area(fpga_inst, "global", fpga_inst.cb_mux, 0))
		#print "Current RAM Cost: " + str(get_current_delay(fpga_inst, 1) * get_eval_area(fpga_inst, "global", fpga_inst.cb_mux, 1))
		#fpga_inst.update_delays(spice_interface)
		#print "Current Cost: " + str(get_current_delay(fpga_inst, 0) * get_eval_area(fpga_inst, "global", fpga_inst.cb_mux, 0))
		#print "Current RAM Cost: " + str(get_current_delay(fpga_inst, 1) * get_eval_area(fpga_inst, "global", fpga_inst.cb_mux, 1))

		# Add subcircuit delays and area to list (need to copy because of mutability)
		area_results_list.append(fpga_inst.area_dict.copy())
		delay_results_list.append(fpga_inst.delay_dict.copy())
		
		# Print all sizing results to terminal
		print_results(opt_type, sizing_results_list, area_results_list, delay_results_list)
		
		# Export these same results to a file
		sizing_results_filename = "sizing_results/sizing_results_o" + str(iteration) + ".txt"
		export_sizing_results(sizing_results_filename, sizing_results_list, area_results_list, delay_results_list)
		
		# Check if transistor sizing is done
		is_done, final_result_index = check_if_done(sizing_results_list, area_results_list, delay_results_list, area_opt_weight, delay_opt_weight)

		# Update the above results with quickmode

		# TODO: Why is it taking the previous iteration results in case of a quick mode
		# from my  understanding the quick mode means that if the improvement in this 
		# iteration is less than the given value stop resizing this subcircuit. This 
		# means the means that probably the current results are the best so far.
		if 1 not in list(quick_mode_dict.values()):
			is_done = True
			final_result_index = iteration - 1

		sys.stdout.flush()
		final_report_file = open("sizing_results/sizes_iteration_" + str(iteration) + ".txt", 'w')
		print_final_transistor_size(fpga_inst, final_report_file)
		final_report_file.close()
		iteration += 1


	# There are two ways we can terminate the above while loop
	# If the algorithm terminates by itself, is_done will be true and final_results_index are the final sizing results
	# However, if is_done is false, that means we terminated because the maximum number of iterations was reached.
	# In that case, the sizing results to use are the last results in sizing_results_list
	if not is_done:
		final_result_index = len(sizing_results_list) - 1


	# final_result_index are the results we need to use
	final_transistor_sizes = sizing_results_list[final_result_index]
	final_transistor_sizes_detailed = sizing_results_detailed_list[final_result_index]

	# Make a dictionary that contains all transistor sizes (instead of a dictionary of dictionaries for each subcircuit)
	final_transistor_sizes_detailed_full = {}
	for subcircuit_name, subcircuit_sizes in final_transistor_sizes_detailed.items():
		final_transistor_sizes_detailed_full.update(subcircuit_sizes)
	
	# Update FPGA transistor sizes
	fpga_inst.transistor_sizes.update(final_transistor_sizes_detailed_full)
	# Calculate area of everything
	fpga_inst.update_area()
	# Re-calculate wire lengths
	fpga_inst.update_wires()
	# Update wire resistance and capacitance
	fpga_inst.update_wire_rc()
		   
	print("FPGA transistor sizing complete!\n")
	
	final_report_file = open("sizing_results_final.txt", 'w')
	print_final_transistor_size(fpga_inst, final_report_file)
	final_report_file.close()

	return 


def override_transistor_sizes(fpga_inst, initial_sizes) :
	# switch block mux transistors
	for trans in fpga_inst.sb_mux.initial_transistor_sizes :
		if trans in fpga_inst.sb_mux.initial_transistor_sizes and trans in initial_sizes:
			fpga_inst.sb_mux.initial_transistor_sizes[trans] = initial_sizes[trans]

	# connection block mux transistors
	for trans in fpga_inst.cb_mux.initial_transistor_sizes :
		if trans in fpga_inst.cb_mux.initial_transistor_sizes and trans in initial_sizes:
			fpga_inst.cb_mux.initial_transistor_sizes[trans] = initial_sizes[trans]

	# local routing mux transistors
	for trans in fpga_inst.logic_cluster.local_mux.initial_transistor_sizes :
		if trans in fpga_inst.logic_cluster.local_mux.initial_transistor_sizes and trans in initial_sizes:
			fpga_inst.logic_cluster.local_mux.initial_transistor_sizes[trans] = initial_sizes[trans]

	# LUT
	for trans in fpga_inst.logic_cluster.ble.lut.initial_transistor_sizes :
		if trans in fpga_inst.logic_cluster.ble.lut.initial_transistor_sizes and trans in initial_sizes:
			fpga_inst.logic_cluster.ble.lut.initial_transistor_sizes[trans] = initial_sizes[trans]

	# LUT input drivers
	for input_driver_name, input_driver in fpga_inst.logic_cluster.ble.lut.input_drivers.items():

		for trans in input_driver.driver.initial_transistor_sizes :
			if trans in input_driver.driver.initial_transistor_sizes and trans in initial_sizes:
				input_driver.driver.initial_transistor_sizes[trans] = initial_sizes[trans]

		for trans in input_driver.not_driver.initial_transistor_sizes :
			if trans in input_driver.not_driver.initial_transistor_sizes and trans in initial_sizes:
				input_driver.not_driver.initial_transistor_sizes[trans] = initial_sizes[trans]

	# local ble output transistors
	for trans in fpga_inst.logic_cluster.ble.local_output.initial_transistor_sizes :
		if trans in fpga_inst.logic_cluster.ble.local_output.initial_transistor_sizes and trans in initial_sizes:
			fpga_inst.logic_cluster.ble.local_output.initial_transistor_sizes[trans] = initial_sizes[trans]
	
	# general ble output transistors
	for trans in fpga_inst.logic_cluster.ble.general_output.initial_transistor_sizes :
		if trans in fpga_inst.logic_cluster.ble.general_output.initial_transistor_sizes and trans in initial_sizes:
			fpga_inst.logic_cluster.ble.general_output.initial_transistor_sizes[trans] = initial_sizes[trans]

	return 


def print_final_transistor_size(fpga_inst, report_file):
	"""
	Dump FPGA transistor sizes to a file.
	"""

	report_file.write("#final sizes\n")
	for trans in fpga_inst.transistor_sizes:
		report_file.write(trans + "  =  " + str(fpga_inst.transistor_sizes[trans]) + "\n")

	return 


		
