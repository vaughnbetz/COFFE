import os

def generate_switch_block_top(mux_name):
	""" Generate the top level switch block SPICE file """
	
	# Create directories
	if not os.path.exists(mux_name):
		os.makedirs(mux_name)  
	# Change to directory    
	os.chdir(mux_name)  
	
	switch_block_filename = mux_name + ".sp"
	sb_file = open(switch_block_filename, 'w')
	sb_file.write(".TITLE Switch block multiplexer\n\n") 
	
	sb_file.write("********************************************************************************\n")
	sb_file.write("** Include libraries, parameters and other\n")
	sb_file.write("********************************************************************************\n\n")
	sb_file.write(".LIB \"../includes.l\" INCLUDES\n\n")
	
	sb_file.write("********************************************************************************\n")
	sb_file.write("** Setup and input\n")
	sb_file.write("********************************************************************************\n\n")
	sb_file.write(".TRAN 1p 4n SWEEP DATA=sweep_data\n")
	sb_file.write(".OPTIONS BRIEF=1\n\n")
	sb_file.write("* Input signal\n")
	sb_file.write("VIN n_in gnd PULSE (0 supply_v 0 0 0 2n 4n)\n\n")
	
	sb_file.write("********************************************************************************\n")
	sb_file.write("** Measurement\n")
	sb_file.write("********************************************************************************\n\n")
	sb_file.write("* inv_sb_mux_1 delay\n")
	sb_file.write(".MEASURE TRAN meas_inv_sb_mux_1_tfall TRIG V(Xrouting_wire_load_1.Xrouting_wire_load_tile_1.Xsb_mux_on_out.n_in) VAL='supply_v/2' RISE=1\n")
	sb_file.write("+    TARG V(Xrouting_wire_load_1.Xrouting_wire_load_tile_1.Xsb_mux_on_out.Xsb_mux_driver.n_1_1) VAL='supply_v/2' FALL=1\n")
	sb_file.write(".MEASURE TRAN meas_inv_sb_mux_1_trise TRIG V(Xrouting_wire_load_1.Xrouting_wire_load_tile_1.Xsb_mux_on_out.n_in) VAL='supply_v/2' FALL=1\n")
	sb_file.write("+    TARG V(Xrouting_wire_load_1.Xrouting_wire_load_tile_1.Xsb_mux_on_out.Xsb_mux_driver.n_1_1) VAL='supply_v/2' RISE=1\n\n")
	sb_file.write("* inv_sb_mux_2 delays\n")
	sb_file.write(".MEASURE TRAN meas_inv_sb_mux_2_tfall TRIG V(Xrouting_wire_load_1.Xrouting_wire_load_tile_1.Xsb_mux_on_out.n_in) VAL='supply_v/2' FALL=1\n")
	sb_file.write("+    TARG V(Xrouting_wire_load_2.Xrouting_wire_load_tile_1.Xsb_mux_on_out.n_in) VAL='supply_v/2' FALL=1\n")
	sb_file.write(".MEASURE TRAN meas_inv_sb_mux_2_trise TRIG V(Xrouting_wire_load_1.Xrouting_wire_load_tile_1.Xsb_mux_on_out.n_in) VAL='supply_v/2' RISE=1\n")
	sb_file.write("+    TARG V(Xrouting_wire_load_2.Xrouting_wire_load_tile_1.Xsb_mux_on_out.n_in) VAL='supply_v/2' RISE=1\n\n")
	sb_file.write("* Total delays\n")
	sb_file.write(".MEASURE TRAN meas_total_tfall TRIG V(Xrouting_wire_load_1.Xrouting_wire_load_tile_1.Xsb_mux_on_out.n_in) VAL='supply_v/2' FALL=1\n")
	sb_file.write("+    TARG V(Xrouting_wire_load_2.Xrouting_wire_load_tile_1.Xsb_mux_on_out.n_in) VAL='supply_v/2' FALL=1\n")
	sb_file.write(".MEASURE TRAN meas_total_trise TRIG V(Xrouting_wire_load_1.Xrouting_wire_load_tile_1.Xsb_mux_on_out.n_in) VAL='supply_v/2' RISE=1\n")
	sb_file.write("+    TARG V(Xrouting_wire_load_2.Xrouting_wire_load_tile_1.Xsb_mux_on_out.n_in) VAL='supply_v/2' RISE=1\n\n")
	
	sb_file.write("********************************************************************************\n")
	sb_file.write("** Circuit\n")
	sb_file.write("********************************************************************************\n\n")
	sb_file.write("Xsb_mux_on_1 n_in n_1_1 vsram vsram_n vdd gnd sb_mux_on\n\n")
	sb_file.write("Xrouting_wire_load_1 n_1_1 n_2_1 n_hang_1 vsram vsram_n vdd gnd routing_wire_load\n\n")
	sb_file.write("Xrouting_wire_load_2 n_2_1 n_3_1 n_hang_2 vsram vsram_n vdd gnd routing_wire_load\n\n")
	sb_file.write(".END")
	sb_file.close()
	
	# Come out of swich block directory
	os.chdir("../")
	
	return (mux_name + "/" + mux_name + ".sp")
	
	
