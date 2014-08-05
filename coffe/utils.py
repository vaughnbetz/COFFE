import sys
import os


def compare_tfall_trise(tfall, trise):
	""" Compare tfall and trise and returns largest value or -1.0
		-1.0 is return if something went wrong in SPICE """
	
	# Initialize output delay
	delay = -1.0
	
	# Compare tfall and trise
	if (tfall == 0.0) or (trise == 0.0):
		# Couldn't find one of the values in output
		# This is an error because maybe SPICE failed
		delay = -1.0
	elif tfall > trise:
		if tfall > 0.0:
			# tfall is positive and bigger than the trise, this is a valid result
			delay = tfall
		else:
			# Both tfall and trise are negative, this is an invalid result
			delay = -1.0
	elif trise >= tfall:
		if trise > 0.0:
			# trise is positive and larger or equal to tfall, this is value result
			delay = trise
		else:
			delay = -1.0
	else:
		delay = -1.0
		
	return delay
   
	
def print_area_and_delay(report_file, fpga_inst):
	""" Print area and delay per subcircuit """
	
	print "  SUBCIRCUIT AREA & DELAY"
	print "  -----------------------"

	report_file.write( "  SUBCIRCUIT AREA & DELAY\n")
	report_file.write( "  -----------------------\n")
	
	
	area_dict = fpga_inst.area_dict

	# I'm using 'ljust' to create neat columns for printing this data. 
	# If subcircuit names are changed, it might make this printing function 
	# not work as well. The 'ljust' constants would have to be adjusted accordingly.
	
	# Print the header
	print "  Subcircuit".ljust(24) + "Area (um^2)".ljust(13) + "Delay (ps)".ljust(13) + "trise (ps)".ljust(13) + "tfall (ps)".ljust(13)
	report_file.write("  Subcircuit".ljust(24) + "Area (um^2)".ljust(13) + "Delay (ps)".ljust(13) + "trise (ps)".ljust(13) + "tfall (ps)".ljust(13) + "\n")
	
	# Switch block mux
	print "  " + fpga_inst.sb_mux.name.ljust(22) + str(round(area_dict[fpga_inst.sb_mux.name]/1e6,3)).ljust(13) + str(round(fpga_inst.sb_mux.delay/1e-12,4)).ljust(13) + str(round(fpga_inst.sb_mux.tfall/1e-12,4)).ljust(13) + str(round(fpga_inst.sb_mux.trise/1e-12,4)).ljust(13)
	report_file.write( "  " + fpga_inst.sb_mux.name.ljust(22) + str(round(area_dict[fpga_inst.sb_mux.name]/1e6,3)).ljust(13) + str(round(fpga_inst.sb_mux.delay/1e-12,4)).ljust(13) + str(round(fpga_inst.sb_mux.tfall/1e-12,4)).ljust(13) + str(round(fpga_inst.sb_mux.trise/1e-12,4)).ljust(13) + "\n")
	
	# Connection block mux
	print "  " + fpga_inst.cb_mux.name.ljust(22) + str(round(area_dict[fpga_inst.cb_mux.name]/1e6,3)).ljust(13) + str(round(fpga_inst.cb_mux.delay/1e-12,4)).ljust(13) + str(round(fpga_inst.cb_mux.tfall/1e-12,4)).ljust(13) + str(round(fpga_inst.cb_mux.trise/1e-12,4)).ljust(13)
	report_file.write( "  " + fpga_inst.cb_mux.name.ljust(22) + str(round(area_dict[fpga_inst.cb_mux.name]/1e6,3)).ljust(13) + str(round(fpga_inst.cb_mux.delay/1e-12,4)).ljust(13) + str(round(fpga_inst.cb_mux.tfall/1e-12,4)).ljust(13) + str(round(fpga_inst.cb_mux.trise/1e-12,4)).ljust(13) + "\n")
	
	# Local mux
	print "  " + fpga_inst.logic_cluster.local_mux.name.ljust(22) + str(round(area_dict[fpga_inst.logic_cluster.local_mux.name]/1e6,3)).ljust(13) + str(round(fpga_inst.logic_cluster.local_mux.delay/1e-12,4)).ljust(13) + str(round(fpga_inst.logic_cluster.local_mux.tfall/1e-12,4)).ljust(13) + str(round(fpga_inst.logic_cluster.local_mux.trise/1e-12,4)).ljust(13)
	report_file.write( "  " + fpga_inst.logic_cluster.local_mux.name.ljust(22) + str(round(area_dict[fpga_inst.logic_cluster.local_mux.name]/1e6,3)).ljust(13) + str(round(fpga_inst.logic_cluster.local_mux.delay/1e-12,4)).ljust(13) + str(round(fpga_inst.logic_cluster.local_mux.tfall/1e-12,4)).ljust(13) + str(round(fpga_inst.logic_cluster.local_mux.trise/1e-12,4)).ljust(13) + "\n")
	
	# Local BLE output
	print "  " + fpga_inst.logic_cluster.ble.local_output.name.ljust(22) + str(round(area_dict[fpga_inst.logic_cluster.ble.local_output.name]/1e6,3)).ljust(13) + str(round(fpga_inst.logic_cluster.ble.local_output.delay/1e-12,4)).ljust(13) + str(round(fpga_inst.logic_cluster.ble.local_output.tfall/1e-12,4)).ljust(13) + str(round(fpga_inst.logic_cluster.ble.local_output.trise/1e-12,4)).ljust(13)
	report_file.write( "  " + fpga_inst.logic_cluster.ble.local_output.name.ljust(22) + str(round(area_dict[fpga_inst.logic_cluster.ble.local_output.name]/1e6,3)).ljust(13) + str(round(fpga_inst.logic_cluster.ble.local_output.delay/1e-12,4)).ljust(13) + str(round(fpga_inst.logic_cluster.ble.local_output.tfall/1e-12,4)).ljust(13) + str(round(fpga_inst.logic_cluster.ble.local_output.trise/1e-12,4)).ljust(13) + "\n")
	
	# General BLE output
	print "  " + fpga_inst.logic_cluster.ble.general_output.name.ljust(22) + str(round(area_dict[fpga_inst.logic_cluster.ble.general_output.name]/1e6,3)).ljust(13) + str(round(fpga_inst.logic_cluster.ble.general_output.delay/1e-12,4)).ljust(13) + str(round(fpga_inst.logic_cluster.ble.general_output.tfall/1e-12,4)).ljust(13) + str(round(fpga_inst.logic_cluster.ble.general_output.trise/1e-12,4)).ljust(13)
	report_file.write( "  " + fpga_inst.logic_cluster.ble.general_output.name.ljust(22) + str(round(area_dict[fpga_inst.logic_cluster.ble.general_output.name]/1e6,3)).ljust(13) + str(round(fpga_inst.logic_cluster.ble.general_output.delay/1e-12,4)).ljust(13) + str(round(fpga_inst.logic_cluster.ble.general_output.tfall/1e-12,4)).ljust(13) + str(round(fpga_inst.logic_cluster.ble.general_output.trise/1e-12,4)).ljust(13) + "\n")
	
	# LUT
	print "  " + fpga_inst.logic_cluster.ble.lut.name.ljust(22) + str(round(area_dict[fpga_inst.logic_cluster.ble.lut.name]/1e6,3)).ljust(13) + str(round(fpga_inst.logic_cluster.ble.lut.delay/1e-12,4)).ljust(13) + str(round(fpga_inst.logic_cluster.ble.lut.tfall/1e-12,4)).ljust(13) + str(round(fpga_inst.logic_cluster.ble.lut.trise/1e-12,4)).ljust(13)
	report_file.write( "  " + fpga_inst.logic_cluster.ble.lut.name.ljust(22) + str(round(area_dict[fpga_inst.logic_cluster.ble.lut.name]/1e6,3)).ljust(13) + str(round(fpga_inst.logic_cluster.ble.lut.delay/1e-12,4)).ljust(13) + str(round(fpga_inst.logic_cluster.ble.lut.tfall/1e-12,4)).ljust(13) + str(round(fpga_inst.logic_cluster.ble.lut.trise/1e-12,4)).ljust(13) + "\n")
	
	# Get LUT input names so that we can print inputs in sorted order
	lut_input_names = fpga_inst.logic_cluster.ble.lut.input_drivers.keys()
	lut_input_names.sort()
	  
	# LUT input drivers
	for input_name in lut_input_names:
		driver = fpga_inst.logic_cluster.ble.lut.input_drivers[input_name].driver
		not_driver = fpga_inst.logic_cluster.ble.lut.input_drivers[input_name].not_driver
		print "  " + driver.name.ljust(22) + str(round(area_dict[driver.name]/1e6,3)).ljust(13) + str(round(driver.delay/1e-12,4)).ljust(13) + str(round(driver.tfall/1e-12,4)).ljust(13) + str(round(driver.trise/1e-12,4)).ljust(13)
		print "  " + not_driver.name.ljust(22) + str(round(area_dict[not_driver.name]/1e6,3)).ljust(13) + str(round(not_driver.delay/1e-12,4)).ljust(13) + str(round(not_driver.tfall/1e-12,4)).ljust(13) + str(round(not_driver.trise/1e-12,4)).ljust(13)

		report_file.write( "  " + driver.name.ljust(22) + str(round(area_dict[driver.name]/1e6,3)).ljust(13) + str(round(driver.delay/1e-12,4)).ljust(13) + str(round(driver.tfall/1e-12,4)).ljust(13) + str(round(driver.trise/1e-12,4)).ljust(13) + "\n")
		report_file.write( "  " + not_driver.name.ljust(22) + str(round(area_dict[not_driver.name]/1e6,3)).ljust(13) + str(round(not_driver.delay/1e-12,4)).ljust(13) + str(round(not_driver.tfall/1e-12,4)).ljust(13) + str(round(not_driver.trise/1e-12,4)).ljust(13) + "\n")
	
	print ""
	report_file.write( "\n" )

	
