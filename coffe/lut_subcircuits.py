import math

# Note: We generate all LUT netlists with a 6-LUT interface regardless of LUT size.
# This makes it easier to include the LUT circuitry in other (top-level) netlists.
# For example, a 5-LUT has the following interface:
# "lut n_in n_out n_a n_b n_c n_d n_e n_f n_vdd n_gnd", which is the same thing as 
# a 6-LUT, but in the 5-LUT case, there is nothing connected to "n_f" inside the LUT
# netlist itself.


# TODO: combine all the LUT generatins into one function that takes the lut
#		size to reduce the amount of code repetition and make differences
#		between them more obvious

def generate_ptran_lut6(spice_filename, min_tran_width, use_finfet):
	""" Generates a 6LUT SPICE deck """
	
	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')
	
	# Create the 6-LUT circuit
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* 6-LUT subcircuit \n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT lut n_in n_out n_a n_b n_c n_d n_e n_f n_vdd n_gnd\n")
	Wn = min_tran_width
	Wp = 1.667*min_tran_width
	if not use_finfet:
		spice_file.write("Xinv_lut_sram_driver_1 n_in n_1_1 n_vdd n_gnd inv Wn=" + str(Wn) + "n Wp=" + str(Wp) + "n\n")
	else:
		spice_file.write("Xinv_lut_sram_driver_1 n_in n_1_1 n_vdd n_gnd inv Wn=1 Wp=1\n")

	spice_file.write("Xwire_lut_sram_driver n_1_1 n_1_2 wire Rw=wire_lut_sram_driver_res Cw=wire_lut_sram_driver_cap\n")
	spice_file.write("Xinv_lut_sram_driver_2 n_1_2 n_2_1 n_vdd n_gnd inv Wn=inv_lut_0sram_driver_2_nmos Wp=inv_lut_0sram_driver_2_pmos\n")
	spice_file.write("Xwire_lut_sram_driver_out n_2_1 n_2_2 wire Rw=wire_lut_sram_driver_out_res Cw=wire_lut_sram_driver_out_cap\n\n")
	
	spice_file.write("* First chain\n")
	spice_file.write("Xptran_lut_L1 n_2_2 n_3_1 n_a n_gnd ptran Wn=ptran_lut_L1_nmos\n")
	spice_file.write("Xwire_lut_L1 n_3_1 n_3_2 wire Rw='wire_lut_L1_res/2' Cw='wire_lut_L1_cap/2'\n")
	spice_file.write("Xwire_lut_L1h n_3_2 n_3_3 wire Rw='wire_lut_L1_res/2' Cw='wire_lut_L1_cap/2'\n")
	spice_file.write("Xptran_lut_L1h n_gnd n_3_3 n_gnd n_gnd ptran Wn=ptran_lut_L1_nmos\n")
	spice_file.write("Xptran_lut_L2 n_3_2 n_4_1 n_b n_gnd ptran Wn=ptran_lut_L2_nmos\n")
	spice_file.write("Xwire_lut_L2 n_4_1 n_4_2 wire Rw='wire_lut_L2_res/2' Cw='wire_lut_L2_cap/2'\n")
	spice_file.write("Xwire_lut_L2h n_4_2 n_4_3 wire Rw='wire_lut_L2_res/2' Cw='wire_lut_L2_cap/2'\n")
	spice_file.write("Xptran_lut_L2h n_gnd n_4_3 n_gnd n_gnd ptran Wn=ptran_lut_L2_nmos\n")
	spice_file.write("Xptran_lut_L3 n_4_2 n_5_1 n_c n_gnd ptran Wn=ptran_lut_L3_nmos\n")
	spice_file.write("Xwire_lut_L3 n_5_1 n_5_2 wire Rw='wire_lut_L3_res/2' Cw='wire_lut_L3_cap/2'\n")
	spice_file.write("Xwire_lut_L3h n_5_2 n_5_3 wire Rw='wire_lut_L3_res/2' Cw='wire_lut_L3_cap/2'\n")
	spice_file.write("Xptran_lut_L3h n_gnd n_5_3 n_gnd n_gnd ptran Wn=ptran_lut_L3_nmos\n\n")

	spice_file.write("* Internal buffer \n")
	spice_file.write("Xrest_lut_int_buffer n_5_2 n_6_1 n_vdd n_gnd rest Wp=rest_lut_int_buffer_pmos\n")
	spice_file.write("Xinv_lut_int_buffer_1 n_5_2 n_6_1 n_vdd n_gnd inv Wn=inv_lut_int_buffer_1_nmos Wp=inv_lut_int_buffer_1_pmos\n")
	spice_file.write("Xwire_lut_int_buffer n_6_1 n_6_2 wire Rw=wire_lut_int_buffer_res Cw=wire_lut_int_buffer_cap\n")
	spice_file.write("Xinv_lut_int_buffer_2 n_6_2 n_7_1 n_vdd n_gnd inv Wn=inv_lut_int_buffer_2_nmos Wp=inv_lut_int_buffer_2_pmos\n")
	spice_file.write("Xwire_lut_int_buffer_out n_7_1 n_7_2 wire Rw=wire_lut_int_buffer_out_res Cw=wire_lut_int_buffer_out_cap\n\n")
	
	spice_file.write("* Second chain\n")
	spice_file.write("Xptran_lut_L4 n_7_2 n_8_1 n_d n_gnd ptran Wn=ptran_lut_L4_nmos\n")
	spice_file.write("Xwire_lut_L4 n_8_1 n_8_2 wire Rw='wire_lut_L4_res/2' Cw='wire_lut_L4_cap/2'\n")
	spice_file.write("Xwire_lut_L4h n_8_2 n_8_3 wire Rw='wire_lut_L4_res/2' Cw='wire_lut_L4_cap/2'\n")
	spice_file.write("Xptran_lut_L4h n_gnd n_8_3 n_gnd n_gnd ptran Wn=ptran_lut_L4_nmos\n")
	spice_file.write("Xptran_lut_L5 n_8_2 n_9_1 n_e n_gnd ptran Wn=ptran_lut_L5_nmos\n")
	spice_file.write("Xwire_lut_L5 n_9_1 n_9_2 wire Rw='wire_lut_L5_res/2' Cw='wire_lut_L5_cap/2'\n")
	spice_file.write("Xwire_lut_L5h n_9_2 n_9_3 wire Rw='wire_lut_L5_res/2' Cw='wire_lut_L5_cap/2'\n")
	spice_file.write("Xptran_lut_L5h n_gnd n_9_3 n_gnd n_gnd ptran Wn=ptran_lut_L5_nmos\n")
	spice_file.write("Xptran_lut_L6 n_9_2 n_10_1 n_f n_gnd ptran Wn=ptran_lut_L6_nmos\n")
	spice_file.write("Xwire_lut_L6 n_10_1 n_10_2 wire Rw='wire_lut_L6_res/2' Cw='wire_lut_L6_cap/2'\n")
	spice_file.write("Xwire_lut_L6h n_10_2 n_10_3 wire Rw='wire_lut_L6_res/2' Cw='wire_lut_L6_cap/2'\n")
	spice_file.write("Xptran_lut_L6h n_gnd n_10_3 n_gnd n_gnd ptran Wn=ptran_lut_L6_nmos\n\n")
	
	spice_file.write("* Output buffer \n")
	spice_file.write("Xrest_lut_out_buffer n_10_2 n_11_1 n_vdd n_gnd rest Wp=rest_lut_out_buffer_pmos\n")
	spice_file.write("Xinv_lut_out_buffer_1 n_10_2 n_11_1 n_vdd n_gnd inv Wn=inv_lut_out_buffer_1_nmos Wp=inv_lut_out_buffer_1_pmos\n")
	spice_file.write("Xwire_lut_out_buffer n_11_1 n_11_2 wire Rw=wire_lut_out_buffer_res Cw=wire_lut_out_buffer_cap\n")
	spice_file.write("Xinv_lut_out_buffer_2 n_11_2 n_out n_vdd n_gnd inv Wn=inv_lut_out_buffer_2_nmos Wp=inv_lut_out_buffer_2_pmos\n\n")
	spice_file.write(".ENDS\n\n\n")
	
	
	# Create a list of all transistors used in this subcircuit
	tran_names_list = []
	tran_names_list.append("inv_lut_0sram_driver_2_nmos")
	tran_names_list.append("inv_lut_0sram_driver_2_pmos")
	tran_names_list.append("ptran_lut_L1_nmos")
	tran_names_list.append("ptran_lut_L2_nmos")
	tran_names_list.append("ptran_lut_L3_nmos")
	tran_names_list.append("rest_lut_int_buffer_pmos")
	tran_names_list.append("inv_lut_int_buffer_1_nmos")
	tran_names_list.append("inv_lut_int_buffer_1_pmos")
	tran_names_list.append("inv_lut_int_buffer_2_nmos")
	tran_names_list.append("inv_lut_int_buffer_2_pmos")
	tran_names_list.append("ptran_lut_L4_nmos")
	tran_names_list.append("ptran_lut_L5_nmos")
	tran_names_list.append("ptran_lut_L6_nmos")
	tran_names_list.append("rest_lut_out_buffer_pmos")
	tran_names_list.append("inv_lut_out_buffer_1_nmos")
	tran_names_list.append("inv_lut_out_buffer_1_pmos")
	tran_names_list.append("inv_lut_out_buffer_2_nmos")
	tran_names_list.append("inv_lut_out_buffer_2_pmos")

	# Create a list of all wires used in this subcircuit
	wire_names_list = []
	wire_names_list.append("wire_lut_sram_driver")
	wire_names_list.append("wire_lut_sram_driver_out")
	wire_names_list.append("wire_lut_L1")
	wire_names_list.append("wire_lut_L2")
	wire_names_list.append("wire_lut_L3")
	wire_names_list.append("wire_lut_int_buffer")
	wire_names_list.append("wire_lut_int_buffer_out")
	wire_names_list.append("wire_lut_L4")
	wire_names_list.append("wire_lut_L5")
	wire_names_list.append("wire_lut_L6")
	wire_names_list.append("wire_lut_out_buffer")
	
	return tran_names_list, wire_names_list


