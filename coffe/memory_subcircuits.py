


import math

# This is the first stage of the row decoder if the decoder bits are less than 8
def generate_rowdecoderstage1(spice_filename, circuit_name, nandtype):

	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')
	
	# Generate SPICE subcircuits
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* " + circuit_name + " stage 0 of row decoder\n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT " + circuit_name + " n_in n_out n_vdd n_gnd\n")
	spice_file.write("X" + circuit_name + "_nand n_in n_1_1 n_vdd n_gnd nand"+str(nandtype)+" Wn=inv_nand" + nandtype + "_" + circuit_name + "_1_nmos Wp=inv_nand" + nandtype+ "_" + circuit_name + "_1_pmos\n")
	spice_file.write("X" + circuit_name + "_inv n_1_1 n_out n_vdd n_gnd inv Wn=inv_" + circuit_name + "_2_nmos Wp=inv_" + circuit_name + "_2_pmos\n")

	spice_file.write(".ENDS\n\n\n")
	
	# Close SPICE file
	spice_file.close()
	
	# Create a list of all transistors used in this subcircuit
	tran_names_list = []
	tran_names_list.append("inv_nand" + nandtype + "_" + circuit_name + "_1_nmos")
	tran_names_list.append("inv_nand" + nandtype + "_" + circuit_name + "_1_pmos")
	tran_names_list.append("inv_" + circuit_name + "_2_nmos")
	tran_names_list.append("inv_" + circuit_name + "_2_pmos")
	# Create a list of all wires used in this subcircuit
	wire_names_list = []


	# return the list of tranaistors and wires
	return tran_names_list, wire_names_list


# This is the low power version of the first stage of the row decoder if the decoder bits are less than 8
def generate_rowdecoderstage1_lp(spice_filename, circuit_name, nandtype):

	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')
	
	# Generate SPICE subcircuits

	spice_file.write("******************************************************************************************\n")
	spice_file.write("* " + circuit_name + " low power stage 0 of row decoder\n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT " + circuit_name + " n_in n_out n_vdd n_gnd\n")
	spice_file.write("X" + circuit_name + "_nand n_in n_1_1 n_vdd n_gnd nand"+str(nandtype)+"_lp Wn=inv_nand" + str(nandtype) + "_" + circuit_name + "_1_nmos Wp=inv_nand" + str(nandtype)+ "_" + circuit_name + "_1_pmos\n")
	spice_file.write("X" + circuit_name + "_inv n_1_1 n_out n_vdd n_gnd inv_lp Wn=inv_" + circuit_name + "_2_nmos Wp=inv_" + circuit_name + "_2_pmos\n")

	spice_file.write(".ENDS\n\n\n")
	
	# Close SPICE file
	spice_file.close()
	
	# Create a list of all transistors used in this subcircuit
	tran_names_list = []
	tran_names_list.append("inv_nand" + str(nandtype) + "_" + circuit_name + "_1_nmos")
	tran_names_list.append("inv_nand" + str(nandtype) + "_" + circuit_name + "_1_pmos")
	tran_names_list.append("inv_" + circuit_name + "_2_nmos")
	tran_names_list.append("inv_" + circuit_name + "_2_pmos")
	# Create a list of all wires used in this subcircuit
	wire_names_list = []

	# return the list of tranaistors and wires
	return tran_names_list, wire_names_list

# This is the second stage of the configurable decoder when using 2-input NAND gates
def generate_configurabledecoder2ii(spice_filename, nand2circuit_name):

   
	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')

	# Create the circuit
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* " + nand2circuit_name + " subcircuit configurable decoder \n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT " + nand2circuit_name + " n_in n_out n_vdd n_gnd\n")
	spice_file.write("X" + nand2circuit_name + "_nand2 n_in n_1_1 n_vdd n_gnd nand2 Wn=inv_nand2_" + nand2circuit_name + "_1_nmos Wp=inv_nand2_" + nand2circuit_name + "_1_pmos\n")
	spice_file.write("X_inv" + nand2circuit_name + " n_1_1 n_out n_vdd n_gnd inv Wn=inv_" + nand2circuit_name + "_2_nmos Wp=inv_" + nand2circuit_name + "_2_pmos\n")
	spice_file.write(".ENDS\n\n\n")
	
	# Close SPICE file
	spice_file.close()
	
	# Create a list of all transistors used in this subcircuit
	tran_names_list = []
	tran_names_list.append("inv_nand2_" + nand2circuit_name + "_1_nmos")
	tran_names_list.append("inv_nand2_" + nand2circuit_name + "_1_pmos")
	tran_names_list.append("inv_" + nand2circuit_name + "_2_nmos")
	tran_names_list.append("inv_" + nand2circuit_name + "_2_nmos")
	
	# Create a list of all wires used in this subcircuit
	wire_names_list = []



	return tran_names_list, wire_names_list

# This is the low power version of the second stage of the configurable decoder when using 2-input NAND gates
def generate_configurabledecoder2ii_lp(spice_filename, nand2circuit_name):

   
	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')
	
	
	# Create the circuit
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* " + nand2circuit_name + " subcircuit configurable decoder \n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT " + nand2circuit_name + " n_in n_out n_vdd n_gnd\n")
	spice_file.write("X" + nand2circuit_name + "_nand2 n_in n_1_1 n_vdd n_gnd nand2_lp Wn=inv_nand2_" + nand2circuit_name + "_1_nmos Wp=inv_nand2_" + nand2circuit_name + "_1_pmos\n")
	spice_file.write("X_inv" + nand2circuit_name + " n_1_1 n_out n_vdd n_gnd inv_lp Wn=inv_" + nand2circuit_name + "_2_nmos Wp=inv_" + nand2circuit_name + "_2_pmos\n")
	spice_file.write(".ENDS\n\n\n")
	
	# Close SPICE file
	spice_file.close()
	
	# Create a list of all transistors used in this subcircuit
	tran_names_list = []
	tran_names_list.append("inv_nand2_" + nand2circuit_name + "_1_nmos")
	tran_names_list.append("inv_nand2_" + nand2circuit_name + "_1_pmos")
	tran_names_list.append("inv_" + nand2circuit_name + "_2_nmos")
	tran_names_list.append("inv_" + nand2circuit_name + "_2_nmos")
	
	# Create a list of all wires used in this subcircuit
	wire_names_list = []



	return tran_names_list, wire_names_list

# This is the second stage of the configurable decoder when using 3-input NAND gates
def generate_configurabledecoder3ii(spice_filename, nand3circuit_name):

   
	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')
	

	# Create the circuit
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* " + nand3circuit_name + " subcircuit configurable decoder \n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT " + nand3circuit_name + " n_in n_out n_vdd n_gnd\n")
	spice_file.write("X" + nand3circuit_name + "_nand3 n_in n_1_1 n_vdd n_gnd nand3 Wn=inv_nand3_" + nand3circuit_name + "_1_nmos Wp=inv_nand3_" + nand3circuit_name + "_1_pmos\n")
	spice_file.write("X_inv" + nand3circuit_name + " n_1_1 n_out n_vdd n_gnd inv Wn=inv_" + nand3circuit_name + "_2_nmos Wp=inv_" + nand3circuit_name + "_2_pmos\n")
	spice_file.write(".ENDS\n\n\n")
	
	# Close SPICE file
	spice_file.close()
	
	# Create a list of all transistors used in this subcircuit
	tran_names_list = []
	tran_names_list.append("inv_nand3_" + nand3circuit_name + "_1_nmos")
	tran_names_list.append("inv_nand3_" + nand3circuit_name + "_1_pmos")
	tran_names_list.append("inv_" + nand3circuit_name + "_2_nmos")
	tran_names_list.append("inv_" + nand3circuit_name + "_2_nmos")
	
	# Create a list of all wires used in this subcircuit
	wire_names_list = []



	return tran_names_list, wire_names_list


# This is the second stage of the configurable decoder when using 3-input NAND gates
def generate_configurabledecoder3ii_lp(spice_filename, nand3circuit_name):

   
	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')

	# Create the circuit
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* " + nand3circuit_name + " subcircuit configurable decoder \n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT " + nand3circuit_name + " n_in n_out n_vdd n_gnd\n")
	spice_file.write("X" + nand3circuit_name + "_nand3 n_in n_1_1 n_vdd n_gnd nand3_lp Wn=inv_nand3_" + nand3circuit_name + "_1_nmos Wp=inv_nand3_" + nand3circuit_name + "_1_pmos\n")
	spice_file.write("X_inv" + nand3circuit_name + " n_1_1 n_out n_vdd n_gnd inv_lp Wn=inv_" + nand3circuit_name + "_2_nmos Wp=inv_" + nand3circuit_name + "_2_pmos\n")
	spice_file.write(".ENDS\n\n\n")
	
	# Close SPICE file
	spice_file.close()
	
	# Create a list of all transistors used in this subcircuit
	tran_names_list = []
	tran_names_list.append("inv_nand3_" + nand3circuit_name + "_1_nmos")
	tran_names_list.append("inv_nand3_" + nand3circuit_name + "_1_pmos")
	tran_names_list.append("inv_" + nand3circuit_name + "_2_nmos")
	tran_names_list.append("inv_" + nand3circuit_name + "_2_nmos")
	
	# Create a list of all wires used in this subcircuit
	wire_names_list = []



	return tran_names_list, wire_names_list

#This is the last stage of the configurable decoder
def generate_configurabledecoderiii(spice_filename, circuit_name, required_size):

   
	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')

	# Create the circuit
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* " + circuit_name + " subcircuit configurable decoder \n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT " + circuit_name + " n_in n_out n_vdd n_gnd\n")
	spice_file.write("X" + circuit_name + "_nand"+str(required_size)+" n_in n_1_1 n_vdd n_gnd nand"+str(required_size)+" Wn=inv_nand"+str(required_size)+"_" + circuit_name + "_1_nmos Wp=inv_nand"+str(required_size)+"_" + circuit_name + "_1_pmos\n")
	spice_file.write("X_inv" + circuit_name + " n_1_1 n_out n_vdd n_gnd inv Wn=inv_" + circuit_name + "_2_nmos Wp=inv_" + circuit_name + "_2_pmos\n")
	spice_file.write(".ENDS\n\n\n")
	
	# Close SPICE file
	spice_file.close()
	
	# Create a list of all transistors used in this subcircuit
	tran_names_list = []
	tran_names_list.append("inv_nand"+str(required_size)+"_" + circuit_name + "_1_nmos")
	tran_names_list.append("inv_nand"+str(required_size)+"_" + circuit_name + "_1_pmos")
	tran_names_list.append("inv_" + circuit_name + "_2_nmos")
	tran_names_list.append("inv_" + circuit_name + "_2_nmos")
	
	# Create a list of all wires used in this subcircuit
	wire_names_list = []



	return tran_names_list, wire_names_list

