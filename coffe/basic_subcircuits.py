def inverter_generate(filename, use_finfet, use_technology):
	""" Generates the SPICE subcircuit for an inverter. Appends it to file 'filename'. """

	# Open the file for appending
	spice_file = open(filename, 'a')  

	if not use_finfet :
		spice_file.write("******************************************************************************************\n")
		spice_file.write("* Inverter\n")
		spice_file.write("******************************************************************************************\n")
		spice_file.write(".SUBCKT inv n_in n_out n_vdd n_gnd Wn=45n Wp=45n\n")
		spice_file.write("MNDOWN n_out n_in n_gnd n_gnd nmos L=gate_length W=Wn ")
		spice_file.write("AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length\n")
		spice_file.write("MPUP n_out n_in n_vdd n_vdd pmos L=gate_length W=Wp ")
		spice_file.write("AS=Wp*trans_diffusion_length AD=Wp*trans_diffusion_length PS=Wp+2*trans_diffusion_length PD=Wp+2*trans_diffusion_length\n")
		spice_file.write(".ENDS\n\n\n")

		spice_file.write("******************************************************************************************\n")
		spice_file.write("* Low Power Inverter\n")
		spice_file.write("******************************************************************************************\n")
		spice_file.write(".SUBCKT inv_lp n_in n_out n_vdd n_gnd Wn=45n Wp=45n\n")
		spice_file.write("MNDOWN n_out n_in n_gnd n_gnd nmos_lp L=gate_length W=Wn ")
		spice_file.write("AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length\n")
		spice_file.write("MPUP n_out n_in n_vdd n_vdd pmos_lp L=gate_length W=Wp ")
		spice_file.write("AS=Wp*trans_diffusion_length AD=Wp*trans_diffusion_length PS=Wp+2*trans_diffusion_length PD=Wp+2*trans_diffusion_length\n")
		spice_file.write(".ENDS\n\n\n")

		if use_technology == "MTJ":
			spice_file.write("******************************************************************************************\n")
			spice_file.write("* MTJ Low Power Inverter\n")
			spice_file.write("******************************************************************************************\n")
			spice_file.write(".SUBCKT inv_lp_mtj n_in n_out n_vdd n_gnd Wn=45n Wp=45n\n")
			spice_file.write("MNDOWN n_out n_in n_gnd n_gnd nmos_lp_mtj L=gate_length W=Wn ")
			spice_file.write("AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length\n")
			spice_file.write("MPUP n_out n_in n_vdd n_vdd pmos_lp_mtj L=gate_length W=Wp ")
			spice_file.write("AS=Wp*trans_diffusion_length AD=Wp*trans_diffusion_length PS=Wp+2*trans_diffusion_length PD=Wp+2*trans_diffusion_length\n")
			spice_file.write(".ENDS\n\n\n")
	else :
		spice_file.write("******************************************************************************************\n")
		spice_file.write("* Inverter\n")
		spice_file.write("******************************************************************************************\n")
		spice_file.write(".SUBCKT inv n_in n_out n_vdd n_gnd Wn=1 Wp=1\n")
		spice_file.write("MNDOWN n_out n_in n_gnd n_gnd nmos L=gate_length nfin=Wn ")
		spice_file.write("ASEO=Wn*min_tran_width*trans_diffusion_length ADEO=Wn*min_tran_width*trans_diffusion_length PSEO='Wn*(min_tran_width+2*trans_diffusion_length)' PDEO='Wn*(min_tran_width+2*trans_diffusion_length)'\n")
		spice_file.write("MPUP n_out n_in n_vdd n_vdd pmos L=gate_length nfin=Wp ")
		spice_file.write("ASEO=Wp*min_tran_width*trans_diffusion_length ADEO=Wp*min_tran_width*trans_diffusion_length PSEO='Wp*(min_tran_width+2*trans_diffusion_length)' PDEO='Wp*(min_tran_width+2*trans_diffusion_length)'\n")
		spice_file.write(".ENDS\n\n\n")


		spice_file.write("******************************************************************************************\n")
		spice_file.write("* Low Power Inverter\n")
		spice_file.write("******************************************************************************************\n")
		spice_file.write(".SUBCKT inv_lp n_in n_out n_vdd n_gnd Wn=1 Wp=1\n")
		spice_file.write("MNDOWN n_out n_in n_gnd n_gnd nmos_lp L=gate_length nfin=Wn ")
		spice_file.write("ASEO=Wn*min_tran_width*trans_diffusion_length ADEO=Wn*min_tran_width*trans_diffusion_length PSEO='Wn*(min_tran_width+2*trans_diffusion_length)' PDEO='Wn*(min_tran_width+2*trans_diffusion_length)'\n")
		spice_file.write("MPUP n_out n_in n_vdd n_vdd pmos_lp L=gate_length nfin=Wp ")
		spice_file.write("ASEO=Wp*min_tran_width*trans_diffusion_length ADEO=Wp*min_tran_width*trans_diffusion_length PSEO='Wp*(min_tran_width+2*trans_diffusion_length)' PDEO='Wp*(min_tran_width+2*trans_diffusion_length)'\n")
		spice_file.write(".ENDS\n\n\n")

		if use_technology == "MTJ":
			spice_file.write("******************************************************************************************\n")
			spice_file.write("* MTJ Low Power Inverter\n")
			spice_file.write("******************************************************************************************\n")
			spice_file.write(".SUBCKT inv_lp_mtj n_in n_out n_vdd n_gnd Wn=1 Wp=1\n")
			spice_file.write("MNDOWN n_out n_in n_gnd n_gnd nmos_lp_mtj L=gate_length nfin=Wn ")
			spice_file.write("ASEO=Wn*min_tran_width*trans_diffusion_length ADEO=Wn*min_tran_width*trans_diffusion_length PSEO='Wn*(min_tran_width+2*trans_diffusion_length)' PDEO='Wn*(min_tran_width+2*trans_diffusion_length)'\n")
			spice_file.write("MPUP n_out n_in n_vdd n_vdd pmos_lp_mtj L=gate_length nfin=Wp ")
			spice_file.write("ASEO=Wp*min_tran_width*trans_diffusion_length ADEO=Wp*min_tran_width*trans_diffusion_length PSEO='Wp*(min_tran_width+2*trans_diffusion_length)' PDEO='Wp*(min_tran_width+2*trans_diffusion_length)'\n")
			spice_file.write(".ENDS\n\n\n")

	spice_file.close()