def generate_ptran_lut5(spice_filename, min_tran_width, use_finfet):
	""" Generates a 5LUT SPICE deck """
	
	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')
	
	# Create the 5-LUT circuit
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* 5-LUT subcircuit \n")
	spice_file.write("******************************************************************************************\n")
	# We use a 6-LUT interface even if this is a 5-LUT. We just won't connect anything to "n_f".
	spice_file.write(".SUBCKT lut n_in n_out n_a n_b n_c n_d n_e n_f n_vdd n_gnd\n")
	Wn = min_tran_width
	Wp = 1.667*min_tran_width
	if not use_finfet:
		spice_file.write("Xinv_lut_sram_driver_1 n_in n_1_1 n_vdd n_gnd inv Wn=" + str(Wn) + "n Wp=" + str(Wp) + "n\n")
	else:
		spice_file.write("Xinv_lut_sram_driver_1 n_in n_1_1 n_vdd n_gnd inv Wn=1 Wp=1\n")

	spice_file.write("Xwire_lut_sram_driver n_1_1 n_1_2 wire Rw=wire_lut_sram_driver_res Cw=wire_lut_sram_driver_cap\n")
	spice_file.write("Xinv_lut_sram_driver_2 n_1_2 n_2_1 n_vdd n_gnd inv Wn=inv_lut_0sram_driver_2_nmos Wp=inv_lut_0sram_driver_2_pmos\n")
	spice_file.write("Xwire_lut_sram_driver_out n_2_1 n_2_2 wire Rw=wire_lut_sram_driver_out_res Cw=wire_lut_sram_driver_out_cap\n\n")
	
	spice_file.write("* First chain\n")
	spice_file.write("Xptran_lut_L1 n_2_2 n_3_1 n_a n_gnd ptran Wn=ptran_lut_L1_nmos\n")
	spice_file.write("Xwire_lut_L1 n_3_1 n_3_2 wire Rw='wire_lut_L1_res/2' Cw='wire_lut_L1_cap/2'\n")
	spice_file.write("Xwire_lut_L1h n_3_2 n_3_3 wire Rw='wire_lut_L1_res/2' Cw='wire_lut_L1_cap/2'\n")
	spice_file.write("Xptran_lut_L1h n_gnd n_3_3 n_gnd n_gnd ptran Wn=ptran_lut_L1_nmos\n")
	spice_file.write("Xptran_lut_L2 n_3_2 n_4_1 n_b n_gnd ptran Wn=ptran_lut_L2_nmos\n")
	spice_file.write("Xwire_lut_L2 n_4_1 n_4_2 wire Rw='wire_lut_L2_res/2' Cw='wire_lut_L2_cap/2'\n")
	spice_file.write("Xwire_lut_L2h n_4_2 n_4_3 wire Rw='wire_lut_L2_res/2' Cw='wire_lut_L2_cap/2'\n")
	spice_file.write("Xptran_lut_L2h n_gnd n_4_3 n_gnd n_gnd ptran Wn=ptran_lut_L2_nmos\n")
	spice_file.write("Xptran_lut_L3 n_4_2 n_5_1 n_c n_gnd ptran Wn=ptran_lut_L3_nmos\n")
	spice_file.write("Xwire_lut_L3 n_5_1 n_5_2 wire Rw='wire_lut_L3_res/2' Cw='wire_lut_L3_cap/2'\n")
	spice_file.write("Xwire_lut_L3h n_5_2 n_5_3 wire Rw='wire_lut_L3_res/2' Cw='wire_lut_L3_cap/2'\n")
	spice_file.write("Xptran_lut_L3h n_gnd n_5_3 n_gnd n_gnd ptran Wn=ptran_lut_L3_nmos\n\n")

	spice_file.write("* Internal buffer \n")
	spice_file.write("Xrest_lut_int_buffer n_5_2 n_6_1 n_vdd n_gnd rest Wp=rest_lut_int_buffer_pmos\n")
	spice_file.write("Xinv_lut_int_buffer_1 n_5_2 n_6_1 n_vdd n_gnd inv Wn=inv_lut_int_buffer_1_nmos Wp=inv_lut_int_buffer_1_pmos\n")
	spice_file.write("Xwire_lut_int_buffer n_6_1 n_6_2 wire Rw=wire_lut_int_buffer_res Cw=wire_lut_int_buffer_cap\n")
	spice_file.write("Xinv_lut_int_buffer_2 n_6_2 n_7_1 n_vdd n_gnd inv Wn=inv_lut_int_buffer_2_nmos Wp=inv_lut_int_buffer_2_pmos\n")
	spice_file.write("Xwire_lut_int_buffer_out n_7_1 n_7_2 wire Rw=wire_lut_int_buffer_out_res Cw=wire_lut_int_buffer_out_cap\n\n")
	
	spice_file.write("* Second chain\n")
	spice_file.write("Xptran_lut_L4 n_7_2 n_8_1 n_d n_gnd ptran Wn=ptran_lut_L4_nmos\n")
	spice_file.write("Xwire_lut_L4 n_8_1 n_8_2 wire Rw='wire_lut_L4_res/2' Cw='wire_lut_L4_cap/2'\n")
	spice_file.write("Xwire_lut_L4h n_8_2 n_8_3 wire Rw='wire_lut_L4_res/2' Cw='wire_lut_L4_cap/2'\n")
	spice_file.write("Xptran_lut_L4h n_gnd n_8_3 n_gnd n_gnd ptran Wn=ptran_lut_L4_nmos\n")
	spice_file.write("Xptran_lut_L5 n_8_2 n_9_1 n_e n_gnd ptran Wn=ptran_lut_L5_nmos\n")
	spice_file.write("Xwire_lut_L5 n_9_1 n_9_2 wire Rw='wire_lut_L5_res/2' Cw='wire_lut_L5_cap/2'\n")
	spice_file.write("Xwire_lut_L5h n_9_2 n_9_3 wire Rw='wire_lut_L5_res/2' Cw='wire_lut_L5_cap/2'\n")
	spice_file.write("Xptran_lut_L5h n_gnd n_9_3 n_gnd n_gnd ptran Wn=ptran_lut_L5_nmos\n")
	
	spice_file.write("* Output buffer \n")
	spice_file.write("Xrest_lut_out_buffer n_9_2 n_11_1 n_vdd n_gnd rest Wp=rest_lut_out_buffer_pmos\n")
	spice_file.write("Xinv_lut_out_buffer_1 n_9_2 n_11_1 n_vdd n_gnd inv Wn=inv_lut_out_buffer_1_nmos Wp=inv_lut_out_buffer_1_pmos\n")
	spice_file.write("Xwire_lut_out_buffer n_11_1 n_11_2 wire Rw=wire_lut_out_buffer_res Cw=wire_lut_out_buffer_cap\n")
	spice_file.write("Xinv_lut_out_buffer_2 n_11_2 n_out n_vdd n_gnd inv Wn=inv_lut_out_buffer_2_nmos Wp=inv_lut_out_buffer_2_pmos\n\n")
	spice_file.write(".ENDS\n\n\n")
	
	
	# Create a list of all transistors used in this subcircuit
	tran_names_list = []
	tran_names_list.append("inv_lut_0sram_driver_2_nmos")
	tran_names_list.append("inv_lut_0sram_driver_2_pmos")
	tran_names_list.append("ptran_lut_L1_nmos")
	tran_names_list.append("ptran_lut_L2_nmos")
	tran_names_list.append("ptran_lut_L3_nmos")
	tran_names_list.append("rest_lut_int_buffer_pmos")
	tran_names_list.append("inv_lut_int_buffer_1_nmos")
	tran_names_list.append("inv_lut_int_buffer_1_pmos")
	tran_names_list.append("inv_lut_int_buffer_2_nmos")
	tran_names_list.append("inv_lut_int_buffer_2_pmos")
	tran_names_list.append("ptran_lut_L4_nmos")
	tran_names_list.append("ptran_lut_L5_nmos")
	tran_names_list.append("rest_lut_out_buffer_pmos")
	tran_names_list.append("inv_lut_out_buffer_1_nmos")
	tran_names_list.append("inv_lut_out_buffer_1_pmos")
	tran_names_list.append("inv_lut_out_buffer_2_nmos")
	tran_names_list.append("inv_lut_out_buffer_2_pmos")

	# Create a list of all wires used in this subcircuit
	wire_names_list = []
	wire_names_list.append("wire_lut_sram_driver")
	wire_names_list.append("wire_lut_sram_driver_out")
	wire_names_list.append("wire_lut_L1")
	wire_names_list.append("wire_lut_L2")
	wire_names_list.append("wire_lut_L3")
	wire_names_list.append("wire_lut_int_buffer")
	wire_names_list.append("wire_lut_int_buffer_out")
	wire_names_list.append("wire_lut_L4")
	wire_names_list.append("wire_lut_L5")
	wire_names_list.append("wire_lut_out_buffer")
	
	return tran_names_list, wire_names_list

	
def generate_ptran_lut4(spice_filename, min_tran_width, use_finfet):
	""" Generates a 4LUT SPICE deck """
	
	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')
	
	# Create the 4-LUT circuit
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* 4-LUT subcircuit \n")
	spice_file.write("******************************************************************************************\n")
	# We use a 6-LUT interface even if this is a 4-LUT. We just won't connect anything to "n_e" and "n_f".
	spice_file.write(".SUBCKT lut n_in n_out n_a n_b n_c n_d n_e n_f n_vdd n_gnd\n")
	Wn = min_tran_width
	Wp = 1.667*min_tran_width
	if not use_finfet:
		spice_file.write("Xinv_lut_sram_driver_1 n_in n_1_1 n_vdd n_gnd inv Wn=" + str(Wn) + "n Wp=" + str(Wp) + "n\n")
	else:
		spice_file.write("Xinv_lut_sram_driver_1 n_in n_1_1 n_vdd n_gnd inv Wn=1 Wp=1\n")

	spice_file.write("Xwire_lut_sram_driver n_1_1 n_1_2 wire Rw=wire_lut_sram_driver_res Cw=wire_lut_sram_driver_cap\n")
	spice_file.write("Xinv_lut_sram_driver_2 n_1_2 n_2_1 n_vdd n_gnd inv Wn=inv_lut_0sram_driver_2_nmos Wp=inv_lut_0sram_driver_2_pmos\n")
	spice_file.write("Xwire_lut_sram_driver_out n_2_1 n_2_2 wire Rw=wire_lut_sram_driver_out_res Cw=wire_lut_sram_driver_out_cap\n\n")
	
	spice_file.write("* First chain\n")
	spice_file.write("Xptran_lut_L1 n_2_2 n_3_1 n_a n_gnd ptran Wn=ptran_lut_L1_nmos\n")
	spice_file.write("Xwire_lut_L1 n_3_1 n_3_2 wire Rw='wire_lut_L1_res/2' Cw='wire_lut_L1_cap/2'\n")
	spice_file.write("Xwire_lut_L1h n_3_2 n_3_3 wire Rw='wire_lut_L1_res/2' Cw='wire_lut_L1_cap/2'\n")
	spice_file.write("Xptran_lut_L1h n_gnd n_3_3 n_gnd n_gnd ptran Wn=ptran_lut_L1_nmos\n")
	spice_file.write("Xptran_lut_L2 n_3_2 n_4_1 n_b n_gnd ptran Wn=ptran_lut_L2_nmos\n")
	spice_file.write("Xwire_lut_L2 n_4_1 n_4_2 wire Rw='wire_lut_L2_res/2' Cw='wire_lut_L2_cap/2'\n")
	spice_file.write("Xwire_lut_L2h n_4_2 n_4_3 wire Rw='wire_lut_L2_res/2' Cw='wire_lut_L2_cap/2'\n")
	spice_file.write("Xptran_lut_L2h n_gnd n_4_3 n_gnd n_gnd ptran Wn=ptran_lut_L2_nmos\n\n")
	
	spice_file.write("* Internal buffer \n")
	spice_file.write("Xrest_lut_int_buffer n_4_2 n_5_1 n_vdd n_gnd rest Wp=rest_lut_int_buffer_pmos\n")
	spice_file.write("Xinv_lut_int_buffer_1 n_4_2 n_5_1 n_vdd n_gnd inv Wn=inv_lut_int_buffer_1_nmos Wp=inv_lut_int_buffer_1_pmos\n")
	spice_file.write("Xwire_lut_int_buffer n_5_1 n_5_2 wire Rw=wire_lut_int_buffer_res Cw=wire_lut_int_buffer_cap\n")
	spice_file.write("Xinv_lut_int_buffer_2 n_5_2 n_6_1 n_vdd n_gnd inv Wn=inv_lut_int_buffer_2_nmos Wp=inv_lut_int_buffer_2_pmos\n")
	spice_file.write("Xwire_lut_int_buffer_out n_6_1 n_6_2 wire Rw=wire_lut_int_buffer_out_res Cw=wire_lut_int_buffer_out_cap\n\n")
	
	spice_file.write("* Second chain\n")
	spice_file.write("Xptran_lut_L3 n_6_2 n_7_1 n_c n_gnd ptran Wn=ptran_lut_L3_nmos\n")
	spice_file.write("Xwire_lut_L3 n_7_1 n_7_2 wire Rw='wire_lut_L3_res/2' Cw='wire_lut_L3_cap/2'\n")
	spice_file.write("Xwire_lut_L3h n_7_2 n_7_3 wire Rw='wire_lut_L3_res/2' Cw='wire_lut_L3_cap/2'\n")
	spice_file.write("Xptran_lut_L3h n_gnd n_7_3 n_gnd n_gnd ptran Wn=ptran_lut_L3_nmos\n")
	spice_file.write("Xptran_lut_L4 n_7_2 n_8_1 n_d n_gnd ptran Wn=ptran_lut_L4_nmos\n")
	spice_file.write("Xwire_lut_L4 n_8_1 n_8_2 wire Rw='wire_lut_L4_res/2' Cw='wire_lut_L4_cap/2'\n")
	spice_file.write("Xwire_lut_L4h n_8_2 n_8_3 wire Rw='wire_lut_L4_res/2' Cw='wire_lut_L4_cap/2'\n")
	spice_file.write("Xptran_lut_L4h n_gnd n_8_3 n_gnd n_gnd ptran Wn=ptran_lut_L4_nmos\n\n")
	
	spice_file.write("* Output buffer \n")
	spice_file.write("Xrest_lut_out_buffer n_8_2 n_9_1 n_vdd n_gnd rest Wp=rest_lut_out_buffer_pmos\n")
	spice_file.write("Xinv_lut_out_buffer_1 n_8_2 n_9_1 n_vdd n_gnd inv Wn=inv_lut_out_buffer_1_nmos Wp=inv_lut_out_buffer_1_pmos\n")
	spice_file.write("Xwire_lut_out_buffer n_9_1 n_9_2 wire Rw=wire_lut_out_buffer_res Cw=wire_lut_out_buffer_cap\n")
	spice_file.write("Xinv_lut_out_buffer_2 n_9_2 n_out n_vdd n_gnd inv Wn=inv_lut_out_buffer_2_nmos Wp=inv_lut_out_buffer_2_pmos\n\n")
	spice_file.write(".ENDS\n\n\n")
	
	
	# Create a list of all transistors used in this subcircuit
	tran_names_list = []
	tran_names_list.append("inv_lut_0sram_driver_2_nmos")
	tran_names_list.append("inv_lut_0sram_driver_2_pmos")
	tran_names_list.append("ptran_lut_L1_nmos")
	tran_names_list.append("ptran_lut_L2_nmos")
	tran_names_list.append("rest_lut_int_buffer_pmos")
	tran_names_list.append("inv_lut_int_buffer_1_nmos")
	tran_names_list.append("inv_lut_int_buffer_1_pmos")
	tran_names_list.append("inv_lut_int_buffer_2_nmos")
	tran_names_list.append("inv_lut_int_buffer_2_pmos")
	tran_names_list.append("ptran_lut_L3_nmos")
	tran_names_list.append("ptran_lut_L4_nmos")
	tran_names_list.append("rest_lut_out_buffer_pmos")
	tran_names_list.append("inv_lut_out_buffer_1_nmos")
	tran_names_list.append("inv_lut_out_buffer_1_pmos")
	tran_names_list.append("inv_lut_out_buffer_2_nmos")
	tran_names_list.append("inv_lut_out_buffer_2_pmos")

	# Create a list of all wires used in this subcircuit
	wire_names_list = []
	wire_names_list.append("wire_lut_sram_driver")
	wire_names_list.append("wire_lut_sram_driver_out")
	wire_names_list.append("wire_lut_L1")
	wire_names_list.append("wire_lut_L2")
	wire_names_list.append("wire_lut_int_buffer")
	wire_names_list.append("wire_lut_int_buffer_out")
	wire_names_list.append("wire_lut_L3")
	wire_names_list.append("wire_lut_L4")
	wire_names_list.append("wire_lut_out_buffer")
	
	return tran_names_list, wire_names_list
	

