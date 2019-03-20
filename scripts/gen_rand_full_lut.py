# lut_mask = [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
# lut_mask = [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0]
# lut_mask = [1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0]
# lut_mask = [1,1,1,1,0,0,0,0,1,1,1,1,0,0,0,0,1,1,1,1,0,0,0,0,1,1,1,1,0,0,0,0,1,1,1,1,0,0,0,0,1,1,1,1,0,0,0,0,1,1,1,1,0,0,0,0,1,1,1,1,0,0,0,0]
# lut_mask = [1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0]
# lut_mask = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
# lut_mask = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
# lut_mask = [0,1,1,0,1,0,0,1,1,0,0,1,0,1,1,0,1,0,0,1,0,1,1,0,0,1,1,0,1,0,0,1,1,0,0,1,0,1,1,0,0,1,1,0,1,0,0,1,0,1,1,0,1,0,0,1,1,0,0,1,0,1,1,0,] #XOR

import math
import random
import sys
import numpy as np

def generate_headers(spice_file):
	spice_file.write(".TITLE rand_lut\n" )
	spice_file.write(".LIB \"../includes.l\" INCLUDES\n")
	spice_file.write(".TRAN 1p 16n SWEEP DATA=sweep_data\n")
	spice_file.write(".OPTIONS BRIEF=1\n")
	spice_file.write("V_LUT n_vdd gnd supply_v\n")
	spice_file.write("VIN_GATE_R n_in_rise gnd PULSE (supply_v 0 3n 0 0 2n 4n)\n")
	spice_file.write("VIN_GATE_F n_in_fall gnd PULSE (0 supply_v 3n 0 0 2n 4n)\n")
	spice_file.write("VIN_GATE_H n_in_high gnd supply_v\n")
	spice_file.write("VIN_GATE_L n_in_low gnd 0\n")
	spice_file.write(".MEASURE TRAN meas_current1 INTEGRAL I(V_LUT) FROM=5ns TO=7ns\n")
	spice_file.write(".MEASURE TRAN meas_current2 INTEGRAL I(V_LUT) FROM=11ns TO=13ns\n")
	spice_file.write(".MEASURE TRAN meas_avg_power PARAM = '-((meas_current1 + meas_current2)/4n)*supply_v'\n")
	spice_file.write("\n")

def generate_drivers(spice_file, input_vector, input_driver):
	drivers = ["a","b","c","d","e","f"]
	sources_toggle = ["n_in_rise", "n_in_fall"]
	sources_static = ["n_in_low", "n_in_high"]

	driver_index = 0
	for d in drivers:
		if (input_driver == d):
			s = sources_toggle[input_vector[driver_index]]
		else:
			s = sources_static[input_vector[driver_index]]
		spice_file.write("Xcb_mux_on_" + d + " " + s + " n_1_1_d_" + d + " vsram vsram_n vdd gnd cb_mux_on\n")
		spice_file.write("Xlocal_routing_wire_load_" + d + " n_1_1_d_" + d + " n_1_2_d_" + d + " vsram vsram_n vdd gnd vdd local_routing_wire_load\n")
		spice_file.write("Xlut_" + d + "_driver_1 n_1_2_d_" + d + " n_" + d + " vsram vsram_n n_rsel n_2_1_d_" + d + " vdd gnd lut_" + d + "_driver\n")
		spice_file.write("Xlut_" + d + "_driver_not_1 n_2_1_d_" + d + " n_" + d + "_b vdd gnd lut_" + d + "_driver_not\n")
		spice_file.write("\n")
		driver_index += 1


def generate_footers(spice_file):
	spice_file.write("Xlut_output_load n_out n_local_out n_general_out vsram vsram_n vdd gnd vdd vdd lut_output_load\n")
	spice_file.write(".OPTIONS POST=2 \n")
	spice_file.write(".END\n")
	spice_file.write("\n")