def generate_connection_block_top(mux_name):
	""" Generate the top level switch block SPICE file """
	
	# Create directories
	if not os.path.exists(mux_name):
		os.makedirs(mux_name)  
	# Change to directory    
	os.chdir(mux_name)
	
	connection_block_filename = mux_name + ".sp"
	cb_file = open(connection_block_filename, 'w')
	cb_file.write(".TITLE Connection block multiplexer\n\n") 
	
	cb_file.write("********************************************************************************\n")
	cb_file.write("** Include libraries, parameters and other\n")
	cb_file.write("********************************************************************************\n\n")
	cb_file.write(".LIB \"../includes.l\" INCLUDES\n\n")
	
	cb_file.write("********************************************************************************\n")
	cb_file.write("** Setup and input\n")
	cb_file.write("********************************************************************************\n\n")
	cb_file.write(".TRAN 1p 4n SWEEP DATA=sweep_data\n")
	cb_file.write(".OPTIONS BRIEF=1\n\n")
	cb_file.write("* Input signal\n")
	cb_file.write("VIN n_in gnd PULSE (0 supply_v 0 0 0 2n 4n)\n\n")
	
	cb_file.write("********************************************************************************\n")
	cb_file.write("** Measurement\n")
	cb_file.write("********************************************************************************\n\n")
	cb_file.write("* inv_cb_mux_1 delay\n")
	cb_file.write(".MEASURE TRAN meas_inv_cb_mux_1_tfall TRIG V(Xrouting_wire_load_1.Xrouting_wire_load_tile_1.Xcb_load_on_1.n_in) VAL='supply_v/2' RISE=1\n")
	cb_file.write("+    TARG V(Xrouting_wire_load_1.Xrouting_wire_load_tile_1.Xcb_load_on_1.Xcb_mux_driver.n_1_1) VAL='supply_v/2' FALL=1\n")
	cb_file.write(".MEASURE TRAN meas_inv_cb_mux_1_trise TRIG V(Xrouting_wire_load_1.Xrouting_wire_load_tile_1.Xcb_load_on_1.n_in) VAL='supply_v/2' FALL=1\n")
	cb_file.write("+    TARG V(Xrouting_wire_load_1.Xrouting_wire_load_tile_1.Xcb_load_on_1.Xcb_mux_driver.n_1_1) VAL='supply_v/2' RISE=1\n\n")
	cb_file.write("* inv_cb_mux_2 delays\n")
	cb_file.write(".MEASURE TRAN meas_inv_cb_mux_2_tfall TRIG V(Xrouting_wire_load_1.Xrouting_wire_load_tile_1.Xcb_load_on_1.n_in) VAL='supply_v/2' FALL=1\n")
	cb_file.write("+    TARG V(Xlocal_routing_wire_load_1.Xlocal_mux_on_1.n_in) VAL='supply_v/2' FALL=1\n")
	cb_file.write(".MEASURE TRAN meas_inv_cb_mux_2_trise TRIG V(Xrouting_wire_load_1.Xrouting_wire_load_tile_1.Xcb_load_on_1.n_in) VAL='supply_v/2' RISE=1\n")
	cb_file.write("+    TARG V(Xlocal_routing_wire_load_1.Xlocal_mux_on_1.n_in) VAL='supply_v/2' RISE=1\n\n")
	cb_file.write("* Total delays\n")
	cb_file.write(".MEASURE TRAN meas_total_tfall TRIG V(Xrouting_wire_load_1.Xrouting_wire_load_tile_1.Xcb_load_on_1.n_in) VAL='supply_v/2' FALL=1\n")
	cb_file.write("+    TARG V(Xlocal_routing_wire_load_1.Xlocal_mux_on_1.n_in) VAL='supply_v/2' FALL=1\n")
	cb_file.write(".MEASURE TRAN meas_total_trise TRIG V(Xrouting_wire_load_1.Xrouting_wire_load_tile_1.Xcb_load_on_1.n_in) VAL='supply_v/2' RISE=1\n")
	cb_file.write("+    TARG V(Xlocal_routing_wire_load_1.Xlocal_mux_on_1.n_in) VAL='supply_v/2' RISE=1\n\n")
	
	cb_file.write("********************************************************************************\n")
	cb_file.write("** Circuit\n")
	cb_file.write("********************************************************************************\n\n")
	cb_file.write("Xsb_mux_on_1 n_in n_1_1 vsram vsram_n vdd gnd sb_mux_on\n")
	cb_file.write("Xrouting_wire_load_1 n_1_1 n_1_2 n_1_3 vsram vsram_n vdd gnd routing_wire_load\n")
	cb_file.write("Xlocal_routing_wire_load_1 n_1_3 n_1_4 vsram vsram_n vdd gnd local_routing_wire_load\n")
	cb_file.write("Xlut_a_driver_1 n_1_4 n_hang1 vsram vsram_n n_hang2 n_hang3 vdd gnd lut_a_driver\n\n")
	cb_file.write(".END")
	cb_file.close()

	# Come out of connection block directory
	os.chdir("../")
	
	return (mux_name + "/" + mux_name + ".sp")


def generate_local_mux_top(mux_name):
	""" Generate the top level local mux SPICE file """
	
	# Create directories
	if not os.path.exists(mux_name):
		os.makedirs(mux_name)  
	# Change to directory    
	os.chdir(mux_name)
	
	connection_block_filename = mux_name + ".sp"
	local_mux_file = open(connection_block_filename, 'w')
	local_mux_file.write(".TITLE Local routing multiplexer\n\n") 
	
	local_mux_file.write("********************************************************************************\n")
	local_mux_file.write("** Include libraries, parameters and other\n")
	local_mux_file.write("********************************************************************************\n\n")
	local_mux_file.write(".LIB \"../includes.l\" INCLUDES\n\n")
	
	local_mux_file.write("********************************************************************************\n")
	local_mux_file.write("** Setup and input\n")
	local_mux_file.write("********************************************************************************\n\n")
	local_mux_file.write(".TRAN 1p 4n SWEEP DATA=sweep_data\n")
	local_mux_file.write(".OPTIONS BRIEF=1\n\n")
	local_mux_file.write("* Input signal\n")
	local_mux_file.write("VIN n_in gnd PULSE (0 supply_v 0 0 0 2n 4n)\n\n")
	
	local_mux_file.write("********************************************************************************\n")
	local_mux_file.write("** Measurement\n")
	local_mux_file.write("********************************************************************************\n\n")
	local_mux_file.write("* inv_local_mux_1 delay\n")
	local_mux_file.write(".MEASURE TRAN meas_inv_local_mux_1_tfall TRIG V(Xlocal_routing_wire_load_1.Xlocal_mux_on_1.n_in) VAL='supply_v/2' RISE=1\n")
	local_mux_file.write("+    TARG V(n_1_4) VAL='supply_v/2' FALL=1\n")
	local_mux_file.write(".MEASURE TRAN meas_inv_local_mux_1_trise TRIG V(Xlocal_routing_wire_load_1.Xlocal_mux_on_1.n_in) VAL='supply_v/2' FALL=1\n")
	local_mux_file.write("+    TARG V(n_1_4) VAL='supply_v/2' RISE=1\n\n")
	local_mux_file.write("* Total delays\n")
	local_mux_file.write(".MEASURE TRAN meas_total_tfall TRIG V(Xlocal_routing_wire_load_1.Xlocal_mux_on_1.n_in) VAL='supply_v/2' RISE=1\n")
	local_mux_file.write("+    TARG V(n_1_4) VAL='supply_v/2' FALL=1\n")
	local_mux_file.write(".MEASURE TRAN meas_total_trise TRIG V(Xlocal_routing_wire_load_1.Xlocal_mux_on_1.n_in) VAL='supply_v/2' FALL=1\n")
	local_mux_file.write("+    TARG V(n_1_4) VAL='supply_v/2' RISE=1\n\n")
	
	local_mux_file.write("********************************************************************************\n")
	local_mux_file.write("** Circuit\n")
	local_mux_file.write("********************************************************************************\n\n")
	local_mux_file.write("Xsb_mux_on_1 n_in n_1_1 vsram vsram_n vdd gnd sb_mux_on\n")
	local_mux_file.write("Xrouting_wire_load_1 n_1_1 n_1_2 n_1_3 vsram vsram_n vdd gnd routing_wire_load\n")
	local_mux_file.write("Xlocal_routing_wire_load_1 n_1_3 n_1_4 vsram vsram_n vdd gnd local_routing_wire_load\n")
	local_mux_file.write("Xlut_A_driver_1 n_1_4 n_hang1 vsram vsram_n n_hang2 n_hang3 vdd gnd lut_A_driver\n\n")
	local_mux_file.write(".END")
	local_mux_file.close()

	# Come out of connection block directory
	os.chdir("../")
	
	return (mux_name + "/" + mux_name + ".sp")
	
	
