def _generate_ptran_driver(spice_file, mux_name, implemented_mux_size):
	""" Generate mux driver for pass-transistor based MUX (it has a level restorer) """
	
	# Create the MUX output driver circuit
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* " + mux_name + " driver subcircuit (" + str(implemented_mux_size) + ":1)\n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT " + mux_name + "_driver n_in n_out n_vdd n_gnd\n")
	spice_file.write("Xrest_" + mux_name + " n_in n_1_1 n_vdd n_gnd rest Wp=rest_" + mux_name + "_pmos\n")
	spice_file.write("Xinv_" + mux_name + "_1 n_in n_1_1 n_vdd n_gnd inv Wn=inv_" + mux_name + "_1_nmos Wp=inv_" + mux_name + "_1_pmos\n")
	spice_file.write("Xwire_" + mux_name + "_driver n_1_1 n_1_2 wire Rw=wire_" + mux_name + "_driver_res Cw=wire_" + mux_name + "_driver_cap\n")
	spice_file.write("Xinv_" + mux_name + "_2 n_1_2 n_out n_vdd n_gnd inv Wn=inv_" + mux_name + "_2_nmos Wp=inv_" + mux_name + "_2_pmos\n")
	spice_file.write(".ENDS\n\n\n")
	
	
def _generate_ptran_sense_only(spice_file, mux_name, implemented_mux_size):
	""" Generate mux driver for pass-transistor based MUX (it has a level restorer) """
	
	# Create the MUX output sense inverter only circuit
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* " + mux_name + " sense inverter subcircuit (" + str(implemented_mux_size) + ":1)\n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT " + mux_name + "_sense n_in n_out n_vdd n_gnd\n")
	spice_file.write("Xrest_" + mux_name + " n_in n_out n_vdd n_gnd rest Wp=rest_" + mux_name + "_pmos\n")
	spice_file.write("Xinv_" + mux_name + "_1 n_in n_out n_vdd n_gnd inv Wn=inv_" + mux_name + "_1_nmos Wp=inv_" + mux_name + "_1_pmos\n")
	spice_file.write(".ENDS\n\n\n")  
            
            
def _generate_ptran_sense_only_local_mux(spice_file, mux_name, implemented_mux_size):
	""" Generate mux driver for pass-transistor based MUX (it has a level restorer) """
	
	# Create the MUX output sense inverter only circuit
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* " + mux_name + " sense inverter subcircuit (" + str(implemented_mux_size) + ":1)\n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT " + mux_name + "_sense n_in n_out n_vdd n_gnd\n")
	spice_file.write("Xrest_" + mux_name + " n_in n_out n_vdd n_gnd rest Wp=rest_" + mux_name + "_pmos\n")
	spice_file.write("Xinv_" + mux_name + "_1 n_in n_out n_vdd n_gnd inv Wn=inv_" + mux_name + "_1_nmos Wp=inv_" + mux_name + "_1_pmos\n")
	spice_file.write(".ENDS\n\n\n")
    
	if "local_mux" in mux_name :
            spice_file.write("******************************************************************************************\n")
            spice_file.write("* " + mux_name + " level shifter + sense inverter subcircuit (" + str(implemented_mux_size) + ":1)\n")
            spice_file.write("******************************************************************************************\n")
            spice_file.write(".SUBCKT " + mux_name + "_sense_lvl_shifter n_in n_out n_vdd_l n_vdd_h n_gnd\n")
            spice_file.write("Xrest_" + mux_name + " n_in n_out_inv n_vdd_l n_gnd rest Wp=rest_" + mux_name + "_pmos\n")
            spice_file.write("Xinv_" + mux_name + "_1 n_in n_out_inv n_vdd_l n_gnd inv Wn=inv_" + mux_name + "_1_nmos Wp=inv_" + mux_name + "_1_pmos\n")
            spice_file.write("Xinv_lvl_shifter_" + mux_name + "_1 n_in n_inv_lvl_shifter_1_out n_out n_vdd_h n_gnd lvl_shifter_single Wn=inv_lvl_shifter_" + mux_name + "_1_nmos Wp=inv_lvl_shifter_" + mux_name + "_1_pmos\n")
            spice_file.write("Xinv_lvl_shifter_" + mux_name + "_2 n_out_inv n_out n_inv_lvl_shifter_1_out  n_vdd_h n_gnd lvl_shifter_single Wn=inv_lvl_shifter_" + mux_name + "_2_nmos Wp=inv_lvl_shifter_" + mux_name + "_2_pmos\n")
            spice_file.write(".ENDS\n\n\n")            
    
def _generate_ptran_2lvl_mux_off(spice_file, mux_name, implemented_mux_size):
	""" Generate off pass-transistor 2-level mux """
	
	# Create the off MUX circuit
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* " + mux_name + " subcircuit (" + str(implemented_mux_size) + ":1), turned off \n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT " + mux_name + "_off n_in n_gate n_gate_n n_vdd n_gnd\n")
	spice_file.write("Xptran_" + mux_name + "_L1 n_in n_gnd n_gnd n_gnd ptran Wn=ptran_" + mux_name + "_L1_nmos\n")
	spice_file.write(".ENDS\n\n\n")
	