def generate_full_lut(spice_file, lut_mask):


	sram_cell_count = 1;
	lut_size = 6
	lvl_curr = lut_size

	lut_mask_index = 0;
	# level 1
	for i in range(1, 2**(lvl_curr-1)+1):
		if (lut_mask[lut_mask_index] == 1):
			spice_file.write("Xinv_sram_driver_1_"+str(i)+" vdd n_inter_" + str(sram_cell_count) + " n_vdd gnd inv Wn=45n Wp=75.015n\n")
		else:
			spice_file.write("Xinv_sram_driver_1_"+str(i)+" gnd n_inter_" + str(sram_cell_count) + " n_vdd gnd inv Wn=45n Wp=75.015n\n")	
		lut_mask_index += 1
		spice_file.write("Xwire_sram_driver_1_"+str(i)+" n_inter_"+ str(sram_cell_count) + " n_inter_2_" + str(sram_cell_count) + " wire Rw=wire_lut_sram_driver_res Cw=wire_lut_sram_driver_cap\n")		
		spice_file.write("Xinv_sram_driver_2_"+str(i)+" n_inter_2_"+ str(sram_cell_count) + " n_inter_3_" + str(sram_cell_count) + " n_vdd gnd inv Wn=inv_lut_0sram_driver_2_nmos Wp=inv_lut_0sram_driver_2_pmos\n")
		spice_file.write("Xwire_sram_driver_2_"+str(i)+" n_inter_3_"+ str(sram_cell_count) + " n_0_" + str(sram_cell_count) + " wire Rw=wire_lut_sram_driver_out_res Cw=wire_lut_sram_driver_out_cap\n")		
		
		if (lut_mask[lut_mask_index] == 1):
			spice_file.write("Xinv_sram_driver_1_2_"+str(i)+" vdd n_inter_" + str(sram_cell_count+1) + " n_vdd gnd inv Wn=45n Wp=75.015n\n")
		else:
			spice_file.write("Xinv_sram_driver_1_2_"+str(i)+" gnd n_inter_" + str(sram_cell_count+1) + " n_vdd gnd inv Wn=45n Wp=75.015n\n")
		lut_mask_index += 1

		spice_file.write("Xwire_sram_driver_1_2_"+str(i)+" n_inter_"+ str(sram_cell_count+1) + " n_inter_2_" + str(sram_cell_count+1) + " wire Rw=wire_lut_sram_driver_res Cw=wire_lut_sram_driver_cap\n")		
		spice_file.write("Xinv_sram_driver_2_2_"+str(i)+" n_inter_2_"+ str(sram_cell_count+1) + " n_inter_3_" + str(sram_cell_count+1) + " n_vdd gnd inv Wn=inv_lut_0sram_driver_2_nmos Wp=inv_lut_0sram_driver_2_pmos\n")
		spice_file.write("Xwire_sram_driver_2_2_"+str(i)+" n_inter_3_"+ str(sram_cell_count+1) + " n_0_" + str(sram_cell_count+1) + " wire Rw=wire_lut_sram_driver_out_res Cw=wire_lut_sram_driver_out_cap\n")		

		spice_file.write("Xlvl1_"+str(i)+"_mux n_0_"+ str(sram_cell_count) + " n_0_" + str(sram_cell_count+1) + " n_a" + " n_a_b" + " n_1_" + str(i) + " gnd simple_mux Wn=ptran_lut_L1_nmos Rw='wire_lut_L1_res/2' Cw='wire_lut_L1_cap/2'\n")
		sram_cell_count = sram_cell_count + 2

	# level 2
	lvl_curr=lvl_curr -1
	sram_cell_count = 1
	for i in range(1, 2**(lvl_curr-1)+1):
		spice_file.write("Xlvl2_"+str(i)+"_mux n_1_"+ str(sram_cell_count) + " n_1_" + str(sram_cell_count+1) + " n_b" + " n_b_b" + " n_2_" + str(i) + " gnd simple_mux Wn=ptran_lut_L2_nmos Rw='wire_lut_L2_res/2' Cw='wire_lut_L2_cap/2'\n")
		sram_cell_count = sram_cell_count + 2
		
	# level 3
	lvl_curr=lvl_curr -1	
	sram_cell_count = 1
	for i in range(1, 2**(lvl_curr-1)+1):
		spice_file.write("Xlvl3_"+str(i)+"_mux n_2_"+ str(sram_cell_count) + " n_2_" + str(sram_cell_count+1) + " n_c" + " n_c_b" + " n_3_" + str(i) + " gnd simple_mux Wn=ptran_lut_L3_nmos Rw='wire_lut_L3_res/2' Cw='wire_lut_L3_cap/2'\n")
		sram_cell_count = sram_cell_count + 2	
	
	# internal_buff
	sram_cell_count = 1
	for i in range(1, 2**(lvl_curr-1)+1):
		spice_file.write("Xlut_buffer_"+str(i)+" n_3_"+ str(sram_cell_count) + " n_3_buff_" + str(sram_cell_count)+ " n_vdd gnd lut_buffer rest_lut_size=rest_lut_int_buffer_pmos inv_1_nmos=inv_lut_int_buffer_1_nmos inv_1_pmos=inv_lut_int_buffer_1_pmos Rw_int=wire_lut_int_buffer_res Cw_int=wire_lut_int_buffer_cap inv_2_nmos=inv_lut_int_buffer_2_nmos inv_2_pmos=inv_lut_int_buffer_2_pmos Rw_out=wire_lut_int_buffer_out_res Cw_out=wire_lut_int_buffer_out_cap \n")
		sram_cell_count = sram_cell_count + 1
		
	# level 4
	lvl_curr=lvl_curr -1
	sram_cell_count = 1
	for i in range(1, 2**(lvl_curr-1)+1):
		spice_file.write("Xlvl4_"+str(i)+"_mux n_3_buff_"+ str(sram_cell_count) + " n_3_buff_" + str(sram_cell_count+1) + " n_d" + " n_d_b" + " n_4_" + str(i) + " gnd simple_mux Wn=ptran_lut_L4_nmos Rw='wire_lut_L4_res/2' Cw='wire_lut_L4_cap/2'\n")
		sram_cell_count = sram_cell_count + 2		
		
	# level 5
	lvl_curr=lvl_curr -1
	sram_cell_count = 1
	for i in range(1, 2**(lvl_curr-1)+1):
		spice_file.write("Xlvl5_"+str(i)+"_mux n_4_"+ str(sram_cell_count) + " n_4_" + str(sram_cell_count+1) + " n_e" + " n_e_b" + " n_5_" + str(i) + " gnd simple_mux Wn=ptran_lut_L5_nmos Rw='wire_lut_L5_res/2' Cw='wire_lut_L5_cap/2'\n")
		sram_cell_count = sram_cell_count + 2			
		
	# level 6
	lvl_curr=lvl_curr -1
	sram_cell_count = 1
	for i in range(1, 2**(lvl_curr-1)+1):
		spice_file.write("Xlvl6_"+str(i)+"_mux n_5_"+ str(sram_cell_count) + " n_5_" + str(sram_cell_count+1) + " n_f" + " n_f_b" + " n_6_" + str(i) + " gnd simple_mux Wn=ptran_lut_L6_nmos Rw='wire_lut_L6_res/2' Cw='wire_lut_L6_cap/2'\n")
		sram_cell_count = sram_cell_count + 2			

	# output_buff
	sram_cell_count = 1
	for i in range(1, 2**(lvl_curr-1)+1):
		spice_file.write("Xlut_buffer_"+str(i)+"_out n_6_"+ str(sram_cell_count) + " n_out n_vdd gnd " +  " lut_buffer rest_lut_size=rest_lut_out_buffer_pmos inv_1_nmos=inv_lut_out_buffer_1_nmos inv_1_pmos=inv_lut_out_buffer_1_pmos Rw_int=wire_lut_out_buffer_res Cw_int=wire_lut_out_buffer_cap inv_2_nmos=inv_lut_out_buffer_2_nmos inv_2_pmos=inv_lut_out_buffer_2_pmos Rw_out=0 Cw_out=0 \n")
		sram_cell_count = sram_cell_count + 1	
		

def generate_spice_file(spice_file, input_vector, driver, lut_mask):
	generate_headers(spice_file)
	generate_drivers(spice_file, input_vector, driver)
	generate_full_lut(spice_file, lut_mask)
	generate_footers(spice_file)

		
np.random.seed(int(sys.argv[1]))

lut_mask = np.random.randint(0,2,64)
input_vector = np.random.randint(0,2,6)

drivers = ["a","b","c","d","e","f","x"]

for d in drivers:
	spice_file = open("rand_lut_" + d + ".sp", 'w')
	generate_spice_file(spice_file, input_vector, d, lut_mask)
	spice_file.close()