def lvl_shifter_generate(filename, use_finfet):
	""" Generates the SPICE subcircuit for a single stage of the conventional lvl shifter. Appends it to file 'filename'. """

	# Open the file for appending
	spice_file = open(filename, 'a')
	spice_file.write("******************************************************************************************\n")
	spice_file.write("*  lvl shifter\n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT lvl_shifter_single n_in_n n_in_p n_out n_vdd n_gnd Wn=45n Wp=45n\n")
	spice_file.write("MNDOWN n_out n_in_n n_gnd n_gnd nmos L=gate_length W=Wn ")
	spice_file.write("AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length\n")
	spice_file.write("MPUP n_out n_in_p n_vdd n_vdd pmos L=gate_length W=Wp ")
	spice_file.write("AS=Wp*trans_diffusion_length AD=Wp*trans_diffusion_length PS=Wp+2*trans_diffusion_length PD=Wp+2*trans_diffusion_length\n")
	spice_file.write(".ENDS\n\n\n")	



def nand2_generate(filename, use_finfet):
	""" Generates the SPICE subcircuit for a 2input nand gate. Appends it to file 'filename'. """

	# Open the file for appending
	# its set up so that the delay of one of the inputs is measured so the other input is set to vdd
	# simulations should still be fine regardless of these values by using default values
	spice_file = open(filename, 'a')  

	if not use_finfet :
		spice_file.write("******************************************************************************************\n")
		spice_file.write("* nand2\n")
		spice_file.write("******************************************************************************************\n")
		spice_file.write(".SUBCKT nand2 n_in n_out n_vdd n_gnd Wn=45n Wp=45n\n") # I dont change the input to the NAND gate, since we are only exciting one of the inputs. The 2nd input is always set to vdd
		spice_file.write("MNDOWN2 n_out n_vdd n_z n_gnd nmos L=gate_length W=Wn ")
		spice_file.write("AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length\n")
		spice_file.write("MNDOWN1 n_z n_in n_gnd n_gnd nmos L=gate_length W=Wn ")
		spice_file.write("AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length\n")
		spice_file.write("MPUP1 n_out n_vdd n_vdd n_vdd pmos L=gate_length W=Wp ")
		spice_file.write("AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length\n")
		spice_file.write("MPUP2 n_out n_in n_vdd n_vdd pmos L=gate_length W=Wp ")
		spice_file.write("AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length\n")
		spice_file.write(".ENDS\n\n\n")
        
		spice_file.write("******************************************************************************************\n")
		spice_file.write("* nand2 decoder\n")
		spice_file.write("******************************************************************************************\n")
		spice_file.write(".SUBCKT nand2_decode n_in1 n_in2 n_out n_vdd n_gnd Wn=45n Wp=45n\n") 
		spice_file.write("MNDOWN2 n_out n_in1 n_z n_gnd nmos L=gate_length W=Wn ")
		spice_file.write("AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length\n")
		spice_file.write("MNDOWN1 n_z n_in2 n_gnd n_gnd nmos L=gate_length W=Wn ")
		spice_file.write("AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length\n")
		spice_file.write("MPUP1 n_out n_in1 n_vdd n_vdd pmos L=gate_length W=Wp ")
		spice_file.write("AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length\n")
		spice_file.write("MPUP2 n_out n_in2 n_vdd n_vdd pmos L=gate_length W=Wp ")
		spice_file.write("AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length\n")
		spice_file.write(".ENDS\n\n\n")
		
		
		spice_file.write("******************************************************************************************\n")
		spice_file.write("* nor2 decoder\n")
		spice_file.write("******************************************************************************************\n")
		spice_file.write(".SUBCKT nor2_decode n_in1 n_in2 n_out n_vdd n_gnd Wn=45n Wp=45n\n") 
		spice_file.write("MNDOWN2 n_out n_in1 n_gnd n_gnd nmos L=gate_length W=Wn ")
		spice_file.write("AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length\n")
		spice_file.write("MNDOWN1 n_out n_in2 n_gnd n_gnd nmos L=gate_length W=Wn ")
		spice_file.write("AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length\n")
		spice_file.write("MPUP1 n_out n_in1 n_z n_vdd pmos L=gate_length W=Wp ")
		spice_file.write("AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length\n")
		spice_file.write("MPUP2 n_z n_in2 n_vdd n_vdd pmos L=gate_length W=Wp ")
		spice_file.write("AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length\n")
		spice_file.write(".ENDS\n\n\n")		
	else :
		spice_file.write("******************************************************************************************\n")
		spice_file.write("* nand2\n")
		spice_file.write("******************************************************************************************\n")
		spice_file.write(".SUBCKT nand2 n_in n_out n_vdd n_gnd Wn=1 Wp=1\n")
		spice_file.write("MNDOWN2 n_out n_vdd n_z n_gnd nmos L=gate_length nfin=Wn ")
		spice_file.write("ASEO=Wn*min_tran_width*trans_diffusion_length ADEO=Wn*min_tran_width*trans_diffusion_length PSEO='Wn*(min_tran_width+2*trans_diffusion_length)' PDEO='Wn*(min_tran_width+2*trans_diffusion_length)'\n")
		spice_file.write("MNDOWN1 n_z n_in n_gnd n_gnd nmos L=gate_length nfin=Wn ")
		spice_file.write("ASEO=Wn*min_tran_width*trans_diffusion_length ADEO=Wn*min_tran_width*trans_diffusion_length PSEO='Wn*(min_tran_width+2*trans_diffusion_length)' PDEO='Wn*(min_tran_width+2*trans_diffusion_length)'\n")
		spice_file.write("MPUP1 n_out n_vdd n_vdd n_vdd pmos L=gate_length nfin=Wp ")
		spice_file.write("ASEO=Wp*min_tran_width*trans_diffusion_length ADEO=Wp*min_tran_width*trans_diffusion_length PSEO='Wp*(min_tran_width+2*trans_diffusion_length)' PDEO='Wp*(min_tran_width+2*trans_diffusion_length)'\n")
		spice_file.write("MPUP2 n_out n_in n_vdd n_vdd pmos L=gate_length nfin=Wp ")
		spice_file.write("ASEO=Wp*min_tran_width*trans_diffusion_length ADEO=Wp*min_tran_width*trans_diffusion_length PSEO='Wp*(min_tran_width+2*trans_diffusion_length)' PDEO='Wp*(min_tran_width+2*trans_diffusion_length)'\n")
		spice_file.write(".ENDS\n\n\n")

	spice_file.close()