def generate_full_lut(spice_file):
	sram_cell_count = 1;
	lut_size = 6
	lvl_curr = lut_size
	# level 1
	for i in range(1, 2**(lvl_curr-1)):
		spice_file.write("Xlvl1_"+str(i)+"_mux n_0_"+ str(sram_cell_count) + " n_0_" + str(sram_cell_count+1) + "n_a" + "n_a_b" + "n_1_" + str(i) + " simple_mux Wn=ptran_lut_L1_nmos Rw='wire_lut_L1_res/2' Cw='wire_lut_L1_cap/2'\n")
		sram_cell_count = sram_cell_count + 2

	# level 2
	lvl_curr=lvl_curr -1
	sram_cell_count = 1
	for i in range(1, 2**(lvl_curr-1)):
		spice_file.write("Xlvl2_"+str(i)+"_mux n_1_"+ str(sram_cell_count) + " n_1_" + str(sram_cell_count+1) + "n_b" + "n_b_b" + "n_2_" + str(i) + " simple_mux Wn=ptran_lut_L2_nmos Rw='wire_lut_L2_res/2' Cw='wire_lut_L2_cap/2'\n")
		sram_cell_count = sram_cell_count + 2
		
	# level 3
	lvl_curr=lvl_curr -1	
	sram_cell_count = 1
	for i in range(1, 2**(lvl_curr-1)):
		spice_file.write("Xlvl3_"+str(i)+"_mux n_2_"+ str(sram_cell_count) + " n_2_" + str(sram_cell_count+1) + "n_c" + "n_c_b" + "n_3_" + str(i) + " simple_mux Wn=ptran_lut_L3_nmos Rw='wire_lut_L3_res/2' Cw='wire_lut_L3_cap/2'\n")
		sram_cell_count = sram_cell_count + 2	
	
	# internal_buff
	sram_cell_count = 1
	for i in range(1, 2**(lvl_curr-1)):
		spice_file.write("Xlut_buffer_"+str(i)+" n_3_"+ str(sram_cell_count) + " n_3_buff_" + str(sram_cell_count)+ " n_vdd n_gnd lut_buffer rest_lut_size=rest_lut_int_buffer_pmos inv_1_nmos=inv_lut_int_buffer_1_nmos inv_1_pmos=inv_lut_int_buffer_1_pmos Rw_int=wire_lut_int_buffer_res Cw_int=wire_lut_int_buffer_cap inv_2_nmos=inv_lut_int_buffer_2_nmos inv_2_pmos=inv_lut_int_buffer_2_pmos Rw_out=wire_lut_int_buffer_out_res Cw_out=wire_lut_int_buffer_out_cap \n")
		sram_cell_count = sram_cell_count + 2
		
	# level 4
	lvl_curr=lvl_curr -1
	sram_cell_count = 1
	for i in range(1, 2**(lvl_curr-1)):
		spice_file.write("Xlvl4_"+str(i)+"_mux n_3_buff_"+ str(sram_cell_count) + " n_3_buff_" + str(sram_cell_count+1) + "n_d" + "n_d_b" + "n_4_" + +str(i) + " simple_mux Wn=ptran_lut_L4_nmos Rw='wire_lut_L4_res/2' Cw='wire_lut_L4_cap/2'\n")
		sram_cell_count = sram_cell_count + 2		
		
	# level 5
	lvl_curr=lvl_curr -1
	sram_cell_count = 1
	for i in range(1, 2**(lvl_curr-1)):
		spice_file.write("Xlvl5_"+str(i)+"_mux n_4_"+ str(sram_cell_count) + " n_4_" + str(sram_cell_count+1) + "n_e" + "n_e_b" + "n_5_" + str(i) + " simple_mux Wn=ptran_lut_L5_nmos Rw='wire_lut_L5_res/2' Cw='wire_lut_L5_cap/2'\n")
		sram_cell_count = sram_cell_count + 2			
		
	# level 6
	lvl_curr=lvl_curr -1
	sram_cell_count = 1
	for i in range(1, 2**(lvl_curr-1)):
		spice_file.write("Xlvl6_"+str(i)+"_mux n_5_"+ str(sram_cell_count) + " n_5_" + str(sram_cell_count+1) + "n_f" + "n_f_b" + "n_6_" + str(i) + " simple_mux Wn=ptran_lut_L6_nmos Rw='wire_lut_L6_res/2' Cw='wire_lut_L6_cap/2'\n")
		sram_cell_count = sram_cell_count + 2			

	# output_buff
	sram_cell_count = 1
	for i in range(1, 2**(lvl_curr-1)):
		spice_file.write("Xlut_buffer_"+str(i)+"_out n_6_"+ str(sram_cell_count) + " n_out n_vdd n_gnd " +  "lut_buffer rest_lut_size=rest_lut_out_buffer_pmos inv_1_nmos=inv_lut_out_buffer_1_nmos inv_1_pmos=inv_lut_out_buffer_1_pmos Rw_int=wire_lut_out_buffer_res Cw_int=wire_lut_out_buffer_cap inv_2_nmos=inv_lut_out_buffer_2_nmos inv_2_pmos=inv_lut_out_buffer_2_pmos Rw_out=0 Cw_out=0 \n")
		sram_cell_count = sram_cell_count + 2		
		
def _generate_ptran_2lvl_mux_partial(spice_file, mux_name, implemented_mux_size, level1_size):
	""" Generate partially on pass-transistor 2-level mux """

	# Create the partially-on MUX circuit
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* " + mux_name + " subcircuit (" + str(implemented_mux_size) + ":1), partially turned on\n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT " + mux_name + "_partial n_in n_gate n_gate_n n_vdd n_gnd\n")
	# Write level 1 netlist
	spice_file.write("Xptran_" + mux_name + "_L1 n_in n_1 n_gate n_gnd ptran Wn=ptran_" + mux_name + "_L1_nmos\n")
	current_node = "n_1"
	for i in range(1, level1_size):
		new_node = "n_1_" + str(i)
		spice_file.write("Xwire_" + mux_name + "_L1_" + str(i) + " " + current_node + " " + new_node + 
							" wire Rw='wire_" + mux_name + "_L1_res/" + str(level1_size) + "' Cw='wire_" +
							mux_name + "_L1_cap/" + str(level1_size) + "'\n")
		spice_file.write("Xptran_" + mux_name + "_L1_" + str(i) + "h n_gnd " + new_node + " n_gnd n_gnd ptran Wn=ptran_" + mux_name + "_L1_nmos\n")
		current_node = new_node
	new_node = "n_1_" + str(level1_size)
	spice_file.write("Xwire_" + mux_name + "_L1_" + str(level1_size) + " " + current_node + " " + new_node + 
							" wire Rw='wire_" + mux_name + "_L1_res/" + str(level1_size) + "' Cw='wire_" +
							mux_name + "_L1_cap/" + str(level1_size) + "'\n")
	current_node = new_node
	# Write level 2 netlist
	spice_file.write("Xptran_" + mux_name + "_L2 " + current_node + " n_gnd n_gnd n_gnd ptran Wn=ptran_" + mux_name + "_L2_nmos\n")
	spice_file.write(".ENDS\n\n\n") 