def generate_lut6_top(lut_name):
	""" Generate the top level 6-LUT SPICE file """

	# Create directory
	if not os.path.exists(lut_name):
		os.makedirs(lut_name)  
	# Change to directory    
	os.chdir(lut_name) 
	
	lut_filename = lut_name + ".sp"
	lut_file = open(lut_filename, 'w')
	lut_file.write(".TITLE 6-LUT\n\n") 
	
	lut_file.write("********************************************************************************\n")
	lut_file.write("** Include libraries, parameters and other\n")
	lut_file.write("********************************************************************************\n\n")
	lut_file.write(".LIB \"../includes.l\" INCLUDES\n\n")
	
	lut_file.write("********************************************************************************\n")
	lut_file.write("** Setup and input\n")
	lut_file.write("********************************************************************************\n\n")
	lut_file.write(".TRAN 1p 4n SWEEP DATA=sweep_data\n")
	lut_file.write(".OPTIONS BRIEF=1\n\n")
	lut_file.write("* Input signal\n")
	lut_file.write("VIN n_in gnd PULSE (0 supply_v 0 0 0 2n 4n)\n\n")
	
	lut_file.write("********************************************************************************\n")
	lut_file.write("** Measurement\n")
	lut_file.write("********************************************************************************\n\n")
	lut_file.write("* inv_lut_0sram_driver_1 delay\n")
	lut_file.write(".MEASURE TRAN meas_inv_lut_0sram_driver_1_tfall TRIG V(n_in) VAL='supply_v/2' RISE=1\n")
	lut_file.write("+    TARG V(Xlut.n_1_1) VAL='supply_v/2' FALL=1\n")
	lut_file.write(".MEASURE TRAN meas_inv_lut_0sram_driver_1_trise TRIG V(n_in) VAL='supply_v/2' FALL=1\n")
	lut_file.write("+    TARG V(Xlut.n_1_1) VAL='supply_v/2' RISE=1\n\n")
	lut_file.write("* inv_lut_sram_driver_2 delay\n")
	lut_file.write(".MEASURE TRAN meas_inv_lut_0sram_driver_2_tfall TRIG V(n_in) VAL='supply_v/2' FALL=1\n")
	lut_file.write("+    TARG V(Xlut.n_2_1) VAL='supply_v/2' FALL=1\n")
	lut_file.write(".MEASURE TRAN meas_inv_lut_0sram_driver_2_trise TRIG V(n_in) VAL='supply_v/2' RISE=1\n")
	lut_file.write("+    TARG V(Xlut.n_2_1) VAL='supply_v/2' RISE=1\n\n")
	lut_file.write("* Xinv_lut_int_buffer_1 delay\n")
	lut_file.write(".MEASURE TRAN meas_inv_lut_int_buffer_1_tfall TRIG V(n_in) VAL='supply_v/2' RISE=1\n")
	lut_file.write("+    TARG V(Xlut.n_6_1) VAL='supply_v/2' FALL=1\n")
	lut_file.write(".MEASURE TRAN meas_inv_lut_int_buffer_1_trise TRIG V(n_in) VAL='supply_v/2' FALL=1\n")
	lut_file.write("+    TARG V(Xlut.n_6_1) VAL='supply_v/2' RISE=1\n\n")
	lut_file.write("* Xinv_lut_int_buffer_2 delay\n")
	lut_file.write(".MEASURE TRAN meas_inv_lut_int_buffer_2_tfall TRIG V(n_in) VAL='supply_v/2' FALL=1\n")
	lut_file.write("+    TARG V(Xlut.n_7_1) VAL='supply_v/2' FALL=1\n")
	lut_file.write(".MEASURE TRAN meas_inv_lut_int_buffer_2_trise TRIG V(n_in) VAL='supply_v/2' RISE=1\n")
	lut_file.write("+    TARG V(Xlut.n_7_1) VAL='supply_v/2' RISE=1\n\n")
	lut_file.write("* Xinv_lut_out_buffer_1 delay\n")
	lut_file.write(".MEASURE TRAN meas_inv_lut_out_buffer_1_tfall TRIG V(n_in) VAL='supply_v/2' RISE=1\n")
	lut_file.write("+    TARG V(Xlut.n_11_1) VAL='supply_v/2' FALL=1\n")
	lut_file.write(".MEASURE TRAN meas_inv_lut_out_buffer_1_trise TRIG V(n_in) VAL='supply_v/2' FALL=1\n")
	lut_file.write("+    TARG V(Xlut.n_11_1) VAL='supply_v/2' RISE=1\n\n")
	lut_file.write("* Xinv_lut_out_buffer_2 delay\n")
	lut_file.write(".MEASURE TRAN meas_inv_lut_out_buffer_2_tfall TRIG V(n_in) VAL='supply_v/2' FALL=1\n")
	lut_file.write("+    TARG V(n_out) VAL='supply_v/2' FALL=1\n")
	lut_file.write(".MEASURE TRAN meas_inv_lut_out_buffer_2_trise TRIG V(n_in) VAL='supply_v/2' RISE=1\n")
	lut_file.write("+    TARG V(n_out) VAL='supply_v/2' RISE=1\n\n")
	lut_file.write("* Total delays\n")
	lut_file.write(".MEASURE TRAN meas_total_tfall TRIG V(n_in) VAL='supply_v/2' FALL=1\n")
	lut_file.write("+    TARG V(n_out) VAL='supply_v/2' FALL=1\n")
	lut_file.write(".MEASURE TRAN meas_total_trise TRIG V(n_in) VAL='supply_v/2' RISE=1\n")
	lut_file.write("+    TARG V(n_out) VAL='supply_v/2' RISE=1\n\n")
	lut_file.write(".MEASURE TRAN meas_logic_low_voltage FIND V(n_out) AT=3n\n\n")
	
	lut_file.write("********************************************************************************\n")
	lut_file.write("** Circuit\n")
	lut_file.write("********************************************************************************\n\n")
	lut_file.write("Xlut n_in n_out vdd vdd vdd vdd vdd vdd vdd gnd lut\n\n")
	lut_file.write("Xlut_output_load n_out n_local_out n_general_out vsram vsram_n vdd gnd lut_output_load\n\n")
	
	lut_file.write(".END")
	lut_file.close()

	# Come out of lut directory
	os.chdir("../")
	
	return (lut_name + "/" + lut_name + ".sp")
 