def nand2_generate_lp(filename, use_finfet):
	""" Generates the SPICE subcircuit for a 2input nand gate. Appends it to file 'filename'. """

	# Open the file for appending
	# its set up so that the delay of one of the inputs is measured so the other input is set to vdd
	# TODO: obtain precise values for AS, AD, PS, PD
	# simulations should still be fine regardless of these values by using default values
	# after adding AS, AD, PS, PD, remove \n from each like and put a space instead
	spice_file = open(filename, 'a')  

	if not use_finfet :
		spice_file.write("******************************************************************************************\n")
		spice_file.write("* nand2\n")
		spice_file.write("******************************************************************************************\n")
		spice_file.write(".SUBCKT nand2_lp n_in n_out n_vdd n_gnd Wn=45n Wp=45n\n") # I dont change the input to the NAND gate, since we are only exciting one of the inputs. The 2nd input is always set to vdd
		spice_file.write("MNDOWN2 n_out n_vdd n_z n_gnd nmos_lp L=gate_length W=Wn ")
		spice_file.write("AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length\n")
		spice_file.write("MNDOWN1 n_z n_in n_gnd n_gnd nmos_lp L=gate_length W=Wn ")
		spice_file.write("AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length\n")
		spice_file.write("MPUP1 n_out n_vdd n_vdd n_vdd pmos_lp L=gate_length W=Wp ")
		spice_file.write("AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length\n")
		spice_file.write("MPUP2 n_out n_in n_vdd n_vdd pmos_lp L=gate_length W=Wp ")
		spice_file.write("AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length\n")
		spice_file.write(".ENDS\n\n\n")
	else :
		spice_file.write("******************************************************************************************\n")
		spice_file.write("* nand2\n")
		spice_file.write("******************************************************************************************\n")
		spice_file.write(".SUBCKT nand2_lp n_in n_out n_vdd n_gnd Wn=1 Wp=1\n")
		spice_file.write("MNDOWN2 n_out n_vdd n_z n_gnd nmos_lp L=gate_length nfin=Wn ")
		spice_file.write("ASEO=Wn*min_tran_width*trans_diffusion_length ADEO=Wn*min_tran_width*trans_diffusion_length PSEO='Wn*(min_tran_width+2*trans_diffusion_length)' PDEO='Wn*(min_tran_width+2*trans_diffusion_length)'\n")
		spice_file.write("MNDOWN1 n_z n_in n_gnd n_gnd nmos_lp L=gate_length nfin=Wn ")
		spice_file.write("ASEO=Wn*min_tran_width*trans_diffusion_length ADEO=Wn*min_tran_width*trans_diffusion_length PSEO='Wn*(min_tran_width+2*trans_diffusion_length)' PDEO='Wn*(min_tran_width+2*trans_diffusion_length)'\n")
		spice_file.write("MPUP1 n_out n_vdd n_vdd n_vdd pmos_lp L=gate_length nfin=Wp ")
		spice_file.write("ASEO=Wp*min_tran_width*trans_diffusion_length ADEO=Wp*min_tran_width*trans_diffusion_length PSEO='Wp*(min_tran_width+2*trans_diffusion_length)' PDEO='Wp*(min_tran_width+2*trans_diffusion_length)'\n")
		spice_file.write("MPUP2 n_out n_in n_vdd n_vdd pmos_lp L=gate_length nfin=Wp ")
		spice_file.write("ASEO=Wp*min_tran_width*trans_diffusion_length ADEO=Wp*min_tran_width*trans_diffusion_length PSEO='Wp*(min_tran_width+2*trans_diffusion_length)' PDEO='Wp*(min_tran_width+2*trans_diffusion_length)'\n")
		spice_file.write(".ENDS\n\n\n")

	spice_file.close()