#This is the low power version of the last stage of the configurable decoder
def generate_configurabledecoderiii_lp(spice_filename, circuit_name, required_size):

   
	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')
	
	
	# Create thecircuit
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* " + circuit_name + " subcircuit configurable decoder \n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT " + circuit_name + " n_in n_out n_vdd n_gnd\n")
	spice_file.write("X" + circuit_name + "_nand"+str(required_size)+" n_in n_1_1 n_vdd n_gnd nand"+str(required_size)+"_lp Wn=inv_nand"+str(required_size)+"_" + circuit_name + "_1_nmos Wp=inv_nand"+str(required_size)+"_" + circuit_name + "_1_pmos\n")
	spice_file.write("X_inv" + circuit_name + " n_1_1 n_out n_vdd n_gnd inv_lp Wn=inv_" + circuit_name + "_2_nmos Wp=inv_" + circuit_name + "_2_pmos\n")
	spice_file.write(".ENDS\n\n\n")
	
	# Close SPICE file
	spice_file.close()
	
	# Create a list of all transistors used in this subcircuit
	tran_names_list = []
	tran_names_list.append("inv_nand"+str(required_size)+"_" + circuit_name + "_1_nmos")
	tran_names_list.append("inv_nand"+str(required_size)+"_" + circuit_name + "_1_pmos")
	tran_names_list.append("inv_" + circuit_name + "_2_nmos")
	tran_names_list.append("inv_" + circuit_name + "_2_nmos")
	
	# Create a list of all wires used in this subcircuit
	wire_names_list = []


	return tran_names_list, wire_names_list


# This is the last stage of the row decoder is the size is less than 8 bits
def generate_rowdecoderstage3(spice_filename, circuit_name, fan_out, number_of_banks):

	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')
	
	# Generate SPICE subcircuits
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* " + circuit_name + " subcircuit row decoder last stage \n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT " + circuit_name + " n_in n_out n_vdd n_gnd\n")
	spice_file.write("X0" + circuit_name + "_nand"+ str(fan_out)+" n_in n_1_1 n_vdd n_gnd nand"+ str(fan_out)+" Wn=inv_nand"+ str(fan_out)+"_" + circuit_name + "_1_nmos Wp=inv_nand"+ str(fan_out)+"_" + circuit_name + "_1_pmos\n")
	#spice_file.write("X_inv" + circuit_name + "_2 n_1_1 n_1_2 n_vdd n_gnd inv Wn=inv_" + circuit_name + "_2_nmos Wp=inv_" + circuit_name + "_2_pmos\n")
	spice_file.write("X_inv" + circuit_name + "_2 n_1_1 n_out n_vdd n_gnd inv Wn=inv_" + circuit_name + "_2_nmos Wp=inv_" + circuit_name + "_2_pmos\n")

	spice_file.write(".ENDS\n\n\n")
	
	# Close SPICE file
	spice_file.close()


	# Create a list of transistors
	tran_names_list = []
	tran_names_list.append("inv_nand"+ str(fan_out)+"_" + circuit_name + "_1_nmos")
	tran_names_list.append("inv_nand"+ str(fan_out)+"_" + circuit_name + "_1_pmos")
	tran_names_list.append("inv_" + circuit_name + "_2_nmos")
	tran_names_list.append("inv_" + circuit_name + "_2_nmos")


	wire_names_list = []


	return tran_names_list, wire_names_list	

# This is the low power version of the last stage of the row decoder is the size is less than 8 bits
def generate_rowdecoderstage3_lp(spice_filename, circuit_name, fan_out, number_of_banks):

	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')
	
	# Generate SPICE subcircuits
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* " + circuit_name + " row decoder last stage \n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT " + circuit_name + " n_in n_out n_vdd n_gnd\n")
	spice_file.write("X0" + circuit_name + "_nand"+ str(fan_out)+" n_in n_1_1 n_vdd n_gnd nand"+ str(fan_out)+"_lp Wn=inv_nand"+ str(fan_out)+"_" + circuit_name + "_1_nmos Wp=inv_nand"+ str(fan_out)+"_" + circuit_name + "_1_pmos\n")
	#spice_file.write("X_inv" + circuit_name + "_2 n_1_1 n_1_2 n_vdd n_gnd inv_lp Wn=inv_" + circuit_name + "_2_nmos Wp=inv_" + circuit_name + "_2_pmos\n")
	spice_file.write("X_inv" + circuit_name + "_2 n_1_1 n_out n_vdd n_gnd inv_lp Wn=inv_" + circuit_name + "_2_nmos Wp=inv_" + circuit_name + "_2_pmos\n")



	spice_file.write(".ENDS\n\n\n")
	
	# Close SPICE file
	spice_file.close()

	# Create a list of transistors

	tran_names_list = []
	tran_names_list.append("inv_nand"+ str(fan_out)+"_" + circuit_name + "_1_nmos")
	tran_names_list.append("inv_nand"+ str(fan_out)+"_" + circuit_name + "_1_pmos")
	tran_names_list.append("inv_" + circuit_name + "_2_nmos")
	tran_names_list.append("inv_" + circuit_name + "_2_nmos")

	wire_names_list = []


	return tran_names_list, wire_names_list	


# This is the level shifter circuitry that we assume
def generate_level_shifter(spice_filename, circuit_name): 

	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')

	# Generate the circuit
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* " + circuit_name + " subcircuit level shifter \n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT " + circuit_name + " n_in n_out n_vdd n_vddlp n_gnd\n")
	spice_file.write("X_inv" + circuit_name + "_1 n_in n_1_1 n_vdd n_gnd inv Wn=inv_level_shifter_1_nmos Wp=inv_level_shifter_1_pmos\n")
	spice_file.write("X_inv" + circuit_name + "_2 n_1_1 n_1_2 n_vdd n_gnd inv Wn=inv_level_shifter_1_nmos Wp=inv_level_shifter_1_pmos\n")
	spice_file.write("M0 n_gnd n_1_1 n_1_3 n_gnd nmos_lp L=22n W=ptran_level_shifter_2_nmos ") 
	spice_file.write("AS=ptran_level_shifter_2_nmos*trans_diffusion_length AD=ptran_level_shifter_2_nmos*trans_diffusion_length PS=ptran_level_shifter_2_nmos+2*trans_diffusion_length PD=ptran_level_shifter_2_nmos+2*trans_diffusion_length\n")
	spice_file.write("M1 n_gnd n_1_2 n_1_4 n_gnd nmos_lp L=22n W=ptran_level_shifter_2_nmos ") 
	spice_file.write("AS=ptran_level_shifter_2_nmos*trans_diffusion_length AD=ptran_level_shifter_2_nmos*trans_diffusion_length PS=ptran_level_shifter_2_nmos+2*trans_diffusion_length PD=ptran_level_shifter_2_nmos+2*trans_diffusion_length\n")
	spice_file.write("M2 n_1_3 n_1_4 n_vddlp n_vddlp pmos_lp L=22n W=ptran_level_shifter_2_nmos ") 
	spice_file.write("AS=ptran_level_shifter_3_pmos*trans_diffusion_length AD=ptran_level_shifter_3_pmos*trans_diffusion_length PS=ptran_level_shifter_3_pmos+2*trans_diffusion_length PD=ptran_level_shifter_3_pmos+2*trans_diffusion_length\n")
	spice_file.write("M3 n_1_4 n_1_3 n_vddlp n_vddlp pmos_lp L=22n W=ptran_level_shifter_3_pmos ") 
	spice_file.write("AS=ptran_level_shifter_3_pmos*trans_diffusion_length AD=ptran_level_shifter_3_pmos*trans_diffusion_length PS=ptran_level_shifter_3_pmos+2*trans_diffusion_length PD=ptran_level_shifter_3_pmos+2*trans_diffusion_length\n")
	spice_file.write("X_inv" + circuit_name + "_3 n_1_4 n_out n_vddlp n_gnd inv_lp Wn=inv_level_shifter_1_nmos Wp=inv_level_shifter_1_pmos\n")

	spice_file.write(".ENDS\n\n\n")

	spice_file.close()

	# Add transistors to the list
	tran_names_list = []
	tran_names_list.append("inv_level_shifter_1_nmos")
	tran_names_list.append("inv_level_shifter_1_pmos")
	tran_names_list.append("ptran_level_shifter_2_nmos")
	tran_names_list.append("ptran_level_shifter_3_pmos")


	return tran_names_list