def generate_lut5_top(lut_name):
	""" Generate the top level 5-LUT SPICE file """

	# Create directory
	if not os.path.exists(lut_name):
		os.makedirs(lut_name)  
	# Change to directory    
	os.chdir(lut_name) 
	
	lut_filename = lut_name + ".sp"
	lut_file = open(lut_filename, 'w')
	lut_file.write(".TITLE 5-LUT\n\n") 
	
	lut_file.write("********************************************************************************\n")
	lut_file.write("** Include libraries, parameters and other\n")
	lut_file.write("********************************************************************************\n\n")
	lut_file.write(".LIB \"../includes.l\" INCLUDES\n\n")
	
	lut_file.write("********************************************************************************\n")
	lut_file.write("** Setup and input\n")
	lut_file.write("********************************************************************************\n\n")
	lut_file.write(".TRAN 1p 4n SWEEP DATA=sweep_data\n")
	lut_file.write(".OPTIONS BRIEF=1\n\n")
	lut_file.write("* Input signal\n")
	lut_file.write("VIN n_in gnd PULSE (0 supply_v 0 0 0 2n 4n)\n\n")
	
	lut_file.write("********************************************************************************\n")
	lut_file.write("** Measurement\n")
	lut_file.write("********************************************************************************\n\n")
	lut_file.write("* inv_lut_0sram_driver_1 delay\n")
	lut_file.write(".MEASURE TRAN meas_inv_lut_0sram_driver_1_tfall TRIG V(n_in) VAL='supply_v/2' RISE=1\n")
	lut_file.write("+    TARG V(Xlut.n_1_1) VAL='supply_v/2' FALL=1\n")
	lut_file.write(".MEASURE TRAN meas_inv_lut_0sram_driver_1_trise TRIG V(n_in) VAL='supply_v/2' FALL=1\n")
	lut_file.write("+    TARG V(Xlut.n_1_1) VAL='supply_v/2' RISE=1\n\n")
	lut_file.write("* inv_lut_sram_driver_2 delay\n")
	lut_file.write(".MEASURE TRAN meas_inv_lut_0sram_driver_2_tfall TRIG V(n_in) VAL='supply_v/2' FALL=1\n")
	lut_file.write("+    TARG V(Xlut.n_2_1) VAL='supply_v/2' FALL=1\n")
	lut_file.write(".MEASURE TRAN meas_inv_lut_0sram_driver_2_trise TRIG V(n_in) VAL='supply_v/2' RISE=1\n")
	lut_file.write("+    TARG V(Xlut.n_2_1) VAL='supply_v/2' RISE=1\n\n")
	lut_file.write("* Xinv_lut_int_buffer_1 delay\n")
	lut_file.write(".MEASURE TRAN meas_inv_lut_int_buffer_1_tfall TRIG V(n_in) VAL='supply_v/2' RISE=1\n")
	lut_file.write("+    TARG V(Xlut.n_6_1) VAL='supply_v/2' FALL=1\n")
	lut_file.write(".MEASURE TRAN meas_inv_lut_int_buffer_1_trise TRIG V(n_in) VAL='supply_v/2' FALL=1\n")
	lut_file.write("+    TARG V(Xlut.n_6_1) VAL='supply_v/2' RISE=1\n\n")
	lut_file.write("* Xinv_lut_int_buffer_2 delay\n")
	lut_file.write(".MEASURE TRAN meas_inv_lut_int_buffer_2_tfall TRIG V(n_in) VAL='supply_v/2' FALL=1\n")
	lut_file.write("+    TARG V(Xlut.n_7_1) VAL='supply_v/2' FALL=1\n")
	lut_file.write(".MEASURE TRAN meas_inv_lut_int_buffer_2_trise TRIG V(n_in) VAL='supply_v/2' RISE=1\n")
	lut_file.write("+    TARG V(Xlut.n_7_1) VAL='supply_v/2' RISE=1\n\n")
	lut_file.write("* Xinv_lut_out_buffer_1 delay\n")
	lut_file.write(".MEASURE TRAN meas_inv_lut_out_buffer_1_tfall TRIG V(n_in) VAL='supply_v/2' RISE=1\n")
	lut_file.write("+    TARG V(Xlut.n_11_1) VAL='supply_v/2' FALL=1\n")
	lut_file.write(".MEASURE TRAN meas_inv_lut_out_buffer_1_trise TRIG V(n_in) VAL='supply_v/2' FALL=1\n")
	lut_file.write("+    TARG V(Xlut.n_11_1) VAL='supply_v/2' RISE=1\n\n")
	lut_file.write("* Xinv_lut_out_buffer_2 delay\n")
	lut_file.write(".MEASURE TRAN meas_inv_lut_out_buffer_2_tfall TRIG V(n_in) VAL='supply_v/2' FALL=1\n")
	lut_file.write("+    TARG V(n_out) VAL='supply_v/2' FALL=1\n")
	lut_file.write(".MEASURE TRAN meas_inv_lut_out_buffer_2_trise TRIG V(n_in) VAL='supply_v/2' RISE=1\n")
	lut_file.write("+    TARG V(n_out) VAL='supply_v/2' RISE=1\n\n")
	lut_file.write("* Total delays\n")
	lut_file.write(".MEASURE TRAN meas_total_tfall TRIG V(n_in) VAL='supply_v/2' FALL=1\n")
	lut_file.write("+    TARG V(n_out) VAL='supply_v/2' FALL=1\n")
	lut_file.write(".MEASURE TRAN meas_total_trise TRIG V(n_in) VAL='supply_v/2' RISE=1\n")
	lut_file.write("+    TARG V(n_out) VAL='supply_v/2' RISE=1\n\n")
	lut_file.write(".MEASURE TRAN meas_logic_low_voltage FIND V(n_out) AT=3n\n\n")
	
	lut_file.write("********************************************************************************\n")
	lut_file.write("** Circuit\n")
	lut_file.write("********************************************************************************\n\n")
	lut_file.write("Xlut n_in n_out vdd vdd vdd vdd vdd vdd vdd gnd lut\n\n")
	lut_file.write("Xlut_output_load n_out n_local_out n_general_out vsram vsram_n vdd gnd lut_output_load\n\n")
	
	lut_file.write(".END")
	lut_file.close()

	# Come out of lut directory
	os.chdir("../")
	
	return (lut_name + "/" + lut_name + ".sp") 
 