def nand3_generate(filename, use_finfet):
	""" Generates the SPICE subcircuit for a 3input nand gate. Appends it to file 'filename'. """

	# Open the file for appending
	# its set up so that the delay of one of the inputs is measured so the other input is set to vdd
	spice_file = open(filename, 'a')  

	if not use_finfet :
		spice_file.write("******************************************************************************************\n")
		spice_file.write("* nand3\n")
		spice_file.write("******************************************************************************************\n")
		spice_file.write(".SUBCKT nand3 n_in n_out n_vdd n_gnd Wn=45n Wp=45n\n") 
		spice_file.write("MNDOWN2 n_out n_vdd n_z n_gnd nmos L=gate_length W=Wn ")
		spice_file.write("AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length\n")
		spice_file.write("MNDOWN1 n_z n_vdd n_z2 n_gnd nmos L=gate_length W=Wn ")
		spice_file.write("AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length\n")
		spice_file.write("MNDOWN0 n_z2 n_in n_gnd n_gnd nmos L=gate_length W=Wn ")
		spice_file.write("AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length\n")
		spice_file.write("MPUP0 n_out n_vdd n_vdd n_vdd pmos L=gate_length W=Wp ")
		spice_file.write("AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length\n")
		spice_file.write("MPUP1 n_out n_vdd n_vdd n_vdd pmos L=gate_length W=Wp ")
		spice_file.write("AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length\n")
		spice_file.write("MPUP2 n_out n_in n_vdd n_vdd pmos L=gate_length W=Wp ")
		spice_file.write("AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length\n")
		spice_file.write(".ENDS\n\n\n")
		
		
		spice_file.write("******************************************************************************************\n")
		spice_file.write("* nand3 decoder\n")
		spice_file.write("******************************************************************************************\n")
		spice_file.write(".SUBCKT nand3_decode n_in1 n_in2 n_in3 n_out n_vdd n_gnd Wn=45n Wp=45n\n") # I dont change the input to the NAND gate, since we are only exciting one of the inputs. The 2nd input is always set to vdd
		spice_file.write("MNDOWN3 n_out n_in1 n_z n_gnd nmos L=gate_length W=Wn ")
		spice_file.write("AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length\n")
		spice_file.write("MNDOWN2 n_z n_in2 n_y n_gnd nmos L=gate_length W=Wn ")
		spice_file.write("AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length\n")
		spice_file.write("MNDOWN1 n_y n_in3 n_gnd n_gnd nmos L=gate_length W=Wn ")
		spice_file.write("AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length\n")

		spice_file.write("MPUP1 n_out n_in1 n_vdd n_vdd pmos L=gate_length W=Wp ")
		spice_file.write("AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length\n")
		spice_file.write("MPUP2 n_out n_in2 n_vdd n_vdd pmos L=gate_length W=Wp ")
		spice_file.write("AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length\n")
		spice_file.write("MPUP3 n_out n_in3 n_vdd n_vdd pmos L=gate_length W=Wp ")
		spice_file.write("AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length\n")
		spice_file.write(".ENDS\n\n\n")		
	else :
		spice_file.write("******************************************************************************************\n")
		spice_file.write("* nand3\n")
		spice_file.write("******************************************************************************************\n")
		spice_file.write(".SUBCKT nand3 n_in n_out n_vdd n_gnd Wn=1 Wp=1\n")
		spice_file.write("MNDOWN2 n_out n_vdd n_z n_gnd nmos L=gate_length nfin=Wn ")
		spice_file.write("ASEO=Wn*min_tran_width*trans_diffusion_length ADEO=Wn*min_tran_width*trans_diffusion_length PSEO='Wn*(min_tran_width+2*trans_diffusion_length)' PDEO='Wn*(min_tran_width+2*trans_diffusion_length)'\n")
		spice_file.write("MNDOWN1 n_z n_vdd n_z2 n_gnd nmos L=gate_length nfin=Wn ")
		spice_file.write("ASEO=Wn*min_tran_width*trans_diffusion_length ADEO=Wn*min_tran_width*trans_diffusion_length PSEO='Wn*(min_tran_width+2*trans_diffusion_length)' PDEO='Wn*(min_tran_width+2*trans_diffusion_length)'\n")
		spice_file.write("MNDOWN0 n_z2 n_in n_gnd n_gnd nmos L=gate_length nfin=Wn ")
		spice_file.write("ASEO=Wn*min_tran_width*trans_diffusion_length ADEO=Wn*min_tran_width*trans_diffusion_length PSEO='Wn*(min_tran_width+2*trans_diffusion_length)' PDEO='Wn*(min_tran_width+2*trans_diffusion_length)'\n")
		spice_file.write("MPUP0 n_out n_vdd n_vdd n_vdd pmos L=gate_length nfin=Wp ")
		spice_file.write("ASEO=Wp*min_tran_width*trans_diffusion_length ADEO=Wp*min_tran_width*trans_diffusion_length PSEO='Wp*(min_tran_width+2*trans_diffusion_length)' PDEO='Wp*(min_tran_width+2*trans_diffusion_length)'\n")
		spice_file.write("MPUP1 n_out n_vdd n_vdd n_vdd pmos L=gate_length nfin=Wp ")
		spice_file.write("ASEO=Wp*min_tran_width*trans_diffusion_length ADEO=Wp*min_tran_width*trans_diffusion_length PSEO='Wp*(min_tran_width+2*trans_diffusion_length)' PDEO='Wp*(min_tran_width+2*trans_diffusion_length)'\n")
		spice_file.write("MPUP2 n_out n_in n_vdd n_vdd pmos L=gate_length nfin=Wp ")
		spice_file.write("ASEO=Wp*min_tran_width*trans_diffusion_length ADEO=Wp*min_tran_width*trans_diffusion_length PSEO='Wp*(min_tran_width+2*trans_diffusion_length)' PDEO='Wp*(min_tran_width+2*trans_diffusion_length)'\n")
		spice_file.write(".ENDS\n\n\n")

	spice_file.close()