def generate_ptran_lut_driver(spice_filename, lut_input_name, lut_input_type):
	""" Generate a pass-transistor LUT driver based on type. """
	
	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')
	  
	# Create the LUT-input circuit header (same interface for all LUT input types)
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* LUT " + lut_input_name + " subcircuit \n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT " + lut_input_name + " n_in n_out n_gate n_gate_n n_rsel n_not_input n_vdd n_gnd\n")
	
	# The next element is the input driver.
	# We only need an input driver if this is not a "default" input.
	if lut_input_type != "default":
		spice_file.write("Xinv_" + lut_input_name + "_0 n_in n_1_1 n_vdd n_gnd inv Wn=inv_" + lut_input_name + "_0_nmos Wp=inv_" + lut_input_name + "_0_pmos\n")
		# If the LUT input is connected to register select, we add a wire and connect it to the rsel node.
		if lut_input_type == "default_rsel" or lut_input_type == "reg_fb_rsel":
			spice_file.write("Xwire_" + lut_input_name + "_0_rsel n_1_1 n_rsel wire Rw=wire_" + lut_input_name + "_0_rsel_res Cw=wire_" + lut_input_name + "_0_rsel_cap\n")
		# Next is the wire connecting the input inverter to either the output buffer (for "default_rsel")
		# or the pass-transistor (for both "reg_fb" and "reg_fb_rsel"). 
		spice_file.write("Xwire_" + lut_input_name + "_0_out n_1_1 n_1_2 wire Rw=wire_" + lut_input_name + "_0_out_res Cw=wire_" + lut_input_name + "_0_out_cap\n")
		# Now we add a sense inverter for "default_rsel" or the ptran level-restorer and sense inv in the case of both "reg_fb"
		if lut_input_type == "default_rsel":
			spice_file.write("Xinv_" + lut_input_name + "_1 n_1_2 n_3_1 n_vdd n_gnd inv Wn=inv_" + lut_input_name + "_1_nmos Wp=inv_" + lut_input_name + "_1_pmos\n")
		else:
			spice_file.write("Xptran_" + lut_input_name + "_0 n_1_2 n_2_1 n_gate n_gnd ptran Wn=ptran_" + lut_input_name + "_0_nmos\n")
			spice_file.write("Xwire_" + lut_input_name + "_0 n_2_1 n_2_2 wire Rw='wire_" + lut_input_name + "_0_res/2' Cw='wire_" + lut_input_name + "_0_cap/2'\n")
			spice_file.write("Xwire_" + lut_input_name + "_0h n_2_2 n_2_3 wire Rw='wire_" + lut_input_name + "_0_res/2' Cw='wire_" + lut_input_name + "_0_cap/2'\n")
			spice_file.write("Xptran_" + lut_input_name + "_0h n_gnd n_2_3 n_gate_n n_gnd ptran Wn=ptran_" + lut_input_name + "_0_nmos\n")
			spice_file.write("Xrest_" + lut_input_name + " n_2_2 n_3_1 n_vdd n_gnd rest Wp=rest_" + lut_input_name + "_pmos\n")
			spice_file.write("Xinv_" + lut_input_name + "_1 n_2_2 n_3_1 n_vdd n_gnd inv Wn=inv_" + lut_input_name + "_1_nmos Wp=inv_" + lut_input_name + "_1_pmos\n")
		# Now we add the wire that connects the sense inverter to the driving inverter
		spice_file.write("Xwire_" + lut_input_name + " n_3_1 n_not_input wire Rw=wire_" + lut_input_name + "_res Cw=wire_" + lut_input_name + "_cap\n")
		# Finally, the driving inverter
		spice_file.write("Xinv_" + lut_input_name + "_2 n_not_input n_out n_vdd n_gnd inv Wn=inv_" + lut_input_name + "_2_nmos Wp=inv_" + lut_input_name + "_2_pmos\n")
	# If this is a default input, all we need is a wire and a driver. But, we are careful to use the same names for corresponding nodes. 
	# This is convenient for writing the top-level SPICE file.   
	else:
		# Add the wire that connects the local mux to the driver
		spice_file.write("Xwire_" + lut_input_name + " n_in n_not_input wire Rw=wire_" + lut_input_name + "_res Cw=wire_" + lut_input_name + "_cap\n")
		# Add the driving inverter
		spice_file.write("Xinv_" + lut_input_name + "_2 n_not_input n_out n_vdd n_gnd inv Wn=inv_" + lut_input_name + "_2_nmos Wp=inv_" + lut_input_name + "_2_pmos\n")
		
	# End the subcircuit    
	spice_file.write(".ENDS\n\n\n")
	
	
	# Create a list of all transistors used in this subcircuit
	tran_names_list = []
	if lut_input_type != "default":
		tran_names_list.append("inv_" + lut_input_name + "_0_nmos")
		tran_names_list.append("inv_" + lut_input_name + "_0_pmos")
	if lut_input_type == "reg_fb" or lut_input_type == "reg_fb_rsel":
		tran_names_list.append("ptran_" + lut_input_name + "_0_nmos")
		tran_names_list.append("rest_" + lut_input_name + "_pmos")
	if lut_input_type != "default":
		tran_names_list.append("inv_" + lut_input_name + "_1_nmos")
		tran_names_list.append("inv_" + lut_input_name + "_1_pmos")
	tran_names_list.append("inv_" + lut_input_name + "_2_nmos")
	tran_names_list.append("inv_" + lut_input_name + "_2_pmos")
	
	
	# Create a list of all wires used in this subcircuit
	wire_names_list = []
	if lut_input_type == "default_rsel" or lut_input_type == "reg_fb_rsel":
		wire_names_list.append("wire_" + lut_input_name + "_0_rsel")
	if lut_input_type != "default":
		wire_names_list.append("wire_" + lut_input_name + "_0_out")
	if lut_input_type == "reg_fb" or lut_input_type == "reg_fb_rsel":
		wire_names_list.append("wire_" + lut_input_name + "_0")
	wire_names_list.append("wire_" + lut_input_name)
	
	return tran_names_list, wire_names_list
 

def generate_ptran_lut_not_driver(spice_filename, lut_input_name):
	""" Generate a pass-transistor LUT driver based on type. """

	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')
	  
	# Create the LUT-input circuit
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* LUT " + lut_input_name + " subcircuit \n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT " + lut_input_name + " n_in n_out n_vdd n_gnd\n")
	spice_file.write("Xinv_" + lut_input_name + "_1 n_in n_1_1 n_vdd n_gnd inv Wn=inv_" + lut_input_name + "_1_nmos Wp=inv_" + lut_input_name + "_1_pmos\n")
	spice_file.write("Xwire_" + lut_input_name + " n_1_1 n_1_2 wire Rw=wire_" + lut_input_name + "_res Cw=wire_" + lut_input_name + "_cap\n")
	spice_file.write("Xinv_" + lut_input_name + "_2 n_1_2 n_out n_vdd n_gnd inv Wn=inv_" + lut_input_name + "_2_nmos Wp=inv_" + lut_input_name + "_2_pmos\n")
	spice_file.write(".ENDS\n\n\n")
	
	
	# Create a list of all transistors used in this subcircuit
	tran_names_list = []
	tran_names_list.append("inv_" + lut_input_name + "_1_nmos")
	tran_names_list.append("inv_" + lut_input_name + "_1_pmos")
	tran_names_list.append("inv_" + lut_input_name + "_2_nmos")
	tran_names_list.append("inv_" + lut_input_name + "_2_pmos")
	
	
	# Create a list of all wires used in this subcircuit
	wire_names_list = []
	wire_names_list.append("wire_" + lut_input_name)
	
	return tran_names_list, wire_names_list
   
   