# This is the sense amp design for MTJ memory array by kosuke
# All of the transistor sizes are fixed.
# This sense amp is designed for LP transistor. It should be redesigned to work for other technologies.
def generate_mtj_sa_lp(spice_filename, circuit_name): 

	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')

	# Create the circuit
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* " + circuit_name + " subcircuit MTJ sense amp \n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT " + circuit_name + "_sa n_inp n_inp_ref n_se1 n_se2 n_out n_vclamp n_vref n_reb n_ref n_vdd n_gnd\n")

	spice_file.write("M0 n_1_1 n_se1 n_vdd n_vdd pmos_lp_mtj L=22n W=300n ") 
	spice_file.write("AS=300n*trans_diffusion_length AD=300n*trans_diffusion_length PS=300n+2*trans_diffusion_length PD=300n+2*trans_diffusion_length\n")	
	spice_file.write("M1 n_1_2 n_se1 n_vdd n_vdd pmos_lp_mtj L=22n W=300n ")
	spice_file.write("AS=300n*trans_diffusion_length AD=300n*trans_diffusion_length PS=300n+2*trans_diffusion_length PD=300n+2*trans_diffusion_length\n")

	spice_file.write("X_invmtjsa_6 n_1_1 n_out n_vdd n_gnd inv_lp_mtj Wn=inv_mtj_subcircuits_mtjsa_6_nmos Wp=inv_mtj_subcircuits_mtjsa_6_pmos\n")
	spice_file.write("X_invmtjsa_6d n_1_2 n_out2 n_vdd n_gnd inv_lp_mtj Wn=inv_mtj_subcircuits_mtjsa_6_nmos Wp=inv_mtj_subcircuits_mtjsa_6_pmos\n")

	spice_file.write("M2 n_1_1 n_1_2 n_vdd n_vdd pmos_lp_mtj L=65n W=100n ") 
	spice_file.write("AS=100n*trans_diffusion_length AD=100n*trans_diffusion_length PS=100n+2*trans_diffusion_length PD=100n+2*trans_diffusion_length\n")	
	spice_file.write("M3 n_1_2 n_1_1 n_vdd n_vdd pmos_lp_mtj L=65n W=100n ")
	spice_file.write("AS=100n*trans_diffusion_length AD=100n*trans_diffusion_length PS=100n+2*trans_diffusion_length PD=100n+2*trans_diffusion_length\n")

	spice_file.write("M4 n_1_1 n_1_2 n_1_5 n_gnd nmos_lp_mtj L=65n W=800n ")
	spice_file.write("AS=800n*trans_diffusion_length AD=800n*trans_diffusion_length PS=800n+2*trans_diffusion_length PD=800n+2*trans_diffusion_length\n")	
	spice_file.write("M5 n_1_2 n_1_1 n_1_6 n_gnd nmos_lp_mtj L=65n W=800n ")
	spice_file.write("AS=800n*trans_diffusion_length AD=800n*trans_diffusion_length PS=800n+2*trans_diffusion_length PD=800m+2*trans_diffusion_length\n")	

	spice_file.write("M6 n_1_5 n_se2 n_gnd n_gnd nmos_lp_mtj L=65n W=250n ")
	spice_file.write("AS=250n*trans_diffusion_length AD=250n*trans_diffusion_length PS=250n+2*trans_diffusion_length PD=250n+2*trans_diffusion_length\n")	
	spice_file.write("M7 n_1_6 n_se2 n_gnd n_gnd nmos_lp_mtj L=65n W=250n ")
	spice_file.write("AS=250n*trans_diffusion_length AD=250n*trans_diffusion_length PS=250n+2*trans_diffusion_length PD=250n+2*trans_diffusion_length\n")

	spice_file.write("M8 n_1_5 n_vref n_1_7 n_gnd nmos_lp_mtj L=22n W=165n ")
	spice_file.write("AS=165n*trans_diffusion_length AD=165n*trans_diffusion_length PS=165n+2*trans_diffusion_length PD=165n+2*trans_diffusion_length\n")	
	spice_file.write("M9 n_1_6 n_vclamp n_1_8 n_gnd nmos_lp_mtj L=22n W=165n ")
	spice_file.write("AS=165n*trans_diffusion_length AD=165n*trans_diffusion_length PS=165n+2*trans_diffusion_length PD=165n+2*trans_diffusion_length\n")

	spice_file.write("M10 n_1_7 n_ref n_inp_ref n_gnd nmos_lp_mtj L=22n W=200n ")
	spice_file.write("AS=200n*trans_diffusion_length AD=200n*trans_diffusion_length PS=200n+2*trans_diffusion_length PD=200n+2*trans_diffusion_length\n")	
	spice_file.write("M11 n_1_8 n_ref n_inp n_gnd nmos_lp_mtj L=22n W=200n ")
	spice_file.write("AS=200n*trans_diffusion_length AD=200n*trans_diffusion_length PS=200n+2*trans_diffusion_length PD=200n+2*trans_diffusion_length\n")	
	spice_file.write("M12 n_1_7 n_reb n_inp n_gnd nmos_lp_mtj L=22n W=200n ")
	spice_file.write("AS=200n*trans_diffusion_length AD=200n*trans_diffusion_length PS=200n+2*trans_diffusion_length PD=200n+2*trans_diffusion_length\n")	
	spice_file.write("M13 n_1_8 n_reb n_inp_ref n_gnd nmos_lp_mtj L=22n W=200n\ ")
	spice_file.write("AS=200n*trans_diffusion_length AD=200n*trans_diffusion_length PS=200n+2*trans_diffusion_length PD=200n+2*trans_diffusion_length\n")	
	spice_file.write(".ENDS\n\n\n")

	spice_file.close()

	# There are no sizable transistors or wires in this circuit
	tran_names_list = []

	tran_names_list.append("ptran_mtj_subcircuits_mtjsa_1_pmos")
	tran_names_list.append("inv_mtj_subcircuits_mtjsa_2_nmos")
	tran_names_list.append("inv_mtj_subcircuits_mtjsa_2_pmos")
	tran_names_list.append("ptran_mtj_subcircuits_mtjsa_3_nmos")
	tran_names_list.append("ptran_mtj_subcircuits_mtjsa_4_nmos")
	tran_names_list.append("ptran_mtj_subcircuits_mtjsa_5_nmos")
	tran_names_list.append("inv_mtj_subcircuits_mtjsa_6_nmos")
	tran_names_list.append("inv_mtj_subcircuits_mtjsa_6_pmos")

	
	wire_names_list = []

	return tran_names_list, wire_names_list


# This is the MTJ-based memory write driver
def generate_mtj_writedriver_lp(spice_filename, circuit_name): 

	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')
	# This sense amp is designed for LP transistor. It should be redesigned to work for other technologies.
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* " + circuit_name + " subcircuit MTJ write driver \n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT " + circuit_name + "_writedriver n_in n_we n_out n_vneg n_vdd n_gnd\n")

	spice_file.write("M0 n_1_1 n_we_b n_vdd n_vdd pmos_lp_mtj L=22n W=600n ") 
	spice_file.write("AS=600n*trans_diffusion_length AD=600n*trans_diffusion_length PS=600n+2*trans_diffusion_length PD=600n+2*trans_diffusion_length\n")	
	spice_file.write("M1 n_out n_in n_1_1 n_vdd pmos_lp_mtj L=22n W=600n ")
	spice_file.write("AS=600n*trans_diffusion_length AD=600n*trans_diffusion_length PS=600n+2*trans_diffusion_length PD=600n+2*trans_diffusion_length\n")	
	spice_file.write("M2 n_out n_in n_1_2 n_gnd nmos_lp_mtj L=22n W=600n ") 
	spice_file.write("AS=600n*trans_diffusion_length AD=600n*trans_diffusion_length PS=600n+2*trans_diffusion_length PD=600n+2*trans_diffusion_length\n")	
	spice_file.write("M3 n_1_2 n_we n_vneg n_gnd nmos_lp_mtj L=22n W=600n ")
	spice_file.write("AS=600n*trans_diffusion_length AD=600n*trans_diffusion_length PS=600n+2*trans_diffusion_length PD=600n+2*trans_diffusion_length\n")	
	spice_file.write("X_inv" + circuit_name + "_1 n_we n_we_b n_vdd n_gnd inv_lp_mtj Wn=45n Wp=90n\n")

	spice_file.write(".ENDS\n\n\n")

	spice_file.close()

	# Create a list of transistors
	tran_names_list = []
	tran_names_list.append("inv_mtj_subcircuits_mtjwd_1_nmos")
	tran_names_list.append("inv_mtj_subcircuits_mtjwd_1_pmos")
	tran_names_list.append("inv_mtj_subcircuits_mtjwd_2_nmos")
	tran_names_list.append("inv_mtj_subcircuits_mtjwd_2_nmos")

	tran_names_list.append("inv_mtj_subcircuits_mtjwd_3_nmos")
	tran_names_list.append("inv_mtj_subcircuits_mtjwd_3_nmos")


	wire_names_list = []

	return tran_names_list, wire_names_list


# This is the column selector in MTJ-based BRAMs
def generate_mtj_cs_lp(spice_filename, circuit_name): 

	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')

	spice_file.write("******************************************************************************************\n")
	spice_file.write("* " + circuit_name + " subcircuit MTJ coulmn selector and pull down \n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT " + circuit_name + "_cs n_in n_out n_ctrl n_ctrl_b n_vdd n_gnd\n")
	spice_file.write("M0 n_in n_ctrl n_out n_vdd pmos_lp_mtj L=22n W=600n ")
	spice_file.write("AS=600n*trans_diffusion_length AD=600n*trans_diffusion_length PS=600n+2*trans_diffusion_length PD=600n+2*trans_diffusion_length\n")	
	spice_file.write("M1 n_out n_ctrl_b n_in n_gnd nmos_lp_mtj L=22n W=600n ") 
	spice_file.write("AS=600n*trans_diffusion_length AD=600n*trans_diffusion_length PS=600n+2*trans_diffusion_length PD=600n+2*trans_diffusion_length\n")	
	spice_file.write("M2 n_out n_ctrl n_gnd n_gnd nmos_lp_mtj L=22n W=ptran_mtj_subcircuits_mtjcs_0_nmos ")
	spice_file.write("AS=ptran_mtj_subcircuits_mtjcs_0_nmos*trans_diffusion_length AD=ptran_mtj_subcircuits_mtjcs_0_nmos*trans_diffusion_length PS=ptran_mtj_subcircuits_mtjcs_0_nmos+2*trans_diffusion_length PD=ptran_mtj_subcircuits_mtjcs_0_nmos+2*trans_diffusion_length\n")	

	spice_file.write(".ENDS\n\n\n")

	spice_file.close()

	# Create a list of transistors
	tran_names_list = []

	tran_names_list.append("tgate_mtj_subcircuits_mtjcs_1_nmos")
	tran_names_list.append("tgate_mtj_subcircuits_mtjcs_1_pmos")


	wire_names_list = []

	return tran_names_list, wire_names_list

"""
The following components are MTJ and SRAM-based memory cells
These cells are not automatically sized and require precise sizing by the user.
"""
# MTJ cell using the high resistance
def generate_mtj_memorycell_high_lp(spice_filename, circuit_name): 

	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')
	# Generate netlist
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* " + circuit_name + " subcircuit MTJ coulmn selector and pull down \n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT mtjhigh n_wl1 n_wl2 n_bl1 n_bl2  n_vdd n_gnd\n")

	spice_file.write("M0 n_bl1 n_wl1 n_1_1 n_gnd nmos_lp_mtj L=22n W=165n ")
	spice_file.write("AS=6.6f AD=6.6f PS=245n PD=245n\n")	
	spice_file.write("M1 n_bl2 n_wl2 n_1_1 n_gnd nmos_lp_mtj L=22n W=165n ")
	spice_file.write("AS=6.6f AD=6.6f PS=245n PD=245n\n")
	spice_file.write("Rmtj n_1_1 n_gnd 'mtj_worst_high'\n")

	spice_file.write(".ENDS\n\n\n")

	spice_file.close()

	tran_names_list = []
	wire_names_list = []

	return tran_names_list, wire_names_list

# MTJ cell using the low resistance
def generate_mtj_memorycell_low_lp(spice_filename, circuit_name): 

	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')

	spice_file.write("******************************************************************************************\n")
	spice_file.write("* " + circuit_name + " subcircuit MTJ coulmn selector and pull down \n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT mtjlow n_wl1 n_wl2 n_bl1 n_bl2  n_vdd n_gnd\n")

	spice_file.write("M0 n_bl1 n_wl1 n_1_1 n_gnd nmos_lp_mtj L=22n W=165n ") 
	spice_file.write("AS=6.6f AD=6.6f PS=245n PD=245n\n")
	spice_file.write("M1 n_bl2 n_wl2 n_1_1 n_gnd nmos_lp_mtj L=22n W=165n ")
	spice_file.write("AS=6.6f AD=6.6f PS=245n PD=245n\n")	
	spice_file.write("Rmtj n_1_1 n_gnd 'mtj_worst_low' \n")

	spice_file.write(".ENDS\n\n\n")

	spice_file.close()

	tran_names_list = []
	wire_names_list = []

	return tran_names_list, wire_names_list

# MTJ cell using the refence resistance
def generate_mtj_memorycell_reference_lp(spice_filename, circuit_name): 

	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')

	spice_file.write("******************************************************************************************\n")
	spice_file.write("* " + circuit_name + " subcircuit MTJ coulmn selector and pull down \n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT " + circuit_name + " n_wl1 n_wl2 n_bl1 n_bl2 n_dummy1 n_dummy2 n_vdd n_gnd\n")

	spice_file.write("M0 n_bl1 n_wl1 n_1_1 n_gnd nmos_lp_mtj L=22n W=165n ") 
	spice_file.write("AS=6.6f AD=6.6f PS=245n PD=245n\n")
	spice_file.write("M1 n_bl2 n_wl2 n_1_1 n_gnd nmos_lp_mtj L=22n W=165n ")
	spice_file.write("AS=6.6f AD=6.6f PS=245n PD=245n\n")	
	spice_file.write("Rmtj n_1_1 n_gnd 'mtj_nominal_low' \n")

	spice_file.write(".ENDS\n\n\n")

	spice_file.close()

	tran_names_list = []
	wire_names_list = []

	return tran_names_list, wire_names_list

