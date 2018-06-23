def generate_ptran_2_input_select_d_ff(spice_filename, use_finfet):
	""" Generates a D Flip-Flop SPICE deck """
	
	# This script has to create the SPICE subcircuits required.
	# It has to return a list of the transistor names used as well as a list of the wire names used.
	
	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')
	
	# Create the FF circuit
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* FF subcircuit \n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT ff n_in n_out n_gate n_gate_n n_clk n_clk_n n_set n_set_n n_reset n_reset_n n_vdd n_gnd\n")
	spice_file.write("* Input selection MUX\n")
	spice_file.write("Xptran_ff_input_select n_in n_1_1 n_gate n_gnd ptran Wn=ptran_ff_input_select_nmos\n")
	spice_file.write("Xwire_ff_input_select n_1_1 n_1_2 wire Rw='wire_ff_input_select_res/2' Cw='wire_ff_input_select_cap/2'\n")
	spice_file.write("Xwire_ff_input_select_h n_1_2 n_1_3 wire Rw='wire_ff_input_select_res/2' Cw='wire_ff_input_select_cap/2'\n")
	spice_file.write("Xptran_ff_input_select_h n_gnd n_1_3 n_gate_n n_gnd ptran Wn=ptran_ff_input_select_nmos\n")
	spice_file.write("Xrest_ff_input_select n_1_2 n_2_1 n_vdd n_gnd rest Wp=rest_ff_input_select_pmos\n")
	spice_file.write("Xinv_ff_input_1 n_1_2 n_2_1 n_vdd n_gnd inv Wn=inv_ff_input_1_nmos Wp=inv_ff_input_1_pmos\n\n")
	spice_file.write("* First T-gate and cross-coupled inverters\n") 
	spice_file.write("Xwire_ff_input_out n_2_1 n_2_2 wire Rw=wire_ff_input_out_res Cw=wire_ff_input_out_cap\n")    
	spice_file.write("Xtgate_ff_1 n_2_2 n_3_1 n_clk_n n_clk n_vdd n_gnd tgate Wn=tgate_ff_1_nmos Wp=tgate_ff_1_pmos\n")
	if not use_finfet :
		spice_file.write("MPtran_ff_set_n n_3_1 n_set_n n_vdd n_vdd pmos L=gate_length W=tran_ff_set_n_pmos\n")
		spice_file.write("MNtran_ff_reset n_3_1 n_reset n_gnd n_gnd nmos L=gate_length W=tran_ff_reset_nmos\n")
	else :
		spice_file.write("MPtran_ff_set_n n_3_1 n_set_n n_vdd n_vdd pmos L=gate_length nfin=tran_ff_set_n_pmos\n")
		spice_file.write("MNtran_ff_reset n_3_1 n_reset n_gnd n_gnd nmos L=gate_length nfin=tran_ff_reset_nmos\n")

	spice_file.write("Xwire_ff_tgate_1_out n_3_1 n_3_2 wire Rw=wire_ff_tgate_1_out_res Cw=wire_ff_tgate_1_out_cap\n")
	spice_file.write("Xinv_ff_cc1_1 n_3_2 n_4_1 n_vdd n_gnd inv Wn=inv_ff_cc1_1_nmos Wp=inv_ff_cc1_1_pmos\n")
	spice_file.write("Xinv_ff_cc1_2 n_4_1 n_3_2 n_vdd n_gnd inv Wn=inv_ff_cc1_2_nmos Wp=inv_ff_cc1_2_pmos\n")
	spice_file.write("Xwire_ff_cc1_out n_4_1 n_4_2 wire Rw=wire_ff_cc1_out_res Cw=wire_ff_cc1_out_cap\n\n")
	spice_file.write("* Second T-gate and cross-coupled inverters\n")
	spice_file.write("Xtgate_ff_2 n_4_2 n_5_1 n_clk n_clk_n n_vdd n_gnd tgate Wn=tgate_ff_2_nmos Wp=tgate_ff_2_pmos\n")
	if not use_finfet :
		spice_file.write("MPtran_ff_reset_n n_5_1 n_reset_n n_vdd n_vdd pmos L=gate_length W=tran_ff_reset_n_pmos\n")
		spice_file.write("MNtran_ff_set n_5_1 n_set n_gnd n_gnd nmos L=gate_length W=tran_ff_set_nmos\n")
	else :
		spice_file.write("MPtran_ff_reset_n n_5_1 n_reset_n n_vdd n_vdd pmos L=gate_length nfin=tran_ff_reset_n_pmos\n")
		spice_file.write("MNtran_ff_set n_5_1 n_set n_gnd n_gnd nmos L=gate_length nfin=tran_ff_set_nmos\n")

	spice_file.write("Xwire_ff_tgate_2_out n_5_1 n_5_2 wire Rw=wire_ff_tgate_2_out_res Cw=wire_ff_tgate_2_out_cap\n")
	spice_file.write("Xinv_ff_cc2_1 n_5_2 n_6_1 n_vdd n_gnd inv Wn=inv_ff_cc2_1_nmos Wp=inv_ff_cc2_1_pmos\n")
	spice_file.write("Xinv_ff_cc2_2 n_6_1 n_5_2 n_vdd n_gnd inv Wn=inv_ff_cc2_2_nmos Wp=inv_ff_cc2_2_pmos\n")
	spice_file.write("Xwire_ff_cc2_out n_6_1 n_6_2 wire Rw=wire_ff_cc2_out_res Cw=wire_ff_cc2_out_cap\n\n")
	spice_file.write("* Output driver\n")
	spice_file.write("Xinv_ff_output_driver n_6_2 n_out n_vdd n_gnd inv Wn=inv_ff_output_driver_nmos Wp=inv_ff_output_driver_pmos\n\n")
	spice_file.write(".ENDS\n\n\n")
	  
	# Create a list of all transistors used in this subcircuit
	tran_names_list = []
	tran_names_list.append("ptran_ff_input_select_nmos")
	tran_names_list.append("rest_ff_input_select_pmos")
	tran_names_list.append("inv_ff_input_1_nmos")
	tran_names_list.append("inv_ff_input_1_pmos")
	tran_names_list.append("tgate_ff_1_nmos")
	tran_names_list.append("tgate_ff_1_pmos")
	tran_names_list.append("tran_ff_set_n_pmos")
	tran_names_list.append("tran_ff_reset_nmos")
	tran_names_list.append("inv_ff_cc1_1_nmos")
	tran_names_list.append("inv_ff_cc1_1_pmos")
	tran_names_list.append("inv_ff_cc1_2_nmos")
	tran_names_list.append("inv_ff_cc1_2_pmos")
	tran_names_list.append("tgate_ff_2_nmos")
	tran_names_list.append("tgate_ff_2_pmos")
	tran_names_list.append("tran_ff_reset_n_pmos")
	tran_names_list.append("tran_ff_set_nmos")
	tran_names_list.append("inv_ff_cc2_1_nmos")
	tran_names_list.append("inv_ff_cc2_1_pmos")
	tran_names_list.append("inv_ff_cc2_2_nmos")
	tran_names_list.append("inv_ff_cc2_2_pmos")
	tran_names_list.append("inv_ff_output_driver_nmos")
	tran_names_list.append("inv_ff_output_driver_pmos")
	
	# Create a list of all wires used in this subcircuit
	wire_names_list = []
	wire_names_list.append("wire_ff_input_select")
	wire_names_list.append("wire_ff_input_out")
	wire_names_list.append("wire_ff_tgate_1_out")
	wire_names_list.append("wire_ff_cc1_out")
	wire_names_list.append("wire_ff_tgate_2_out")
	wire_names_list.append("wire_ff_cc2_out")
  
	return tran_names_list, wire_names_list
	
	
