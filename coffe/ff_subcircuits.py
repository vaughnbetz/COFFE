import mux_subcircuits

def generate_ptran_2_input_select_d_ff(spice_filename, use_finfet):
	""" Generates a D Flip-Flop SPICE deck with a Rsel mux at its input """
	
	# This script has to create the SPICE subcircuits required.
	# It has to return a list of the transistor names used as well as a list of the wire names used.
	
	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')
	
	# Create the FF circuit
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* FF subcircuit \n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT ff n_in n_out n_gate n_gate_n n_clk n_clk_n n_set n_set_n n_reset n_reset_n n_vdd n_gnd\n\n")

	spice_file.write("* Input selection MUX\n")
	spice_file.write("Xptran_ff_input_select n_in n_1_1 n_gate n_gnd ptran Wn=ptran_ff_input_select_nmos\n")
	spice_file.write("Xwire_ff_input_select n_1_1 n_1_2 wire Rw='wire_ff_input_select_res/2' Cw='wire_ff_input_select_cap/2'\n")
	spice_file.write("Xwire_ff_input_select_h n_1_2 n_1_3 wire Rw='wire_ff_input_select_res/2' Cw='wire_ff_input_select_cap/2'\n")
	spice_file.write("Xptran_ff_input_select_h n_gnd n_1_3 n_gate_n n_gnd ptran Wn=ptran_ff_input_select_nmos\n")
	spice_file.write("Xrest_ff_input_select n_1_2 n_2_1 n_vdd n_gnd rest Wp=rest_ff_input_select_pmos\n\n")

	spice_file.write("* FF input driver\n")
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

	# Close SPICE file
	spice_file.close()
	  
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
	
	
def generate_ptran_d_ff(spice_filename, use_finfet, with_driver = True):
	""" Generates a D Flip-Flop SPICE deck """
	
	# This script has to create the SPICE subcircuits required.
	# It has to return a list of the transistor names used as well as a list of the wire names used.
	
	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')

	if with_driver:
		n_2_1 = "n_2_1"
	else:
		n_2_1 = "n_in"
	
	# Create the FF circuit
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* FF subcircuit \n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT ff_only n_in n_out n_gate n_gate_n n_clk n_clk_n n_set n_set_n n_reset n_reset_n n_vdd n_gnd\n\n")

	if with_driver:
		spice_file.write("* FF input driver\n")
		spice_file.write("Xinv_ff_input n_in n_2_1 n_vdd n_gnd inv Wn=inv_ff_input_1_nmos Wp=inv_ff_input_1_pmos\n\n")

	spice_file.write("* First T-gate and cross-coupled inverters\n") 
	spice_file.write("Xwire_ff_input_out "+n_2_1+" n_2_2 wire Rw=wire_ff_input_out_res Cw=wire_ff_input_out_cap\n")    
	spice_file.write("Xtgate_ff_1 n_2_2 n_3_1 n_clk_n n_clk n_vdd n_gnd tgate Wn=tgate_ff_1_nmos Wp=tgate_ff_1_pmos\n")
	if not use_finfet:
		spice_file.write("MPtran_ff_set_n n_3_1 n_set_n n_vdd n_vdd pmos L=gate_length W=tran_ff_set_n_pmos\n")
		spice_file.write("MNtran_ff_reset n_3_1 n_reset n_gnd n_gnd nmos L=gate_length W=tran_ff_reset_nmos\n")
	else:
		spice_file.write("MPtran_ff_set_n n_3_1 n_set_n n_vdd n_vdd pmos L=gate_length nfin=tran_ff_set_n_pmos\n")
		spice_file.write("MNtran_ff_reset n_3_1 n_reset n_gnd n_gnd nmos L=gate_length nfin=tran_ff_reset_nmos\n")
	spice_file.write("Xwire_ff_tgate_1_out n_3_1 n_3_2 wire Rw=wire_ff_tgate_1_out_res Cw=wire_ff_tgate_1_out_cap\n")
	spice_file.write("Xinv_ff_cc1_1 n_3_2 n_4_1 n_vdd n_gnd inv Wn=inv_ff_cc1_1_nmos Wp=inv_ff_cc1_1_pmos\n")
	spice_file.write("Xinv_ff_cc1_2 n_4_1 n_3_2 n_vdd n_gnd inv Wn=inv_ff_cc1_2_nmos Wp=inv_ff_cc1_2_pmos\n")
	spice_file.write("Xwire_ff_cc1_out n_4_1 n_4_2 wire Rw=wire_ff_cc1_out_res Cw=wire_ff_cc1_out_cap\n\n")

	spice_file.write("* Second T-gate and cross-coupled inverters\n")
	spice_file.write("Xtgate_ff_2 n_4_2 n_5_1 n_clk n_clk_n n_vdd n_gnd tgate Wn=tgate_ff_2_nmos Wp=tgate_ff_2_pmos\n")
	if not use_finfet: 
		spice_file.write("MPtran_ff_reset_n n_5_1 n_reset_n n_vdd n_vdd pmos L=gate_length W=tran_ff_reset_n_pmos\n")
		spice_file.write("MNtran_ff_set n_5_1 n_set n_gnd n_gnd nmos L=gate_length W=tran_ff_set_nmos\n")
	else:
		spice_file.write("MPtran_ff_reset_n n_5_1 n_reset_n n_vdd n_vdd pmos L=gate_length nfin=tran_ff_reset_n_pmos\n")
		spice_file.write("MNtran_ff_set n_5_1 n_set n_gnd n_gnd nmos L=gate_length nfin=tran_ff_set_nmos\n")
	spice_file.write("Xwire_ff_tgate_2_out n_5_1 n_5_2 wire Rw=wire_ff_tgate_2_out_res Cw=wire_ff_tgate_2_out_cap\n")
	spice_file.write("Xinv_ff_cc2_1 n_5_2 n_6_1 n_vdd n_gnd inv Wn=inv_ff_cc2_1_nmos Wp=inv_ff_cc2_1_pmos\n")
	spice_file.write("Xinv_ff_cc2_2 n_6_1 n_5_2 n_vdd n_gnd inv Wn=inv_ff_cc2_2_nmos Wp=inv_ff_cc2_2_pmos\n")
	spice_file.write("Xwire_ff_cc2_out n_6_1 n_6_2 wire Rw=wire_ff_cc2_out_res Cw=wire_ff_cc2_out_cap\n\n")

	spice_file.write("* Output driver\n")
	spice_file.write("Xinv_ff_output_driver n_6_2 n_out n_vdd n_gnd inv Wn=inv_ff_output_driver_nmos Wp=inv_ff_output_driver_pmos\n\n")

	spice_file.write(".ENDS\n\n\n")

	# Close SPICE file
	spice_file.close()
	  
	# Create a list of all transistors used in this subcircuit
	tran_names_list = []
	if with_driver:
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



