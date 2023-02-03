import sys
import os

def print_vpr_file_memory(vpr_file, fpga_inst):

	# get delay values
	Tdel = fpga_inst.sb_mux.delay
	T_ipin_cblock = fpga_inst.cb_mux.delay
	local_CLB_routing = fpga_inst.logic_cluster.local_mux.delay
	local_feedback = fpga_inst.logic_cluster.ble.local_output.delay
	logic_block_output = fpga_inst.logic_cluster.ble.general_output.delay

	# get lut delays
	lut_input_names = list(fpga_inst.logic_cluster.ble.lut.input_drivers.keys())
	lut_input_names.sort()
	lut_delays = {}
	for input_name in lut_input_names:
		lut_input = fpga_inst.logic_cluster.ble.lut.input_drivers[input_name]
		driver_delay = max(lut_input.driver.delay, lut_input.not_driver.delay)
		path_delay = lut_input.delay
		lut_delays[input_name] = driver_delay+path_delay

	# get archetecture parameters
	Rfb = fpga_inst.specs.Rfb
	Fcin = fpga_inst.specs.Fcin
	Fcout = fpga_inst.specs.Fcout
	Fs = fpga_inst.specs.Fs
	N = fpga_inst.specs.N
	K = fpga_inst.specs.K
	L = fpga_inst.specs.L

		
	# get areas
	grid_logic_tile_area = fpga_inst.area_dict["logic_cluster"]/fpga_inst.specs.min_width_tran_area
	if grid_logic_tile_area < 1.00 :
		grid_logic_tile_area = 1.00
	ipin_mux_trans_size = fpga_inst.area_dict["ipin_mux_trans_size"]/fpga_inst.specs.min_width_tran_area
	if ipin_mux_trans_size < 1.00 :
		ipin_mux_trans_size = 1.00
	mux_trans_size = fpga_inst.area_dict["switch_mux_trans_size"]/fpga_inst.specs.min_width_tran_area
	if mux_trans_size < 1.00 :
		mux_trans_size = 1.00
	buf_size = fpga_inst.area_dict["switch_buf_size"]/fpga_inst.specs.min_width_tran_area
	if buf_size < 1.00 :
		buf_size = 1.00

	# get memory information
	memory_height = int(round(fpga_inst.area_dict["ram"]/fpga_inst.area_dict["tile"], 0))
	memory_max_width =  2 ** fpga_inst.RAM.conf_decoder_bits
	memory_address_bits = fpga_inst.specs.row_decoder_bits + fpga_inst.specs.col_decoder_bits + fpga_inst.specs.conf_decoder_bits
	memory_max_depth = 2 ** (fpga_inst.specs.row_decoder_bits + fpga_inst.specs.col_decoder_bits + fpga_inst.specs.conf_decoder_bits)
	memory_clktoq = fpga_inst.RAM.frequency
	memory_setup_time = fpga_inst.RAM.RAM_local_mux.delay + 52.3e-12
	memory_input_mux_size = 25
	# Todo: I can add output mux size and create a crossbar at the output. Not sure if it will actually help. 
	cb_buf_size = fpga_inst.area_dict["cb_buf_size"]/fpga_inst.specs.min_width_tran_area
	if cb_buf_size < 1.00:
		cb_buf_size = 1.00

	vpr_file.write("<architecture>  \n")
	vpr_file.write("<!-- ODIN II specific config -->\n")
	vpr_file.write("<models>\n")
	vpr_file.write("  <model name=\"multiply\">\n")
	vpr_file.write("    <input_ports>\n")
	vpr_file.write("    <port name=\"a\" combinational_sink_ports=\"out\"/> \n")
	vpr_file.write("    <port name=\"b\" combinational_sink_ports=\"out\"/>\n")
	vpr_file.write("    </input_ports>\n")
	vpr_file.write("    <output_ports>\n")
	vpr_file.write("    <port name=\"out\"/>\n")
	vpr_file.write("    </output_ports>\n")
	vpr_file.write("  </model>\n")
	    
	vpr_file.write("<model name=\"single_port_ram\">\n")
	vpr_file.write("  <input_ports>\n")
	vpr_file.write("  <port name=\"we\" clock=\"clk\"/>     <!-- control -->\n")
	vpr_file.write("  <port name=\"addr\" clock=\"clk\"/>  <!-- address lines -->\n")
	vpr_file.write("  <port name=\"data\" clock=\"clk\"/>  <!-- data lines can be broken down into smaller bit widths minimum size 1 -->\n")
	vpr_file.write("  <port name=\"clk\" is_clock=\"1\"/>  <!-- memories are often clocked -->\n")
	vpr_file.write("  </input_ports>\n")
	vpr_file.write("  <output_ports>\n")
	vpr_file.write("  <port name=\"out\" clock=\"clk\"/>   <!-- output can be broken down into smaller bit widths minimum size 1 -->\n")
	vpr_file.write("  </output_ports>\n")
	vpr_file.write("</model>\n")

	vpr_file.write("<model name=\"dual_port_ram\">\n")
	vpr_file.write("  <input_ports>\n")
	vpr_file.write("  <port name=\"we1\" clock=\"clk\"/>     <!-- write enable -->\n")
	vpr_file.write("  <port name=\"we2\" clock=\"clk\"/>     <!-- write enable -->\n")
	vpr_file.write("  <port name=\"addr1\" clock=\"clk\"/>  <!-- address lines -->\n")
	vpr_file.write("  <port name=\"addr2\" clock=\"clk\"/>  <!-- address lines -->\n")
	vpr_file.write("  <port name=\"data1\" clock=\"clk\"/>  <!-- data lines can be broken down into smaller bit widths minimum size 1 -->\n")
	vpr_file.write("  <port name=\"data2\" clock=\"clk\"/>  <!-- data lines can be broken down into smaller bit widths minimum size 1 -->\n")
	vpr_file.write("  <port name=\"clk\" is_clock=\"1\"/>  <!-- memories are often clocked -->\n")
	vpr_file.write("  </input_ports>\n")
	vpr_file.write("  <output_ports>\n")
	vpr_file.write("  <port name=\"out1\" clock=\"clk\"/>   <!-- output can be broken down into smaller bit widths minimum size 1 -->\n")
	vpr_file.write("  <port name=\"out2\" clock=\"clk\"/>   <!-- output can be broken down into smaller bit widths minimum size 1 -->\n")
	vpr_file.write("  </output_ports>\n")
	vpr_file.write("</model>\n")

	vpr_file.write("</models>\n")
	vpr_file.write("<!-- ODIN II specific config ends -->\n")
	vpr_file.write("<!-- Physical descriptions begin -->\n")
	vpr_file.write("<layout>\n")
	vpr_file.write("<auto_layout aspect_ratio=\"1.0\">\n")
	vpr_file.write("<perimeter type=\"io\" priority=\"100\"/>\n")
	vpr_file.write("<corners type=\"EMPTY\" priority=\"101\"/>\n")
	vpr_file.write("<fill type=\"clb\" priority=\"10\"/>\n")
	vpr_file.write("<col type=\"mult_36\" startx=\"4\" starty=\"1\" repeatx=\"8\" priority=\"20\" />\n")
	vpr_file.write("<col type=\"EMPTY\" startx=\"4\" starty=\"1\" repeatx=\"8\" priority=\"19\" />\n")
	vpr_file.write("<col type=\"memory\" startx=\"2\" starty=\"1\" repeatx=\"8\" priority=\"20\" />\n")
	vpr_file.write("<col type=\"EMPTY\" startx=\"2\" starty=\"1\" repeatx=\"8\" priority=\"19\" />\n")
	vpr_file.write("</auto_layout>\n")
	vpr_file.write("</layout>\n")

	vpr_file.write("  <device>\n")
	vpr_file.write("    <sizing R_minW_nmos=\"13090.000000\" R_minW_pmos=\"19086.831111\"/> \n") #ipin_mux_trans_size=\"" + str(ipin_mux_trans_size)+ "\"/>\n
	vpr_file.write("    <area grid_logic_tile_area=\"" + str(grid_logic_tile_area) +"\"/>\n")
	vpr_file.write("    <chan_width_distr>\n")
	vpr_file.write("      <x distr=\"uniform\" peak=\"1.000000\"/>\n")
	vpr_file.write("      <y distr=\"uniform\" peak=\"1.000000\"/>\n")
	vpr_file.write("    </chan_width_distr>\n")
	vpr_file.write("    <switch_block type=\"wilton\" fs=\"" + str(Fs) + "\"/>\n")
	vpr_file.write("    <connection_block input_switch_name=\"ipin_cblock\"/>\n")
	vpr_file.write("  </device>\n")

	
	vpr_file.write("  <switchlist>\n")
	vpr_file.write("    <switch type=\"mux\" name=\"0\" R=\"0.000000\" Cin=\"0.000000e+00\" Cout=\"0.000000e+00\" Tdel=\"" + str(Tdel) + "\" mux_trans_size=\"" + str(mux_trans_size) + "\" buf_size=\"" + str(buf_size) + "\"/>\n")
	vpr_file.write("    <switch type=\"mux\" name=\"ipin_cblock\" R=\"0.000000\" Cin=\"0.000000e+00\" Cout=\"0.000000e+00\" Tdel=\"" + str(T_ipin_cblock) + "\" mux_trans_size=\"" + str(ipin_mux_trans_size) + "\" buf_size=\"" + str(cb_buf_size) + "\"/>\n")
	vpr_file.write("  </switchlist>\n")

	vpr_file.write("  <segmentlist>\n")
	vpr_file.write("    <segment freq=\"1.000000\" length=\"" + str(L) + "\" type=\"unidir\" Rmetal=\"0.000000\" Cmetal=\"0.000000e+00\">\n")
	vpr_file.write("    <mux name=\"0\"/>\n")
	vpr_file.write("    <sb type=\"pattern\">1 1 1 1 1</sb>\n")
	vpr_file.write("    <cb type=\"pattern\">1 1 1 1</cb>\n")
	vpr_file.write("    </segment>\n")
	vpr_file.write("  </segmentlist>\n")

	vpr_file.write("  <complexblocklist>\n")
	vpr_file.write("      <!-- Capacity is a unique property of I/Os, it is the maximum number of I/Os that can be placed at the same (X,Y) location on the FPGA -->\n")
	vpr_file.write("     <pb_type name=\"io\" capacity=\"8\">\n")
	vpr_file.write("       <input name=\"outpad\" num_pins=\"1\"/>\n")
	vpr_file.write("       <output name=\"inpad\" num_pins=\"1\"/>\n")
	vpr_file.write("       <clock name=\"clock\" num_pins=\"1\"/>\n")
	vpr_file.write("    <!-- IOs can operate as either inputs or outputs -->\n")
	vpr_file.write("    <mode name=\"inpad\">\n")
	vpr_file.write("      <pb_type name=\"inpad\" blif_model=\".input\" num_pb=\"1\">\n")
	vpr_file.write("        <output name=\"inpad\" num_pins=\"1\"/>\n")
	vpr_file.write("      </pb_type>\n")
	vpr_file.write("      <interconnect>\n")
	vpr_file.write("        <direct name=\"inpad\" input=\"inpad.inpad\" output=\"io.inpad\">\n")
	vpr_file.write("        <delay_constant max=\"4.243e-11\" in_port=\"inpad.inpad\" out_port=\"io.inpad\"/>\n")
	vpr_file.write("        </direct>\n")
	vpr_file.write("      </interconnect>  \n")
	vpr_file.write("    </mode>\n")
	vpr_file.write("    <mode name=\"outpad\">\n")
	vpr_file.write("      <pb_type name=\"outpad\" blif_model=\".output\" num_pb=\"1\">\n")
	vpr_file.write("        <input name=\"outpad\" num_pins=\"1\"/>\n")
	vpr_file.write("      </pb_type>\n")
	vpr_file.write("      <interconnect>\n")
	vpr_file.write("        <direct name=\"outpad\" input=\"io.outpad\" output=\"outpad.outpad\">\n")
	vpr_file.write("        <delay_constant max=\"1.394e-11\" in_port=\"io.outpad\" out_port=\"outpad.outpad\"/>\n")
	vpr_file.write("        </direct>\n")
	vpr_file.write("      </interconnect>\n")
	vpr_file.write("    </mode>\n")
	vpr_file.write("    <fc default_in_type=\"frac\" default_in_val=\"0.15\" default_out_type=\"frac\" default_out_val=\"0.10\"/>\n")
	vpr_file.write("    <!-- IOs go on the periphery of the FPGA, for consistency, \n")
	vpr_file.write("      make it physically equivalent on all sides so that only one definition of I/Os is needed.\n")
	vpr_file.write("      If I do not make a physically equivalent definition, then I need to define 4 different I/Os, one for each side of the FPGA\n")
	vpr_file.write("    -->\n")
	vpr_file.write("    <pinlocations pattern=\"custom\">\n")
	vpr_file.write("      <loc side=\"left\">io.outpad io.inpad io.clock</loc>\n")
	vpr_file.write("      <loc side=\"top\">io.outpad io.inpad io.clock</loc>\n")
	vpr_file.write("      <loc side=\"right\">io.outpad io.inpad io.clock</loc>\n")
	vpr_file.write("      <loc side=\"bottom\">io.outpad io.inpad io.clock</loc>\n")
	vpr_file.write("    </pinlocations>\n")

	vpr_file.write("  </pb_type>\n")
	vpr_file.write("  <!-- Logic cluster definition -->\n")
	vpr_file.write("  <pb_type name=\"clb\" area=\""+str(grid_logic_tile_area)+"\">\n")
	vpr_file.write("    <input name=\"I1\" num_pins=\"" + str(N) + "\" equivalent=\"true\"/>\n")
	vpr_file.write("    <input name=\"I2\" num_pins=\"" + str(N) + "\" equivalent=\"true\"/>\n")
	vpr_file.write("    <input name=\"I3\" num_pins=\"" + str(N) + "\" equivalent=\"true\"/>\n")
	vpr_file.write("    <input name=\"I4\" num_pins=\"" + str(N) + "\" equivalent=\"true\"/>\n")
	vpr_file.write("    <output name=\"O1\" num_pins=\"2\" equivalent=\"true\"/>\n")
	vpr_file.write("    <output name=\"O2\" num_pins=\"2\" equivalent=\"true\"/>\n")
	vpr_file.write("    <output name=\"O3\" num_pins=\"2\" equivalent=\"true\"/>\n")
	vpr_file.write("    <output name=\"O4\" num_pins=\"2\" equivalent=\"true\"/>\n")
	vpr_file.write("    <output name=\"O5\" num_pins=\"2\" equivalent=\"true\"/>\n")
	vpr_file.write("    <output name=\"O6\" num_pins=\"2\" equivalent=\"true\"/>\n")
	vpr_file.write("    <output name=\"O7\" num_pins=\"2\" equivalent=\"true\"/>\n")
	vpr_file.write("    <output name=\"O8\" num_pins=\"2\" equivalent=\"true\"/>\n")
	vpr_file.write("    <output name=\"O9\" num_pins=\"2\" equivalent=\"true\"/>\n")
	vpr_file.write("    <output name=\"O10\" num_pins=\"2\" equivalent=\"true\"/>\n")
	vpr_file.write("    <clock name=\"clk\" num_pins=\"1\"/>")

	vpr_file.write("  <!-- Basic logic element definition -->\n")
	vpr_file.write("  <pb_type name=\"ble6\" num_pb=\"" + str(N) + "\">\n")
	vpr_file.write("  <input name=\"in_A\" num_pins=\"1\" equivalent=\"false\"/>\n")
	vpr_file.write("  <input name=\"in_B\" num_pins=\"1\" equivalent=\"false\"/>\n")
	vpr_file.write("  <input name=\"in_C\" num_pins=\"1\" equivalent=\"false\"/>\n")
	vpr_file.write("  <input name=\"in_D\" num_pins=\"1\" equivalent=\"false\"/>\n")
	vpr_file.write("  <input name=\"in_E\" num_pins=\"1\" equivalent=\"false\"/>\n")
	vpr_file.write("  <input name=\"in_F\" num_pins=\"1\" equivalent=\"false\"/>\n")
	vpr_file.write("  <output name=\"out_local\" num_pins=\"1\" equivalent=\"false\"/>\n")
	vpr_file.write("  <output name=\"out_routing\" num_pins=\"2\" equivalent=\"true\"/>\n")
	vpr_file.write("  <clock name=\"clk\" num_pins=\"1\"/> \n")
	vpr_file.write("  <pb_type name=\"lut6\" blif_model=\".names\" num_pb=\"1\" class=\"lut\">\n")
	vpr_file.write("  <input name=\"in\" num_pins=\"" + str(K) + "\" port_class=\"lut_in\"/>\n")
	vpr_file.write("  <output name=\"out\" num_pins=\"1\" port_class=\"lut_out\"/>\n")
	vpr_file.write("  <!-- We define the LUT delays on the LUT pins instead of through the LUT -->\n")
	vpr_file.write("  <delay_matrix type=\"max\" in_port=\"lut6.in\" out_port=\"lut6.out\">\n")
	vpr_file.write("     0\n")
	vpr_file.write("     0\n")
	vpr_file.write("     0\n")
	vpr_file.write("     0\n")
	vpr_file.write("     0\n")
	vpr_file.write("     0\n")
	vpr_file.write("  </delay_matrix>\n")
	vpr_file.write("  </pb_type>\n")
	vpr_file.write("  <pb_type name=\"ff\" blif_model=\".latch\" num_pb=\"1\" class=\"flipflop\">\n")
	vpr_file.write("  <input name=\"D\" num_pins=\"1\" port_class=\"D\"/>\n")
	vpr_file.write("  <output name=\"Q\" num_pins=\"1\" port_class=\"Q\"/>\n")
	vpr_file.write("  <clock name=\"clk\" num_pins=\"1\" port_class=\"clock\"/>\n")
	vpr_file.write("  <T_setup value=\"1.891e-11\" port=\"ff.D\" clock=\"clk\"/>\n")
	vpr_file.write("  <T_clock_to_Q max=\"6.032e-11\" port=\"ff.Q\" clock=\"clk\"/>\n")
	vpr_file.write("  </pb_type>\n")

	vpr_file.write("      <interconnect>\n")


	feedback_mux = {}
	input_num = 0
	direct_num = 1
	for input_name in lut_input_names:
		if Rfb.count(input_name) != 1 :
			vpr_file.write("    <direct name=\"direct" + str(input_num) + "\" input=\"ble6.in_" + input_name.upper() + "\" output=\"lut6.in[" + str(input_num) + ":" + str(input_num) + "]\">\n")
			vpr_file.write("      <delay_constant max=\"" + str(lut_delays[input_name]) + "\" in_port=\"ble6.in_" + input_name.upper() + "\" out_port=\"lut6.in[" + str(input_num) + ":" + str(input_num) + "]\" />\n")
			vpr_file.write("    </direct>\n")
			direct_num = direct_num + 1

		else:
			feedback_mux[input_name] = input_num

		input_num = input_num + 1

	vpr_file.write("      <!--Clock -->\n")
	vpr_file.write("      <direct name=\"direct" + str(direct_num) + "\" input=\"ble6.clk\" output=\"ff.clk\"/>\n")


	mux_num = 1
	for name in feedback_mux :
		vpr_file.write("      <!-- Register feedback mux -->   \n")
		vpr_file.write("      <mux name=\"mux" + str(mux_num) + "\" input=\"ble6.in_" + name.upper() + " ff.Q\" output=\"lut6.in[" + str(feedback_mux[name]) + ":" + str(feedback_mux[name]) + "]\">\n")
		vpr_file.write("        <delay_constant max=\"" + str(lut_delays[name]) + "\" in_port=\"ble6.in_" + name.upper() + "\" out_port=\"lut6.in[" + str(feedback_mux[name]) + ":" + str(feedback_mux[name]) + "]\" />\n")
		vpr_file.write("        <delay_constant max=\"" + str(lut_delays[name]) + "\" in_port=\"ff.Q\" out_port=\"lut6.in[" + str(feedback_mux[name]) + ":" + str(feedback_mux[name]) + "]\" />  \n")
		vpr_file.write("      </mux>\n")
		mux_num = mux_num + 1
		vpr_file.write("      <!-- FF input selection mux -->\n")
		vpr_file.write("      <mux name=\"" + str(mux_num) + "\" input=\"lut6.out ble6.in_" + name.upper() + "\" output=\"ff.D\">\n")
		vpr_file.write("        <delay_constant max=\"1.74588e-11\" in_port=\"lut6.out\" out_port=\"ff.D\" />\n")
		vpr_file.write("        <delay_constant max=\"1.74588e-11\" in_port=\"ble6.in_" + name.upper() + "\" out_port=\"ff.D\" />\n")
		vpr_file.write("      </mux>\n")
		mux_num = mux_num + 1


	vpr_file.write("      <!-- BLE output (local) -->\n")
	vpr_file.write("      <mux name=\"mux" + str(mux_num) + "\" input=\"ff.Q lut6.out\" output=\"ble6.out_local\">\n")
	vpr_file.write("        <delay_constant max=\"" + str(local_feedback) + "\" in_port=\"ff.Q\" out_port=\"ble6.out_local\" />\n")
	vpr_file.write("        <delay_constant max=\"" + str(local_feedback) + "\" in_port=\"lut6.out\" out_port=\"ble6.out_local\" />\n")
	vpr_file.write("      </mux>\n")
	mux_num = mux_num + 1

	vpr_file.write("      <!-- BLE output (routing 1) --> \n")
	vpr_file.write("      <mux name=\"mux" + str(mux_num) + "\" input=\"ff.Q lut6.out\" output=\"ble6.out_routing[0:0]\">\n")
	vpr_file.write("        <delay_constant max=\"" + str(logic_block_output)+ "\" in_port=\"ff.Q\" out_port=\"ble6.out_routing[0:0]\" />\n")
	vpr_file.write("        <delay_constant max=\"" + str(logic_block_output)+ "\" in_port=\"lut6.out\" out_port=\"ble6.out_routing[0:0]\" />\n")
	vpr_file.write("      </mux>\n")
	mux_num = mux_num + 1

	vpr_file.write("      <!-- BLE output (routing 2) --> \n")
	vpr_file.write("      <mux name=\"mux" + str(mux_num) + "\" input=\"ff.Q lut6.out\" output=\"ble6.out_routing[1:1]\">\n")
	vpr_file.write("        <delay_constant max=\"" + str(logic_block_output)+ "\" in_port=\"ff.Q\" out_port=\"ble6.out_routing[1:1]\" />\n")
	vpr_file.write("        <delay_constant max=\"" + str(logic_block_output)+ "\" in_port=\"lut6.out\" out_port=\"ble6.out_routing[1:1]\" />\n")
	vpr_file.write("      </mux>\n")
	vpr_file.write("      </interconnect>\n")
	vpr_file.write("    </pb_type>\n")
        
	vpr_file.write("    <interconnect>\n")
	vpr_file.write("    <!-- 50% sparsely populated local routing -->\n")
	vpr_file.write("    <complete name=\"lutA\" input=\"clb.I4 clb.I3 ble6[1:0].out_local ble6[3:2].out_local ble6[8:8].out_local\" output=\"ble6[9:0].in_A\">\n")
	vpr_file.write("      <delay_constant max=\"" + str(local_CLB_routing) + "\" in_port=\"clb.I4\" out_port=\"ble6.in_A\" />\n")
	vpr_file.write("      <delay_constant max=\"" + str(local_CLB_routing) + "\" in_port=\"clb.I3\" out_port=\"ble6.in_A\" />\n")
	vpr_file.write("      </complete>\n")
	vpr_file.write("    <complete name=\"lutB\" input=\"clb.I3 clb.I2 ble6[3:2].out_local ble6[5:4].out_local ble6[9:9].out_local\" output=\"ble6[9:0].in_B\">\n")
	vpr_file.write("      <delay_constant max=\"" + str(local_CLB_routing) + "\" in_port=\"clb.I3\" out_port=\"ble6.in_B\" />\n")
	vpr_file.write("      <delay_constant max=\"" + str(local_CLB_routing) + "\" in_port=\"clb.I2\" out_port=\"ble6.in_B\" />\n")
	vpr_file.write("      </complete>\n")
	vpr_file.write("    <complete name=\"lutC\" input=\"clb.I2 clb.I1 ble6[5:4].out_local ble6[7:6].out_local ble6[8:8].out_local\" output=\"ble6[9:0].in_C\">\n")
	vpr_file.write("      <delay_constant max=\"" + str(local_CLB_routing) + "\" in_port=\"clb.I2\" out_port=\"ble6.in_C\" />\n")
	vpr_file.write("      <delay_constant max=\"" + str(local_CLB_routing) + "\" in_port=\"clb.I1\" out_port=\"ble6.in_C\" />\n")
	vpr_file.write("      </complete>\n")
	vpr_file.write("    <complete name=\"lutD\" input=\"clb.I4 clb.I2 ble6[1:0].out_local ble6[5:4].out_local ble6[9:9].out_local\" output=\"ble6[9:0].in_D\">\n")
	vpr_file.write("      <delay_constant max=\"" + str(local_CLB_routing) + "\" in_port=\"clb.I4\" out_port=\"ble6.in_D\" />\n")
	vpr_file.write("      <delay_constant max=\"" + str(local_CLB_routing) + "\" in_port=\"clb.I2\" out_port=\"ble6.in_D\" />\n")
	vpr_file.write("      </complete>\n")
	vpr_file.write("    <complete name=\"lutE\" input=\"clb.I3 clb.I1 ble6[3:2].out_local ble6[7:6].out_local ble6[8:8].out_local\" output=\"ble6[9:0].in_E\">\n")
	vpr_file.write("      <delay_constant max=\"" + str(local_CLB_routing) + "\" in_port=\"clb.I3\" out_port=\"ble6.in_E\" />\n")
	vpr_file.write("      <delay_constant max=\"" + str(local_CLB_routing) + "\" in_port=\"clb.I1\" out_port=\"ble6.in_E\" />\n")
	vpr_file.write("      </complete>\n")
	vpr_file.write("    <complete name=\"lutF\" input=\"clb.I4 clb.I1 ble6[1:0].out_local ble6[7:6].out_local ble6[9:9].out_local\" output=\"ble6[9:0].in_F\">\n")
	vpr_file.write("      <delay_constant max=\"" + str(local_CLB_routing) + "\" in_port=\"clb.I4\" out_port=\"ble6.in_F\" />\n")
	vpr_file.write("      <delay_constant max=\"" + str(local_CLB_routing) + "\" in_port=\"clb.I1\" out_port=\"ble6.in_F\" />\n")
	vpr_file.write("      </complete>\n")
	vpr_file.write("      <complete name=\"clks\" input=\"clb.clk\" output=\"ble6[9:0].clk\">\n")
	vpr_file.write("      </complete>\n")
	          
	vpr_file.write("      <!-- Direct connections to CLB outputs -->\n")
	vpr_file.write("      <direct name=\"clbouts1\" input=\"ble6[0:0].out_routing\" output=\"clb.O1\"/>\n")
	vpr_file.write("      <direct name=\"clbouts2\" input=\"ble6[1:1].out_routing\" output=\"clb.O2\"/>\n")
	vpr_file.write("      <direct name=\"clbouts3\" input=\"ble6[2:2].out_routing\" output=\"clb.O3\"/>\n")
	vpr_file.write("      <direct name=\"clbouts4\" input=\"ble6[3:3].out_routing\" output=\"clb.O4\"/>\n")
	vpr_file.write("      <direct name=\"clbouts5\" input=\"ble6[4:4].out_routing\" output=\"clb.O5\"/>\n")
	vpr_file.write("      <direct name=\"clbouts6\" input=\"ble6[5:5].out_routing\" output=\"clb.O6\"/>\n")
	vpr_file.write("      <direct name=\"clbouts7\" input=\"ble6[6:6].out_routing\" output=\"clb.O7\"/>\n")
	vpr_file.write("      <direct name=\"clbouts8\" input=\"ble6[7:7].out_routing\" output=\"clb.O8\"/>\n")
	vpr_file.write("      <direct name=\"clbouts9\" input=\"ble6[8:8].out_routing\" output=\"clb.O9\"/>\n")
	vpr_file.write("      <direct name=\"clbouts10\" input=\"ble6[9:9].out_routing\" output=\"clb.O10\"/>\n")

	vpr_file.write("    </interconnect>\n")
	vpr_file.write("    <fc default_in_type=\"frac\" default_in_val=\"" + str(Fcin) + "\" default_out_type=\"frac\" default_out_val=\"" + str(Fcout) + "\"/>\n")
	vpr_file.write("    <!-- Two sided connectivity CLB architecture--> \n")
	vpr_file.write("    <pinlocations pattern=\"custom\">\n")
	vpr_file.write("  <loc side=\"right\">clb.O1 clb.O2 clb.O3 clb.O4 clb.O5 clb.I1 clb.I3 clb.clk</loc> \n")
	vpr_file.write("      <loc side=\"bottom\">clb.O6 clb.O7 clb.O8 clb.O9 clb.O10 clb.I2 clb.I4 clb.clk</loc>      \n")
	vpr_file.write("    </pinlocations>\n")
	vpr_file.write("  </pb_type>\n")

	vpr_file.write("  <!-- This is the 36*36 uniform mult -->\n")
	vpr_file.write("  <pb_type name=\"mult_36\" height=\"4\" area=\"118800\">\n")
	vpr_file.write("      <input name=\"a\" num_pins=\"36\"/>\n")
	vpr_file.write("      <input name=\"b\" num_pins=\"36\"/>\n")
	vpr_file.write("      <output name=\"out\" num_pins=\"72\"/>\n")

	vpr_file.write("      <mode name=\"two_divisible_mult_18x18\">\n")
	vpr_file.write("        <pb_type name=\"divisible_mult_18x18\" num_pb=\"2\">\n")
	vpr_file.write("          <input name=\"a\" num_pins=\"18\"/>\n")
	vpr_file.write("          <input name=\"b\" num_pins=\"18\"/>\n")
	vpr_file.write("          <output name=\"out\" num_pins=\"36\"/>\n")

	vpr_file.write("          <mode name=\"two_mult_9x9\">\n")
	vpr_file.write("            <pb_type name=\"mult_9x9_slice\" num_pb=\"2\">\n")
	vpr_file.write("              <input name=\"A_cfg\" num_pins=\"9\"/>\n")
	vpr_file.write("              <input name=\"B_cfg\" num_pins=\"9\"/>\n")
	vpr_file.write("              <output name=\"OUT_cfg\" num_pins=\"18\"/>\n")

	vpr_file.write("              <pb_type name=\"mult_9x9\" blif_model=\".subckt multiply\" num_pb=\"1\">\n")
	vpr_file.write("                <input name=\"a\" num_pins=\"9\"/>\n")
	vpr_file.write("                <input name=\"b\" num_pins=\"9\"/>\n")
	vpr_file.write("                <output name=\"out\" num_pins=\"18\"/>\n")
	vpr_file.write("                <delay_constant max=\"1.667e-9\" in_port=\"mult_9x9.a\" out_port=\"mult_9x9.out\"/>\n")
	vpr_file.write("                <delay_constant max=\"1.667e-9\" in_port=\"mult_9x9.b\" out_port=\"mult_9x9.out\"/>\n")
	vpr_file.write("              </pb_type>\n")

	vpr_file.write("              <interconnect>\n")
	vpr_file.write("                <direct name=\"a2a\" input=\"mult_9x9_slice.A_cfg\" output=\"mult_9x9.a\">\n")
	vpr_file.write("                </direct>\n")
	vpr_file.write("                <direct name=\"b2b\" input=\"mult_9x9_slice.B_cfg\" output=\"mult_9x9.b\">\n")
	vpr_file.write("                </direct>\n")
	vpr_file.write("                <direct name=\"out2out\" input=\"mult_9x9.out\" output=\"mult_9x9_slice.OUT_cfg\">\n")
	vpr_file.write("                </direct>\n")
	vpr_file.write("              </interconnect>\n")
	vpr_file.write("            </pb_type>\n")
	vpr_file.write("            <interconnect>\n")
	vpr_file.write("              <direct name=\"a2a\" input=\"divisible_mult_18x18.a\" output=\"mult_9x9_slice[1:0].A_cfg\">\n")
	vpr_file.write("              </direct>\n")
	vpr_file.write("              <direct name=\"b2b\" input=\"divisible_mult_18x18.b\" output=\"mult_9x9_slice[1:0].B_cfg\">\n")
	vpr_file.write("              </direct>\n")
	vpr_file.write("              <direct name=\"out2out\" input=\"mult_9x9_slice[1:0].OUT_cfg\" output=\"divisible_mult_18x18.out\">\n")
	vpr_file.write("              </direct>\n")
	vpr_file.write("            </interconnect>\n")
	vpr_file.write("          </mode>\n")

	vpr_file.write("          <mode name=\"mult_18x18\">\n")
	vpr_file.write("            <pb_type name=\"mult_18x18_slice\" num_pb=\"1\">\n")
	vpr_file.write("              <input name=\"A_cfg\" num_pins=\"18\"/>\n")
	vpr_file.write("              <input name=\"B_cfg\" num_pins=\"18\"/>\n")
	vpr_file.write("              <output name=\"OUT_cfg\" num_pins=\"36\"/>\n")

	vpr_file.write("              <pb_type name=\"mult_18x18\" blif_model=\".subckt multiply\" num_pb=\"1\" >\n")
	vpr_file.write("                <input name=\"a\" num_pins=\"18\"/>\n")
	vpr_file.write("                <input name=\"b\" num_pins=\"18\"/>\n")
	vpr_file.write("                <output name=\"out\" num_pins=\"36\"/>\n")
	vpr_file.write("                <delay_constant max=\"1.667e-9\" in_port=\"mult_18x18.a\" out_port=\"mult_18x18.out\"/>\n")
	vpr_file.write("                <delay_constant max=\"1.667e-9\" in_port=\"mult_18x18.b\" out_port=\"mult_18x18.out\"/>\n")
	vpr_file.write("              </pb_type>\n")

	vpr_file.write("              <interconnect>\n")
	vpr_file.write("                <direct name=\"a2a\" input=\"mult_18x18_slice.A_cfg\" output=\"mult_18x18.a\">\n")
	vpr_file.write("                </direct>\n")
	vpr_file.write("                <direct name=\"b2b\" input=\"mult_18x18_slice.B_cfg\" output=\"mult_18x18.b\">\n")
	vpr_file.write("                </direct>\n")
	vpr_file.write("                <direct name=\"out2out\" input=\"mult_18x18.out\" output=\"mult_18x18_slice.OUT_cfg\">\n")
	vpr_file.write("                </direct>\n")
	vpr_file.write("              </interconnect>\n")
	vpr_file.write("            </pb_type>\n")
	vpr_file.write("            <interconnect>\n")
	vpr_file.write("              <direct name=\"a2a\" input=\"divisible_mult_18x18.a\" output=\"mult_18x18_slice.A_cfg\">\n")
	vpr_file.write("              </direct>\n")
	vpr_file.write("              <direct name=\"b2b\" input=\"divisible_mult_18x18.b\" output=\"mult_18x18_slice.B_cfg\">\n")
	vpr_file.write("              </direct>\n")
	vpr_file.write("              <direct name=\"out2out\" input=\"mult_18x18_slice.OUT_cfg\" output=\"divisible_mult_18x18.out\">\n")
	vpr_file.write("              </direct>\n")
	vpr_file.write("            </interconnect>\n")
	vpr_file.write("          </mode>\n")
	vpr_file.write("        </pb_type>\n")
	vpr_file.write("        <interconnect>\n")
	vpr_file.write("          <direct name=\"a2a\" input=\"mult_36.a\" output=\"divisible_mult_18x18[1:0].a\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"b2b\" input=\"mult_36.b\" output=\"divisible_mult_18x18[1:0].b\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"out2out\" input=\"divisible_mult_18x18[1:0].out\" output=\"mult_36.out\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("        </interconnect>\n")
	vpr_file.write("      </mode>\n")

	vpr_file.write("      <mode name=\"mult_36x36\">\n")
	vpr_file.write("        <pb_type name=\"mult_36x36_slice\" num_pb=\"1\">\n")
	vpr_file.write("          <input name=\"A_cfg\" num_pins=\"36\"/>\n")
	vpr_file.write("          <input name=\"B_cfg\" num_pins=\"36\"/>\n")
	vpr_file.write("          <output name=\"OUT_cfg\" num_pins=\"72\"/>\n")

	vpr_file.write("          <pb_type name=\"mult_36x36\" blif_model=\".subckt multiply\" num_pb=\"1\">\n")
	vpr_file.write("            <input name=\"a\" num_pins=\"36\"/>\n")
	vpr_file.write("            <input name=\"b\" num_pins=\"36\"/>\n")
	vpr_file.write("            <output name=\"out\" num_pins=\"72\"/>\n")
	vpr_file.write("            <delay_constant max=\"1.667e-9\" in_port=\"mult_36x36.a\" out_port=\"mult_36x36.out\"/>\n")
	vpr_file.write("            <delay_constant max=\"1.667e-9\" in_port=\"mult_36x36.b\" out_port=\"mult_36x36.out\"/>\n")
	vpr_file.write("          </pb_type>\n")

	vpr_file.write("          <interconnect>\n")
	vpr_file.write("            <direct name=\"a2a\" input=\"mult_36x36_slice.A_cfg\" output=\"mult_36x36.a\">\n")
	vpr_file.write("            </direct>\n")
	vpr_file.write("            <direct name=\"b2b\" input=\"mult_36x36_slice.B_cfg\" output=\"mult_36x36.b\">\n")
	vpr_file.write("            </direct>\n")
	vpr_file.write("            <direct name=\"out2out\" input=\"mult_36x36.out\" output=\"mult_36x36_slice.OUT_cfg\">\n")
	vpr_file.write("            </direct>\n")
	vpr_file.write("          </interconnect>\n")
	vpr_file.write("        </pb_type>\n")
	vpr_file.write("        <interconnect>\n")
	vpr_file.write("          <direct name=\"a2a\" input=\"mult_36.a\" output=\"mult_36x36_slice.A_cfg\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"b2b\" input=\"mult_36.b\" output=\"mult_36x36_slice.B_cfg\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"out2out\" input=\"mult_36x36_slice.OUT_cfg\" output=\"mult_36.out\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("        </interconnect>\n")
	vpr_file.write("      </mode>\n")

	vpr_file.write("    <fc default_in_type=\"frac\" default_in_val=\"0.15\" default_out_type=\"frac\" default_out_val=\"0.10\"/>\n")
	vpr_file.write("    <pinlocations pattern=\"spread\"/>\n")

	vpr_file.write("  </pb_type>\n")


	vpr_file.write("<!-- This is the Block RAM module  -->\n")

	vpr_file.write("  <pb_type name=\"memory\" height=\""+str(memory_height)+"\" area=\""+str(fpga_inst.area_dict["ram_core"]/fpga_inst.specs.min_width_tran_area)+"\">\n")

	vpr_file.write("      <input name=\"addr1\" num_pins=\""+str(memory_address_bits)+"\"/>\n")
	vpr_file.write("      <input name=\"addr2\" num_pins=\""+str(memory_address_bits)+"\"/>\n")
	
	vpr_file.write("      <input name=\"data\" num_pins=\""+str(memory_max_width)+"\"/>\n")
	
	vpr_file.write("      <input name=\"we1\" num_pins=\"1\"/>\n")
	vpr_file.write("      <input name=\"we2\" num_pins=\"1\"/>\n")
	
	vpr_file.write("      <output name=\"out\" num_pins=\""+str(memory_max_width)+"\"/>\n")
	
	vpr_file.write("      <clock name=\"clk\" num_pins=\"1\"/>\n")

	# I start with the widest single port mode and increase depth
	current_width = memory_max_width
	current_depth = memory_max_depth / current_width
	current_address_bits = fpga_inst.specs.row_decoder_bits + fpga_inst.specs.col_decoder_bits - 1

	while current_width >= 1:
		vpr_file.write("      <mode name=\"mem_"+str(current_depth)+"x"+str(current_width)+"_sp\">\n")
		vpr_file.write("        <pb_type name=\"mem_"+str(current_depth)+"x"+str(current_width)+"_sp\" blif_model=\".subckt single_port_ram\" class=\"memory\" num_pb=\"1\">\n")
		vpr_file.write("          <input name=\"addr\" num_pins=\""+str(current_address_bits)+"\" port_class=\"address\"/>\n")
		vpr_file.write("          <input name=\"data\" num_pins=\""+str(current_width)+"\" port_class=\"data_in\"/>\n")
		vpr_file.write("          <input name=\"we\" num_pins=\"1\" port_class=\"write_en\"/>\n")
		vpr_file.write("          <output name=\"out\" num_pins=\""+str(current_width)+"\" port_class=\"data_out\"/>\n")
		vpr_file.write("          <clock name=\"clk\" num_pins=\"1\" port_class=\"clock\"/>\n")
		vpr_file.write("          <T_setup value=\""+str(memory_setup_time)+"\" port=\"mem_"+str(current_depth)+"x"+str(current_width)+"_sp.addr\" clock=\"clk\"/>\n")
		vpr_file.write("          <T_setup value=\""+str(memory_setup_time)+"\" port=\"mem_"+str(current_depth)+"x"+str(current_width)+"_sp.data\" clock=\"clk\"/>\n")
		vpr_file.write("          <T_setup value=\""+str(memory_setup_time)+"\" port=\"mem_"+str(current_depth)+"x"+str(current_width)+"_sp.we\" clock=\"clk\"/>\n")
		vpr_file.write("          <T_clock_to_Q max=\""+str(memory_clktoq)+"\" port=\"mem_"+str(current_depth)+"x"+str(current_width)+"_sp.out\" clock=\"clk\"/>\n")
		vpr_file.write("        </pb_type>\n")
		vpr_file.write("        <interconnect>\n")
		vpr_file.write("          <direct name=\"address1\" input=\"memory.addr1["+str(current_address_bits - 1)+":0]\" output=\"mem_"+str(current_depth)+"x"+str(current_width)+"_sp.addr\">\n")
		vpr_file.write("          </direct>\n")
		vpr_file.write("          <direct name=\"data1\" input=\"memory.data["+str(current_width - 1)+":0]\" output=\"mem_"+str(current_depth)+"x"+str(current_width)+"_sp.data\">\n")
		vpr_file.write("          </direct>\n")
		vpr_file.write("          <direct name=\"writeen1\" input=\"memory.we1\" output=\"mem_"+str(current_depth)+"x"+str(current_width)+"_sp.we\">\n")
		vpr_file.write("          </direct>\n")
		vpr_file.write("          <direct name=\"dataout1\" input=\"mem_"+str(current_depth)+"x"+str(current_width)+"_sp.out\" output=\"memory.out["+str(current_width - 1)+":0]\">\n")
		vpr_file.write("          </direct>\n")
		vpr_file.write("          <direct name=\"clk\" input=\"memory.clk\" output=\"mem_"+str(current_depth)+"x"+str(current_width)+"_sp.clk\">\n")
		vpr_file.write("          </direct>\n")
		vpr_file.write("        </interconnect>\n")
		vpr_file.write("      </mode>\n")

		# Update width, depth, and address bits
		current_width /= 2
		current_depth *= 2
		current_address_bits += 1

	# Generate dual port modes:
	# In Dual Port mode, maximum width is half of single port mode
	current_width = memory_max_width / 2
	current_depth = memory_max_depth / current_width
	current_address_bits = fpga_inst.specs.row_decoder_bits + fpga_inst.specs.col_decoder_bits

	while current_width >= 1:

		vpr_file.write("      <mode name=\"mem_"+str(current_depth)+"x"+str(current_width)+"_dp\">\n")
		vpr_file.write("        <pb_type name=\"mem_"+str(current_depth)+"x"+str(current_width)+"_dp\" blif_model=\".subckt dual_port_ram\" class=\"memory\" num_pb=\"1\">\n")
		vpr_file.write("          <input name=\"addr1\" num_pins=\""+str(current_address_bits)+"\" port_class=\"address1\"/>\n")
		vpr_file.write("          <input name=\"addr2\" num_pins=\""+str(current_address_bits)+"\" port_class=\"address2\"/>\n")
		vpr_file.write("          <input name=\"data1\" num_pins=\""+str(current_width)+"\" port_class=\"data_in1\"/>\n")
		vpr_file.write("          <input name=\"data2\" num_pins=\""+str(current_width)+"\" port_class=\"data_in2\"/>\n")
		vpr_file.write("          <input name=\"we1\" num_pins=\"1\" port_class=\"write_en1\"/>\n")
		vpr_file.write("          <input name=\"we2\" num_pins=\"1\" port_class=\"write_en2\"/>\n")
		vpr_file.write("          <output name=\"out1\" num_pins=\""+str(current_width)+"\" port_class=\"data_out1\"/>\n")
		vpr_file.write("          <output name=\"out2\" num_pins=\""+str(current_width)+"\" port_class=\"data_out2\"/>\n")
		vpr_file.write("          <clock name=\"clk\" num_pins=\"1\" port_class=\"clock\"/>\n")
		vpr_file.write("          <T_setup value=\""+str(memory_setup_time)+"\" port=\"mem_"+str(current_depth)+"x"+str(current_width)+"_dp.addr1\" clock=\"clk\"/>\n")
		vpr_file.write("          <T_setup value=\""+str(memory_setup_time)+"\" port=\"mem_"+str(current_depth)+"x"+str(current_width)+"_dp.data1\" clock=\"clk\"/>\n")
		vpr_file.write("          <T_setup value=\""+str(memory_setup_time)+"\" port=\"mem_"+str(current_depth)+"x"+str(current_width)+"_dp.we1\" clock=\"clk\"/>\n")
		vpr_file.write("          <T_setup value=\""+str(memory_setup_time)+"\" port=\"mem_"+str(current_depth)+"x"+str(current_width)+"_dp.addr2\" clock=\"clk\"/>\n")
		vpr_file.write("          <T_setup value=\""+str(memory_setup_time)+"\" port=\"mem_"+str(current_depth)+"x"+str(current_width)+"_dp.data2\" clock=\"clk\"/>\n")
		vpr_file.write("          <T_setup value=\""+str(memory_setup_time)+"\" port=\"mem_"+str(current_depth)+"x"+str(current_width)+"_dp.we2\" clock=\"clk\"/>\n")
		vpr_file.write("          <T_clock_to_Q max=\""+str(memory_clktoq)+"\" port=\"mem_"+str(current_depth)+"x"+str(current_width)+"_dp.out1\" clock=\"clk\"/>\n")
		vpr_file.write("          <T_clock_to_Q max=\""+str(memory_clktoq)+"\" port=\"mem_"+str(current_depth)+"x"+str(current_width)+"_dp.out2\" clock=\"clk\"/>\n")
		vpr_file.write("        </pb_type>\n")
		vpr_file.write("        <interconnect>\n")
		vpr_file.write("          <direct name=\"address1\" input=\"memory.addr1["+str(current_address_bits -1)+":0]\" output=\"mem_"+str(current_depth)+"x"+str(current_width)+"_dp.addr1\">\n")
		vpr_file.write("          </direct>\n")
		vpr_file.write("          <direct name=\"address2\" input=\"memory.addr2["+str(current_address_bits -1)+":0]\" output=\"mem_"+str(current_depth)+"x"+str(current_width)+"_dp.addr2\">\n")
		vpr_file.write("          </direct>\n")
		vpr_file.write("          <direct name=\"data1\" input=\"memory.data["+str(current_width - 1)+":0]\" output=\"mem_"+str(current_depth)+"x"+str(current_width)+"_dp.data1\">\n")
		vpr_file.write("          </direct>\n")
		vpr_file.write("          <direct name=\"data2\" input=\"memory.data["+str(2*current_width - 1)+":"+str(current_width)+"]\" output=\"mem_"+str(current_depth)+"x"+str(current_width)+"_dp.data2\">\n")
		vpr_file.write("          </direct>\n")
		vpr_file.write("          <direct name=\"writeen1\" input=\"memory.we1\" output=\"mem_"+str(current_depth)+"x"+str(current_width)+"_dp.we1\">\n")
		vpr_file.write("          </direct>\n")
		vpr_file.write("          <direct name=\"writeen2\" input=\"memory.we2\" output=\"mem_"+str(current_depth)+"x"+str(current_width)+"_dp.we2\">\n")
		vpr_file.write("          </direct>\n")
		vpr_file.write("          <direct name=\"dataout1\" input=\"mem_"+str(current_depth)+"x"+str(current_width)+"_dp.out1\" output=\"memory.out["+str(current_width - 1)+":0]\">\n")
		vpr_file.write("          </direct>\n")
		vpr_file.write("          <direct name=\"dataout2\" input=\"mem_"+str(current_depth)+"x"+str(current_width)+"_dp.out2\" output=\"memory.out["+str(2*current_width - 1)+":"+str(current_width)+"]\">\n")
		vpr_file.write("          </direct>\n")
		vpr_file.write("          <direct name=\"clk\" input=\"memory.clk\" output=\"mem_"+str(current_depth)+"x"+str(current_width)+"_dp.clk\">\n")
		vpr_file.write("          </direct>\n")
		vpr_file.write("        </interconnect>\n")
		vpr_file.write("      </mode>\n")

		current_width /= 2
		current_depth *= 2
		current_address_bits += 1


	#vpr_file.write("    <fc default_in_type=\"abs\" default_in_val=\""+str(fpga_inst.cb_mux.required_size)+"\" default_out_type=\"abs\" default_out_val=\""+str(fpga_inst.sb_mux.required_size)+"\"/>\n")
	#vpr_file.write("    <pinlocations pattern=\"spread\"/>\n")
	vpr_file.write("    <fc default_in_type=\"frac\" default_in_val=\"0.15\" default_out_type=\"frac\" default_out_val=\"0.10\"/>\n")
	vpr_file.write("    <pinlocations pattern=\"spread\"/>\n")
	vpr_file.write("  </pb_type>\n")


	vpr_file.write("</complexblocklist>\n")
	vpr_file.write("</architecture>\n")



def print_vpr_file_flut_hard(vpr_file, fpga_inst):

	# get delay values
	Tdel = fpga_inst.sb_mux.delay
	T_ipin_cblock = fpga_inst.cb_mux.delay
	local_CLB_routing = fpga_inst.logic_cluster.local_mux.delay
	local_feedback = fpga_inst.logic_cluster.ble.local_output.delay
	logic_block_output = fpga_inst.logic_cluster.ble.general_output.delay

	# get lut delays
	lut_input_names = list(fpga_inst.logic_cluster.ble.lut.input_drivers.keys())
	lut_input_names.sort()
	lut_delays = {}
	for input_name in lut_input_names:
		lut_input = fpga_inst.logic_cluster.ble.lut.input_drivers[input_name]
		driver_delay = max(lut_input.driver.delay, lut_input.not_driver.delay)
		path_delay = lut_input.delay
		lut_delays[input_name] = driver_delay+path_delay
		if fpga_inst.specs.use_fluts:
			lut_delays[input_name] += fpga_inst.logic_cluster.ble.fmux.delay
	# get archetecture parameters
	Rfb = fpga_inst.specs.Rfb
	Fcin = fpga_inst.specs.Fcin
	Fcout = fpga_inst.specs.Fcout
	Fs = fpga_inst.specs.Fs
	N = fpga_inst.specs.N
	K = fpga_inst.specs.K
	L = fpga_inst.specs.L
	independent_inputs = fpga_inst.specs.independent_inputs
		
	# get areas
	grid_logic_tile_area = fpga_inst.area_dict["logic_cluster"]/fpga_inst.specs.min_width_tran_area
	if grid_logic_tile_area < 1.00 :
		grid_logic_tile_area = 1.00
	ipin_mux_trans_size = fpga_inst.area_dict["ipin_mux_trans_size"]/fpga_inst.specs.min_width_tran_area
	if ipin_mux_trans_size < 1.00 :
		ipin_mux_trans_size = 1.00
	mux_trans_size = fpga_inst.area_dict["switch_mux_trans_size"]/fpga_inst.specs.min_width_tran_area
	if mux_trans_size < 1.00 :
		mux_trans_size = 1.00
	buf_size = fpga_inst.area_dict["switch_buf_size"]/fpga_inst.specs.min_width_tran_area
	if buf_size < 1.00 :
		buf_size = 1.00

	cb_buf_size = fpga_inst.area_dict["cb_buf_size"]/fpga_inst.specs.min_width_tran_area
	if cb_buf_size < 1.00:
		cb_buf_size = 1.00

	vpr_file.write("<architecture>  \n")
	vpr_file.write("<!-- ODIN II specific config -->\n")
	vpr_file.write("<models>\n")
	vpr_file.write("  <model name=\"multiply\">\n")
	vpr_file.write("    <input_ports>\n")
	vpr_file.write("    <port name=\"a\" combinational_sink_ports=\"out\"/> \n")
	vpr_file.write("    <port name=\"b\" combinational_sink_ports=\"out\"/>\n")
	vpr_file.write("    </input_ports>\n")
	vpr_file.write("    <output_ports>\n")
	vpr_file.write("    <port name=\"out\"/>\n")
	vpr_file.write("    </output_ports>\n")
	vpr_file.write("  </model>\n")
	    
	vpr_file.write("<model name=\"single_port_ram\">\n")
	vpr_file.write("  <input_ports>\n")
	vpr_file.write("  <port name=\"we\" clock=\"clk\"/>     <!-- control -->\n")
	vpr_file.write("  <port name=\"addr\" clock=\"clk\"/>  <!-- address lines -->\n")
	vpr_file.write("  <port name=\"data\" clock=\"clk\"/>  <!-- data lines can be broken down into smaller bit widths minimum size 1 -->\n")
	vpr_file.write("  <port name=\"clk\" is_clock=\"1\"/>  <!-- memories are often clocked -->\n")
	vpr_file.write("  </input_ports>\n")
	vpr_file.write("  <output_ports>\n")
	vpr_file.write("  <port name=\"out\" clock=\"clk\"/>   <!-- output can be broken down into smaller bit widths minimum size 1 -->\n")
	vpr_file.write("  </output_ports>\n")
	vpr_file.write("</model>\n")

	vpr_file.write("<model name=\"dual_port_ram\">\n")
	vpr_file.write("  <input_ports>\n")
	vpr_file.write("  <port name=\"we1\" clock=\"clk\"/>     <!-- write enable -->\n")
	vpr_file.write("  <port name=\"we2\" clock=\"clk\"/>     <!-- write enable -->\n")
	vpr_file.write("  <port name=\"addr1\" clock=\"clk\"/>  <!-- address lines -->\n")
	vpr_file.write("  <port name=\"addr2\" clock=\"clk\"/>  <!-- address lines -->\n")
	vpr_file.write("  <port name=\"data1\" clock=\"clk\"/>  <!-- data lines can be broken down into smaller bit widths minimum size 1 -->\n")
	vpr_file.write("  <port name=\"data2\" clock=\"clk\"/>  <!-- data lines can be broken down into smaller bit widths minimum size 1 -->\n")
	vpr_file.write("  <port name=\"clk\" is_clock=\"1\"/>  <!-- memories are often clocked -->\n")
	vpr_file.write("  </input_ports>\n")
	vpr_file.write("  <output_ports>\n")
	vpr_file.write("  <port name=\"out1\" clock=\"clk\"/>   <!-- output can be broken down into smaller bit widths minimum size 1 -->\n")
	vpr_file.write("  <port name=\"out2\" clock=\"clk\"/>   <!-- output can be broken down into smaller bit widths minimum size 1 -->\n")
	vpr_file.write("  </output_ports>\n")
	vpr_file.write("</model>\n")

	vpr_file.write("</models>\n")
	vpr_file.write("<!-- ODIN II specific config ends -->\n")
	vpr_file.write("<!-- Physical descriptions begin -->\n")
	vpr_file.write("<layout>\n")
	vpr_file.write("<auto_layout aspect_ratio=\"1.0\">\n")
	vpr_file.write("<perimeter type=\"io\" priority=\"100\"/>\n")
	vpr_file.write("<corners type=\"EMPTY\" priority=\"101\"/>\n")
	vpr_file.write("<fill type=\"clb\" priority=\"10\"/>\n")
	vpr_file.write("<col type=\"mult_36\" startx=\"4\" starty=\"1\" repeatx=\"8\" priority=\"20\" />\n")
	vpr_file.write("<col type=\"EMPTY\" startx=\"4\" starty=\"1\" repeatx=\"8\" priority=\"19\" />\n")
	vpr_file.write("<col type=\"memory\" startx=\"2\" starty=\"1\" repeatx=\"8\" priority=\"20\" />\n")
	vpr_file.write("<col type=\"EMPTY\" startx=\"2\" starty=\"1\" repeatx=\"8\" priority=\"19\" />\n")
	vpr_file.write("</auto_layout>\n")
	vpr_file.write("</layout>\n")

	vpr_file.write("  <device>\n")
	vpr_file.write("    <sizing R_minW_nmos=\"13090.000000\" R_minW_pmos=\"19086.831111\"/> \n") #ipin_mux_trans_size=\"" + str(ipin_mux_trans_size)+ "\"/>\n
	vpr_file.write("    <area grid_logic_tile_area=\"" + str(grid_logic_tile_area) +"\"/>\n")
	vpr_file.write("    <chan_width_distr>\n")
	vpr_file.write("      <x distr=\"uniform\" peak=\"1.000000\"/>\n")
	vpr_file.write("      <y distr=\"uniform\" peak=\"1.000000\"/>\n")
	vpr_file.write("    </chan_width_distr>\n")
	vpr_file.write("    <switch_block type=\"wilton\" fs=\"" + str(Fs) + "\"/>\n")
	vpr_file.write("    <connection_block input_switch_name=\"ipin_cblock\"/>\n")
	vpr_file.write("  </device>\n")

	
	vpr_file.write("  <switchlist>\n")
	vpr_file.write("    <switch type=\"mux\" name=\"0\" R=\"0.000000\" Cin=\"0.000000e+00\" Cout=\"0.000000e+00\" Tdel=\"" + str(Tdel) + "\" mux_trans_size=\"" + str(mux_trans_size) + "\" buf_size=\"" + str(buf_size) + "\"/>\n")
	vpr_file.write("    <switch type=\"mux\" name=\"ipin_cblock\" R=\"0.000000\" Cin=\"0.000000e+00\" Cout=\"0.000000e+00\" Tdel=\"" + str(T_ipin_cblock) + "\" mux_trans_size=\"" + str(ipin_mux_trans_size) + "\" buf_size=\"" + str(cb_buf_size) + "\"/>\n")
	vpr_file.write("  </switchlist>\n")

	vpr_file.write("  <segmentlist>\n")
	vpr_file.write("    <segment freq=\"1.000000\" length=\"" + str(L) + "\" type=\"unidir\" Rmetal=\"0.000000\" Cmetal=\"0.000000e+00\">\n")
	vpr_file.write("    <mux name=\"0\"/>\n")
	vpr_file.write("    <sb type=\"pattern\">1 1 1 1 1</sb>\n")
	vpr_file.write("    <cb type=\"pattern\">1 1 1 1</cb>\n")
	vpr_file.write("    </segment>\n")
	vpr_file.write("  </segmentlist>\n")

	vpr_file.write("  <complexblocklist>\n")
	vpr_file.write("      <!-- Capacity is a unique property of I/Os, it is the maximum number of I/Os that can be placed at the same (X,Y) location on the FPGA -->\n")
	vpr_file.write("     <pb_type name=\"io\" capacity=\"8\">\n")
	vpr_file.write("       <input name=\"outpad\" num_pins=\"1\"/>\n")
	vpr_file.write("       <output name=\"inpad\" num_pins=\"1\"/>\n")
	vpr_file.write("       <clock name=\"clock\" num_pins=\"1\"/>\n")
	vpr_file.write("    <!-- IOs can operate as either inputs or outputs -->\n")
	vpr_file.write("    <mode name=\"inpad\">\n")
	vpr_file.write("      <pb_type name=\"inpad\" blif_model=\".input\" num_pb=\"1\">\n")
	vpr_file.write("        <output name=\"inpad\" num_pins=\"1\"/>\n")
	vpr_file.write("      </pb_type>\n")
	vpr_file.write("      <interconnect>\n")
	vpr_file.write("        <direct name=\"inpad\" input=\"inpad.inpad\" output=\"io.inpad\">\n")
	vpr_file.write("        <delay_constant max=\"4.243e-11\" in_port=\"inpad.inpad\" out_port=\"io.inpad\"/>\n")
	vpr_file.write("        </direct>\n")
	vpr_file.write("      </interconnect>  \n")
	vpr_file.write("    </mode>\n")
	vpr_file.write("    <mode name=\"outpad\">\n")
	vpr_file.write("      <pb_type name=\"outpad\" blif_model=\".output\" num_pb=\"1\">\n")
	vpr_file.write("        <input name=\"outpad\" num_pins=\"1\"/>\n")
	vpr_file.write("      </pb_type>\n")
	vpr_file.write("      <interconnect>\n")
	vpr_file.write("        <direct name=\"outpad\" input=\"io.outpad\" output=\"outpad.outpad\">\n")
	vpr_file.write("        <delay_constant max=\"1.394e-11\" in_port=\"io.outpad\" out_port=\"outpad.outpad\"/>\n")
	vpr_file.write("        </direct>\n")
	vpr_file.write("      </interconnect>\n")
	vpr_file.write("    </mode>\n")
	vpr_file.write("    <fc default_in_type=\"frac\" default_in_val=\"0.15\" default_out_type=\"frac\" default_out_val=\"0.10\"/>\n")
	vpr_file.write("    <!-- IOs go on the periphery of the FPGA, for consistency, \n")
	vpr_file.write("      make it physically equivalent on all sides so that only one definition of I/Os is needed.\n")
	vpr_file.write("      If I do not make a physically equivalent definition, then I need to define 4 different I/Os, one for each side of the FPGA\n")
	vpr_file.write("    -->\n")
	vpr_file.write("    <pinlocations pattern=\"custom\">\n")
	vpr_file.write("      <loc side=\"left\">io.outpad io.inpad io.clock</loc>\n")
	vpr_file.write("      <loc side=\"top\">io.outpad io.inpad io.clock</loc>\n")
	vpr_file.write("      <loc side=\"right\">io.outpad io.inpad io.clock</loc>\n")
	vpr_file.write("      <loc side=\"bottom\">io.outpad io.inpad io.clock</loc>\n")
	vpr_file.write("    </pinlocations>\n")


	vpr_file.write("  </pb_type>\n")
	vpr_file.write("  <!-- Logic cluster definition -->\n")
	vpr_file.write("  <pb_type name=\"clb\" area=\""+str(grid_logic_tile_area)+"\">\n")
	vpr_file.write("    <input name=\"I1\" num_pins=\"" + str(N) + "\" equivalent=\"true\"/>\n")
	vpr_file.write("    <input name=\"I2\" num_pins=\"" + str(N) + "\" equivalent=\"true\"/>\n")
	vpr_file.write("    <input name=\"I3\" num_pins=\"" + str(N) + "\" equivalent=\"true\"/>\n")
	vpr_file.write("    <input name=\"I4\" num_pins=\"" + str(N) + "\" equivalent=\"true\"/>\n")
	vpr_file.write("    <output name=\"O1\" num_pins=\"2\" equivalent=\"true\"/>\n")
	vpr_file.write("    <output name=\"O2\" num_pins=\"2\" equivalent=\"true\"/>\n")
	vpr_file.write("    <output name=\"O3\" num_pins=\"2\" equivalent=\"true\"/>\n")
	vpr_file.write("    <output name=\"O4\" num_pins=\"2\" equivalent=\"true\"/>\n")
	vpr_file.write("    <output name=\"O5\" num_pins=\"2\" equivalent=\"true\"/>\n")
	vpr_file.write("    <output name=\"O6\" num_pins=\"2\" equivalent=\"true\"/>\n")
	vpr_file.write("    <output name=\"O7\" num_pins=\"2\" equivalent=\"true\"/>\n")
	vpr_file.write("    <output name=\"O8\" num_pins=\"2\" equivalent=\"true\"/>\n")
	vpr_file.write("    <output name=\"O9\" num_pins=\"2\" equivalent=\"true\"/>\n")
	vpr_file.write("    <output name=\"O10\" num_pins=\"2\" equivalent=\"true\"/>\n")
	vpr_file.write("    <clock name=\"clk\" num_pins=\"1\"/>")

	vpr_file.write("  <!-- Basic logic element definition -->\n")
	vpr_file.write("  <pb_type name=\"fle\" num_pb=\""+ str(N) +"\">\n")
	vpr_file.write("  <input name=\"in_A\" num_pins=\"1\" equivalent=\"false\"/>\n")
	vpr_file.write("  <input name=\"in_B\" num_pins=\"1\" equivalent=\"false\"/>\n")
	vpr_file.write("  <input name=\"in_C\" num_pins=\"1\" equivalent=\"false\"/>\n")
	vpr_file.write("  <input name=\"in_D\" num_pins=\"1\" equivalent=\"false\"/>\n")
	vpr_file.write("  <input name=\"in_E\" num_pins=\"1\" equivalent=\"false\"/>\n")
	vpr_file.write("  <input name=\"in_F\" num_pins=\"1\" equivalent=\"false\"/>\n")
	if independent_inputs > 0:
		vpr_file.write("  <input name=\"in_E2\" num_pins=\"1\" equivalent=\"false\"/>\n")	
	if independent_inputs > 1:
		vpr_file.write("  <input name=\"in_D2\" num_pins=\"1\" equivalent=\"false\"/>\n")	
	if independent_inputs > 2:
		vpr_file.write("  <input name=\"in_C2\" num_pins=\"1\" equivalent=\"false\"/>\n")	
	if independent_inputs > 3:
		vpr_file.write("  <input name=\"in_B2\" num_pins=\"1\" equivalent=\"false\"/>\n")	
	if independent_inputs > 4:
		vpr_file.write("  <input name=\"in_A2\" num_pins=\"1\" equivalent=\"false\"/>\n")		

	vpr_file.write("  <output name=\"out_local\" num_pins=\"2\" equivalent=\"false\"/>\n")
	vpr_file.write("  <output name=\"out_routing\" num_pins=\"2\" equivalent=\"true\"/>\n")
	vpr_file.write("  <clock name=\"clk\" num_pins=\"1\"/> \n")

	vpr_file.write("  <mode name=\"n1_lut6\">\n")
	vpr_file.write("  <pb_type name=\"ble6\" num_pb=\"" + str(1) + "\">\n")
	vpr_file.write("  <input name=\"in_A\" num_pins=\"1\" equivalent=\"false\"/>\n")
	vpr_file.write("  <input name=\"in_B\" num_pins=\"1\" equivalent=\"false\"/>\n")
	vpr_file.write("  <input name=\"in_C\" num_pins=\"1\" equivalent=\"false\"/>\n")
	vpr_file.write("  <input name=\"in_D\" num_pins=\"1\" equivalent=\"false\"/>\n")
	vpr_file.write("  <input name=\"in_E\" num_pins=\"1\" equivalent=\"false\"/>\n")
	vpr_file.write("  <input name=\"in_F\" num_pins=\"1\" equivalent=\"false\"/>\n")
	vpr_file.write("  <output name=\"out_local\" num_pins=\"1\" equivalent=\"false\"/>\n")
	vpr_file.write("  <output name=\"out_routing\" num_pins=\"2\" equivalent=\"true\"/>\n")
	vpr_file.write("  <clock name=\"clk\" num_pins=\"1\"/> \n")
	vpr_file.write("  <pb_type name=\"lut6\" blif_model=\".names\" num_pb=\"1\" class=\"lut\">\n")
	vpr_file.write("  <input name=\"in\" num_pins=\"" + str(K) + "\" port_class=\"lut_in\"/>\n")
	vpr_file.write("  <output name=\"out\" num_pins=\"1\" port_class=\"lut_out\"/>\n")
	vpr_file.write("  <!-- We define the LUT delays on the LUT pins instead of through the LUT -->\n")
	vpr_file.write("  <delay_matrix type=\"max\" in_port=\"lut6.in\" out_port=\"lut6.out\">\n")
	vpr_file.write("     0\n")
	vpr_file.write("     0\n")
	vpr_file.write("     0\n")
	vpr_file.write("     0\n")
	vpr_file.write("     0\n")
	vpr_file.write("     0\n")
	vpr_file.write("  </delay_matrix>\n")
	vpr_file.write("  </pb_type>\n")
	vpr_file.write("  <pb_type name=\"ff\" blif_model=\".latch\" num_pb=\"1\" class=\"flipflop\">\n")
	vpr_file.write("  <input name=\"D\" num_pins=\"1\" port_class=\"D\"/>\n")
	vpr_file.write("  <output name=\"Q\" num_pins=\"1\" port_class=\"Q\"/>\n")
	vpr_file.write("  <clock name=\"clk\" num_pins=\"1\" port_class=\"clock\"/>\n")
	vpr_file.write("  <T_setup value=\"1.891e-11\" port=\"ff.D\" clock=\"clk\"/>\n")
	vpr_file.write("  <T_clock_to_Q max=\"6.032e-11\" port=\"ff.Q\" clock=\"clk\"/>\n")
	vpr_file.write("  </pb_type>\n")

	vpr_file.write("      <interconnect>\n")


	feedback_mux = {}
	input_num = 0
	direct_num = 1
	for input_name in lut_input_names:
		if Rfb.count(input_name) != 1 :
			vpr_file.write("    <direct name=\"direct" + str(input_num) + "\" input=\"ble6.in_" + input_name.upper() + "\" output=\"lut6.in[" + str(input_num) + ":" + str(input_num) + "]\">\n")
			vpr_file.write("      <delay_constant max=\"" + str(lut_delays[input_name]) + "\" in_port=\"ble6.in_" + input_name.upper() + "\" out_port=\"lut6.in[" + str(input_num) + ":" + str(input_num) + "]\" />\n")
			vpr_file.write("    </direct>\n")

			direct_num = direct_num + 1

		else:
			feedback_mux[input_name] = input_num

		input_num = input_num + 1

	vpr_file.write("      <!--Clock -->\n")

	vpr_file.write("      <direct name=\"direct" + str(direct_num) + "\" input=\"ble6.clk\" output=\"ff.clk\"/>\n")


	mux_num = 1
	for name in feedback_mux :
		vpr_file.write("      <!-- Register feedback mux -->   \n")
		vpr_file.write("      <mux name=\"mux" + str(mux_num) + "\" input=\"ble6.in_" + name.upper() + " ff.Q\" output=\"lut6.in[" + str(feedback_mux[name]) + ":" + str(feedback_mux[name]) + "]\">\n")
		vpr_file.write("        <delay_constant max=\"" + str(lut_delays[name]) + "\" in_port=\"ble6.in_" + name.upper() + "\" out_port=\"lut6.in[" + str(feedback_mux[name]) + ":" + str(feedback_mux[name]) + "]\" />\n")
		vpr_file.write("        <delay_constant max=\"" + str(lut_delays[name]) + "\" in_port=\"ff.Q\" out_port=\"lut6.in[" + str(feedback_mux[name]) + ":" + str(feedback_mux[name]) + "]\" />  \n")
		vpr_file.write("      </mux>\n")
		mux_num = mux_num + 1
		vpr_file.write("      <!-- FF input selection mux -->\n")
		vpr_file.write("      <mux name=\"" + str(mux_num) + "\" input=\"lut6.out ble6.in_" + name.upper() + "\" output=\"ff.D\">\n")
		vpr_file.write("        <delay_constant max=\"1.74588e-11\" in_port=\"lut6.out\" out_port=\"ff.D\" />\n")
		vpr_file.write("        <delay_constant max=\"1.74588e-11\" in_port=\"ble6.in_" + name.upper() + "\" out_port=\"ff.D\" />\n")
		vpr_file.write("      </mux>\n")
		mux_num = mux_num + 1


	vpr_file.write("      <!-- BLE output (local) -->\n")
	vpr_file.write("      <mux name=\"mux" + str(mux_num) + "\" input=\"ff.Q lut6.out\" output=\"ble6.out_local\">\n")
	vpr_file.write("        <delay_constant max=\"" + str(local_feedback) + "\" in_port=\"ff.Q\" out_port=\"ble6.out_local\" />\n")
	vpr_file.write("        <delay_constant max=\"" + str(local_feedback) + "\" in_port=\"lut6.out\" out_port=\"ble6.out_local\" />\n")
	vpr_file.write("      </mux>\n")
	mux_num = mux_num + 1

	vpr_file.write("      <!-- BLE output (routing 1) --> \n")
	vpr_file.write("      <mux name=\"mux" + str(mux_num) + "\" input=\"ff.Q lut6.out\" output=\"ble6.out_routing[0:0]\">\n")
	vpr_file.write("        <delay_constant max=\"" + str(logic_block_output)+ "\" in_port=\"ff.Q\" out_port=\"ble6.out_routing[0:0]\" />\n")
	vpr_file.write("        <delay_constant max=\"" + str(logic_block_output)+ "\" in_port=\"lut6.out\" out_port=\"ble6.out_routing[0:0]\" />\n")
	vpr_file.write("      </mux>\n")
	mux_num = mux_num + 1

	vpr_file.write("      <!-- BLE output (routing 2) --> \n")
	vpr_file.write("      <mux name=\"mux" + str(mux_num) + "\" input=\"ff.Q lut6.out\" output=\"ble6.out_routing[1:1]\">\n")
	vpr_file.write("        <delay_constant max=\"" + str(logic_block_output)+ "\" in_port=\"ff.Q\" out_port=\"ble6.out_routing[1:1]\" />\n")
	vpr_file.write("        <delay_constant max=\"" + str(logic_block_output)+ "\" in_port=\"lut6.out\" out_port=\"ble6.out_routing[1:1]\" />\n")
	vpr_file.write("      </mux>\n")
	vpr_file.write("      </interconnect>\n")
	vpr_file.write("    </pb_type>\n")
	vpr_file.write("  <interconnect>\n")
	vpr_file.write(" <direct name=\"direct1\" input=\"fle.in_A\" output=\"ble6.in_A\"/>\n")
	vpr_file.write(" <direct name=\"direct2\" input=\"fle.in_B\" output=\"ble6.in_B\"/>\n")
	vpr_file.write(" <direct name=\"direct3\" input=\"fle.in_C\" output=\"ble6.in_C\"/>\n")
	vpr_file.write(" <direct name=\"direct4\" input=\"fle.in_D\" output=\"ble6.in_D\"/>\n")
	vpr_file.write(" <direct name=\"direct5\" input=\"fle.in_E\" output=\"ble6.in_E\"/>\n")
	vpr_file.write(" <direct name=\"direct6\" input=\"fle.in_F\" output=\"ble6.in_F\"/>\n")
	vpr_file.write(" <direct name=\"direct7\" input=\"ble6.out_local\" output=\"fle.out_local[0:0]\"/>\n")
	vpr_file.write(" <direct name=\"direct8\" input=\"ble6.out_routing\" output=\"fle.out_routing\"/>\n")
	vpr_file.write(" <direct name=\"direct9\" input=\"fle.clk\" output=\"ble6.clk\"/>\n")
	vpr_file.write(" </interconnect>\n")

	vpr_file.write("    </mode>  \n")
	vpr_file.write("    <mode name=\"n2_lut5\">\n")
	vpr_file.write("      <pb_type name=\"lut5inter\" num_pb=\"1\">\n")
	vpr_file.write("  <input name=\"in_A\" num_pins=\"1\" equivalent=\"false\"/>\n")
	vpr_file.write("  <input name=\"in_B\" num_pins=\"1\" equivalent=\"false\"/>\n")
	vpr_file.write("  <input name=\"in_C\" num_pins=\"1\" equivalent=\"false\"/>\n")
	vpr_file.write("  <input name=\"in_D\" num_pins=\"1\" equivalent=\"false\"/>\n")
	vpr_file.write("  <input name=\"in_E\" num_pins=\"1\" equivalent=\"false\"/>\n")
	if independent_inputs > 0:
		vpr_file.write("  <input name=\"in_E2\" num_pins=\"1\" equivalent=\"false\"/>\n")	
	if independent_inputs > 1:
		vpr_file.write("  <input name=\"in_D2\" num_pins=\"1\" equivalent=\"false\"/>\n")	
	if independent_inputs > 2:
		vpr_file.write("  <input name=\"in_C2\" num_pins=\"1\" equivalent=\"false\"/>\n")	
	if independent_inputs > 3:
		vpr_file.write("  <input name=\"in_B2\" num_pins=\"1\" equivalent=\"false\"/>\n")	
	if independent_inputs > 4:
		vpr_file.write("  <input name=\"in_A2\" num_pins=\"1\" equivalent=\"false\"/>\n")		
	vpr_file.write("  <output name=\"out_local\" num_pins=\"2\" equivalent=\"false\"/>\n")
	vpr_file.write("  <output name=\"out_routing\" num_pins=\"2\" equivalent=\"true\"/>\n")
	vpr_file.write("  <clock name=\"clk\" num_pins=\"1\"/> \n")
	vpr_file.write("  <pb_type name=\"ble5\" num_pb=\"2\">\n")
	vpr_file.write("  <input name=\"in_A\" num_pins=\"1\" equivalent=\"false\"/>\n")
	vpr_file.write("  <input name=\"in_B\" num_pins=\"1\" equivalent=\"false\"/>\n")
	vpr_file.write("  <input name=\"in_C\" num_pins=\"1\" equivalent=\"false\"/>\n")
	vpr_file.write("  <input name=\"in_D\" num_pins=\"1\" equivalent=\"false\"/>\n")
	vpr_file.write("  <input name=\"in_E\" num_pins=\"1\" equivalent=\"false\"/>\n")
	vpr_file.write("  <output name=\"out_local\" num_pins=\"1\" equivalent=\"false\"/>\n")
	vpr_file.write("  <output name=\"out_routing\" num_pins=\"1\" equivalent=\"true\"/>\n")
	vpr_file.write("  <clock name=\"clk\" num_pins=\"1\"/> \n")
	vpr_file.write("          <pb_type name=\"lut5\" blif_model=\".names\" num_pb=\"1\" class=\"lut\">\n")
	vpr_file.write("            <input name=\"in\" num_pins=\"5\" port_class=\"lut_in\"/>\n")
	vpr_file.write("            <output name=\"out\" num_pins=\"1\" port_class=\"lut_out\"/>\n")
	vpr_file.write("  <!-- We define the LUT delays on the LUT pins instead of through the LUT -->\n")
	vpr_file.write("  <delay_matrix type=\"max\" in_port=\"lut5.in\" out_port=\"lut5.out\">\n")
	vpr_file.write("     0\n")
	vpr_file.write("     0\n")
	vpr_file.write("     0\n")
	vpr_file.write("     0\n")
	vpr_file.write("     0\n")
	vpr_file.write("  </delay_matrix>\n")
	vpr_file.write("  </pb_type>\n")
	vpr_file.write("  <pb_type name=\"ff\" blif_model=\".latch\" num_pb=\"1\" class=\"flipflop\">\n")
	vpr_file.write("  <input name=\"D\" num_pins=\"1\" port_class=\"D\"/>\n")
	vpr_file.write("  <output name=\"Q\" num_pins=\"1\" port_class=\"Q\"/>\n")
	vpr_file.write("  <clock name=\"clk\" num_pins=\"1\" port_class=\"clock\"/>\n")
	vpr_file.write("  <T_setup value=\"1.891e-11\" port=\"ff.D\" clock=\"clk\"/>\n")
	vpr_file.write("  <T_clock_to_Q max=\"6.032e-11\" port=\"ff.Q\" clock=\"clk\"/>\n")
	vpr_file.write("  </pb_type>\n")
	vpr_file.write("      <interconnect>\n")





	feedback_mux = {}
	input_num = 0
	direct_num = 1
	for input_name in lut_input_names:
		if Rfb.count(input_name) != 1 and input_num != 5:
			vpr_file.write("    <direct name=\"direct" + str(input_num) + "\" input=\"ble5.in_" + input_name.upper() + "\" output=\"lut5.in[" + str(input_num) + ":" + str(input_num) + "]\">\n")
			vpr_file.write("      <delay_constant max=\"" + str(lut_delays[input_name]) + "\" in_port=\"ble5.in_" + input_name.upper() + "\" out_port=\"lut5.in[" + str(input_num) + ":" + str(input_num) + "]\" />\n")
			vpr_file.write("    </direct>\n")

			direct_num = direct_num + 1

		elif input_num != 5:
			feedback_mux[input_name] = input_num

		input_num = input_num + 1

	vpr_file.write("      <!--Clock -->\n")

	vpr_file.write("      <direct name=\"direct" + str(direct_num) + "\" input=\"ble5.clk\" output=\"ff.clk\"/>\n")


	mux_num = 1
	for name in feedback_mux :
		vpr_file.write("      <!-- Register feedback mux -->   \n")
		vpr_file.write("      <mux name=\"mux" + str(mux_num) + "\" input=\"ble5.in_" + name.upper() + " ff.Q\" output=\"lut5.in[" + str(feedback_mux[name]) + ":" + str(feedback_mux[name]) + "]\">\n")
		vpr_file.write("        <delay_constant max=\"" + str(lut_delays[name]) + "\" in_port=\"ble5.in_" + name.upper() + "\" out_port=\"lut5.in[" + str(feedback_mux[name]) + ":" + str(feedback_mux[name]) + "]\" />\n")
		vpr_file.write("        <delay_constant max=\"" + str(lut_delays[name]) + "\" in_port=\"ff.Q\" out_port=\"lut5.in[" + str(feedback_mux[name]) + ":" + str(feedback_mux[name]) + "]\" />  \n")
		vpr_file.write("      </mux>\n")
		mux_num = mux_num + 1
		vpr_file.write("      <!-- FF input selection mux -->\n")
		vpr_file.write("      <mux name=\"" + str(mux_num) + "\" input=\"lut5.out ble5.in_" + name.upper() + "\" output=\"ff.D\">\n")
		vpr_file.write("        <delay_constant max=\"1.74588e-11\" in_port=\"lut5.out\" out_port=\"ff.D\" />\n")
		vpr_file.write("        <delay_constant max=\"1.74588e-11\" in_port=\"ble5.in_" + name.upper() + "\" out_port=\"ff.D\" />\n")
		vpr_file.write("      </mux>\n")
		mux_num = mux_num + 1


	vpr_file.write("      <!-- BLE output (local) -->\n")
	vpr_file.write("      <mux name=\"mux" + str(mux_num) + "\" input=\"ff.Q lut5.out\" output=\"ble5.out_local\">\n")
	vpr_file.write("        <delay_constant max=\"" + str(local_feedback) + "\" in_port=\"ff.Q\" out_port=\"ble5.out_local\" />\n")
	vpr_file.write("        <delay_constant max=\"" + str(local_feedback) + "\" in_port=\"lut5.out\" out_port=\"ble5.out_local\" />\n")
	vpr_file.write("      </mux>\n")
	mux_num = mux_num + 1

	vpr_file.write("      <!-- BLE output (routing 1) --> \n")
	vpr_file.write("      <mux name=\"mux" + str(mux_num) + "\" input=\"ff.Q lut5.out\" output=\"ble5.out_routing[0:0]\">\n")
	vpr_file.write("        <delay_constant max=\"" + str(logic_block_output)+ "\" in_port=\"ff.Q\" out_port=\"ble5.out_routing[0:0]\" />\n")
	vpr_file.write("        <delay_constant max=\"" + str(logic_block_output)+ "\" in_port=\"lut5.out\" out_port=\"ble5.out_routing[0:0]\" />\n")
	vpr_file.write("      </mux>\n")
	vpr_file.write(" </interconnect>\n")
	vpr_file.write("    </pb_type>\n")

	vpr_file.write("  <interconnect>\n")
	vpr_file.write(" <direct name=\"direct1\" input=\"lut5inter.in_A\" output=\"ble5[0:0].in_A\"/>\n")
	vpr_file.write(" <direct name=\"direct2\" input=\"lut5inter.in_B\" output=\"ble5[0:0].in_B\"/>\n")
	vpr_file.write(" <direct name=\"direct3\" input=\"lut5inter.in_C\" output=\"ble5[0:0].in_C\"/>\n")
	vpr_file.write(" <direct name=\"direct4\" input=\"lut5inter.in_D\" output=\"ble5[0:0].in_D\"/>\n")
	vpr_file.write(" <direct name=\"direct5\" input=\"lut5inter.in_E\" output=\"ble5[0:0].in_E\"/>\n")

	if independent_inputs > 4:
		vpr_file.write(" <direct name=\"direct6\" input=\"lut5inter.in_A2\" output=\"ble5[1:1].in_A\"/>\n")
	else:
		vpr_file.write(" <direct name=\"direct6\" input=\"lut5inter.in_A\" output=\"ble5[1:1].in_A\"/>\n")

	if independent_inputs > 3:
		vpr_file.write(" <direct name=\"direct7\" input=\"lut5inter.in_B2\" output=\"ble5[1:1].in_B\"/>\n")
	else:
		vpr_file.write(" <direct name=\"direct7\" input=\"lut5inter.in_B\" output=\"ble5[1:1].in_B\"/>\n")

	if independent_inputs > 2:
		vpr_file.write(" <direct name=\"direct8\" input=\"lut5inter.in_C2\" output=\"ble5[1:1].in_C\"/>\n")
	else:
		vpr_file.write(" <direct name=\"direct8\" input=\"lut5inter.in_C\" output=\"ble5[1:1].in_C\"/>\n")

	if independent_inputs > 1:
		vpr_file.write(" <direct name=\"direct9\" input=\"lut5inter.in_D2\" output=\"ble5[1:1].in_D\"/>\n")
	else:
		vpr_file.write(" <direct name=\"direct9\" input=\"lut5inter.in_D\" output=\"ble5[1:1].in_D\"/>\n")

	if independent_inputs > 0:
		vpr_file.write(" <direct name=\"direct10\" input=\"lut5inter.in_E2\" output=\"ble5[1:1].in_E\"/>\n")
	else:
		vpr_file.write(" <direct name=\"direct10\" input=\"lut5inter.in_E\" output=\"ble5[1:1].in_E\"/>\n")
	vpr_file.write(" <direct name=\"direct11\" input=\"ble5[1:0].out_local\" output=\"lut5inter.out_local\"/>\n")
	vpr_file.write(" <direct name=\"direct12\" input=\"ble5[1:0].out_routing\" output=\"lut5inter.out_routing\"/>\n") 

	vpr_file.write(" <complete name=\"complete1\" input=\"lut5inter.clk\" output=\"ble5[1:0].clk\"/> \n")                 
	vpr_file.write("        </interconnect>\n")  
	vpr_file.write("      </pb_type>\n")  




	vpr_file.write("  <interconnect>\n")
	vpr_file.write(" <direct name=\"direct1\" input=\"fle.in_A\" output=\"lut5inter.in_A\"/>\n")
	vpr_file.write(" <direct name=\"direct2\" input=\"fle.in_B\" output=\"lut5inter.in_B\"/>\n")
	vpr_file.write(" <direct name=\"direct3\" input=\"fle.in_C\" output=\"lut5inter.in_C\"/>\n")
	vpr_file.write(" <direct name=\"direct4\" input=\"fle.in_D\" output=\"lut5inter.in_D\"/>\n")
	vpr_file.write(" <direct name=\"direct5\" input=\"fle.in_E\" output=\"lut5inter.in_E\"/>\n")	
	vpr_file.write(" <direct name=\"direct7\" input=\"lut5inter.out_local\" output=\"fle.out_local\"/>\n")
	vpr_file.write(" <direct name=\"direct8\" input=\"lut5inter.out_routing\" output=\"fle.out_routing\"/>\n")
	vpr_file.write(" <direct name=\"direct9\" input=\"fle.clk\" output=\"lut5inter.clk\"/>\n")
	if independent_inputs > 0:
		vpr_file.write(" <direct name=\"direct10\" input=\"fle.in_E2\" output=\"lut5inter.in_E2\"/>\n")	
	if independent_inputs > 1:
		vpr_file.write(" <direct name=\"direct11\" input=\"fle.in_D2\" output=\"lut5inter.in_D2\"/>\n")	
	if independent_inputs > 2:
		vpr_file.write(" <direct name=\"direct12\" input=\"fle.in_C2\" output=\"lut5inter.in_C2\"/>\n")	
	if independent_inputs > 3:
		vpr_file.write(" <direct name=\"direct13\" input=\"fle.in_B2\" output=\"lut5inter.in_B2\"/>\n")
	if independent_inputs > 4:
		vpr_file.write(" <direct name=\"direct14\" input=\"fle.in_A2\" output=\"lut5inter.in_A2\"/>\n")	
	vpr_file.write(" </interconnect>\n")

	vpr_file.write("    </mode> \n")
	vpr_file.write("    </pb_type>\n")



	vpr_file.write("    <interconnect>\n")
	vpr_file.write("    <!-- 50% sparsely populated local routing -->\n")
	vpr_file.write("    <complete name=\"lutA\" input=\"clb.I4 clb.I3 fle[1:0].out_local fle[3:2].out_local fle[8:8].out_local\" output=\"fle[9:0].in_A\">\n")
	vpr_file.write("      <delay_constant max=\"" + str(local_CLB_routing) + "\" in_port=\"clb.I4\" out_port=\"fle.in_A\" />\n")
	vpr_file.write("      <delay_constant max=\"" + str(local_CLB_routing) + "\" in_port=\"clb.I3\" out_port=\"fle.in_A\" />\n")
	vpr_file.write("      </complete>\n")
	if independent_inputs > 4:
		vpr_file.write("    <complete name=\"lutA2\" input=\"clb.I4 clb.I3 fle[1:0].out_local fle[3:2].out_local fle[8:8].out_local\" output=\"fle[9:0].in_A2\">\n")
		vpr_file.write("      <delay_constant max=\"" + str(local_CLB_routing) + "\" in_port=\"clb.I4\" out_port=\"fle.in_A2\" />\n")
		vpr_file.write("      <delay_constant max=\"" + str(local_CLB_routing) + "\" in_port=\"clb.I3\" out_port=\"fle.in_A2\" />\n")
		vpr_file.write("      </complete>\n")
	vpr_file.write("    <complete name=\"lutB\" input=\"clb.I3 clb.I2 fle[3:2].out_local fle[5:4].out_local fle[9:9].out_local\" output=\"fle[9:0].in_B\">\n")
	vpr_file.write("      <delay_constant max=\"" + str(local_CLB_routing) + "\" in_port=\"clb.I3\" out_port=\"fle.in_B\" />\n")
	vpr_file.write("      <delay_constant max=\"" + str(local_CLB_routing) + "\" in_port=\"clb.I2\" out_port=\"fle.in_B\" />\n")
	vpr_file.write("      </complete>\n")
	if independent_inputs > 3:
		vpr_file.write("    <complete name=\"lutB2\" input=\"clb.I3 clb.I2 fle[3:2].out_local fle[5:4].out_local fle[9:9].out_local\" output=\"fle[9:0].in_B2\">\n")
		vpr_file.write("      <delay_constant max=\"" + str(local_CLB_routing) + "\" in_port=\"clb.I3\" out_port=\"fle.in_B2\" />\n")
		vpr_file.write("      <delay_constant max=\"" + str(local_CLB_routing) + "\" in_port=\"clb.I2\" out_port=\"fle.in_B2\" />\n")
		vpr_file.write("      </complete>\n")
	vpr_file.write("    <complete name=\"lutC\" input=\"clb.I2 clb.I1 fle[5:4].out_local fle[7:6].out_local fle[8:8].out_local\" output=\"fle[9:0].in_C\">\n")
	vpr_file.write("      <delay_constant max=\"" + str(local_CLB_routing) + "\" in_port=\"clb.I2\" out_port=\"fle.in_C\" />\n")
	vpr_file.write("      <delay_constant max=\"" + str(local_CLB_routing) + "\" in_port=\"clb.I1\" out_port=\"fle.in_C\" />\n")
	vpr_file.write("      </complete>\n")
	if independent_inputs > 2:
		vpr_file.write("    <complete name=\"lutC2\" input=\"clb.I2 clb.I1 fle[5:4].out_local fle[7:6].out_local fle[8:8].out_local\" output=\"fle[9:0].in_C2\">\n")
		vpr_file.write("      <delay_constant max=\"" + str(local_CLB_routing) + "\" in_port=\"clb.I2\" out_port=\"fle.in_C2\" />\n")
		vpr_file.write("      <delay_constant max=\"" + str(local_CLB_routing) + "\" in_port=\"clb.I1\" out_port=\"fle.in_C2\" />\n")
		vpr_file.write("      </complete>\n")
	vpr_file.write("    <complete name=\"lutD\" input=\"clb.I4 clb.I2 fle[1:0].out_local fle[5:4].out_local fle[9:9].out_local\" output=\"fle[9:0].in_D\">\n")
	vpr_file.write("      <delay_constant max=\"" + str(local_CLB_routing) + "\" in_port=\"clb.I4\" out_port=\"fle.in_D\" />\n")
	vpr_file.write("      <delay_constant max=\"" + str(local_CLB_routing) + "\" in_port=\"clb.I2\" out_port=\"fle.in_D\" />\n")
	vpr_file.write("      </complete>\n")
	if independent_inputs > 1:
		vpr_file.write("    <complete name=\"lutD2\" input=\"clb.I4 clb.I2 fle[1:0].out_local fle[5:4].out_local fle[9:9].out_local\" output=\"fle[9:0].in_D2\">\n")
		vpr_file.write("      <delay_constant max=\"" + str(local_CLB_routing) + "\" in_port=\"clb.I4\" out_port=\"fle.in_D2\" />\n")
		vpr_file.write("      <delay_constant max=\"" + str(local_CLB_routing) + "\" in_port=\"clb.I2\" out_port=\"fle.in_D2\" />\n")
		vpr_file.write("      </complete>\n")
	vpr_file.write("    <complete name=\"lutE\" input=\"clb.I3 clb.I1 fle[3:2].out_local fle[7:6].out_local fle[8:8].out_local\" output=\"fle[9:0].in_E\">\n")
	vpr_file.write("      <delay_constant max=\"" + str(local_CLB_routing) + "\" in_port=\"clb.I3\" out_port=\"fle.in_E\" />\n")
	vpr_file.write("      <delay_constant max=\"" + str(local_CLB_routing) + "\" in_port=\"clb.I1\" out_port=\"fle.in_E\" />\n")
	vpr_file.write("      </complete>\n")
	if independent_inputs > 0:
		vpr_file.write("    <complete name=\"lutE2\" input=\"clb.I3 clb.I1 fle[3:2].out_local fle[7:6].out_local fle[8:8].out_local\" output=\"fle[9:0].in_E2\">\n")
		vpr_file.write("      <delay_constant max=\"" + str(local_CLB_routing) + "\" in_port=\"clb.I3\" out_port=\"fle.in_E2\" />\n")
		vpr_file.write("      <delay_constant max=\"" + str(local_CLB_routing) + "\" in_port=\"clb.I1\" out_port=\"fle.in_E2\" />\n")
		vpr_file.write("      </complete>\n")		
	vpr_file.write("    <complete name=\"lutF\" input=\"clb.I4 clb.I1 fle[1:0].out_local fle[7:6].out_local fle[9:9].out_local\" output=\"fle[9:0].in_F\">\n")
	vpr_file.write("      <delay_constant max=\"" + str(local_CLB_routing) + "\" in_port=\"clb.I4\" out_port=\"fle.in_F\" />\n")
	vpr_file.write("      <delay_constant max=\"" + str(local_CLB_routing) + "\" in_port=\"clb.I1\" out_port=\"fle.in_F\" />\n")
	vpr_file.write("      </complete>\n")
	vpr_file.write("      <complete name=\"clks\" input=\"clb.clk\" output=\"fle[9:0].clk\">\n")
	vpr_file.write("      </complete>\n")
	          
	vpr_file.write("      <!-- Direct connections to CLB outputs -->\n")
	vpr_file.write("      <direct name=\"clbouts1\" input=\"fle[0:0].out_routing\" output=\"clb.O1\"/>\n")
	vpr_file.write("      <direct name=\"clbouts2\" input=\"fle[1:1].out_routing\" output=\"clb.O2\"/>\n")
	vpr_file.write("      <direct name=\"clbouts3\" input=\"fle[2:2].out_routing\" output=\"clb.O3\"/>\n")
	vpr_file.write("      <direct name=\"clbouts4\" input=\"fle[3:3].out_routing\" output=\"clb.O4\"/>\n")
	vpr_file.write("      <direct name=\"clbouts5\" input=\"fle[4:4].out_routing\" output=\"clb.O5\"/>\n")
	vpr_file.write("      <direct name=\"clbouts6\" input=\"fle[5:5].out_routing\" output=\"clb.O6\"/>\n")
	vpr_file.write("      <direct name=\"clbouts7\" input=\"fle[6:6].out_routing\" output=\"clb.O7\"/>\n")
	vpr_file.write("      <direct name=\"clbouts8\" input=\"fle[7:7].out_routing\" output=\"clb.O8\"/>\n")
	vpr_file.write("      <direct name=\"clbouts9\" input=\"fle[8:8].out_routing\" output=\"clb.O9\"/>\n")
	vpr_file.write("      <direct name=\"clbouts10\" input=\"fle[9:9].out_routing\" output=\"clb.O10\"/>\n")

	vpr_file.write("    </interconnect>\n")
	vpr_file.write("    <fc default_in_type=\"frac\" default_in_val=\"" + str(Fcin) + "\" default_out_type=\"frac\" default_out_val=\"" + str(Fcout) + "\"/>\n")
	vpr_file.write("    <!-- Two sided connectivity CLB architecture--> \n")
	vpr_file.write("    <pinlocations pattern=\"custom\">\n")
	vpr_file.write("  <loc side=\"right\">clb.O1 clb.O2 clb.O3 clb.O4 clb.O5 clb.I1 clb.I3 clb.clk</loc> \n")
	vpr_file.write("      <loc side=\"bottom\">clb.O6 clb.O7 clb.O8 clb.O9 clb.O10 clb.I2 clb.I4 clb.clk</loc>      \n")
	vpr_file.write("    </pinlocations>\n")

	vpr_file.write("  </pb_type>\n")

	vpr_file.write("  <!-- This is the 36*36 uniform mult -->\n")
	vpr_file.write("  <pb_type name=\"mult_36\" height=\"4\">\n")
	vpr_file.write("      <input name=\"a\" num_pins=\"36\"/>\n")
	vpr_file.write("      <input name=\"b\" num_pins=\"36\"/>\n")
	vpr_file.write("      <output name=\"out\" num_pins=\"72\"/>\n")

	vpr_file.write("      <mode name=\"two_divisible_mult_18x18\">\n")
	vpr_file.write("        <pb_type name=\"divisible_mult_18x18\" num_pb=\"2\">\n")
	vpr_file.write("          <input name=\"a\" num_pins=\"18\"/>\n")
	vpr_file.write("          <input name=\"b\" num_pins=\"18\"/>\n")
	vpr_file.write("          <output name=\"out\" num_pins=\"36\"/>\n")

	vpr_file.write("          <mode name=\"two_mult_9x9\">\n")
	vpr_file.write("            <pb_type name=\"mult_9x9_slice\" num_pb=\"2\">\n")
	vpr_file.write("              <input name=\"A_cfg\" num_pins=\"9\"/>\n")
	vpr_file.write("              <input name=\"B_cfg\" num_pins=\"9\"/>\n")
	vpr_file.write("              <output name=\"OUT_cfg\" num_pins=\"18\"/>\n")

	vpr_file.write("              <pb_type name=\"mult_9x9\" blif_model=\".subckt multiply\" num_pb=\"1\">\n")
	vpr_file.write("                <input name=\"a\" num_pins=\"9\"/>\n")
	vpr_file.write("                <input name=\"b\" num_pins=\"9\"/>\n")
	vpr_file.write("                <output name=\"out\" num_pins=\"18\"/>\n")
	vpr_file.write("                <delay_constant max=\"1.667e-9\" in_port=\"mult_9x9.a\" out_port=\"mult_9x9.out\"/>\n")
	vpr_file.write("                <delay_constant max=\"1.667e-9\" in_port=\"mult_9x9.b\" out_port=\"mult_9x9.out\"/>\n")
	vpr_file.write("              </pb_type>\n")

	vpr_file.write("              <interconnect>\n")
	vpr_file.write("                <direct name=\"a2a\" input=\"mult_9x9_slice.A_cfg\" output=\"mult_9x9.a\">\n")
	vpr_file.write("                </direct>\n")
	vpr_file.write("                <direct name=\"b2b\" input=\"mult_9x9_slice.B_cfg\" output=\"mult_9x9.b\">\n")
	vpr_file.write("                </direct>\n")
	vpr_file.write("                <direct name=\"out2out\" input=\"mult_9x9.out\" output=\"mult_9x9_slice.OUT_cfg\">\n")
	vpr_file.write("                </direct>\n")
	vpr_file.write("              </interconnect>\n")
	vpr_file.write("            </pb_type>\n")
	vpr_file.write("            <interconnect>\n")
	vpr_file.write("              <direct name=\"a2a\" input=\"divisible_mult_18x18.a\" output=\"mult_9x9_slice[1:0].A_cfg\">\n")
	vpr_file.write("              </direct>\n")
	vpr_file.write("              <direct name=\"b2b\" input=\"divisible_mult_18x18.b\" output=\"mult_9x9_slice[1:0].B_cfg\">\n")
	vpr_file.write("              </direct>\n")
	vpr_file.write("              <direct name=\"out2out\" input=\"mult_9x9_slice[1:0].OUT_cfg\" output=\"divisible_mult_18x18.out\">\n")
	vpr_file.write("              </direct>\n")
	vpr_file.write("            </interconnect>\n")
	vpr_file.write("          </mode>\n")

	vpr_file.write("          <mode name=\"mult_18x18\">\n")
	vpr_file.write("            <pb_type name=\"mult_18x18_slice\" num_pb=\"1\">\n")
	vpr_file.write("              <input name=\"A_cfg\" num_pins=\"18\"/>\n")
	vpr_file.write("              <input name=\"B_cfg\" num_pins=\"18\"/>\n")
	vpr_file.write("              <output name=\"OUT_cfg\" num_pins=\"36\"/>\n")

	vpr_file.write("              <pb_type name=\"mult_18x18\" blif_model=\".subckt multiply\" num_pb=\"1\" >\n")
	vpr_file.write("                <input name=\"a\" num_pins=\"18\"/>\n")
	vpr_file.write("                <input name=\"b\" num_pins=\"18\"/>\n")
	vpr_file.write("                <output name=\"out\" num_pins=\"36\"/>\n")
	vpr_file.write("                <delay_constant max=\"1.667e-9\" in_port=\"mult_18x18.a\" out_port=\"mult_18x18.out\"/>\n")
	vpr_file.write("                <delay_constant max=\"1.667e-9\" in_port=\"mult_18x18.b\" out_port=\"mult_18x18.out\"/>\n")
	vpr_file.write("              </pb_type>\n")

	vpr_file.write("              <interconnect>\n")
	vpr_file.write("                <direct name=\"a2a\" input=\"mult_18x18_slice.A_cfg\" output=\"mult_18x18.a\">\n")
	vpr_file.write("                </direct>\n")
	vpr_file.write("                <direct name=\"b2b\" input=\"mult_18x18_slice.B_cfg\" output=\"mult_18x18.b\">\n")
	vpr_file.write("                </direct>\n")
	vpr_file.write("                <direct name=\"out2out\" input=\"mult_18x18.out\" output=\"mult_18x18_slice.OUT_cfg\">\n")
	vpr_file.write("                </direct>\n")
	vpr_file.write("              </interconnect>\n")
	vpr_file.write("            </pb_type>\n")
	vpr_file.write("            <interconnect>\n")
	vpr_file.write("              <direct name=\"a2a\" input=\"divisible_mult_18x18.a\" output=\"mult_18x18_slice.A_cfg\">\n")
	vpr_file.write("              </direct>\n")
	vpr_file.write("              <direct name=\"b2b\" input=\"divisible_mult_18x18.b\" output=\"mult_18x18_slice.B_cfg\">\n")
	vpr_file.write("              </direct>\n")
	vpr_file.write("              <direct name=\"out2out\" input=\"mult_18x18_slice.OUT_cfg\" output=\"divisible_mult_18x18.out\">\n")
	vpr_file.write("              </direct>\n")
	vpr_file.write("            </interconnect>\n")
	vpr_file.write("          </mode>\n")
	vpr_file.write("        </pb_type>\n")
	vpr_file.write("        <interconnect>\n")
	vpr_file.write("          <direct name=\"a2a\" input=\"mult_36.a\" output=\"divisible_mult_18x18[1:0].a\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"b2b\" input=\"mult_36.b\" output=\"divisible_mult_18x18[1:0].b\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"out2out\" input=\"divisible_mult_18x18[1:0].out\" output=\"mult_36.out\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("        </interconnect>\n")
	vpr_file.write("      </mode>\n")

	vpr_file.write("      <mode name=\"mult_36x36\">\n")
	vpr_file.write("        <pb_type name=\"mult_36x36_slice\" num_pb=\"1\">\n")
	vpr_file.write("          <input name=\"A_cfg\" num_pins=\"36\"/>\n")
	vpr_file.write("          <input name=\"B_cfg\" num_pins=\"36\"/>\n")
	vpr_file.write("          <output name=\"OUT_cfg\" num_pins=\"72\"/>\n")

	vpr_file.write("          <pb_type name=\"mult_36x36\" blif_model=\".subckt multiply\" num_pb=\"1\">\n")
	vpr_file.write("            <input name=\"a\" num_pins=\"36\"/>\n")
	vpr_file.write("            <input name=\"b\" num_pins=\"36\"/>\n")
	vpr_file.write("            <output name=\"out\" num_pins=\"72\"/>\n")
	vpr_file.write("            <delay_constant max=\"1.667e-9\" in_port=\"mult_36x36.a\" out_port=\"mult_36x36.out\"/>\n")
	vpr_file.write("            <delay_constant max=\"1.667e-9\" in_port=\"mult_36x36.b\" out_port=\"mult_36x36.out\"/>\n")
	vpr_file.write("          </pb_type>\n")

	vpr_file.write("          <interconnect>\n")
	vpr_file.write("            <direct name=\"a2a\" input=\"mult_36x36_slice.A_cfg\" output=\"mult_36x36.a\">\n")
	vpr_file.write("            </direct>\n")
	vpr_file.write("            <direct name=\"b2b\" input=\"mult_36x36_slice.B_cfg\" output=\"mult_36x36.b\">\n")
	vpr_file.write("            </direct>\n")
	vpr_file.write("            <direct name=\"out2out\" input=\"mult_36x36.out\" output=\"mult_36x36_slice.OUT_cfg\">\n")
	vpr_file.write("            </direct>\n")
	vpr_file.write("          </interconnect>\n")
	vpr_file.write("        </pb_type>\n")
	vpr_file.write("        <interconnect>\n")
	vpr_file.write("          <direct name=\"a2a\" input=\"mult_36.a\" output=\"mult_36x36_slice.A_cfg\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"b2b\" input=\"mult_36.b\" output=\"mult_36x36_slice.B_cfg\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"out2out\" input=\"mult_36x36_slice.OUT_cfg\" output=\"mult_36.out\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("        </interconnect>\n")
	vpr_file.write("      </mode>\n")

	vpr_file.write("    <fc default_in_type=\"frac\" default_in_val=\"0.15\" default_out_type=\"frac\" default_out_val=\"0.10\"/>\n")
	vpr_file.write("    <pinlocations pattern=\"spread\"/>\n")


	vpr_file.write("  </pb_type>\n")


	vpr_file.write("<!-- 32 Kb Memory based off Stratix IV 9K memory and Virtex V 36 Kb.  Setup time set to match flip-flop setup time at 40 nm. Clock to q based off Stratix IV 600 max MHz  -->\n")
	vpr_file.write("  <pb_type name=\"memory\" height=\"6\">\n")
	vpr_file.write("      <input name=\"addr1\" num_pins=\"15\"/>\n")
	vpr_file.write("      <input name=\"addr2\" num_pins=\"15\"/>\n")
	vpr_file.write("      <input name=\"data\" num_pins=\"64\"/>\n")
	vpr_file.write("      <input name=\"we1\" num_pins=\"1\"/>\n")
	vpr_file.write("      <input name=\"we2\" num_pins=\"1\"/>\n")
	vpr_file.write("      <output name=\"out\" num_pins=\"64\"/>\n")
	vpr_file.write("      <clock name=\"clk\" num_pins=\"1\"/>\n")

	vpr_file.write("      <mode name=\"mem_512x64_sp\">\n")
	vpr_file.write("        <pb_type name=\"mem_512x64_sp\" blif_model=\".subckt single_port_ram\" class=\"memory\" num_pb=\"1\">\n")
	vpr_file.write("          <input name=\"addr\" num_pins=\"9\" port_class=\"address\"/>\n")
	vpr_file.write("          <input name=\"data\" num_pins=\"64\" port_class=\"data_in\"/>\n")
	vpr_file.write("          <input name=\"we\" num_pins=\"1\" port_class=\"write_en\"/>\n")
	vpr_file.write("          <output name=\"out\" num_pins=\"64\" port_class=\"data_out\"/>\n")
	vpr_file.write("          <clock name=\"clk\" num_pins=\"1\" port_class=\"clock\"/>\n")
	vpr_file.write("          <T_setup value=\"2.448e-10\" port=\"mem_512x64_sp.addr\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_setup value=\"2.448e-10\" port=\"mem_512x64_sp.data\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_setup value=\"2.448e-10\" port=\"mem_512x64_sp.we\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_clock_to_Q max=\"1.667e-9\" port=\"mem_512x64_sp.out\" clock=\"clk\"/>\n")
	vpr_file.write("        </pb_type>\n")
	vpr_file.write("        <interconnect>\n")
	vpr_file.write("          <direct name=\"address1\" input=\"memory.addr1[8:0]\" output=\"mem_512x64_sp.addr\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"data1\" input=\"memory.data[63:0]\" output=\"mem_512x64_sp.data\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"writeen1\" input=\"memory.we1\" output=\"mem_512x64_sp.we\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"dataout1\" input=\"mem_512x64_sp.out\" output=\"memory.out[63:0]\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"clk\" input=\"memory.clk\" output=\"mem_512x64_sp.clk\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("        </interconnect>\n")
	vpr_file.write("      </mode>\n")
	          
	vpr_file.write("      <mode name=\"mem_1024x32_sp\">\n")
	vpr_file.write("        <pb_type name=\"mem_1024x32_sp\" blif_model=\".subckt single_port_ram\" class=\"memory\" num_pb=\"1\">\n")
	vpr_file.write("          <input name=\"addr\" num_pins=\"" + str(N) + "\" port_class=\"address\"/>\n")
	vpr_file.write("          <input name=\"data\" num_pins=\"32\" port_class=\"data_in\"/>\n")
	vpr_file.write("          <input name=\"we\" num_pins=\"1\" port_class=\"write_en\"/>\n")
	vpr_file.write("          <output name=\"out\" num_pins=\"32\" port_class=\"data_out\"/>\n")
	vpr_file.write("          <clock name=\"clk\" num_pins=\"1\" port_class=\"clock\"/>\n")
	vpr_file.write("          <T_setup value=\"2.448e-10\" port=\"mem_1024x32_sp.addr\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_setup value=\"2.448e-10\" port=\"mem_1024x32_sp.data\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_setup value=\"2.448e-10\" port=\"mem_1024x32_sp.we\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_clock_to_Q max=\"1.667e-9\" port=\"mem_1024x32_sp.out\" clock=\"clk\"/>\n")
	vpr_file.write("        </pb_type>\n")
	vpr_file.write("        <interconnect>\n")
	vpr_file.write("          <direct name=\"address1\" input=\"memory.addr1[9:0]\" output=\"mem_1024x32_sp.addr\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"data1\" input=\"memory.data[31:0]\" output=\"mem_1024x32_sp.data\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"writeen1\" input=\"memory.we1\" output=\"mem_1024x32_sp.we\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"dataout1\" input=\"mem_1024x32_sp.out\" output=\"memory.out[31:0]\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"clk\" input=\"memory.clk\" output=\"mem_1024x32_sp.clk\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("        </interconnect>\n")
	vpr_file.write("      </mode>\n")

	          
	vpr_file.write("      <mode name=\"mem_2048x16_sp\">\n")
	vpr_file.write("        <pb_type name=\"mem_2048x16_sp\" blif_model=\".subckt single_port_ram\" class=\"memory\" num_pb=\"1\">\n")
	vpr_file.write("          <input name=\"addr\" num_pins=\"11\" port_class=\"address\"/>\n")
	vpr_file.write("          <input name=\"data\" num_pins=\"16\" port_class=\"data_in\"/>\n")
	vpr_file.write("          <input name=\"we\" num_pins=\"1\" port_class=\"write_en\"/>\n")
	vpr_file.write("          <output name=\"out\" num_pins=\"16\" port_class=\"data_out\"/>\n")
	vpr_file.write("          <clock name=\"clk\" num_pins=\"1\" port_class=\"clock\"/>\n")
	vpr_file.write("          <T_setup value=\"2.448e-10\" port=\"mem_2048x16_sp.addr\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_setup value=\"2.448e-10\" port=\"mem_2048x16_sp.data\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_setup value=\"2.448e-10\" port=\"mem_2048x16_sp.we\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_clock_to_Q max=\"1.667e-9\" port=\"mem_2048x16_sp.out\" clock=\"clk\"/>\n")
	vpr_file.write("        </pb_type>\n")
	vpr_file.write("        <interconnect>\n")
	vpr_file.write("          <direct name=\"address1\" input=\"memory.addr1[10:0]\" output=\"mem_2048x16_sp.addr\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"data1\" input=\"memory.data[15:0]\" output=\"mem_2048x16_sp.data\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"writeen1\" input=\"memory.we1\" output=\"mem_2048x16_sp.we\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"dataout1\" input=\"mem_2048x16_sp.out\" output=\"memory.out[15:0]\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"clk\" input=\"memory.clk\" output=\"mem_2048x16_sp.clk\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("        </interconnect>\n")
	vpr_file.write("      </mode>\n")

	vpr_file.write("      <mode name=\"mem_4096x8_sp\">\n")
	vpr_file.write("        <pb_type name=\"mem_4096x8_sp\" blif_model=\".subckt single_port_ram\" class=\"memory\" num_pb=\"1\">\n")
	vpr_file.write("          <input name=\"addr\" num_pins=\"12\" port_class=\"address\"/>\n")
	vpr_file.write("          <input name=\"data\" num_pins=\"8\" port_class=\"data_in\"/>\n")
	vpr_file.write("          <input name=\"we\" num_pins=\"1\" port_class=\"write_en\"/>\n")
	vpr_file.write("          <output name=\"out\" num_pins=\"8\" port_class=\"data_out\"/>\n")
	vpr_file.write("          <clock name=\"clk\" num_pins=\"1\" port_class=\"clock\"/>\n")
	vpr_file.write("          <T_setup value=\"2.448e-10\" port=\"mem_4096x8_sp.addr\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_setup value=\"2.448e-10\" port=\"mem_4096x8_sp.data\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_setup value=\"2.448e-10\" port=\"mem_4096x8_sp.we\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_clock_to_Q max=\"1.667e-9\" port=\"mem_4096x8_sp.out\" clock=\"clk\"/>\n")
	vpr_file.write("        </pb_type>\n")
	vpr_file.write("        <interconnect>\n")
	vpr_file.write("          <direct name=\"address1\" input=\"memory.addr1[11:0]\" output=\"mem_4096x8_sp.addr\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"data1\" input=\"memory.data[7:0]\" output=\"mem_4096x8_sp.data\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"writeen1\" input=\"memory.we1\" output=\"mem_4096x8_sp.we\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"dataout1\" input=\"mem_4096x8_sp.out\" output=\"memory.out[7:0]\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"clk\" input=\"memory.clk\" output=\"mem_4096x8_sp.clk\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("        </interconnect>\n")
	vpr_file.write("      </mode>\n")
	 
	vpr_file.write("      <mode name=\"mem_8192x4_sp\">\n")
	vpr_file.write("        <pb_type name=\"mem_8192x4_sp\" blif_model=\".subckt single_port_ram\" class=\"memory\" num_pb=\"1\">\n")
	vpr_file.write("          <input name=\"addr\" num_pins=\"13\" port_class=\"address\"/>\n")
	vpr_file.write("          <input name=\"data\" num_pins=\"4\" port_class=\"data_in\"/>\n")
	vpr_file.write("          <input name=\"we\" num_pins=\"1\" port_class=\"write_en\"/>\n")
	vpr_file.write("          <output name=\"out\" num_pins=\"4\" port_class=\"data_out\"/>\n")
	vpr_file.write("          <clock name=\"clk\" num_pins=\"1\" port_class=\"clock\"/>\n")
	vpr_file.write("          <T_setup value=\"2.448e-10\" port=\"mem_8192x4_sp.addr\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_setup value=\"2.448e-10\" port=\"mem_8192x4_sp.data\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_setup value=\"2.448e-10\" port=\"mem_8192x4_sp.we\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_clock_to_Q max=\"1.667e-9\" port=\"mem_8192x4_sp.out\" clock=\"clk\"/>\n")
	vpr_file.write("        </pb_type>\n")
	vpr_file.write("        <interconnect>\n")
	vpr_file.write("          <direct name=\"address1\" input=\"memory.addr1[12:0]\" output=\"mem_8192x4_sp.addr\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"data1\" input=\"memory.data[3:0]\" output=\"mem_8192x4_sp.data\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"writeen1\" input=\"memory.we1\" output=\"mem_8192x4_sp.we\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"dataout1\" input=\"mem_8192x4_sp.out\" output=\"memory.out[3:0]\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"clk\" input=\"memory.clk\" output=\"mem_8192x4_sp.clk\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("        </interconnect>\n")
	vpr_file.write("      </mode>\n")

	vpr_file.write("      <mode name=\"mem_16384x2_sp\">\n")
	vpr_file.write("        <pb_type name=\"mem_16384x2_sp\" blif_model=\".subckt single_port_ram\" class=\"memory\" num_pb=\"1\">\n")
	vpr_file.write("          <input name=\"addr\" num_pins=\"14\" port_class=\"address\"/>\n")
	vpr_file.write("          <input name=\"data\" num_pins=\"2\" port_class=\"data_in\"/>\n")
	vpr_file.write("          <input name=\"we\" num_pins=\"1\" port_class=\"write_en\"/>\n")
	vpr_file.write("          <output name=\"out\" num_pins=\"2\" port_class=\"data_out\"/>\n")
	vpr_file.write("          <clock name=\"clk\" num_pins=\"1\" port_class=\"clock\"/>\n")
	vpr_file.write("          <T_setup value=\"2.448e-10\" port=\"mem_16384x2_sp.addr\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_setup value=\"2.448e-10\" port=\"mem_16384x2_sp.data\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_setup value=\"2.448e-10\" port=\"mem_16384x2_sp.we\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_clock_to_Q max=\"1.667e-9\" port=\"mem_16384x2_sp.out\" clock=\"clk\"/>\n")
	vpr_file.write("        </pb_type>\n")
	vpr_file.write("        <interconnect>\n")
	vpr_file.write("          <direct name=\"address1\" input=\"memory.addr1[13:0]\" output=\"mem_16384x2_sp.addr\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"data1\" input=\"memory.data[1:0]\" output=\"mem_16384x2_sp.data\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"writeen1\" input=\"memory.we1\" output=\"mem_16384x2_sp.we\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"dataout1\" input=\"mem_16384x2_sp.out\" output=\"memory.out[1:0]\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"clk\" input=\"memory.clk\" output=\"mem_16384x2_sp.clk\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("        </interconnect>\n")
	vpr_file.write("      </mode>  \n")
	          
	vpr_file.write("      <mode name=\"mem_32768x1_sp\">\n")
	vpr_file.write("        <pb_type name=\"mem_32768x1_sp\" blif_model=\".subckt single_port_ram\" class=\"memory\" num_pb=\"1\">\n")
	vpr_file.write("          <input name=\"addr\" num_pins=\"15\" port_class=\"address\"/>\n")
	vpr_file.write("          <input name=\"data\" num_pins=\"1\" port_class=\"data_in\"/>\n")
	vpr_file.write("          <input name=\"we\" num_pins=\"1\" port_class=\"write_en\"/>\n")
	vpr_file.write("          <output name=\"out\" num_pins=\"1\" port_class=\"data_out\"/>\n")
	vpr_file.write("          <clock name=\"clk\" num_pins=\"1\" port_class=\"clock\"/>\n")
	vpr_file.write("          <T_setup value=\"2.448e-10\" port=\"mem_32768x1_sp.addr\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_setup value=\"2.448e-10\" port=\"mem_32768x1_sp.data\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_setup value=\"2.448e-10\" port=\"mem_32768x1_sp.we\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_clock_to_Q max=\"1.667e-9\" port=\"mem_32768x1_sp.out\" clock=\"clk\"/>\n")
	vpr_file.write("        </pb_type>\n")
	vpr_file.write("        <interconnect>\n")
	vpr_file.write("          <direct name=\"address1\" input=\"memory.addr1[14:0]\" output=\"mem_32768x1_sp.addr\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"data1\" input=\"memory.data[0:0]\" output=\"mem_32768x1_sp.data\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"writeen1\" input=\"memory.we1\" output=\"mem_32768x1_sp.we\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"dataout1\" input=\"mem_32768x1_sp.out\" output=\"memory.out[0:0]\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"clk\" input=\"memory.clk\" output=\"mem_32768x1_sp.clk\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("        </interconnect>\n")
	vpr_file.write("      </mode> \n")
	                   
	vpr_file.write("      <mode name=\"mem_1024x32_dp\">\n")
	vpr_file.write("        <pb_type name=\"mem_1024x32_dp\" blif_model=\".subckt dual_port_ram\" class=\"memory\" num_pb=\"1\">\n")
	vpr_file.write("          <input name=\"addr1\" num_pins=\"" + str(N) + "\" port_class=\"address1\"/>\n")
	vpr_file.write("          <input name=\"addr2\" num_pins=\"" + str(N) + "\" port_class=\"address2\"/>\n")
	vpr_file.write("          <input name=\"data1\" num_pins=\"32\" port_class=\"data_in1\"/>\n")
	vpr_file.write("          <input name=\"data2\" num_pins=\"32\" port_class=\"data_in2\"/>\n")
	vpr_file.write("          <input name=\"we1\" num_pins=\"1\" port_class=\"write_en1\"/>\n")
	vpr_file.write("          <input name=\"we2\" num_pins=\"1\" port_class=\"write_en2\"/>\n")
	vpr_file.write("          <output name=\"out1\" num_pins=\"32\" port_class=\"data_out1\"/>\n")
	vpr_file.write("          <output name=\"out2\" num_pins=\"32\" port_class=\"data_out2\"/>\n")
	vpr_file.write("          <clock name=\"clk\" num_pins=\"1\" port_class=\"clock\"/>\n")
	vpr_file.write("          <T_setup value=\"2.448e-10\" port=\"mem_1024x32_dp.addr1\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_setup value=\"2.448e-10\" port=\"mem_1024x32_dp.data1\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_setup value=\"2.448e-10\" port=\"mem_1024x32_dp.we1\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_setup value=\"2.448e-10\" port=\"mem_1024x32_dp.addr2\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_setup value=\"2.448e-10\" port=\"mem_1024x32_dp.data2\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_setup value=\"2.448e-10\" port=\"mem_1024x32_dp.we2\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_clock_to_Q max=\"1.667e-9\" port=\"mem_1024x32_dp.out1\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_clock_to_Q max=\"1.667e-9\" port=\"mem_1024x32_dp.out2\" clock=\"clk\"/>\n")
	vpr_file.write("        </pb_type>\n")
	vpr_file.write("        <interconnect>\n")
	vpr_file.write("          <direct name=\"address1\" input=\"memory.addr1[9:0]\" output=\"mem_1024x32_dp.addr1\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"address2\" input=\"memory.addr2[9:0]\" output=\"mem_1024x32_dp.addr2\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"data1\" input=\"memory.data[31:0]\" output=\"mem_1024x32_dp.data1\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"data2\" input=\"memory.data[63:32]\" output=\"mem_1024x32_dp.data2\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"writeen1\" input=\"memory.we1\" output=\"mem_1024x32_dp.we1\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"writeen2\" input=\"memory.we2\" output=\"mem_1024x32_dp.we2\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"dataout1\" input=\"mem_1024x32_dp.out1\" output=\"memory.out[31:0]\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"dataout2\" input=\"mem_1024x32_dp.out2\" output=\"memory.out[63:32]\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"clk\" input=\"memory.clk\" output=\"mem_1024x32_dp.clk\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("        </interconnect>\n")
	vpr_file.write("      </mode>\n")
	          
	vpr_file.write("      <mode name=\"mem_2048x16_dp\">\n")
	vpr_file.write("        <pb_type name=\"mem_2048x16_dp\" blif_model=\".subckt dual_port_ram\" class=\"memory\" num_pb=\"1\">\n")
	vpr_file.write("          <input name=\"addr1\" num_pins=\"11\" port_class=\"address1\"/>\n")
	vpr_file.write("          <input name=\"addr2\" num_pins=\"11\" port_class=\"address2\"/>\n")
	vpr_file.write("          <input name=\"data1\" num_pins=\"16\" port_class=\"data_in1\"/>\n")
	vpr_file.write("          <input name=\"data2\" num_pins=\"16\" port_class=\"data_in2\"/>\n")
	vpr_file.write("          <input name=\"we1\" num_pins=\"1\" port_class=\"write_en1\"/>\n")
	vpr_file.write("          <input name=\"we2\" num_pins=\"1\" port_class=\"write_en2\"/>\n")
	vpr_file.write("          <output name=\"out1\" num_pins=\"16\" port_class=\"data_out1\"/>\n")
	vpr_file.write("          <output name=\"out2\" num_pins=\"16\" port_class=\"data_out2\"/>\n")
	vpr_file.write("          <clock name=\"clk\" num_pins=\"1\" port_class=\"clock\"/>\n")
	vpr_file.write("          <T_setup value=\"2.448e-10\" port=\"mem_2048x16_dp.addr1\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_setup value=\"2.448e-10\" port=\"mem_2048x16_dp.data1\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_setup value=\"2.448e-10\" port=\"mem_2048x16_dp.we1\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_setup value=\"2.448e-10\" port=\"mem_2048x16_dp.addr2\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_setup value=\"2.448e-10\" port=\"mem_2048x16_dp.data2\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_setup value=\"2.448e-10\" port=\"mem_2048x16_dp.we2\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_clock_to_Q max=\"1.667e-9\" port=\"mem_2048x16_dp.out1\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_clock_to_Q max=\"1.667e-9\" port=\"mem_2048x16_dp.out2\" clock=\"clk\"/>\n")
	vpr_file.write("        </pb_type>\n")
	vpr_file.write("        <interconnect>\n")
	vpr_file.write("          <direct name=\"address1\" input=\"memory.addr1[10:0]\" output=\"mem_2048x16_dp.addr1\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"address2\" input=\"memory.addr2[10:0]\" output=\"mem_2048x16_dp.addr2\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"data1\" input=\"memory.data[15:0]\" output=\"mem_2048x16_dp.data1\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"data2\" input=\"memory.data[31:16]\" output=\"mem_2048x16_dp.data2\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"writeen1\" input=\"memory.we1\" output=\"mem_2048x16_dp.we1\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"writeen2\" input=\"memory.we2\" output=\"mem_2048x16_dp.we2\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"dataout1\" input=\"mem_2048x16_dp.out1\" output=\"memory.out[15:0]\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"dataout2\" input=\"mem_2048x16_dp.out2\" output=\"memory.out[31:16]\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"clk\" input=\"memory.clk\" output=\"mem_2048x16_dp.clk\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("        </interconnect>\n")
	vpr_file.write("      </mode>\n")
	          
	vpr_file.write("      <mode name=\"mem_2048x8_dp\">\n")
	vpr_file.write("        <pb_type name=\"mem_2048x8_dp\" blif_model=\".subckt dual_port_ram\" class=\"memory\" num_pb=\"1\">\n")
	vpr_file.write("          <input name=\"addr1\" num_pins=\"12\" port_class=\"address1\"/>\n")
	vpr_file.write("          <input name=\"addr2\" num_pins=\"12\" port_class=\"address2\"/>\n")
	vpr_file.write("          <input name=\"data1\" num_pins=\"8\" port_class=\"data_in1\"/>\n")
	vpr_file.write("          <input name=\"data2\" num_pins=\"8\" port_class=\"data_in2\"/>\n")
	vpr_file.write("          <input name=\"we1\" num_pins=\"1\" port_class=\"write_en1\"/>\n")
	vpr_file.write("          <input name=\"we2\" num_pins=\"1\" port_class=\"write_en2\"/>\n")
	vpr_file.write("          <output name=\"out1\" num_pins=\"8\" port_class=\"data_out1\"/>\n")
	vpr_file.write("          <output name=\"out2\" num_pins=\"8\" port_class=\"data_out2\"/>\n")
	vpr_file.write("          <clock name=\"clk\" num_pins=\"1\" port_class=\"clock\"/>\n")
	vpr_file.write("          <T_setup value=\"2.448e-10\" port=\"mem_2048x8_dp.addr1\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_setup value=\"2.448e-10\" port=\"mem_2048x8_dp.data1\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_setup value=\"2.448e-10\" port=\"mem_2048x8_dp.we1\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_setup value=\"2.448e-10\" port=\"mem_2048x8_dp.addr2\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_setup value=\"2.448e-10\" port=\"mem_2048x8_dp.data2\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_setup value=\"2.448e-10\" port=\"mem_2048x8_dp.we2\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_clock_to_Q max=\"1.667e-9\" port=\"mem_2048x8_dp.out1\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_clock_to_Q max=\"1.667e-9\" port=\"mem_2048x8_dp.out2\" clock=\"clk\"/>\n")
	vpr_file.write("        </pb_type>\n")
	vpr_file.write("        <interconnect>\n")
	vpr_file.write("          <direct name=\"address1\" input=\"memory.addr1[11:0]\" output=\"mem_2048x8_dp.addr1\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"address2\" input=\"memory.addr2[11:0]\" output=\"mem_2048x8_dp.addr2\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"data1\" input=\"memory.data[7:0]\" output=\"mem_2048x8_dp.data1\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"data2\" input=\"memory.data[15:8]\" output=\"mem_2048x8_dp.data2\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"writeen1\" input=\"memory.we1\" output=\"mem_2048x8_dp.we1\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"writeen2\" input=\"memory.we2\" output=\"mem_2048x8_dp.we2\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"dataout1\" input=\"mem_2048x8_dp.out1\" output=\"memory.out[7:0]\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"dataout2\" input=\"mem_2048x8_dp.out2\" output=\"memory.out[15:8]\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"clk\" input=\"memory.clk\" output=\"mem_2048x8_dp.clk\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("        </interconnect>\n")
	vpr_file.write("      </mode>\n")
	vpr_file.write("      <mode name=\"mem_8192x4_dp\">\n")
	vpr_file.write("        <pb_type name=\"mem_8192x4_dp\" blif_model=\".subckt dual_port_ram\" class=\"memory\" num_pb=\"1\">\n")
	vpr_file.write("          <input name=\"addr1\" num_pins=\"13\" port_class=\"address1\"/>\n")
	vpr_file.write("          <input name=\"addr2\" num_pins=\"13\" port_class=\"address2\"/>\n")
	vpr_file.write("          <input name=\"data1\" num_pins=\"4\" port_class=\"data_in1\"/>\n")
	vpr_file.write("          <input name=\"data2\" num_pins=\"4\" port_class=\"data_in2\"/>\n")
	vpr_file.write("          <input name=\"we1\" num_pins=\"1\" port_class=\"write_en1\"/>\n")
	vpr_file.write("          <input name=\"we2\" num_pins=\"1\" port_class=\"write_en2\"/>\n")
	vpr_file.write("          <output name=\"out1\" num_pins=\"4\" port_class=\"data_out1\"/>\n")
	vpr_file.write("          <output name=\"out2\" num_pins=\"4\" port_class=\"data_out2\"/>\n")
	vpr_file.write("          <clock name=\"clk\" num_pins=\"1\" port_class=\"clock\"/>\n")
	vpr_file.write("          <T_setup value=\"2.448e-10\" port=\"mem_8192x4_dp.addr1\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_setup value=\"2.448e-10\" port=\"mem_8192x4_dp.data1\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_setup value=\"2.448e-10\" port=\"mem_8192x4_dp.we1\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_setup value=\"2.448e-10\" port=\"mem_8192x4_dp.addr2\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_setup value=\"2.448e-10\" port=\"mem_8192x4_dp.data2\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_setup value=\"2.448e-10\" port=\"mem_8192x4_dp.we2\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_clock_to_Q max=\"1.667e-9\" port=\"mem_8192x4_dp.out1\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_clock_to_Q max=\"1.667e-9\" port=\"mem_8192x4_dp.out2\" clock=\"clk\"/>\n")
	vpr_file.write("        </pb_type>\n")
	vpr_file.write("        <interconnect>\n")
	vpr_file.write("          <direct name=\"address1\" input=\"memory.addr1[12:0]\" output=\"mem_8192x4_dp.addr1\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"address2\" input=\"memory.addr2[12:0]\" output=\"mem_8192x4_dp.addr2\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"data1\" input=\"memory.data[3:0]\" output=\"mem_8192x4_dp.data1\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"data2\" input=\"memory.data[7:4]\" output=\"mem_8192x4_dp.data2\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"writeen1\" input=\"memory.we1\" output=\"mem_8192x4_dp.we1\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"writeen2\" input=\"memory.we2\" output=\"mem_8192x4_dp.we2\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"dataout1\" input=\"mem_8192x4_dp.out1\" output=\"memory.out[3:0]\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"dataout2\" input=\"mem_8192x4_dp.out2\" output=\"memory.out[7:4]\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"clk\" input=\"memory.clk\" output=\"mem_8192x4_dp.clk\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("        </interconnect>\n")
	vpr_file.write("      </mode>\n")
	vpr_file.write("      <mode name=\"mem_16384x2_dp\">\n")
	vpr_file.write("        <pb_type name=\"mem_16384x2_dp\" blif_model=\".subckt dual_port_ram\" class=\"memory\" num_pb=\"1\">\n")
	vpr_file.write("          <input name=\"addr1\" num_pins=\"14\" port_class=\"address1\"/>\n")
	vpr_file.write("          <input name=\"addr2\" num_pins=\"14\" port_class=\"address2\"/>\n")
	vpr_file.write("          <input name=\"data1\" num_pins=\"2\" port_class=\"data_in1\"/>\n")
	vpr_file.write("          <input name=\"data2\" num_pins=\"2\" port_class=\"data_in2\"/>\n")
	vpr_file.write("          <input name=\"we1\" num_pins=\"1\" port_class=\"write_en1\"/>\n")
	vpr_file.write("          <input name=\"we2\" num_pins=\"1\" port_class=\"write_en2\"/>\n")
	vpr_file.write("          <output name=\"out1\" num_pins=\"2\" port_class=\"data_out1\"/>\n")
	vpr_file.write("          <output name=\"out2\" num_pins=\"2\" port_class=\"data_out2\"/>\n")
	vpr_file.write("          <clock name=\"clk\" num_pins=\"1\" port_class=\"clock\"/>\n")
	vpr_file.write("          <T_setup value=\"2.448e-10\" port=\"mem_16384x2_dp.addr1\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_setup value=\"2.448e-10\" port=\"mem_16384x2_dp.data1\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_setup value=\"2.448e-10\" port=\"mem_16384x2_dp.we1\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_setup value=\"2.448e-10\" port=\"mem_16384x2_dp.addr2\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_setup value=\"2.448e-10\" port=\"mem_16384x2_dp.data2\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_setup value=\"2.448e-10\" port=\"mem_16384x2_dp.we2\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_clock_to_Q max=\"1.667e-9\" port=\"mem_16384x2_dp.out1\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_clock_to_Q max=\"1.667e-9\" port=\"mem_16384x2_dp.out2\" clock=\"clk\"/>\n")
	vpr_file.write("        </pb_type>\n")
	vpr_file.write("        <interconnect>\n")
	vpr_file.write("          <direct name=\"address1\" input=\"memory.addr1[13:0]\" output=\"mem_16384x2_dp.addr1\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"address2\" input=\"memory.addr2[13:0]\" output=\"mem_16384x2_dp.addr2\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"data1\" input=\"memory.data[1:0]\" output=\"mem_16384x2_dp.data1\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"data2\" input=\"memory.data[3:2]\" output=\"mem_16384x2_dp.data2\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"writeen1\" input=\"memory.we1\" output=\"mem_16384x2_dp.we1\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"writeen2\" input=\"memory.we2\" output=\"mem_16384x2_dp.we2\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"dataout1\" input=\"mem_16384x2_dp.out1\" output=\"memory.out[1:0]\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"dataout2\" input=\"mem_16384x2_dp.out2\" output=\"memory.out[3:2]\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"clk\" input=\"memory.clk\" output=\"mem_16384x2_dp.clk\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("        </interconnect>\n")
	vpr_file.write("      </mode>\n")
	          
	vpr_file.write("      <mode name=\"mem_32768x1_dp\">\n")
	vpr_file.write("        <pb_type name=\"mem_32768x1_dp\" blif_model=\".subckt dual_port_ram\" class=\"memory\" num_pb=\"1\">\n")
	vpr_file.write("          <input name=\"addr1\" num_pins=\"15\" port_class=\"address1\"/>\n")
	vpr_file.write("          <input name=\"addr2\" num_pins=\"15\" port_class=\"address2\"/>\n")
	vpr_file.write("          <input name=\"data1\" num_pins=\"1\" port_class=\"data_in1\"/>\n")
	vpr_file.write("          <input name=\"data2\" num_pins=\"1\" port_class=\"data_in2\"/>\n")
	vpr_file.write("          <input name=\"we1\" num_pins=\"1\" port_class=\"write_en1\"/>\n")
	vpr_file.write("          <input name=\"we2\" num_pins=\"1\" port_class=\"write_en2\"/>\n")
	vpr_file.write("          <output name=\"out1\" num_pins=\"1\" port_class=\"data_out1\"/>\n")
	vpr_file.write("          <output name=\"out2\" num_pins=\"1\" port_class=\"data_out2\"/>\n")
	vpr_file.write("          <clock name=\"clk\" num_pins=\"1\" port_class=\"clock\"/>\n")
	vpr_file.write("          <T_setup value=\"2.448e-10\" port=\"mem_32768x1_dp.addr1\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_setup value=\"2.448e-10\" port=\"mem_32768x1_dp.data1\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_setup value=\"2.448e-10\" port=\"mem_32768x1_dp.we1\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_setup value=\"2.448e-10\" port=\"mem_32768x1_dp.addr2\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_setup value=\"2.448e-10\" port=\"mem_32768x1_dp.data2\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_setup value=\"2.448e-10\" port=\"mem_32768x1_dp.we2\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_clock_to_Q max=\"1.667e-9\" port=\"mem_32768x1_dp.out1\" clock=\"clk\"/>\n")
	vpr_file.write("          <T_clock_to_Q max=\"1.667e-9\" port=\"mem_32768x1_dp.out2\" clock=\"clk\"/>\n")
	vpr_file.write("        </pb_type>\n")
	vpr_file.write("        <interconnect>\n")
	vpr_file.write("          <direct name=\"address1\" input=\"memory.addr1[14:0]\" output=\"mem_32768x1_dp.addr1\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"address2\" input=\"memory.addr2[14:0]\" output=\"mem_32768x1_dp.addr2\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"data1\" input=\"memory.data[0:0]\" output=\"mem_32768x1_dp.data1\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"data2\" input=\"memory.data[1:1]\" output=\"mem_32768x1_dp.data2\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"writeen1\" input=\"memory.we1\" output=\"mem_32768x1_dp.we1\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"writeen2\" input=\"memory.we2\" output=\"mem_32768x1_dp.we2\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"dataout1\" input=\"mem_32768x1_dp.out1\" output=\"memory.out[0:0]\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"dataout2\" input=\"mem_32768x1_dp.out2\" output=\"memory.out[1:1]\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("          <direct name=\"clk\" input=\"memory.clk\" output=\"mem_32768x1_dp.clk\">\n")
	vpr_file.write("          </direct>\n")
	vpr_file.write("        </interconnect>\n")
	vpr_file.write("      </mode>\n")

	vpr_file.write("    <fc default_in_type=\"frac\" default_in_val=\"0.15\" default_out_type=\"frac\" default_out_val=\"0.10\"/>\n")
	vpr_file.write("    <pinlocations pattern=\"spread\"/>\n")

	vpr_file.write("  </pb_type>\n")


	vpr_file.write("</complexblocklist>\n")
	vpr_file.write("</architecture>\n")


def print_vpr_file(fpga_inst, arch_folder, enable_bram_module):

	vpr_file = open(arch_folder + "/vpr_arch.xml", 'w')

	if enable_bram_module == 1:
		print_vpr_file_memory(vpr_file, fpga_inst)
	else:
		print_vpr_file_flut_hard(vpr_file, fpga_inst)
		
	vpr_file.close()