def print_block_area(report_file, fpga_inst):
		""" Print physical area of important blocks (like SB, CB, LUT, etc.) in um^2 """
		
		tile = fpga_inst.area_dict["tile"]/1000000
		lut = fpga_inst.area_dict["lut_total"]/1000000
		ff = fpga_inst.area_dict["ff_total"]/1000000
		ble_output = fpga_inst.area_dict["ble_output_total"]/1000000
		local_mux = fpga_inst.area_dict["local_mux_total"]/1000000
		cb = fpga_inst.area_dict["cb_total"]/1000000
		sb = fpga_inst.area_dict["sb_total"]/1000000
		sanity_check = lut+ff+ble_output+local_mux+cb+sb
		
		print "  TILE AREA CONTRIBUTIONS"
		print "  -----------------------"
		print "  Block".ljust(20) + "Total Area (um^2)".ljust(20) + "Fraction of total tile area"
		print "  Tile".ljust(20) + str(round(tile,3)).ljust(20) + "100%"
		print "  LUT".ljust(20) + str(round(lut,3)).ljust(20) + str(round(lut/tile*100,3)) + "%"
		print "  FF".ljust(20) + str(round(ff,3)).ljust(20) + str(round(ff/tile*100,3)) + "%"
		print "  BLE output".ljust(20) + str(round(ble_output,3)).ljust(20) + str(round(ble_output/tile*100,3)) + "%"
		print "  Local mux".ljust(20) + str(round(local_mux,3)).ljust(20) + str(round(local_mux/tile*100,3)) + "%"
		print "  Connection block".ljust(20) + str(round(cb,3)).ljust(20) + str(round(cb/tile*100,3)) + "%"
		print "  Switch block".ljust(20) + str(round(sb,3)).ljust(20) + str(round(sb/tile*100,3)) + "%"
		print ""    

		report_file.write( "  TILE AREA CONTRIBUTIONS\n")
		report_file.write( "  -----------------------\n")
		report_file.write( "  Block".ljust(20) + "Total Area (um^2)".ljust(20) + "Fraction of total tile area\n")
		report_file.write( "  Tile".ljust(20) + str(round(tile,3)).ljust(20) + "100%\n")
		report_file.write( "  LUT".ljust(20) + str(round(lut,3)).ljust(20) + str(round(lut/tile*100,3)) + "%\n")
		report_file.write( "  FF".ljust(20) + str(round(ff,3)).ljust(20) + str(round(ff/tile*100,3)) + "%\n")
		report_file.write( "  BLE output".ljust(20) + str(round(ble_output,3)).ljust(20) + str(round(ble_output/tile*100,3)) + "%\n")
		report_file.write( "  Local mux".ljust(20) + str(round(local_mux,3)).ljust(20) + str(round(local_mux/tile*100,3)) + "%\n")
		report_file.write( "  Connection block".ljust(20) + str(round(cb,3)).ljust(20) + str(round(cb/tile*100,3)) + "%\n")
		report_file.write( "  Switch block".ljust(20) + str(round(sb,3)).ljust(20) + str(round(sb/tile*100,3)) + "%\n")
		report_file.write( "\n")
 