def _generate_ptran_2lvl_mux_on(spice_file, mux_name, implemented_mux_size, level1_size, level2_size):
	""" Generate on pass-transistor 2-level mux, never call this outside this file """

	# Create the fully-on MUX circuit
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* " + mux_name + " subcircuit (" + str(implemented_mux_size) + ":1), fully turned on (mux only)\n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT " + mux_name + "_on_mux_only n_in n_out n_gate n_gate_n n_vdd n_gnd\n")
	# Write level 1 netlist
	spice_file.write("Xptran_" + mux_name + "_L1 n_in n_1 n_gate n_gnd ptran Wn=ptran_" + mux_name + "_L1_nmos\n")
	current_node = "n_1"
	for i in range(1, level1_size):
		new_node = "n_1_" + str(i)
		spice_file.write("Xwire_" + mux_name + "_L1_" + str(i) + " " + current_node + " " + new_node + 
							" wire Rw='wire_" + mux_name + "_L1_res/" + str(level1_size) + "' Cw='wire_" +
							mux_name + "_L1_cap/" + str(level1_size) + "'\n")
		spice_file.write("Xptran_" + mux_name + "_L1_" + str(i) + "h n_gnd " + new_node + " n_gnd n_gnd ptran Wn=ptran_" + mux_name + "_L1_nmos\n")
		current_node = new_node
	new_node = "n_1_" + str(level1_size)
	spice_file.write("Xwire_" + mux_name + "_L1_" + str(level1_size) + " " + current_node + " " + new_node + 
							" wire Rw='wire_" + mux_name + "_L1_res/" + str(level1_size) + "' Cw='wire_" +
							mux_name + "_L1_cap/" + str(level1_size) + "'\n")
	current_node = new_node
	# Write level 2 netlist
	spice_file.write("Xptran_" + mux_name + "_L2 " + current_node + " n_2 n_gate n_gnd ptran Wn=ptran_" + mux_name + "_L2_nmos\n")
	current_node = "n_2"
	wire_counter = 1
	tran_counter = 1
	# These are the switches below driver connection
	for i in range(1, (level2_size/2)):
		new_node = "n_2_" + str(i)
		spice_file.write("Xwire_" + mux_name + "_L2_" + str(wire_counter) + " " + current_node + " " + new_node + 
							" wire Rw='wire_" + mux_name + "_L2_res/" + str(level2_size-1) + "' Cw='wire_" +
							mux_name + "_L2_cap/" + str(level2_size-1) + "'\n")
		spice_file.write("Xptran_" + mux_name + "_L2_" + str(tran_counter) + "h n_gnd " + new_node + " n_gnd n_gnd ptran Wn=ptran_" + mux_name + "_L2_nmos\n")
		wire_counter = wire_counter + 1
		tran_counter = tran_counter + 1
		current_node = new_node
	# These are the middle wires
	# If level size is odd, we put a full size wire, if even, wire is only half size (wire is in middle of two switches) 
	if level2_size%2==0:
		spice_file.write("Xwire_" + mux_name + "_L2_" + str(wire_counter) + " " + current_node + " n_out" + 
							" wire Rw='wire_" + mux_name + "_L2_res/" + str(2*(level2_size-1)) + "' Cw='wire_" +
							mux_name + "_L2_cap/" + str(2*(level2_size-1)) + "'\n")
		wire_counter = wire_counter + 1
		new_node = "n_2_" + str(level2_size/2)
		spice_file.write("Xwire_" + mux_name + "_L2_" + str(wire_counter) + " " + " n_out " + new_node + 
							" wire Rw='wire_" + mux_name + "_L2_res/" + str(2*(level2_size-1)) + "' Cw='wire_" +
							mux_name + "_L2_cap/" + str(2*(level2_size-1)) + "'\n")
		spice_file.write("Xptran_" + mux_name + "_L2_" + str(tran_counter) + "h n_gnd " + new_node + " n_gnd n_gnd ptran Wn=ptran_" + mux_name + "_L2_nmos\n")
		wire_counter = wire_counter + 1
		tran_counter = tran_counter + 1
		current_node = new_node
	else:
		spice_file.write("Xwire_" + mux_name + "_L2_" + str(wire_counter) + " " + current_node + " n_out" + 
							" wire Rw='wire_" + mux_name + "_L2_res/" + str(level2_size-1) + "' Cw='wire_" +
							mux_name + "_L2_cap/" + str(level2_size-1) + "'\n")
		spice_file.write("Xptran_" + mux_name + "_L2_" + str(tran_counter) + "h n_gnd n_out n_gnd n_gnd ptran Wn=ptran_" + mux_name + "_L2_nmos\n")
		wire_counter = wire_counter + 1
		tran_counter = tran_counter + 1
		new_node = "n_2_" + str(level2_size/2)
		spice_file.write("Xwire_" + mux_name + "_L2_" + str(wire_counter) + " " + " n_out " + new_node + 
							" wire Rw='wire_" + mux_name + "_L2_res/" + str(level2_size-1) + "' Cw='wire_" +
							mux_name + "_L2_cap/" + str(level2_size-1) + "'\n")
		spice_file.write("Xptran_" + mux_name + "_L2_" + str(tran_counter) + "h n_gnd " + new_node + " n_gnd n_gnd ptran Wn=ptran_" + mux_name + "_L2_nmos\n")
		wire_counter = wire_counter + 1
		tran_counter = tran_counter + 1
		current_node = new_node
	# These are the switches above driver connection
	for i in range(1, (level2_size/2)):
		new_node = "n_2_" + str(i+level2_size/2)
		spice_file.write("Xwire_" + mux_name + "_L2_" + str(wire_counter) + " " + current_node + " " + new_node + 
							" wire Rw='wire_" + mux_name + "_L2_res/" + str(level2_size-1) + "' Cw='wire_" +
							mux_name + "_L2_cap/" + str(level2_size-1) + "'\n")
		spice_file.write("Xptran_" + mux_name + "_L2_" + str(tran_counter) + "h n_gnd " + new_node + " n_gnd n_gnd ptran Wn=ptran_" + mux_name + "_L2_nmos\n")
		wire_counter = wire_counter + 1
		tran_counter = tran_counter + 1
		current_node = new_node  
	spice_file.write(".ENDS\n\n\n")


def generate_ptran_2lvl_mux(spice_filename, mux_name, implemented_mux_size, level1_size, level2_size):
	""" 
	Creates two-level MUX circuits
	There are 3 different types of MUX that are generated depending on how 'on' the mux is
		1. Fully on (both levels are on) circuit name: mux_name + "_on"
		2. Partially on (only level 1 is on) circuit name: mux_name + "_partial"
		3. Off (both levels are off) circuit name: mux_name + "_off"
	"""
   
	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')
	
	# Generate SPICE subcircuits
	_generate_ptran_driver(spice_file, mux_name, implemented_mux_size)
	_generate_ptran_2lvl_mux_off(spice_file, mux_name, implemented_mux_size)
	_generate_ptran_2lvl_mux_partial(spice_file, mux_name, implemented_mux_size, level1_size)
	_generate_ptran_2lvl_mux_on(spice_file, mux_name, implemented_mux_size, level1_size, level2_size)
	
	# Create the fully-on MUX circuit
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* " + mux_name + " subcircuit (" + str(implemented_mux_size) + ":1), fully turned on \n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT " + mux_name + "_on n_in n_out n_gate n_gate_n n_vdd n_gnd\n")
	spice_file.write("X" + mux_name + "_on_mux_only n_in n_1_1 n_gate n_gate_n n_vdd n_gnd " + mux_name + "_on_mux_only\n")
	spice_file.write("X" + mux_name + "_driver n_1_1 n_out n_vdd n_gnd " + mux_name + "_driver\n")
	spice_file.write(".ENDS\n\n\n")
	
	# Close SPICE file
	spice_file.close()
	
	# Create a list of all transistors used in this subcircuit
	tran_names_list = []
	tran_names_list.append("ptran_" + mux_name + "_L1_nmos")
	tran_names_list.append("ptran_" + mux_name + "_L2_nmos")
	tran_names_list.append("rest_" + mux_name + "_pmos")
	tran_names_list.append("inv_" + mux_name + "_1_nmos")
	tran_names_list.append("inv_" + mux_name + "_1_pmos")
	tran_names_list.append("inv_" + mux_name + "_2_nmos")
	tran_names_list.append("inv_" + mux_name + "_2_pmos")
	
	# Create a list of all wires used in this subcircuit
	wire_names_list = []
	wire_names_list.append("wire_" + mux_name + "_driver")
	wire_names_list.append("wire_" + mux_name + "_L1")
	wire_names_list.append("wire_" + mux_name + "_L2")
	
	return tran_names_list, wire_names_list
	
	