def generate_lut4_top(lut_name):
	""" Generate the top level 4-LUT SPICE file """

	# Create directory
	if not os.path.exists(lut_name):
		os.makedirs(lut_name)  
	# Change to directory    
	os.chdir(lut_name) 
	
	lut_filename = lut_name + ".sp"
	lut_file = open(lut_filename, 'w')
	lut_file.write(".TITLE 4-LUT\n\n") 
	
	lut_file.write("********************************************************************************\n")
	lut_file.write("** Include libraries, parameters and other\n")
	lut_file.write("********************************************************************************\n\n")
	lut_file.write(".LIB \"../includes.l\" INCLUDES\n\n")
	
	lut_file.write("********************************************************************************\n")
	lut_file.write("** Setup and input\n")
	lut_file.write("********************************************************************************\n\n")
	lut_file.write(".TRAN 1p 4n SWEEP DATA=sweep_data\n")
	lut_file.write(".OPTIONS BRIEF=1\n\n")
	lut_file.write("* Input signal\n")
	lut_file.write("VIN n_in gnd PULSE (0 supply_v 0 0 0 2n 4n)\n\n")
	
	lut_file.write("********************************************************************************\n")
	lut_file.write("** Measurement\n")
	lut_file.write("********************************************************************************\n\n")
	lut_file.write("* inv_lut_0sram_driver_1 delay\n")
	lut_file.write(".MEASURE TRAN meas_inv_lut_0sram_driver_1_tfall TRIG V(n_in) VAL='supply_v/2' RISE=1\n")
	lut_file.write("+    TARG V(Xlut.n_1_1) VAL='supply_v/2' FALL=1\n")
	lut_file.write(".MEASURE TRAN meas_inv_lut_0sram_driver_1_trise TRIG V(n_in) VAL='supply_v/2' FALL=1\n")
	lut_file.write("+    TARG V(Xlut.n_1_1) VAL='supply_v/2' RISE=1\n\n")
	lut_file.write("* inv_lut_sram_driver_2 delay\n")
	lut_file.write(".MEASURE TRAN meas_inv_lut_0sram_driver_2_tfall TRIG V(n_in) VAL='supply_v/2' FALL=1\n")
	lut_file.write("+    TARG V(Xlut.n_2_1) VAL='supply_v/2' FALL=1\n")
	lut_file.write(".MEASURE TRAN meas_inv_lut_0sram_driver_2_trise TRIG V(n_in) VAL='supply_v/2' RISE=1\n")
	lut_file.write("+    TARG V(Xlut.n_2_1) VAL='supply_v/2' RISE=1\n\n")
	lut_file.write("* Xinv_lut_int_buffer_1 delay\n")
	lut_file.write(".MEASURE TRAN meas_inv_lut_int_buffer_1_tfall TRIG V(n_in) VAL='supply_v/2' RISE=1\n")
	lut_file.write("+    TARG V(Xlut.n_5_1) VAL='supply_v/2' FALL=1\n")
	lut_file.write(".MEASURE TRAN meas_inv_lut_int_buffer_1_trise TRIG V(n_in) VAL='supply_v/2' FALL=1\n")
	lut_file.write("+    TARG V(Xlut.n_5_1) VAL='supply_v/2' RISE=1\n\n")
	lut_file.write("* Xinv_lut_int_buffer_2 delay\n")
	lut_file.write(".MEASURE TRAN meas_inv_lut_int_buffer_2_tfall TRIG V(n_in) VAL='supply_v/2' FALL=1\n")
	lut_file.write("+    TARG V(Xlut.n_6_1) VAL='supply_v/2' FALL=1\n")
	lut_file.write(".MEASURE TRAN meas_inv_lut_int_buffer_2_trise TRIG V(n_in) VAL='supply_v/2' RISE=1\n")
	lut_file.write("+    TARG V(Xlut.n_6_1) VAL='supply_v/2' RISE=1\n\n")
	lut_file.write("* Xinv_lut_out_buffer_1 delay\n")
	lut_file.write(".MEASURE TRAN meas_inv_lut_out_buffer_1_tfall TRIG V(n_in) VAL='supply_v/2' RISE=1\n")
	lut_file.write("+    TARG V(Xlut.n_9_1) VAL='supply_v/2' FALL=1\n")
	lut_file.write(".MEASURE TRAN meas_inv_lut_out_buffer_1_trise TRIG V(n_in) VAL='supply_v/2' FALL=1\n")
	lut_file.write("+    TARG V(Xlut.n_9_1) VAL='supply_v/2' RISE=1\n\n")
	lut_file.write("* Xinv_lut_out_buffer_2 delay\n")
	lut_file.write(".MEASURE TRAN meas_inv_lut_out_buffer_2_tfall TRIG V(n_in) VAL='supply_v/2' FALL=1\n")
	lut_file.write("+    TARG V(n_out) VAL='supply_v/2' FALL=1\n")
	lut_file.write(".MEASURE TRAN meas_inv_lut_out_buffer_2_trise TRIG V(n_in) VAL='supply_v/2' RISE=1\n")
	lut_file.write("+    TARG V(n_out) VAL='supply_v/2' RISE=1\n\n")
	lut_file.write("* Total delays\n")
	lut_file.write(".MEASURE TRAN meas_total_tfall TRIG V(n_in) VAL='supply_v/2' FALL=1\n")
	lut_file.write("+    TARG V(n_out) VAL='supply_v/2' FALL=1\n")
	lut_file.write(".MEASURE TRAN meas_total_trise TRIG V(n_in) VAL='supply_v/2' RISE=1\n")
	lut_file.write("+    TARG V(n_out) VAL='supply_v/2' RISE=1\n\n")
	lut_file.write(".MEASURE TRAN meas_logic_low_voltage FIND V(n_out) AT=3n\n\n")
	
	lut_file.write("********************************************************************************\n")
	lut_file.write("** Circuit\n")
	lut_file.write("********************************************************************************\n\n")
	lut_file.write("Xlut n_in n_out vdd vdd vdd vdd vdd vdd vdd gnd lut\n\n")
	lut_file.write("Xlut_output_load n_out n_local_out n_general_out vsram vsram_n vdd gnd lut_output_load\n\n")
	
	lut_file.write(".END")
	lut_file.close()

	# Come out of lut directory
	os.chdir("../")
	
	return (lut_name + "/" + lut_name + ".sp")
	
 