# MTJ cell using the refence resistance
def generate_mtj_memorycellh_reference_lp(spice_filename, circuit_name): 

	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')

	spice_file.write("******************************************************************************************\n")
	spice_file.write("* " + circuit_name + " subcircuit MTJ coulmn selector and pull down \n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT " + circuit_name + "h n_wl1 n_wl2 n_bl1 n_bl2 n_dummy1 n_dummy2 n_vdd n_gnd\n")

	spice_file.write("M0 n_bl1 n_wl1 n_1_1 n_gnd nmos_lp_mtj L=22n W=165n ") 
	spice_file.write("AS=6.6f AD=6.6f PS=245n PD=245n\n")
	spice_file.write("M1 n_bl2 n_wl2 n_1_1 n_gnd nmos_lp_mtj L=22n W=165n ")
	spice_file.write("AS=6.6f AD=6.6f PS=245n PD=245n\n")	
	spice_file.write("Rmtj n_1_1 n_gnd 'mtj_nominal_high' \n")

	spice_file.write(".ENDS\n\n\n")

	spice_file.close()

	tran_names_list = []
	wire_names_list = []

	return tran_names_list, wire_names_list

# MTJ cell using the refence resistance
def generate_mtj_memorycell_reference_lp_target(spice_filename, circuit_name): 

	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')

	spice_file.write("******************************************************************************************\n")
	spice_file.write("* " + circuit_name + " subcircuit MTJ memory cell \n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT memory_cell_ref n_wl1 n_wl2 n_bl1 n_bl2 n_dummy1 n_dummy2 n_vdd n_gnd\n")

	spice_file.write("M0 n_bl1 n_wl1 n_1_1 n_gnd nmos_lp_mtj L=22n W=165n ") 
	spice_file.write("AS=6.6f AD=6.6f PS=245n PD=245n\n")
	spice_file.write("M1 n_bl2 n_wl2 n_1_1 n_gnd nmos_lp_mtj L=22n W=165n ")
	spice_file.write("AS=6.6f AD=6.6f PS=245n PD=245n\n")	
	spice_file.write("Rmtj n_1_1 n_gnd 2118 \n")

	spice_file.write(".ENDS\n\n\n")

	spice_file.close()

	tran_names_list = []
	wire_names_list = []

	return tran_names_list, wire_names_list


# Memory cell:
def generate_memorycell(spice_filename, circuit_name):

	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')
	# currently only works for 22nm
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* " + circuit_name + " subcircuit memory sram cell \n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT " + circuit_name + " n_wl1 n_wl2 n_bl1 n_bl2 n_br1 n_br2 n_vdd n_gnd\n")
	spice_file.write("M1 n_1_1 n_1_2 n_gnd n_gnd nmos L=22n W=115n AD=6.9f PD=295n AS=4.6f PS=195n\n") #PD
	spice_file.write("M0 n_1_2 n_1_1 n_gnd n_gnd nmos L=22n W=115n AD=6.9f PD=295n AS=4.6f PS=195n\n") #PD 

	spice_file.write("M3 n_1_1 n_1_2 n_vdd n_vdd pmos L=22n W=45n AD=2.7f PD=210n AS=1.8f PS=125n\n") #PU
	spice_file.write("M2 n_1_2 n_1_1 n_vdd n_vdd pmos L=22n W=45n AD=2.7f PD=210n AS=1.8f PS=125n\n") #PU

	spice_file.write("M4 n_bl1 n_wl1 n_1_2 n_gnd nmos L=22n W=55n AD=2.2f PD=135n AS=3.3f PS=230n\n") #PG
	spice_file.write("M5 n_br1 n_wl1 n_1_1 n_gnd nmos L=22n W=55n AD=2.2f PD=135n AS=1.1f PS=40n\n") #PG
	spice_file.write("M6 n_bl2 n_wl2 n_1_1 n_gnd nmos L=22n W=55n AD=2.2f PD=135n AS=3.3f PS=230n\n") #PG
	spice_file.write("M7 n_br2 n_wl2 n_1_2 n_gnd nmos L=22n W=55n AD=2.2f PD=135n AS=1.1f PS=40n\n") #PG

	spice_file.write(".ENDS\n\n\n")

	spice_file.close()

	tran_names_list = []
	wire_names_list = []

	return tran_names_list, wire_names_list


# Memory cell:
def generate_memorycell_lp(spice_filename, circuit_name):

	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')
	# currently only works for 22nm
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* " + circuit_name + " subcircuit low power memory sram cell \n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT " + circuit_name + " n_wl1 n_wl2 n_bl1 n_bl2 n_br1 n_br2 n_vdd n_gnd\n")
	spice_file.write("M1 n_1_1 n_1_2 n_gnd n_gnd nmos_lp L=22n W=115n AD=6.9f PD=295n AS=4.6f PS=195n\n") #PD
	spice_file.write("M0 n_1_2 n_1_1 n_gnd n_gnd nmos_lp L=22n W=115n AD=6.9f PD=295n AS=4.6f PS=195n\n") #PD 

	spice_file.write("M3 n_1_1 n_1_2 n_vdd n_vdd pmos_lp L=22n W=45n AD=2.7f PD=210n AS=1.8f PS=125n\n") #PU
	spice_file.write("M2 n_1_2 n_1_1 n_vdd n_vdd pmos_lp L=22n W=45n AD=2.7f PD=210n AS=1.8f PS=125n\n") #PU

	spice_file.write("M4 n_bl1 n_wl1 n_1_2 n_gnd nmos_lp L=22n W=55n AD=2.2f PD=135n AS=3.3f PS=230n\n") #PG
	spice_file.write("M5 n_br1 n_wl1 n_1_1 n_gnd nmos_lp L=22n W=55n AD=2.2f PD=135n AS=1.1f PS=40n\n") #PG
	spice_file.write("M6 n_bl2 n_wl2 n_1_1 n_gnd nmos_lp L=22n W=55n AD=2.2f PD=135n AS=3.3f PS=230n\n") #PG
	spice_file.write("M7 n_br2 n_wl2 n_1_2 n_gnd nmos_lp L=22n W=55n AD=2.2f PD=135n AS=1.1f PS=40n\n") #PG
	spice_file.write(".ENDS\n\n\n")

	spice_file.close()

	tran_names_list = []
	wire_names_list = []

	return tran_names_list, wire_names_list

# This is the sense amplifier for SRAM-based memories
# This circuit is not automatically sized and requires precicse sizing by the user
def generate_samp(spice_filename, circuit_name):

	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')
	# currently only works for 22nm and sizes are pre-determined.
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* " + circuit_name + " subcircuit sense amp \n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT " + circuit_name + " n_se n_in1 n_in2 n_out n_vdd n_gnd \n")


	spice_file.write("M1 n_in1 n_se n_1_1 n_vdd pmos L=32n W=250n ")
	spice_file.write("AS=250n*trans_diffusion_length AD=250n*trans_diffusion_length PS=250n+2*trans_diffusion_length PD=250n+2*trans_diffusion_length\n")	
	spice_file.write("M0 n_1_1 n_1_2 n_vdd n_vdd pmos L=65n W=100n ")
	spice_file.write("AS=100n*trans_diffusion_length AD=100n*trans_diffusion_length PS=100n+2*trans_diffusion_length PD=100n+2*trans_diffusion_length\n")	
	spice_file.write("M2 n_1_2 n_1_1 n_vdd  n_vdd pmos L=65n W=100n ")
	spice_file.write("AS=100n*trans_diffusion_length AD=100n*trans_diffusion_length PS=100n+2*trans_diffusion_length PD=100n+2*trans_diffusion_length\n")
	spice_file.write("M3 n_in2 n_se n_1_2 n_vdd pmos L=32n W=250n ")
	spice_file.write("AS=250n*trans_diffusion_length AD=250n*trans_diffusion_length PS=250n+2*trans_diffusion_length PD=250n+2*trans_diffusion_length\n")	
	spice_file.write("M4 n_1_1 n_1_2 n_gnd2 n_gnd nmos L=65n W=900n ")
	spice_file.write("AS=900n*trans_diffusion_length AD=900n*trans_diffusion_length PS=900n+2*trans_diffusion_length PD=900n+2*trans_diffusion_length\n")	
	spice_file.write("M5 n_1_2 n_1_1 n_gnd2 n_gnd nmos L=65n W=900n ")
	spice_file.write("AS=900n*trans_diffusion_length AD=900n*trans_diffusion_length PS=900n+2*trans_diffusion_length PD=900n+2*trans_diffusion_length\n")	
	spice_file.write("M6 n_gnd2 n_se n_gnd n_gnd nmos L=65n W=250n ")
	spice_file.write("AS=250n*trans_diffusion_length AD=250n*trans_diffusion_length PS=250n+2*trans_diffusion_length PD=250n+2*trans_diffusion_length\n")	

	spice_file.write("X_inv" + circuit_name + "_1 n_1_1 n_hang n_vdd n_gnd inv Wn=min_tran_width Wp=min_tran_width\n")
	spice_file.write("X_inv" + circuit_name + "_2 n_1_2 n_out n_vdd n_gnd inv Wn=min_tran_width Wp=min_tran_width\n")

	spice_file.write(".ENDS\n\n\n")
	spice_file.close()	
	tran_names_list = []
	wire_names_list = []

	return tran_names_list, wire_names_list