def generate_ptran_2lvl_mux_no_driver(spice_filename, mux_name, implemented_mux_size, level1_size, level2_size):
	""" 
	Creates two-level MUX files
	There are 3 different types of MUX that are generated depending on how 'on' the mux is
		1. Fully on (both levels are on) circuit name: mux_name + "_on"
		2. Partially on (only level 1 is on) circuit name: mux_name + "_partial"
		3. Off (both levels are off) circuit name: mux_name + "_off"
		
	No driver is attached to the on mux (we need this for the local routing mux)
	"""
	
	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')
	
	# Generate SPICE subcircuits
	_generate_ptran_sense_only(spice_file, mux_name, implemented_mux_size)
	_generate_ptran_2lvl_mux_off(spice_file, mux_name, implemented_mux_size)
	_generate_ptran_2lvl_mux_partial(spice_file, mux_name, implemented_mux_size, level1_size)
	_generate_ptran_2lvl_mux_on(spice_file, mux_name, implemented_mux_size, level1_size, level2_size)
	
	# Create the fully-on MUX circuit
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* " + mux_name + " subcircuit (" + str(implemented_mux_size) + ":1), fully turned on \n")
	spice_file.write("******************************************************************************************\n")

	spice_file.write(".SUBCKT " + mux_name + "_on n_in n_out n_gate n_gate_n n_vdd n_gnd\n")
	spice_file.write("X" + mux_name + "_on_mux_only n_in n_1_1 n_gate n_gate_n n_vdd n_gnd " + mux_name + "_on_mux_only\n")
	spice_file.write("X" + mux_name + "_sense n_1_1 n_out n_vdd n_gnd " + mux_name + "_sense\n")
	spice_file.write(".ENDS\n\n\n")
		
	
	# Close SPICE file
	spice_file.close()
	
	# Create a list of all transistors used in this subcircuit
	tran_names_list = []
	tran_names_list.append("ptran_" + mux_name + "_L1_nmos")
	tran_names_list.append("ptran_" + mux_name + "_L2_nmos")
	tran_names_list.append("rest_" + mux_name + "_pmos")
	tran_names_list.append("inv_" + mux_name + "_1_nmos")
	tran_names_list.append("inv_" + mux_name + "_1_pmos")
    

    

	# Create a list of all wires used in this subcircuit
	wire_names_list = []
	wire_names_list.append("wire_" + mux_name + "_L1")
	wire_names_list.append("wire_" + mux_name + "_L2")
	
	return tran_names_list, wire_names_list
	
    
    
	
def generate_ptran_2lvl_mux_no_driver_gb_lut_level_shifter(spice_filename, mux_name, implemented_mux_size, level1_size, level2_size):
	""" 
	Creates two-level MUX files
	There are 3 different types of MUX that are generated depending on how 'on' the mux is
		1. Fully on (both levels are on) circuit name: mux_name + "_on"
		2. Partially on (only level 1 is on) circuit name: mux_name + "_partial"
		3. Off (both levels are off) circuit name: mux_name + "_off"
		
	No driver is attached to the on mux (we need this for the local routing mux)
	"""
	
	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')
	
	# Generate SPICE subcircuits
	_generate_ptran_sense_only_local_mux(spice_file, mux_name, implemented_mux_size)
	_generate_ptran_2lvl_mux_off(spice_file, mux_name, implemented_mux_size)
	_generate_ptran_2lvl_mux_partial(spice_file, mux_name, implemented_mux_size, level1_size)
	_generate_ptran_2lvl_mux_on(spice_file, mux_name, implemented_mux_size, level1_size, level2_size)
	
	# Create the fully-on MUX circuit
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* " + mux_name + " subcircuit (" + str(implemented_mux_size) + ":1), fully turned on \n")
	spice_file.write("******************************************************************************************\n")
	if "local_mux" not in mux_name :
        	spice_file.write(".SUBCKT " + mux_name + "_on n_in n_out n_gate n_gate_n n_vdd n_gnd\n")
        	spice_file.write("X" + mux_name + "_on_mux_only n_in n_1_1 n_gate n_gate_n n_vdd n_gnd " + mux_name + "_on_mux_only\n")
        	spice_file.write("X" + mux_name + "_sense n_1_1 n_out n_vdd n_gnd " + mux_name + "_sense\n")
        	spice_file.write(".ENDS\n\n\n")
	else :    
        	spice_file.write(".SUBCKT " + mux_name + "_on_lvl_shift n_in n_out n_gate n_gate_n n_vdd n_vdd_h n_gnd\n")
        	spice_file.write("X" + mux_name + "_on_mux_only n_in n_1_1 n_gate n_gate_n n_vdd n_gnd " + mux_name + "_on_mux_only\n")
        	spice_file.write("X" + mux_name + "_sense_and_lvl_shifter n_1_1 n_out n_vdd n_vdd_h gnd " + mux_name + "_sense_lvl_shifter\n")
        	spice_file.write(".ENDS\n\n\n")
		
	
	# Close SPICE file
	spice_file.close()
	
	# Create a list of all transistors used in this subcircuit
	tran_names_list = []
	tran_names_list.append("ptran_" + mux_name + "_L1_nmos")
	tran_names_list.append("ptran_" + mux_name + "_L2_nmos")
	tran_names_list.append("rest_" + mux_name + "_pmos")
	tran_names_list.append("inv_" + mux_name + "_1_nmos")
	tran_names_list.append("inv_" + mux_name + "_1_pmos")
    
    # transistors of the level shifter
    	if "local_mux" in mux_name :
        	tran_names_list.append("inv_lvl_shifter_" + mux_name + "_1_nmos")
        	tran_names_list.append("inv_lvl_shifter_" + mux_name + "_1_pmos")
        	tran_names_list.append("inv_lvl_shifter_" + mux_name + "_2_nmos")
        	tran_names_list.append("inv_lvl_shifter_" + mux_name + "_2_pmos")
    

	# Create a list of all wires used in this subcircuit
	wire_names_list = []
	wire_names_list.append("wire_" + mux_name + "_L1")
	wire_names_list.append("wire_" + mux_name + "_L2")
	
	return tran_names_list, wire_names_list    
 