def generate_ptran_d_ff(spice_filename, use_finfet):
	""" Generates a D Flip-Flop SPICE deck """
	
	# This script has to create the SPICE subcircuits required.
	# It has to return a list of the transistor names used as well as a list of the wire names used.
	
	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')
	
	# Create the FF circuit
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* FF subcircuit \n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT ff n_in n_out n_gate n_gate_n n_clk n_clk_n n_set n_set_n n_reset n_reset_n n_vdd n_gnd\n")
	spice_file.write("* FF input driver\n")
	spice_file.write("Xinv_ff_input n_1_2 n_2_1 n_vdd n_gnd inv Wn=inv_ff_input_1_nmos Wp=inv_ff_input_1_pmos\n\n")
	spice_file.write("* First T-gate and cross-coupled inverters\n") 
	spice_file.write("Xwire_ff_input_out n_2_1 n_2_2 wire Rw=wire_ff_input_out_res Cw=wire_ff_input_out_cap\n")    
	spice_file.write("Xtgate_ff_1 n_2_2 n_3_1 n_clk_n n_clk n_vdd n_gnd tgate Wn=tgate_ff_1_nmos Wp=tgate_ff_1_pmos\n")
	if not use_finfet :
		spice_file.write("MPtran_ff_set_n n_3_1 n_set_n n_vdd n_vdd pmos L=gate_length W=tran_ff_set_n_pmos\n")
		spice_file.write("MNtran_ff_reset n_3_1 n_reset n_gnd n_gnd nmos L=gate_length W=tran_ff_reset_nmos\n")
	else :
		spice_file.write("MPtran_ff_set_n n_3_1 n_set_n n_vdd n_vdd pmos L=gate_length nfin=tran_ff_set_n_pmos\n")
		spice_file.write("MNtran_ff_reset n_3_1 n_reset n_gnd n_gnd nmos L=gate_length nfin=tran_ff_reset_nmos\n")

	spice_file.write("Xwire_ff_tgate_1_out n_3_1 n_3_2 wire Rw=wire_ff_tgate_1_out_res Cw=wire_ff_tgate_1_out_cap\n")
	spice_file.write("Xinv_ff_cc1_1 n_3_2 n_4_1 n_vdd n_gnd inv Wn=inv_ff_cc1_1_nmos Wp=inv_ff_cc1_1_pmos\n")
	spice_file.write("Xinv_ff_cc1_2 n_4_1 n_3_2 n_vdd n_gnd inv Wn=inv_ff_cc1_2_nmos Wp=inv_ff_cc1_2_pmos\n")
	spice_file.write("Xwire_ff_cc1_out n_4_1 n_4_2 wire Rw=wire_ff_cc1_out_res Cw=wire_ff_cc1_out_cap\n\n")
	spice_file.write("* Second T-gate and cross-coupled inverters\n")
	spice_file.write("Xtgate_ff_2 n_4_2 n_5_1 n_clk n_clk_n n_vdd n_gnd tgate Wn=tgate_ff_2_nmos Wp=tgate_ff_2_pmos\n")
	if not use_finfet : 
		spice_file.write("MPtran_ff_reset_n n_5_1 n_reset_n n_vdd n_vdd pmos L=gate_length W=tran_ff_reset_n_pmos\n")
		spice_file.write("MNtran_ff_set n_5_1 n_set n_gnd n_gnd nmos L=gate_length W=tran_ff_set_nmos\n")
	else :
		spice_file.write("MPtran_ff_reset_n n_5_1 n_reset_n n_vdd n_vdd pmos L=gate_length W=tran_ff_reset_n_pmos\n")
		spice_file.write("MNtran_ff_set n_5_1 n_set n_gnd n_gnd nmos L=gate_length W=tran_ff_set_nmos\n")
	spice_file.write("Xwire_ff_tgate_2_out n_5_1 n_5_2 wire Rw=wire_ff_tgate_2_out_res Cw=wire_ff_tgate_2_out_cap\n")
	spice_file.write("Xinv_ff_cc2_1 n_5_2 n_6_1 n_vdd n_gnd inv Wn=inv_ff_cc2_1_nmos Wp=inv_ff_cc2_1_pmos\n")
	spice_file.write("Xinv_ff_cc2_2 n_6_1 n_5_2 n_vdd n_gnd inv Wn=inv_ff_cc2_2_nmos Wp=inv_ff_cc2_2_pmos\n")
	spice_file.write("Xwire_ff_cc2_out n_6_1 n_6_2 wire Rw=wire_ff_cc2_out_res Cw=wire_ff_cc2_out_cap\n\n")
	spice_file.write("* Output driver\n")
	spice_file.write("Xinv_ff_output_driver n_6_2 n_out n_vdd n_gnd inv Wn=inv_ff_output_driver_nmos Wp=inv_ff_output_driver_pmos\n\n")
	spice_file.write(".ENDS\n\n\n")
	  
	# Create a list of all transistors used in this subcircuit
	tran_names_list = []
	tran_names_list.append("inv_ff_input_1_nmos")
	tran_names_list.append("inv_ff_input_1_pmos")
	tran_names_list.append("tgate_ff_1_nmos")
	tran_names_list.append("tgate_ff_1_pmos")
	tran_names_list.append("tran_ff_set_n_pmos")
	tran_names_list.append("tran_ff_reset_nmos")
	tran_names_list.append("inv_ff_cc1_1_nmos")
	tran_names_list.append("inv_ff_cc1_1_pmos")
	tran_names_list.append("inv_ff_cc1_2_nmos")
	tran_names_list.append("inv_ff_cc1_2_pmos")
	tran_names_list.append("tgate_ff_2_nmos")
	tran_names_list.append("tgate_ff_2_pmos")
	tran_names_list.append("tran_ff_reset_n_pmos")
	tran_names_list.append("tran_ff_set_nmos")
	tran_names_list.append("inv_ff_cc2_1_nmos")
	tran_names_list.append("inv_ff_cc2_1_pmos")
	tran_names_list.append("inv_ff_cc2_2_nmos")
	tran_names_list.append("inv_ff_cc2_2_pmos")
	tran_names_list.append("inv_ff_output_driver_nmos")
	tran_names_list.append("inv_ff_output_driver_pmos")
	
	# Create a list of all wires used in this subcircuit
	wire_names_list = []
	wire_names_list.append("wire_ff_input_out")
	wire_names_list.append("wire_ff_tgate_1_out")
	wire_names_list.append("wire_ff_cc1_out")
	wire_names_list.append("wire_ff_tgate_2_out")
	wire_names_list.append("wire_ff_cc2_out")
  
	return tran_names_list, wire_names_list