def print_vpr_delays(report_file, fpga_inst):

	print "  VPR DELAYS"
	print "  ----------"
	print "  Path".ljust(50) + "Delay (ps)"
	print "  Tdel (routing switch)".ljust(50) + str(fpga_inst.sb_mux.delay)
	print "  T_ipin_cblock (connection block mux)".ljust(50) + str(fpga_inst.cb_mux.delay)
	print "  CLB input -> BLE input (local CLB routing)".ljust(50) + str(fpga_inst.logic_cluster.local_mux.delay)
	print "  LUT output -> BLE input (local feedback)".ljust(50) + str(fpga_inst.logic_cluster.ble.local_output.delay)
	print "  LUT output -> CLB output (logic block output)".ljust(50) + str(fpga_inst.logic_cluster.ble.general_output.delay)

	report_file.write( "  VPR DELAYS" + "\n")
	report_file.write( "  ----------" + "\n")
	report_file.write( "  Path".ljust(50) + "Delay (ps)" + "\n")
	report_file.write( "  Tdel (routing switch)".ljust(50) + str(fpga_inst.sb_mux.delay) + "\n")
	report_file.write( "  T_ipin_cblock (connection block mux)".ljust(50) + str(fpga_inst.cb_mux.delay) + "\n")
	report_file.write( "  CLB input -> BLE input (local CLB routing)".ljust(50) + str(fpga_inst.logic_cluster.local_mux.delay) + "\n")
	report_file.write( "  LUT output -> BLE input (local feedback)".ljust(50) + str(fpga_inst.logic_cluster.ble.local_output.delay) + "\n")
	report_file.write( "  LUT output -> CLB output (logic block output)".ljust(50) + str(fpga_inst.logic_cluster.ble.general_output.delay) + "\n")
	
	# Figure out LUT delays
	lut_input_names = fpga_inst.logic_cluster.ble.lut.input_drivers.keys()
	lut_input_names.sort()
	for input_name in lut_input_names:
		lut_input = fpga_inst.logic_cluster.ble.lut.input_drivers[input_name]
		driver_delay = max(lut_input.driver.delay, lut_input.not_driver.delay)
		path_delay = lut_input.delay
		print ("  lut_" + input_name).ljust(50) + str(driver_delay+path_delay)
		report_file.write( ("  lut_" + input_name).ljust(50) + str(driver_delay+path_delay) + "\n")
	
	print ""
	report_file.write( "\n")
 