def nand3_generate_lp(filename, use_finfet):
	""" Generates the SPICE subcircuit for a 3input nand gate. Appends it to file 'filename'. """

	# Open the file for appending
	# its set up so that the delay of one of the inputs is measured so the other input is set to vdd
	spice_file = open(filename, 'a')  

	if not use_finfet :
		spice_file.write("******************************************************************************************\n")
		spice_file.write("* nand3\n")
		spice_file.write("******************************************************************************************\n")
		spice_file.write(".SUBCKT nand3_lp n_in n_out n_vdd n_gnd Wn=45n Wp=45n\n") 
		spice_file.write("MNDOWN2 n_out n_vdd n_z n_gnd nmos_lp L=gate_length W=Wn ")
		spice_file.write("AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length\n")
		spice_file.write("MNDOWN1 n_z n_vdd n_z2 n_gnd nmos_lp L=gate_length W=Wn ")
		spice_file.write("AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length\n")
		spice_file.write("MNDOWN0 n_z2 n_in n_gnd n_gnd nmos_lp L=gate_length W=Wn ")
		spice_file.write("AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length\n")
		spice_file.write("MPUP0 n_out n_vdd n_vdd n_vdd pmos_lp L=gate_length W=Wp ")
		spice_file.write("AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length\n")
		spice_file.write("MPUP1 n_out n_vdd n_vdd n_vdd pmos_lp L=gate_length W=Wp ")
		spice_file.write("AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length\n")
		spice_file.write("MPUP2 n_out n_in n_vdd n_vdd pmos_lp L=gate_length W=Wp ")
		spice_file.write("AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length\n")
		spice_file.write(".ENDS\n\n\n")
	else :
		spice_file.write("******************************************************************************************\n")
		spice_file.write("* nand3\n")
		spice_file.write("******************************************************************************************\n")
		spice_file.write(".SUBCKT nand3_lp n_in n_out n_vdd n_gnd Wn=1 Wp=1\n")
		spice_file.write("MNDOWN2 n_out n_vdd n_z n_gnd nmos_lp L=gate_length nfin=Wn ")
		spice_file.write("ASEO=Wn*min_tran_width*trans_diffusion_length ADEO=Wn*min_tran_width*trans_diffusion_length PSEO='Wn*(min_tran_width+2*trans_diffusion_length)' PDEO='Wn*(min_tran_width+2*trans_diffusion_length)'\n")
		spice_file.write("MNDOWN1 n_z n_vdd n_z2 n_gnd nmos_lp L=gate_length nfin=Wn ")
		spice_file.write("ASEO=Wn*min_tran_width*trans_diffusion_length ADEO=Wn*min_tran_width*trans_diffusion_length PSEO='Wn*(min_tran_width+2*trans_diffusion_length)' PDEO='Wn*(min_tran_width+2*trans_diffusion_length)'\n")
		spice_file.write("MNDOWN0 n_z2 n_in n_gnd n_gnd nmos_lp L=gate_length nfin=Wn ")
		spice_file.write("ASEO=Wn*min_tran_width*trans_diffusion_length ADEO=Wn*min_tran_width*trans_diffusion_length PSEO='Wn*(min_tran_width+2*trans_diffusion_length)' PDEO='Wn*(min_tran_width+2*trans_diffusion_length)'\n")
		spice_file.write("MPUP0 n_out n_vdd n_vdd n_vdd pmos_lp L=gate_length nfin=Wp ")
		spice_file.write("ASEO=Wp*min_tran_width*trans_diffusion_length ADEO=Wp*min_tran_width*trans_diffusion_length PSEO='Wp*(min_tran_width+2*trans_diffusion_length)' PDEO='Wp*(min_tran_width+2*trans_diffusion_length)'\n")
		spice_file.write("MPUP1 n_out n_vdd n_vdd n_vdd pmos_lp L=gate_length nfin=Wp ")
		spice_file.write("ASEO=Wp*min_tran_width*trans_diffusion_length ADEO=Wp*min_tran_width*trans_diffusion_length PSEO='Wp*(min_tran_width+2*trans_diffusion_length)' PDEO='Wp*(min_tran_width+2*trans_diffusion_length)'\n")
		spice_file.write("MPUP2 n_out n_in n_vdd n_vdd pmos_lp L=gate_length nfin=Wp ")
		spice_file.write("ASEO=Wp*min_tran_width*trans_diffusion_length ADEO=Wp*min_tran_width*trans_diffusion_length PSEO='Wp*(min_tran_width+2*trans_diffusion_length)' PDEO='Wp*(min_tran_width+2*trans_diffusion_length)'\n")
		spice_file.write(".ENDS\n\n\n")

	spice_file.close()
	
	