def generate_tgate_2_input_select_d_ff(spice_filename, use_finfet):
	""" Generates a D Flip-Flop SPICE deck """
	
	# This script has to create the SPICE subcircuits required.
	# It has to return a list of the transistor names used as well as a list of the wire names used.
	
	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')
	
	# Create the FF circuit
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* FF subcircuit \n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT ff n_in n_out n_gate n_gate_n n_clk n_clk_n n_set n_set_n n_reset n_reset_n n_vdd n_gnd\n")
	spice_file.write("* Input selection MUX\n")

	spice_file.write("Xtgate_ff_input_select n_in n_1_1 n_gate n_gate_n n_vdd n_gnd tgate Wn=tgate_ff_input_select_nmos Wp=tgate_ff_input_select_pmos\n")
	
	spice_file.write("Xwire_ff_input_select n_1_1 n_1_2 wire Rw='wire_ff_input_select_res/2' Cw='wire_ff_input_select_cap/2'\n")
	spice_file.write("Xwire_ff_input_select_h n_1_2 n_1_3 wire Rw='wire_ff_input_select_res/2' Cw='wire_ff_input_select_cap/2'\n")

	spice_file.write("Xtgate_ff_input_select_h n_gnd n_1_3 n_gate_n n_gate n_vdd n_gnd tgate Wn=tgate_ff_input_select_nmos Wp=tgate_ff_input_select_pmos\n")
	# spice_file.write("Xrest_ff_input_select n_1_2 n_2_1 n_vdd n_gnd rest Wp=rest_ff_input_select_pmos\n")

	spice_file.write("Xinv_ff_input_1 n_1_2 n_2_1 n_vdd n_gnd inv Wn=inv_ff_input_1_nmos Wp=inv_ff_input_1_pmos\n\n")
	spice_file.write("* First T-gate and cross-coupled inverters\n") 
	spice_file.write("Xwire_ff_input_out n_2_1 n_2_2 wire Rw=wire_ff_input_out_res Cw=wire_ff_input_out_cap\n")    
	spice_file.write("Xtgate_ff_1 n_2_2 n_3_1 n_clk_n n_clk n_vdd n_gnd tgate Wn=tgate_ff_1_nmos Wp=tgate_ff_1_pmos\n")
	if not use_finfet :
		spice_file.write("MPtran_ff_set_n n_3_1 n_set_n n_vdd n_vdd pmos L=gate_length W=tran_ff_set_n_pmos\n")
		spice_file.write("MNtran_ff_reset n_3_1 n_reset n_gnd n_gnd nmos L=gate_length W=tran_ff_reset_nmos\n")
	else :
		spice_file.write("MPtran_ff_set_n n_3_1 n_set_n n_vdd n_vdd pmos L=gate_length nfin=tran_ff_set_n_pmos\n")
		spice_file.write("MNtran_ff_reset n_3_1 n_reset n_gnd n_gnd nmos L=gate_length nfin=tran_ff_reset_nmos\n")

	spice_file.write("Xwire_ff_tgate_1_out n_3_1 n_3_2 wire Rw=wire_ff_tgate_1_out_res Cw=wire_ff_tgate_1_out_cap\n")
	spice_file.write("Xinv_ff_cc1_1 n_3_2 n_4_1 n_vdd n_gnd inv Wn=inv_ff_cc1_1_nmos Wp=inv_ff_cc1_1_pmos\n")
	spice_file.write("Xinv_ff_cc1_2 n_4_1 n_3_2 n_vdd n_gnd inv Wn=inv_ff_cc1_2_nmos Wp=inv_ff_cc1_2_pmos\n")
	spice_file.write("Xwire_ff_cc1_out n_4_1 n_4_2 wire Rw=wire_ff_cc1_out_res Cw=wire_ff_cc1_out_cap\n\n")
	spice_file.write("* Second T-gate and cross-coupled inverters\n")
	spice_file.write("Xtgate_ff_2 n_4_2 n_5_1 n_clk n_clk_n n_vdd n_gnd tgate Wn=tgate_ff_2_nmos Wp=tgate_ff_2_pmos\n")
	if not use_finfet :
		spice_file.write("MPtran_ff_reset_n n_5_1 n_reset_n n_vdd n_vdd pmos L=gate_length W=tran_ff_reset_n_pmos\n")
		spice_file.write("MNtran_ff_set n_5_1 n_set n_gnd n_gnd nmos L=gate_length W=tran_ff_set_nmos\n")
	else :
		spice_file.write("MPtran_ff_reset_n n_5_1 n_reset_n n_vdd n_vdd pmos L=gate_length nfin=tran_ff_reset_n_pmos\n")
		spice_file.write("MNtran_ff_set n_5_1 n_set n_gnd n_gnd nmos L=gate_length nfin=tran_ff_set_nmos\n")

	spice_file.write("Xwire_ff_tgate_2_out n_5_1 n_5_2 wire Rw=wire_ff_tgate_2_out_res Cw=wire_ff_tgate_2_out_cap\n")
	spice_file.write("Xinv_ff_cc2_1 n_5_2 n_6_1 n_vdd n_gnd inv Wn=inv_ff_cc2_1_nmos Wp=inv_ff_cc2_1_pmos\n")
	spice_file.write("Xinv_ff_cc2_2 n_6_1 n_5_2 n_vdd n_gnd inv Wn=inv_ff_cc2_2_nmos Wp=inv_ff_cc2_2_pmos\n")
	spice_file.write("Xwire_ff_cc2_out n_6_1 n_6_2 wire Rw=wire_ff_cc2_out_res Cw=wire_ff_cc2_out_cap\n\n")
	spice_file.write("* Output driver\n")
	spice_file.write("Xinv_ff_output_driver n_6_2 n_out n_vdd n_gnd inv Wn=inv_ff_output_driver_nmos Wp=inv_ff_output_driver_pmos\n\n")
	spice_file.write(".ENDS\n\n\n")
	  
	# Create a list of all transistors used in this subcircuit
	tran_names_list = []
	tran_names_list.append("tgate_ff_input_select_nmos")
	tran_names_list.append("tgate_ff_input_select_pmos")
	# tran_names_list.append("rest_ff_input_select_pmos")
	tran_names_list.append("inv_ff_input_1_nmos")
	tran_names_list.append("inv_ff_input_1_pmos")
	tran_names_list.append("tgate_ff_1_nmos")
	tran_names_list.append("tgate_ff_1_pmos")
	tran_names_list.append("tran_ff_set_n_pmos")
	tran_names_list.append("tran_ff_reset_nmos")
	tran_names_list.append("inv_ff_cc1_1_nmos")
	tran_names_list.append("inv_ff_cc1_1_pmos")
	tran_names_list.append("inv_ff_cc1_2_nmos")
	tran_names_list.append("inv_ff_cc1_2_pmos")
	tran_names_list.append("tgate_ff_2_nmos")
	tran_names_list.append("tgate_ff_2_pmos")
	tran_names_list.append("tran_ff_reset_n_pmos")
	tran_names_list.append("tran_ff_set_nmos")
	tran_names_list.append("inv_ff_cc2_1_nmos")
	tran_names_list.append("inv_ff_cc2_1_pmos")
	tran_names_list.append("inv_ff_cc2_2_nmos")
	tran_names_list.append("inv_ff_cc2_2_pmos")
	tran_names_list.append("inv_ff_output_driver_nmos")
	tran_names_list.append("inv_ff_output_driver_pmos")
	
	# Create a list of all wires used in this subcircuit
	wire_names_list = []
	wire_names_list.append("wire_ff_input_select")
	wire_names_list.append("wire_ff_input_out")
	wire_names_list.append("wire_ff_tgate_1_out")
	wire_names_list.append("wire_ff_cc1_out")
	wire_names_list.append("wire_ff_tgate_2_out")
	wire_names_list.append("wire_ff_cc2_out")
  
	return tran_names_list, wire_names_list
	
	