# This is the sense amplifier for SRAM-based memories
# This circuit is not automatically sized and requires precicse sizing by the user
def generate_samp_lp(spice_filename, circuit_name):

	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')
	# currently only works for 22nm

	spice_file.write("******************************************************************************************\n")
	spice_file.write("* " + circuit_name + " subcircuit sense amp \n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT " + circuit_name + " n_se n_in1 n_in2 n_out n_vdd n_gnd \n")

	spice_file.write("M1 n_in1 n_se n_1_1 n_vdd pmos_lp L=32n W=250n ")
	spice_file.write("AS=250n*trans_diffusion_length AD=250n*trans_diffusion_length PS=250n+2*trans_diffusion_length PD=250n+2*trans_diffusion_length\n")	
	spice_file.write("M0 n_1_1 n_1_2 n_vdd n_vdd pmos_lp L=65n W=100n ")
	spice_file.write("AS=100n*trans_diffusion_length AD=100n*trans_diffusion_length PS=100n+2*trans_diffusion_length PD=100n+2*trans_diffusion_length\n")	
	spice_file.write("M2 n_1_2 n_1_1 n_vdd  n_vdd pmos_lp L=65n W=100n ")
	spice_file.write("AS=100n*trans_diffusion_length AD=100n*trans_diffusion_length PS=100n+2*trans_diffusion_length PD=100n+2*trans_diffusion_length\n")	
	spice_file.write("M3 n_in2 n_se n_1_2 n_vdd pmos_lp L=32n W=250n ")
	spice_file.write("AS=250n*trans_diffusion_length AD=250n*trans_diffusion_length PS=250n+2*trans_diffusion_length PD=250n+2*trans_diffusion_length\n")	
	spice_file.write("M4 n_1_1 n_1_2 n_gnd2 n_gnd nmos_lp L=65n W=900n ")
	spice_file.write("AS=900n*trans_diffusion_length AD=900n*trans_diffusion_length PS=900n+2*trans_diffusion_length PD=900n+2*trans_diffusion_length\n")
	spice_file.write("M5 n_1_2 n_1_1 n_gnd2 n_gnd nmos_lp L=65n W=900n ")
	spice_file.write("AS=900n*trans_diffusion_length AD=900n*trans_diffusion_length PS=900n+2*trans_diffusion_length PD=900n+2*trans_diffusion_length\n")
	spice_file.write("M6 n_gnd2 n_se n_gnd n_gnd nmos_lp L=65n W=250n ")
	spice_file.write("AS=250n*trans_diffusion_length AD=250n*trans_diffusion_length PS=250n+2*trans_diffusion_length PD=250n+2*trans_diffusion_length\n")	
	#add the two inverters
	#spice_file.write("X_inv" + circuit_name + "_1 n_1_1 n_hang n_vdd n_gnd inv Wn=inv_samp_output_1_nmos Wp=inv_samp_output_1_pmos\n")
	#spice_file.write("X_inv" + circuit_name + "_2 n_1_2 n_out n_vdd n_gnd inv Wn=inv_samp_output_1_nmos Wp=inv_samp_output_1_pmos\n")
	spice_file.write("X_inv" + circuit_name + "_1 n_1_1 n_hang n_vdd n_gnd inv_lp Wn=min_tran_width Wp=min_tran_width\n")
	spice_file.write("X_inv" + circuit_name + "_2 n_1_2 n_out n_vdd n_gnd inv_lp Wn=min_tran_width Wp=min_tran_width\n")

	spice_file.write(".ENDS\n\n\n")
	spice_file.close()	
	tran_names_list = []
	wire_names_list = []

	return tran_names_list, wire_names_list

# This is the column decoder used in memory
def generate_columndecoder(spice_filename, circuit_name, decsize):

	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')
	# currently only works for 22nm

	spice_file.write("******************************************************************************************\n")
	spice_file.write("* " + circuit_name + " subcircuit write driver \n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT " + circuit_name + " n_in n_out n_vdd n_gnd\n")

	if decsize == 1:
		spice_file.write("X_inv_columndecoder_1 n_in n_1_1 n_vdd n_gnd inv Wn=inv_columndecoder_1_nmos Wp=inv_columndecoder_1_pmos\n")
		spice_file.write("X_inv_columndecoder_2 n_1_1 n_1_2 n_vdd n_gnd inv Wn=inv_columndecoder_2_nmos Wp=inv_columndecoder_2_pmos\n")
		spice_file.write("X_inv_columndecoder_3 n_1_2 n_out n_vdd n_gnd inv Wn=inv_columndecoder_3_nmos Wp=inv_columndecoder_3_pmos\n")
	if decsize == 2:
		spice_file.write("X_inv_columndecoder_1 n_in n_1_1 n_vdd n_gnd inv Wn=inv_columndecoder_1_nmos Wp=inv_columndecoder_1_pmos\n")
		spice_file.write("X_inv_columndecoder_2 n_1_1 n_1_2 n_vdd n_gnd nand2 Wn=inv_columndecoder_2_nmos Wp=inv_columndecoder_2_pmos\n")
		spice_file.write("X_inv_columndecoder_3 n_1_2 n_out n_vdd n_gnd inv Wn=inv_columndecoder_3_nmos Wp=inv_columndecoder_3_pmos\n")
	if decsize == 3:
		spice_file.write("X_inv_columndecoder_1 n_in n_1_1 n_vdd n_gnd inv Wn=inv_columndecoder_1_nmos Wp=inv_columndecoder_1_pmos\n")
		spice_file.write("X_inv_columndecoder_2 n_1_1 n_1_2 n_vdd n_gnd nand3 Wn=inv_columndecoder_2_nmos Wp=inv_columndecoder_2_pmos\n")
		spice_file.write("X_inv_columndecoder_3 n_1_2 n_out n_vdd n_gnd inv Wn=inv_columndecoder_3_nmos Wp=inv_columndecoder_3_pmos\n")

	spice_file.write(".ENDS\n\n\n")
	spice_file.close()	
	tran_names_list = []
	# wont be sizing the inveters, chooising minimum size
	tran_names_list.append("inv_columndecoder_1_nmos")
	tran_names_list.append("inv_columndecoder_1_pmos")
	tran_names_list.append("inv_columndecoder_2_nmos")
	tran_names_list.append("inv_columndecoder_2_pmos")
	tran_names_list.append("inv_columndecoder_3_nmos")
	tran_names_list.append("inv_columndecoder_3_pmos")

	wire_names_list = []

	return tran_names_list, wire_names_list

# This is the column decoder used in memory
def generate_columndecoder_lp(spice_filename, circuit_name, decsize):

	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')
	# currently only works for 22nm

	spice_file.write("******************************************************************************************\n")
	spice_file.write("* " + circuit_name + " subcircuit write driver \n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT " + circuit_name + " n_in n_out n_vdd n_gnd\n")

	if decsize == 1:
		spice_file.write("X_inv_columndecoder_1 n_in n_1_1 n_vdd n_gnd inv_lp Wn=inv_columndecoder_1_nmos Wp=inv_columndecoder_1_pmos\n")
		spice_file.write("X_inv_columndecoder_2 n_1_1 n_1_2 n_vdd n_gnd inv_lp Wn=inv_columndecoder_2_nmos Wp=inv_columndecoder_2_pmos\n")
		spice_file.write("X_inv_columndecoder_3 n_1_2 n_out n_vdd n_gnd inv_lp Wn=inv_columndecoder_3_nmos Wp=inv_columndecoder_3_pmos\n")
	if decsize == 2:
		spice_file.write("X_inv_columndecoder_1 n_in n_1_1 n_vdd n_gnd inv_lp Wn=inv_columndecoder_1_nmos Wp=inv_columndecoder_1_pmos\n")
		spice_file.write("X_inv_columndecoder_2 n_1_1 n_1_2 n_vdd n_gnd nand2_lp Wn=inv_columndecoder_2_nmos Wp=inv_columndecoder_2_pmos\n")
		spice_file.write("X_inv_columndecoder_3 n_1_2 n_out n_vdd n_gnd inv_lp Wn=inv_columndecoder_3_nmos Wp=inv_columndecoder_3_pmos\n")
	if decsize == 3:
		spice_file.write("X_inv_columndecoder_1 n_in n_1_1 n_vdd n_gnd inv_lp Wn=inv_columndecoder_1_nmos Wp=inv_columndecoder_1_pmos\n")
		spice_file.write("X_inv_columndecoder_2 n_1_1 n_1_2 n_vdd n_gnd nand3_lp Wn=inv_columndecoder_2_nmos Wp=inv_columndecoder_2_pmos\n")
		spice_file.write("X_inv_columndecoder_3 n_1_2 n_out n_vdd n_gnd inv_lp Wn=inv_columndecoder_3_nmos Wp=inv_columndecoder_3_pmos\n")

	spice_file.write(".ENDS\n\n\n")
	spice_file.close()	
	tran_names_list = []
	# wont be sizing the inveters, chooising minimum size
	tran_names_list.append("inv_columndecoder_1_nmos")
	tran_names_list.append("inv_columndecoder_1_pmos")
	tran_names_list.append("inv_columndecoder_2_nmos")
	tran_names_list.append("inv_columndecoder_2_pmos")
	tran_names_list.append("inv_columndecoder_3_nmos")
	tran_names_list.append("inv_columndecoder_3_pmos")

	wire_names_list = []

	return tran_names_list, wire_names_list