def generate_ptran_lut_driver_load(spice_filename, lut_input_name, K, use_fluts):
	""" Generates LUT input load SPICE deck 
		Note: the input K incase of fluts is still input comming from the architecure file.
		For a 5-FLUT K = 5"""
	
	#TODO: how come the number of loading transistors doesn't depend 
	# on whether this is an independent input of not

	# Calculate number of pass-transistors loading this input
	max_num_ptran = math.pow(2, K)
	if lut_input_name == "a":
		num_ptran_load = int(max_num_ptran/2)
		ptran_level = "L1"
	elif lut_input_name == "b":
		num_ptran_load = int(max_num_ptran/4)
		ptran_level = "L2"
	elif lut_input_name == "c":
		num_ptran_load = int(max_num_ptran/8)
		ptran_level = "L3"
	elif lut_input_name == "d":
		num_ptran_load = int(max_num_ptran/16)
		ptran_level = "L4"
	elif lut_input_name == "e":
		num_ptran_load = int(max_num_ptran/32)
		ptran_level = "L5"
	elif lut_input_name == "f":
		num_ptran_load = int(max_num_ptran/64)
		ptran_level = "L6"
	
	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')
	
	# Create the input load circuit
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* LUT " + lut_input_name + "-input load subcircuit \n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT lut_" + lut_input_name + "_driver_load n_1 n_vdd n_gnd\n")
	for ptran in range(num_ptran_load):
		ptran += 1
		spice_file.write("Xwire_lut_" + lut_input_name + "_driver_load_" + str(ptran) + " n_" + str(ptran) + " n_" + str(ptran+1) + " wire Rw='wire_lut_" + lut_input_name + "_driver_load_res/" + str(num_ptran_load) + "' Cw='wire_lut_" + lut_input_name + "_driver_load_cap/" + str(num_ptran_load) + "'\n")
		if use_fluts and num_ptran_load == 1:
			spice_file.write("Xptran_lut_" + lut_input_name + "_driver_load_" + str(ptran) + " n_gnd n_gnd n_" + str(ptran+1) + " n_gnd ptran Wn=ptran_flut_mux_nmos\n") 
		else:
			spice_file.write("Xptran_lut_" + lut_input_name + "_driver_load_" + str(ptran) + " n_gnd n_gnd n_" + str(ptran+1) + " n_gnd ptran Wn=ptran_lut_" + ptran_level + "_nmos\n") 
	spice_file.write(".ENDS\n\n\n")
	
	# Create a list of all wires used in this subcircuit
	wire_names_list = []
	wire_names_list.append("wire_lut_" + lut_input_name + "_driver_load")
	
	return wire_names_list


def generate_tgate_lut6(spice_filename, min_tran_width, use_finfet):
	""" Generates a 6LUT SPICE deck """
	
	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')
	
	# Create the 6-LUT circuit
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* 6-LUT subcircuit \n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT lut n_in n_out n_a n_a_n n_b n_b_n n_c n_c_n n_d n_d_n n_e n_e_n n_f n_f_n n_vdd n_gnd\n")
	Wn = min_tran_width
	Wp = 1.667*min_tran_width
	
	if not use_finfet :
		spice_file.write("Xinv_lut_sram_driver_1 n_in n_1_1 n_vdd n_gnd inv Wn=" + str(Wn) + "n Wp=" + str(Wp) + "n\n")
	else:
		spice_file.write("Xinv_lut_sram_driver_1 n_in n_1_1 n_vdd n_gnd inv Wn=1 Wp=2 \n")

	spice_file.write("Xwire_lut_sram_driver n_1_1 n_1_2 wire Rw=wire_lut_sram_driver_res Cw=wire_lut_sram_driver_cap\n")
	spice_file.write("Xinv_lut_sram_driver_2 n_1_2 n_2_1 n_vdd n_gnd inv Wn=inv_lut_0sram_driver_2_nmos Wp=inv_lut_0sram_driver_2_pmos\n")
	spice_file.write("Xwire_lut_sram_driver_out n_2_1 n_2_2 wire Rw=wire_lut_sram_driver_out_res Cw=wire_lut_sram_driver_out_cap\n\n")
	
	spice_file.write("* First chain\n")
	spice_file.write("Xtgate_lut_L1 n_2_2 n_3_1 n_a n_a_n n_vdd n_gnd tgate Wn=tgate_lut_L1_nmos Wp=tgate_lut_L1_pmos\n")
	spice_file.write("Xwire_lut_L1 n_3_1 n_3_2 wire Rw='wire_lut_L1_res/2' Cw='wire_lut_L1_cap/2'\n")
	spice_file.write("Xwire_lut_L1h n_3_2 n_3_3 wire Rw='wire_lut_L1_res/2' Cw='wire_lut_L1_cap/2'\n")
	spice_file.write("Xtgate_lut_L1h n_gnd n_3_3 n_gnd n_vdd n_vdd n_gnd tgate Wn=tgate_lut_L1_nmos Wp=tgate_lut_L1_pmos\n")
	spice_file.write("Xtgate_lut_L2 n_3_2 n_4_1 n_b n_b_n n_vdd n_gnd tgate Wn=tgate_lut_L2_nmos Wp=tgate_lut_L2_pmos\n")
	spice_file.write("Xwire_lut_L2 n_4_1 n_4_2 wire Rw='wire_lut_L2_res/2' Cw='wire_lut_L2_cap/2'\n")
	spice_file.write("Xwire_lut_L2h n_4_2 n_4_3 wire Rw='wire_lut_L2_res/2' Cw='wire_lut_L2_cap/2'\n")
	spice_file.write("Xtgate_lut_L2h n_gnd n_4_3 n_gnd n_vdd n_vdd n_gnd tgate Wn=tgate_lut_L2_nmos Wp=tgate_lut_L2_pmos\n")
	spice_file.write("Xtgate_lut_L3 n_4_2 n_5_1 n_c n_c_n n_vdd n_gnd tgate Wn=tgate_lut_L3_nmos Wp=tgate_lut_L3_pmos\n")
	spice_file.write("Xwire_lut_L3 n_5_1 n_5_2 wire Rw='wire_lut_L3_res/2' Cw='wire_lut_L3_cap/2'\n")
	spice_file.write("Xwire_lut_L3h n_5_2 n_5_3 wire Rw='wire_lut_L3_res/2' Cw='wire_lut_L3_cap/2'\n")
	spice_file.write("Xtgate_lut_L3h n_gnd n_5_3 n_gnd n_vdd n_vdd n_gnd tgate Wn=tgate_lut_L3_nmos Wp=tgate_lut_L3_pmos\n\n")

	spice_file.write("* Internal buffer \n")
	# spice_file.write("Xrest_lut_int_buffer n_5_2 n_6_1 n_vdd n_gnd rest Wp=rest_lut_int_buffer_pmos\n")
	spice_file.write("Xinv_lut_int_buffer_1 n_5_2 n_6_1 n_vdd n_gnd inv Wn=inv_lut_int_buffer_1_nmos Wp=inv_lut_int_buffer_1_pmos\n")
	spice_file.write("Xwire_lut_int_buffer n_6_1 n_6_2 wire Rw=wire_lut_int_buffer_res Cw=wire_lut_int_buffer_cap\n")
	spice_file.write("Xinv_lut_int_buffer_2 n_6_2 n_7_1 n_vdd n_gnd inv Wn=inv_lut_int_buffer_2_nmos Wp=inv_lut_int_buffer_2_pmos\n")
	spice_file.write("Xwire_lut_int_buffer_out n_7_1 n_7_2 wire Rw=wire_lut_int_buffer_out_res Cw=wire_lut_int_buffer_out_cap\n\n")
	
	spice_file.write("* Second chain\n")
	spice_file.write("Xtgate_lut_L4 n_7_2 n_8_1 n_d n_d_n n_vdd n_gnd tgate Wn=tgate_lut_L4_nmos Wp=tgate_lut_L4_pmos\n")
	spice_file.write("Xwire_lut_L4 n_8_1 n_8_2 wire Rw='wire_lut_L4_res/2' Cw='wire_lut_L4_cap/2'\n")
	spice_file.write("Xwire_lut_L4h n_8_2 n_8_3 wire Rw='wire_lut_L4_res/2' Cw='wire_lut_L4_cap/2'\n")
	spice_file.write("Xtgate_lut_L4h n_gnd n_8_3 n_gnd n_vdd n_vdd n_gnd tgate Wn=tgate_lut_L4_nmos Wp=tgate_lut_L4_pmos\n")
	spice_file.write("Xtgate_lut_L5 n_8_2 n_9_1 n_e n_e_n n_vdd n_gnd tgate Wn=tgate_lut_L5_nmos Wp=tgate_lut_L5_pmos\n")
	spice_file.write("Xwire_lut_L5 n_9_1 n_9_2 wire Rw='wire_lut_L5_res/2' Cw='wire_lut_L5_cap/2'\n")
	spice_file.write("Xwire_lut_L5h n_9_2 n_9_3 wire Rw='wire_lut_L5_res/2' Cw='wire_lut_L5_cap/2'\n")
	spice_file.write("Xtgate_lut_L5h n_gnd n_9_3 n_gnd n_vdd n_vdd n_gnd tgate Wn=tgate_lut_L5_nmos Wp=tgate_lut_L5_pmos\n")
	spice_file.write("Xtgate_lut_L6 n_9_2 n_10_1 n_f n_f_n n_vdd n_gnd tgate Wn=tgate_lut_L6_nmos Wp=tgate_lut_L6_pmos\n")
	spice_file.write("Xwire_lut_L6 n_10_1 n_10_2 wire Rw='wire_lut_L6_res/2' Cw='wire_lut_L6_cap/2'\n")
	spice_file.write("Xwire_lut_L6h n_10_2 n_10_3 wire Rw='wire_lut_L6_res/2' Cw='wire_lut_L6_cap/2'\n")
	spice_file.write("Xtgate_lut_L6h n_gnd n_10_3 n_gnd n_vdd n_vdd n_gnd tgate Wn=tgate_lut_L6_nmos Wp=tgate_lut_L6_pmos\n\n")
	
	spice_file.write("* Output buffer \n")
	# spice_file.write("Xrest_lut_out_buffer n_10_2 n_11_1 n_vdd n_gnd rest Wp=rest_lut_out_buffer_pmos\n")
	spice_file.write("Xinv_lut_out_buffer_1 n_10_2 n_11_1 n_vdd n_gnd inv Wn=inv_lut_out_buffer_1_nmos Wp=inv_lut_out_buffer_1_pmos\n")
	spice_file.write("Xwire_lut_out_buffer n_11_1 n_11_2 wire Rw=wire_lut_out_buffer_res Cw=wire_lut_out_buffer_cap\n")
	spice_file.write("Xinv_lut_out_buffer_2 n_11_2 n_out n_vdd n_gnd inv Wn=inv_lut_out_buffer_2_nmos Wp=inv_lut_out_buffer_2_pmos\n\n")
	spice_file.write(".ENDS\n\n\n")
	
	
	# Create a list of all transistors used in this subcircuit
	tran_names_list = []
	tran_names_list.append("inv_lut_0sram_driver_2_nmos")
	tran_names_list.append("inv_lut_0sram_driver_2_pmos")
	tran_names_list.append("tgate_lut_L1_nmos")
	tran_names_list.append("tgate_lut_L1_pmos")
	tran_names_list.append("tgate_lut_L2_nmos")
	tran_names_list.append("tgate_lut_L2_pmos")
	tran_names_list.append("tgate_lut_L3_nmos")
	tran_names_list.append("tgate_lut_L3_pmos")
	# tran_names_list.append("rest_lut_int_buffer_pmos")
	tran_names_list.append("inv_lut_int_buffer_1_nmos")
	tran_names_list.append("inv_lut_int_buffer_1_pmos")
	tran_names_list.append("inv_lut_int_buffer_2_nmos")
	tran_names_list.append("inv_lut_int_buffer_2_pmos")
	tran_names_list.append("tgate_lut_L4_nmos")
	tran_names_list.append("tgate_lut_L4_pmos")
	tran_names_list.append("tgate_lut_L5_nmos")
	tran_names_list.append("tgate_lut_L5_pmos")
	tran_names_list.append("tgate_lut_L6_nmos")
	tran_names_list.append("tgate_lut_L6_pmos")
	# tran_names_list.append("rest_lut_out_buffer_pmos")
	tran_names_list.append("inv_lut_out_buffer_1_nmos")
	tran_names_list.append("inv_lut_out_buffer_1_pmos")
	tran_names_list.append("inv_lut_out_buffer_2_nmos")
	tran_names_list.append("inv_lut_out_buffer_2_pmos")

	# Create a list of all wires used in this subcircuit
	wire_names_list = []
	wire_names_list.append("wire_lut_sram_driver")
	wire_names_list.append("wire_lut_sram_driver_out")
	wire_names_list.append("wire_lut_L1")
	wire_names_list.append("wire_lut_L2")
	wire_names_list.append("wire_lut_L3")
	wire_names_list.append("wire_lut_int_buffer")
	wire_names_list.append("wire_lut_int_buffer_out")
	wire_names_list.append("wire_lut_L4")
	wire_names_list.append("wire_lut_L5")
	wire_names_list.append("wire_lut_L6")
	wire_names_list.append("wire_lut_out_buffer")
	
	return tran_names_list, wire_names_list