def rest_generate(filename, use_finfet):
	""" Generates the SPICE subcircuit for a level-restorer. Appends it to file 'filename'. """

	# Open the file for appending
	spice_file = open(filename, 'a')  

	if not use_finfet :
		spice_file.write("******************************************************************************************\n")
		spice_file.write("* Level-restorer PMOS\n")
		spice_file.write("******************************************************************************************\n")
		spice_file.write(".SUBCKT rest n_pull n_gate n_vdd n_gnd Wp=45n\n")
		spice_file.write("MPREST n_pull n_gate n_vdd n_vdd pmos L=gate_length*rest_length_factor W=Wp ")
		spice_file.write("AS=Wp*trans_diffusion_length AD=Wp*trans_diffusion_length PS=Wp+2*trans_diffusion_length PD=Wp+2*trans_diffusion_length\n")
		spice_file.write(".ENDS\n\n\n")
	else :
		spice_file.write("******************************************************************************************\n")
		spice_file.write("* Level-restorer PMOS\n")
		spice_file.write("******************************************************************************************\n")
		spice_file.write(".SUBCKT rest n_pull n_gate n_vdd n_gnd Wp=1 \n")
		spice_file.write("MPREST n_pull n_gate n_vdd n_vdd pmos L=gate_length*rest_length_factor nfin=Wp ")
		spice_file.write("ASEO=Wp*min_tran_width*trans_diffusion_length ADEO=Wp*min_tran_width*trans_diffusion_length PSEO='Wp*(min_tran_width+2*trans_diffusion_length)' PDEO='Wp*(min_tran_width+2*trans_diffusion_length)'\n")
		spice_file.write(".ENDS\n\n\n")   
		
	spice_file.close()
	
	
def wire_generate(filename):
	""" Generates the SPICE subcircuit for a wire. Appends it to file 'filename'. """

	# Open the file for appending
	spice_file = open(filename, 'a')  
	spice_file.write("******************************************************************************************\n")
	spice_file.write("* Interconnect wire\n")
	spice_file.write("******************************************************************************************\n")
	spice_file.write(".SUBCKT wire n_in n_out Rw=1 Cw=1\n")
	spice_file.write("CWIRE_1 n_in gnd Cw\n")
	spice_file.write("RWIRE_1 n_in n_out Rw\n")
	spice_file.write("CWIRE_2 n_out gnd Cw\n")
	spice_file.write(".ENDS\n\n\n")   
	spice_file.close()
	
	
def ptran_generate(filename, use_finfet):
	""" Generates the SPICE subcircuit for a pass-transistor. Appends it to file 'filename'. """

	# Open the file for appending
	spice_file = open(filename, 'a')  

	if not use_finfet :
		spice_file.write("******************************************************************************************\n")
		spice_file.write("* Pass-transistor\n")
		spice_file.write("******************************************************************************************\n")
		spice_file.write(".SUBCKT ptran n_in n_out n_gate n_gnd Wn=45n \n")
		spice_file.write("MNPASS n_in n_gate n_out n_gnd nmos L=gate_length W=Wn ")
		spice_file.write("AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length\n")
		spice_file.write(".ENDS\n\n\n")   
	else :
		spice_file.write("******************************************************************************************\n")
		spice_file.write("* Pass-transistor\n")
		spice_file.write("******************************************************************************************\n")
		spice_file.write(".SUBCKT ptran n_in n_out n_gate n_gnd Wn=1\n")
		spice_file.write("MNPASS n_in n_gate n_out n_gnd nmos L=gate_length nfin=Wn ")
		spice_file.write("ASEO=Wn*min_tran_width*trans_diffusion_length ADEO=Wn*min_tran_width*trans_diffusion_length PSEO='Wn*(min_tran_width+2*trans_diffusion_length)' PDEO='Wn*(min_tran_width+2*trans_diffusion_length)'\n")
		spice_file.write(".ENDS\n\n\n")   

	spice_file.close()
	