def generate_dff(spice_filename, name, use_finfet, use_tgate, Rsel, input_size, mux_name, ff_generated):
	""" This function creates a d flip flop and optionally an input select mux of any
		size could be added to it. This supports either pass-transistor or transmission gates"""
	# TODO: add a mux name as an input since for different ff the ff itself is the same but the  input 
	# input mux should be different and the total subcircuit name should be different

	with_driver = False
	transistor_name_list = []
	wire_names_list = []

	if not ff_generated:
		if use_tgate:
			transistor_name_list, wire_names_list = generate_tgate_d_ff(spice_filename, use_finfet, with_driver)
		else:
			transistor_name_list, wire_names_list = generate_ptran_d_ff(spice_filename, use_finfet, with_driver)

	
	# generate ptran dff and tgate dff are exactly the same functions
	#transistor_name_list, wire_names_list = generate_ptran_d_ff(spice_filename, use_finfet, with_driver)

	title = ""
	if Rsel:
		n_1_1 = "n_1_1"
		#name += "_with_mux"
		title = "with input mux "
	else:
		n_1_1 = "n_in"

	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')

	# Create the FF circuit with driver and input select mux
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* FF "+title+"subcircuit \n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT "+name+" n_in n_out n_gate n_gate_n n_clk n_clk_n n_set n_set_n n_reset n_reset_n n_vdd n_gnd\n\n")

	if Rsel:
		spice_file.write("X"+mux_name+" n_in n_1_1 n_gate n_gate_n n_vdd n_gnd "+mux_name+"\n\n")
		if not use_tgate:
			spice_file.write("Xrest_"+mux_name+" n_1_1 n_1_2 n_vdd n_gnd rest Wp=rest_"+mux_name+"_pmos\n\n")

	spice_file.write("Xinv_ff_input_1 "+n_1_1+" n_1_2 n_vdd n_gnd inv Wn=inv_ff_input_1_nmos Wp=inv_ff_input_1_pmos\n\n")
	spice_file.write("Xff_only n_1_2 n_out n_gate n_gate_n n_clk n_clk_n n_set n_set_n n_reset n_reset_n n_vdd n_gnd ff_only\n\n")

	spice_file.write(".ENDS\n\n\n")

	# Close SPICE file
	spice_file.close()

	if not ff_generated:
		transistor_name_list.append("inv_ff_input_1_nmos")
		transistor_name_list.append("inv_ff_input_1_pmos")
	if Rsel and not use_tgate:
		transistor_name_list.append("rest_"+mux_name+"_pmos")


	return transistor_name_list, wire_names_list