def generate_lut_driver_top(input_driver_name, input_driver_type):
	""" Generate the top level lut input driver SPICE file """
	
	# Create directories
	if not os.path.exists(input_driver_name):
		os.makedirs(input_driver_name)  
	# Change to directory    
	os.chdir(input_driver_name) 
 
	lut_driver_filename = input_driver_name + ".sp"
	input_driver_file = open(lut_driver_filename, 'w')
	input_driver_file.write(".TITLE " + input_driver_name + " \n\n") 
 
	input_driver_file.write("********************************************************************************\n")
	input_driver_file.write("** Include libraries, parameters and other\n")
	input_driver_file.write("********************************************************************************\n\n")
	input_driver_file.write(".LIB \"../includes.l\" INCLUDES\n\n")
	
	input_driver_file.write("********************************************************************************\n")
	input_driver_file.write("** Setup and input\n")
	input_driver_file.write("********************************************************************************\n\n")
	input_driver_file.write(".TRAN 1p 4n SWEEP DATA=sweep_data\n")
	input_driver_file.write(".OPTIONS BRIEF=1\n\n")
	input_driver_file.write("* Input signal\n")
	input_driver_file.write("VIN n_in gnd PULSE (0 supply_v 0 0 0 2n 4n)\n\n")
	
	input_driver_file.write("********************************************************************************\n")
	input_driver_file.write("** Measurement\n")
	input_driver_file.write("********************************************************************************\n\n")
	# We measure different things based on the input driver type
	if input_driver_type != "default":
		input_driver_file.write("* inv_" + input_driver_name + "_0 delays\n")
		input_driver_file.write(".MEASURE TRAN meas_inv_" + input_driver_name + "_0_tfall TRIG V(n_1_2) VAL='supply_v/2' RISE=1\n")
		input_driver_file.write("+    TARG V(X" + input_driver_name + "_1.n_1_1) VAL='supply_v/2' FALL=1\n")
		input_driver_file.write(".MEASURE TRAN meas_inv_" + input_driver_name + "_0_trise TRIG V(n_1_2) VAL='supply_v/2' FALL=1\n")
		input_driver_file.write("+    TARG V(X" + input_driver_name + "_1.n_1_1) VAL='supply_v/2' RISE=1\n\n")
		input_driver_file.write("* inv_" + input_driver_name + "_1 delays\n")
		input_driver_file.write(".MEASURE TRAN meas_inv_" + input_driver_name + "_1_tfall TRIG V(n_1_2) VAL='supply_v/2' FALL=1\n")
		input_driver_file.write("+    TARG V(X" + input_driver_name + "_1.n_3_1) VAL='supply_v/2' FALL=1\n")
		input_driver_file.write(".MEASURE TRAN meas_inv_" + input_driver_name + "_1_trise TRIG V(n_1_2) VAL='supply_v/2' RISE=1\n")
		input_driver_file.write("+    TARG V(X" + input_driver_name + "_1.n_3_1) VAL='supply_v/2' RISE=1\n\n")
	input_driver_file.write("* inv_" + input_driver_name + "_2 delays\n")
	input_driver_file.write(".MEASURE TRAN meas_inv_" + input_driver_name + "_2_tfall TRIG V(n_1_2) VAL='supply_v/2' RISE=1\n")
	input_driver_file.write("+    TARG V(n_out) VAL='supply_v/2' FALL=1\n")
	input_driver_file.write(".MEASURE TRAN meas_inv_" + input_driver_name + "_2_trise TRIG V(n_1_2) VAL='supply_v/2' FALL=1\n")
	input_driver_file.write("+    TARG V(n_out) VAL='supply_v/2' RISE=1\n\n")
	input_driver_file.write("* Total delays\n")
	input_driver_file.write(".MEASURE TRAN meas_total_tfall TRIG V(n_1_2) VAL='supply_v/2' RISE=1\n")
	input_driver_file.write("+    TARG V(n_out) VAL='supply_v/2' FALL=1\n")
	input_driver_file.write(".MEASURE TRAN meas_total_trise TRIG V(n_1_2) VAL='supply_v/2' FALL=1\n")
	input_driver_file.write("+    TARG V(n_out) VAL='supply_v/2' RISE=1\n\n")
	
	input_driver_file.write("********************************************************************************\n")
	input_driver_file.write("** Circuit\n")
	input_driver_file.write("********************************************************************************\n\n")
	input_driver_file.write("Xcb_mux_on_1 n_in n_1_1 vsram vsram_n vdd gnd cb_mux_on\n")
	input_driver_file.write("Xlocal_routing_wire_load_1 n_1_1 n_1_2 vsram vsram_n vdd gnd local_routing_wire_load\n")
	input_driver_file.write("X" + input_driver_name + "_1 n_1_2 n_out vsram vsram_n n_rsel n_2_1 vdd gnd " + input_driver_name + "\n")
	if input_driver_type == "default_rsel" or input_driver_type == "reg_fb_rsel":
		# Connect a load to n_rsel node
		input_driver_file.write("Xff n_rsel n_ff_out vsram vsram_n gnd vdd gnd vdd gnd vdd vdd gnd ff\n")
	input_driver_file.write("X" + input_driver_name + "_not_1 n_2_1 n_out_n vdd gnd " + input_driver_name + "_not\n")
	input_driver_file.write("X" + input_driver_name + "_load_1 n_out vdd gnd " + input_driver_name + "_load\n")
	input_driver_file.write("X" + input_driver_name + "_load_2 n_out_n vdd gnd " + input_driver_name + "_load\n\n")
	input_driver_file.write(".END")
	input_driver_file.close()

	# Come out of lut_driver directory
	os.chdir("../")
	
	return (input_driver_name + "/" + input_driver_name + ".sp")
	

def generate_lut_driver_not_top(input_driver_name, input_driver_type):
	""" Generate the top level lut input not driver SPICE file """
	
	# Create directories
	input_driver_name_no_not = input_driver_name.replace("_not", "")
	if not os.path.exists(input_driver_name_no_not):
		os.makedirs(input_driver_name_no_not)  
	# Change to directory    
	os.chdir(input_driver_name_no_not)    
	
	lut_driver_filename = input_driver_name + ".sp"
	input_driver_file = open(lut_driver_filename, 'w')
	input_driver_file.write(".TITLE " + input_driver_name + " \n\n") 
	
	input_driver_file.write("********************************************************************************\n")
	input_driver_file.write("** Include libraries, parameters and other\n")
	input_driver_file.write("********************************************************************************\n\n")
	input_driver_file.write(".LIB \"../includes.l\" INCLUDES\n\n")
	
	input_driver_file.write("********************************************************************************\n")
	input_driver_file.write("** Setup and input\n")
	input_driver_file.write("********************************************************************************\n\n")
	input_driver_file.write(".TRAN 1p 4n SWEEP DATA=sweep_data\n")
	input_driver_file.write(".OPTIONS BRIEF=1\n\n")
	input_driver_file.write("* Input signal\n")
	input_driver_file.write("VIN n_in gnd PULSE (0 supply_v 0 0 0 2n 4n)\n\n")
	
	input_driver_file.write("********************************************************************************\n")
	input_driver_file.write("** Measurement\n")
	input_driver_file.write("********************************************************************************\n\n")
	input_driver_file.write("* inv_" + input_driver_name + "_1 delays\n")
	input_driver_file.write(".MEASURE TRAN meas_inv_" + input_driver_name + "_1_tfall TRIG V(n_1_2) VAL='supply_v/2' RISE=1\n")
	input_driver_file.write("+    TARG V(X" + input_driver_name + "_1.n_1_1) VAL='supply_v/2' FALL=1\n")
	input_driver_file.write(".MEASURE TRAN meas_inv_" + input_driver_name + "_1_trise TRIG V(n_1_2) VAL='supply_v/2' FALL=1\n")
	input_driver_file.write("+    TARG V(X" + input_driver_name + "_1.n_1_1) VAL='supply_v/2' RISE=1\n\n")
	input_driver_file.write("* inv_" + input_driver_name + "_2 delays\n")
	input_driver_file.write(".MEASURE TRAN meas_inv_" + input_driver_name + "_2_tfall TRIG V(n_1_2) VAL='supply_v/2' FALL=1\n")
	input_driver_file.write("+    TARG V(n_out_n) VAL='supply_v/2' FALL=1\n")
	input_driver_file.write(".MEASURE TRAN meas_inv_" + input_driver_name + "_2_trise TRIG V(n_1_2) VAL='supply_v/2' RISE=1\n")
	input_driver_file.write("+    TARG V(n_out_n) VAL='supply_v/2' RISE=1\n\n")
	input_driver_file.write("* Total delays\n")
	input_driver_file.write(".MEASURE TRAN meas_total_tfall TRIG V(n_1_2) VAL='supply_v/2' FALL=1\n")
	input_driver_file.write("+    TARG V(n_out_n) VAL='supply_v/2' FALL=1\n")
	input_driver_file.write(".MEASURE TRAN meas_total_trise TRIG V(n_1_2) VAL='supply_v/2' RISE=1\n")
	input_driver_file.write("+    TARG V(n_out_n) VAL='supply_v/2' RISE=1\n\n")
	
	input_driver_file.write("********************************************************************************\n")
	input_driver_file.write("** Circuit\n")
	input_driver_file.write("********************************************************************************\n\n")
	input_driver_file.write("Xcb_mux_on_1 n_in n_1_1 vsram vsram_n vdd gnd cb_mux_on\n")
	input_driver_file.write("Xlocal_routing_wire_load_1 n_1_1 n_1_2 vsram vsram_n vdd gnd local_routing_wire_load\n")
	input_driver_file.write("X" + input_driver_name_no_not + "_1 n_1_2 n_out vsram vsram_n n_rsel n_2_1 vdd gnd " + input_driver_name_no_not + "\n")
	if input_driver_type == "default_rsel" or input_driver_type == "reg_fb_rsel":
		# Connect a load to n_rsel node
		input_driver_file.write("Xff n_rsel n_ff_out vsram vsram_n gnd vdd gnd vdd gnd vdd vdd gnd ff\n")
	input_driver_file.write("X" + input_driver_name + "_1 n_2_1 n_out_n vdd gnd " + input_driver_name + "\n")
	input_driver_file.write("X" + input_driver_name_no_not + "_load_1 n_out n_vdd n_gnd " + input_driver_name_no_not + "_load\n")
	input_driver_file.write("X" + input_driver_name_no_not + "_load_2 n_out_n n_vdd n_gnd " + input_driver_name_no_not + "_load\n\n")
	input_driver_file.write(".END")
	input_driver_file.close()

	# Come out of lut_driver directory
	os.chdir("../")
	
	return (input_driver_name_no_not + "/" + input_driver_name + ".sp")    
   
  