def generate_tgate_lut5(spice_filename, min_tran_width, use_finfet):
	""" Generates a 5LUT SPICE deck """
	
	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')
	
	# Create the 5-LUT circuit
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* 5-LUT subcircuit \n")
	spice_file.write("******************************************************************************************\n")
	# We use a 6-LUT interface even if this is a 5-LUT. We just won't connect anything to "n_f".
	spice_file.write(".SUBCKT lut n_in n_out n_a n_a_n n_b n_b_n n_c n_c_n n_d n_d_n n_e n_e_n n_f n_f_n n_vdd n_gnd\n")
	Wn = min_tran_width
	Wp = 1.667*min_tran_width
	if not use_finfet :
		spice_file.write("Xinv_lut_sram_driver_1 n_in n_1_1 n_vdd n_gnd inv Wn=" + str(Wn) + "n Wp=" + str(Wp) + "n\n")
	else:
		spice_file.write("Xinv_lut_sram_driver_1 n_in n_1_1 n_vdd n_gnd inv Wn=1 Wp=2 \n")

	spice_file.write("Xwire_lut_sram_driver n_1_1 n_1_2 wire Rw=wire_lut_sram_driver_res Cw=wire_lut_sram_driver_cap\n")
	spice_file.write("Xinv_lut_sram_driver_2 n_1_2 n_2_1 n_vdd n_gnd inv Wn=inv_lut_0sram_driver_2_nmos Wp=inv_lut_0sram_driver_2_pmos\n")
	spice_file.write("Xwire_lut_sram_driver_out n_2_1 n_2_2 wire Rw=wire_lut_sram_driver_out_res Cw=wire_lut_sram_driver_out_cap\n\n")
	
	spice_file.write("* First chain\n")
	spice_file.write("Xtgate_lut_L1 n_2_2 n_3_1 n_a n_a_n n_vdd n_gnd tgate Wn=tgate_lut_L1_nmos Wp=tgate_lut_L1_pmos\n")
	spice_file.write("Xwire_lut_L1 n_3_1 n_3_2 wire Rw='wire_lut_L1_res/2' Cw='wire_lut_L1_cap/2'\n")
	spice_file.write("Xwire_lut_L1h n_3_2 n_3_3 wire Rw='wire_lut_L1_res/2' Cw='wire_lut_L1_cap/2'\n")
	spice_file.write("Xtgate_lut_L1h n_gnd n_3_3 n_gnd n_vdd n_vdd n_gnd tgate Wn=tgate_lut_L1_nmos Wp=tgate_lut_L1_pmos\n")
	spice_file.write("Xtgate_lut_L2 n_3_2 n_4_1 n_b n_b_n n_vdd n_gnd tgate Wn=tgate_lut_L2_nmos Wp=tgate_lut_L2_pmos\n")
	spice_file.write("Xwire_lut_L2 n_4_1 n_4_2 wire Rw='wire_lut_L2_res/2' Cw='wire_lut_L2_cap/2'\n")
	spice_file.write("Xwire_lut_L2h n_4_2 n_4_3 wire Rw='wire_lut_L2_res/2' Cw='wire_lut_L2_cap/2'\n")
	spice_file.write("Xtgate_lut_L2h n_gnd n_4_3 n_gnd n_vdd n_vdd n_gnd tgate Wn=tgate_lut_L2_nmos Wp=tgate_lut_L2_pmos\n")
	spice_file.write("Xtgate_lut_L3 n_4_2 n_5_1 n_c n_c_n n_vdd n_gnd tgate Wn=tgate_lut_L3_nmos Wp=tgate_lut_L3_pmos\n")
	spice_file.write("Xwire_lut_L3 n_5_1 n_5_2 wire Rw='wire_lut_L3_res/2' Cw='wire_lut_L3_cap/2'\n")
	spice_file.write("Xwire_lut_L3h n_5_2 n_5_3 wire Rw='wire_lut_L3_res/2' Cw='wire_lut_L3_cap/2'\n")
	spice_file.write("Xtgate_lut_L3h n_gnd n_5_3 n_gnd n_vdd n_vdd n_gnd tgate Wn=tgate_lut_L3_nmos Wp=tgate_lut_L3_pmos\n\n")

	spice_file.write("* Internal buffer \n")
	# spice_file.write("Xrest_lut_int_buffer n_5_2 n_6_1 n_vdd n_gnd rest Wp=rest_lut_int_buffer_pmos\n")
	spice_file.write("Xinv_lut_int_buffer_1 n_5_2 n_6_1 n_vdd n_gnd inv Wn=inv_lut_int_buffer_1_nmos Wp=inv_lut_int_buffer_1_pmos\n")
	spice_file.write("Xwire_lut_int_buffer n_6_1 n_6_2 wire Rw=wire_lut_int_buffer_res Cw=wire_lut_int_buffer_cap\n")
	spice_file.write("Xinv_lut_int_buffer_2 n_6_2 n_7_1 n_vdd n_gnd inv Wn=inv_lut_int_buffer_2_nmos Wp=inv_lut_int_buffer_2_pmos\n")
	spice_file.write("Xwire_lut_int_buffer_out n_7_1 n_7_2 wire Rw=wire_lut_int_buffer_out_res Cw=wire_lut_int_buffer_out_cap\n\n")
	
	spice_file.write("* Second chain\n")
	spice_file.write("Xtgate_lut_L4 n_7_2 n_8_1 n_d n_d_n n_vdd n_gnd tgate Wn=tgate_lut_L4_nmos Wp=tgate_lut_L4_pmos\n")
	spice_file.write("Xwire_lut_L4 n_8_1 n_8_2 wire Rw='wire_lut_L4_res/2' Cw='wire_lut_L4_cap/2'\n")
	spice_file.write("Xwire_lut_L4h n_8_2 n_8_3 wire Rw='wire_lut_L4_res/2' Cw='wire_lut_L4_cap/2'\n")
	spice_file.write("Xtgate_lut_L4h n_gnd n_8_3 n_gnd n_vdd n_vdd n_gnd tgate Wn=tgate_lut_L4_nmos Wp=tgate_lut_L4_pmos\n")
	spice_file.write("Xtgate_lut_L5 n_8_2 n_9_1 n_e n_e_n n_vdd n_gnd tgate Wn=tgate_lut_L5_nmos Wp=tgate_lut_L5_pmos\n")
	spice_file.write("Xwire_lut_L5 n_9_1 n_9_2 wire Rw='wire_lut_L5_res/2' Cw='wire_lut_L5_cap/2'\n")
	spice_file.write("Xwire_lut_L5h n_9_2 n_9_3 wire Rw='wire_lut_L5_res/2' Cw='wire_lut_L5_cap/2'\n")
	spice_file.write("Xtgate_lut_L5h n_gnd n_9_3 n_gnd n_vdd n_vdd n_gnd tgate Wn=tgate_lut_L5_nmos Wp=tgate_lut_L5_pmos\n")
	
	spice_file.write("* Output buffer \n")
	# spice_file.write("Xrest_lut_out_buffer n_9_2 n_11_1 n_vdd n_gnd rest Wp=rest_lut_out_buffer_pmos\n")
	spice_file.write("Xinv_lut_out_buffer_1 n_9_2 n_11_1 n_vdd n_gnd inv Wn=inv_lut_out_buffer_1_nmos Wp=inv_lut_out_buffer_1_pmos\n")
	spice_file.write("Xwire_lut_out_buffer n_11_1 n_11_2 wire Rw=wire_lut_out_buffer_res Cw=wire_lut_out_buffer_cap\n")
	spice_file.write("Xinv_lut_out_buffer_2 n_11_2 n_out n_vdd n_gnd inv Wn=inv_lut_out_buffer_2_nmos Wp=inv_lut_out_buffer_2_pmos\n\n")
	spice_file.write(".ENDS\n\n\n")
	
	
	# Create a list of all transistors used in this subcircuit
	tran_names_list = []
	tran_names_list.append("inv_lut_0sram_driver_2_nmos")
	tran_names_list.append("inv_lut_0sram_driver_2_pmos")
	tran_names_list.append("tgate_lut_L1_nmos")
	tran_names_list.append("tgate_lut_L1_pmos")
	tran_names_list.append("tgate_lut_L2_nmos")
	tran_names_list.append("tgate_lut_L2_pmos")
	tran_names_list.append("tgate_lut_L3_nmos")
	tran_names_list.append("tgate_lut_L3_pmos")
	# tran_names_list.append("rest_lut_int_buffer_pmos")
	tran_names_list.append("inv_lut_int_buffer_1_nmos")
	tran_names_list.append("inv_lut_int_buffer_1_pmos")
	tran_names_list.append("inv_lut_int_buffer_2_nmos")
	tran_names_list.append("inv_lut_int_buffer_2_pmos")
	tran_names_list.append("tgate_lut_L4_nmos")
	tran_names_list.append("tgate_lut_L4_pmos")
	tran_names_list.append("tgate_lut_L5_nmos")
	tran_names_list.append("tgate_lut_L5_pmos")
	# tran_names_list.append("rest_lut_out_buffer_pmos")
	tran_names_list.append("inv_lut_out_buffer_1_nmos")
	tran_names_list.append("inv_lut_out_buffer_1_pmos")
	tran_names_list.append("inv_lut_out_buffer_2_nmos")
	tran_names_list.append("inv_lut_out_buffer_2_pmos")

	# Create a list of all wires used in this subcircuit
	wire_names_list = []
	wire_names_list.append("wire_lut_sram_driver")
	wire_names_list.append("wire_lut_sram_driver_out")
	wire_names_list.append("wire_lut_L1")
	wire_names_list.append("wire_lut_L2")
	wire_names_list.append("wire_lut_L3")
	wire_names_list.append("wire_lut_int_buffer")
	wire_names_list.append("wire_lut_int_buffer_out")
	wire_names_list.append("wire_lut_L4")
	wire_names_list.append("wire_lut_L5")
	wire_names_list.append("wire_lut_out_buffer")
	
	return tran_names_list, wire_names_list

	