def generate_ptran_2_to_1_mux(spice_filename, mux_name):
	""" Generate a 2:1 pass-transistor MUX with shared SRAM """

	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')
	
	# Create the 2:1 MUX circuit
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* " + mux_name + " subcircuit (2:1)\n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT " + mux_name + " n_in n_out n_gate n_gate_n n_vdd n_gnd\n")
	spice_file.write("Xptran_" + mux_name + " n_in n_1_1 n_gate n_gnd ptran Wn=ptran_" + mux_name + "_nmos\n")
	spice_file.write("Xwire_" + mux_name + " n_1_1 n_1_2 wire Rw='wire_" + mux_name + "_res/2' Cw='wire_" + mux_name + "_cap/2'\n")
	spice_file.write("Xwire_" + mux_name + "_h n_1_2 n_1_3 wire Rw='wire_" + mux_name + "_res/2' Cw='wire_" + mux_name + "_cap/2'\n")
	spice_file.write("Xptran_" + mux_name + "_h n_gnd n_1_3 n_gnd n_gnd ptran Wn=ptran_" + mux_name + "_nmos\n")
	spice_file.write("Xrest_" + mux_name + " n_1_2 n_2_1 n_vdd n_gnd rest Wp=rest_" + mux_name + "_pmos\n")
	spice_file.write("Xinv_" + mux_name + "_1 n_1_2 n_2_1 n_vdd n_gnd inv Wn=inv_" + mux_name + "_1_nmos Wp=inv_" + mux_name + "_1_pmos\n")
	spice_file.write("Xwire_" + mux_name + "_driver n_2_1 n_2_2 wire Rw=wire_" + mux_name + "_driver_res Cw=wire_" + mux_name + "_driver_cap\n")
	spice_file.write("Xinv_" + mux_name + "_2 n_2_2 n_out n_vdd n_gnd inv Wn=inv_" + mux_name + "_2_nmos Wp=inv_" + mux_name + "_2_pmos\n")
	spice_file.write(".ENDS\n\n\n")
	spice_file.close()
	
	# Create a list of all transistors used in this subcircuit
	tran_names_list = []
	tran_names_list.append("ptran_" + mux_name + "_nmos")
	tran_names_list.append("rest_" + mux_name + "_pmos")
	tran_names_list.append("inv_" + mux_name + "_1_nmos")
	tran_names_list.append("inv_" + mux_name + "_1_pmos")
	tran_names_list.append("inv_" + mux_name + "_2_nmos")
	tran_names_list.append("inv_" + mux_name + "_2_pmos")
	
	# Create a list of all wires used in this subcircuit
	wire_names_list = []
	wire_names_list.append("wire_" + mux_name)
	wire_names_list.append("wire_" + mux_name + "_driver")
	
	return tran_names_list, wire_names_list 


def _generate_tgate_driver(spice_file, mux_name, implemented_mux_size):
	""" Generate mux driver for pass-transistor based MUX (it has a level restorer) """
	
	# Create the MUX output driver circuit
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* " + mux_name + " driver subcircuit (" + str(implemented_mux_size) + ":1)\n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT " + mux_name + "_driver n_in n_out n_vdd n_gnd\n")
	# spice_file.write("Xrest_" + mux_name + " n_in n_1_1 n_vdd n_gnd rest Wp=rest_" + mux_name + "_pmos\n")
	spice_file.write("Xinv_" + mux_name + "_1 n_in n_1_1 n_vdd n_gnd inv Wn=inv_" + mux_name + "_1_nmos Wp=inv_" + mux_name + "_1_pmos\n")
	spice_file.write("Xwire_" + mux_name + "_driver n_1_1 n_1_2 wire Rw=wire_" + mux_name + "_driver_res Cw=wire_" + mux_name + "_driver_cap\n")
	spice_file.write("Xinv_" + mux_name + "_2 n_1_2 n_out n_vdd n_gnd inv Wn=inv_" + mux_name + "_2_nmos Wp=inv_" + mux_name + "_2_pmos\n")
	spice_file.write(".ENDS\n\n\n")

	
def _generate_tgate_sense_only(spice_file, mux_name, implemented_mux_size):
	""" Generate mux driver for pass-transistor based MUX (it has a level restorer) """
	
	# Create the MUX output sense inverter only circuit
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* " + mux_name + " sense inverter subcircuit (" + str(implemented_mux_size) + ":1)\n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT " + mux_name + "_sense n_in n_out n_vdd n_gnd\n")
	# spice_file.write("Xrest_" + mux_name + " n_in n_out n_vdd n_gnd rest Wp=rest_" + mux_name + "_pmos\n")
	spice_file.write("Xinv_" + mux_name + "_1 n_in n_out n_vdd n_gnd inv Wn=inv_" + mux_name + "_1_nmos Wp=inv_" + mux_name + "_1_pmos\n")
	spice_file.write(".ENDS\n\n\n")
	
def _generate_tgate_2lvl_mux_off(spice_file, mux_name, implemented_mux_size):
	""" Generate off pass-transistor 2-level mux """
	
	# Create the off MUX circuit
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* " + mux_name + " subcircuit (" + str(implemented_mux_size) + ":1), turned off \n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT " + mux_name + "_off n_in n_gate n_gate_n n_vdd n_gnd\n")
	spice_file.write("Xtgate_" + mux_name + "_L1 n_in n_gnd n_gnd n_vdd n_vdd n_gnd tgate Wn=tgate_" + mux_name + "_L1_nmos Wp=tgate_" + mux_name + "_L1_pmos\n")
	spice_file.write(".ENDS\n\n\n")
	