def print_vpr_areas(report_file, fpga_inst):

	print "  VPR AREAS"
	print "  ----------"
	print "  grid_logic_tile_area".ljust(50) + str(fpga_inst.area_dict["logic_cluster"]/fpga_inst.specs.min_width_tran_area)
	print "  ipin_mux_trans_size (connection block mux)".ljust(50) + str(fpga_inst.area_dict["ipin_mux_trans_size"]/fpga_inst.specs.min_width_tran_area)
	print "  mux_trans_size (routing switch)".ljust(50) + str(fpga_inst.area_dict["switch_mux_trans_size"]/fpga_inst.specs.min_width_tran_area)
	print "  buf_size (routing switch)".ljust(50) + str(fpga_inst.area_dict["switch_buf_size"]/fpga_inst.specs.min_width_tran_area)
	print ""

	report_file.write( "  VPR AREAS" + "\n")
	report_file.write( "  ----------" + "\n")
	report_file.write( "  grid_logic_tile_area".ljust(50) + str(fpga_inst.area_dict["logic_cluster"]/fpga_inst.specs.min_width_tran_area) + "\n")
	report_file.write( "  ipin_mux_trans_size (connection block mux)".ljust(50) + str(fpga_inst.area_dict["ipin_mux_trans_size"]/fpga_inst.specs.min_width_tran_area) + "\n")
	report_file.write( "  mux_trans_size (routing switch)".ljust(50) + str(fpga_inst.area_dict["switch_mux_trans_size"]/fpga_inst.specs.min_width_tran_area) + "\n")
	report_file.write( "  buf_size (routing switch)".ljust(50) + str(fpga_inst.area_dict["switch_buf_size"]/fpga_inst.specs.min_width_tran_area) + "\n")
	report_file.write( "\n")

	