def generate_tgate_2_input_select_d_ff(spice_filename, use_finfet):
	""" Generates a D Flip-Flop SPICE deck with a Rsel mux at its input """
	
	# This script has to create the SPICE subcircuits required.
	# It has to return a list of the transistor names used as well as a list of the wire names used.
	
	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')
	
	# Create the FF circuit
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* FF subcircuit \n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT ff n_in n_out n_gate n_gate_n n_clk n_clk_n n_set n_set_n n_reset n_reset_n n_vdd n_gnd\n\n")

	spice_file.write("* Input selection MUX\n")
	spice_file.write("Xtgate_ff_input_select n_in n_1_1 n_gate n_gate_n n_vdd n_gnd tgate Wn=tgate_ff_input_select_nmos Wp=tgate_ff_input_select_pmos\n")
	spice_file.write("Xwire_ff_input_select n_1_1 n_1_2 wire Rw='wire_ff_input_select_res/2' Cw='wire_ff_input_select_cap/2'\n")
	spice_file.write("Xwire_ff_input_select_h n_1_2 n_1_3 wire Rw='wire_ff_input_select_res/2' Cw='wire_ff_input_select_cap/2'\n")
	spice_file.write("Xtgate_ff_input_select_h n_gnd n_1_3 n_gate_n n_gate n_vdd n_gnd tgate Wn=tgate_ff_input_select_nmos Wp=tgate_ff_input_select_pmos\n\n")

	spice_file.write("* FF input driver\n")
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

	# Close SPICE file
	spice_file.close()
	  
	# Create a list of all transistors used in this subcircuit
	tran_names_list = []
	tran_names_list.append("tgate_ff_input_select_nmos")
	tran_names_list.append("tgate_ff_input_select_pmos")
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
	
	
def generate_tgate_d_ff(spice_filename, use_finfet, with_driver = True):
	""" Generates a D Flip-Flop SPICE deck with an input driver"""
	
	# This script has to create the SPICE subcircuits required.
	# It has to return a list of the transistor names used as well as a list of the wire names used.
	
	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')

	if with_driver:
		n_2_1 = "n_2_1"
	else:
		n_2_1 = "n_in"
	
	# Create the FF circuit
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* FF subcircuit \n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT ff_only n_in n_out n_gate n_gate_n n_clk n_clk_n n_set n_set_n n_reset n_reset_n n_vdd n_gnd\n\n")

	if with_driver:
		spice_file.write("* FF input driver\n")
		spice_file.write("Xinv_ff_input n_in n_2_1 n_vdd n_gnd inv Wn=inv_ff_input_1_nmos Wp=inv_ff_input_1_pmos\n\n")

	spice_file.write("* First T-gate and cross-coupled inverters\n") 
	spice_file.write("Xwire_ff_input_out "+n_2_1+" n_2_2 wire Rw=wire_ff_input_out_res Cw=wire_ff_input_out_cap\n")    
	spice_file.write("Xtgate_ff_1 n_2_2 n_3_1 n_clk_n n_clk n_vdd n_gnd tgate Wn=tgate_ff_1_nmos Wp=tgate_ff_1_pmos\n")
	if not use_finfet:
		spice_file.write("MPtran_ff_set_n n_3_1 n_set_n n_vdd n_vdd pmos L=gate_length W=tran_ff_set_n_pmos\n")
		spice_file.write("MNtran_ff_reset n_3_1 n_reset n_gnd n_gnd nmos L=gate_length W=tran_ff_reset_nmos\n")
	else:
		spice_file.write("MPtran_ff_set_n n_3_1 n_set_n n_vdd n_vdd pmos L=gate_length nfin=tran_ff_set_n_pmos\n")
		spice_file.write("MNtran_ff_reset n_3_1 n_reset n_gnd n_gnd nmos L=gate_length nfin=tran_ff_reset_nmos\n")
	spice_file.write("Xwire_ff_tgate_1_out n_3_1 n_3_2 wire Rw=wire_ff_tgate_1_out_res Cw=wire_ff_tgate_1_out_cap\n")
	spice_file.write("Xinv_ff_cc1_1 n_3_2 n_4_1 n_vdd n_gnd inv Wn=inv_ff_cc1_1_nmos Wp=inv_ff_cc1_1_pmos\n")
	spice_file.write("Xinv_ff_cc1_2 n_4_1 n_3_2 n_vdd n_gnd inv Wn=inv_ff_cc1_2_nmos Wp=inv_ff_cc1_2_pmos\n")
	spice_file.write("Xwire_ff_cc1_out n_4_1 n_4_2 wire Rw=wire_ff_cc1_out_res Cw=wire_ff_cc1_out_cap\n\n")

	spice_file.write("* Second T-gate and cross-coupled inverters\n")
	spice_file.write("Xtgate_ff_2 n_4_2 n_5_1 n_clk n_clk_n n_vdd n_gnd tgate Wn=tgate_ff_2_nmos Wp=tgate_ff_2_pmos\n")
	if not use_finfet: 
		spice_file.write("MPtran_ff_reset_n n_5_1 n_reset_n n_vdd n_vdd pmos L=gate_length W=tran_ff_reset_n_pmos\n")
		spice_file.write("MNtran_ff_set n_5_1 n_set n_gnd n_gnd nmos L=gate_length W=tran_ff_set_nmos\n")
	else:
		spice_file.write("MPtran_ff_reset_n n_5_1 n_reset_n n_vdd n_vdd pmos L=gate_length nfin=tran_ff_reset_n_pmos\n")
		spice_file.write("MNtran_ff_set n_5_1 n_set n_gnd n_gnd nmos L=gate_length nfin=tran_ff_set_nmos\n")
	spice_file.write("Xwire_ff_tgate_2_out n_5_1 n_5_2 wire Rw=wire_ff_tgate_2_out_res Cw=wire_ff_tgate_2_out_cap\n")
	spice_file.write("Xinv_ff_cc2_1 n_5_2 n_6_1 n_vdd n_gnd inv Wn=inv_ff_cc2_1_nmos Wp=inv_ff_cc2_1_pmos\n")
	spice_file.write("Xinv_ff_cc2_2 n_6_1 n_5_2 n_vdd n_gnd inv Wn=inv_ff_cc2_2_nmos Wp=inv_ff_cc2_2_pmos\n")
	spice_file.write("Xwire_ff_cc2_out n_6_1 n_6_2 wire Rw=wire_ff_cc2_out_res Cw=wire_ff_cc2_out_cap\n\n")

	spice_file.write("* Output driver\n")
	spice_file.write("Xinv_ff_output_driver n_6_2 n_out n_vdd n_gnd inv Wn=inv_ff_output_driver_nmos Wp=inv_ff_output_driver_pmos\n\n")

	spice_file.write(".ENDS\n\n\n")

	# Close SPICE file
	spice_file.close()
	  
	# Create a list of all transistors used in this subcircuit
	tran_names_list = []
	if with_driver:
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