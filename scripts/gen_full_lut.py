import math

def generate_full_lut(spice_file_name):

	spice_file = open(spice_file_name, 'w')
	sram_cell_count = 1;
	lut_size = 6
	lvl_curr = lut_size
	# level 1
	for i in range(1, 2**(lvl_curr-1)+1):
		#spice_file.write("Xinv_sram_driver_1_"+str(i)+" n_sram_"+ str(sram_cell_count) + " n_inter_" + str(sram_cell_count) + " n_vdd gnd inv Wn=45n Wp=75.015'\n")
		if (math.ceil(i%2)==0):
			spice_file.write("Xinv_sram_driver_1_"+str(i)+" vdd n_inter_" + str(sram_cell_count) + " n_vdd gnd inv Wn=45n Wp=75.015n\n")
		else:
			spice_file.write("Xinv_sram_driver_1_"+str(i)+" gnd n_inter_" + str(sram_cell_count) + " n_vdd gnd inv Wn=45n Wp=75.015n\n")	
		spice_file.write("Xwire_sram_driver_1_"+str(i)+" n_inter_"+ str(sram_cell_count) + " n_inter_2_" + str(sram_cell_count) + " wire Rw=wire_lut_sram_driver_res Cw=wire_lut_sram_driver_cap\n")		
		spice_file.write("Xinv_sram_driver_2_"+str(i)+" n_inter_2_"+ str(sram_cell_count) + " n_inter_3_" + str(sram_cell_count) + " n_vdd gnd inv Wn=inv_lut_0sram_driver_2_nmos Wp=inv_lut_0sram_driver_2_pmos\n")
		spice_file.write("Xwire_sram_driver_2_"+str(i)+" n_inter_3_"+ str(sram_cell_count) + " n_0_" + str(sram_cell_count) + " wire Rw=wire_lut_sram_driver_out_res Cw=wire_lut_sram_driver_out_cap\n")		
		
		#spice_file.write("Xinv_sram_driver_1_"+str(i)+" n_sram_"+ str(sram_cell_count+1) + " n_inter_" + str(sram_cell_count+1) + " n_vdd gnd inv Wn=45n Wp=75.015'\n")
				#spice_file.write("Xinv_sram_driver_1_"+str(i)+" n_sram_"+ str(sram_cell_count) + " n_inter_" + str(sram_cell_count) + " n_vdd gnd inv Wn=45n Wp=75.015'\n")
		if (math.ceil(i%2)==0):
			spice_file.write("Xinv_sram_driver_1_2_"+str(i)+" gnd n_inter_" + str(sram_cell_count+1) + " n_vdd gnd inv Wn=45n Wp=75.015n\n")
		else:
			spice_file.write("Xinv_sram_driver_1_2_"+str(i)+" vdd n_inter_" + str(sram_cell_count+1) + " n_vdd gnd inv Wn=45n Wp=75.015n\n")

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
		sram_cell_count = sram_cell_count + 2
		
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
		sram_cell_count = sram_cell_count + 2	
		
		
		
		
		
generate_full_lut("test.sp")		