def ptran_pmos_generate(filename, use_finfet):
	""" Generates the SPICE subcircuit for a PMOS pass-transistor. Appends it to file 'filename'. """

	# Open the file for appending
	spice_file = open(filename, 'a')  

	if not use_finfet :
		spice_file.write("******************************************************************************************\n")
		spice_file.write("* PMOS Pass-transistor\n")
		spice_file.write("******************************************************************************************\n")
		spice_file.write(".SUBCKT ptranp n_in n_out n_gate n_vdd Wn=45n \n")
		spice_file.write("MPPASS n_in n_gate n_out n_vdd pmos L=gate_length W=Wn ")
		spice_file.write("AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length\n")
		spice_file.write(".ENDS\n\n\n")   
	else :
		spice_file.write("******************************************************************************************\n")
		spice_file.write("* PMOS Pass-transistor\n")
		spice_file.write("******************************************************************************************\n")
		spice_file.write(".SUBCKT ptranp n_in n_out n_gate n_vdd Wn=1\n")
		spice_file.write("MPPASS n_in n_gate n_out n_vdd pmos L=gate_length nfin=Wn ")
		spice_file.write("ASEO=Wn*min_tran_width*trans_diffusion_length ADEO=Wn*min_tran_width*trans_diffusion_length PSEO='Wn*(min_tran_width+2*trans_diffusion_length)' PDEO='Wn*(min_tran_width+2*trans_diffusion_length)'\n")
		spice_file.write(".ENDS\n\n\n")   

	spice_file.close()

def tgate_generate(filename, use_finfet):
	""" Generates the SPICE subcircuit for a transmission gate. Appends it to file 'filename'. """

	# Open the file for appending
	spice_file = open(filename, 'a')  

	if not use_finfet :
		spice_file.write("******************************************************************************************\n")
		spice_file.write("* Transmission gate\n")
		spice_file.write("******************************************************************************************\n")
		spice_file.write(".SUBCKT tgate n_in n_out n_gate_nmos n_gate_pmos n_vdd n_gnd Wn=45n Wp=45n\n")
		spice_file.write("MNTGATE n_in n_gate_nmos n_out n_gnd nmos L=gate_length W=Wn ")
		spice_file.write("AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length\n")
		spice_file.write("MPTGATE n_in n_gate_pmos n_out n_vdd pmos L=gate_length W=Wp ")
		spice_file.write("AS=Wp*trans_diffusion_length AD=Wp*trans_diffusion_length PS=Wp+2*trans_diffusion_length PD=Wp+2*trans_diffusion_length\n")
		spice_file.write(".ENDS\n\n\n")   
	else :
		spice_file.write("******************************************************************************************\n")
		spice_file.write("* Transmission gate\n")
		spice_file.write("******************************************************************************************\n")
		spice_file.write(".SUBCKT tgate n_in n_out n_gate_nmos n_gate_pmos n_vdd n_gnd Wn=1 Wp=1\n")
		spice_file.write("MNTGATE n_in n_gate_nmos n_out n_gnd nmos L=gate_length nfin=Wn ")
		spice_file.write("ASEO=Wn*min_tran_width*trans_diffusion_length ADEO=Wn*min_tran_width*trans_diffusion_length PSEO='Wn*(min_tran_width+2*trans_diffusion_length)' PDEO='Wn*(min_tran_width+2*trans_diffusion_length)'\n")
		spice_file.write("MPTGATE n_in n_gate_pmos n_out n_vdd pmos L=gate_length nfin=Wp ")
		spice_file.write("ASEO=Wp*min_tran_width*trans_diffusion_length ADEO=Wp*min_tran_width*trans_diffusion_length PSEO='Wp*(min_tran_width+2*trans_diffusion_length)' PDEO='Wp*(min_tran_width+2*trans_diffusion_length)'\n")
		spice_file.write(".ENDS\n\n\n")

	spice_file.close()


def tgate_generate_lp(filename, use_finfet):
	""" Generates the SPICE subcircuit for a transmission gate. Appends it to file 'filename'. """

	# Open the file for appending
	spice_file = open(filename, 'a')  

	if not use_finfet :
		spice_file.write("******************************************************************************************\n")
		spice_file.write("* Transmission gate\n")
		spice_file.write("******************************************************************************************\n")
		spice_file.write(".SUBCKT tgate_lp n_in n_out n_gate_nmos n_gate_pmos n_vdd n_gnd Wn=45n Wp=45n\n")
		spice_file.write("MNTGATE n_in n_gate_nmos n_out n_gnd nmos_lp L=gate_length W=Wn ")
		spice_file.write("AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length\n")
		spice_file.write("MPTGATE n_in n_gate_pmos n_out n_vdd pmos_lp L=gate_length W=Wp ")
		spice_file.write("AS=Wp*trans_diffusion_length AD=Wp*trans_diffusion_length PS=Wp+2*trans_diffusion_length PD=Wp+2*trans_diffusion_length\n")
		spice_file.write(".ENDS\n\n\n")   
	else :
		spice_file.write("******************************************************************************************\n")
		spice_file.write("* Transmission gate\n")
		spice_file.write("******************************************************************************************\n")
		spice_file.write(".SUBCKT tgate_lp n_in n_out n_gate_nmos n_gate_pmos n_vdd n_gnd Wn=1 Wp=1\n")
		spice_file.write("MNTGATE n_in n_gate_nmos n_out n_gnd nmos_lp L=gate_length nfin=Wn ")
		spice_file.write("ASEO=Wn*min_tran_width*trans_diffusion_length ADEO=Wn*min_tran_width*trans_diffusion_length PSEO='Wn*(min_tran_width+2*trans_diffusion_length)' PDEO='Wn*(min_tran_width+2*trans_diffusion_length)'\n")
		spice_file.write("MPTGATE n_in n_gate_pmos n_out n_vdd pmos_lp L=gate_length nfin=Wp ")
		spice_file.write("ASEO=Wp*min_tran_width*trans_diffusion_length ADEO=Wp*min_tran_width*trans_diffusion_length PSEO='Wp*(min_tran_width+2*trans_diffusion_length)' PDEO='Wp*(min_tran_width+2*trans_diffusion_length)'\n")
		spice_file.write(".ENDS\n\n\n")

	spice_file.close()