def generate_tgate_lut4(spice_filename, min_tran_width, use_finfet):
	""" Generates a 4LUT SPICE deck """
	
	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')
	
	# Create the 4-LUT circuit
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* 4-LUT subcircuit \n")
	spice_file.write("******************************************************************************************\n")
	# We use a 6-LUT interface even if this is a 4-LUT. We just won't connect anything to "n_e" and "n_f".
	spice_file.write(".SUBCKT lut n_in n_out n_a n_a_n n_b n_b_n n_c n_c_n n_d n_d_n n_e n_e_n n_f n_f_n n_vdd n_gnd\n")
	Wn = min_tran_width
	Wp = 1.667*min_tran_width
	if not use_finfet :
		spice_file.write("Xinv_lut_sram_driver_1 n_in n_1_1 n_vdd n_gnd inv Wn=" + str(Wn) + "n Wp=" + str(Wp) + "n\n")
	else:
		spice_file.write("Xinv_lut_sram_driver_1 n_in n_1_1 n_vdd n_gnd inv Wn=1 Wp=2 \n")

	spice_file.write("Xwire_lut_sram_driver n_1_1 n_1_2 wire Rw=wire_lut_sram_driver_res Cw=wire_lut_sram_driver_cap\n")
	spice_file.write("Xinv_lut_sram_driver_2 n_1_2 n_2_1 n_vdd n_gnd inv Wn=inv_lut_0sram_driver_2_nmos Wp=inv_lut_0sram_driver_2_pmos\n")
	spice_file.write("Xwire_lut_sram_driver_out n_2_1 n_2_2 wire Rw=wire_lut_sram_driver_out_res Cw=wire_lut_sram_driver_out_cap\n\n")
	
	spice_file.write("* First chain\n")
	spice_file.write("Xtgate_lut_L1 n_2_2 n_3_1 n_a n_a_n n_vdd n_gnd tgate Wn=tgate_lut_L1_nmos Wp=tgate_lut_L1_pmos\n")
	spice_file.write("Xwire_lut_L1 n_3_1 n_3_2 wire Rw='wire_lut_L1_res/2' Cw='wire_lut_L1_cap/2'\n")
	spice_file.write("Xwire_lut_L1h n_3_2 n_3_3 wire Rw='wire_lut_L1_res/2' Cw='wire_lut_L1_cap/2'\n")
	spice_file.write("Xtgate_lut_L1h n_gnd n_3_3 n_gnd n_vdd n_vdd n_gnd tgate Wn=tgate_lut_L1_nmos Wp=tgate_lut_L1_pmos\n")
	spice_file.write("Xtgate_lut_L2 n_3_2 n_4_1 n_b n_b_n n_vdd n_gnd tgate Wn=tgate_lut_L2_nmos Wp=tgate_lut_L2_pmos\n")
	spice_file.write("Xwire_lut_L2 n_4_1 n_4_2 wire Rw='wire_lut_L2_res/2' Cw='wire_lut_L2_cap/2'\n")
	spice_file.write("Xwire_lut_L2h n_4_2 n_4_3 wire Rw='wire_lut_L2_res/2' Cw='wire_lut_L2_cap/2'\n")
	spice_file.write("Xtgate_lut_L2h n_gnd n_4_3 n_gnd n_vdd n_vdd n_gnd tgate Wn=tgate_lut_L2_nmos Wp=tgate_lut_L2_pmos\n\n")
	
	spice_file.write("* Internal buffer \n")
	# spice_file.write("Xrest_lut_int_buffer n_4_2 n_5_1 n_vdd n_gnd rest Wp=rest_lut_int_buffer_pmos\n")
	spice_file.write("Xinv_lut_int_buffer_1 n_4_2 n_5_1 n_vdd n_gnd inv Wn=inv_lut_int_buffer_1_nmos Wp=inv_lut_int_buffer_1_pmos\n")
	spice_file.write("Xwire_lut_int_buffer n_5_1 n_5_2 wire Rw=wire_lut_int_buffer_res Cw=wire_lut_int_buffer_cap\n")
	spice_file.write("Xinv_lut_int_buffer_2 n_5_2 n_6_1 n_vdd n_gnd inv Wn=inv_lut_int_buffer_2_nmos Wp=inv_lut_int_buffer_2_pmos\n")
	spice_file.write("Xwire_lut_int_buffer_out n_6_1 n_6_2 wire Rw=wire_lut_int_buffer_out_res Cw=wire_lut_int_buffer_out_cap\n\n")
	
	spice_file.write("* Second chain\n")
	spice_file.write("Xtgate_lut_L3 n_6_2 n_7_1 n_c n_c_n n_vdd n_gnd tgate Wn=tgate_lut_L3_nmos Wp=tgate_lut_L3_pmos\n")
	spice_file.write("Xwire_lut_L3 n_7_1 n_7_2 wire Rw='wire_lut_L3_res/2' Cw='wire_lut_L3_cap/2'\n")
	spice_file.write("Xwire_lut_L3h n_7_2 n_7_3 wire Rw='wire_lut_L3_res/2' Cw='wire_lut_L3_cap/2'\n")
	spice_file.write("Xtgate_lut_L3h n_gnd n_7_3 n_gnd n_vdd n_vdd n_gnd tgate Wn=tgate_lut_L3_nmos Wp=tgate_lut_L3_pmos\n")
	spice_file.write("Xtgate_lut_L4 n_7_2 n_8_1 n_d n_d_n n_vdd n_gnd tgate Wn=tgate_lut_L4_nmos Wp=tgate_lut_L4_pmos\n")
	spice_file.write("Xwire_lut_L4 n_8_1 n_8_2 wire Rw='wire_lut_L4_res/2' Cw='wire_lut_L4_cap/2'\n")
	spice_file.write("Xwire_lut_L4h n_8_2 n_8_3 wire Rw='wire_lut_L4_res/2' Cw='wire_lut_L4_cap/2'\n")
	spice_file.write("Xtgate_lut_L4h n_gnd n_8_3 n_gnd n_vdd n_vdd n_gnd tgate Wn=tgate_lut_L4_nmos Wp=tgate_lut_L4_pmos\n\n")
	
	spice_file.write("* Output buffer \n")
	# spice_file.write("Xrest_lut_out_buffer n_8_2 n_9_1 n_vdd n_gnd rest Wp=rest_lut_out_buffer_pmos\n")
	spice_file.write("Xinv_lut_out_buffer_1 n_8_2 n_9_1 n_vdd n_gnd inv Wn=inv_lut_out_buffer_1_nmos Wp=inv_lut_out_buffer_1_pmos\n")
	spice_file.write("Xwire_lut_out_buffer n_9_1 n_9_2 wire Rw=wire_lut_out_buffer_res Cw=wire_lut_out_buffer_cap\n")
	spice_file.write("Xinv_lut_out_buffer_2 n_9_2 n_out n_vdd n_gnd inv Wn=inv_lut_out_buffer_2_nmos Wp=inv_lut_out_buffer_2_pmos\n\n")
	spice_file.write(".ENDS\n\n\n")
	
	
	# Create a list of all transistors used in this subcircuit
	tran_names_list = []
	tran_names_list.append("inv_lut_0sram_driver_2_nmos")
	tran_names_list.append("inv_lut_0sram_driver_2_pmos")
	tran_names_list.append("tgate_lut_L1_nmos")
	tran_names_list.append("tgate_lut_L1_pmos")
	tran_names_list.append("tgate_lut_L2_nmos")
	tran_names_list.append("tgate_lut_L2_pmos")
	# tran_names_list.append("rest_lut_int_buffer_pmos")
	tran_names_list.append("inv_lut_int_buffer_1_nmos")
	tran_names_list.append("inv_lut_int_buffer_1_pmos")
	tran_names_list.append("inv_lut_int_buffer_2_nmos")
	tran_names_list.append("inv_lut_int_buffer_2_pmos")
	tran_names_list.append("tgate_lut_L3_nmos")
	tran_names_list.append("tgate_lut_L3_pmos")
	tran_names_list.append("tgate_lut_L4_nmos")
	tran_names_list.append("tgate_lut_L4_pmos")
	# tran_names_list.append("rest_lut_out_buffer_pmos")
	tran_names_list.append("inv_lut_out_buffer_1_nmos")
	tran_names_list.append("inv_lut_out_buffer_1_pmos")
	tran_names_list.append("inv_lut_out_buffer_2_nmos")
	tran_names_list.append("inv_lut_out_buffer_2_pmos")

	# Create a list of all wires used in this subcircuit
	wire_names_list = []
	wire_names_list.append("wire_lut_sram_driver")
	wire_names_list.append("wire_lut_sram_driver_out")
	wire_names_list.append("wire_lut_L1")
	wire_names_list.append("wire_lut_L2")
	wire_names_list.append("wire_lut_int_buffer")
	wire_names_list.append("wire_lut_int_buffer_out")
	wire_names_list.append("wire_lut_L3")
	wire_names_list.append("wire_lut_L4")
	wire_names_list.append("wire_lut_out_buffer")
	
	return tran_names_list, wire_names_list

	

def generate_tgate_lut_driver(spice_filename, lut_input_name, lut_input_type):
	""" Generate a pass-transistor LUT driver based on type. """
	
	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')
	  
	# Create the LUT-input circuit header (same interface for all LUT input types)
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* LUT " + lut_input_name + " subcircuit \n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT " + lut_input_name + " n_in n_out n_gate n_gate_n n_rsel n_not_input n_vdd n_gnd\n")
	
	# The next element is the input driver.
	# We only need an input driver if this is not a "default" input.
	if lut_input_type != "default":
		spice_file.write("Xinv_" + lut_input_name + "_0 n_in n_1_1 n_vdd n_gnd inv Wn=inv_" + lut_input_name + "_0_nmos Wp=inv_" + lut_input_name + "_0_pmos\n")
		# If the LUT input is connected to register select, we add a wire and connect it to the rsel node.
		if lut_input_type == "default_rsel" or lut_input_type == "reg_fb_rsel":
			spice_file.write("Xwire_" + lut_input_name + "_0_rsel n_1_1 n_rsel wire Rw=wire_" + lut_input_name + "_0_rsel_res Cw=wire_" + lut_input_name + "_0_rsel_cap\n")
		# Next is the wire connecting the input inverter to either the output buffer (for "default_rsel")
		# or the pass-transistor (for both "reg_fb" and "reg_fb_rsel"). 
		spice_file.write("Xwire_" + lut_input_name + "_0_out n_1_1 n_1_2 wire Rw=wire_" + lut_input_name + "_0_out_res Cw=wire_" + lut_input_name + "_0_out_cap\n")
		# Now we add a sense inverter for "default_rsel" or the ptran level-restorer and sense inv in the case of both "reg_fb"
		if lut_input_type == "default_rsel":
			spice_file.write("Xinv_" + lut_input_name + "_1 n_1_2 n_3_1 n_vdd n_gnd inv Wn=inv_" + lut_input_name + "_1_nmos Wp=inv_" + lut_input_name + "_1_pmos\n")
		else:
			spice_file.write("Xtgate_" + lut_input_name + "_0 n_1_2 n_2_1 n_gate n_gate_n n_vdd n_gnd tgate Wn=tgate_" + lut_input_name + "_0_nmos Wp=tgate_" + lut_input_name + "_0_pmos\n")
			spice_file.write("Xwire_" + lut_input_name + "_0 n_2_1 n_2_2 wire Rw='wire_" + lut_input_name + "_0_res/2' Cw='wire_" + lut_input_name + "_0_cap/2'\n")
			spice_file.write("Xwire_" + lut_input_name + "_0h n_2_2 n_2_3 wire Rw='wire_" + lut_input_name + "_0_res/2' Cw='wire_" + lut_input_name + "_0_cap/2'\n")
			spice_file.write("Xtgate_" + lut_input_name + "_0h n_gnd n_2_3 n_gate_n n_gate n_vdd n_gnd tgate Wn=tgate_" + lut_input_name + "_0_nmos Wp=tgate_" + lut_input_name + "_0_pmos\n")
			# spice_file.write("Xrest_" + lut_input_name + " n_2_2 n_3_1 n_vdd n_gnd rest Wp=rest_" + lut_input_name + "_pmos\n")
			spice_file.write("Xinv_" + lut_input_name + "_1 n_2_2 n_3_1 n_vdd n_gnd inv Wn=inv_" + lut_input_name + "_1_nmos Wp=inv_" + lut_input_name + "_1_pmos\n")
		# Now we add the wire that connects the sense inverter to the driving inverter
		spice_file.write("Xwire_" + lut_input_name + " n_3_1 n_not_input wire Rw=wire_" + lut_input_name + "_res Cw=wire_" + lut_input_name + "_cap\n")
		# Finally, the driving inverter
		spice_file.write("Xinv_" + lut_input_name + "_2 n_not_input n_out n_vdd n_gnd inv Wn=inv_" + lut_input_name + "_2_nmos Wp=inv_" + lut_input_name + "_2_pmos\n")
	# If this is a default input, all we need is a wire and a driver. But, we are careful to use the same names for corresponding nodes. 
	# This is convenient for writing the top-level SPICE file.   
	else:
		# Add the wire that connects the local mux to the driver
		spice_file.write("Xwire_" + lut_input_name + " n_in n_not_input wire Rw=wire_" + lut_input_name + "_res Cw=wire_" + lut_input_name + "_cap\n")
		# Add the driving inverter
		spice_file.write("Xinv_" + lut_input_name + "_2 n_not_input n_out n_vdd n_gnd inv Wn=inv_" + lut_input_name + "_2_nmos Wp=inv_" + lut_input_name + "_2_pmos\n")
		
	# End the subcircuit    
	spice_file.write(".ENDS\n\n\n")
	
	
	# Create a list of all transistors used in this subcircuit
	tran_names_list = []
	if lut_input_type != "default":
		tran_names_list.append("inv_" + lut_input_name + "_0_nmos")
		tran_names_list.append("inv_" + lut_input_name + "_0_pmos")
	if lut_input_type == "reg_fb" or lut_input_type == "reg_fb_rsel":
		tran_names_list.append("tgate_" + lut_input_name + "_0_nmos")
		tran_names_list.append("tgate_" + lut_input_name + "_0_pmos")
		# tran_names_list.append("rest_" + lut_input_name + "_pmos")
	if lut_input_type != "default":
		tran_names_list.append("inv_" + lut_input_name + "_1_nmos")
		tran_names_list.append("inv_" + lut_input_name + "_1_pmos")
	tran_names_list.append("inv_" + lut_input_name + "_2_nmos")
	tran_names_list.append("inv_" + lut_input_name + "_2_pmos")
	
	
	# Create a list of all wires used in this subcircuit
	wire_names_list = []
	if lut_input_type == "default_rsel" or lut_input_type == "reg_fb_rsel":
		wire_names_list.append("wire_" + lut_input_name + "_0_rsel")
	if lut_input_type != "default":
		wire_names_list.append("wire_" + lut_input_name + "_0_out")
	if lut_input_type == "reg_fb" or lut_input_type == "reg_fb_rsel":
		wire_names_list.append("wire_" + lut_input_name + "_0")
	wire_names_list.append("wire_" + lut_input_name)
	
	return tran_names_list, wire_names_list
 