def _generate_tgate_2lvl_mux_partial(spice_file, mux_name, implemented_mux_size, level1_size):
	""" Generate partially on pass-transistor 2-level mux """

	# Create the partially-on MUX circuit
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* " + mux_name + " subcircuit (" + str(implemented_mux_size) + ":1), partially turned on\n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT " + mux_name + "_partial n_in n_gate n_gate_n n_vdd n_gnd\n")
	# Write level 1 netlist
	spice_file.write("Xtgate_" + mux_name + "_L1 n_in n_1 n_gate n_gate_n n_vdd n_gnd tgate Wn=tgate_" + mux_name + "_L1_nmos Wp=tgate_" + mux_name + "_L1_pmos\n")
	current_node = "n_1"
	for i in range(1, level1_size):
		new_node = "n_1_" + str(i)
		spice_file.write("Xwire_" + mux_name + "_L1_" + str(i) + " " + current_node + " " + new_node + 
							" wire Rw='wire_" + mux_name + "_L1_res/" + str(level1_size) + "' Cw='wire_" +
							mux_name + "_L1_cap/" + str(level1_size) + "'\n")
		spice_file.write("Xtgate_" + mux_name + "_L1_" + str(i) + "h n_gnd " + new_node + " n_gnd n_vdd n_vdd n_gnd tgate Wn=tgate_" + mux_name + "_L1_nmos Wp=tgate_" + mux_name + "_L1_pmos\n")
		current_node = new_node
	new_node = "n_1_" + str(level1_size)
	spice_file.write("Xwire_" + mux_name + "_L1_" + str(level1_size) + " " + current_node + " " + new_node + 
							" wire Rw='wire_" + mux_name + "_L1_res/" + str(level1_size) + "' Cw='wire_" +
							mux_name + "_L1_cap/" + str(level1_size) + "'\n")
	current_node = new_node
	# Write level 2 netlist
	spice_file.write("Xtgate_" + mux_name + "_L2 " + current_node + " n_gnd n_gnd n_vdd n_vdd n_gnd tgate Wn=tgate_" + mux_name + "_L2_nmos Wp=tgate_" + mux_name + "_L2_pmos\n")
	spice_file.write(".ENDS\n\n\n") 


def _generate_tgate_2lvl_mux_on(spice_file, mux_name, implemented_mux_size, level1_size, level2_size):
	""" Generate on pass-transistor 2-level mux, never call this outside this file """

	# Create the fully-on MUX circuit
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* " + mux_name + " subcircuit (" + str(implemented_mux_size) + ":1), fully turned on (mux only)\n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT " + mux_name + "_on_mux_only n_in n_out n_gate n_gate_n n_vdd n_gnd\n")
	# Write level 1 netlist
	spice_file.write("Xtgate_" + mux_name + "_L1 n_in n_1 n_gate n_gate_n n_vdd n_gnd tgate Wn=tgate_" + mux_name + "_L1_nmos Wp=tgate_" + mux_name + "_L1_pmos\n")
	current_node = "n_1"
	for i in range(1, level1_size):
		new_node = "n_1_" + str(i)
		spice_file.write("Xwire_" + mux_name + "_L1_" + str(i) + " " + current_node + " " + new_node + 
							" wire Rw='wire_" + mux_name + "_L1_res/" + str(level1_size) + "' Cw='wire_" +
							mux_name + "_L1_cap/" + str(level1_size) + "'\n")
		spice_file.write("Xtgate_" + mux_name + "_L1_" + str(i) + "h n_gnd " + new_node + " n_gnd n_vdd n_vdd n_gnd tgate Wn=tgate_" + mux_name + "_L1_nmos Wp=tgate_" + mux_name + "_L1_pmos\n")
		current_node = new_node
	new_node = "n_1_" + str(level1_size)
	spice_file.write("Xwire_" + mux_name + "_L1_" + str(level1_size) + " " + current_node + " " + new_node + 
							" wire Rw='wire_" + mux_name + "_L1_res/" + str(level1_size) + "' Cw='wire_" +
							mux_name + "_L1_cap/" + str(level1_size) + "'\n")
	current_node = new_node
	# Write level 2 netlist
	spice_file.write("Xtgate_" + mux_name + "_L2 " + current_node + " n_2 n_gate n_gate_n n_vdd n_gnd tgate Wn=tgate_" + mux_name + "_L2_nmos Wp=tgate_" + mux_name + "_L2_pmos\n")
	current_node = "n_2"
	wire_counter = 1
	tran_counter = 1
	# These are the switches below driver connection
	for i in range(1, (level2_size/2)):
		new_node = "n_2_" + str(i)
		spice_file.write("Xwire_" + mux_name + "_L2_" + str(wire_counter) + " " + current_node + " " + new_node + 
							" wire Rw='wire_" + mux_name + "_L2_res/" + str(level2_size-1) + "' Cw='wire_" +
							mux_name + "_L2_cap/" + str(level2_size-1) + "'\n")
		spice_file.write("Xtagte_" + mux_name + "_L2_" + str(tran_counter) + "h n_gnd " + new_node + " n_gnd n_vdd n_vdd n_gnd tgate Wn=tgate_" + mux_name + "_L2_nmos Wp=tgate_" + mux_name + "_L2_pmos\n")
		wire_counter = wire_counter + 1
		tran_counter = tran_counter + 1
		current_node = new_node
	# These are the middle wires
	# If level size is odd, we put a full size wire, if even, wire is only half size (wire is in middle of two switches) 
	if level2_size%2==0:
		spice_file.write("Xwire_" + mux_name + "_L2_" + str(wire_counter) + " " + current_node + " n_out" + 
							" wire Rw='wire_" + mux_name + "_L2_res/" + str(2*(level2_size-1)) + "' Cw='wire_" +
							mux_name + "_L2_cap/" + str(2*(level2_size-1)) + "'\n")
		wire_counter = wire_counter + 1
		new_node = "n_2_" + str(level2_size/2)
		spice_file.write("Xwire_" + mux_name + "_L2_" + str(wire_counter) + " " + " n_out " + new_node + 
							" wire Rw='wire_" + mux_name + "_L2_res/" + str(2*(level2_size-1)) + "' Cw='wire_" +
							mux_name + "_L2_cap/" + str(2*(level2_size-1)) + "'\n")
		spice_file.write("Xtgate_" + mux_name + "_L2_" + str(tran_counter) + "h n_gnd " + new_node + " n_gnd n_vdd n_vdd n_gnd tgate Wn=tgate_" + mux_name + "_L2_nmos Wp=tgate_" + mux_name + "_L2_pmos\n")
		wire_counter = wire_counter + 1
		tran_counter = tran_counter + 1
		current_node = new_node
	else:
		spice_file.write("Xwire_" + mux_name + "_L2_" + str(wire_counter) + " " + current_node + " n_out" + 
							" wire Rw='wire_" + mux_name + "_L2_res/" + str(level2_size-1) + "' Cw='wire_" +
							mux_name + "_L2_cap/" + str(level2_size-1) + "'\n")
		spice_file.write("Xtgate_" + mux_name + "_L2_" + str(tran_counter) + "h n_gnd n_out n_gnd n_vdd n_vdd n_gnd tgate Wn=tgate_" + mux_name + "_L2_nmos Wp=tgate_" + mux_name + "_L2_pmos\n")
		wire_counter = wire_counter + 1
		tran_counter = tran_counter + 1
		new_node = "n_2_" + str(level2_size/2)
		spice_file.write("Xwire_" + mux_name + "_L2_" + str(wire_counter) + " " + " n_out " + new_node + 
							" wire Rw='wire_" + mux_name + "_L2_res/" + str(level2_size-1) + "' Cw='wire_" +
							mux_name + "_L2_cap/" + str(level2_size-1) + "'\n")
		spice_file.write("Xtgate_" + mux_name + "_L2_" + str(tran_counter) + "h n_gnd " + new_node + " n_gnd n_vdd n_vdd n_gnd tgate Wn=tgate_" + mux_name + "_L2_nmos Wp=tgate_" + mux_name + "_L2_pmos\n")
		wire_counter = wire_counter + 1
		tran_counter = tran_counter + 1
		current_node = new_node
	# These are the switches above driver connection
	for i in range(1, (level2_size/2)):
		new_node = "n_2_" + str(i+level2_size/2)
		spice_file.write("Xwire_" + mux_name + "_L2_" + str(wire_counter) + " " + current_node + " " + new_node + 
							" wire Rw='wire_" + mux_name + "_L2_res/" + str(level2_size-1) + "' Cw='wire_" +
							mux_name + "_L2_cap/" + str(level2_size-1) + "'\n")
		spice_file.write("Xtgate_" + mux_name + "_L2_" + str(tran_counter) + "h n_gnd " + new_node + " n_gnd n_vdd n_vdd n_gnd tgate Wn=tgate_" + mux_name + "_L2_nmos Wp=tgate_" + mux_name + "_L2_pmos\n")
		wire_counter = wire_counter + 1
		tran_counter = tran_counter + 1
		current_node = new_node  
	spice_file.write(".ENDS\n\n\n")

	