def generate_lut_and_driver_top(input_driver_name, input_driver_type):
	""" Generate the top level lut with driver SPICE file. We use this to measure final delays of paths through the LUT. """
	
	# Create directories
	if not os.path.exists(input_driver_name):
		os.makedirs(input_driver_name)  
	# Change to directory    
	os.chdir(input_driver_name)  
	
	lut_driver_filename = input_driver_name + "_with_lut.sp"
	spice_file = open(lut_driver_filename, 'w')
	spice_file.write(".TITLE " + input_driver_name + " \n\n") 
	
	spice_file.write("********************************************************************************\n")
	spice_file.write("** Include libraries, parameters and other\n")
	spice_file.write("********************************************************************************\n\n")
	spice_file.write(".LIB \"../includes.l\" INCLUDES\n\n")
	
	spice_file.write("********************************************************************************\n")
	spice_file.write("** Setup and input\n")
	spice_file.write("********************************************************************************\n\n")
	spice_file.write(".TRAN 1p 16n SWEEP DATA=sweep_data\n")
	spice_file.write(".OPTIONS BRIEF=1\n\n")
	spice_file.write("* Input signal\n")
	spice_file.write("VIN_SRAM n_in_sram gnd PULSE (0 supply_v 4n 0 0 4n 8n)\n")
	spice_file.write("VIN_GATE n_in_gate gnd PULSE (supply_v 0 3n 0 0 2n 4n)\n\n")
	
	spice_file.write("********************************************************************************\n")
	spice_file.write("** Measurement\n")
	spice_file.write("********************************************************************************\n\n")
	spice_file.write("* Total delays\n")
	spice_file.write(".MEASURE TRAN meas_total_tfall TRIG V(n_3_1) VAL='supply_v/2' RISE=2\n")
	spice_file.write("+    TARG V(n_out) VAL='supply_v/2' FALL=1\n")
	spice_file.write(".MEASURE TRAN meas_total_trise TRIG V(n_3_1) VAL='supply_v/2' RISE=1\n")
	spice_file.write("+    TARG V(n_out) VAL='supply_v/2' RISE=1\n\n")
	
	spice_file.write("********************************************************************************\n")
	spice_file.write("** Circuit\n")
	spice_file.write("********************************************************************************\n\n")    
	spice_file.write("Xcb_mux_on_1 n_in_gate n_1_1 vsram vsram_n vdd gnd cb_mux_on\n")
	spice_file.write("Xlocal_routing_wire_load_1 n_1_1 n_1_2 vsram vsram_n vdd gnd local_routing_wire_load\n")
	spice_file.write("X" + input_driver_name + "_1 n_1_2 n_3_1 vsram vsram_n n_rsel n_2_1 vdd gnd " + input_driver_name + "\n")
	if input_driver_type == "default_rsel" or input_driver_type == "reg_fb_rsel":
		# Connect a load to n_rsel node
		spice_file.write("Xff n_rsel n_ff_out vsram vsram_n gnd vdd gnd vdd gnd vdd vdd gnd ff\n")
	spice_file.write("X" + input_driver_name + "_not_1 n_2_1 n_1_4 vdd gnd " + input_driver_name + "_not\n")
	
	# Connect the LUT driver to a different LUT input based on LUT driver name
	if input_driver_name == "lut_a_driver":
		spice_file.write("Xlut n_in_sram n_out n_3_1 vdd vdd vdd vdd vdd vdd gnd lut\n")
	elif input_driver_name == "lut_b_driver":
		spice_file.write("Xlut n_in_sram n_out vdd n_3_1 vdd vdd vdd vdd vdd gnd lut\n")
	elif input_driver_name == "lut_c_driver":
		spice_file.write("Xlut n_in_sram n_out vdd vdd n_3_1 vdd vdd vdd vdd gnd lut\n")
	elif input_driver_name == "lut_d_driver":
		spice_file.write("Xlut n_in_sram n_out vdd vdd vdd n_3_1 vdd vdd vdd gnd lut\n")
	elif input_driver_name == "lut_e_driver":
		spice_file.write("Xlut n_in_sram n_out vdd vdd vdd vdd n_3_1 vdd vdd gnd lut\n")
	elif input_driver_name == "lut_f_driver":
		spice_file.write("Xlut n_in_sram n_out vdd vdd vdd vdd vdd n_3_1 vdd gnd lut\n")
	
	spice_file.write("Xlut_output_load n_out n_local_out n_general_out vsram vsram_n vdd gnd lut_output_load\n\n")
	
	
	spice_file.write(".END")
	spice_file.close()

	# Come out of lut_driver directory
	os.chdir("../")  
  
	