def load_arch_params(filename, use_finfet):
	""" Parse the architecture description file and load values into dictionary. 
		Returns this dictionary.
		Will print error message and terminate program if an invalid parameter is found
		or if a parameter is missing.
		"""
	
	# This is the dictionary of parameters we expect to find
	arch_params = {
		'W': -1,
		'L': -1,
		'Fs': -1,
		'N': -1,
		'K': -1,
		'I': -1,
		'Fcin': -1.0,
		'Fcout': -1.0,
		'Or': -1,
		'Ofb': -1,
		'Fclocal': -1.0,
		'Rsel': "",
		'Rfb': "",
		'vdd': -1,
		'vsram': -1,
		'vsram_n': -1,
		'gate_length': -1,
		'min_tran_width': -1,
		'min_width_tran_area': -1,
		'sram_cell_area': -1,
		'gate_extension' : -1,
		'model_path': "",
		'model_library': "",
		'metal' : []

	}
	if use_finfet :
		arch_params['fin_height'] = -1
		arch_params['fin_width'] = -1
		arch_params['lg'] = -1
		arch_params['rest_length_factor'] = -1

	params_file = open(filename, 'r')
	for line in params_file:
	
		# Ignore comment lines
		if line.startswith('#'):
			continue
		
		# Remove line feeds and spaces
		line = line.replace('\n', '')
		line = line.replace('\r', '')
		line = line.replace('\t', '')
		line = line.replace(' ', '')
		
		# Ignore empty lines
		if line == "":
			continue
		
		# Split lines at '='
		words = line.split('=')
		if words[0] not in arch_params.keys():
			print "ERROR: Found invalid architecture parameter (" + words[0] + ") in " + filename
			sys.exit()
		 
		param = words[0]
		value = words[1]

		#architecture parameters 
		if param == 'W':
			arch_params['W'] = int(value)
		elif param == 'L':
			arch_params['L'] = int(value)
		elif param == 'Fs':
			arch_params['Fs'] = int(value)
		elif param == 'N':
			arch_params['N'] = int(value)
		elif param == 'K':
			arch_params['K'] = int(value)
		elif param == 'I':
			arch_params['I'] = int(value)
		elif param == 'Fcin':
			arch_params['Fcin'] = float(value)
		elif param == 'Fcout':
			arch_params['Fcout'] = float(value) 
		elif param == 'Or':
			arch_params['Or'] = int(value)
		elif param == 'Ofb':
			arch_params['Ofb'] = int(value)
		elif param == 'Fclocal':
			arch_params['Fclocal'] = float(value)
		elif param == 'Rsel':
			arch_params['Rsel'] = value
		elif param == 'Rfb':
			arch_params['Rfb'] = value
		
		#process technology parameters
		elif param == 'vdd':
			arch_params['vdd'] = float(value)
		elif param == 'vsram':
			arch_params['vsram'] = float(value)
		elif param == 'vsram_n':
			arch_params['vsram_n'] = float(value)
		elif param == 'gate_length':
			arch_params['gate_length'] = int(value)
		elif param == 'min_tran_width':
			arch_params['min_tran_width'] = int(value)
		elif param == 'min_width_tran_area':
			arch_params['min_width_tran_area'] = int(value)
		elif param == 'sram_cell_area':
			arch_params['sram_cell_area'] = float(value)
		elif param == 'gate_extension':
			arch_params['gate_extension'] = int(value)
		elif param == 'model_path':
			arch_params['model_path'] = os.path.abspath(value)
		elif param == 'model_library':
			arch_params['model_library'] = value
		elif param == 'metal':
			value_words = value.split(',')
			r = value_words[0].replace(' ', '')
			r = r.replace(' ', '')
			r = r.replace('\n', '')
			r = r.replace('\r', '')
			r = r.replace('\t', '')
			c = value_words[1].replace(' ', '')
			c = c.replace(' ', '')
			c = c.replace('\n', '')
			c = c.replace('\r', '')
			c = c.replace('\t', '')
			arch_params['metal'].append((float(r),float(c)))
	
		#finFET parameters
		elif use_finfet :
			if param == "fin_height" :
				arch_params['fin_height'] = int(value)
			elif param == "fin_width" :
				arch_params['fin_width'] = int(value)
			elif param == "lg" :
				arch_params['lg'] = int(value)
			elif param == 'rest_length_factor':
				arch_params['rest_length_factor'] = float(value)

	params_file.close()
	
	# Check that we read everything
	for param, value in arch_params.iteritems():
		if value == -1 or value == "":
			print "ERROR: Did not find architecture parameter " + param + " in " + filename
			sys.exit()
	
	check_arch_params(arch_params, filename, use_finfet)
	return arch_params 