def generate_tgate_2lvl_mux(spice_filename, mux_name, implemented_mux_size, level1_size, level2_size):
	""" 
	Creates two-level MUX circuits
	There are 3 different types of MUX that are generated depending on how 'on' the mux is
		1. Fully on (both levels are on) circuit name: mux_name + "_on"
		2. Partially on (only level 1 is on) circuit name: mux_name + "_partial"
		3. Off (both levels are off) circuit name: mux_name + "_off"
	"""
   
	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')
	
	# Generate SPICE subcircuits
	_generate_tgate_driver(spice_file, mux_name, implemented_mux_size)
	_generate_tgate_2lvl_mux_off(spice_file, mux_name, implemented_mux_size)
	_generate_tgate_2lvl_mux_partial(spice_file, mux_name, implemented_mux_size, level1_size)
	_generate_tgate_2lvl_mux_on(spice_file, mux_name, implemented_mux_size, level1_size, level2_size)
	
	# Create the fully-on MUX circuit
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* " + mux_name + " subcircuit (" + str(implemented_mux_size) + ":1), fully turned on \n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT " + mux_name + "_on n_in n_out n_gate n_gate_n n_vdd n_gnd\n")
	spice_file.write("X" + mux_name + "_on_mux_only n_in n_1_1 n_gate n_gate_n n_vdd n_gnd " + mux_name + "_on_mux_only\n")
	spice_file.write("X" + mux_name + "_driver n_1_1 n_out n_vdd n_gnd " + mux_name + "_driver\n")
	spice_file.write(".ENDS\n\n\n")
	
	# Close SPICE file
	spice_file.close()
	
	# Create a list of all transistors used in this subcircuit
	tran_names_list = []
	tran_names_list.append("tgate_" + mux_name + "_L1_nmos")
	tran_names_list.append("tgate_" + mux_name + "_L1_pmos")
	tran_names_list.append("tgate_" + mux_name + "_L2_nmos")
	tran_names_list.append("tgate_" + mux_name + "_L2_pmos")
	# tran_names_list.append("rest_" + mux_name + "_pmos")
	tran_names_list.append("inv_" + mux_name + "_1_nmos")
	tran_names_list.append("inv_" + mux_name + "_1_pmos")
	tran_names_list.append("inv_" + mux_name + "_2_nmos")
	tran_names_list.append("inv_" + mux_name + "_2_pmos")
	
	# Create a list of all wires used in this subcircuit
	wire_names_list = []
	wire_names_list.append("wire_" + mux_name + "_driver")
	wire_names_list.append("wire_" + mux_name + "_L1")
	wire_names_list.append("wire_" + mux_name + "_L2")
	
	return tran_names_list, wire_names_list
	
	
def generate_tgate_2lvl_mux_no_driver(spice_filename, mux_name, implemented_mux_size, level1_size, level2_size):
	""" 
	Creates two-level MUX files
	There are 3 different types of MUX that are generated depending on how 'on' the mux is
		1. Fully on (both levels are on) circuit name: mux_name + "_on"
		2. Partially on (only level 1 is on) circuit name: mux_name + "_partial"
		3. Off (both levels are off) circuit name: mux_name + "_off"
		
	No driver is attached to the on mux (we need this for the local routing mux)
	"""
	
	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')
	
	# Generate SPICE subcircuits
	_generate_tgate_sense_only(spice_file, mux_name, implemented_mux_size)
	_generate_tgate_2lvl_mux_off(spice_file, mux_name, implemented_mux_size)
	_generate_tgate_2lvl_mux_partial(spice_file, mux_name, implemented_mux_size, level1_size)
	_generate_tgate_2lvl_mux_on(spice_file, mux_name, implemented_mux_size, level1_size, level2_size)
	
	# Create the fully-on MUX circuit
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* " + mux_name + " subcircuit (" + str(implemented_mux_size) + ":1), fully turned on \n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT " + mux_name + "_on n_in n_out n_gate n_gate_n n_vdd n_gnd\n")
	spice_file.write("X" + mux_name + "_on_mux_only n_in n_1_1 n_gate n_gate_n n_vdd n_gnd " + mux_name + "_on_mux_only\n")
	spice_file.write("X" + mux_name + "_sense n_1_1 n_out n_vdd n_gnd " + mux_name + "_sense\n")
	spice_file.write(".ENDS\n\n\n")
	
	# Close SPICE file
	spice_file.close()
	
	# Create a list of all transistors used in this subcircuit
	tran_names_list = []
	tran_names_list.append("tgate_" + mux_name + "_L1_nmos")
	tran_names_list.append("tgate_" + mux_name + "_L1_pmos")
	tran_names_list.append("tgate_" + mux_name + "_L2_nmos")
	tran_names_list.append("tgate_" + mux_name + "_L2_pmos")
	# tran_names_list.append("rest_" + mux_name + "_pmos")
	tran_names_list.append("inv_" + mux_name + "_1_nmos")
	tran_names_list.append("inv_" + mux_name + "_1_pmos")
	
	# Create a list of all wires used in this subcircuit
	wire_names_list = []
	wire_names_list.append("wire_" + mux_name + "_L1")
	wire_names_list.append("wire_" + mux_name + "_L2")
	
	return tran_names_list, wire_names_list
	
 