def generate_local_ble_output_top(name):
	""" Generate the top level local ble output SPICE file """
	
	# Create directories
	if not os.path.exists(name):
		os.makedirs(name)  
	# Change to directory    
	os.chdir(name)   
	
	local_ble_output_filename = name + ".sp"
	top_file = open(local_ble_output_filename, 'w')
	top_file.write(".TITLE Local BLE output\n\n") 
	
	top_file.write("********************************************************************************\n")
	top_file.write("** Include libraries, parameters and other\n")
	top_file.write("********************************************************************************\n\n")
	top_file.write(".LIB \"../includes.l\" INCLUDES\n\n")
	
	top_file.write("********************************************************************************\n")
	top_file.write("** Setup and input\n")
	top_file.write("********************************************************************************\n\n")
	top_file.write(".TRAN 1p 4n SWEEP DATA=sweep_data\n")
	top_file.write(".OPTIONS BRIEF=1\n\n")
	top_file.write("* Input signal\n")
	top_file.write("VIN n_in gnd PULSE (0 supply_v 0 0 0 2n 4n)\n\n")
	
	top_file.write("********************************************************************************\n")
	top_file.write("** Measurement\n")
	top_file.write("********************************************************************************\n\n")
	top_file.write("* inv_local_ble_output_1 delay\n")
	top_file.write(".MEASURE TRAN meas_inv_local_ble_output_1_tfall TRIG V(n_1_1) VAL='supply_v/2' RISE=1\n")
	top_file.write("+    TARG V(Xlut_output_load.Xble_outputs.Xlocal_ble_output_1.n_2_1) VAL='supply_v/2' FALL=1\n")
	top_file.write(".MEASURE TRAN meas_inv_local_ble_output_1_trise TRIG V(n_1_1) VAL='supply_v/2' FALL=1\n")
	top_file.write("+    TARG V(Xlut_output_load.Xble_outputs.Xlocal_ble_output_1.n_2_1) VAL='supply_v/2' RISE=1\n\n")
	top_file.write("* inv_local_ble_output_2 delays\n")
	top_file.write(".MEASURE TRAN meas_inv_local_ble_output_2_tfall TRIG V(n_1_1) VAL='supply_v/2' FALL=1\n")
	top_file.write("+    TARG V(Xlocal_ble_output_load.n_1_2) VAL='supply_v/2' RISE=1\n")
	top_file.write(".MEASURE TRAN meas_inv_local_ble_output_2_trise TRIG V(n_1_1) VAL='supply_v/2' RISE=1\n")
	top_file.write("+    TARG V(Xlocal_ble_output_load.n_1_2) VAL='supply_v/2' FALL=1\n\n")
	top_file.write("* Total delays\n")
	top_file.write(".MEASURE TRAN meas_total_tfall TRIG V(n_1_1) VAL='supply_v/2' FALL=1\n")
	top_file.write("+    TARG V(Xlocal_ble_output_load.n_1_2) VAL='supply_v/2' RISE=1\n")
	top_file.write(".MEASURE TRAN meas_total_trise TRIG V(n_1_1) VAL='supply_v/2' RISE=1\n")
	top_file.write("+    TARG V(Xlocal_ble_output_load.n_1_2) VAL='supply_v/2' FALL=1\n\n")
	
	top_file.write("********************************************************************************\n")
	top_file.write("** Circuit\n")
	top_file.write("********************************************************************************\n\n")
	top_file.write("Xlut n_in n_1_1 vdd vdd vdd vdd vdd vdd vdd gnd lut\n\n")
	top_file.write("Xlut_output_load n_1_1 n_local_out n_general_out vsram vsram_n vdd gnd lut_output_load\n\n")
	top_file.write("Xlocal_ble_output_load n_local_out vsram vsram_n vdd gnd local_ble_output_load\n")
	top_file.write(".END")
	top_file.close()

	# Come out of connection block directory
	os.chdir("../")
	
	return (name + "/" + name + ".sp")
	
	
def generate_general_ble_output_top(name):
	""" """
	
	# Create directories
	if not os.path.exists(name):
		os.makedirs(name)  
	# Change to directory    
	os.chdir(name)  
	
	general_ble_output_filename = name + ".sp"
	top_file = open(general_ble_output_filename, 'w')
	top_file.write(".TITLE General BLE output\n\n") 
	
	top_file.write("********************************************************************************\n")
	top_file.write("** Include libraries, parameters and other\n")
	top_file.write("********************************************************************************\n\n")
	top_file.write(".LIB \"../includes.l\" INCLUDES\n\n")
	
	top_file.write("********************************************************************************\n")
	top_file.write("** Setup and input\n")
	top_file.write("********************************************************************************\n\n")
	top_file.write(".TRAN 1p 4n SWEEP DATA=sweep_data\n")
	top_file.write(".OPTIONS BRIEF=1\n\n")
	top_file.write("* Input signal\n")
	top_file.write("VIN n_in gnd PULSE (0 supply_v 0 0 0 2n 4n)\n\n")
	
	top_file.write("********************************************************************************\n")
	top_file.write("** Measurement\n")
	top_file.write("********************************************************************************\n\n")
	top_file.write("* inv_general_ble_output_1 delay\n")
	top_file.write(".MEASURE TRAN meas_inv_general_ble_output_1_tfall TRIG V(n_1_1) VAL='supply_v/2' RISE=1\n")
	top_file.write("+    TARG V(Xlut_output_load.Xble_outputs.Xgeneral_ble_output_1.n_2_1) VAL='supply_v/2' FALL=1\n")
	top_file.write(".MEASURE TRAN meas_inv_general_ble_output_1_trise TRIG V(n_1_1) VAL='supply_v/2' FALL=1\n")
	top_file.write("+    TARG V(Xlut_output_load.Xble_outputs.Xgeneral_ble_output_1.n_2_1) VAL='supply_v/2' RISE=1\n\n")
	top_file.write("* inv_general_ble_output_2 delays\n")
	top_file.write(".MEASURE TRAN meas_inv_general_ble_output_2_tfall TRIG V(n_1_1) VAL='supply_v/2' FALL=1\n")
	top_file.write("+    TARG V(Xgeneral_ble_output_load.n_1_9) VAL='supply_v/2' FALL=1\n")
	top_file.write(".MEASURE TRAN meas_inv_general_ble_output_2_trise TRIG V(n_1_1) VAL='supply_v/2' RISE=1\n")
	top_file.write("+    TARG V(Xgeneral_ble_output_load.n_1_9) VAL='supply_v/2' RISE=1\n\n")
	top_file.write("* Total delays\n")
	top_file.write(".MEASURE TRAN meas_total_tfall TRIG V(n_1_1) VAL='supply_v/2' FALL=1\n")
	top_file.write("+    TARG V(Xgeneral_ble_output_load.n_1_9) VAL='supply_v/2' FALL=1\n")
	top_file.write(".MEASURE TRAN meas_total_trise TRIG V(n_1_1) VAL='supply_v/2' RISE=1\n")
	top_file.write("+    TARG V(Xgeneral_ble_output_load.n_1_9) VAL='supply_v/2' RISE=1\n\n")
	
	top_file.write("********************************************************************************\n")
	top_file.write("** Circuit\n")
	top_file.write("********************************************************************************\n\n")
	top_file.write("Xlut n_in n_1_1 vdd vdd vdd vdd vdd vdd vdd gnd lut\n\n")
	top_file.write("Xlut_output_load n_1_1 n_local_out n_general_out vsram vsram_n vdd gnd lut_output_load\n\n")
	top_file.write("Xgeneral_ble_output_load n_general_out n_hang1 vsram vsram_n vdd gnd general_ble_output_load\n")
	top_file.write(".END")
	top_file.close()

	# Come out of connection block directory
	os.chdir("../")
	
	return (name + "/" + name + ".sp")
	
	