def check_arch_params (arch_params, filename, use_finfet):
	if arch_params['W'] <= 0:
		print_error (arch_params['W'], "W", filename)
	if arch_params['L'] <= 0:
		print_error (arch_params['L'], "L", filename)
	if arch_params['Fs'] <= 0:
		print_error (arch_params['Fs'], "Fs", filename)
	if arch_params['N'] <= 0:
		print_error (arch_params['N'], "N", filename)
	if arch_params['K'] <= 4 and  arch_params['K'] != 5 and arch_params['K'] != 6:
		print_error (arch_params['K'], "K", filename)
	if arch_params['I'] <= 0:
		print_error (arch_params['I'], "I", filename)
	if arch_params['Fcin'] <= 0.0 or arch_params['Fcin'] > 1.0:
		print_error (arch_params['Fcin'], "Fcin", filename)
	if arch_params['Fcout'] <= 0.0 or arch_params['Fcout'] > 1.0 :
		print_error (arch_params['Fcout'], "Fcout", filename)
	if arch_params['Or'] <= 0:
		print_error (arch_params['Or'], "Or", filename)
	if arch_params['Ofb'] <= 0:
		print_error (arch_params['Ofb'], "Ofb", filename)
	if arch_params['Fclocal'] <= 0.0 or arch_params['Fclocal'] >= 1.0:
		print_error (arch_params['Fclocal'], "Fclocal", filename)
	if arch_params['Rsel'] != 'z' and (arch_params['Rsel'] < 'a' or arch_params['Rsel'] > chr(arch_params['K']+96)):
		print_error (arch_params['Rsel'], "Fclocal", filename)
	if len(arch_params['Rfb']) > arch_params['K'] and arch_params['Rfb'] != 'z':
		print "ERROR: Invalid value (" + str(arch_params['Rfb']) + ") for Rfb in " + filename + " (string too long)"
	else:
		# Now, let's make sure all these characters are valid characters
		for character in arch_params['Rfb']:
			# The character has to be a valid LUT input
			if (character < 'a' or character > chr(arch_params['K']+96)):
				print "ERROR: Invalid value (" + str(arch_params['Rfb']) + ") for Rfb in " + filename + " (" + character + " is not valid)"
				sys.exit()
			# The character should not appear twice
			elif arch_params['Rfb'].count(character) > 1:
				print "ERROR: Invalid value (" + str(arch_params['Rfb']) + ") for Rfb in " + filename + " (" + character + " appears more than once)"
				sys.exit()

	#process technology parameters
	if arch_params['vdd'] < 0 :
		print_warning (arch_params['vdd'], "vdd", filename)                     
	if arch_params['gate_length'] < 0 :
		print_error (arch_params['gate_length'], "gate_length", filename)            
	if arch_params['min_tran_width'] < 0 :
		print_error (arch_params['min_tran_width'], "min_tran_width", filename)            
	if arch_params['min_width_tran_area'] < 0 :
		print_error (arch_params['min_width_tran_area'], "min_width_tran_area", filename)            
	if arch_params['sram_cell_area'] < 0 :
		print_error (arch_params['sram_cell_area'], "sram_cell_area", filename)
	if arch_params['gate_extension'] < 0 :
		print_error (arch_params['gate_extension'], "gate_extension", filename)           

	if use_finfet :
		if arch_params['fin_width'] < 0 :
			print_error (arch_params['fin_width'], "fin_width", filename)            
		if arch_params['fin_height'] < 0 :
			print_error (arch_params['fin_height'], "fin_height", filename)            
		if arch_params['lg'] < 0 :
			print_error (arch_params['lg'], "lg", filename)            
		if arch_params['rest_length_factor'] < 0 :
			print_error (arch_params['rest_length_factor'], "rest_length_factor", filename) 