# This is the output crossbar
def generate_pgateoutputcrossbar(spice_filename, circuit_name, maxwidth, def_use_tgate):

	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')
	# currently only works for 22nm

	spice_file.write("******************************************************************************************\n")
	spice_file.write("* " + circuit_name + " subcircuit pgate output crossbar \n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT " + circuit_name + " n_in n_out n_vdd n_sram_v n_gnd\n")

	spice_file.write("X_inv_pgateoutputcrossbar_1 n_in n_1_1 n_vdd n_gnd inv Wn=inv_pgateoutputcrossbar_1_nmos Wp=inv_pgateoutputcrossbar_1_pmos\n")
	spice_file.write("X_inv_pgateoutputcrossbar_2 n_1_1 n_1_2 n_vdd n_gnd inv Wn=inv_pgateoutputcrossbar_2_nmos Wp=inv_pgateoutputcrossbar_2_pmos\n")

	# TODO: figure out if TGATE is better or using a tristate buffer
	if def_use_tgate == 1:
		spice_file.write("X_tgate n_1_2 n_0_0 n_vdd n_gnd n_vdd n_gnd RAM_tgate Wn=tgate_pgateoutputcrossbar_3_nmos Wp=tgate_pgateoutputcrossbar_3_pmos\n")
	# Replacing this TGATE with a tri-state buffer to improve the output crossbar
	else:
		spice_file.write("M0 n_t_up n_gnd n_vdd n_vdd pmos L=22n W=inv_pgateoutputcrossbar_3_pmos ")
		spice_file.write("AS=inv_pgateoutputcrossbar_3_pmos*trans_diffusion_length AD=inv_pgateoutputcrossbar_3_pmos*trans_diffusion_length PS=inv_pgateoutputcrossbar_3_pmos+2*trans_diffusion_length PD=inv_pgateoutputcrossbar_3_pmos+2*trans_diffusion_length\n")
		spice_file.write("M1 n_0_0 n_1_2 n_t_up n_vdd pmos L=22n W=inv_pgateoutputcrossbar_3_pmos ")
		spice_file.write("AS=inv_pgateoutputcrossbar_3_pmos*trans_diffusion_length AD=inv_pgateoutputcrossbar_3_pmos*trans_diffusion_length PS=inv_pgateoutputcrossbar_3_pmos+2*trans_diffusion_length PD=inv_pgateoutputcrossbar_3_pmos+2*trans_diffusion_length\n")
		spice_file.write("M2 n_0_0 n_1_2 n_t_bot  n_gnd nmos L=22n W=inv_pgateoutputcrossbar_3_nmos ")
		spice_file.write("AS=inv_pgateoutputcrossbar_3_nmos*trans_diffusion_length AD=inv_pgateoutputcrossbar_3_nmos*trans_diffusion_length PS=inv_pgateoutputcrossbar_3_nmos+2*trans_diffusion_length PD=inv_pgateoutputcrossbar_3_nmos+2*trans_diffusion_length\n")
		spice_file.write("M3 n_t_bot n_vdd n_gnd n_gnd nmos L=22n W=inv_pgateoutputcrossbar_3_nmos ")
		spice_file.write("AS=inv_pgateoutputcrossbar_3_nmos*trans_diffusion_length AD=inv_pgateoutputcrossbar_3_nmos*trans_diffusion_length PS=inv_pgateoutputcrossbar_3_nmos+2*trans_diffusion_length PD=inv_pgateoutputcrossbar_3_nmos+2*trans_diffusion_length\n")
	
	# There is a wire with logn of pass transistors connected to it. I'll keep it simple
	spice_file.write("X_wire_0_0 n_0_0 n_0_1 wire Rw=wire_"+circuit_name+"_res/2 Cw=wire_"+circuit_name+"_cap/2 \n")
	for i in range(0, int(math.log(maxwidth, 2))):
		spice_file.write("X_ptran_0_"+str(i+1)+" n_0_1 n_hang_nbd n_gnd n_gnd ptran Wn=ptran_pgateoutputcrossbar_4_nmos \n")
	spice_file.write("X_wire_0_1 n_0_1 n_1_3 wire Rw=wire_"+circuit_name+"_res/2 Cw=wire_"+circuit_name+"_cap/2 \n")

	spice_file.write("X_ptran_0 n_1_3 n_1_4 n_sram_v n_gnd ptran Wn=ptran_pgateoutputcrossbar_4_nmos \n")
	spice_file.write("X_wire_out n_1_4 n_out wire Rw=wire_"+circuit_name+"_res Cw=wire_"+circuit_name+"_cap \n")
	spice_file.write("X_wire_0 n_1_4 n_1_5 wire Rw=wire_"+circuit_name+"_res/"+str(maxwidth)+" Cw=wire_"+circuit_name+"_cap/"+str(maxwidth)+" \n")
	# there are two ports in the RAM block, hence the multiplication
	for i in range(1, 2 * maxwidth -1):
		spice_file.write("X_tgate"+str(i)+" n_x_"+str(i)+" n_hang_"+str(i)+" n_gnd n_vdd n_vdd n_gnd RAM_tgate\n")
		spice_file.write("X_ptran_"+str(i)+" n_hang_"+str(i)+" n_1_"+str(i+4)+" n_gnd n_gnd ptran Wn=ptran_pgateoutputcrossbar_4_nmos\n")
		spice_file.write("X_wire_"+str(i)+" n_1_"+str(i+4)+" n_1_"+str(i+5)+" wire Rw=wire_"+circuit_name+"_res/"+str(maxwidth)+" Cw=wire_"+circuit_name+"_cap/"+str(maxwidth)+"\n")
	
	spice_file.write("X_tgate"+str(2 *maxwidth-1)+" n_x_"+str(2 *maxwidth-1)+" n_hang_"+str(2 *maxwidth-1)+" n_gnd n_vdd n_vdd n_gnd RAM_tgate\n")
	spice_file.write("X_ptran_"+str(2 *maxwidth-1)+" n_hang_"+str(2 *maxwidth-1)+" n_1_"+str(2 *maxwidth+3)+" n_gnd n_gnd ptran Wn=ptran_pgateoutputcrossbar_4_nmos\n")
	spice_file.write("X_wire_"+str(2 *maxwidth-1)+" n_1_"+str(2 * maxwidth+3)+" n_1_"+str(2 * maxwidth+4)+" wire Rw=wire_"+circuit_name+"_res/"+str(maxwidth)+" Cw=wire_"+circuit_name+"_cap/"+str(maxwidth)+"\n")

	# This part is the best case power consumption to average power:
	spice_file.write("X_inv_pgateoutputcrossbarp_1 n_in n_2_1 n_vdd n_gnd inv Wn=inv_pgateoutputcrossbar_1_nmos Wp=inv_pgateoutputcrossbar_1_pmos\n")
	spice_file.write("X_inv_pgateoutputcrossbarp_2 n_2_1 n_2_2 n_vdd n_gnd inv Wn=inv_pgateoutputcrossbar_2_nmos Wp=inv_pgateoutputcrossbar_2_pmos\n")

	if def_use_tgate == 1:
		spice_file.write("X_2tgate n_2_2 n_20_0 n_vdd n_gnd n_vdd n_gnd RAM_tgate Wn=tgate_pgateoutputcrossbar_3_nmos Wp=tgate_pgateoutputcrossbar_3_pmos\n")
	#replacing this TGATE with a tri-state buffer to improve the output crossbar
	else:
		spice_file.write("M02 n_2t_up n_gnd n_vdd n_vdd pmos L=22n W=inv_pgateoutputcrossbar_3_pmos ")
		spice_file.write("AS=inv_pgateoutputcrossbar_3_pmos*trans_diffusion_length AD=inv_pgateoutputcrossbar_3_pmos*trans_diffusion_length PS=inv_pgateoutputcrossbar_3_pmos+2*trans_diffusion_length PD=inv_pgateoutputcrossbar_3_pmos+2*trans_diffusion_length\n")
		spice_file.write("M12 n_20_0 n_2_2 n_2t_up n_vdd pmos L=22n W=inv_pgateoutputcrossbar_3_pmos ")
		spice_file.write("AS=inv_pgateoutputcrossbar_3_pmos*trans_diffusion_length AD=inv_pgateoutputcrossbar_3_pmos*trans_diffusion_length PS=inv_pgateoutputcrossbar_3_pmos+2*trans_diffusion_length PD=inv_pgateoutputcrossbar_3_pmos+2*trans_diffusion_length\n")
		spice_file.write("M22 n_20_0 n_2_2 n_2t_bot  n_gnd nmos L=22n W=inv_pgateoutputcrossbar_3_nmos ")
		spice_file.write("AS=inv_pgateoutputcrossbar_3_nmos*trans_diffusion_length AD=inv_pgateoutputcrossbar_3_nmos*trans_diffusion_length PS=inv_pgateoutputcrossbar_3_nmos+2*trans_diffusion_length PD=inv_pgateoutputcrossbar_3_nmos+2*trans_diffusion_length\n")
		spice_file.write("M32 n_2t_bot n_vdd n_gnd n_gnd nmos L=22n W=inv_pgateoutputcrossbar_3_nmos ")
		spice_file.write("AS=inv_pgateoutputcrossbar_3_nmos*trans_diffusion_length AD=inv_pgateoutputcrossbar_3_nmos*trans_diffusion_length PS=inv_pgateoutputcrossbar_3_nmos+2*trans_diffusion_length PD=inv_pgateoutputcrossbar_3_nmos+2*trans_diffusion_length\n")
	
	# There is a wire with logn of pass transistors connected to it. I'll keep it simple
	spice_file.write("X_wire2_0_0 n_20_0 n_hang wire Rw=wire_"+circuit_name+"_res Cw=wire_"+circuit_name+"_cap \n")

	spice_file.write(".ENDS\n\n\n")
	spice_file.close()	
	tran_names_list = []
	tran_names_list.append("inv_pgateoutputcrossbar_1_nmos")
	tran_names_list.append("inv_pgateoutputcrossbar_1_pmos")
	tran_names_list.append("inv_pgateoutputcrossbar_2_nmos")
	tran_names_list.append("inv_pgateoutputcrossbar_2_pmos")
	if def_use_tgate == 1:
		tran_names_list.append("tgate_pgateoutputcrossbar_3_nmos")
		tran_names_list.append("tgate_pgateoutputcrossbar_3_pmos")
	else:
		tran_names_list.append("inv_pgateoutputcrossbar_3_nmos")
		tran_names_list.append("inv_pgateoutputcrossbar_3_pmos")
	tran_names_list.append("ptran_pgateoutputcrossbar_4_nmos")


	wire_names_list = []

	return tran_names_list, wire_names_list


# This is the write driver
# The part which is commented out can be restored (you need to comment those below it) to enable sizing of this module
# It is however expected that write driver not be in the critical path of SRAM-based BRAm and therefore sizing it will just increase COFEE's runtime.
def generate_writedriver(spice_filename, circuit_name):

	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')
	# currently only works for 22nm

	spice_file.write("******************************************************************************************\n")
	spice_file.write("* " + circuit_name + " subcircuit write driver \n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT " + circuit_name + " n_we n_din n_bl n_br n_vdd n_gnd\n")

	#spice_file.write("M1 p_1_1 n_web n_vdd n_vdd pmos L=gate_length W=tgate_writedriver_3_pmos\n")
	#spice_file.write("M0 p_1_2 n_web n_vdd n_vdd pmos L=gate_length W=tgate_writedriver_3_pmos\n")
	#spice_file.write("M2 n_bl n_din p_1_1  n_vdd pmos L=gate_length W=tgate_writedriver_3_pmos\n")
	#spice_file.write("M3 n_br n_dinb p_1_2 n_vdd pmos L=gate_length W=tgate_writedriver_3_pmos\n")

	#spice_file.write("M4 n_1_1 n_we n_gnd n_gnd nmos L=gate_length W=tgate_writedriver_3_nmos\n")
	#spice_file.write("M5 n_1_2 n_we n_gnd n_gnd nmos L=gate_length W=tgate_writedriver_3_nmos\n")
	#spice_file.write("M6 n_bl n_din n_1_1 n_gnd nmos L=gate_length W=tgate_writedriver_3_nmos\n")
	#spice_file.write("M7 n_br n_dinb n_1_2 n_gnd nmos L=gate_length W=tgate_writedriver_3_nmos\n")

	spice_file.write("M1 p_1_1 n_web n_vdd n_vdd pmos L=gate_length W=150n ")
	spice_file.write("AS=150n*trans_diffusion_length AD=150n*trans_diffusion_length PS=150n+2*trans_diffusion_length PD=150n+2*trans_diffusion_length\n")	
	spice_file.write("M0 p_1_2 n_web n_vdd n_vdd pmos L=gate_length W=150n ")
	spice_file.write("AS=150n*trans_diffusion_length AD=150n*trans_diffusion_length PS=150n+2*trans_diffusion_length PD=150n+2*trans_diffusion_length\n")	
	spice_file.write("M2 n_bl n_din p_1_1  n_vdd pmos L=gate_length W=150n ")
	spice_file.write("AS=150n*trans_diffusion_length AD=150n*trans_diffusion_length PS=150n+2*trans_diffusion_length PD=150n+2*trans_diffusion_length\n")	
	spice_file.write("M3 n_br n_dinb p_1_2 n_vdd pmos L=gate_length W=150n ")
	spice_file.write("AS=150n*trans_diffusion_length AD=150n*trans_diffusion_length PS=150n+2*trans_diffusion_length PD=150n+2*trans_diffusion_length\n")	

	spice_file.write("M4 n_1_1 n_we n_gnd n_gnd nmos L=gate_length W=250n ")
	spice_file.write("AS=250n*trans_diffusion_length AD=250n*trans_diffusion_length PS=250n+2*trans_diffusion_length PD=250n+2*trans_diffusion_length\n")	
	spice_file.write("M5 n_1_2 n_we n_gnd n_gnd nmos L=gate_length W=250n ")
	spice_file.write("AS=250n*trans_diffusion_length AD=250n*trans_diffusion_length PS=250n+2*trans_diffusion_length PD=250n+2*trans_diffusion_length\n")	
	spice_file.write("M6 n_bl n_din n_1_1 n_gnd nmos L=gate_length W=250n ")
	spice_file.write("AS=250n*trans_diffusion_length AD=250n*trans_diffusion_length PS=250n+2*trans_diffusion_length PD=250n+2*trans_diffusion_length\n")	
	spice_file.write("M7 n_br n_dinb n_1_2 n_gnd nmos L=gate_length W=250n ")
	spice_file.write("AS=250n*trans_diffusion_length AD=250n*trans_diffusion_length PS=250n+2*trans_diffusion_length PD=250n+2*trans_diffusion_length\n")	
	#add the two inverters

	#spice_file.write("X_inv_writedriver_1 n_din n_dinb n_vdd n_gnd inv Wn=inv_writedriver_1_nmos Wp=inv_writedriver_1_pmos\n")
	#spice_file.write("X_inv_writedriver_2 n_we n_web n_vdd n_gnd inv Wn=inv_writedriver_2_nmos Wp=inv_writedriver_2_pmos\n")
	spice_file.write("X_inv_writedriver_1 n_din n_dinb n_vdd n_gnd inv Wn=55n Wp=110n\n")
	spice_file.write("X_inv_writedriver_2 n_we n_web n_vdd n_gnd inv Wn=55n Wp=110n\n")
	spice_file.write(".ENDS\n\n\n")
	spice_file.close()	
	tran_names_list = []
	# wont be sizing the inveters, chooising minimum size
	tran_names_list.append("inv_writedriver_1_nmos")
	tran_names_list.append("inv_writedriver_1_pmos")
	tran_names_list.append("inv_writedriver_2_nmos")
	tran_names_list.append("inv_writedriver_2_pmos")
	tran_names_list.append("tgate_writedriver_3_nmos")
	tran_names_list.append("tgate_writedriver_3_pmos")

	wire_names_list = []

	return tran_names_list, wire_names_list