def generate_tgate_2_to_1_mux(spice_filename, mux_name):
	""" Generate a 2:1 pass-transistor MUX with shared SRAM """

	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')
	
	# Create the 2:1 MUX circuit
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* " + mux_name + " subcircuit (2:1)\n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT " + mux_name + " n_in n_out n_gate n_gate_n n_vdd n_gnd\n")
	spice_file.write("Xtgate_" + mux_name + " n_in n_1_1 n_gate n_gate_n n_vdd n_gnd tgate Wn=tgate_" + mux_name + "_nmos Wp=tgate_" + mux_name + "_pmos\n")
	spice_file.write("Xwire_" + mux_name + " n_1_1 n_1_2 wire Rw='wire_" + mux_name + "_res/2' Cw='wire_" + mux_name + "_cap/2'\n")
	spice_file.write("Xwire_" + mux_name + "_h n_1_2 n_1_3 wire Rw='wire_" + mux_name + "_res/2' Cw='wire_" + mux_name + "_cap/2'\n")
	spice_file.write("Xtgate_" + mux_name + "_h n_gnd n_1_3 n_gnd n_vdd n_vdd n_gnd tgate Wn=tgate_" + mux_name + "_nmos Wp=tgate_" + mux_name + "_pmos\n")
	# spice_file.write("Xrest_" + mux_name + " n_1_2 n_2_1 n_vdd n_gnd rest Wp=rest_" + mux_name + "_pmos\n")
	spice_file.write("Xinv_" + mux_name + "_1 n_1_2 n_2_1 n_vdd n_gnd inv Wn=inv_" + mux_name + "_1_nmos Wp=inv_" + mux_name + "_1_pmos\n")
	spice_file.write("Xwire_" + mux_name + "_driver n_2_1 n_2_2 wire Rw=wire_" + mux_name + "_driver_res Cw=wire_" + mux_name + "_driver_cap\n")
	spice_file.write("Xinv_" + mux_name + "_2 n_2_2 n_out n_vdd n_gnd inv Wn=inv_" + mux_name + "_2_nmos Wp=inv_" + mux_name + "_2_pmos\n")
	spice_file.write(".ENDS\n\n\n")
	spice_file.close()
	
	# Create a list of all transistors used in this subcircuit
	tran_names_list = []
	tran_names_list.append("tgate_" + mux_name + "_nmos")
	tran_names_list.append("tgate_" + mux_name + "_pmos")
	# tran_names_list.append("rest_" + mux_name + "_pmos")
	tran_names_list.append("inv_" + mux_name + "_1_nmos")
	tran_names_list.append("inv_" + mux_name + "_1_pmos")
	tran_names_list.append("inv_" + mux_name + "_2_nmos")
	tran_names_list.append("inv_" + mux_name + "_2_pmos")
	
	# Create a list of all wires used in this subcircuit
	wire_names_list = []
	wire_names_list.append("wire_" + mux_name)
	wire_names_list.append("wire_" + mux_name + "_driver")
	
	return tran_names_list, wire_names_list  


def generate_dedicated_driver(spice_filename, driver_name, num_bufs, top_name):
	""" Generate a driver for the dedicated routing links """
	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')
	# Create the driver
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* " + driver_name + " subcircuit (2:1)\n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT " + driver_name + " n_in n_out n_vdd n_gnd\n")
	count = 1
	spice_file.write("Xinv_" + driver_name + "_"+str(count)+" n_in n_1_"+str(count)+" n_vdd n_gnd inv Wn=inv_" + driver_name + "_"+str(1)+"_nmos Wp=inv_" + driver_name + "_"+str(1)+"_pmos\n")
	spice_file.write("Xwirer_edi_"+str(count)+" n_1_"+str(count)+" n_1_"+str(count+1)+" wire Rw=wire_"+top_name+"_2_res/"+str(num_bufs*2)+" Cw=wire_"+top_name+"_2_cap/"+str(num_bufs*2)+" \n")
	count += 1
	for i in range(2, num_bufs * 2):
		spice_file.write("Xinv_" + driver_name + "_"+str(i)+" n_1_"+str(count)+" n_1_"+str(count + 1)+" n_vdd n_gnd inv Wn=inv_" + driver_name + "_"+str(i)+"_nmos Wp=inv_" + driver_name + "_"+str(i)+"_pmos\n")
		spice_file.write("Xwirer_edi_"+str(i)+" n_1_"+str(count + 1)+" n_1_"+str(count + 2)+" wire Rw=wire_"+top_name+"_2_res/"+str(num_bufs*2)+" Cw=wire_"+top_name+"_2_cap/"+str(num_bufs*2)+" \n")
		count += 2

	spice_file.write("Xinv_" + driver_name + "_"+str(num_bufs * 2)+" n_1_"+str(count)+" n_1_"+str(count + 1)+" n_vdd n_gnd inv Wn=inv_" + driver_name + "_"+str(num_bufs * 2)+"_nmos Wp=inv_" + driver_name + "_"+str(num_bufs * 2)+"_pmos\n")
	spice_file.write("Xwirer_edi_"+str(num_bufs * 2 + 1)+" n_1_"+str(count + 1)+" n_out wire Rw=wire_"+top_name+"_2_res/"+str(num_bufs*2)+" Cw=wire_"+top_name+"_2_cap/"+str(num_bufs*2)+" \n")

	spice_file.write(".ENDS\n\n\n")
	spice_file.close()
	
	# Create a list of all transistors used in this subcircuit
	tran_names_list = []
	for i in range(1, num_bufs * 2 + 1):
		tran_names_list.append("inv_" + driver_name + "_"+str(i)+"_nmos")
		tran_names_list.append("inv_" + driver_name + "_"+str(i)+"_pmos")
		
	
	# Create a list of all wires used in this subcircuit
	wire_names_list = []
	
	return tran_names_list, wire_names_list  