def RAM_tgate_generate(filename, use_finfet):
	""" Generates the SPICE subcircuit for a transmission gate used in the RAM cell. Appends it to file 'filename'. """

	# Open the file for appending
	spice_file = open(filename, 'a')  

	if not use_finfet :
		spice_file.write("******************************************************************************************\n")
		spice_file.write("* Transmission gate\n")
		spice_file.write("******************************************************************************************\n")
		spice_file.write(".SUBCKT RAM_tgate n_in n_out n_gate_nmos n_gate_pmos n_vdd n_gnd Wn=200n Wp=250n\n")
		spice_file.write("MNTGATE n_in n_gate_nmos n_out n_gnd nmos L=gate_length W=Wn ")
		spice_file.write("AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length\n")
		spice_file.write("MPTGATE n_in n_gate_pmos n_out n_vdd pmos L=gate_length W=Wp ")
		spice_file.write("AS=Wp*trans_diffusion_length AD=Wp*trans_diffusion_length PS=Wp+2*trans_diffusion_length PD=Wp+2*trans_diffusion_length\n")
		spice_file.write(".ENDS\n\n\n")   
	else :
		spice_file.write("******************************************************************************************\n")
		spice_file.write("* Transmission gate\n")
		spice_file.write("******************************************************************************************\n")
		spice_file.write(".SUBCKT RAM_tgate n_in n_out n_gate_nmos n_gate_pmos n_vdd n_gnd Wn=1 Wp=1\n")
		spice_file.write("MNTGATE n_in n_gate_nmos n_out n_gnd nmos L=gate_length nfin=Wn ")
		spice_file.write("ASEO=Wn*min_tran_width*trans_diffusion_length ADEO=Wn*min_tran_width*trans_diffusion_length PSEO='Wn*(min_tran_width+2*trans_diffusion_length)' PDEO='Wn*(min_tran_width+2*trans_diffusion_length)'\n")
		spice_file.write("MPTGATE n_in n_gate_pmos n_out n_vdd pmos L=gate_length nfin=Wp ")
		spice_file.write("ASEO=Wp*min_tran_width*trans_diffusion_length ADEO=Wp*min_tran_width*trans_diffusion_length PSEO='Wp*(min_tran_width+2*trans_diffusion_length)' PDEO='Wp*(min_tran_width+2*trans_diffusion_length)'\n")
		spice_file.write(".ENDS\n\n\n")

	spice_file.close()

def RAM_tgate_generate_lp(filename, use_finfet):
	""" Generates the SPICE subcircuit for a transmission gate used in the RAM cell. Appends it to file 'filename'. """

	# Open the file for appending
	spice_file = open(filename, 'a')  

	if not use_finfet :
		spice_file.write("******************************************************************************************\n")
		spice_file.write("* Transmission gate\n")
		spice_file.write("******************************************************************************************\n")
		spice_file.write(".SUBCKT RAM_tgate_lp n_in n_out n_gate_nmos n_gate_pmos n_vdd n_gnd Wn=200n Wp=250n\n")
		spice_file.write("MNTGATE n_in n_gate_nmos n_out n_gnd nmos_lp L=gate_length W=Wn ")
		spice_file.write("AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length\n")
		spice_file.write("MPTGATE n_in n_gate_pmos n_out n_vdd pmos_lp L=gate_length W=Wp ")
		spice_file.write("AS=Wp*trans_diffusion_length AD=Wp*trans_diffusion_length PS=Wp+2*trans_diffusion_length PD=Wp+2*trans_diffusion_length\n")
		spice_file.write(".ENDS\n\n\n")   
	else :
		spice_file.write("******************************************************************************************\n")
		spice_file.write("* Transmission gate\n")
		spice_file.write("******************************************************************************************\n")
		spice_file.write(".SUBCKT RAM_tgate_lp n_in n_out n_gate_nmos n_gate_pmos n_vdd n_gnd Wn=1 Wp=1\n")
		spice_file.write("MNTGATE n_in n_gate_nmos n_out n_gnd nmos_lp L=gate_length nfin=Wn ")
		spice_file.write("ASEO=Wn*min_tran_width*trans_diffusion_length ADEO=Wn*min_tran_width*trans_diffusion_length PSEO='Wn*(min_tran_width+2*trans_diffusion_length)' PDEO='Wn*(min_tran_width+2*trans_diffusion_length)'\n")
		spice_file.write("MPTGATE n_in n_gate_pmos n_out n_vdd pmos_lp L=gate_length nfin=Wp ")
		spice_file.write("ASEO=Wp*min_tran_width*trans_diffusion_length ADEO=Wp*min_tran_width*trans_diffusion_length PSEO='Wp*(min_tran_width+2*trans_diffusion_length)' PDEO='Wp*(min_tran_width+2*trans_diffusion_length)'\n")
		spice_file.write(".ENDS\n\n\n")

	spice_file.close()