#todo: automate sizing in the write driver
#this is the write driver
def generate_writedriver_lp(spice_filename, circuit_name):

	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')
	# currently only works for 22nm

	spice_file.write("******************************************************************************************\n")
	spice_file.write("* " + circuit_name + " subcircuit low power write driver \n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT " + circuit_name + " n_we n_din n_bl n_br n_vdd n_gnd\n")

	#spice_file.write("M1 p_1_1 n_web n_vdd n_vdd pmos L=gate_length W=tgate_writedriver_3_pmos\n")
	#spice_file.write("M0 p_1_2 n_web n_vdd n_vdd pmos L=gate_length W=tgate_writedriver_3_pmos\n")
	#spice_file.write("M2 n_bl n_din p_1_1  n_vdd pmos L=gate_length W=tgate_writedriver_3_pmos\n")
	#spice_file.write("M3 n_br n_dinb p_1_2 n_vdd pmos L=gate_length W=tgate_writedriver_3_pmos\n")

	#spice_file.write("M4 n_1_1 n_we n_gnd n_gnd nmos L=gate_length W=tgate_writedriver_3_nmos\n")
	#spice_file.write("M5 n_1_2 n_we n_gnd n_gnd nmos L=gate_length W=tgate_writedriver_3_nmos\n")
	#spice_file.write("M6 n_bl n_din n_1_1 n_gnd nmos L=gate_length W=tgate_writedriver_3_nmos\n")
	#spice_file.write("M7 n_br n_dinb n_1_2 n_gnd nmos L=gate_length W=tgate_writedriver_3_nmos\n")

	spice_file.write("M1 p_1_1 n_web n_vdd n_vdd pmos_lp L=gate_length W=150n ")
	spice_file.write("AS=150n*trans_diffusion_length AD=150n*trans_diffusion_length PS=150n+2*trans_diffusion_length PD=150n+2*trans_diffusion_length\n")	
	spice_file.write("M0 p_1_2 n_web n_vdd n_vdd pmos_lp L=gate_length W=150n ")
	spice_file.write("AS=150n*trans_diffusion_length AD=150n*trans_diffusion_length PS=150n+2*trans_diffusion_length PD=150n+2*trans_diffusion_length\n")	
	spice_file.write("M2 n_bl n_din p_1_1  n_vdd pmos_lp L=gate_length W=150n ")
	spice_file.write("AS=150n*trans_diffusion_length AD=150n*trans_diffusion_length PS=150n+2*trans_diffusion_length PD=150n+2*trans_diffusion_length\n")	
	spice_file.write("M3 n_br n_dinb p_1_2 n_vdd pmos_lp L=gate_length W=150n ")
	spice_file.write("AS=150n*trans_diffusion_length AD=150n*trans_diffusion_length PS=150n+2*trans_diffusion_length PD=150n+2*trans_diffusion_length\n")	

	spice_file.write("M4 n_1_1 n_we n_gnd n_gnd nmos_lp L=gate_length W=250n ")
	spice_file.write("AS=250n*trans_diffusion_length AD=250n*trans_diffusion_length PS=250n+2*trans_diffusion_length PD=250n+2*trans_diffusion_length\n")	
	spice_file.write("M5 n_1_2 n_we n_gnd n_gnd nmos_lp L=gate_length W=250n ")
	spice_file.write("AS=250n*trans_diffusion_length AD=250n*trans_diffusion_length PS=250n+2*trans_diffusion_length PD=250n+2*trans_diffusion_length\n")	
	spice_file.write("M6 n_bl n_din n_1_1 n_gnd nmos_lp L=gate_length W=250n ")
	spice_file.write("AS=250n*trans_diffusion_length AD=250n*trans_diffusion_length PS=250n+2*trans_diffusion_length PD=250n+2*trans_diffusion_length\n")	
	spice_file.write("M7 n_br n_dinb n_1_2 n_gnd nmos_lp L=gate_length W=250n ")
	spice_file.write("AS=250n*trans_diffusion_length AD=250n*trans_diffusion_length PS=250n+2*trans_diffusion_length PD=250n+2*trans_diffusion_length\n")	
	#add the two inverters
	#add the two inverters

	#spice_file.write("X_inv_writedriver_1 n_din n_dinb n_vdd n_gnd inv Wn=inv_writedriver_1_nmos Wp=inv_writedriver_1_pmos\n")
	#spice_file.write("X_inv_writedriver_2 n_we n_web n_vdd n_gnd inv Wn=inv_writedriver_2_nmos Wp=inv_writedriver_2_pmos\n")
	spice_file.write("X_inv_writedriver_1 n_din n_dinb n_vdd n_gnd inv_lp Wn=55n Wp=110n\n")
	spice_file.write("X_inv_writedriver_2 n_we n_web n_vdd n_gnd inv_lp Wn=55n Wp=110n\n")
	spice_file.write(".ENDS\n\n\n")
	spice_file.close()	
	tran_names_list = []
	# wont be sizing the inveters, chooising minimum size
	tran_names_list.append("inv_writedriver_1_nmos")
	tran_names_list.append("inv_writedriver_1_pmos")
	tran_names_list.append("inv_writedriver_2_nmos")
	tran_names_list.append("inv_writedriver_2_pmos")
	tran_names_list.append("tgate_writedriver_3_nmos")
	tran_names_list.append("tgate_writedriver_3_pmos")

	wire_names_list = []

	return tran_names_list, wire_names_list



# This is the precharging circuitry for SRAM-based memory block
def generate_precharge(spice_filename, circuit_name):

	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')
	# currently only works for 22nm
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* " + circuit_name + " subcircuit precharge and equalization \n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT " + circuit_name + " n_precharge_bar n_bl n_blbar n_vdd n_gnd\n")
	spice_file.write("M1 n_bl n_precharge_bar n_vdd n_vdd pmos L=gate_length W=ptran_precharge_side_nmos ")
	spice_file.write("AS=ptran_precharge_side_nmos*trans_diffusion_length AD=ptran_precharge_side_nmos*trans_diffusion_length PS=ptran_precharge_side_nmos+2*trans_diffusion_length PD=ptran_precharge_side_nmos+2*trans_diffusion_length\n")
	spice_file.write("M0 n_blbar n_precharge_bar n_vdd n_vdd pmos L=gate_length W=ptran_precharge_side_nmos ")
	spice_file.write("AS=ptran_precharge_side_nmos*trans_diffusion_length AD=ptran_precharge_side_nmos*trans_diffusion_length PS=ptran_precharge_side_nmos+2*trans_diffusion_length PD=ptran_precharge_side_nmos+2*trans_diffusion_length\n")
	spice_file.write("M2 n_bl n_precharge_bar n_blbar n_vdd pmos L=gate_length W=ptran_equalization_nmos ")
	spice_file.write("AS=ptran_equalization_nmos*trans_diffusion_length AD=ptran_equalization_nmos*trans_diffusion_length PS=ptran_equalization_nmos+2*trans_diffusion_length PD=ptran_equalization_nmos+2*trans_diffusion_length\n")
	spice_file.write(".ENDS\n\n\n")
	spice_file.close()

	tran_names_list = []
	tran_names_list.append("ptran_precharge_side_pmos")
	tran_names_list.append("ptran_equalization_pmos")
	wire_names_list = []

	return tran_names_list, wire_names_list

# This is the precharging circuitry for SRAM-based memory block
def generate_precharge_lp(spice_filename, circuit_name):

	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')

	# currently only works for 22nm
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* " + circuit_name + " subcircuit low power precharge and equalization \n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT " + circuit_name + " n_precharge_bar n_bl n_blbar n_vdd n_gnd\n")
	spice_file.write("M1 n_bl n_precharge_bar n_vdd n_vdd pmos_lp L=gate_length W=ptran_precharge_side_nmos ")
	spice_file.write("AS=ptran_precharge_side_nmos*trans_diffusion_length AD=ptran_precharge_side_nmos*trans_diffusion_length PS=ptran_precharge_side_nmos+2*trans_diffusion_length PD=ptran_precharge_side_nmos+2*trans_diffusion_length\n")
	spice_file.write("M0 n_blbar n_precharge_bar n_vdd n_vdd pmos_lp L=gate_length W=ptran_precharge_side_nmos ")
	spice_file.write("AS=ptran_precharge_side_nmos*trans_diffusion_length AD=ptran_precharge_side_nmos*trans_diffusion_length PS=ptran_precharge_side_nmos+2*trans_diffusion_length PD=ptran_precharge_side_nmos+2*trans_diffusion_length\n")
	spice_file.write("M2 n_bl n_precharge_bar n_blbar n_vdd pmos_lp L=gate_length W=ptran_precharge_side_nmos ")
	spice_file.write("AS=ptran_equalization_nmos*trans_diffusion_length AD=ptran_equalization_nmos*trans_diffusion_length PS=ptran_equalization_nmos+2*trans_diffusion_length PD=ptran_equalization_nmos+2*trans_diffusion_length\n")
	spice_file.write(".ENDS\n\n\n")
	spice_file.close()

	tran_names_list = []
	tran_names_list.append("ptran_precharge_side_pmos")
	tran_names_list.append("ptran_equalization_pmos")
	wire_names_list = []

	return tran_names_list, wire_names_list