#samething doesn't change?
def generate_tgate_lut_not_driver(spice_filename, lut_input_name):
	""" Generate a pass-transistor LUT driver based on type. """

	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')
	  
	# Create the LUT-input circuit
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* LUT " + lut_input_name + " subcircuit \n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT " + lut_input_name + " n_in n_out n_vdd n_gnd\n")
	spice_file.write("Xinv_" + lut_input_name + "_1 n_in n_1_1 n_vdd n_gnd inv Wn=inv_" + lut_input_name + "_1_nmos Wp=inv_" + lut_input_name + "_1_pmos\n")
	spice_file.write("Xwire_" + lut_input_name + " n_1_1 n_1_2 wire Rw=wire_" + lut_input_name + "_res Cw=wire_" + lut_input_name + "_cap\n")
	spice_file.write("Xinv_" + lut_input_name + "_2 n_1_2 n_out n_vdd n_gnd inv Wn=inv_" + lut_input_name + "_2_nmos Wp=inv_" + lut_input_name + "_2_pmos\n")
	spice_file.write(".ENDS\n\n\n")
	
	
	# Create a list of all transistors used in this subcircuit
	tran_names_list = []
	tran_names_list.append("inv_" + lut_input_name + "_1_nmos")
	tran_names_list.append("inv_" + lut_input_name + "_1_pmos")
	tran_names_list.append("inv_" + lut_input_name + "_2_nmos")
	tran_names_list.append("inv_" + lut_input_name + "_2_pmos")
	
	
	# Create a list of all wires used in this subcircuit
	wire_names_list = []
	wire_names_list.append("wire_" + lut_input_name)
	
	return tran_names_list, wire_names_list


def generate_tgate_lut_driver_load(spice_filename, lut_input_name, K, use_fluts):
	""" Generates LUT input load SPICE deck """
	
	# Calculate number of pass-transistors loading this input
	max_num_tgate = math.pow(2, K)
	if lut_input_name == "a":
		num_tgate_load = int(max_num_tgate/2)
		tgate_level = "L1"
	elif lut_input_name == "b":
		num_tgate_load = int(max_num_tgate/4)
		tgate_level = "L2"
	elif lut_input_name == "c":
		num_tgate_load = int(max_num_tgate/8)
		tgate_level = "L3"
	elif lut_input_name == "d":
		num_tgate_load = int(max_num_tgate/16)
		tgate_level = "L4"
	elif lut_input_name == "e":
		num_tgate_load = int(max_num_tgate/32)
		tgate_level = "L5"
	elif lut_input_name == "f":
		num_tgate_load = int(max_num_tgate/64)
		tgate_level = "L6"
	
	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')
	
	# Create the input load circuit
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* LUT " + lut_input_name + "-input load subcircuit \n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT lut_" + lut_input_name + "_driver_load n_1 n_vdd n_gnd\n")
	for tgate in range(num_tgate_load):
		tgate += 1
		spice_file.write("Xwire_lut_" + lut_input_name + "_driver_load_" + str(tgate) + " n_" + str(tgate) + " n_" + str(tgate+1) + " wire Rw='wire_lut_" + lut_input_name + "_driver_load_res/" + str(num_tgate_load) + "' Cw='wire_lut_" + lut_input_name + "_driver_load_cap/" + str(num_tgate_load) + "'\n")
		if use_fluts and num_tgate_load == 1:
			spice_file.write("Xtgate_lut_" + lut_input_name + "_driver_load_" + str(tgate) + " n_gnd n_vdd n_gnd n_" + str(tgate+1) + " n_vdd n_gnd tgate Wn=tgate_flut_mux_nmos Wp=tgate_flut_mux_pmos\n") 
		else:
			spice_file.write("Xtgate_lut_" + lut_input_name + "_driver_load_" + str(tgate) + " n_gnd n_vdd n_gnd n_" + str(tgate+1) + " n_vdd n_gnd tgate Wn=tgate_lut_" + tgate_level + "_nmos Wp=tgate_lut_" + tgate_level + "_pmos\n") 
		
	spice_file.write(".ENDS\n\n\n")
	
	# Create a list of all wires used in this subcircuit
	wire_names_list = []
	wire_names_list.append("wire_lut_" + lut_input_name + "_driver_load")
	
	return wire_names_list


# not used in the code
def generate_full_adder(spice_filename, circuit_name, use_finfet):
	""" Generates full adder SPICE deck """


	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')
	
	# Create the circuit
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* Full adder subcircuit \n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT FA_" + circuit_name + " n_a n_b n_cin n_cout n_sum_out n_p n_vdd n_gnd\n")
	# The core of the FA consists of 3 inveters, 6 Transmission gates and 4 pass transistors.
	# There should be a wire for all inputs and outputs, I'll assume the following for the wires:
	# Cin and cout take half of the wire that is as long as the square root of the LUT + adder + the additional muxes
	# sum takes the square root of the area of the adder (same for b)
	# n_a takes the square root of the area of the LUT (This should be changed if this input comes from elsewhere, like another lut)

	spice_file.write("Xinv_" + circuit_name + "_1 n_a_in n_a_in_bar n_vdd n_gnd inv Wn=inv_" + circuit_name + "_1_nmos Wp=inv_" + circuit_name + "_1_pmos\n")
	spice_file.write("Xinv_" + circuit_name + "_2 n_cin_in n_cin_in_bar n_vdd n_gnd inv Wn=inv_" + circuit_name + "_2_nmos Wp=inv_" + circuit_name + "_2_pmos\n")

	spice_file.write("Xtgate_" + circuit_name + "_1 n_cin_in n_sum_internal n_p n_p_bar n_vdd n_gnd tgate Wn=tgate_" + circuit_name + "_1_nmos Wp=tgate_" + circuit_name + "_1_pmos\n") 
	spice_file.write("Xtgate_" + circuit_name + "_2 n_cin_in_bar n_sum_internal n_p_bar n_p n_vdd n_gnd tgate Wn=tgate_" + circuit_name + "_2_nmos Wp=tgate_" + circuit_name + "_2_pmos\n") 
	spice_file.write("Xtgate_" + circuit_name + "_3 n_b_in n_p n_a_in_bar n_a_in n_vdd n_gnd tgate Wn=tgate_" + circuit_name + "_3_nmos Wp=tgate_" + circuit_name + "_3_pmos\n") 
	spice_file.write("Xtgate_" + circuit_name + "_4 n_b_in n_p_bar n_a_in n_a_in_bar n_vdd n_gnd tgate Wn=tgate_" + circuit_name + "_4_nmos Wp=tgate_" + circuit_name + "_4_pmos\n") 
	spice_file.write("Xtgate_" + circuit_name + "_5 n_a_in_bar n_sum_internal n_p_bar n_p n_vdd n_gnd tgate Wn=tgate_" + circuit_name + "_5_nmos Wp=tgate_" + circuit_name + "_5_pmos\n") 
	spice_file.write("Xtgate_" + circuit_name + "_6 n_cin_in_bar n_sum_internal n_p n_p_bar n_vdd n_gnd tgate Wn=tgate_" + circuit_name + "_6_nmos Wp=tgate_" + circuit_name + "_6_pmos\n") 

	spice_file.write("Xptran_" + circuit_name + "_1 n_p n_b_in n_a_in_bar n_gnd ptran Wn=ptran_" + circuit_name + "_1_nmos\n")
	spice_file.write("Xptran_" + circuit_name + "_2 n_p_bar n_b_in n_a_in n_gnd ptran Wn=ptran_" + circuit_name + "_2_nmos\n")
	spice_file.write("Xptran_" + circuit_name + "_3 n_p_bar n_b_in n_a_in_bar n_vdd ptranp Wn=ptran_" + circuit_name + "_3_nmos\n")
	spice_file.write("Xptran_" + circuit_name + "_4 n_p n_b_in n_a_in n_vdd ptranp Wn=ptran_" + circuit_name + "_4_nmos\n")

	spice_file.write("Xwire_" + circuit_name + "_1 n_a n_a_in wire Rw='wire_fa_a_res' Cw='wire_fa_a_cap' \n")
	spice_file.write("Xwire_" + circuit_name + "_2 n_b n_b_in wire Rw='wire_fa_b_res' Cw='wire_fa_b_cap' \n")
	spice_file.write("Xwire_" + circuit_name + "_3 n_cin n_cin_in wire Rw='wire_fa_cin_res' Cw='wire_fa_cin_cap' \n")
	spice_file.write("Xwire_" + circuit_name + "_4 n_cout n_cout_in wire Rw='wire_fa_cout_res' Cw='wire_fa_cout_cap' \n")
	spice_file.write("Xwire_" + circuit_name + "_5 n_sum_out n_sum_in wire Rw='wire_fa_cout_res' Cw='wire_fa_cout_cap' \n")

	spice_file.write("Xinv_" + circuit_name + "_3 n_sum_internal n_sum_in n_vdd n_gnd inv Wn=inv_" + circuit_name + "_3_nmos Wp=inv_" + circuit_name + "_3_pmos\n")
	spice_file.write(".ENDS\n\n\n")

	# Create a list of all transistors used in this subcircuit
	tran_names_list = []
	tran_names_list.append("inv_" + circuit_name + "_1_nmos")
	tran_names_list.append("inv_" + circuit_name + "_1_pmos")
	tran_names_list.append("inv_" + circuit_name + "_2_nmos")
	tran_names_list.append("inv_" + circuit_name + "_2_pmos")
	tran_names_list.append("inv_" + circuit_name + "_3_nmos")
	tran_names_list.append("inv_" + circuit_name + "_3_pmos")	
	tran_names_list.append("tgate_" + circuit_name + "_1_nmos")
	tran_names_list.append("tgate_" + circuit_name + "_1_pmos")
	tran_names_list.append("tgate_" + circuit_name + "_2_nmos")
	tran_names_list.append("tgate_" + circuit_name + "_2_pmos")
	tran_names_list.append("tgate_" + circuit_name + "_3_nmos")
	tran_names_list.append("tgate_" + circuit_name + "_3_pmos")
	tran_names_list.append("tgate_" + circuit_name + "_4_nmos")
	tran_names_list.append("tgate_" + circuit_name + "_4_pmos")
	tran_names_list.append("tgate_" + circuit_name + "_5_nmos")
	tran_names_list.append("tgate_" + circuit_name + "_5_pmos")
	tran_names_list.append("tgate_" + circuit_name + "_6_nmos")
	tran_names_list.append("tgate_" + circuit_name + "_6_pmos")
	tran_names_list.append("ptran_" + circuit_name + "_1_nmos")
	tran_names_list.append("ptran_" + circuit_name + "_2_nmos")
	tran_names_list.append("ptran_" + circuit_name + "_3_nmos")
	tran_names_list.append("ptran_" + circuit_name + "_4_nmos")
	# Create a list of all wires used in this subcircuit
	wire_names_list = []
	wire_names_list.append("wire_" + circuit_name + "_1")
	wire_names_list.append("wire_" + circuit_name + "_2")
	wire_names_list.append("wire_" + circuit_name + "_3")
	wire_names_list.append("wire_" + circuit_name + "_4")
	wire_names_list.append("wire_" + circuit_name + "_5")	

	return tran_names_list, wire_names_list
	