def generate_tgate_d_ff(spice_filename, use_finfet):
	""" Generates a D Flip-Flop SPICE deck """
	
	# This script has to create the SPICE subcircuits required.
	# It has to return a list of the transistor names used as well as a list of the wire names used.
	
	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')
	
	# Create the FF circuit
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* FF subcircuit \n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT ff n_in n_out n_gate n_gate_n n_clk n_clk_n n_set n_set_n n_reset n_reset_n n_vdd n_gnd\n")
	spice_file.write("* FF input driver\n")
	spice_file.write("Xinv_ff_input n_1_2 n_2_1 n_vdd n_gnd inv Wn=inv_ff_input_1_nmos Wp=inv_ff_input_1_pmos\n\n")
	spice_file.write("* First T-gate and cross-coupled inverters\n") 
	spice_file.write("Xwire_ff_input_out n_2_1 n_2_2 wire Rw=wire_ff_input_out_res Cw=wire_ff_input_out_cap\n")    
	spice_file.write("Xtgate_ff_1 n_2_2 n_3_1 n_clk_n n_clk n_vdd n_gnd tgate Wn=tgate_ff_1_nmos Wp=tgate_ff_1_pmos\n")
	if not use_finfet :
		spice_file.write("MPtran_ff_set_n n_3_1 n_set_n n_vdd n_vdd pmos L=gate_length W=tran_ff_set_n_pmos\n")
		spice_file.write("MNtran_ff_reset n_3_1 n_reset n_gnd n_gnd nmos L=gate_length W=tran_ff_reset_nmos\n")
	else :
		spice_file.write("MPtran_ff_set_n n_3_1 n_set_n n_vdd n_vdd pmos L=gate_length nfin=tran_ff_set_n_pmos\n")
		spice_file.write("MNtran_ff_reset n_3_1 n_reset n_gnd n_gnd nmos L=gate_length nfin=tran_ff_reset_nmos\n")

	spice_file.write("Xwire_ff_tgate_1_out n_3_1 n_3_2 wire Rw=wire_ff_tgate_1_out_res Cw=wire_ff_tgate_1_out_cap\n")
	spice_file.write("Xinv_ff_cc1_1 n_3_2 n_4_1 n_vdd n_gnd inv Wn=inv_ff_cc1_1_nmos Wp=inv_ff_cc1_1_pmos\n")
	spice_file.write("Xinv_ff_cc1_2 n_4_1 n_3_2 n_vdd n_gnd inv Wn=inv_ff_cc1_2_nmos Wp=inv_ff_cc1_2_pmos\n")
	spice_file.write("Xwire_ff_cc1_out n_4_1 n_4_2 wire Rw=wire_ff_cc1_out_res Cw=wire_ff_cc1_out_cap\n\n")
	spice_file.write("* Second T-gate and cross-coupled inverters\n")
	spice_file.write("Xtgate_ff_2 n_4_2 n_5_1 n_clk n_clk_n n_vdd n_gnd tgate Wn=tgate_ff_2_nmos Wp=tgate_ff_2_pmos\n")
	if not use_finfet : 
		spice_file.write("MPtran_ff_reset_n n_5_1 n_reset_n n_vdd n_vdd pmos L=gate_length W=tran_ff_reset_n_pmos\n")
		spice_file.write("MNtran_ff_set n_5_1 n_set n_gnd n_gnd nmos L=gate_length W=tran_ff_set_nmos\n")
	else :
		spice_file.write("MPtran_ff_reset_n n_5_1 n_reset_n n_vdd n_vdd pmos L=gate_length W=tran_ff_reset_n_pmos\n")
		spice_file.write("MNtran_ff_set n_5_1 n_set n_gnd n_gnd nmos L=gate_length W=tran_ff_set_nmos\n")
	spice_file.write("Xwire_ff_tgate_2_out n_5_1 n_5_2 wire Rw=wire_ff_tgate_2_out_res Cw=wire_ff_tgate_2_out_cap\n")
	spice_file.write("Xinv_ff_cc2_1 n_5_2 n_6_1 n_vdd n_gnd inv Wn=inv_ff_cc2_1_nmos Wp=inv_ff_cc2_1_pmos\n")
	spice_file.write("Xinv_ff_cc2_2 n_6_1 n_5_2 n_vdd n_gnd inv Wn=inv_ff_cc2_2_nmos Wp=inv_ff_cc2_2_pmos\n")
	spice_file.write("Xwire_ff_cc2_out n_6_1 n_6_2 wire Rw=wire_ff_cc2_out_res Cw=wire_ff_cc2_out_cap\n\n")
	spice_file.write("* Output driver\n")
	spice_file.write("Xinv_ff_output_driver n_6_2 n_out n_vdd n_gnd inv Wn=inv_ff_output_driver_nmos Wp=inv_ff_output_driver_pmos\n\n")
	spice_file.write(".ENDS\n\n\n")
	  
	# Create a list of all transistors used in this subcircuit
	tran_names_list = []
	tran_names_list.append("inv_ff_input_1_nmos")
	tran_names_list.append("inv_ff_input_1_pmos")
	tran_names_list.append("tgate_ff_1_nmos")
	tran_names_list.append("tgate_ff_1_pmos")
	tran_names_list.append("tran_ff_set_n_pmos")
	tran_names_list.append("tran_ff_reset_nmos")
	tran_names_list.append("inv_ff_cc1_1_nmos")
	tran_names_list.append("inv_ff_cc1_1_pmos")
	tran_names_list.append("inv_ff_cc1_2_nmos")
	tran_names_list.append("inv_ff_cc1_2_pmos")
	tran_names_list.append("tgate_ff_2_nmos")
	tran_names_list.append("tgate_ff_2_pmos")
	tran_names_list.append("tran_ff_reset_n_pmos")
	tran_names_list.append("tran_ff_set_nmos")
	tran_names_list.append("inv_ff_cc2_1_nmos")
	tran_names_list.append("inv_ff_cc2_1_pmos")
	tran_names_list.append("inv_ff_cc2_2_nmos")
	tran_names_list.append("inv_ff_cc2_2_pmos")
	tran_names_list.append("inv_ff_output_driver_nmos")
	tran_names_list.append("inv_ff_output_driver_pmos")
	
	# Create a list of all wires used in this subcircuit
	wire_names_list = []
	wire_names_list.append("wire_ff_input_out")
	wire_names_list.append("wire_ff_tgate_1_out")
	wire_names_list.append("wire_ff_cc1_out")
	wire_names_list.append("wire_ff_tgate_2_out")
	wire_names_list.append("wire_ff_cc2_out")
  
	return tran_names_list, wire_names_list