# This is the first stage of the configurable decoder
def generate_configurabledecoderi(spice_filename, circuit_name):

	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')
	
	# Generate SPICE subcircuits
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* " + circuit_name + " part of the columndecoder\n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT " + circuit_name + " n_in n_out n_vdd n_gnd\n")
	spice_file.write("X" + circuit_name + " n_in n_1_1 n_vdd n_gnd inv Wn=inv_xconfigurabledecoderi_1_nmos Wp=inv_xconfigurabledecoderi_1_pmos\n")
	spice_file.write("Xtgate" + circuit_name + "_1 n_1_1 n_out n_vdd n_gnd n_vdd n_gnd tgate Wn=tgate_xconfigurabledecoderi_2_nmos Wp=tgate_xconfigurabledecoderi_2_pmos\n")


	spice_file.write(".ENDS\n\n\n")
	
	# Close SPICE file
	spice_file.close()
	
	# Create a list of all transistors used in this subcircuit
	tran_names_list = []
	tran_names_list.append("inv_xconfigurabledecoderi_1_nmos")
	tran_names_list.append("inv_xconfigurabledecoderi_1_pmos")
	tran_names_list.append("tgate_xconfigurabledecoderi_2_nmos")
	tran_names_list.append("tgate_xconfigurabledecoderi_2_pmos")

	# Create a list of all wires used in this subcircuit
	wire_names_list = []
	wire_names_list.append("wire_" + circuit_name )


	return tran_names_list, wire_names_list

# This is the initial stage of the row decoder
def generate_rowdecoderstage0_lp(spice_filename, circuit_name):

	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')
	
	# Generate SPICE subcircuits

	spice_file.write("******************************************************************************************\n")
	spice_file.write("* " + circuit_name + " low power stage 0 of row decoder\n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT " + circuit_name + " n_in n_out n_vdd n_gnd\n")
	spice_file.write("X" + circuit_name + " n_in n_out n_vdd n_gnd inv_lp Wn=inv_rowdecoderstage0_1_nmos Wp=inv_rowdecoderstage0_1_pmos\n")

	spice_file.write(".ENDS\n\n\n")
	
	# Close SPICE file
	spice_file.close()
	
	# Create a list of all transistors used in this subcircuit
	tran_names_list = []
	tran_names_list.append("inv_rowdecoderstage0_1_nmos")
	tran_names_list.append("inv_rowdecoderstage0_1_pmos")

	# Create a list of all wires used in this subcircuit
	wire_names_list = []
	wire_names_list.append("wire_" + circuit_name )


	return tran_names_list, wire_names_list

# This is the initial stage of the row decoder
def generate_rowdecoderstage0(spice_filename, circuit_name):

	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')
	
	# Generate SPICE subcircuits

	spice_file.write("******************************************************************************************\n")
	spice_file.write("* " + circuit_name + " stage 0 of row decoder\n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT " + circuit_name + " n_in n_out n_vdd n_gnd\n")
	spice_file.write("X" + circuit_name + " n_in n_out n_vdd n_gnd inv Wn=inv_rowdecoderstage0_1_nmos Wp=inv_rowdecoderstage0_1_pmos\n")

	spice_file.write(".ENDS\n\n\n")
	
	# Close SPICE file
	spice_file.close()
	
	# Create a list of all transistors used in this subcircuit
	tran_names_list = []
	tran_names_list.append("inv_rowdecoderstage0_1_nmos")
	tran_names_list.append("inv_rowdecoderstage0_1_pmos")

	# Create a list of all wires used in this subcircuit
	wire_names_list = []
	wire_names_list.append("wire_" + circuit_name )


	return tran_names_list, wire_names_list


# This is the first stage of the configurable decoder
def generate_configurabledecoderi_lp(spice_filename, circuit_name):

	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')
	
	# Generate SPICE subcircuits


	spice_file.write("******************************************************************************************\n")
	spice_file.write("* " + circuit_name + " part of the configurable decoder\n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT " + circuit_name + " n_in n_out n_vdd n_gnd\n")
	spice_file.write("X" + circuit_name + " n_in n_1_1 n_vdd n_gnd inv_lp Wn=inv_xconfigurabledecoderi_1_nmos Wp=inv_xconfigurabledecoderi_1_pmos\n")
	spice_file.write("Xtgate" + circuit_name + "_1 n_1_1 n_out n_vdd n_gnd n_vdd n_gnd tgate_lp Wn=tgate_xconfigurabledecoderi_2_nmos Wp=tgate_xconfigurabledecoderi_2_pmos\n")

	spice_file.write(".ENDS\n\n\n")
	
	# Close SPICE file
	spice_file.close()
	
	# Create a list of all transistors used in this subcircuit
	tran_names_list = []
	tran_names_list.append("inv_xconfigurabledecoderi_1_nmos")
	tran_names_list.append("inv_xconfigurabledecoderi_1_pmos")
	tran_names_list.append("tgate_xconfigurabledecoderi_2_nmos")
	tran_names_list.append("tgate_xconfigurabledecoderi_2_pmos")

	# Create a list of all wires used in this subcircuit
	wire_names_list = []
	wire_names_list.append("wire_" + circuit_name )


	return tran_names_list, wire_names_list


# This is the wordline driver
def generate_wordline_driver_lp(spice_filename, circuit_name, nand_size, repeater):

	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')
	
	# Generate SPICE subcircuits

	# Create the fully-on MUX circuit
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* " + circuit_name + " subcircuit predecoder stage 3 \n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT " + circuit_name + " n_in n_out n_vdd n_gnd\n")
	spice_file.write("X" + circuit_name + "_nand"+str(nand_size)+" n_in n_1_1 n_vdd n_gnd nand"+str(nand_size)+"_lp Wn=inv_nand"+str(nand_size)+"_" + circuit_name + "_1_nmos Wp=inv_nand"+str(nand_size)+"_" + circuit_name + "_1_pmos\n")
	if repeater == 0:
		spice_file.write("X_inv" + circuit_name + "_2 n_1_1 n_1_2 n_vdd n_gnd inv_lp Wn=inv_" + circuit_name + "_2_nmos Wp=inv_" + circuit_name + "_2_pmos\n")
		spice_file.write("X_inv" + circuit_name + "_3 n_1_2 n_1_3 n_vdd n_gnd inv_lp Wn=inv_" + circuit_name + "_3_nmos Wp=inv_" + circuit_name + "_3_pmos\n")
	else:
		spice_file.write("X_inv" + circuit_name + "_2 n_1_1 n_1_2 n_vdd n_gnd inv_lp Wn=inv_" + circuit_name + "_2_nmos Wp=inv_" + circuit_name + "_2_pmos\n")
		spice_file.write("Xwirelrepeat n_1_2 n_1_2_2 wire Rw=wire_memorycell_horizontal_res/2 Cw=wire_memorycell_horizontal_cap/2 \n") 
		spice_file.write("X_inv" + circuit_name + "_3 n_1_2_2 n_1_3 n_vdd n_gnd inv_lp Wn=inv_" + circuit_name + "_3_nmos Wp=inv_" + circuit_name + "_3_pmos\n")
	spice_file.write("X_inv" + circuit_name + "_4 n_1_3 n_out n_vdd n_gnd inv_lp Wn=inv_" + circuit_name + "_4_nmos Wp=inv_" + circuit_name + "_4_pmos\n")
	spice_file.write(".ENDS\n\n\n")
	
	# Close SPICE file
	spice_file.close()
	
	# Create a list of all transistors used in this subcircuit
	tran_names_list = []
	tran_names_list.append("inv_nand"+str(nand_size)+"_" + circuit_name + "_1_nmos")
	tran_names_list.append("inv_nand"+str(nand_size)+"_" + circuit_name + "_1_pmos")
	tran_names_list.append("inv_" + circuit_name + "_2_nmos")
	tran_names_list.append("inv_" + circuit_name + "_2_nmos")
	tran_names_list.append("inv_" + circuit_name + "_3_nmos")
	tran_names_list.append("inv_" + circuit_name + "_3_nmos")
	tran_names_list.append("inv_" + circuit_name + "_4_nmos")
	tran_names_list.append("inv_" + circuit_name + "_4_nmos")	
	# Create a list of all wires used in this subcircuit

	wire_names_list = [] 
	return tran_names_list, wire_names_list


# This is the wordline driver
def generate_wordline_driver(spice_filename, circuit_name, nand_size, repeater):

	# Open SPICE file for appending
	spice_file = open(spice_filename, 'a')
	
	# Generate SPICE subcircuits

	# Create the fully-on MUX circuit
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* " + circuit_name + " subcircuit predecoder stage 3 \n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT " + circuit_name + " n_in n_out n_vdd n_gnd\n")
	spice_file.write("X" + circuit_name + "_nand"+str(nand_size)+" n_in n_1_1 n_vdd n_gnd nand"+str(nand_size)+" Wn=inv_nand"+str(nand_size)+"_" + circuit_name + "_1_nmos Wp=inv_nand"+str(nand_size)+"_" + circuit_name + "_1_pmos\n")
	if repeater == 0:
		spice_file.write("X_inv" + circuit_name + "_2 n_1_1 n_1_2 n_vdd n_gnd inv Wn=inv_" + circuit_name + "_2_nmos Wp=inv_" + circuit_name + "_2_pmos\n")
		spice_file.write("X_inv" + circuit_name + "_3 n_1_2 n_1_3 n_vdd n_gnd inv Wn=inv_" + circuit_name + "_3_nmos Wp=inv_" + circuit_name + "_3_pmos\n")
	else:
		spice_file.write("X_inv" + circuit_name + "_2 n_1_1 n_1_2 n_vdd n_gnd inv Wn=inv_" + circuit_name + "_2_nmos Wp=inv_" + circuit_name + "_2_pmos\n")
		spice_file.write("Xwirelrepeat n_1_2 n_1_2_2 wire Rw=wire_memorycell_horizontal_res/2 Cw=wire_memorycell_horizontal_cap/2 \n") 
		spice_file.write("X_inv" + circuit_name + "_3 n_1_2_2 n_1_3 n_vdd n_gnd inv Wn=inv_" + circuit_name + "_3_nmos Wp=inv_" + circuit_name + "_3_pmos\n")
	spice_file.write("X_inv" + circuit_name + "_4 n_1_3 n_out n_vdd n_gnd inv Wn=inv_" + circuit_name + "_4_nmos Wp=inv_" + circuit_name + "_4_pmos\n")
	spice_file.write(".ENDS\n\n\n")
	
	# Close SPICE file
	spice_file.close()
	
	# Create a list of all transistors used in this subcircuit
	tran_names_list = []
	tran_names_list.append("inv_nand"+str(nand_size)+"_" + circuit_name + "_1_nmos")
	tran_names_list.append("inv_nand"+str(nand_size)+"_" + circuit_name + "_1_pmos")
	tran_names_list.append("inv_" + circuit_name + "_2_nmos")
	tran_names_list.append("inv_" + circuit_name + "_2_nmos")
	tran_names_list.append("inv_" + circuit_name + "_3_nmos")
	tran_names_list.append("inv_" + circuit_name + "_3_nmos")
	tran_names_list.append("inv_" + circuit_name + "_4_nmos")
	tran_names_list.append("inv_" + circuit_name + "_4_nmos")	
	# Create a list of all wires used in this subcircuit
	wire_names_list = [] 


	return tran_names_list, wire_names_list