def print_error(value, arguement, filename):
	print "ERROR: Invalid value (" + value + ") for " + arguement + " in " + filename
	sys.exit()

def print_warning(value, arguement, filename):
	print "WARNING: Negative value (" + value + ") for " + arguement + " in " + filename

def print_architecture_params(report_file, arch_params_dict):
	report_file.write("----------Archetecture Parameters----------\n")
	report_file.write( "N = " + str( arch_params_dict['N']) + "\n" )
	report_file.write( "K = " + str( arch_params_dict['K']) + "\n" )
	report_file.write( "W = " + str( arch_params_dict['W']) + "\n" )
	report_file.write( "L = " + str( arch_params_dict['L']) + "\n" )
	report_file.write( "I = " + str( arch_params_dict['I']) + "\n" )
	report_file.write( "Fs = " + str( arch_params_dict['Fs']) + "\n" )
	report_file.write( "Fcin = " + str( arch_params_dict['Fcin']) + "\n" )
	report_file.write( "Fcout = " + str( arch_params_dict['Fcout']) + "\n" )
	report_file.write( "Or = " + str( arch_params_dict['Or']) + "\n" )
	report_file.write( "Ofb = " + str( arch_params_dict['Ofb']) + "\n" )
	report_file.write( "Rsel = " + str( arch_params_dict['Rsel']) + "\n" )
	report_file.write( "Rfb = " + str( arch_params_dict['Rfb']) + "\n" )
	report_file.write( "Fclocal = " + str( arch_params_dict['Fclocal']) + "\n" )

	report_file.write("----------Process Technology Parameters----------\n")
	report_file.write ( "vdd = " + str( arch_params_dict['vdd']) + "\n" )
	report_file.write ( "vsram = " + str( arch_params_dict['vsram']) + "\n" )
	report_file.write ( "vsram_n = " + str( arch_params_dict['vsram_n']) + "\n" )
	report_file.write ( "gate_length = " + str( arch_params_dict['gate_length']) + "\n" )
	report_file.write ( "min_tran_width = " + str( arch_params_dict['min_tran_width']) + "\n" )
	report_file.write ( "min_width_tran_area = " + str( arch_params_dict['min_width_tran_area']) + "\n" )
	report_file.write ( "sram_cell_area = " + str( arch_params_dict['sram_cell_area']) + "\n" )
	report_file.write ( "model_path = " + str( arch_params_dict['model_path']) + "\n" )
	report_file.write ( "model_library = " + str( arch_params_dict['model_library']) + "\n" )
	report_file.write ( "metal = " + str( arch_params_dict['metal']) + "\n" )