# Simplified version of the above FA, much faster to size
def generate_full_adder_simplified(spice_filename, circuit_name, use_finfet):
	""" Generates full adder SPICE deck """

	
	#TODO: The logic of the cout is not right. Checked with a waveform viewer. 
	#The cin fed to the tgate 6 should be cin and not cin complement and the same 
	#thing applies for the n_a fed to the other tgate connected to cout. Probably this
	#also added to the critical path of the carry chain.
	

	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')
	
	# Create the circuit
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* Full adder subcircuit \n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT FA_" + circuit_name + " n_a n_b n_cin n_cout n_sum_out n_p n_vdd n_gnd\n")
	# The core of the FA consists of 3 inveters, 6 Transmission gates and 4 pass transistors.
	# There should be a wire for all inputs and outputs, I'll assume the following for the wires:
	# Cin and cout take half of the wire that is as long as the square root of the LUT + adder + the additional muxes
	# sum takes the square root of the area of the adder (same for b)
	# n_a takes the square root of the area of the LUT (This should be changed if this input comes from elsewhere, like another lut)

	spice_file.write("Xinv_" + circuit_name + "_1 n_a_in n_a_in_bar n_vdd n_gnd inv Wn=inv_" + circuit_name + "_1_nmos Wp=inv_" + circuit_name + "_1_pmos\n")
	spice_file.write("Xinv_" + circuit_name + "_2 n_cin_in n_cin_in_bar n_vdd n_gnd inv Wn=inv_" + circuit_name + "_2_nmos Wp=inv_" + circuit_name + "_1_pmos\n")

	spice_file.write("Xtgate_" + circuit_name + "_1 n_cin_in n_sum_internal n_p n_p_bar n_vdd n_gnd tgate Wn=tgate_" + circuit_name + "_2_nmos Wp=tgate_" + circuit_name + "_2_pmos\n") 
	spice_file.write("Xtgate_" + circuit_name + "_2 n_cin_in_bar n_sum_internal n_p_bar n_p n_vdd n_gnd tgate Wn=tgate_" + circuit_name + "_2_nmos Wp=tgate_" + circuit_name + "_2_pmos\n") 
	spice_file.write("Xtgate_" + circuit_name + "_3 n_b_in n_p n_a_in_bar n_a_in n_vdd n_gnd tgate Wn=tgate_" + circuit_name + "_1_nmos Wp=tgate_" + circuit_name + "_1_pmos\n") 
	spice_file.write("Xtgate_" + circuit_name + "_4 n_b_in n_p_bar n_a_in n_a_in_bar n_vdd n_gnd tgate Wn=tgate_" + circuit_name + "_1_nmos Wp=tgate_" + circuit_name + "_1_pmos\n") 
	spice_file.write("Xtgate_" + circuit_name + "_5 n_a_in_bar n_cout_in n_p_bar n_p n_vdd n_gnd tgate Wn=tgate_" + circuit_name + "_2_nmos Wp=tgate_" + circuit_name + "_2_pmos\n") 
	spice_file.write("Xtgate_" + circuit_name + "_6 n_cin_in_bar n_cout_in n_p n_p_bar n_vdd n_gnd tgate Wn=tgate_" + circuit_name + "_2_nmos Wp=tgate_" + circuit_name + "_2_pmos\n") 

	spice_file.write("Xptran_" + circuit_name + "_1 n_p n_a_in_bar n_b_in n_gnd ptran Wn=tgate_" + circuit_name + "_1_nmos\n")
	spice_file.write("Xptran_" + circuit_name + "_2 n_p_bar n_a_in n_b_in n_gnd ptran Wn=tgate_" + circuit_name + "_1_nmos\n")
	spice_file.write("Xptran_" + circuit_name + "_3 n_p_bar n_a_in_bar n_b_in n_vdd ptranp Wn=tgate_" + circuit_name + "_1_pmos\n")
	spice_file.write("Xptran_" + circuit_name + "_4 n_p n_a_in n_b_in n_vdd ptranp Wn=tgate_" + circuit_name + "_1_pmos\n")

	spice_file.write("Xwire_" + circuit_name + "_1 n_a n_a_in wire Rw='wire_" + circuit_name + "_1_res' Cw='wire_" + circuit_name + "_1_cap' \n")
	spice_file.write("Xwire_" + circuit_name + "_2 n_b n_b_in wire Rw='wire_" + circuit_name + "_2_res' Cw='wire_" + circuit_name + "_2_cap' \n")
	spice_file.write("Xwire_" + circuit_name + "_3 n_cin n_cin_in wire Rw='wire_" + circuit_name + "_3_res' Cw='wire_" + circuit_name + "_3_cap' \n")
	spice_file.write("Xwire_" + circuit_name + "_4 n_cout n_cout_in wire Rw='wire_" + circuit_name + "_4_res' Cw='wire_" + circuit_name + "_4_cap' \n")
	spice_file.write("Xwire_" + circuit_name + "_5 n_sum_out n_sum_in wire Rw='wire_" + circuit_name + "_5_res' Cw='wire_" + circuit_name + "_5_cap' \n")

	spice_file.write("Xinv_" + circuit_name + "_3 n_sum_internal n_sum_in n_vdd n_gnd inv Wn=inv_" + circuit_name + "_2_nmos Wp=inv_" + circuit_name + "_2_pmos\n")

	spice_file.write(".ENDS\n\n\n")
	# Create a list of all transistors used in this subcircuit
	tran_names_list = []
	tran_names_list.append("inv_" + circuit_name + "_1_nmos")
	tran_names_list.append("inv_" + circuit_name + "_1_pmos")
	tran_names_list.append("inv_" + circuit_name + "_2_nmos")
	tran_names_list.append("inv_" + circuit_name + "_2_pmos")

	tran_names_list.append("tgate_" + circuit_name + "_1_nmos")
	tran_names_list.append("tgate_" + circuit_name + "_1_pmos")
	tran_names_list.append("tgate_" + circuit_name + "_2_nmos")
	tran_names_list.append("tgate_" + circuit_name + "_2_pmos")
	
	# Create a list of all wires used in this subcircuit
	wire_names_list = []
	wire_names_list.append("wire_" + circuit_name + "_1")
	wire_names_list.append("wire_" + circuit_name + "_2")
	wire_names_list.append("wire_" + circuit_name + "_3")
	wire_names_list.append("wire_" + circuit_name + "_4")
	wire_names_list.append("wire_" + circuit_name + "_5")	

	return tran_names_list, wire_names_list
	

def generate_carry_chain_perf_ripple(spice_filename, circuit_name, use_finfet):
	""" Generates carry chain inverters for sum SPICE deck """


	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')
	
	# Create the circuit
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* carry chain periphery subcircuit \n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT " + circuit_name + " n_in n_out n_vdd n_gnd\n")
	spice_file.write("Xinv_lut_int_buffer_1 n_in n_out n_vdd n_gnd inv Wn=inv_" + circuit_name + "_1_nmos Wp=inv_" + circuit_name + "_1_pmos\n")
	spice_file.write(".ENDS\n\n\n")

	tran_names_list = []
	tran_names_list.append("inv_" + circuit_name + "_1_nmos")
	tran_names_list.append("inv_" + circuit_name + "_1_pmos")
	wire_names_list = []
	return tran_names_list, wire_names_list


def generate_skip_and_tree(spice_filename, circuit_name, use_finfet, nand1_size, nand2_size):

	""" Generates carry chain skip and tree for sum SPICE deck """

	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')
	
	# Create the circuit
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* carry chain and tree subcircuit \n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT " + circuit_name + " n_in n_out n_vdd n_gnd\n")


	spice_file.write("Xwire_" + circuit_name + "_1 n_in n_1_1 wire Rw='wire_"+circuit_name+"_1_res' Cw='wire_"+circuit_name+"_1_cap' \n")
	spice_file.write("Xnand1 n_1_1 n_1_2 n_vdd n_gnd nand"+str(nand1_size)+" Wn=inv_nand"+str(nand1_size)+"_" + circuit_name + "_1_nmos Wp=inv_nand"+str(nand1_size)+"_" + circuit_name + "_1_pmos\n")
	spice_file.write("Xinv1 n_1_2 n_1_3 n_vdd n_gnd inv Wn=inv_" + circuit_name + "_2_nmos Wp=inv_" + circuit_name + "_2_pmos\n")

	spice_file.write("Xwire_" + circuit_name + "_2 n_1_3 n_1_4 wire Rw='wire_"+circuit_name+"_2_res' Cw='wire_"+circuit_name+"_2_cap' \n")
	spice_file.write("Xnand2 n_1_4 n_1_5 n_vdd n_gnd nand"+str(nand2_size)+" Wn=inv_nand"+str(nand2_size)+"_" + circuit_name + "_3_nmos Wp=inv_nand"+str(nand2_size)+"_" + circuit_name + "_3_pmos\n")
	spice_file.write("Xinv2 n_1_5 n_out n_vdd n_gnd inv Wn=inv_" + circuit_name + "_4_nmos Wp=inv_" + circuit_name + "_4_pmos\n")
	spice_file.write(".ENDS\n\n\n")

	tran_names_list = []
	tran_names_list.append("inv_nand"+str(nand1_size)+"_" + circuit_name + "_1_nmos")
	tran_names_list.append("inv_nand"+str(nand1_size)+"_" + circuit_name + "_1_pmos")
	tran_names_list.append("inv_" + circuit_name + "_2_nmos")
	tran_names_list.append("inv_" + circuit_name + "_2_pmos")	
	tran_names_list.append("inv_nand"+str(nand2_size)+"_" + circuit_name + "_3_nmos")
	tran_names_list.append("inv_nand"+str(nand2_size)+"_" + circuit_name + "_3_pmos")
	tran_names_list.append("inv_" + circuit_name + "_4_nmos")
	tran_names_list.append("inv_" + circuit_name + "_4_pmos")
	wire_names_list = []
	wire_names_list.append("wire_"+circuit_name+"_1")
	wire_names_list.append("wire_"+circuit_name+"_2")
	
	return tran_names_list, wire_names_list


def generate_carry_inter(spice_filename, circuit_name, use_finfet):

	""" Generates the driver to load "cin" of the next cluster """

	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')
	
	# Create the circuit
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* carry chain and tree subcircuit \n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT " + circuit_name + " n_in n_out n_vdd n_gnd\n")

	spice_file.write("Xinv1 n_in n_1_1 n_vdd n_gnd inv Wn=inv_" + circuit_name + "_1_nmos Wp=inv_" + circuit_name + "_1_pmos\n")
	spice_file.write("Xinv2 n_1_1 n_1_2 n_vdd n_gnd inv Wn=inv_" + circuit_name + "_2_nmos Wp=inv_" + circuit_name + "_2_pmos\n")
	spice_file.write("Xwire_" + circuit_name + "_1 n_1_2 n_out wire Rw='wire_"+circuit_name+"_1_res' Cw='wire_"+circuit_name+"_1_cap' \n")

	spice_file.write(".ENDS\n\n\n")

	tran_names_list = []

	tran_names_list.append("inv_" + circuit_name + "_1_nmos")
	tran_names_list.append("inv_" + circuit_name + "_1_pmos")	
	tran_names_list.append("inv_" + circuit_name + "_2_nmos")
	tran_names_list.append("inv_" + circuit_name + "_2_pmos")
	wire_names_list = []
	wire_names_list.append("wire_"+circuit_name+"_1")

	return tran_names_list, wire_names_list


