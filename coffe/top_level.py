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
    sb_file.write(".TRAN 1p 8n SWEEP DATA=sweep_data\n")
    sb_file.write(".OPTIONS BRIEF=1\n\n")
    sb_file.write("* Input signal\n")
    sb_file.write("VIN n_in gnd PULSE (0 supply_v 0 0 0 2n 8n)\n\n")

    sb_file.write("* Power rail for the circuit under test.\n")
    sb_file.write("* This allows us to measure power of a circuit under test without measuring the power of wave shaping and load circuitry.\n")
    sb_file.write("V_SB_MUX vdd_sb_mux gnd supply_v\n\n")

    
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

    sb_file.write(".MEASURE TRAN meas_logic_low_voltage FIND V(Xrouting_wire_load_2.Xrouting_wire_load_tile_1.Xsb_mux_on_out.n_in) AT=7nn\n\n")

    sb_file.write("* Measure the power required to propagate a rise and a fall transition through the subcircuit at 250MHz.\n")
    sb_file.write(".MEASURE TRAN meas_current INTEGRAL I(V_SB_MUX) FROM=0ns TO=4ns\n")
    sb_file.write(".MEASURE TRAN meas_avg_power PARAM = '-(meas_current/4n)*supply_v'\n\n")

    sb_file.write("********************************************************************************\n")
    sb_file.write("** Circuit\n")
    sb_file.write("********************************************************************************\n\n")
    sb_file.write("Xsb_mux_on_1 n_in n_1_1 vsram vsram_n vdd gnd sb_mux_on\n\n")
    sb_file.write("Xrouting_wire_load_1 n_1_1 n_2_1 n_hang_1 vsram vsram_n vdd gnd vdd_sb_mux vdd routing_wire_load\n\n")
    sb_file.write("Xrouting_wire_load_2 n_2_1 n_3_1 n_hang_2 vsram vsram_n vdd gnd vdd vdd routing_wire_load\n\n")
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
    
    cb_file.write("* Power rail for the circuit under test.\n")
    cb_file.write("* This allows us to measure power of a circuit under test without measuring the power of wave shaping and load circuitry.\n")
    cb_file.write("V_CB_MUX vdd_cb_mux gnd supply_v\n\n")
    
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

    cb_file.write(".MEASURE TRAN meas_logic_low_voltage FIND V(Xlocal_routing_wire_load_1.Xlocal_mux_on_1.n_in) AT=3n\n\n")
    
    cb_file.write("* Measure the power required to propagate a rise and a fall transition through the subcircuit at 250MHz.\n")
    cb_file.write(".MEASURE TRAN meas_current INTEGRAL I(V_CB_MUX) FROM=0ns TO=4ns\n")
    cb_file.write(".MEASURE TRAN meas_avg_power PARAM = '-(meas_current/4n)*supply_v'\n\n")

    cb_file.write("********************************************************************************\n")
    cb_file.write("** Circuit\n")
    cb_file.write("********************************************************************************\n\n")
    cb_file.write("Xsb_mux_on_1 n_in n_1_1 vsram vsram_n vdd gnd sb_mux_on\n")
    cb_file.write("Xrouting_wire_load_1 n_1_1 n_1_2 n_1_3 vsram vsram_n vdd gnd vdd vdd_cb_mux routing_wire_load\n")
    cb_file.write("Xlocal_routing_wire_load_1 n_1_3 n_1_4 vsram vsram_n vdd gnd vdd local_routing_wire_load\n")
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
    
    local_mux_file.write("* Power rail for the circuit under test.\n")
    local_mux_file.write("* This allows us to measure power of a circuit under test without measuring the power of wave shaping and load circuitry.\n")
    local_mux_file.write("V_LOCAL_MUX vdd_local_mux gnd supply_v\n\n")

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

    local_mux_file.write(".MEASURE TRAN meas_logic_low_voltage FIND V(n_1_1) AT=3n\n\n")

    local_mux_file.write("* Measure the power required to propagate a rise and a fall transition through the subcircuit at 250MHz.\n")
    local_mux_file.write(".MEASURE TRAN meas_current INTEGRAL I(V_LOCAL_MUX) FROM=0ns TO=4ns\n")
    local_mux_file.write(".MEASURE TRAN meas_avg_power PARAM = '-(meas_current/4n)*supply_v'\n\n")
    
    local_mux_file.write("********************************************************************************\n")
    local_mux_file.write("** Circuit\n")
    local_mux_file.write("********************************************************************************\n\n")
    local_mux_file.write("Xsb_mux_on_1 n_in n_1_1 vsram vsram_n vdd gnd sb_mux_on\n")
    local_mux_file.write("Xrouting_wire_load_1 n_1_1 n_1_2 n_1_3 vsram vsram_n vdd gnd vdd vdd routing_wire_load\n")
    local_mux_file.write("Xlocal_routing_wire_load_1 n_1_3 n_1_4 vsram vsram_n vdd gnd vdd_local_mux local_routing_wire_load\n")
    local_mux_file.write("Xlut_A_driver_1 n_1_4 n_hang1 vsram vsram_n n_hang2 n_hang3 vdd gnd lut_A_driver\n\n")
    local_mux_file.write(".END")
    local_mux_file.close()

    # Come out of top-level directory
    os.chdir("../")
    
    return (mux_name + "/" + mux_name + ".sp")

# This netlist measures the power consumption of read operation in SRAM-basd memories
def generate_sram_read_power_top(name, sram_per_column, unselected_column_count):

    # Create directories
    if not os.path.exists(name):
        os.makedirs(name)  
    # Change to directory    
    os.chdir(name)   

    # Create and open file
    # The following are important parameter definitions
    # ram_frequency is the operating frequency of the SRAM-based memory
    # precharge_max is the maximum of precharge delay, rowdecoder delay and configurable decoder delay
    # wl_eva is the sum of worldline delay and evaluation time + precharge_max
    # sa_xbar_ff is the sum of sense amp, output crossbar and flip flop delays + wl_eva

    # duplicate the precharge?
    if sram_per_column == 512:
        duplicate = 1
    else:
        duplicate = 0

    # create the file and generate the netlist:

    filename = name + ".sp"
    the_file = open(filename, 'w')
    the_file.write(".TITLE SRAM read power measurement circuit \n\n")
    the_file.write("********************************************************************************\n")
    the_file.write("** Include libraries, parameters and other\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".LIB \"../includes.l\" INCLUDES\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Setup and input\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".TRAN 1p '4 * ram_frequency' SWEEP DATA=sweep_data\n")
    the_file.write(".OPTIONS BRIEF=1\n\n")
    the_file.write("* Input signal\n")
    the_file.write("Vprecharge n_precharge gnd PULSE (supply_v 0 0 50p 50p 'precharge_max' 'ram_frequency')\n")
    the_file.write("Vprecharge2 n_precharge2 gnd PULSE (supply_v 0 0 50p 50p 'precharge_max' 'ram_frequency')\n")
    the_file.write("Vwl n_wl_eva gnd PULSE (supply_v 0 0 50p 50p 'wl_eva' 'ram_frequency')\n")

    the_file.write("* Power rail for the circuit under test.\n")
    the_file.write("* This allows us to measure power of a circuit under test without measuring the power of wave shaping and load circuitry.\n")
    the_file.write("V_selected vdd_selected gnd supply_v\n\n")
    the_file.write("V_unselected vdd_unselected gnd supply_v\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Measurement\n")
    the_file.write("********************************************************************************\n\n")

    the_file.write("* Measure the power required to propagate a rise and a fall transition through the subcircuit at 250MHz.\n")
    the_file.write(".MEASURE TRAN meas_current_selected INTEGRAL I(V_selected) FROM=0ns TO='4 * ram_frequency'\n")
    the_file.write(".MEASURE TRAN meas_avg_power_selected PARAM = '-(meas_current_selected/(4 * ram_frequency)) * supply_v'\n\n")
    the_file.write(".MEASURE TRAN meas_current_unselected INTEGRAL I(V_unselected) FROM=0ns TO='4 * ram_frequency'\n")
    the_file.write(".MEASURE TRAN meas_avg_power_unselected PARAM = '-(meas_current_unselected/(4 * ram_frequency)) * supply_v'\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Circuit\n")
    the_file.write("********************************************************************************\n\n")

    # sense amp
    the_file.write("xsamp1 n_wl_eva tgate_l tgate_r n_hang_samp vdd_selected gnd samp1\n")
    # write driver
    the_file.write("xwrite gnd gnd tgate_l tgate_r vdd_selected gnd writedriver\n")
    # column selectors
    the_file.write("xtgate1 n_bl_0 tgate_l vdd gnd vdd_selected gnd RAM_tgate\n")
    the_file.write("xtgater n_br_0 tgate_r vdd gnd vdd_selected gnd RAM_tgate\n")
    the_file.write("xprecharge n_precharge n_bl_0 n_br_0 vdd_selected gnd precharge\n")
    if duplicate == 1:
        the_file.write("xprecharge_dup n_precharge n_bl_512 n_br_512 vdd_selected gnd precharge\n")

    #unselected columns
    for i in range(0, unselected_column_count):
        the_file.write("xtgatel_"+str(i)+" n_bl"+str(i)+"_0 tgate_l gnd vdd vdd_unselected gnd RAM_tgate\n")
        the_file.write("xtgater_"+str(i)+" n_br"+str(i)+"_0 tgate_r gnd vdd vdd_unselected gnd RAM_tgate\n")
        the_file.write("xprecharge"+str(i)+" n_precharge n_bl"+str(i)+"_0 n_br"+str(i)+"_0 vdd_unselected gnd precharge\n")
        if duplicate == 1:
            the_file.write("xprecharge"+str(i)+"_dup n_precharge n_bl"+str(i)+"_512 n_br"+str(i)+"_512 vdd_unselected gnd precharge\n")    
    # SRAM cells
    # selected column:
    for i in range(0, sram_per_column - 1):
        the_file.write("Xwirel"+str(i)+" n_bl_"+str(i)+" n_bl_"+str(i+1)+" wire Rw=wire_memorycell_vertical_res/"+str(sram_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(sram_per_column)+"\n")
        the_file.write("Xwirer"+str(i)+" n_br_"+str(i)+" n_br_"+str(i+1)+" wire Rw=wire_memorycell_vertical_res/"+str(sram_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(sram_per_column)+"\n")
        the_file.write("Xsram"+str(i)+" gnd gnd n_bl_"+str(i + 1)+" gnd n_br_"+str(i + 1)+" gnd vdd_selected gnd memorycell\n")
    the_file.write("Xwirel"+str(sram_per_column - 1)+" n_bl_"+str(sram_per_column -1)+" n_bl_"+str(sram_per_column)+" wire Rw=wire_memorycell_vertical_res/"+str(sram_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(sram_per_column)+"\n")
    the_file.write("Xwirer"+str(sram_per_column - 1)+" n_br_"+str(sram_per_column -1)+" n_br_"+str(sram_per_column)+" wire Rw=wire_memorycell_vertical_res/"+str(sram_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(sram_per_column)+"\n")
    the_file.write("Xsram"+str(sram_per_column - 1)+" n_precharge2 gnd n_bl_"+str(sram_per_column)+" gnd n_br_"+str(sram_per_column)+" gnd vdd_selected gnd memorycell\n")
    # unselected column:
    for j in range(0, unselected_column_count):
        for i in range(0, sram_per_column - 1):
            the_file.write("Xwire"+str(j)+"l"+str(i)+" n_bl"+str(j)+"_"+str(i)+" n_bl"+str(j)+"_"+str(i+1)+" wire Rw=wire_memorycell_vertical_res/"+str(sram_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(sram_per_column)+"\n")
            the_file.write("Xwire"+str(j)+"r"+str(i)+" n_br"+str(j)+"_"+str(i)+" n_br"+str(j)+"_"+str(i+1)+" wire Rw=wire_memorycell_vertical_res/"+str(sram_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(sram_per_column)+"\n")
            the_file.write("Xsram_"+str(j)+"_"+str(i)+" gnd gnd n_bl"+str(j)+"_"+str(i + 1)+" gnd n_br"+str(j)+"_"+str(i + 1)+" gnd vdd_unselected gnd memorycell\n")
        the_file.write("Xwire"+str(j)+"l"+str(sram_per_column - 1)+" n_bl"+str(j)+"_"+str(sram_per_column - 1)+" n_bl"+str(j)+"_"+str(sram_per_column)+" wire Rw=wire_memorycell_vertical_res/"+str(sram_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(sram_per_column)+"\n")
        the_file.write("Xwire"+str(j)+"r"+str(sram_per_column - 1)+" n_br"+str(j)+"_"+str(sram_per_column - 1)+" n_br"+str(j)+"_"+str(sram_per_column)+" wire Rw=wire_memorycell_vertical_res/"+str(sram_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(sram_per_column)+"\n")
        the_file.write("Xsram_"+str(j)+"_"+str(sram_per_column - 1)+" n_precharge2 gnd n_bl"+str(j)+"_"+str(sram_per_column)+" gnd n_br"+str(j)+"_"+str(sram_per_column)+" gnd vdd_unselected gnd memorycell\n")
    # initial conditions:
    # one of the bitline is set to vdd, the other set to 0:
    the_file.write(".IC V(n_bl_0) = 'supply_v' \n")
    the_file.write(".IC V(n_br_0) = 0 \n")

    for i in range(0, sram_per_column):
        the_file.write(".IC V(Xsram"+str(i)+".n_1_1) = 'supply_v' \n")
        the_file.write(".IC V(Xsram"+str(i)+".n_1_2) = 0 \n")
    for i in range(0, sram_per_column):
        for j in range(0, unselected_column_count):
            the_file.write(".IC V(n_bl"+str(j)+"_"+str(i)+") = 'supply_v' \n")
            the_file.write(".IC V(n_br"+str(j)+"_"+str(i)+") = 0 \n")
            the_file.write(".IC V(Xsram_"+str(j)+"_"+str(i)+".n_1_1) = 'supply_v' \n")
            the_file.write(".IC V(Xsram_"+str(j)+"_"+str(i)+".n_1_2) = 0 \n")

    #the_file.write(".print tran V(n_bl_0) V(n_bl_"+str(sram_per_column)+") V(n_br_0) V(Xprechargesa.n_1_2) V(n_br_"+str(sram_per_column)+") V(n_bl"+str(0)+"_"+str(sram_per_column)+") V(n_br"+str(0)+"_"+str(sram_per_column)+") V(Xsram"+str(sram_per_column - 1)+".n_1_2) V(Xsram"+str(sram_per_column - 1)+".n_1_1) V(n_precharge) V(n_wl_eva) I(V_unselected) I(V_selected)\n")   
    the_file.write(".END")
    the_file.close()

    # Come out of top-level directory
    os.chdir("../")

    return (name + "/" + name + ".sp")




# This netlist measures the power consumption of write operation in SRAM-basd memories
def generate_sram_writelh_power_top_lp(name, sram_per_column, unselected_column_count):

    # Create directories
    if not os.path.exists(name):
        os.makedirs(name)  
    # Change to directory    
    os.chdir(name)   

    # Create and open file
    # The following are important parameter definitions
    # ram_frequency is the operating frequency of the SRAM-based memory
    # precharge_max is the maximum of precharge delay, rowdecoder delay and configurable decoder delay
    # wl_eva is the sum of worldline delay and evaluation time + precharge_max
    # sa_xbar_ff is the sum of sense amp, output crossbar and flip flop delays + wl_eva

    # duplicate the precharge?
    if sram_per_column == 512:
        duplicate = 1
    else:
        duplicate = 0

    filename = name + ".sp"
    the_file = open(filename, 'w')
    the_file.write(".TITLE SRAM write power measurement circuit \n\n")
    the_file.write("********************************************************************************\n")
    the_file.write("** Include libraries, parameters and other\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".LIB \"../includes.l\" INCLUDES\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Setup and input\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".TRAN 1p '4 * ram_frequency' SWEEP DATA=sweep_data\n")
    the_file.write(".OPTIONS BRIEF=1\n\n")
    the_file.write("* Input signal\n")
    the_file.write("Vprecharge n_precharge gnd PULSE (supply_v_lp 0 0 50p 50p 'precharge_max' 'ram_frequency')\n")
    the_file.write("Vdatain n_data_in gnd PULSE (supply_v_lp 0 0 0 0 'ram_frequency' ' 2 * ram_frequency')\n")

    the_file.write("* Power rail for the circuit under test.\n")
    the_file.write("* This allows us to measure power of a circuit under test without measuring the power of wave shaping and load circuitry.\n")
    the_file.write("V_selected vdd_selected gnd supply_v_lp\n\n")
    the_file.write("V_unselected vdd_unselected gnd supply_v_lp\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Measurement\n")
    the_file.write("********************************************************************************\n\n")

    the_file.write("* Measure the power required to propagate a rise and a fall transition through the subcircuit at 250MHz.\n")
    the_file.write(".MEASURE TRAN meas_current_selected INTEGRAL I(V_selected) FROM= 0ns TO='4 * ram_frequency'\n")
    the_file.write(".MEASURE TRAN meas_avg_power_selected PARAM = '-(meas_current_selected/(4 * ram_frequency)) * supply_v_lp'\n\n")
    the_file.write(".MEASURE TRAN meas_current_unselected INTEGRAL I(V_unselected) FROM= 0ns TO='4 * ram_frequency'\n")
    the_file.write(".MEASURE TRAN meas_avg_power_unselected PARAM = '-(meas_current_unselected/(4 * ram_frequency)) * supply_v_lp'\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Circuit\n")
    the_file.write("********************************************************************************\n\n")

    # sense amp
    the_file.write("xsamp1 vdd_lp tgate_l tgate_r n_hang_samp vdd_selected gnd samp1\n")
    # write driver
    the_file.write("xwrite n_precharge n_data_in tgate_l tgate_r vdd_selected gnd writedriver\n")
    # column selectors
    the_file.write("xtgate1 n_bl_0 tgate_l vdd_lp gnd vdd_selected gnd RAM_tgate\n")
    the_file.write("xtgater n_br_0 tgate_r vdd_lp gnd vdd_selected gnd RAM_tgate\n")
    the_file.write("xprecharge n_precharge n_bl_0 n_br_0 vdd_selected gnd precharge\n")
    if duplicate == 1:
        the_file.write("xprecharge_dup n_precharge n_bl_512 n_br_512 vdd_selected gnd precharge\n")

    #unselected columns
    for i in range(0, unselected_column_count):
        the_file.write("xtgatel_"+str(i)+" n_bl"+str(i)+"_0 tgate_l gnd vdd_lp vdd_unselected gnd RAM_tgate\n")
        the_file.write("xtgater_"+str(i)+" n_br"+str(i)+"_0 tgate_r gnd vdd_lp vdd_unselected gnd RAM_tgate\n")
        the_file.write("xprecharge"+str(i)+" n_precharge n_bl"+str(i)+"_0 n_br"+str(i)+"_0 vdd_unselected gnd precharge\n")
        if duplicate == 1:
            the_file.write("xprecharge"+str(i)+"_dup n_precharge n_bl"+str(i)+"_512 n_br"+str(i)+"_512 vdd_unselected gnd precharge\n")    
    # SRAM cells
    # selected column:
    for i in range(0, sram_per_column - 1):
        the_file.write("Xwirel"+str(i)+" n_bl_"+str(i)+" n_bl_"+str(i+1)+" wire Rw=wire_memorycell_vertical_res/"+str(sram_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(sram_per_column)+"\n")
        the_file.write("Xwirer"+str(i)+" n_br_"+str(i)+" n_br_"+str(i+1)+" wire Rw=wire_memorycell_vertical_res/"+str(sram_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(sram_per_column)+"\n")
        the_file.write("Xsram"+str(i)+" gnd gnd n_bl_"+str(i + 1)+" gnd n_br_"+str(i + 1)+" gnd vdd_selected gnd memorycell\n")
    the_file.write("Xwirel"+str(sram_per_column - 1)+" n_bl_"+str(sram_per_column -1)+" n_bl_"+str(sram_per_column)+" wire Rw=wire_memorycell_vertical_res/"+str(sram_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(sram_per_column)+"\n")
    the_file.write("Xwirer"+str(sram_per_column - 1)+" n_br_"+str(sram_per_column -1)+" n_br_"+str(sram_per_column)+" wire Rw=wire_memorycell_vertical_res/"+str(sram_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(sram_per_column)+"\n")
    the_file.write("Xsram"+str(sram_per_column - 1)+" n_precharge gnd n_bl_"+str(sram_per_column)+" gnd n_br_"+str(sram_per_column)+" gnd vdd_selected gnd memorycell\n")
    # unselected column:
    for j in range(0, unselected_column_count):
        for i in range(0, sram_per_column - 1):
            the_file.write("Xwire"+str(j)+"l"+str(i)+" n_bl"+str(j)+"_"+str(i)+" n_bl"+str(j)+"_"+str(i+1)+" wire Rw=wire_memorycell_vertical_res/"+str(sram_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(sram_per_column)+"\n")
            the_file.write("Xwire"+str(j)+"r"+str(i)+" n_br"+str(j)+"_"+str(i)+" n_br"+str(j)+"_"+str(i+1)+" wire Rw=wire_memorycell_vertical_res/"+str(sram_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(sram_per_column)+"\n")
            the_file.write("Xsram_"+str(j)+"_"+str(i)+" gnd gnd n_bl"+str(j)+"_"+str(i + 1)+" gnd n_br"+str(j)+"_"+str(i + 1)+" gnd vdd_unselected gnd memorycell\n")
        the_file.write("Xwire"+str(j)+"l"+str(sram_per_column - 1)+" n_bl"+str(j)+"_"+str(sram_per_column - 1)+" n_bl"+str(j)+"_"+str(sram_per_column)+" wire Rw=wire_memorycell_vertical_res/"+str(sram_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(sram_per_column)+"\n")
        the_file.write("Xwire"+str(j)+"r"+str(sram_per_column - 1)+" n_br"+str(j)+"_"+str(sram_per_column - 1)+" n_br"+str(j)+"_"+str(sram_per_column)+" wire Rw=wire_memorycell_vertical_res/"+str(sram_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(sram_per_column)+"\n")
        the_file.write("Xsram_"+str(j)+"_"+str(sram_per_column - 1)+" n_precharge gnd n_bl"+str(j)+"_"+str(sram_per_column)+" gnd n_br"+str(j)+"_"+str(sram_per_column)+" gnd vdd_unselected gnd memorycell\n")
    # initial conditions:
    # one of the bitline is set to vdd, the other set to 0:
    the_file.write(".IC V(n_bl_0) = 'supply_v_lp' \n")
    the_file.write(".IC V(n_br_0) = 0 \n")

    for i in range(0, sram_per_column):
        the_file.write(".IC V(Xsram"+str(i)+".n_1_1) = 'supply_v_lp' \n")
        the_file.write(".IC V(Xsram"+str(i)+".n_1_2) = 0 \n")
    for i in range(0, sram_per_column):
        for j in range(0, unselected_column_count):
            the_file.write(".IC V(n_bl"+str(j)+"_"+str(i)+") = 'supply_v_lp' \n")
            the_file.write(".IC V(n_br"+str(j)+"_"+str(i)+") = 0 \n")
            the_file.write(".IC V(Xsram_"+str(j)+"_"+str(i)+".n_1_1) = 'supply_v_lp' \n")
            the_file.write(".IC V(Xsram_"+str(j)+"_"+str(i)+".n_1_2) = 0 \n")

    the_file.write(".print tran V(tgate_l) V(tgate_r) V(n_bl_0) V(n_bl_"+str(sram_per_column)+") V(n_br_0) V(Xprechargesa.n_1_2) V(n_br_"+str(sram_per_column)+") V(n_bl"+str(0)+"_"+str(sram_per_column)+") V(n_br"+str(0)+"_"+str(sram_per_column)+") V(Xsram"+str(sram_per_column - 1)+".n_1_2) V(Xsram"+str(sram_per_column - 1)+".n_1_1) V(n_precharge) V(n_wl_eva) I(V_unselected) I(V_selected)\n")   
    the_file.write(".END")
    the_file.close()

    # Come out of top-level directory
    os.chdir("../")

    return (name + "/" + name + ".sp")


# This netlist measures the power consumption of write operation in MTJ-basd memories:
def generate_mtj_read_power_top_lp(name, mtj_per_column):

    # Create directories
    if not os.path.exists(name):
        os.makedirs(name)  
    # Change to directory    
    os.chdir(name)   

    # Create and open file
    # The following are important parameter definitions
    # ram_frequency is the operating frequency of the MTJ-based memory
    # precharge_max is the maximum of bitline discharge delay, rowdecoder delay and configurable decoder delay
    # sa_se1 is the signal that control the first sense enable signal in MTJ-based sense amp
    # sa_se2 is the signal that control the second sense enable signal in MTJ-based sense amp

    # duplicate the precharge?
    if mtj_per_column == 512:
        duplicate = 1
    else:
        duplicate = 0

    # create the file and generate the netlist

    filename = name + ".sp"
    the_file = open(filename, 'w')
    the_file.write(".TITLE MTJ write power measurement circuit \n\n")
    the_file.write("********************************************************************************\n")
    the_file.write("** Include libraries, parameters and other\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".LIB \"../includes.l\" INCLUDES\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Setup and input\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".TRAN 1p '4 * ram_frequency' SWEEP DATA=sweep_data\n")
    the_file.write(".OPTIONS BRIEF=1\n\n")
    the_file.write("* Input signal\n")
    the_file.write("Vprecharge n_precharge gnd PULSE (supply_v_lp 0 0 50p 50p 'precharge_max' 'ram_frequency')\n")
    the_file.write("Vprechargeb n_precharge_b gnd PULSE (0 supply_v_lp 0 50p 50p 'precharge_max' 'ram_frequency')\n")
    the_file.write("Vse1 n_se1 gnd PULSE (supply_v_lp 0 0 50p 50p 'sa_se1' 'ram_frequency')\n")
    the_file.write("Vse2 n_se2 gnd PULSE (supply_v_lp 0 0 50p 50p 'sa_se2' 'ram_frequency')\n")

    the_file.write("* Power rail for the circuit under test.\n")
    the_file.write("* This allows us to measure powersna of a circuit under test without measuring the power of wave shaping and load circuitry.\n")
    the_file.write("V_readl vdd_readl gnd supply_v_lp\n\n")
    the_file.write("V_readh vdd_readh gnd supply_v_lp\n\n")


    the_file.write("********************************************************************************\n")
    the_file.write("** Measurement\n")
    the_file.write("********************************************************************************\n\n")

    the_file.write("* Measure the power required to propagate a rise and a fall transition through the subcircuit at 250MHz.\n")

    the_file.write(".MEASURE TRAN meas_current_readl INTEGRAL I(V_readl) FROM= 0ns TO='4 * ram_frequency'\n")
    the_file.write(".MEASURE TRAN meas_avg_power_readl PARAM = '-(meas_current_readl/(4 * ram_frequency)) * supply_v_lp'\n\n")

    the_file.write(".MEASURE TRAN meas_current_readh INTEGRAL I(V_readh) FROM= 0ns TO='4 * ram_frequency'\n")
    the_file.write(".MEASURE TRAN meas_avg_power_readh PARAM = '-(meas_current_readh/(4 * ram_frequency)) * supply_v_lp'\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Circuit\n")
    the_file.write("********************************************************************************\n\n")

    # Low state cell:
    # MTJ sense amp and precharge
    the_file.write("Xprechargesa n_1_1 n_2_1 n_se1 n_se2 n_hang_out vclmpmtj vrefmtj gnd vdd_lp vdd_readl gnd mtj_subcircuits_sa\n")
    # MTJ write driver
    the_file.write("Xwritedriver gnd gnd n_1_1 gnd vdd_readl gnd mtj_subcircuits_writedriver\n")
    the_file.write("Xwritedriver_ref gnd gnd n_2_1 gnd vdd_readl gnd mtj_subcircuits_writedriver\n")
    # MTJ CS
    the_file.write("Xcs n_1_1 n_bl_0 n_precharge_b n_precharge vdd_readl gnd mtj_subcircuits_cs\n")
    the_file.write("Xcs_ref n_2_1 n_bl2_0 n_precharge_b n_precharge vdd_readl gnd mtj_subcircuits_cs\n")
    if duplicate == 1:
        the_file.write("xprecharge_dup n_hang_low n_bl_512 n_precharge_b n_precharge vdd_readl gnd mtj_subcircuits_cs\n")
        the_file.write("xprecharge_dup_ref n_hang2_low n_bl2_512 n_precharge_b n_precharge vdd_readl gnd mtj_subcircuits_cs\n")  

    # MTJ cells
    # Selected column:
    for i in range(0, mtj_per_column - 1):
        the_file.write("Xwirel"+str(i)+" n_bl_"+str(i)+" n_bl_"+str(i+1)+" wire Rw=wire_memorycell_vertical_res/"+str(mtj_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(mtj_per_column)+"\n")
        the_file.write("Xwirer"+str(i)+" n_br_"+str(i)+" n_br_"+str(i+1)+" wire Rw=wire_memorycell_vertical_res/"+str(mtj_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(mtj_per_column)+"\n")
        the_file.write("Xmtj"+str(i)+" gnd gnd n_bl_"+str(i + 1)+" gnd n_br_"+str(i + 1)+" gnd vdd_readl gnd memorycell\n")
    the_file.write("Xwirel"+str(mtj_per_column - 1)+" n_bl_"+str(mtj_per_column -1)+" n_bl_"+str(mtj_per_column)+" wire Rw=wire_memorycell_vertical_res/"+str(mtj_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(mtj_per_column)+"\n")
    the_file.write("Xwirer"+str(mtj_per_column - 1)+" n_br_"+str(mtj_per_column -1)+" n_br_"+str(mtj_per_column)+" wire Rw=wire_memorycell_vertical_res/"+str(mtj_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(mtj_per_column)+"\n")
    the_file.write("Xmtj"+str(mtj_per_column - 1)+" n_precharge gnd n_bl_"+str(mtj_per_column)+" gnd n_br_"+str(mtj_per_column)+" gnd vdd_readl gnd memorycell\n")
    
    # Reference bank:
    for i in range(1, mtj_per_column):
        the_file.write("Xwirel"+str(i)+"_ref n_bl2_"+str(i)+" n_bl2_"+str(i+1)+" wire Rw=wire_memorycell_vertical_res/"+str(mtj_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(mtj_per_column)+"\n")
        the_file.write("Xwirer"+str(i)+"_ref n_br2_"+str(i)+" n_br2_"+str(i+1)+" wire Rw=wire_memorycell_vertical_res/"+str(mtj_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(mtj_per_column)+"\n")
        the_file.write("Xmtj"+str(i)+"_ref gnd gnd n_bl2_"+str(i + 1)+" gnd n_br2_"+str(i + 1)+" gnd vdd_readl gnd memorycell\n")
    the_file.write("Xwirel"+str(0)+"_ref n_bl2_"+str(0)+" n_bl2_"+str(1)+" wire Rw=wire_memorycell_vertical_res/"+str(mtj_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(mtj_per_column)+"\n")
    the_file.write("Xwirer"+str(0)+"_ref n_br2_"+str(0)+" n_br2_"+str(1)+" wire Rw=wire_memorycell_vertical_res/"+str(mtj_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(mtj_per_column)+"\n")
    the_file.write("Xmtj"+str(0)+"_ref n_precharge gnd n_bl2_"+str(1)+" gnd n_br2_"+str(1)+" gnd vdd_readl gnd memorycell\n")

    # Initial conditions:
    the_file.write(".IC V(n_bl_0) = 0 \n")
    the_file.write(".IC V(n_br_0) = 0 \n")

    the_file.write(".IC V(Xprechargesa.n_1_5) = 0 \n")
    the_file.write(".IC V(Xprechargesa.n_1_6) = 0 \n")
    the_file.write(".IC V(Xprechargesa.n_1_1) = 0.95 \n")
    the_file.write(".IC V(Xprechargesa.n_1_2) = 0.95 \n")
    
    # High state cell:
    # MTJ sense amp and precharge
    the_file.write("X2prechargesa n2_1_1 n2_2_1 n_se1 n_se2 n2_hang_out vclmpmtj vrefmtj gnd vdd_lp vdd_readh gnd mtj_subcircuits_sa\n")
    # MTJ write driver
    the_file.write("X2writedriver gnd gnd n2_1_1 gnd vdd_lp gnd mtj_subcircuits_writedriver\n")
    the_file.write("X2writedriver_ref gnd gnd n2_2_1 gnd vdd_lp gnd mtj_subcircuits_writedriver\n")
    # MTJ CS
    the_file.write("X2cs n2_1_1 n2_bl_0 n_precharge_b n_precharge vdd_lp gnd mtj_subcircuits_cs\n")
    the_file.write("X2cs_ref n2_2_1 n2_bl2_0 n_precharge_b n_precharge vdd_lp gnd mtj_subcircuits_cs\n")
    if duplicate == 1:
        the_file.write("x2precharge_dup n2_hang_low n2_bl_512 n_precharge_b n_precharge vdd_lp gnd mtj_subcircuits_cs\n")
        the_file.write("x2precharge_dup_ref n2_hang2_low n2_bl2_512 n_precharge_b n_precharge vdd_lp gnd mtj_subcircuits_cs\n")  

    # MTJ cells
    # Selected column:
    for i in range(0, mtj_per_column - 1):
        the_file.write("X2wirel"+str(i)+" n2_bl_"+str(i)+" n2_bl_"+str(i+1)+" wire Rw=wire_memorycell_vertical_res/"+str(mtj_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(mtj_per_column)+"\n")
        the_file.write("X2wirer"+str(i)+" n2_br_"+str(i)+" n2_br_"+str(i+1)+" wire Rw=wire_memorycell_vertical_res/"+str(mtj_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(mtj_per_column)+"\n")
        the_file.write("X2mtj"+str(i)+" gnd gnd n2_bl_"+str(i + 1)+" gnd n2_br_"+str(i + 1)+" gnd vdd_readh gnd memorycellh\n")
    the_file.write("X2wirel"+str(mtj_per_column - 1)+" n2_bl_"+str(mtj_per_column -1)+" n2_bl_"+str(mtj_per_column)+" wire Rw=wire_memorycell_vertical_res/"+str(mtj_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(mtj_per_column)+"\n")
    the_file.write("X2wirer"+str(mtj_per_column - 1)+" n2_br_"+str(mtj_per_column -1)+" n2_br_"+str(mtj_per_column)+" wire Rw=wire_memorycell_vertical_res/"+str(mtj_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(mtj_per_column)+"\n")
    the_file.write("X2mtj"+str(mtj_per_column - 1)+" n_precharge gnd n2_bl_"+str(mtj_per_column)+" gnd n2_br_"+str(mtj_per_column)+" gnd vdd_readh gnd memorycellh\n")
    
    # Reference bank:
    for i in range(1, mtj_per_column):
        the_file.write("X2wirel"+str(i)+"_ref n2_bl2_"+str(i)+" n2_bl2_"+str(i+1)+" wire Rw=wire_memorycell_vertical_res/"+str(mtj_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(mtj_per_column)+"\n")
        the_file.write("X2wirer"+str(i)+"_ref n2_br2_"+str(i)+" n2_br2_"+str(i+1)+" wire Rw=wire_memorycell_vertical_res/"+str(mtj_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(mtj_per_column)+"\n")
        the_file.write("X2mtj"+str(i)+"_ref gnd gnd n2_bl2_"+str(i + 1)+" gnd n2_br2_"+str(i + 1)+" gnd vdd_readh gnd memorycellh\n")
    the_file.write("X2wirel"+str(0)+"_ref n2_bl2_"+str(0)+" n2_bl2_"+str(1)+" wire Rw=wire_memorycell_vertical_res/"+str(mtj_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(mtj_per_column)+"\n")
    the_file.write("X2wirer"+str(0)+"_ref n2_br2_"+str(0)+" n2_br2_"+str(1)+" wire Rw=wire_memorycell_vertical_res/"+str(mtj_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(mtj_per_column)+"\n")
    the_file.write("X2mtj"+str(0)+"_ref n_precharge gnd n2_bl2_"+str(1)+" gnd n2_br2_"+str(1)+" gnd vdd_readh gnd memorycell\n")

    # Initial conditions:
    the_file.write(".IC V(n2_bl_0) = 0 \n")
    the_file.write(".IC V(n2_br_0) = 0 \n")

    the_file.write(".IC V(X2prechargesa.n_1_5) = 0 \n")
    the_file.write(".IC V(X2prechargesa.n_1_6) = 0 \n")
    the_file.write(".IC V(X2prechargesa.n_1_1) = 0.95 \n")
    the_file.write(".IC V(X2prechargesa.n_1_2) = 0.95 \n")

    the_file.write(".END")
    the_file.close()

    # Come out of top-level directory
    os.chdir("../")

    return (name + "/" + name + ".sp")



# This netlist measures the power consumption of write operation in MTJ-basd memories
def generate_mtj_write_power_top_lp(name, mtj_per_column):

    # Create directories
    if not os.path.exists(name):
        os.makedirs(name)  
    # Change to directory    
    os.chdir(name)   

    # Create and open file
    # The following are important parameter definitions
    # ram_frequency is the operating frequency of the MTJ-based memory
    # precharge_max is the maximum of bitline discharge delay, rowdecoder delay and configurable decoder delay

    # duplicate the precharge?
    if mtj_per_column == 512:
        duplicate = 1
    else:
        duplicate = 0


    # create the file and generate the netlist

    filename = name + ".sp"
    the_file = open(filename, 'w')
    the_file.write(".TITLE MTJ write power measurement circuit \n\n")
    the_file.write("********************************************************************************\n")
    the_file.write("** Include libraries, parameters and other\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".LIB \"../includes.l\" INCLUDES\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Setup and input\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".TRAN 1p '4 * ram_frequency' SWEEP DATA=sweep_data\n")
    the_file.write(".OPTIONS BRIEF=1\n\n")
    the_file.write("* Input signal\n")
    the_file.write("Vprecharge n_precharge gnd PULSE (supply_v_lp 0 0 50p 50p 'precharge_max' 'ram_frequency')\n")
    the_file.write("Vprechargeb n_precharge_b gnd PULSE (0 supply_v_lp 0 50p 50p 'precharge_max' 'ram_frequency')\n")
    the_file.write("Vdatain n_data_in gnd PULSE (supply_v_lp 0 0 0 0 'ram_frequency' ' 2 * ram_frequency')\n")

    the_file.write("* Power rail for the circuit under test.\n")
    the_file.write("* This allows us to measure powersna of a circuit under test without measuring the power of wave shaping and load circuitry.\n")
    the_file.write("V_selected vdd_selected gnd supply_v_lp\n\n")
    the_file.write("V_selectedh vdd_selectedh gnd supply_v_lp\n\n")
    the_file.write("V_negl vnegl gnd -0.27\n\n")
    the_file.write("V_negh vnegh gnd -0.27\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Measurement\n")
    the_file.write("********************************************************************************\n\n")

    the_file.write("* Measure the power required to propagate a rise and a fall transition through the subcircuit at 250MHz.\n")

    the_file.write(".MEASURE TRAN meas_current_selected INTEGRAL I(V_selected) FROM= 0ns TO='4 * ram_frequency'\n")
    the_file.write(".MEASURE TRAN meas_avg_power_selected PARAM = '-(meas_current_selected/(4 * ram_frequency)) * supply_v_lp'\n\n")

    the_file.write(".MEASURE TRAN meas_current_selectedn INTEGRAL I(V_negl) FROM= 0ns TO='4 * ram_frequency'\n")
    the_file.write(".MEASURE TRAN meas_avg_power_selectedn PARAM = '-(meas_current_selectedn/(4 * ram_frequency)) * 0.27'\n\n")

    the_file.write(".MEASURE TRAN meas_current_selectedh INTEGRAL I(V_selectedh) FROM= 0ns TO='4 * ram_frequency'\n")
    the_file.write(".MEASURE TRAN meas_avg_power_selectedh PARAM = '-(meas_current_selectedh/(4 * ram_frequency)) * supply_v_lp'\n\n")

    the_file.write(".MEASURE TRAN meas_current_selectedhn INTEGRAL I(V_negh) FROM= 0ns TO='4 * ram_frequency'\n")
    the_file.write(".MEASURE TRAN meas_avg_power_selectedhn PARAM = '-(meas_current_selectedhn/(4 * ram_frequency)) * 0.27'\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Circuit\n")
    the_file.write("********************************************************************************\n\n")

    # Low state cell:
    # MTJ sense amp and precharge
    the_file.write("Xprechargesa n_1_1 n_hang_1 gnd gnd n_hang_out vclmpmtj vrefmtj gnd gnd vdd_lp gnd mtj_subcircuits_sa\n")
    # MTJ write driver
    the_file.write("Xwritedriver n_data_in vdd_lp n_1_1 vnegl vdd_selected gnd mtj_subcircuits_writedriver\n")
    # MTJ CS
    the_file.write("Xcs n_1_1 n_bl_0 n_precharge_b n_precharge vdd_lp gnd mtj_subcircuits_cs\n")
    if duplicate == 1:
        the_file.write("xprecharge_dup n_hang_low n_bl_512 n_precharge_b n_precharge vdd_lp gnd mtj_subcircuits_cs\n") 

    # MTJ cells
    # Selected column:
    for i in range(0, mtj_per_column - 1):
        the_file.write("Xwirel"+str(i)+" n_bl_"+str(i)+" n_bl_"+str(i+1)+" wire Rw=wire_memorycell_vertical_res/"+str(mtj_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(mtj_per_column)+"\n")
        the_file.write("Xwirer"+str(i)+" n_br_"+str(i)+" n_br_"+str(i+1)+" wire Rw=wire_memorycell_vertical_res/"+str(mtj_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(mtj_per_column)+"\n")
        the_file.write("Xmtj"+str(i)+" gnd gnd n_bl_"+str(i + 1)+" gnd n_br_"+str(i + 1)+" gnd vdd_selected gnd memorycell\n")
    the_file.write("Xwirel"+str(mtj_per_column - 1)+" n_bl_"+str(mtj_per_column -1)+" n_bl_"+str(mtj_per_column)+" wire Rw=wire_memorycell_vertical_res/"+str(mtj_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(mtj_per_column)+"\n")
    the_file.write("Xwirer"+str(mtj_per_column - 1)+" n_br_"+str(mtj_per_column -1)+" n_br_"+str(mtj_per_column)+" wire Rw=wire_memorycell_vertical_res/"+str(mtj_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(mtj_per_column)+"\n")
    the_file.write("Xmtj"+str(mtj_per_column - 1)+" n_precharge gnd n_bl_"+str(mtj_per_column)+" gnd n_br_"+str(mtj_per_column)+" gnd vdd_selected gnd memorycell\n")
    
    # Initial conditions:
    the_file.write(".IC V(n_bl_0) = 0.8 \n")
    the_file.write(".IC V(n_br_0) = 0 \n")

    # High state cell:
    # MTJ sense amp and precharge
    the_file.write("X2prechargesa n2_1_1 n2_hang_1 gnd gnd n2_hang_out vclmpmtj vrefmtj gnd gnd vdd_lp gnd mtj_subcircuits_sa\n")
    # MTJ write driver
    the_file.write("X2writedriver n2_data_in vdd_lp n2_1_1 vnegh vdd_selectedh gnd mtj_subcircuits_writedriver\n")
    # MTJ CS
    the_file.write("X2cs n2_1_1 n2_bl_0 n2_precharge_b n2_precharge vdd_lp gnd mtj_subcircuits_cs\n")
    if duplicate == 1:
        the_file.write("x2precharge_dup n2_hang_low n2_bl_512 n2_precharge_b n2_precharge vdd_lp gnd mtj_subcircuits_cs\n") 

    # MTJ cells
    # Selected column:
    for i in range(0, mtj_per_column - 1):
        the_file.write("X2wirel"+str(i)+" n2_bl_"+str(i)+" n2_bl_"+str(i+1)+" wire Rw=wire_memorycell_vertical_res/"+str(mtj_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(mtj_per_column)+"\n")
        the_file.write("X2wirer"+str(i)+" n2_br_"+str(i)+" n2_br_"+str(i+1)+" wire Rw=wire_memorycell_vertical_res/"+str(mtj_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(mtj_per_column)+"\n")
        the_file.write("X2mtj"+str(i)+" gnd gnd n2_bl_"+str(i + 1)+" gnd n2_br_"+str(i + 1)+" gnd vdd_selectedh gnd memorycellh\n")
    the_file.write("X2wirel"+str(mtj_per_column - 1)+" n2_bl_"+str(mtj_per_column -1)+" n2_bl_"+str(mtj_per_column)+" wire Rw=wire_memorycell_vertical_res/"+str(mtj_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(mtj_per_column)+"\n")
    the_file.write("X2wirer"+str(mtj_per_column - 1)+" n2_br_"+str(mtj_per_column -1)+" n2_br_"+str(mtj_per_column)+" wire Rw=wire_memorycell_vertical_res/"+str(mtj_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(mtj_per_column)+"\n")
    the_file.write("X2mtj"+str(mtj_per_column - 1)+" n_precharge gnd n2_bl_"+str(mtj_per_column)+" gnd n2_br_"+str(mtj_per_column)+" gnd vdd_selectedh gnd memorycellh\n")
    
    # Initial conditions:
    the_file.write(".IC V(n2_bl_0) = 0.8 \n")
    the_file.write(".IC V(n2_br_0) = 0 \n")


    the_file.write(".END")
    the_file.close()

    # Come out of top-level directory
    os.chdir("../")

    return (name + "/" + name + ".sp")


# This netlist measures the power consumption of write operation in SRAM-basd memories
def generate_sram_writehh_power_top_lp(name, sram_per_column, unselected_column_count):

    # Create directories
    if not os.path.exists(name):
        os.makedirs(name)  
    # Change to directory    
    os.chdir(name)   

    # Create and open file
    # The following are important parameter definitions
    # ram_frequency is the operating frequency of the SRAM-based memory
    # precharge_max is the maximum of precharge delay, rowdecoder delay and configurable decoder delay
    # wl_eva is the sum of worldline delay and evaluation time + precharge_max
    # sa_xbar_ff is the sum of sense amp, output crossbar and flip flop delays + wl_eva

    # duplicate the precharge?
    if sram_per_column == 512:
        duplicate = 1
    else:
        duplicate = 0

    filename = name + ".sp"
    the_file = open(filename, 'w')
    the_file.write(".TITLE SRAM write power measurement circuit \n\n")
    the_file.write("********************************************************************************\n")
    the_file.write("** Include libraries, parameters and other\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".LIB \"../includes.l\" INCLUDES\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Setup and input\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".TRAN 1p '4 * ram_frequency' SWEEP DATA=sweep_data\n")
    the_file.write(".OPTIONS BRIEF=1\n\n")
    the_file.write("* Input signal\n")
    the_file.write("Vprecharge n_precharge gnd PULSE (supply_v_lp 0 0 50p 50p 'precharge_max' 'ram_frequency')\n")

    the_file.write("* Power rail for the circuit under test.\n")
    the_file.write("* This allows us to measure power of a circuit under test without measuring the power of wave shaping and load circuitry.\n")
    the_file.write("V_selected vdd_selected gnd supply_v_lp\n\n")
    the_file.write("V_unselected vdd_unselected gnd supply_v_lp\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Measurement\n")
    the_file.write("********************************************************************************\n\n")

    the_file.write("* Measure the power required to propagate a rise and a fall transition through the subcircuit at 250MHz.\n")
    the_file.write(".MEASURE TRAN meas_current_selected INTEGRAL I(V_selected) FROM= 0ns TO='4 * ram_frequency'\n")
    the_file.write(".MEASURE TRAN meas_avg_power_selected PARAM = '-(meas_current_selected/(4 * ram_frequency)) * supply_v_lp'\n\n")
    the_file.write(".MEASURE TRAN meas_current_unselected INTEGRAL I(V_unselected) FROM= 0ns TO='4 * ram_frequency'\n")
    the_file.write(".MEASURE TRAN meas_avg_power_unselected PARAM = '-(meas_current_unselected/(4 * ram_frequency)) * supply_v_lp'\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Circuit\n")
    the_file.write("********************************************************************************\n\n")

    # sense amp
    the_file.write("xsamp1 vdd_lp tgate_l tgate_r n_hang_samp vdd_selected gnd samp1\n")
    # write driver
    the_file.write("xwrite n_precharge vdd_lp tgate_l tgate_r vdd_selected gnd writedriver\n")
    # column selectors
    the_file.write("xtgate1 n_bl_0 tgate_l vdd_lp gnd vdd_selected gnd RAM_tgate\n")
    the_file.write("xtgater n_br_0 tgate_r vdd_lp gnd vdd_selected gnd RAM_tgate\n")
    the_file.write("xprecharge n_precharge n_bl_0 n_br_0 vdd_selected gnd precharge\n")
    if duplicate == 1:
        the_file.write("xprecharge_dup n_precharge n_bl_512 n_br_512 vdd_selected gnd precharge\n")

    #unselected columns
    for i in range(0, unselected_column_count):
        the_file.write("xtgatel_"+str(i)+" n_bl"+str(i)+"_0 tgate_l gnd vdd_lp vdd_unselected gnd RAM_tgate\n")
        the_file.write("xtgater_"+str(i)+" n_br"+str(i)+"_0 tgate_r gnd vdd_lp vdd_unselected gnd RAM_tgate\n")
        the_file.write("xprecharge"+str(i)+" n_precharge n_bl"+str(i)+"_0 n_br"+str(i)+"_0 vdd_unselected gnd precharge\n")
        if duplicate == 1:
            the_file.write("xprecharge"+str(i)+"_dup n_precharge n_bl"+str(i)+"_512 n_br"+str(i)+"_512 vdd_unselected gnd precharge\n")    
    # SRAM cells
    # selected column:
    for i in range(0, sram_per_column - 1):
        the_file.write("Xwirel"+str(i)+" n_bl_"+str(i)+" n_bl_"+str(i+1)+" wire Rw=wire_memorycell_vertical_res/"+str(sram_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(sram_per_column)+"\n")
        the_file.write("Xwirer"+str(i)+" n_br_"+str(i)+" n_br_"+str(i+1)+" wire Rw=wire_memorycell_vertical_res/"+str(sram_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(sram_per_column)+"\n")
        the_file.write("Xsram"+str(i)+" gnd gnd n_bl_"+str(i + 1)+" gnd n_br_"+str(i + 1)+" gnd vdd_selected gnd memorycell\n")
    the_file.write("Xwirel"+str(sram_per_column - 1)+" n_bl_"+str(sram_per_column -1)+" n_bl_"+str(sram_per_column)+" wire Rw=wire_memorycell_vertical_res/"+str(sram_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(sram_per_column)+"\n")
    the_file.write("Xwirer"+str(sram_per_column - 1)+" n_br_"+str(sram_per_column -1)+" n_br_"+str(sram_per_column)+" wire Rw=wire_memorycell_vertical_res/"+str(sram_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(sram_per_column)+"\n")
    the_file.write("Xsram"+str(sram_per_column - 1)+" n_precharge gnd n_bl_"+str(sram_per_column)+" gnd n_br_"+str(sram_per_column)+" gnd vdd_selected gnd memorycell\n")
    # unselected column:
    for j in range(0, unselected_column_count):
        for i in range(0, sram_per_column - 1):
            the_file.write("Xwire"+str(j)+"l"+str(i)+" n_bl"+str(j)+"_"+str(i)+" n_bl"+str(j)+"_"+str(i+1)+" wire Rw=wire_memorycell_vertical_res/"+str(sram_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(sram_per_column)+"\n")
            the_file.write("Xwire"+str(j)+"r"+str(i)+" n_br"+str(j)+"_"+str(i)+" n_br"+str(j)+"_"+str(i+1)+" wire Rw=wire_memorycell_vertical_res/"+str(sram_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(sram_per_column)+"\n")
            the_file.write("Xsram_"+str(j)+"_"+str(i)+" gnd gnd n_bl"+str(j)+"_"+str(i + 1)+" gnd n_br"+str(j)+"_"+str(i + 1)+" gnd vdd_unselected gnd memorycell\n")
        the_file.write("Xwire"+str(j)+"l"+str(sram_per_column - 1)+" n_bl"+str(j)+"_"+str(sram_per_column - 1)+" n_bl"+str(j)+"_"+str(sram_per_column)+" wire Rw=wire_memorycell_vertical_res/"+str(sram_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(sram_per_column)+"\n")
        the_file.write("Xwire"+str(j)+"r"+str(sram_per_column - 1)+" n_br"+str(j)+"_"+str(sram_per_column - 1)+" n_br"+str(j)+"_"+str(sram_per_column)+" wire Rw=wire_memorycell_vertical_res/"+str(sram_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(sram_per_column)+"\n")
        the_file.write("Xsram_"+str(j)+"_"+str(sram_per_column - 1)+" n_precharge gnd n_bl"+str(j)+"_"+str(sram_per_column)+" gnd n_br"+str(j)+"_"+str(sram_per_column)+" gnd vdd_unselected gnd memorycell\n")
    # initial conditions:
    # one of the bitline is set to vdd, the other set to 0:
    the_file.write(".IC V(n_bl_0) = 'supply_v_lp' \n")
    the_file.write(".IC V(n_br_0) = 0 \n")

    for i in range(0, sram_per_column):
        the_file.write(".IC V(Xsram"+str(i)+".n_1_1) = 'supply_v_lp' \n")
        the_file.write(".IC V(Xsram"+str(i)+".n_1_2) = 0 \n")
    for i in range(0, sram_per_column):
        for j in range(0, unselected_column_count):
            the_file.write(".IC V(n_bl"+str(j)+"_"+str(i)+") = 'supply_v_lp' \n")
            the_file.write(".IC V(n_br"+str(j)+"_"+str(i)+") = 0 \n")
            the_file.write(".IC V(Xsram_"+str(j)+"_"+str(i)+".n_1_1) = 'supply_v_lp' \n")
            the_file.write(".IC V(Xsram_"+str(j)+"_"+str(i)+".n_1_2) = 0 \n")

    the_file.write(".print tran V(tgate_l) V(tgate_r) V(n_bl_0) V(n_bl_"+str(sram_per_column)+") V(n_br_0) V(Xprechargesa.n_1_2) V(n_br_"+str(sram_per_column)+") V(n_bl"+str(0)+"_"+str(sram_per_column)+") V(n_br"+str(0)+"_"+str(sram_per_column)+") V(Xsram"+str(sram_per_column - 1)+".n_1_2) V(Xsram"+str(sram_per_column - 1)+".n_1_1) V(n_precharge) V(n_wl_eva) I(V_unselected) I(V_selected)\n")   
    the_file.write(".END")
    the_file.close()

    # Come out of top-level directory
    os.chdir("../")

    return (name + "/" + name + ".sp")

# This netlist measures the power consumption of write operation in SRAM-basd memories
def generate_sram_writep_power_top_lp(name, sram_per_column, unselected_column_count):

    # Create directories
    if not os.path.exists(name):
        os.makedirs(name)  
    # Change to directory    
    os.chdir(name)   

    # Create and open file
    # The following are important parameter definitions
    # ram_frequency is the operating frequency of the SRAM-based memory
    # precharge_max is the maximum of precharge delay, rowdecoder delay and configurable decoder delay
    # wl_eva is the sum of worldline delay and evaluation time + precharge_max
    # sa_xbar_ff is the sum of sense amp, output crossbar and flip flop delays + wl_eva

    # duplicate the precharge?
    if sram_per_column == 512:
        duplicate = 1
    else:
        duplicate = 0

    filename = name + ".sp"
    the_file = open(filename, 'w')
    the_file.write(".TITLE SRAM write power measurement circuit \n\n")
    the_file.write("********************************************************************************\n")
    the_file.write("** Include libraries, parameters and other\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".LIB \"../includes.l\" INCLUDES\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Setup and input\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".TRAN 1p '4 * ram_frequency' SWEEP DATA=sweep_data\n")
    the_file.write(".OPTIONS BRIEF=1\n\n")
    the_file.write("* Input signal\n")
    the_file.write("Vprecharge n_precharge gnd PULSE (supply_v_lp 0 0 50p 50p 'precharge_max' 'ram_frequency')\n")
    the_file.write("Vdatain n_data_in gnd PULSE (supply_v_lp 0 0 0 0 'ram_frequency' ' 2 * ram_frequency')\n")

    the_file.write("* Power rail for the circuit under test.\n")
    the_file.write("* This allows us to measure power of a circuit under test without measuring the power of wave shaping and load circuitry.\n")
    the_file.write("V_selected vdd_selected gnd supply_v_lp\n\n")
    the_file.write("V_unselected vdd_unselected gnd supply_v_lp\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Measurement\n")
    the_file.write("********************************************************************************\n\n")

    the_file.write("* Measure the power required to propagate a rise and a fall transition through the subcircuit at 250MHz.\n")
    the_file.write(".MEASURE TRAN meas_current_selected INTEGRAL I(V_selected) FROM= 0ns TO='4 * ram_frequency'\n")
    the_file.write(".MEASURE TRAN meas_avg_power_selected PARAM = '-(meas_current_selected/(4 * ram_frequency)) * supply_v_lp'\n\n")
    the_file.write(".MEASURE TRAN meas_current_unselected INTEGRAL I(V_unselected) FROM= 0ns TO='4 * ram_frequency'\n")
    the_file.write(".MEASURE TRAN meas_avg_power_unselected PARAM = '-(meas_current_unselected/(4 * ram_frequency)) * supply_v_lp'\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Circuit\n")
    the_file.write("********************************************************************************\n\n")

    # sense amp
    the_file.write("xsamp1 vdd_lp tgate_l tgate_r n_hang_samp vdd_selected gnd samp1\n")
    # write driver
    the_file.write("xwrite gnd n_data_in tgate_l tgate_r vdd_selected gnd writedriver\n")
    # column selectors
    the_file.write("xtgate1 n_bl_0 tgate_l vdd_lp gnd vdd_selected gnd RAM_tgate\n")
    the_file.write("xtgater n_br_0 tgate_r vdd_lp gnd vdd_selected gnd RAM_tgate\n")
    the_file.write("xprecharge n_precharge n_bl_0 n_br_0 vdd_selected gnd precharge\n")
    if duplicate == 1:
        the_file.write("xprecharge_dup n_precharge n_bl_512 n_br_512 vdd_selected gnd precharge\n")

    #unselected columns
    for i in range(0, unselected_column_count):
        the_file.write("xtgatel_"+str(i)+" n_bl"+str(i)+"_0 tgate_l gnd vdd_lp vdd_unselected gnd RAM_tgate\n")
        the_file.write("xtgater_"+str(i)+" n_br"+str(i)+"_0 tgate_r gnd vdd_lp vdd_unselected gnd RAM_tgate\n")
        the_file.write("xprecharge"+str(i)+" n_precharge n_bl"+str(i)+"_0 n_br"+str(i)+"_0 vdd_unselected gnd precharge\n")
        if duplicate == 1:
            the_file.write("xprecharge"+str(i)+"_dup n_precharge n_bl"+str(i)+"_512 n_br"+str(i)+"_512 vdd_unselected gnd precharge\n")    
    # SRAM cells
    # selected column:
    for i in range(0, sram_per_column - 1):
        the_file.write("Xwirel"+str(i)+" n_bl_"+str(i)+" n_bl_"+str(i+1)+" wire Rw=wire_memorycell_vertical_res/"+str(sram_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(sram_per_column)+"\n")
        the_file.write("Xwirer"+str(i)+" n_br_"+str(i)+" n_br_"+str(i+1)+" wire Rw=wire_memorycell_vertical_res/"+str(sram_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(sram_per_column)+"\n")
        the_file.write("Xsram"+str(i)+" gnd gnd n_bl_"+str(i + 1)+" gnd n_br_"+str(i + 1)+" gnd vdd_selected gnd memorycell\n")
    the_file.write("Xwirel"+str(sram_per_column - 1)+" n_bl_"+str(sram_per_column -1)+" n_bl_"+str(sram_per_column)+" wire Rw=wire_memorycell_vertical_res/"+str(sram_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(sram_per_column)+"\n")
    the_file.write("Xwirer"+str(sram_per_column - 1)+" n_br_"+str(sram_per_column -1)+" n_br_"+str(sram_per_column)+" wire Rw=wire_memorycell_vertical_res/"+str(sram_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(sram_per_column)+"\n")
    the_file.write("Xsram"+str(sram_per_column - 1)+" n_precharge gnd n_bl_"+str(sram_per_column)+" gnd n_br_"+str(sram_per_column)+" gnd vdd_selected gnd memorycell\n")
    # unselected column:
    for j in range(0, unselected_column_count):
        for i in range(0, sram_per_column - 1):
            the_file.write("Xwire"+str(j)+"l"+str(i)+" n_bl"+str(j)+"_"+str(i)+" n_bl"+str(j)+"_"+str(i+1)+" wire Rw=wire_memorycell_vertical_res/"+str(sram_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(sram_per_column)+"\n")
            the_file.write("Xwire"+str(j)+"r"+str(i)+" n_br"+str(j)+"_"+str(i)+" n_br"+str(j)+"_"+str(i+1)+" wire Rw=wire_memorycell_vertical_res/"+str(sram_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(sram_per_column)+"\n")
            the_file.write("Xsram_"+str(j)+"_"+str(i)+" gnd gnd n_bl"+str(j)+"_"+str(i + 1)+" gnd n_br"+str(j)+"_"+str(i + 1)+" gnd vdd_unselected gnd memorycell\n")
        the_file.write("Xwire"+str(j)+"l"+str(sram_per_column - 1)+" n_bl"+str(j)+"_"+str(sram_per_column - 1)+" n_bl"+str(j)+"_"+str(sram_per_column)+" wire Rw=wire_memorycell_vertical_res/"+str(sram_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(sram_per_column)+"\n")
        the_file.write("Xwire"+str(j)+"r"+str(sram_per_column - 1)+" n_br"+str(j)+"_"+str(sram_per_column - 1)+" n_br"+str(j)+"_"+str(sram_per_column)+" wire Rw=wire_memorycell_vertical_res/"+str(sram_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(sram_per_column)+"\n")
        the_file.write("Xsram_"+str(j)+"_"+str(sram_per_column - 1)+" n_precharge gnd n_bl"+str(j)+"_"+str(sram_per_column)+" gnd n_br"+str(j)+"_"+str(sram_per_column)+" gnd vdd_unselected gnd memorycell\n")
    # initial conditions:
    # one of the bitline is set to vdd, the other set to 0:
    the_file.write(".IC V(n_bl_0) = 'supply_v_lp' \n")
    the_file.write(".IC V(n_br_0) = 0 \n")

    for i in range(0, sram_per_column):
        the_file.write(".IC V(Xsram"+str(i)+".n_1_1) = 'supply_v_lp' \n")
        the_file.write(".IC V(Xsram"+str(i)+".n_1_2) = 0 \n")
    for i in range(0, sram_per_column):
        for j in range(0, unselected_column_count):
            the_file.write(".IC V(n_bl"+str(j)+"_"+str(i)+") = 'supply_v_lp' \n")
            the_file.write(".IC V(n_br"+str(j)+"_"+str(i)+") = 0 \n")
            the_file.write(".IC V(Xsram_"+str(j)+"_"+str(i)+".n_1_1) = 'supply_v_lp' \n")
            the_file.write(".IC V(Xsram_"+str(j)+"_"+str(i)+".n_1_2) = 0 \n")

    the_file.write(".print tran V(tgate_l) V(tgate_r) V(n_bl_0) V(n_bl_"+str(sram_per_column)+") V(n_br_0) V(Xprechargesa.n_1_2) V(n_br_"+str(sram_per_column)+") V(n_bl"+str(0)+"_"+str(sram_per_column)+") V(n_br"+str(0)+"_"+str(sram_per_column)+") V(Xsram"+str(sram_per_column - 1)+".n_1_2) V(Xsram"+str(sram_per_column - 1)+".n_1_1) V(n_precharge) V(n_wl_eva) I(V_unselected) I(V_selected)\n")   
    the_file.write(".END")
    the_file.close()

    # Come out of top-level directory
    os.chdir("../")

    return (name + "/" + name + ".sp")


# This netlist measures the power consumption of read operation in SRAM-basd memories
def generate_sram_read_power_top_lp(name, sram_per_column, unselected_column_count):

    # Create directories
    if not os.path.exists(name):
        os.makedirs(name)  
    # Change to directory    
    os.chdir(name)   

    # Create and open file
    # The following are important parameter definitions
    # ram_frequency is the operating frequency of the SRAM-based memory
    # precharge_max is the maximum of precharge delay, rowdecoder delay and configurable decoder delay
    # wl_eva is the sum of worldline delay and evaluation time + precharge_max
    # sa_xbar_ff is the sum of sense amp, output crossbar and flip flop delays + wl_eva

    # duplicate the precharge?
    if sram_per_column == 512:
        duplicate = 1
    else:
        duplicate = 0

    filename = name + ".sp"
    the_file = open(filename, 'w')
    the_file.write(".TITLE SRAM read power measurement circuit \n\n")
    the_file.write("********************************************************************************\n")
    the_file.write("** Include libraries, parameters and other\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".LIB \"../includes.l\" INCLUDES\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Setup and input\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".TRAN 1p '4 * ram_frequency' SWEEP DATA=sweep_data\n")
    the_file.write(".OPTIONS BRIEF=1\n\n")
    the_file.write("* Input signal\n")
    the_file.write("Vprecharge n_precharge gnd PULSE (supply_v_lp 0 0 50p 50p 'precharge_max' 'ram_frequency')\n")
    the_file.write("Vprecharge2 n_precharge2 gnd PULSE (supply_v_lp 0 0 50p 50p 'precharge_max' 'ram_frequency')\n")
    the_file.write("Vwl n_wl_eva gnd PULSE (supply_v_lp 0 0 50p 50p 'wl_eva' 'ram_frequency')\n")

    the_file.write("* Power rail for the circuit under test.\n")
    the_file.write("* This allows us to measure power of a circuit under test without measuring the power of wave shaping and load circuitry.\n")
    the_file.write("V_selected vdd_selected gnd supply_v_lp\n\n")
    the_file.write("V_unselected vdd_unselected gnd supply_v_lp\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Measurement\n")
    the_file.write("********************************************************************************\n\n")

    the_file.write("* Measure the power required to propagate a rise and a fall transition through the subcircuit at 250MHz.\n")
    the_file.write(".MEASURE TRAN meas_current_selected INTEGRAL I(V_selected) FROM=0ns TO='4 * ram_frequency'\n")
    the_file.write(".MEASURE TRAN meas_avg_power_selected PARAM = '-(meas_current_selected/(4 * ram_frequency)) * supply_v_lp'\n\n")
    the_file.write(".MEASURE TRAN meas_current_unselected INTEGRAL I(V_unselected) FROM=0ns TO='4 * ram_frequency'\n")
    the_file.write(".MEASURE TRAN meas_avg_power_unselected PARAM = '-(meas_current_unselected/(4 * ram_frequency)) * supply_v_lp'\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Circuit\n")
    the_file.write("********************************************************************************\n\n")

    # sense amp
    the_file.write("xsamp1 n_wl_eva tgate_l tgate_r n_hang_samp vdd_selected gnd samp1\n")
    # write driver
    the_file.write("xwrite gnd gnd tgate_l tgate_r vdd_selected gnd writedriver\n")
    # column selectors
    the_file.write("xtgate1 n_bl_0 tgate_l vdd_lp gnd vdd_selected gnd RAM_tgate\n")
    the_file.write("xtgater n_br_0 tgate_r vdd_lp gnd vdd_selected gnd RAM_tgate\n")
    the_file.write("xprecharge n_precharge n_bl_0 n_br_0 vdd_selected gnd precharge\n")
    if duplicate == 1:
        the_file.write("xprecharge_dup n_precharge n_bl_512 n_br_512 vdd_selected gnd precharge\n")

    #unselected columns
    for i in range(0, unselected_column_count):
        the_file.write("xtgatel_"+str(i)+" n_bl"+str(i)+"_0 tgate_l gnd vdd_lp vdd_unselected gnd RAM_tgate\n")
        the_file.write("xtgater_"+str(i)+" n_br"+str(i)+"_0 tgate_r gnd vdd_lp vdd_unselected gnd RAM_tgate\n")
        the_file.write("xprecharge"+str(i)+" n_precharge n_bl"+str(i)+"_0 n_br"+str(i)+"_0 vdd_unselected gnd precharge\n")
        if duplicate == 1:
            the_file.write("xprecharge"+str(i)+"_dup n_precharge n_bl"+str(i)+"_512 n_br"+str(i)+"_512 vdd_unselected gnd precharge\n")    
    # SRAM cells
    # selected column:
    for i in range(0, sram_per_column - 1):
        the_file.write("Xwirel"+str(i)+" n_bl_"+str(i)+" n_bl_"+str(i+1)+" wire Rw=wire_memorycell_vertical_res/"+str(sram_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(sram_per_column)+"\n")
        the_file.write("Xwirer"+str(i)+" n_br_"+str(i)+" n_br_"+str(i+1)+" wire Rw=wire_memorycell_vertical_res/"+str(sram_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(sram_per_column)+"\n")
        the_file.write("Xsram"+str(i)+" gnd gnd n_bl_"+str(i + 1)+" gnd n_br_"+str(i + 1)+" gnd vdd_selected gnd memorycell\n")
    the_file.write("Xwirel"+str(sram_per_column - 1)+" n_bl_"+str(sram_per_column -1)+" n_bl_"+str(sram_per_column)+" wire Rw=wire_memorycell_vertical_res/"+str(sram_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(sram_per_column)+"\n")
    the_file.write("Xwirer"+str(sram_per_column - 1)+" n_br_"+str(sram_per_column -1)+" n_br_"+str(sram_per_column)+" wire Rw=wire_memorycell_vertical_res/"+str(sram_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(sram_per_column)+"\n")
    the_file.write("Xsram"+str(sram_per_column - 1)+" n_precharge2 gnd n_bl_"+str(sram_per_column)+" gnd n_br_"+str(sram_per_column)+" gnd vdd_selected gnd memorycell\n")
    # unselected column:
    for j in range(0, unselected_column_count):
        for i in range(0, sram_per_column - 1):
            the_file.write("Xwire"+str(j)+"l"+str(i)+" n_bl"+str(j)+"_"+str(i)+" n_bl"+str(j)+"_"+str(i+1)+" wire Rw=wire_memorycell_vertical_res/"+str(sram_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(sram_per_column)+"\n")
            the_file.write("Xwire"+str(j)+"r"+str(i)+" n_br"+str(j)+"_"+str(i)+" n_br"+str(j)+"_"+str(i+1)+" wire Rw=wire_memorycell_vertical_res/"+str(sram_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(sram_per_column)+"\n")
            the_file.write("Xsram_"+str(j)+"_"+str(i)+" gnd gnd n_bl"+str(j)+"_"+str(i + 1)+" gnd n_br"+str(j)+"_"+str(i + 1)+" gnd vdd_unselected gnd memorycell\n")
        the_file.write("Xwire"+str(j)+"l"+str(sram_per_column - 1)+" n_bl"+str(j)+"_"+str(sram_per_column - 1)+" n_bl"+str(j)+"_"+str(sram_per_column)+" wire Rw=wire_memorycell_vertical_res/"+str(sram_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(sram_per_column)+"\n")
        the_file.write("Xwire"+str(j)+"r"+str(sram_per_column - 1)+" n_br"+str(j)+"_"+str(sram_per_column - 1)+" n_br"+str(j)+"_"+str(sram_per_column)+" wire Rw=wire_memorycell_vertical_res/"+str(sram_per_column)+" Cw=wire_memorycell_vertical_cap/"+str(sram_per_column)+"\n")
        the_file.write("Xsram_"+str(j)+"_"+str(sram_per_column - 1)+" n_precharge2 gnd n_bl"+str(j)+"_"+str(sram_per_column)+" gnd n_br"+str(j)+"_"+str(sram_per_column)+" gnd vdd_unselected gnd memorycell\n")
    # initial conditions:
    # one of the bitline is set to vdd, the other set to 0:
    the_file.write(".IC V(n_bl_0) = 'supply_v_lp' \n")
    the_file.write(".IC V(n_br_0) = 0 \n")

    for i in range(0, sram_per_column):
        the_file.write(".IC V(Xsram"+str(i)+".n_1_1) = 'supply_v_lp' \n")
        the_file.write(".IC V(Xsram"+str(i)+".n_1_2) = 0 \n")
    for i in range(0, sram_per_column):
        for j in range(0, unselected_column_count):
            the_file.write(".IC V(n_bl"+str(j)+"_"+str(i)+") = 'supply_v_lp' \n")
            the_file.write(".IC V(n_br"+str(j)+"_"+str(i)+") = 0 \n")
            the_file.write(".IC V(Xsram_"+str(j)+"_"+str(i)+".n_1_1) = 'supply_v_lp' \n")
            the_file.write(".IC V(Xsram_"+str(j)+"_"+str(i)+".n_1_2) = 0 \n")

    #the_file.write(".print tran V(n_bl_0) V(n_bl_"+str(sram_per_column)+") V(n_br_0) V(Xprechargesa.n_1_2) V(n_br_"+str(sram_per_column)+") V(n_bl"+str(0)+"_"+str(sram_per_column)+") V(n_br"+str(0)+"_"+str(sram_per_column)+") V(Xsram"+str(sram_per_column - 1)+".n_1_2) V(Xsram"+str(sram_per_column - 1)+".n_1_1) V(n_precharge) V(n_wl_eva) I(V_unselected) I(V_selected)\n")   
    the_file.write(".END")
    the_file.close()

    # Come out of top-level directory
    os.chdir("../")

    return (name + "/" + name + ".sp")


# This is the top-level netlist used to evaluate and size the output crossbar:

def generate_pgateoutputcrossbar_top(name, maxwidth, def_use_tgate):

    # Create directories
    if not os.path.exists(name):
        os.makedirs(name)  
    # Change to directory    
    os.chdir(name)

    # create the spice file and generate the netlist
    filename = name + ".sp"
    the_file = open(filename, 'w')
    the_file.write(".TITLE A nand2 path\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Include libraries, parameters and other\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".LIB \"../includes.l\" INCLUDES\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Setup and input\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".TRAN 1p 4n SWEEP DATA=sweep_data\n")
    the_file.write(".OPTIONS BRIEF=1\n\n")
    the_file.write("* Input signal\n")
    the_file.write("VIN n_in gnd PULSE (0 supply_v 0 0 0 2n 4n)\n")

    
    the_file.write("* Power rail for the circuit under test.\n")
    the_file.write("* This allows us to measure power of a circuit under test without measuring the power of wave shaping and load circuitry.\n")
    the_file.write("V_nand2 vdd_nand2 gnd supply_v\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Measurement\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write("* inv_" + name + " delay\n")
    the_file.write(".MEASURE TRAN meas_inv_" + name + "_1_tfall TRIG V(n_1_1) VAL='supply_v/2' RISE=1\n")
    the_file.write("+    TARG V(xoutputcrossbar.n_1_1) VAL='supply_v/2' FALL=1\n")
    the_file.write(".MEASURE TRAN meas_inv_" + name + "_1_trise TRIG V(n_1_1) VAL='supply_v/2' FALL=1\n")
    the_file.write("+    TARG V(xoutputcrossbar.n_1_1) VAL='supply_v/2' RISE=1\n\n")

    the_file.write("* inv_" + name + " delay\n")
    the_file.write(".MEASURE TRAN meas_inv_" + name + "_2_tfall TRIG V(n_1_1) VAL='supply_v/2' FALL=1\n")
    the_file.write("+    TARG V(xoutputcrossbar.n_1_2) VAL='supply_v/2' FALL=1\n")
    the_file.write(".MEASURE TRAN meas_inv_" + name + "_2_trise TRIG V(n_1_1) VAL='supply_v/2' RISE=1\n")
    the_file.write("+    TARG V(xoutputcrossbar.n_1_2) VAL='supply_v/2' RISE=1\n\n")

    # There are other output crossbar types possible.
    # I added this line so that we could try them out in the future
    if def_use_tgate == 0:

        the_file.write("* inv_" + name + " delay\n")
        the_file.write(".MEASURE TRAN meas_inv_" + name + "_3_tfall TRIG V(n_1_1) VAL='supply_v/2' RISE=1\n")
        the_file.write("+    TARG V(xoutputcrossbar.n_1_3) VAL='supply_v/2' FALL=1\n")
        the_file.write(".MEASURE TRAN meas_inv_" + name + "_3_trise TRIG V(n_1_1) VAL='supply_v/2' FALL=1\n")
        the_file.write("+    TARG V(xoutputcrossbar.n_1_3) VAL='supply_v/2' RISE=1\n\n")

    the_file.write("* Total delays\n")
    the_file.write(".MEASURE TRAN meas_total_tfall TRIG V(n_1_1) VAL='supply_v/2' FALL=1\n")
    the_file.write("+    TARG V(n_1_2) VAL='supply_v/2' RISE=1\n")
    the_file.write(".MEASURE TRAN meas_total_trise TRIG V(n_1_1) VAL='supply_v/2' RISE=1\n")
    the_file.write("+    TARG V(n_1_2) VAL='supply_v/2' FALL=1\n\n")

    the_file.write(".MEASURE TRAN meas_logic_low_voltage FIND V(n_in) AT=3n\n\n")

    the_file.write("* Measure the power required to propagate a rise and a fall transition through the subcircuit at 250MHz.\n")
    the_file.write(".MEASURE TRAN meas_current INTEGRAL I(V_nand2) FROM=0ns TO=4ns\n")
    the_file.write(".MEASURE TRAN meas_avg_power PARAM = '-(meas_current/8n)*supply_v'\n\n")
    
    the_file.write("********************************************************************************\n")
    the_file.write("** Circuit\n")
    the_file.write("********************************************************************************\n\n")
    #The sense amp driver
    the_file.write("X_inv_samp n_in n_1_1 vdd gnd inv Wn=min_tran_width Wp=min_tran_width\n")   
    #the actual circuit
    the_file.write("xoutputcrossbar n_1_1 n_1_2 vdd_nand2 vsram gnd pgateoutputcrossbar\n")
    #the load (a flip flop in this case)
    the_file.write("Xff n_1_2 n_hang2 vdd gnd vdd nnd gnd vdd gnd vdd vdd gnd ff\n")


    the_file.write(".END")
    the_file.close()

    # Come out of top-level directory
    os.chdir("../")

    return (name + "/" + name + ".sp")


# this is the last stage of the configurable decoder
def generate_configurabledecoderiii_top(name, fanin1,fanin2, required_size, tgatecount):

    # create directory
    if not os.path.exists(name):
        os.makedirs(name)  
    # Change to directory    
    os.chdir(name)

    # create spice file and generate netlist
    filename = name + ".sp"
    the_file = open(filename, 'w')
    the_file.write(".TITLE last stage of configurable decoder\n\n")


    the_file.write("********************************************************************************\n")
    the_file.write("** Include libraries, parameters and other\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".LIB \"../includes.l\" INCLUDES\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Setup and input\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".TRAN 1p 4n SWEEP DATA=sweep_data\n")
    the_file.write(".OPTIONS BRIEF=1\n\n")
    the_file.write("* Input signal\n")
    the_file.write("VIN n_in gnd PULSE (0 supply_v 0 0 0 2n 4n)\n")

    
    the_file.write("* Power rail for the circuit under test.\n")
    the_file.write("* This allows us to measure power of a circuit under test without measuring the power of wave shaping and load circuitry.\n")
    the_file.write("V_third1 vdd_third1 gnd supply_v\n\n")
    the_file.write("V_third2 vdd_third2 gnd supply_v\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Measurement\n")
    the_file.write("********************************************************************************\n\n")

    if fanin1 !=0:
        the_file.write("* inv_nand" + str(required_size) + "" + name + " delay\n")
        the_file.write(".MEASURE TRAN meaz1_inv_nand" + str(required_size) + "_" + name + "_1_tfall TRIG V(n_1_"+str(fanin1)+") VAL='supply_v/2' RISE=1\n")
        the_file.write("+    TARG V(Xloadnand"+str(fanin1)+".n_1_1) VAL='supply_v/2' FALL=1\n")
        the_file.write(".MEASURE TRAN meaz1_inv_nand" + str(required_size) + "_" + name + "_1_trise TRIG V(n_1_"+str(fanin1)+") VAL='supply_v/2' FALL=1\n")
        the_file.write("+    TARG V(Xloadnand"+str(fanin1)+".n_1_1) VAL='supply_v/2' RISE=1\n\n")

        the_file.write("* inv" + name + "_2 delay\n")
        the_file.write(".MEASURE TRAN meaz1_inv_" + name + "_2_tfall TRIG V(n_1_"+str(fanin1)+") VAL='supply_v/2' FALL=1\n")
        the_file.write("+    TARG V(Xloadnand"+str(fanin1)+".n_out) VAL='supply_v/2' FALL=1\n")
        the_file.write(".MEASURE TRAN meaz1_inv_" + name + "_2_trise TRIG V(n_1_"+str(fanin1)+") VAL='supply_v/2' RISE=1\n")
        the_file.write("+    TARG V(Xloadnand"+str(fanin1)+".n_out) VAL='supply_v/2' RISE=1\n\n")


        the_file.write("* Total delays\n")
        the_file.write(".MEASURE TRAN meaz1_total_tfall TRIG V(n_1_"+str(fanin1)+") VAL='supply_v/2' FALL=1\n")
        the_file.write("+    TARG V(n_1_"+str(fanin1 + tgatecount + 2)+") VAL='supply_v/2' FALL=1\n")
        the_file.write(".MEASURE TRAN meaz1_total_trise TRIG V(n_1_"+str(fanin1)+") VAL='supply_v/2' RISE=1\n")
        the_file.write("+    TARG V(n_1_"+str(fanin1 + tgatecount + 2)+") VAL='supply_v/2' RISE=1\n\n")

        
    if fanin2 !=0:
        the_file.write("* inv_nand" + name + " delay\n")
        the_file.write(".MEASURE TRAN meaz2_inv_nand" + str(required_size) + "_" + name + "_1_tfall TRIG V(n_2_"+str(fanin2)+") VAL='supply_v/2' RISE=1\n")
        the_file.write("+    TARG V(X2loadnand"+str(fanin2)+".n_1_1) VAL='supply_v/2' FALL=1\n")
        the_file.write(".MEASURE TRAN meaz2_inv_nand" + str(required_size) + "_" + name + "_1_trise TRIG V(n_2_"+str(fanin2)+") VAL='supply_v/2' FALL=1\n")
        the_file.write("+    TARG V(X2loadnand"+str(fanin2)+".n_1_1) VAL='supply_v/2' RISE=1\n\n")

        the_file.write("* inv" + name + "_2 delay\n")
        the_file.write(".MEASURE TRAN meaz2_inv_" + name + "_2_tfall TRIG V(n_2_"+str(fanin2)+") VAL='supply_v/2' FALL=1\n")
        the_file.write("+    TARG V(X2loadnand"+str(fanin2)+".n_out) VAL='supply_v/2' FALL=1\n")
        the_file.write(".MEASURE TRAN meaz2_inv_" + name + "_2_trise TRIG V(n_2_"+str(fanin2)+") VAL='supply_v/2' RISE=1\n")
        the_file.write("+    TARG V(X2loadnand"+str(fanin2)+".n_out) VAL='supply_v/2' RISE=1\n\n")


        the_file.write("* Total delays\n")
        the_file.write(".MEASURE TRAN meaz2_total_tfall TRIG V(n_2_"+str(fanin2)+") VAL='supply_v/2' FALL=1\n")
        the_file.write("+    TARG V(n_2_"+str(fanin2 + tgatecount + 2)+") VAL='supply_v/2' FALL=1\n")
        the_file.write(".MEASURE TRAN meaz2_total_trise TRIG V(n_2_"+str(fanin2)+") VAL='supply_v/2' RISE=1\n")
        the_file.write("+    TARG V(n_2_"+str(fanin2 + tgatecount + 2)+") VAL='supply_v/2' RISE=1\n\n")


    the_file.write(".MEASURE TRAN meas_logic_low_voltage FIND V(n_in) AT=3n\n\n")
    if fanin1 != 0:
        the_file.write("* Measure the power required to propagate a rise and a fall transition through the subcircuit at 250MHz.\n")
        the_file.write(".MEASURE TRAN meaz1_current INTEGRAL I(V_third1) FROM=0ns TO=4ns\n")
        the_file.write(".MEASURE TRAN meaz1_avg_power PARAM = '-(meaz1_current/4n)*supply_v'\n\n")
    if fanin2 != 0:
        the_file.write("* Measure the power required to propagate a rise and a fall transition through the subcircuit at 250MHz.\n")
        the_file.write(".MEASURE TRAN meaz2_current INTEGRAL I(V_third2) FROM=0ns TO=4ns\n")
        the_file.write(".MEASURE TRAN meaz2_avg_power PARAM = '-(meaz2_current/4n)*supply_v'\n\n")
    
    the_file.write("********************************************************************************\n")
    the_file.write("** Circuit\n")
    the_file.write("********************************************************************************\n\n")
    # the configurable decoder can have up to two seperate previous stages that result in different wave forms:
    if fanin1 !=0:
        the_file.write("Xnandu n_in n_1_0 vdd gnd xconfigurabledecoder3ii\n")
        the_file.write("Xwire0 n_1_0 n_1_1 wire Rw=wire_xconfigurabledecoderi_res/"+str(fanin1)+" Cw=wire_xconfigurabledecoderi_cap/"+str(fanin1)+"\n")
        for i in range(1, fanin1):
            the_file.write("Xloadnand"+str(i)+" n_1_"+str(i)+" n_hang_"+str(i+1)+" vdd gnd xconfigurabledecoderiii\n")
            the_file.write("Xwire"+str(i)+" n_1_"+str(i)+" n_1_"+str(i+1)+" wire Rw=wire_xconfigurabledecoderi_res/"+str(fanin1)+" Cw=wire_xconfigurabledecoderi_cap/"+str(fanin1)+"\n")

        the_file.write("Xloadnand"+str(fanin1)+" n_1_"+str(fanin1)+" n_1_"+str(fanin1 + 1)+" vdd_third1 gnd xconfigurabledecoderiii\n")
        #RAM load :
        the_file.write("Xwireadded n_1_"+str(fanin1 + 1)+" n_1_"+str(fanin1 + 2)+" wire Rw=wire_xconfigurabledecoderiii_res Cw=wire_xconfigurabledecoderiii_cap \n")
        for i in range(fanin1 +2, fanin1 +tgatecount +2):
            the_file.write("Xwirel"+str(i)+" n_1_"+str(i)+" n_1_"+str(i+1)+" wire Rw=wire_memorycell_horizontal_res/"+str(tgatecount)+" Cw=wire_memorycell_horizontal_cap/"+str(tgatecount)+"\n")
        the_file.write("Xtgate"+str(fanin1 +tgatecount)+" gnd gnd n_1_"+str(fanin1 +tgatecount+2)+" vdd vdd gnd RAM_tgate\n")

    if fanin2 !=0:
        the_file.write("Xnandv n_in n_2_0 vdd gnd xconfigurabledecoder2ii\n")
        the_file.write("X2wire0 n_2_0 n_2_1 wire Rw=wire_xconfigurabledecoderi_res/"+str(fanin2)+" Cw=wire_xconfigurabledecoderi_cap/"+str(fanin2)+"\n")
        for i in range(1, fanin2):
            the_file.write("X2loadnand"+str(i)+" n_2_"+str(i)+" n_hang2_"+str(i+1)+" vdd gnd xconfigurabledecoderiii\n")
            the_file.write("X2wire"+str(i)+" n_2_"+str(i)+" n_2_"+str(i+1)+" wire Rw=wire_xconfigurabledecoderi_res/"+str(fanin2)+" Cw=wire_xconfigurabledecoderi_cap/"+str(fanin2)+"\n")

        the_file.write("X2loadnand"+str(fanin2)+" n_2_"+str(fanin2)+" n_2_"+str(fanin2 + 1)+" vdd_third1 gnd xconfigurabledecoderiii\n")
        #RAM load should be added here
        the_file.write("Xwireadded2 n_2_"+str(fanin2 + 1)+" n_2_"+str(fanin2 + 2)+" wire Rw=wire_xconfigurabledecoderiii_res Cw=wire_xconfigurabledecoderiii_cap \n")
        for i in range(fanin2 +2, fanin2 +tgatecount +2):
            the_file.write("X2wirel"+str(i)+" n_2_"+str(i)+" n_2_"+str(i+1)+" wire Rw=wire_memorycell_horizontal_res/"+str(tgatecount)+" Cw=wire_memorycell_horizontal_cap/"+str(tgatecount)+"\n") 
        the_file.write("X2tgate"+str(fanin2 +tgatecount)+" gnd gnd n_2_"+str(fanin2 +tgatecount+2)+" vdd vdd gnd RAM_tgate\n")
        #the_file.write("X2loadnand3"+str(fanout1 + fanin2)+" n_2_"+str(fanout1 + fanin2)+" n_2_out vdd gnd thirdstage1\n")

    the_file.write(".END")
    the_file.close()

    # Come out of top-level directory
    os.chdir("../")

    return (name + "/" + name + ".sp")   


# This is the MTJ charing top-level scheme:
def generate_mtj_charge(name, colsize):

    # create directory:
    if not os.path.exists(name):
        os.makedirs(name)  
    # Change to directory    
    os.chdir(name)

    # generate spice file and netlist:

    filename = name + ".sp"
    the_file = open(filename, 'w')
    the_file.write(".TITLE bitline charging process in MTJ-based RAM block\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Include libraries, parameters and other\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".LIB \"../includes.l\" INCLUDES\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Setup and input\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".TRAN 1p 4n SWEEP DATA=sweep_data\n")
    the_file.write(".OPTIONS BRIEF=1\n\n")
    the_file.write("* Input signal\n")
    the_file.write("VIN n_in_b gnd PULSE (0 supply_v_lp 0 0 0 4n 8n)\n")
    the_file.write("VINb n_in gnd PULSE (supply_v_lp 0 0 0 0 4n 8n)\n")


    the_file.write("* Power rail for the circuit under test.\n")
    the_file.write("* This allows us to measure power of a circuit under test without measuring the power of wave shaping and load circuitry.\n")
    the_file.write("V_charge vdd_charge gnd supply_v_lp\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Measurement\n")
    the_file.write("********************************************************************************\n\n")

    the_file.write("* Total delays\n")
    the_file.write(".MEASURE TRAN meas_total_tfall TRIG V(n_in) VAL='supply_v_lp/2' FALL=1\n")
    the_file.write("+    TARG V(n_br_"+str(colsize)+") VAL='target_bl' RISE=1\n")
    #we are only measuring fall, so I just copy it down here for regularity
    the_file.write(".MEASURE TRAN meas_total_trise TRIG V(n_in) VAL='supply_v_lp/2' FALL=1\n")
    the_file.write("+    TARG V(n_br_"+str(colsize)+") VAL='target_bl' RISE=1 \n\n")

    the_file.write(".MEASURE TRAN meas_logic_low_voltage FIND V(gnd) AT=3n\n\n")
    the_file.write(".MEASURE TRAN meas_outputtarget FIND V(n_br_"+str(colsize)+") AT=4n\n\n")

    the_file.write("* Measure the power required to propagate a rise and a fall transition through the subcircuit at 250MHz.\n")
    the_file.write(".MEASURE TRAN meas_current INTEGRAL I(V_charge) FROM=0ns TO=4ns\n")
    the_file.write(".MEASURE TRAN meas_avg_power PARAM = '-(meas_current/4n)*supply_v_lp'\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Circuit\n")
    the_file.write("********************************************************************************\n\n")  


    #MTJ sense amp and precharge
    the_file.write("Xprechargesa n_1_1 n_2_1 gnd gnd n_hang_out vclmpmtj vrefmtj gnd n_in_b vdd_charge gnd mtj_subcircuits_sa\n")
    #MTJ write driver
    the_file.write("Xwritedriver gnd gnd n_1_1 gnd vdd_lp gnd mtj_subcircuits_writedriver\n")
    the_file.write("Xwritedriver_ref gnd gnd n_2_1 gnd vdd_lp gnd mtj_subcircuits_writedriver\n")
    #MTJ CS
    the_file.write("Xcs n_1_1 n_bl_0 n_in n_in_b vdd_lp gnd mtj_subcircuits_cs\n")
    the_file.write("Xcs_ref n_2_1 n_br_0 n_in n_in_b vdd_lp gnd mtj_subcircuits_cs\n")
    #MTJ cells
    for i in range(0, colsize - 1):
        the_file.write("Xwire"+str(i)+" n_bl_"+str(i)+" n_bl_"+str(i+1)+" wire Rw=wire_memorycell_vertical_res/"+str(colsize)+" Cw=wire_memorycell_vertical_cap/"+str(colsize)+"\n")
        the_file.write("XMTJ"+str(i)+" gnd gnd n_bl_"+str(i + 1)+" gnd gnd gnd vdd_lp gnd memorycell\n")

        the_file.write("X2wire"+str(i)+" n_br_"+str(i)+" n_br_"+str(i+1)+" wire Rw=wire_memorycell_vertical_res/"+str(colsize)+" Cw=wire_memorycell_vertical_cap/"+str(colsize)+"\n")
        the_file.write("X2MTJ"+str(i)+" gnd gnd n_br_"+str(i + 1)+" gnd gnd gnd vdd_lp gnd memorycell\n")

    the_file.write("Xwire"+str(colsize)+" n_bl_"+str(colsize - 1)+" n_bl_"+str(colsize)+" wire Rw=wire_memorycell_vertical_res/"+str(colsize)+" Cw=wire_memorycell_vertical_cap/"+str(colsize)+"\n")
    the_file.write("XMTJ"+str(colsize)+" vdd_lp gnd n_bl_"+str(colsize)+" gnd  vdd_lp gnd mtjlow\n")

    the_file.write("X2wire"+str(colsize)+" n_br_"+str(colsize - 1)+" n_br_"+str(colsize)+" wire Rw=wire_memorycell_vertical_res/"+str(colsize)+" Cw=wire_memorycell_vertical_cap/"+str(colsize)+"\n")
    the_file.write("X2MTJ"+str(colsize)+" vdd_lp gnd n_br_"+str(colsize)+" gnd gnd gnd vdd_lp gnd memorycell\n") 

    #initial conditions
    the_file.write(".IC V(n_1_1) = 0 \n")
    the_file.write(".IC V(n_2_1) = 0 \n")
    for i in range(0, colsize + 1):
        the_file.write(".IC V(n_bl_"+str(i)+") = 0 \n")
        the_file.write(".IC V(n_br_"+str(i)+") = 0 \n")


    the_file.write(".END")
    the_file.close()

    # Come out of top-level directory
    os.chdir("../")

    return (name + "/" + name + ".sp")        



# MTJ-based sense amplifier measurements:
def generate_mtj_sa_top(name, colsize):

    # create the directory
    if not os.path.exists(name):
        os.makedirs(name)  
    # Change to directory    
    os.chdir(name)

    # Create the file and generate the netlist:

    filename = name + ".sp"
    the_file = open(filename, 'w')
    the_file.write(".TITLE bitline charging process in MTJ-based RAM block\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Include libraries, parameters and other\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".LIB \"../includes.l\" INCLUDES\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Setup and input\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".TRAN 1p 4n SWEEP DATA=sweep_data\n")
    the_file.write(".OPTIONS BRIEF=1\n\n")
    the_file.write("* Input signal\n")
    the_file.write("VIN n_in gnd PULSE (0 supply_v_lp 'time_bl' 50p 50p 4n 8n)\n")

    the_file.write("VINc n_inc_b gnd PULSE (0 supply_v_lp 0 0 0 4n 8n)\n")
    the_file.write("VINbc n_inc gnd PULSE (supply_v_lp 0 0 0 0 4n 8n)\n")


    the_file.write("* Power rail for the circuit under test.\n")
    the_file.write("* This allows us to measure power of a circuit under test without measuring the power of wave shaping and load circuitry.\n")
    the_file.write("V_charge vdd_charge gnd supply_v_lp\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Measurement\n")
    the_file.write("********************************************************************************\n\n")

    the_file.write("* Total delays\n")
    the_file.write(".MEASURE TRAN meas_total_tfall TRIG V(n_in) VAL='supply_v_lp * 0.1' RISE=1\n")
    the_file.write("+    TARG V(n_hang_out) VAL='supply_v_lp * 0.95' RISE=1\n")
    #we are only measuring fall, so I just copy it down here for regularity
    the_file.write(".MEASURE TRAN meas_total_trise TRIG V(n_in) VAL='supply_v_lp * 0.1' RISE=1\n")
    the_file.write("+    TARG V(n_hang_out) VAL='supply_v_lp * 0.95' RISE=1 \n\n")

    the_file.write(".MEASURE TRAN meas_logic_low_voltage FIND V(gnd) AT=3n\n\n")

    the_file.write("* Measure the power required to propagate a rise and a fall transition through the subcircuit at 250MHz.\n")
    the_file.write(".MEASURE TRAN meas_current INTEGRAL I(V_charge) FROM=0ns TO=4ns\n")
    the_file.write(".MEASURE TRAN meas_avg_power PARAM = '-(meas_current/4n)*supply_v_lp'\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Circuit\n")
    the_file.write("********************************************************************************\n\n")  


    #MTJ sense amp and precharge
    the_file.write("Xprechargesa n_1_1 n_2_1 n_in gnd n_hang_out vclmpmtj vrefmtj vdd_lp gnd vdd_charge gnd mtj_subcircuits_sa\n")

    the_file.write("Xinv4 n_hang_out n_hang_out3 vdd_lp gnd inv_lp Wn = 180n Wp = 300\n")
    #MTJ write driver
    the_file.write("Xwritedriver gnd gnd n_1_1 gnd vdd_lp gnd mtj_subcircuits_writedriver\n")
    the_file.write("Xwritedriver_ref gnd gnd n_2_1 gnd vdd_lp gnd mtj_subcircuits_writedriver\n")
    #MTJ CS
    the_file.write("Xcs n_1_1 n_bl_0 n_inc n_inc_b vdd_lp gnd mtj_subcircuits_cs\n")
    #the_file.write("Xcs n_1_1 gnd n_inc n_inc_b vdd_lp gnd mtj_subcircuits_cs\n")
    the_file.write("Xcs_ref n_2_1 n_br_0 n_inc n_inc_b vdd_lp gnd mtj_subcircuits_cs\n")
    #MTJ cells
    for i in range(0, colsize - 1):
        the_file.write("Xwire"+str(i)+" n_bl_"+str(i)+" n_bl_"+str(i+1)+" wire Rw=wire_memorycell_vertical_res/"+str(colsize)+" Cw=wire_memorycell_vertical_cap/"+str(colsize)+"\n")
        the_file.write("XMTJ"+str(i)+" gnd gnd n_bl_"+str(i + 1)+" gnd gnd gnd vdd_lp gnd memorycell\n")

        the_file.write("X2wire"+str(i)+" n_br_"+str(i)+" n_br_"+str(i+1)+" wire Rw=wire_memorycell_vertical_res/"+str(colsize)+" Cw=wire_memorycell_vertical_cap/"+str(colsize)+"\n")
        the_file.write("X2MTJ"+str(i)+" gnd gnd n_br_"+str(i + 1)+" gnd gnd gnd vdd_lp gnd memorycell\n")

    the_file.write("Xwire"+str(colsize)+" n_bl_"+str(colsize - 1)+" n_bl_"+str(colsize)+" wire Rw=wire_memorycell_vertical_res/"+str(colsize)+" Cw=wire_memorycell_vertical_cap/"+str(colsize)+"\n")
    the_file.write("XMTJ"+str(colsize)+" vdd_lp gnd n_bl_"+str(colsize)+" gnd vdd_lp gnd mtjlow\n")

    the_file.write("X2wire"+str(colsize)+" n_br_"+str(colsize - 1)+" n_br_"+str(colsize)+" wire Rw=wire_memorycell_vertical_res/"+str(colsize)+" Cw=wire_memorycell_vertical_cap/"+str(colsize)+"\n")
    the_file.write("X2MTJ"+str(colsize)+" vdd_lp gnd n_br_"+str(colsize)+" gnd gnd gnd vdd_lp gnd memory_cell_ref\n") 

    the_file.write(".IC V(n_1_1) = 0 \n")
    the_file.write(".IC V(n_2_1) = 0 \n")
    the_file.write(".IC V(Xprechargesa.n_1_5) = 0 \n")
    the_file.write(".IC V(Xprechargesa.n_1_6) = 0 \n")
    for i in range(0, colsize + 1):
        the_file.write(".IC V(n_bl_"+str(i)+") = 0 \n")
        the_file.write(".IC V(n_br_"+str(i)+") = 0 \n")

    the_file.write(".END")
    the_file.close()

    # Come out of top-level directory
    os.chdir("../")

    return (name + "/" + name + ".sp")        


# this is the netlist used to measure mtj discharge process and size its transistor
def generate_mtj_discharge(name, colsize):

    if not os.path.exists(name):
        os.makedirs(name)  
    # Change to directory    
    os.chdir(name)

    # if the column is too big, this bit discharging circuit only works for half of the path
    half = 0
    colsize2 = colsize
    if colsize == 512:
        colsize2 = 256
        half = 1

    # create the spice file and fill it with netlist
    filename = name + ".sp"
    the_file = open(filename, 'w')
    the_file.write(".TITLE bitline discharging process in MTJ-based RAM block\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Include libraries, parameters and other\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".LIB \"../includes.l\" INCLUDES\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Setup and input\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".TRAN 1p 4n SWEEP DATA=sweep_data\n")
    the_file.write(".OPTIONS BRIEF=1\n\n")
    the_file.write("* Input signal\n")
    the_file.write("VIN n_in gnd PULSE (0 supply_v_lp 0 0 0 4n 8n)\n")
    the_file.write("VINb n_in_b gnd PULSE (supply_v_lp 0 0 0 0 4n 8n)\n")


    the_file.write("* Power rail for the circuit under test.\n")
    the_file.write("* This allows us to measure power of a circuit under test without measuring the power of wave shaping and load circuitry.\n")
    the_file.write("V_discharge vdd_discharge gnd supply_v_lp\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Measurement\n")
    the_file.write("********************************************************************************\n\n")


    the_file.write("* Total delays\n")
    the_file.write(".MEASURE TRAN meas_total_tfall TRIG V(n_in) VAL='supply_v_lp/2' RISE=1\n")
    the_file.write("+    TARG V(n_bl_"+str(colsize2)+") VAL='0.01 * supply_v_lp' FALL=1\n")
    #we are only measuring fall, so I just copy it down here for regularity
    the_file.write(".MEASURE TRAN meas_total_trise TRIG V(n_in) VAL='supply_v_lp/2' RISE=1\n")
    the_file.write("+    TARG V(n_bl_"+str(colsize2)+") VAL='0.01 * supply_v_lp' FALL=1\n\n")

    the_file.write(".MEASURE TRAN meas_logic_low_voltage FIND V(gnd) AT=3n\n\n")

    the_file.write("* Measure the power required to propagate a rise and a fall transition through the subcircuit at 250MHz.\n")
    the_file.write(".MEASURE TRAN meas_current INTEGRAL I(V_discharge) FROM=0ns TO=4ns\n")
    if half == 0:
        the_file.write(".MEASURE TRAN meas_avg_power PARAM = '-(meas_current/4n)*supply_v_lp'\n\n")
    else:
        the_file.write(".MEASURE TRAN meas_avg_power PARAM = '-(meas_current/2n)*supply_v_lp'\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Circuit\n")
    the_file.write("********************************************************************************\n\n")  

    #the_file.write("* inv_nand" + str(required_size) + "" + name + " delay\n")
    #MTJ sense amp and precharge
    the_file.write("Xprechargesa n_1_1 gnd vdd_lp gnd n_hang_out vclmpmtj vrefmtj gnd gnd vdd_lp gnd mtj_subcircuits_sa\n")
    #MTJ write driver
    the_file.write("Xwritedriver gnd gnd n_1_1 gnd vdd_lp gnd mtj_subcircuits_writedriver\n")
    #MTJ CS
    the_file.write("Xcs n_1_1 n_bl_0 n_in n_in_b vdd_discharge gnd mtj_subcircuits_cs\n")
    #MTJ cells
    for i in range(0, colsize2):
        the_file.write("Xwire"+str(i)+" n_bl_"+str(i)+" n_bl_"+str(i+1)+" wire Rw=wire_memorycell_vertical_res/"+str(colsize)+" Cw=wire_memorycell_vertical_cap/"+str(colsize)+"\n")
        the_file.write("XMTJ"+str(i)+" gnd gnd n_bl_"+str(i + 1)+" gnd gnd gnd vdd_lp gnd memorycell\n")
        
    #initial conditions

    the_file.write(".IC V(n_1_1) = 0.8 \n")
    for i in range(0, colsize2 + 1):
        the_file.write(".IC V(n_bl_"+str(i)+") = 0.8 \n")


    the_file.write(".END")
    the_file.close()

    # Come out of top-level directory
    os.chdir("../")

    return (name + "/" + name + ".sp")         



# this is the top-level path for the last stage in the configurable decoder
def generate_configurabledecoderiii_top_lp(name, fanin1,fanin2, required_size, tgatecount):

    # Create the directory
    if not os.path.exists(name):
        os.makedirs(name)  
    # Change to directory    
    os.chdir(name)

    # Create the spice file and generate the netlist
    filename = name + ".sp"
    the_file = open(filename, 'w')
    the_file.write(".TITLE last stage of configurable decoder\n\n")


    the_file.write("********************************************************************************\n")
    the_file.write("** Include libraries, parameters and other\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".LIB \"../includes.l\" INCLUDES\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Setup and input\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".TRAN 1p 4n SWEEP DATA=sweep_data\n")
    the_file.write(".OPTIONS BRIEF=1\n\n")
    the_file.write("* Input signal\n")
    the_file.write("VIN n_in gnd PULSE (0 supply_v_lp 0 0 0 2n 4n)\n")

    
    the_file.write("* Power rail for the circuit under test.\n")
    the_file.write("* This allows us to measure power of a circuit under test without measuring the power of wave shaping and load circuitry.\n")
    the_file.write("V_third1 vdd_third1 gnd supply_v_lp\n\n")
    the_file.write("V_third2 vdd_third2 gnd supply_v_lp\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Measurement\n")
    the_file.write("********************************************************************************\n\n")

    if fanin1 !=0:
        the_file.write("* inv_nand" + str(required_size) + "" + name + " delay\n")
        the_file.write(".MEASURE TRAN meaz1_inv_nand" + str(required_size) + "_" + name + "_1_tfall TRIG V(n_1_"+str(fanin1)+") VAL='supply_v_lp/2' RISE=1\n")
        the_file.write("+    TARG V(Xloadnand"+str(fanin1)+".n_1_1) VAL='supply_v_lp/2' FALL=1\n")
        the_file.write(".MEASURE TRAN meaz1_inv_nand" + str(required_size) + "_" + name + "_1_trise TRIG V(n_1_"+str(fanin1)+") VAL='supply_v_lp/2' FALL=1\n")
        the_file.write("+    TARG V(Xloadnand"+str(fanin1)+".n_1_1) VAL='supply_v_lp/2' RISE=1\n\n")

        the_file.write("* inv" + name + "_2 delay\n")
        the_file.write(".MEASURE TRAN meaz1_inv_" + name + "_2_tfall TRIG V(n_1_"+str(fanin1)+") VAL='supply_v_lp/2' FALL=1\n")
        the_file.write("+    TARG V(Xloadnand"+str(fanin1)+".n_out) VAL='supply_v_lp/2' FALL=1\n")
        the_file.write(".MEASURE TRAN meaz1_inv_" + name + "_2_trise TRIG V(n_1_"+str(fanin1)+") VAL='supply_v_lp/2' RISE=1\n")
        the_file.write("+    TARG V(Xloadnand"+str(fanin1)+".n_out) VAL='supply_v_lp/2' RISE=1\n\n")


        the_file.write("* Total delays\n")
        the_file.write(".MEASURE TRAN meaz1_total_tfall TRIG V(n_1_"+str(fanin1)+") VAL='supply_v_lp/2' FALL=1\n")
        the_file.write("+    TARG V(n_1_"+str(fanin1 + tgatecount + 2)+") VAL='supply_v_lp/2' FALL=1\n")
        the_file.write(".MEASURE TRAN meaz1_total_trise TRIG V(n_1_"+str(fanin1)+") VAL='supply_v_lp/2' RISE=1\n")
        the_file.write("+    TARG V(n_1_"+str(fanin1 + tgatecount + 2)+") VAL='supply_v_lp/2' RISE=1\n\n")

        
    if fanin2 !=0:
        the_file.write("* inv_nand" + name + " delay\n")
        the_file.write(".MEASURE TRAN meaz2_inv_nand" + str(required_size) + "_" + name + "_1_tfall TRIG V(n_2_"+str(fanin2)+") VAL='supply_v_lp/2' RISE=1\n")
        the_file.write("+    TARG V(X2loadnand"+str(fanin2)+".n_1_1) VAL='supply_v_lp/2' FALL=1\n")
        the_file.write(".MEASURE TRAN meaz2_inv_nand" + str(required_size) + "_" + name + "_1_trise TRIG V(n_2_"+str(fanin2)+") VAL='supply_v_lp/2' FALL=1\n")
        the_file.write("+    TARG V(X2loadnand"+str(fanin2)+".n_1_1) VAL='supply_v_lp/2' RISE=1\n\n")

        the_file.write("* inv" + name + "_2 delay\n")
        the_file.write(".MEASURE TRAN meaz2_inv_" + name + "_2_tfall TRIG V(n_2_"+str(fanin2)+") VAL='supply_v_lp/2' FALL=1\n")
        the_file.write("+    TARG V(X2loadnand"+str(fanin2)+".n_out) VAL='supply_v_lp/2' FALL=1\n")
        the_file.write(".MEASURE TRAN meaz2_inv_" + name + "_2_trise TRIG V(n_2_"+str(fanin2)+") VAL='supply_v_lp/2' RISE=1\n")
        the_file.write("+    TARG V(X2loadnand"+str(fanin2)+".n_out) VAL='supply_v_lp/2' RISE=1\n\n")


        the_file.write("* Total delays\n")
        the_file.write(".MEASURE TRAN meaz2_total_tfall TRIG V(n_2_"+str(fanin2)+") VAL='supply_v_lp/2' FALL=1\n")
        the_file.write("+    TARG V(n_2_"+str(fanin2 + tgatecount + 2)+") VAL='supply_v_lp/2' FALL=1\n")
        the_file.write(".MEASURE TRAN meaz2_total_trise TRIG V(n_2_"+str(fanin2)+") VAL='supply_v_lp/2' RISE=1\n")
        the_file.write("+    TARG V(n_2_"+str(fanin2 + tgatecount + 2)+") VAL='supply_v_lp/2' RISE=1\n\n")


    the_file.write(".MEASURE TRAN meas_logic_low_voltage FIND V(n_in) AT=3n\n\n")
    if fanin1 != 0:
        the_file.write("* Measure the power required to propagate a rise and a fall transition through the subcircuit at 250MHz.\n")
        the_file.write(".MEASURE TRAN meaz1_current INTEGRAL I(V_third1) FROM=0ns TO=4ns\n")
        the_file.write(".MEASURE TRAN meaz1_avg_power PARAM = '-(meaz1_current/4n)*supply_v_lp'\n\n")
    if fanin2 != 0:
        the_file.write("* Measure the power required to propagate a rise and a fall transition through the subcircuit at 250MHz.\n")
        the_file.write(".MEASURE TRAN meaz2_current INTEGRAL I(V_third2) FROM=0ns TO=4ns\n")
        the_file.write(".MEASURE TRAN meaz2_avg_power PARAM = '-(meaz2_current/4n)*supply_v_lp'\n\n")
    
    the_file.write("********************************************************************************\n")
    the_file.write("** Circuit\n")
    the_file.write("********************************************************************************\n\n")
    if fanin1 !=0:
        the_file.write("Xnandu n_in n_1_0 vdd_lp gnd xconfigurabledecoder3ii\n")
        the_file.write("Xwire0 n_1_0 n_1_1 wire Rw=wire_xconfigurabledecoderi_res/"+str(fanin1)+" Cw=wire_xconfigurabledecoderi_cap/"+str(fanin1)+"\n")
        for i in range(1, fanin1):
            the_file.write("Xloadnand"+str(i)+" n_1_"+str(i)+" n_hang_"+str(i+1)+" vdd_lp gnd xconfigurabledecoderiii\n")
            the_file.write("Xwire"+str(i)+" n_1_"+str(i)+" n_1_"+str(i+1)+" wire Rw=wire_xconfigurabledecoderi_res/"+str(fanin1)+" Cw=wire_xconfigurabledecoderi_cap/"+str(fanin1)+"\n")
        the_file.write("Xloadnand"+str(fanin1)+" n_1_"+str(fanin1)+" n_1_"+str(fanin1 + 1)+" vdd_third1 gnd xconfigurabledecoderiii\n")
        #RAM load:
        the_file.write("Xwireadded n_1_"+str(fanin1 + 1)+" n_1_"+str(fanin1 + 2)+" wire Rw=wire_xconfigurabledecoderiii_res Cw=wire_xconfigurabledecoderiii_cap \n")
        for i in range(fanin1 +2, fanin1 +tgatecount +2):
            the_file.write("Xwirel"+str(i)+" n_1_"+str(i)+" n_1_"+str(i+1)+" wire Rw=wire_memorycell_horizontal_res/"+str(tgatecount)+" Cw=wire_memorycell_horizontal_cap/"+str(tgatecount)+"\n") 
        the_file.write("Xtgate"+str(fanin1 +tgatecount)+" gnd gnd n_1_"+str(fanin1 +tgatecount+2)+" vdd_lp vdd_lp gnd RAM_tgate\n")

    if fanin2 !=0:
        the_file.write("Xnandv n_in n_2_0 vdd_lp gnd xconfigurabledecoder2ii\n")
        the_file.write("X2wire0 n_2_0 n_2_1 wire Rw=wire_xconfigurabledecoderi_res/"+str(fanin2)+" Cw=wire_xconfigurabledecoderi_cap/"+str(fanin2)+"\n")
        for i in range(1, fanin2):
            the_file.write("X2loadnand"+str(i)+" n_2_"+str(i)+" n_hang2_"+str(i+1)+" vdd_lp gnd xconfigurabledecoderiii\n")
            the_file.write("X2wire"+str(i)+" n_2_"+str(i)+" n_2_"+str(i+1)+" wire Rw=wire_xconfigurabledecoderi_res/"+str(fanin2)+" Cw=wire_xconfigurabledecoderi_cap/"+str(fanin2)+"\n")
        the_file.write("X2loadnand"+str(fanin2)+" n_2_"+str(fanin2)+" n_2_"+str(fanin2 + 1)+" vdd_third2 gnd xconfigurabledecoderiii\n")
        #RAM load should be added here
        the_file.write("Xwireadded2 n_2_"+str(fanin2 + 1)+" n_2_"+str(fanin2 + 2)+" wire Rw=wire_xconfigurabledecoderiii_res Cw=wire_xconfigurabledecoderiii_cap \n")
        for i in range(fanin2 +2, fanin2 +tgatecount +2):
            the_file.write("X2wirel"+str(i)+" n_2_"+str(i)+" n_2_"+str(i+1)+" wire Rw=wire_memorycell_horizontal_res/"+str(tgatecount)+" Cw=wire_memorycell_horizontal_cap/"+str(tgatecount)+"\n") 
        the_file.write("X2tgate"+str(fanin2 +tgatecount)+" gnd gnd n_2_"+str(fanin2 +tgatecount+2)+" vdd_lp vdd_lp gnd RAM_tgate\n")
        #the_file.write("X2loadnand3"+str(fanout1 + fanin2)+" n_2_"+str(fanout1 + fanin2)+" n_2_out vdd gnd thirdstage1\n")

    the_file.write(".END")
    the_file.close()

    # Come out of top-level directory
    os.chdir("../")

    return (name + "/" + name + ".sp")   

# Last stage of the row decoder:
def generate_rowdecoderstage3_top_lp(name, fanin1,fanin2, sramcount, number_of_banks, gate_type):


    # Create the dictory:
    if not os.path.exists(name):
        os.makedirs(name)  
    # Change to directory    
    os.chdir(name)


    filename = name + ".sp"
    the_file = open(filename, 'w')
    the_file.write(".TITLE thirdstage\n\n")


    the_file.write("********************************************************************************\n")
    the_file.write("** Include libraries, parameters and other\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".LIB \"../includes.l\" INCLUDES\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Setup and input\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".TRAN 1p 4n SWEEP DATA=sweep_data\n")
    the_file.write(".OPTIONS BRIEF=1\n\n")
    the_file.write("* Input signal\n")
    the_file.write("VIN n_in gnd PULSE (0 supply_v_lp 0 0 0 2n 4n)\n")

    
    the_file.write("* Power rail for the circuit under test.\n")
    the_file.write("* This allows us to measure power of a circuit under test without measuring the power of wave shaping and load circuitry.\n")
    the_file.write("V_third1 vdd_third1 gnd supply_v_lp\n\n")
    the_file.write("V_third2 vdd_third2 gnd supply_v_lp\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Measurement\n")
    the_file.write("********************************************************************************\n\n")

    if fanin1 !=0:
        the_file.write("* inv_nand" + name + " delay\n")
        the_file.write(".MEASURE TRAN meaz1_inv_nand"+str(gate_type)+"_" + name + "_1_tfall TRIG V(n_1_1) VAL='supply_v_lp/2' RISE=1\n")
        the_file.write("+    TARG V(Xloadnand"+str(fanin1)+".n_1_1) VAL='supply_v_lp/2' FALL=1\n")
        the_file.write(".MEASURE TRAN meaz1_inv_nand"+str(gate_type)+"_" + name + "_1_trise TRIG V(n_1_1) VAL='supply_v_lp/2' FALL=1\n")
        the_file.write("+    TARG V(Xloadnand"+str(fanin1)+".n_1_1) VAL='supply_v_lp/2' RISE=1\n\n")


        the_file.write("* inv" + name + "_2 delay\n")
        the_file.write(".MEASURE TRAN meaz1_inv_" + name + "_2_tfall TRIG V(n_1_1) VAL='supply_v_lp/2' FALL=1\n")
        the_file.write("+    TARG V(Xloadnand"+str(fanin1)+".n_out) VAL='supply_v_lp/2' FALL=1\n")
        the_file.write(".MEASURE TRAN meaz1_inv_" + name + "_2_trise TRIG V(n_1_1) VAL='supply_v_lp/2' RISE=1\n")
        the_file.write("+    TARG V(Xloadnand"+str(fanin1)+".n_out) VAL='supply_v_lp/2' RISE=1\n\n")

        the_file.write("* Total delays\n")
        the_file.write(".MEASURE TRAN meaz1_total_tfall TRIG V(n_1_1) VAL='supply_v_lp/2' FALL=1\n")
        the_file.write("+    TARG V(Xloadnand"+str(fanin1)+".n_out) VAL='supply_v_lp/2' FALL=1\n")
        the_file.write(".MEASURE TRAN meaz1_total_trise TRIG V(n_1_1) VAL='supply_v_lp/2' RISE=1\n")
        the_file.write("+    TARG V(Xloadnand"+str(fanin1)+".n_out) VAL='supply_v_lp/2' RISE=1\n\n")

        
    if fanin2 !=0:
        the_file.write("* inv_nand" + name + " delay\n")
        the_file.write(".MEASURE TRAN meaz2_inv_nand"+str(gate_type)+"_" + name + "_1_tfall TRIG V(n_2_"+str(fanin2)+") VAL='supply_v_lp/2' RISE=1\n")
        the_file.write("+    TARG V(X2loadnand"+str(fanin2)+".n_1_1) VAL='supply_v_lp/2' FALL=1\n")
        the_file.write(".MEASURE TRAN meaz2_inv_nand"+str(gate_type)+"_" + name + "_1_trise TRIG V(n_2_"+str(fanin2)+") VAL='supply_v_lp/2' FALL=1\n")
        the_file.write("+    TARG V(X2loadnand"+str(fanin2)+".n_1_1) VAL='supply_v_lp/2' RISE=1\n\n")

        the_file.write("* inv" + name + "_2 delay\n")
        the_file.write(".MEASURE TRAN meaz2_inv_" + name + "_2_tfall TRIG V(n_2_"+str(fanin2)+") VAL='supply_v_lp/2' FALL=1\n")
        the_file.write("+    TARG V(X2loadnand"+str(fanin2)+".n_out) VAL='supply_v_lp/2' FALL=1\n")
        the_file.write(".MEASURE TRAN meaz2_inv_" + name + "_2_trise TRIG V(n_2_"+str(fanin2)+") VAL='supply_v_lp/2' RISE=1\n")
        the_file.write("+    TARG V(X2loadnand"+str(fanin2)+".n_out) VAL='supply_v_lp/2' RISE=1\n\n")


        the_file.write("* Total delays\n")
        the_file.write(".MEASURE TRAN meaz2_total_tfall TRIG V(n_2_"+str(fanin2)+") VAL='supply_v_lp/2' FALL=1\n")
        the_file.write("+    TARG V(X2loadnand"+str(fanin2)+".n_out) VAL='supply_v_lp/2' FALL=1\n")
        the_file.write(".MEASURE TRAN meaz2_total_trise TRIG V(n_2_"+str(fanin2)+") VAL='supply_v_lp/2' RISE=1\n")
        the_file.write("+    TARG V(X2loadnand"+str(fanin2)+".n_out) VAL='supply_v_lp/2' RISE=1\n\n")


    the_file.write(".MEASURE TRAN meas_logic_low_voltage FIND V(n_in) AT=3n\n\n")
    if fanin1 != 0:
        the_file.write("* Measure the power required to propagate a rise and a fall transition through the subcircuit at 250MHz.\n")
        the_file.write(".MEASURE TRAN meaz1_current INTEGRAL I(V_third1) FROM=0ns TO=4ns\n")
        the_file.write(".MEASURE TRAN meaz1_avg_power PARAM = '-(meaz1_current/4n)*supply_v_lp'\n\n")
    if fanin2 != 0:
        the_file.write("* Measure the power required to propagate a rise and a fall transition through the subcircuit at 250MHz.\n")
        the_file.write(".MEASURE TRAN meaz2_current INTEGRAL I(V_third2) FROM=0ns TO=4ns\n")
        the_file.write(".MEASURE TRAN meaz2_avg_power PARAM = '-(meaz2_current/4n)*supply_v_lp'\n\n")
    
    the_file.write("********************************************************************************\n")
    the_file.write("** Circuit\n")
    the_file.write("********************************************************************************\n\n")
    if fanin1 !=0:
        the_file.write("Xnandu n_in n_1_1 vdd_lp gnd rowdecoderstage12\n")
        for i in range(1, fanin1):
            the_file.write("Xloadnand"+str(i)+" n_1_"+str(i)+" n_hang_"+str(i+1)+" vdd_lp gnd rowdecoderstage3\n")
            the_file.write("Xwire"+str(i)+" n_1_"+str(i)+" n_1_"+str(i+1)+" wire Rw=wire_rowdecoderstage0_res/"+str(fanin1)+" Cw=wire_rowdecoderstage0_cap/"+str(fanin1)+"\n")
        the_file.write("Xloadnand"+str(fanin1)+" n_1_"+str(fanin1)+" n_1_"+str(fanin1 + 1)+" vdd_third1 gnd rowdecoderstage3\n")
        the_file.write("Xwordline n_1_"+str(fanin1 + 1)+" n_1_"+str(fanin1 + 2)+" vdd_lp gnd wordline_driver\n")


    if fanin2 !=0:
        the_file.write("Xnandv n_in n_2_1 vdd_lp gnd rowdecoderstage13\n")
        for i in range(1, fanin2):
            the_file.write("X2loadnand"+str(i)+" n_2_"+str(i)+" n_hang2_"+str(i+1)+" vdd_lp gnd rowdecoderstage3\n")
            the_file.write("X2wire"+str(i)+" n_2_"+str(i)+" n_2_"+str(i+1)+" wire Rw=wire_rowdecoderstage0_res/"+str(fanin2)+" Cw=wire_rowdecoderstage0_cap/"+str(fanin2)+"\n")
        the_file.write("X2loadnand"+str(fanin2)+" n_2_"+str(fanin2)+" n_2_"+str(fanin2 + 1)+" vdd_third2 gnd rowdecoderstage3\n")
        the_file.write("X2wordline n_2_"+str(fanin2 + 1)+" n_2_"+str(fanin2 + 2)+" vdd_lp gnd wordline_driver\n")


    the_file.write(".END")
    the_file.close()

    # Come out of top-level directory
    os.chdir("../")

    return (name + "/" + name + ".sp")


# This is the wordline driver:
def generate_wordline_driver_top_lp(name, sramcount, nandsize, smallrow, repeater):

    # Create the directory
    if not os.path.exists(name):
        os.makedirs(name)  
    # Change to directory    
    os.chdir(name)

    # Create the spice file and generate the netlist
    filename = name + ".sp"
    the_file = open(filename, 'w')
    the_file.write(".TITLE wordline driver\n\n")


    the_file.write("********************************************************************************\n")
    the_file.write("** Include libraries, parameters and other\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".LIB \"../includes.l\" INCLUDES\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Setup and input\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".TRAN 1p 4n SWEEP DATA=sweep_data\n")
    the_file.write(".OPTIONS BRIEF=1\n\n")
    the_file.write("* Input signal\n")
    the_file.write("VIN n_in gnd PULSE (0 supply_v_lp 0 0 0 2n 4n)\n")

    
    the_file.write("* Power rail for the circuit under test.\n")
    the_file.write("* This allows us to measure power of a circuit under test without measuring the power of wave shaping and load circuitry.\n")
    the_file.write("V_wordline vdd_wordline gnd supply_v_lp\n\n")


    the_file.write("********************************************************************************\n")
    the_file.write("** Measurement\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write("* inv_" + name + " delay\n")
    the_file.write(".MEASURE TRAN meas_inv_nand"+str(nandsize)+"_wordline_driver_1_tfall TRIG V(n_1_1) VAL='supply_v_lp/2' RISE=1\n")
    the_file.write("+    TARG V(Xwordline.n_1_1) VAL='supply_v_lp/2' FALL=1\n")
    the_file.write(".MEASURE TRAN meas_inv_nand"+str(nandsize)+"_wordline_driver_1_trise TRIG V(n_1_1) VAL='supply_v_lp/2' FALL=1\n")
    the_file.write("+    TARG V(Xwordline.n_1_1) VAL='supply_v_lp/2' RISE=1\n\n")

    the_file.write("* inv_" + name + " delay\n")
    the_file.write(".MEASURE TRAN meas_inv_wordline_driver_2_tfall TRIG V(n_1_1) VAL='supply_v_lp/2' FALL=1\n")
    the_file.write("+    TARG V(Xwordline.n_1_2) VAL='supply_v_lp/2' FALL=1\n")
    the_file.write(".MEASURE TRAN meas_inv_wordline_driver_2_trise TRIG V(n_1_1) VAL='supply_v_lp/2' RISE=1\n")
    the_file.write("+    TARG V(Xwordline.n_1_2) VAL='supply_v_lp/2' RISE=1\n\n")

    the_file.write("* inv_" + name + " delay\n")
    the_file.write(".MEASURE TRAN meas_inv_wordline_driver_3_tfall TRIG V(n_1_1) VAL='supply_v_lp/2' RISE=1\n")
    the_file.write("+    TARG V(Xwordline.n_1_3) VAL='supply_v_lp/2' FALL=1\n")
    the_file.write(".MEASURE TRAN meas_inv_wordline_driver_3_trise TRIG V(n_1_1) VAL='supply_v_lp/2' FALL=1\n")
    the_file.write("+    TARG V(Xwordline.n_1_3) VAL='supply_v_lp/2' RISE=1\n\n")

    the_file.write("* inv_" + name + " delay\n")
    the_file.write(".MEASURE TRAN meas_inv_wordline_driver_4_tfall TRIG V(n_1_1) VAL='supply_v_lp/2' FALL=1\n")
    the_file.write("+    TARG V(n_1_"+str(sramcount+1)+") VAL='supply_v_lp * 0.1' FALL=1\n")
    the_file.write(".MEASURE TRAN meas_inv_wordline_driver_4_trise TRIG V(n_1_1) VAL='supply_v_lp/2' RISE=1\n")
    the_file.write("+    TARG V(n_1_"+str(sramcount+1)+") VAL='supply_v_lp * 0.9' RISE=1\n\n")

    the_file.write("* Total delays\n")
    the_file.write(".MEASURE TRAN meaz1_total_tfall TRIG V(n_1_1) VAL='supply_v_lp/2' FALL=1\n")
    the_file.write("+    TARG V(n_1_"+str(sramcount+1)+") VAL='supply_v_lp * 0.1' FALL=1\n")
    the_file.write(".MEASURE TRAN meaz1_total_trise TRIG V(n_1_1) VAL='supply_v_lp/2' RISE=1\n")
    the_file.write("+    TARG V(n_1_"+str(sramcount+1)+") VAL='supply_v_lp * 0.9' RISE=1\n\n")


    the_file.write(".MEASURE TRAN meas_logic_low_voltage FIND V(n_in) AT=3n\n\n")

    the_file.write("* Measure the power required to propagate a rise and a fall transition through the subcircuit at 250MHz.\n")
    the_file.write(".MEASURE TRAN meas_current INTEGRAL I(V_wordline) FROM=0ns TO=4ns\n")
    the_file.write(".MEASURE TRAN meas_avg_power PARAM = '-(meas_current/4n)*supply_v_lp'\n\n")

    
    the_file.write("********************************************************************************\n")
    the_file.write("** Circuit\n")
    the_file.write("********************************************************************************\n\n")
    
    #last stage of row decoder:
    the_file.write("Xnandu n_in n_1_1 vdd_lp gnd rowdecoderstage3\n")
    #Wordline driver:
    the_file.write("Xwordline n_1_1 n_1_2 vdd_wordline gnd wordline_driver\n")
    #RAM load:
    for i in range(2, int(sramcount +2)):
        the_file.write("Xmemcell"+str(i)+" n_1_"+str(i)+" gnd gnd gnd gnd gnd vdd_lp gnd memorycell\n")
        if repeater == 0:
            the_file.write("Xwirel"+str(i)+" n_1_"+str(i)+" n_1_"+str(i+1)+" wire Rw=wire_wordline_driver_res/"+str(sramcount)+" Cw=wire_wordline_driver_cap/"+str(sramcount)+"\n")
        else:
            the_file.write("Xwirel"+str(i)+" n_1_"+str(i)+" n_1_"+str(i+1)+" wire Rw=wire_wordline_driver_res/"+str(2*sramcount)+" Cw=wire_wordline_driver_cap/"+str(2*sramcount)+"\n")

    the_file.write(".END")
    the_file.close()

    # Come out of top-level directory
    os.chdir("../")

    return (name + "/" + name + ".sp")


# This is the last stage of the row decoder:
def generate_rowdecoderstage3_top(name, fanin1,fanin2, sramcount, number_of_banks, gate_type):

    # Create the dictory:
    if not os.path.exists(name):
        os.makedirs(name)  
    # Change to directory    
    os.chdir(name)

    # Create spice file and fill it up with the netlist:
    filename = name + ".sp"
    the_file = open(filename, 'w')
    the_file.write(".TITLE thirdstage\n\n")


    the_file.write("********************************************************************************\n")
    the_file.write("** Include libraries, parameters and other\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".LIB \"../includes.l\" INCLUDES\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Setup and input\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".TRAN 1p 4n SWEEP DATA=sweep_data\n")
    the_file.write(".OPTIONS BRIEF=1\n\n")
    the_file.write("* Input signal\n")
    the_file.write("VIN n_in gnd PULSE (0 supply_v 0 0 0 2n 4n)\n")

    
    the_file.write("* Power rail for the circuit under test.\n")
    the_file.write("* This allows us to measure power of a circuit under test without measuring the power of wave shaping and load circuitry.\n")
    the_file.write("V_third1 vdd_third1 gnd supply_v\n\n")
    the_file.write("V_third2 vdd_third2 gnd supply_v\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Measurement\n")
    the_file.write("********************************************************************************\n\n")

    if fanin1 !=0:
        the_file.write("* inv_nand" + name + " delay\n")
        the_file.write(".MEASURE TRAN meaz1_inv_nand"+str(gate_type)+"_" + name + "_1_tfall TRIG V(n_1_1) VAL='supply_v/2' RISE=1\n")
        the_file.write("+    TARG V(Xloadnand"+str(fanin1)+".n_1_1) VAL='supply_v/2' FALL=1\n")
        the_file.write(".MEASURE TRAN meaz1_inv_nand"+str(gate_type)+"_" + name + "_1_trise TRIG V(n_1_1) VAL='supply_v/2' FALL=1\n")
        the_file.write("+    TARG V(Xloadnand"+str(fanin1)+".n_1_1) VAL='supply_v/2' RISE=1\n\n")


        the_file.write("* inv" + name + "_2 delay\n")
        the_file.write(".MEASURE TRAN meaz1_inv_" + name + "_2_tfall TRIG V(n_1_1) VAL='supply_v/2' FALL=1\n")
        the_file.write("+    TARG V(Xloadnand"+str(fanin1)+".n_out) VAL='supply_v/2' FALL=1\n")
        the_file.write(".MEASURE TRAN meaz1_inv_" + name + "_2_trise TRIG V(n_1_1) VAL='supply_v/2' RISE=1\n")
        the_file.write("+    TARG V(Xloadnand"+str(fanin1)+".n_out) VAL='supply_v/2' RISE=1\n\n")

        the_file.write("* Total delays\n")
        the_file.write(".MEASURE TRAN meaz1_total_tfall TRIG V(n_1_1) VAL='supply_v/2' FALL=1\n")
        the_file.write("+    TARG V(Xloadnand"+str(fanin1)+".n_out) VAL='supply_v/2' FALL=1\n")
        the_file.write(".MEASURE TRAN meaz1_total_trise TRIG V(n_1_1) VAL='supply_v/2' RISE=1\n")
        the_file.write("+    TARG V(Xloadnand"+str(fanin1)+".n_out) VAL='supply_v/2' RISE=1\n\n")

        
    if fanin2 !=0:
        the_file.write("* inv_nand" + name + " delay\n")
        the_file.write(".MEASURE TRAN meaz2_inv_nand"+str(gate_type)+"_" + name + "_1_tfall TRIG V(n_2_"+str(fanin2)+") VAL='supply_v/2' RISE=1\n")
        the_file.write("+    TARG V(X2loadnand"+str(fanin2)+".n_1_1) VAL='supply_v/2' FALL=1\n")
        the_file.write(".MEASURE TRAN meaz2_inv_nand"+str(gate_type)+"_" + name + "_1_trise TRIG V(n_2_"+str(fanin2)+") VAL='supply_v/2' FALL=1\n")
        the_file.write("+    TARG V(X2loadnand"+str(fanin2)+".n_1_1) VAL='supply_v/2' RISE=1\n\n")

        the_file.write("* inv" + name + "_2 delay\n")
        the_file.write(".MEASURE TRAN meaz2_inv_" + name + "_2_tfall TRIG V(n_2_"+str(fanin2)+") VAL='supply_v/2' FALL=1\n")
        the_file.write("+    TARG V(X2loadnand"+str(fanin2)+".n_out) VAL='supply_v/2' FALL=1\n")
        the_file.write(".MEASURE TRAN meaz2_inv_" + name + "_2_trise TRIG V(n_2_"+str(fanin2)+") VAL='supply_v/2' RISE=1\n")
        the_file.write("+    TARG V(X2loadnand"+str(fanin2)+".n_out) VAL='supply_v/2' RISE=1\n\n")


        the_file.write("* Total delays\n")
        the_file.write(".MEASURE TRAN meaz2_total_tfall TRIG V(n_2_"+str(fanin2)+") VAL='supply_v/2' FALL=1\n")
        the_file.write("+    TARG V(X2loadnand"+str(fanin2)+".n_out) VAL='supply_v/2' FALL=1\n")
        the_file.write(".MEASURE TRAN meaz2_total_trise TRIG V(n_2_"+str(fanin2)+") VAL='supply_v/2' RISE=1\n")
        the_file.write("+    TARG V(X2loadnand"+str(fanin2)+".n_out) VAL='supply_v/2' RISE=1\n\n")


    the_file.write(".MEASURE TRAN meas_logic_low_voltage FIND V(n_in) AT=3n\n\n")
    if fanin1 != 0:
        the_file.write("* Measure the power required to propagate a rise and a fall transition through the subcircuit at 250MHz.\n")
        the_file.write(".MEASURE TRAN meaz1_current INTEGRAL I(V_third1) FROM=0ns TO=4ns\n")
        the_file.write(".MEASURE TRAN meaz1_avg_power PARAM = '-(meaz1_current/4n)*supply_v'\n\n")
    if fanin2 != 0:
        the_file.write("* Measure the power required to propagate a rise and a fall transition through the subcircuit at 250MHz.\n")
        the_file.write(".MEASURE TRAN meaz2_current INTEGRAL I(V_third2) FROM=0ns TO=4ns\n")
        the_file.write(".MEASURE TRAN meaz2_avg_power PARAM = '-(meaz2_current/4n)*supply_v'\n\n")
    
    the_file.write("********************************************************************************\n")
    the_file.write("** Circuit\n")
    the_file.write("********************************************************************************\n\n")
    if fanin1 !=0:
        the_file.write("Xnandu n_in n_1_1 vdd gnd rowdecoderstage12\n")
        for i in range(1, fanin1):
            the_file.write("Xloadnand"+str(i)+" n_1_"+str(i)+" n_hang_"+str(i+1)+" vdd gnd rowdecoderstage3\n")
            the_file.write("Xwire"+str(i)+" n_1_"+str(i)+" n_1_"+str(i+1)+" wire Rw=wire_rowdecoderstage0_res/"+str(fanin1)+" Cw=wire_rowdecoderstage0_cap/"+str(fanin1)+"\n")
        the_file.write("Xloadnand"+str(fanin1)+" n_1_"+str(fanin1)+" n_1_"+str(fanin1 + 1)+" vdd_third1 gnd rowdecoderstage3\n")
        the_file.write("Xwordline n_1_"+str(fanin1 + 1)+" n_1_"+str(fanin1 + 2)+" vdd gnd wordline_driver\n")


    if fanin2 !=0:
        the_file.write("Xnandv n_in n_2_1 vdd gnd rowdecoderstage13\n")
        for i in range(1, fanin2):
            the_file.write("X2loadnand"+str(i)+" n_2_"+str(i)+" n_hang2_"+str(i+1)+" vdd gnd rowdecoderstage3\n")
            the_file.write("X2wire"+str(i)+" n_2_"+str(i)+" n_2_"+str(i+1)+" wire Rw=wire_rowdecoderstage0_res/"+str(fanin2)+" Cw=wire_rowdecoderstage0_cap/"+str(fanin2)+"\n")
        the_file.write("X2loadnand"+str(fanin2)+" n_2_"+str(fanin2)+" n_2_"+str(fanin2 + 1)+" vdd_third2 gnd rowdecoderstage3\n")
        the_file.write("X2wordline n_2_"+str(fanin2 + 1)+" n_2_"+str(fanin2 + 2)+" vdd gnd wordline_driver\n")


    the_file.write(".END")
    the_file.close()

    # Come out of top-level directory
    os.chdir("../")

    return (name + "/" + name + ".sp")

# This is the first stage of the row decoder:
def generate_rowdecoderstage1_top(name, fanout, size):

    # Create directories
    if not os.path.exists(name):
        os.makedirs(name)  
    # Change to directory    
    os.chdir(name)

    # Create the spice file and generate netlist:
    filename = name + ".sp"
    the_file = open(filename, 'w')
    the_file.write(".TITLE stage one of the small row decoder\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Include libraries, parameters and other\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".LIB \"../includes.l\" INCLUDES\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Setup and input\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".TRAN 1p 4n SWEEP DATA=sweep_data\n")
    the_file.write(".OPTIONS BRIEF=1\n\n")
    the_file.write("* Input signal\n")
    the_file.write("VIN n_in gnd PULSE (0 supply_v 0 0 0 2n 4n)\n")
    
    the_file.write("* Power rail for the circuit under test.\n")
    the_file.write("* This allows us to measure power of a circuit under test without measuring the power of wave shaping and load circuitry.\n")
    the_file.write("V_sec vdd_sec gnd supply_v\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Measurement\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write("* inv_nand2" + name + " delay\n")
    the_file.write(".MEASURE TRAN meas_inv_nand" + str(size) + "_" + name + "_1_tfall TRIG V(n_1_1) VAL='supply_v/2' RISE=1\n")
    the_file.write("+    TARG V(Xsec.n_1_1) VAL='supply_v/2' FALL=1\n")
    the_file.write(".MEASURE TRAN meas_inv_nand" + str(size) + "_" + name + "_1_trise TRIG V(n_1_1) VAL='supply_v/2' FALL=1\n")
    the_file.write("+    TARG V(Xsec.n_1_1) VAL='supply_v/2' RISE=1\n\n")

    the_file.write("* inv_" + name + " delay\n")
    the_file.write(".MEASURE TRAN meas_inv_" + name + "_2_tfall TRIG V(n_1_1) VAL='supply_v/2' FALL=1\n")
    the_file.write("+    TARG V(n_1_"+str(1+fanout)+") VAL='supply_v/2' FALL=1\n")
    the_file.write(".MEASURE TRAN meas_inv_" + name + "_2_trise TRIG V(n_1_1) VAL='supply_v/2' RISE=1\n")
    the_file.write("+    TARG V(n_1_"+str(1+fanout)+") VAL='supply_v/2' RISE=1\n\n")

    the_file.write("* Total delays\n")
    the_file.write(".MEASURE TRAN meas_total_tfall TRIG V(n_1_1) VAL='supply_v/2' FALL=1\n")
    the_file.write("+    TARG V(n_1_"+str(1+fanout)+") VAL='supply_v/2' FALL=1\n")
    the_file.write(".MEASURE TRAN meas_total_trise TRIG V(n_1_1) VAL='supply_v/2' RISE=1\n")
    the_file.write("+    TARG V(n_1_"+str(1+fanout)+") VAL='supply_v/2' RISE=1\n\n")

    the_file.write(".MEASURE TRAN meas_logic_low_voltage FIND V(n_in) AT=3n\n\n")

    the_file.write("* Measure the power required to propagate a rise and a fall transition through the subcircuit at 250MHz.\n")
    the_file.write(".MEASURE TRAN meas_current INTEGRAL I(V_sec) FROM=0ns TO=4ns\n")
    the_file.write(".MEASURE TRAN meas_avg_power PARAM = '-(meas_current/4n)*supply_v'\n\n")
    
    the_file.write("********************************************************************************\n")
    the_file.write("** Circuit\n")
    the_file.write("********************************************************************************\n\n")
    # wave shaping circuitry
    the_file.write("Xrowstage0 n_in n_1_1 vdd gnd rowdecoderstage0\n")
    #add the nand2 circuit here
    the_file.write("Xsec n_1_1 n_1_2 vdd_sec gnd "+ name +"\n")
    #the load to this circuit:

    for i in range(2, 2+fanout):
        the_file.write("Xwire"+str(i)+" n_1_"+str(i)+" n_1_"+str(i+1)+" wire Rw=wire_rowdecoderstage0_res/"+str(fanout)+" Cw=wire_rowdecoderstage0_cap/"+str(fanout)+"\n")
        the_file.write("Xloadnand"+str(i)+" n_1_"+str(i)+" n_hang_"+str(i+1)+" vdd gnd rowdecoderstage3\n")

    the_file.write(".END")
    the_file.close()

    # Come out of top-level directory
    os.chdir("../")

    return (name + "/" + name + ".sp")



# This is the first stage of row decoder using low power transistors:
def generate_rowdecoderstage1_top_lp(name, fanout, size):

    # Create directories
    if not os.path.exists(name):
        os.makedirs(name)  
    # Change to directory    
    os.chdir(name)

    # Create the spice file:
    filename = name + ".sp"
    the_file = open(filename, 'w')
    the_file.write(".TITLE stage one of the small row decoder\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Include libraries, parameters and other\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".LIB \"../includes.l\" INCLUDES\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Setup and input\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".TRAN 1p 4n SWEEP DATA=sweep_data\n")
    the_file.write(".OPTIONS BRIEF=1\n\n")
    the_file.write("* Input signal\n")
    the_file.write("VIN n_in gnd PULSE (0 supply_v_lp 0 0 0 2n 4n)\n")
    
    the_file.write("* Power rail for the circuit under test.\n")
    the_file.write("* This allows us to measure power of a circuit under test without measuring the power of wave shaping and load circuitry.\n")
    the_file.write("V_sec vdd_sec gnd supply_v_lp\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Measurement\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write("* inv_nand2" + name + " delay\n")
    the_file.write(".MEASURE TRAN meas_inv_nand" + str(size) + "_" + name + "_1_tfall TRIG V(n_1_1) VAL='supply_v_lp/2' RISE=1\n")
    the_file.write("+    TARG V(Xsec.n_1_1) VAL='supply_v_lp/2' FALL=1\n")
    the_file.write(".MEASURE TRAN meas_inv_nand" + str(size) + "_" + name + "_1_trise TRIG V(n_1_1) VAL='supply_v_lp/2' FALL=1\n")
    the_file.write("+    TARG V(Xsec.n_1_1) VAL='supply_v_lp/2' RISE=1\n\n")

    the_file.write("* inv_" + name + " delay\n")
    the_file.write(".MEASURE TRAN meas_inv_" + name + "_2_tfall TRIG V(n_1_1) VAL='supply_v_lp/2' FALL=1\n")
    the_file.write("+    TARG V(n_1_"+str(1+fanout)+") VAL='supply_v_lp/2' FALL=1\n")
    the_file.write(".MEASURE TRAN meas_inv_" + name + "_2_trise TRIG V(n_1_1) VAL='supply_v_lp/2' RISE=1\n")
    the_file.write("+    TARG V(n_1_"+str(1+fanout)+") VAL='supply_v_lp/2' RISE=1\n\n")

    the_file.write("* Total delays\n")
    the_file.write(".MEASURE TRAN meas_total_tfall TRIG V(n_1_1) VAL='supply_v_lp/2' FALL=1\n")
    the_file.write("+    TARG V(n_1_"+str(1+fanout)+") VAL='supply_v_lp/2' FALL=1\n")
    the_file.write(".MEASURE TRAN meas_total_trise TRIG V(n_1_1) VAL='supply_v_lp/2' RISE=1\n")
    the_file.write("+    TARG V(n_1_"+str(1+fanout)+") VAL='supply_v_lp/2' RISE=1\n\n")

    the_file.write(".MEASURE TRAN meas_logic_low_voltage FIND V(n_in) AT=3n\n\n")

    the_file.write("* Measure the power required to propagate a rise and a fall transition through the subcircuit at 250MHz.\n")
    the_file.write(".MEASURE TRAN meas_current INTEGRAL I(V_sec) FROM=0ns TO=4ns\n")
    the_file.write(".MEASURE TRAN meas_avg_power PARAM = '-(meas_current/4n)*supply_v_lp'\n\n")
    
    the_file.write("********************************************************************************\n")
    the_file.write("** Circuit\n")
    the_file.write("********************************************************************************\n\n")
    # wave shaping circuitry
    the_file.write("Xrowstage0 n_in n_1_1 vdd_lp gnd rowdecoderstage0\n")

    #add the nand2 circuit here
    the_file.write("Xsec n_1_1 n_1_2 vdd_sec gnd "+ name +"\n")
    #the load to this circuit:
    for i in range(2, 2+fanout):
        the_file.write("Xwire"+str(i)+" n_1_"+str(i)+" n_1_"+str(i+1)+" wire Rw=wire_rowdecoderstage0_res/"+str(fanout)+" Cw=wire_rowdecoderstage0_cap/"+str(fanout)+"\n")
        the_file.write("Xloadnand"+str(i)+" n_1_"+str(i)+" n_hang_"+str(i+1)+" vdd_lp gnd rowdecoderstage3\n")

    the_file.write(".END")
    the_file.close()

    # Come out of top-level directory
    os.chdir("../")

    return (name + "/" + name + ".sp")


# This is the top-level path for the second stage in the configurable decoder:
def generate_configurabledecoder2ii_top(name, fanout, size):

    # Create directories
    if not os.path.exists(name):
        os.makedirs(name)  
    # Change to directory    
    os.chdir(name)

    # create the file and 
    filename = name + ".sp"
    the_file = open(filename, 'w')
    the_file.write(".TITLE second stage in configurable decoder\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Include libraries, parameters and other\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".LIB \"../includes.l\" INCLUDES\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Setup and input\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".TRAN 1p 4n SWEEP DATA=sweep_data\n")
    the_file.write(".OPTIONS BRIEF=1\n\n")
    the_file.write("* Input signal\n")
    the_file.write("VIN n_in gnd PULSE (0 supply_v 0 0 0 2n 4n)\n")
    
    the_file.write("* Power rail for the circuit under test.\n")
    the_file.write("* This allows us to measure power of a circuit under test without measuring the power of wave shaping and load circuitry.\n")
    the_file.write("V_sec vdd_sec gnd supply_v\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Measurement\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write("* inv_nand2" + name + " delay\n")
    the_file.write(".MEASURE TRAN meas_inv_nand" + str(size) + "_" + name + "_1_tfall TRIG V(n_1_1) VAL='supply_v/2' RISE=1\n")
    the_file.write("+    TARG V(Xsec.n_1_1) VAL='supply_v/2' FALL=1\n")
    the_file.write(".MEASURE TRAN meas_inv_nand" + str(size) + "_" + name + "_1_trise TRIG V(n_1_1) VAL='supply_v/2' FALL=1\n")
    the_file.write("+    TARG V(Xsec.n_1_1) VAL='supply_v/2' RISE=1\n\n")

    the_file.write("* inv_" + name + " delay\n")
    the_file.write(".MEASURE TRAN meas_inv_" + name + "_2_tfall TRIG V(n_1_1) VAL='supply_v/2' FALL=1\n")
    the_file.write("+    TARG V(n_1_"+str(1+fanout)+") VAL='supply_v/2' FALL=1\n")
    the_file.write(".MEASURE TRAN meas_inv_" + name + "_2_trise TRIG V(n_1_1) VAL='supply_v/2' RISE=1\n")
    the_file.write("+    TARG V(n_1_"+str(1+fanout)+") VAL='supply_v/2' RISE=1\n\n")

    the_file.write("* Total delays\n")
    the_file.write(".MEASURE TRAN meas_total_tfall TRIG V(n_1_1) VAL='supply_v/2' FALL=1\n")
    the_file.write("+    TARG V(n_1_"+str(1+fanout)+") VAL='supply_v/2' FALL=1\n")
    the_file.write(".MEASURE TRAN meas_total_trise TRIG V(n_1_1) VAL='supply_v/2' RISE=1\n")
    the_file.write("+    TARG V(n_1_"+str(1+fanout)+") VAL='supply_v/2' RISE=1\n\n")

    the_file.write(".MEASURE TRAN meas_logic_low_voltage FIND V(n_in) AT=3n\n\n")

    the_file.write("* Measure the power required to propagate a rise and a fall transition through the subcircuit at 250MHz.\n")
    the_file.write(".MEASURE TRAN meas_current INTEGRAL I(V_sec) FROM=0ns TO=4ns\n")
    the_file.write(".MEASURE TRAN meas_avg_power PARAM = '-(meas_current/4n)*supply_v'\n\n")
    
    the_file.write("********************************************************************************\n")
    the_file.write("** Circuit\n")
    the_file.write("********************************************************************************\n\n")
    # wave shaping circuitry
    the_file.write("xconfigurabledecoderi n_in n_1_1 vdd gnd xconfigurabledecoderi\n")

    #add the nand2 circuit here
    the_file.write("Xsec n_1_1 n_1_2 vdd_sec gnd "+ name +"\n")
    #the load to this circuit:

    for i in range(2, 2+fanout):
        the_file.write("Xwire"+str(i)+" n_1_"+str(i)+" n_1_"+str(i+1)+" wire Rw=wire_xconfigurabledecoderi_res/"+str(fanout)+" Cw=wire_xconfigurabledecoderi_cap/"+str(fanout)+"\n")
        the_file.write("Xloadnand"+str(i)+" n_1_"+str(i)+" n_hang_"+str(i+1)+" vdd gnd xconfigurabledecoderiii\n")

    the_file.write(".END")
    the_file.close()

    # Come out of top-level directory
    os.chdir("../")

    return (name + "/" + name + ".sp")


# This is the top-level path for the second stage of the configurable decoder::
def generate_configurabledecoder2ii_top_lp(name, fanout, size):

    # Create directories
    if not os.path.exists(name):
        os.makedirs(name)  
    # Change to directory    
    os.chdir(name)


    filename = name + ".sp"
    the_file = open(filename, 'w')
    the_file.write(".TITLE second stage in configurable decoder\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Include libraries, parameters and other\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".LIB \"../includes.l\" INCLUDES\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Setup and input\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".TRAN 1p 4n SWEEP DATA=sweep_data\n")
    the_file.write(".OPTIONS BRIEF=1\n\n")
    the_file.write("* Input signal\n")
    the_file.write("VIN n_in gnd PULSE (0 supply_v_lp 0 0 0 2n 4n)\n")
    
    the_file.write("* Power rail for the circuit under test.\n")
    the_file.write("* This allows us to measure power of a circuit under test without measuring the power of wave shaping and load circuitry.\n")
    the_file.write("V_sec vdd_sec gnd supply_v_lp\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Measurement\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write("* inv_nand2" + name + " delay\n")
    the_file.write(".MEASURE TRAN meas_inv_nand" + str(size) + "_" + name + "_1_tfall TRIG V(n_1_1) VAL='supply_v_lp/2' RISE=1\n")
    the_file.write("+    TARG V(Xsec.n_1_1) VAL='supply_v_lp/2' FALL=1\n")
    the_file.write(".MEASURE TRAN meas_inv_nand" + str(size) + "_" + name + "_1_trise TRIG V(n_1_1) VAL='supply_v_lp/2' FALL=1\n")
    the_file.write("+    TARG V(Xsec.n_1_1) VAL='supply_v_lp/2' RISE=1\n\n")

    the_file.write("* inv_" + name + " delay\n")
    the_file.write(".MEASURE TRAN meas_inv_" + name + "_2_tfall TRIG V(n_1_1) VAL='supply_v_lp/2' FALL=1\n")
    the_file.write("+    TARG V(n_1_"+str(1+fanout)+") VAL='supply_v_lp/2' FALL=1\n")
    the_file.write(".MEASURE TRAN meas_inv_" + name + "_2_trise TRIG V(n_1_1) VAL='supply_v_lp/2' RISE=1\n")
    the_file.write("+    TARG V(n_1_"+str(1+fanout)+") VAL='supply_v_lp/2' RISE=1\n\n")

    the_file.write("* Total delays\n")
    the_file.write(".MEASURE TRAN meas_total_tfall TRIG V(n_1_1) VAL='supply_v_lp/2' FALL=1\n")
    the_file.write("+    TARG V(n_1_"+str(1+fanout)+") VAL='supply_v_lp/2' FALL=1\n")
    the_file.write(".MEASURE TRAN meas_total_trise TRIG V(n_1_1) VAL='supply_v_lp/2' RISE=1\n")
    the_file.write("+    TARG V(n_1_"+str(1+fanout)+") VAL='supply_v_lp/2' RISE=1\n\n")

    the_file.write(".MEASURE TRAN meas_logic_low_voltage FIND V(n_in) AT=3n\n\n")

    the_file.write("* Measure the power required to propagate a rise and a fall transition through the subcircuit at 250MHz.\n")
    the_file.write(".MEASURE TRAN meas_current INTEGRAL I(V_sec) FROM=0ns TO=4ns\n")
    the_file.write(".MEASURE TRAN meas_avg_power PARAM = '-(meas_current/4n)*supply_v_lp'\n\n")
    
    the_file.write("********************************************************************************\n")
    the_file.write("** Circuit\n")
    the_file.write("********************************************************************************\n\n")
    # wave shaping circuitry
    the_file.write("xconfigurabledecoderi n_in n_1_1 vdd_lp gnd xconfigurabledecoderi\n")

    #add the nand2 circuit here
    the_file.write("Xsec n_1_1 n_1_2 vdd_sec gnd "+ name +"\n")
    #the load to this circuit:

    for i in range(2, 2+fanout):
        the_file.write("Xwire"+str(i)+" n_1_"+str(i)+" n_1_"+str(i+1)+" wire Rw=wire_xconfigurabledecoderi_res/"+str(fanout)+" Cw=wire_xconfigurabledecoderi_cap/"+str(fanout)+"\n")
        the_file.write("Xloadnand"+str(i)+" n_1_"+str(i)+" n_hang_"+str(i+1)+" vdd_lp gnd xconfigurabledecoderiii\n")

    the_file.write(".END")
    the_file.close()

    # Come out of top-level directory
    os.chdir("../")

    return (name + "/" + name + ".sp")





# This is the top-level path for the initial stage in the row-decoder:
def generate_rowdecoderstage0_top(name,numberofgates2,numberofgates3, decodersize, label2, label3):

    # Create directories
    if not os.path.exists(name):
        os.makedirs(name)  
    # Change to directory    
    os.chdir(name)

    filename = name + ".sp"
    the_file = open(filename, 'w')
    the_file.write(".TITLE RAM row decoder stage 0\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Include libraries, parameters and other\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".LIB \"../includes.l\" INCLUDES\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Setup and input\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".TRAN 1p 5n SWEEP DATA=sweep_data\n")
    the_file.write(".OPTIONS BRIEF=1\n\n")
    the_file.write("* Input signal\n")
    the_file.write("VIN n_in gnd PULSE (0 supply_v 0 0 0 2n 4n)\n")
    the_file.write("* Power rail for the circuit under test.\n")
    the_file.write("* This allows us to measure power of a circuit under test without measuring the power of wave shaping and load circuitry.\n")
    the_file.write("V_test vdd_test gnd supply_v\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Measurement\n")
    the_file.write("********************************************************************************\n\n")

    the_file.write("* inv_rowdecoderstage0_1 delay\n")
    the_file.write(".MEASURE TRAN meas_inv_rowdecoderstage0_1_tfall TRIG V(n_1_4) VAL='supply_v/2' RISE=1\n")
    the_file.write("+    TARG V(n_1_"+str(numberofgates2 + 5+ numberofgates3)+") VAL='supply_v/2' FALL=1\n")
    the_file.write(".MEASURE TRAN meas_inv_rowdecoderstage0_1_trise TRIG V(n_1_4) VAL='supply_v/2' FALL=1\n")
    the_file.write("+    TARG V(n_1_"+str(numberofgates2 + 5+ numberofgates3)+") VAL='supply_v/2' RISE=1\n\n")
    
    the_file.write("* Total delays\n")
    the_file.write(".MEASURE TRAN meas_total_tfall TRIG V(n_1_4) VAL='supply_v/2' RISE=1\n")
    the_file.write("+    TARG V(n_1_"+str(numberofgates2 + 5+ numberofgates3)+") VAL='supply_v/2' FALL=1\n")
    the_file.write(".MEASURE TRAN meas_total_trise TRIG V(n_1_4) VAL='supply_v/2' FALL=1\n")
    the_file.write("+    TARG V(n_1_"+str(numberofgates2 + 5+ numberofgates3)+") VAL='supply_v/2' RISE=1\n\n")

    the_file.write(".MEASURE TRAN meas_logic_low_voltage FIND V(n_in) AT=3n\n\n")


    the_file.write("* Measure the power required to propagate a rise and a fall transition through the subcircuit at 250MHz.\n")
    the_file.write(".MEASURE TRAN meas_current INTEGRAL I(V_test) FROM=0ns TO=4ns\n")
    the_file.write(".MEASURE TRAN meas_avg_power PARAM = '-(meas_current/4n)*supply_v'\n\n")
    
    the_file.write("********************************************************************************\n")
    the_file.write("** Circuit\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write("Xrouting_wire_load_1 n_in n_1_1 n_1_2 vsram vsram_n vdd gnd vdd vdd routing_wire_load\n")
    the_file.write("Xlocal_routing_wire_load_1 n_1_2 n_1_3 vsram vsram_n vdd gnd vdd RAM_local_routing_wire_load\n")
    the_file.write("Xinv_ff_output_driver n_1_3 n_1_4 vdd gnd inv Wn=inv_ff_output_driver_nmos Wp=inv_ff_output_driver_pmos\n")
    # Circuit Under test
    the_file.write("Xdstage0 n_1_4 n_1_5 vdd_test gnd rowdecoderstage0\n")
    #the load
    for i in range(5, numberofgates2+5):
        the_file.write("Xwire"+str(i)+" n_1_"+str(i)+" n_1_"+str(i+1)+" wire Rw=wire_rowdecoderstage0_res/"+str(numberofgates2+numberofgates3)+" Cw=wire_rowdecoderstage0_cap/"+str(numberofgates2+numberofgates3)+"\n")
        the_file.write("Xnand2"+str(i)+" n_1_"+str(i+1)+" n_hang_"+str(i)+" vdd gnd nand2 Wn=inv_nand2_rowdecoderstage12_1_nmos Wp=inv_nand2_rowdecoderstage12_1_pmos\n")
    for i in range(5+ numberofgates2, numberofgates2 + 5+ numberofgates3):
        the_file.write("Xwire3"+str(i)+" n_1_"+str(i)+" n_1_"+str(i+1)+" wire Rw=wire_rowdecoderstage0_res/"+str(numberofgates2+numberofgates3)+" Cw=wire_rowdecoderstage0_cap/"+str(numberofgates2+numberofgates3)+"\n")
        the_file.write("Xnand3"+str(i)+" n_1_"+str(i+1)+" n_hang_"+str(i)+" vdd gnd nand3 Wn=inv_nand3_rowdecoderstage13_1_nmos Wp=inv_nand3_rowdecoderstage13_1_pmos\n")


    the_file.write(".END")
    the_file.close()

    # Come out of the directory
    os.chdir("../")

    return (name + "/" + name + ".sp")


def generate_rowdecoderstage0_top_lp(name,numberofgates2,numberofgates3, decodersize, label2, label3):

    # Create directories
    if not os.path.exists(name):
        os.makedirs(name)  
    # Change to directory    
    os.chdir(name)
    filename = name + ".sp"
    the_file = open(filename, 'w')
    the_file.write(".TITLE RAM row decoder stage 0\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Include libraries, parameters and other\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".LIB \"../includes.l\" INCLUDES\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Setup and input\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".TRAN 1p 5n SWEEP DATA=sweep_data\n")
    the_file.write(".OPTIONS BRIEF=1\n\n")
    the_file.write("* Input signal\n")
    the_file.write("VIN n_in gnd PULSE (0 supply_v_lp 0 0 0 2n 4n)\n")
    the_file.write("* Power rail for the circuit under test.\n")
    the_file.write("* This allows us to measure power of a circuit under test without measuring the power of wave shaping and load circuitry.\n")
    the_file.write("V_test vdd_test gnd supply_v_lp\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Measurement\n")
    the_file.write("********************************************************************************\n\n")

    the_file.write("* inv_rowdecoderstage0_1 delay\n")
    the_file.write(".MEASURE TRAN meas_inv_rowdecoderstage0_1_tfall TRIG V(n_1_4) VAL='supply_v_lp/2' RISE=1\n")
    the_file.write("+    TARG V(n_1_"+str(numberofgates2 + 5+ numberofgates3)+") VAL='supply_v_lp/2' FALL=1\n")
    the_file.write(".MEASURE TRAN meas_inv_rowdecoderstage0_1_trise TRIG V(n_1_4) VAL='supply_v_lp/2' FALL=1\n")
    the_file.write("+    TARG V(n_1_"+str(numberofgates2 + 5+ numberofgates3)+") VAL='supply_v_lp/2' RISE=1\n\n")
    
    the_file.write("* Total delays\n")
    the_file.write(".MEASURE TRAN meas_total_tfall TRIG V(n_1_4) VAL='supply_v_lp/2' RISE=1\n")
    the_file.write("+    TARG V(n_1_"+str(numberofgates2 + 5+ numberofgates3)+") VAL='supply_v_lp/2' FALL=1\n")
    the_file.write(".MEASURE TRAN meas_total_trise TRIG V(n_1_4) VAL='supply_v_lp/2' FALL=1\n")
    the_file.write("+    TARG V(n_1_"+str(numberofgates2 + 5+ numberofgates3)+") VAL='supply_v_lp/2' RISE=1\n\n")

    the_file.write(".MEASURE TRAN meas_logic_low_voltage FIND V(n_in) AT=3n\n\n")

    the_file.write("* Measure the power required to propagate a rise and a fall transition through the subcircuit at 250MHz.\n")
    the_file.write(".MEASURE TRAN meas_current INTEGRAL I(V_test) FROM=0ns TO=4ns\n")
    the_file.write(".MEASURE TRAN meas_avg_power PARAM = '-(meas_current/4n)*supply_v_lp'\n\n")
    
    the_file.write("********************************************************************************\n")
    the_file.write("** Circuit\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write("Xrouting_wire_load_1 n_in n_1_1 n_1_2 vsram vsram_n vdd gnd vdd vdd routing_wire_load\n")
    the_file.write("Xlocal_routing_wire_load_1 n_1_2 n_1_3 vsram vsram_n vdd gnd vdd RAM_local_routing_wire_load\n")
    the_file.write("Xinv_ff_output_driver n_1_3 n_1_4 vdd_lp gnd inv_lp Wn=inv_ff_output_driver_nmos Wp=inv_ff_output_driver_pmos\n")
    # Circuit Under test
    the_file.write("Xdstage0 n_1_4 n_1_5 vdd_test gnd rowdecoderstage0\n")
    #the load
    for i in range(5, numberofgates2+5):
        the_file.write("Xwire"+str(i)+" n_1_"+str(i)+" n_1_"+str(i+1)+" wire Rw=wire_rowdecoderstage0_res/"+str(numberofgates2+numberofgates3)+" Cw=wire_rowdecoderstage0_cap/"+str(numberofgates2+numberofgates3)+"\n")
        the_file.write("Xnand2"+str(i)+" n_1_"+str(i+1)+" n_hang_"+str(i)+" vdd_lp gnd nand2_lp Wn=inv_nand2_rowdecoderstage12_1_nmos Wp=inv_nand2_rowdecoderstage12_1_pmos\n")
    for i in range(5+ numberofgates2, numberofgates2 + 5+ numberofgates3):
        the_file.write("Xwire3"+str(i)+" n_1_"+str(i)+" n_1_"+str(i+1)+" wire Rw=wire_rowdecoderstage0_res/"+str(numberofgates2+numberofgates3)+" Cw=wire_rowdecoderstage0_cap/"+str(numberofgates2+numberofgates3)+"\n")
        the_file.write("Xnand3"+str(i)+" n_1_"+str(i+1)+" n_hang_"+str(i)+" vdd_lp gnd nand3_lp Wn=inv_nand3_rowdecoderstage13_1_nmos Wp=inv_nand3_rowdecoderstage13_1_pmos\n")

    the_file.write(".END")
    the_file.close()

    # Come out of the directory
    os.chdir("../")

    return (name + "/" + name + ".sp")


# This is the top-level path for the first stage in the configurable decoder:
def generate_configurabledecoderi_top(name,numberofgates2,numberofgates3, ConfiDecodersize):

    # Create directories
    if not os.path.exists(name):
        os.makedirs(name)  
    # Change to directory    
    os.chdir(name)

    filename = name + ".sp"
    the_file = open(filename, 'w')
    the_file.write(".TITLE RAM configurable decoder\n\n")



    the_file.write("********************************************************************************\n")
    the_file.write("** Include libraries, parameters and other\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".LIB \"../includes.l\" INCLUDES\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Setup and input\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".TRAN 1p 5n SWEEP DATA=sweep_data\n")
    the_file.write(".OPTIONS BRIEF=1\n\n")
    the_file.write("* Input signal\n")
    the_file.write("VIN n_in gnd PULSE (0 supply_v 0 0 0 2n 4n)\n")
    the_file.write("* Power rail for the circuit under test.\n")
    the_file.write("* This allows us to measure power of a circuit under test without measuring the power of wave shaping and load circuitry.\n")
    the_file.write("V_test vdd_test gnd supply_v\n\n")

    #fall time is meaningless in precharge circuitry. I'll keep the format to make things easier.

    the_file.write("********************************************************************************\n")
    the_file.write("** Measurement\n")
    the_file.write("********************************************************************************\n\n")

    the_file.write("* inv_columndecoder_1 delay\n")
    the_file.write(".MEASURE TRAN meas_inv_xconfigurabledecoderi_1_tfall TRIG V(n_1_4) VAL='supply_v/2' RISE=1\n")
    the_file.write("+    TARG V(n_1_"+str(numberofgates2 + 5+ numberofgates3)+") VAL='supply_v/2' FALL=1\n")
    the_file.write(".MEASURE TRAN meas_inv_xconfigurabledecoderi_1_trise TRIG V(n_1_4) VAL='supply_v/2' FALL=1\n")
    the_file.write("+    TARG V(n_1_"+str(numberofgates2 + 5+ numberofgates3)+") VAL='supply_v/2' RISE=1\n\n")
    
    the_file.write("* Total delays\n")
    the_file.write(".MEASURE TRAN meas_total_tfall TRIG V(n_1_4) VAL='supply_v/2' RISE=1\n")
    the_file.write("+    TARG V(n_1_"+str(numberofgates2 + 5+ numberofgates3)+") VAL='supply_v/2' FALL=1\n")
    the_file.write(".MEASURE TRAN meas_total_trise TRIG V(n_1_4) VAL='supply_v/2' FALL=1\n")
    the_file.write("+    TARG V(n_1_"+str(numberofgates2 + 5+ numberofgates3)+") VAL='supply_v/2' RISE=1\n\n")

    the_file.write(".MEASURE TRAN meas_logic_low_voltage FIND V(n_in) AT=3n\n\n")

    the_file.write("* Measure the power required to propagate a rise and a fall transition through the subcircuit at 250MHz.\n")
    the_file.write(".MEASURE TRAN meas_current INTEGRAL I(V_test) FROM=0ns TO=4ns\n")
    the_file.write(".MEASURE TRAN meas_avg_power PARAM = '-(meas_current/4n)*supply_v'\n\n")
    
    the_file.write("********************************************************************************\n")
    the_file.write("** Circuit\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write("Xrouting_wire_load_1 n_in n_1_1 n_1_2 vsram vsram_n vdd gnd vdd vdd routing_wire_load\n")
    the_file.write("Xlocal_routing_wire_load_1 n_1_2 n_1_3 vsram vsram_n vdd gnd vdd RAM_local_routing_wire_load\n")
    the_file.write("Xinv_ff_output_driver n_1_3 n_1_4 vdd gnd inv Wn=inv_ff_output_driver_nmos Wp=inv_ff_output_driver_pmos\n")
    #add configurable recorder
    the_file.write("Xdconfi n_1_4 n_1_5 vdd_test gnd xconfigurabledecoderi\n")
    #the load
    for i in range(5, numberofgates2+5):
        the_file.write("Xwire"+str(i)+" n_1_"+str(i)+" n_1_"+str(i+1)+" wire Rw=wire_xconfigurabledecoderi_res/"+str(numberofgates2+numberofgates3)+" Cw=wire_xconfigurabledecoderi_cap/"+str(numberofgates2+numberofgates3)+"\n")
        the_file.write("Xnand2"+str(i)+" n_1_"+str(i+1)+" n_hang_"+str(i)+" vdd gnd nand2 Wn=inv_nand2_xconfigurabledecoder2ii_1_nmos Wp=inv_nand2_xconfigurabledecoder2ii_1_pmos\n")

    for i in range(5+ numberofgates2, numberofgates2 + 5+ numberofgates3):
        the_file.write("Xwire3"+str(i)+" n_1_"+str(i)+" n_1_"+str(i+1)+" wire Rw=wire_xconfigurabledecoderi_res/"+str(numberofgates2+numberofgates3)+" Cw=wire_xconfigurabledecoderi_cap/"+str(numberofgates2+numberofgates3)+"\n")
        the_file.write("Xnand3"+str(i)+" n_1_"+str(i+1)+" n_hang_"+str(i)+" vdd gnd nand3 Wn=inv_nand3_xconfigurabledecoder3ii_1_nmos Wp=inv_nand3_xconfigurabledecoder3ii_1_pmos\n")

    the_file.write(".END")
    the_file.close()

    # Come out of top-level directory
    os.chdir("../")

    return (name + "/" + name + ".sp")


# This is the top-level path for the first stage in the configurable decoder:
def generate_configurabledecoderi_top_lp(name,numberofgates2,numberofgates3, ConfiDecodersize):

    # Create directories
    if not os.path.exists(name):
        os.makedirs(name)  
    # Change to directory    
    os.chdir(name)

    filename = name + ".sp"
    the_file = open(filename, 'w')
    the_file.write(".TITLE RAM configurable decoder\n\n")



    the_file.write("********************************************************************************\n")
    the_file.write("** Include libraries, parameters and other\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".LIB \"../includes.l\" INCLUDES\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Setup and input\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".TRAN 1p 5n SWEEP DATA=sweep_data\n")
    the_file.write(".OPTIONS BRIEF=1\n\n")
    the_file.write("* Input signal\n")
    the_file.write("VIN n_in gnd PULSE (0 supply_v_lp 0 0 0 2n 4n)\n")
    the_file.write("* Power rail for the circuit under test.\n")
    the_file.write("* This allows us to measure power of a circuit under test without measuring the power of wave shaping and load circuitry.\n")
    the_file.write("V_test vdd_test gnd supply_v_lp\n\n")

    #fall time is meaningless in precharge circuitry. I'll keep the format to make things easier.

    the_file.write("********************************************************************************\n")
    the_file.write("** Measurement\n")
    the_file.write("********************************************************************************\n\n")

    the_file.write("* inv_columndecoder_1 delay\n")
    the_file.write(".MEASURE TRAN meas_inv_xconfigurabledecoderi_1_tfall TRIG V(n_1_4) VAL='supply_v_lp/2' RISE=1\n")
    the_file.write("+    TARG V(n_1_"+str(numberofgates2 + 5+ numberofgates3)+") VAL='supply_v_lp/2' FALL=1\n")
    the_file.write(".MEASURE TRAN meas_inv_xconfigurabledecoderi_1_trise TRIG V(n_1_4) VAL='supply_v_lp/2' FALL=1\n")
    the_file.write("+    TARG V(n_1_"+str(numberofgates2 + 5+ numberofgates3)+") VAL='supply_v_lp/2' RISE=1\n\n")
    
    the_file.write("* Total delays\n")
    the_file.write(".MEASURE TRAN meas_total_tfall TRIG V(n_1_4) VAL='supply_v_lp/2' RISE=1\n")
    the_file.write("+    TARG V(n_1_"+str(numberofgates2 + 5+ numberofgates3)+") VAL='supply_v_lp/2' FALL=1\n")
    the_file.write(".MEASURE TRAN meas_total_trise TRIG V(n_1_4) VAL='supply_v_lp/2' FALL=1\n")
    the_file.write("+    TARG V(n_1_"+str(numberofgates2 + 5+ numberofgates3)+") VAL='supply_v_lp/2' RISE=1\n\n")

    the_file.write(".MEASURE TRAN meas_logic_low_voltage FIND V(n_in) AT=3n\n\n")

    the_file.write("* Measure the power required to propagate a rise and a fall transition through the subcircuit at 250MHz.\n")
    the_file.write(".MEASURE TRAN meas_current INTEGRAL I(V_test) FROM=0ns TO=4ns\n")
    the_file.write(".MEASURE TRAN meas_avg_power PARAM = '-(meas_current/4n)*supply_v_lp'\n\n")
    
    the_file.write("********************************************************************************\n")
    the_file.write("** Circuit\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write("Xrouting_wire_load_1 n_in n_1_1 n_1_2 vsram vsram_n vdd gnd vdd vdd routing_wire_load\n")
    the_file.write("Xlocal_routing_wire_load_1 n_1_2 n_1_3 vsram vsram_n vdd gnd vdd RAM_local_routing_wire_load\n")
    the_file.write("Xinv_ff_output_driver n_1_3 n_1_4 vdd_lp gnd inv_lp Wn=inv_ff_output_driver_nmos Wp=inv_ff_output_driver_pmos\n")
    #add configurable recorder
    the_file.write("Xdconfi n_1_4 n_1_5 vdd_test gnd xconfigurabledecoderi\n")
    #the load
    for i in range(5, numberofgates2+5):
        the_file.write("Xwire"+str(i)+" n_1_"+str(i)+" n_1_"+str(i+1)+" wire Rw=wire_xconfigurabledecoderi_res/"+str(numberofgates2+numberofgates3)+" Cw=wire_xconfigurabledecoderi_cap/"+str(numberofgates2+numberofgates3)+"\n")
        the_file.write("Xnand2"+str(i)+" n_1_"+str(i+1)+" n_hang_"+str(i)+" vdd_lp gnd nand2 Wn=inv_nand2_xconfigurabledecoder2ii_1_nmos Wp=inv_nand2_xconfigurabledecoder2ii_1_pmos\n")

    for i in range(5+ numberofgates2, numberofgates2 + 5+ numberofgates3):
        the_file.write("Xwire3"+str(i)+" n_1_"+str(i)+" n_1_"+str(i+1)+" wire Rw=wire_xconfigurabledecoderi_res/"+str(numberofgates2+numberofgates3)+" Cw=wire_xconfigurabledecoderi_cap/"+str(numberofgates2+numberofgates3)+"\n")
        the_file.write("Xnand3"+str(i)+" n_1_"+str(i+1)+" n_hang_"+str(i)+" vdd_lp gnd nand3 Wn=inv_nand3_xconfigurabledecoder3ii_1_nmos Wp=inv_nand3_xconfigurabledecoder3ii_1_pmos\n")

    the_file.write(".END")
    the_file.close()

    # Come out of top-level directory
    os.chdir("../")

    return (name + "/" + name + ".sp")

# This is the top-level path for column decoder:
def generate_columndecoder_top(name, numberoftgates, decsize):

    # Create directories
    if not os.path.exists(name):
        os.makedirs(name)  
    # Change to directory    
    os.chdir(name)

    filename = name + ".sp"
    the_file = open(filename, 'w')
    the_file.write(".TITLE RAM column decoder\n\n")



    the_file.write("********************************************************************************\n")
    the_file.write("** Include libraries, parameters and other\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".LIB \"../includes.l\" INCLUDES\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Setup and input\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".TRAN 1p 5n SWEEP DATA=sweep_data\n")
    the_file.write(".OPTIONS BRIEF=1\n\n")
    the_file.write("* Input signal\n")
    the_file.write("VIN n_in gnd PULSE (0 supply_v 0 0 0 2n 4n)\n")
    the_file.write("* Power rail for the circuit under test.\n")
    the_file.write("* This allows us to measure power of a circuit under test without measuring the power of wave shaping and load circuitry.\n")
    the_file.write("V_col vdd_col gnd supply_v\n\n")

    #fall time is meaningless in precharge circuitry. I'll keep the format to make things easier.

    the_file.write("********************************************************************************\n")
    the_file.write("** Measurement\n")
    the_file.write("********************************************************************************\n\n")

    the_file.write("* inv_columndecoder_1 delay\n")
    the_file.write(".MEASURE TRAN meas_inv_columndecoder_1_tfall TRIG V(Xdecorder.n_in) VAL='supply_v/2' RISE=1\n")
    the_file.write("+    TARG V(Xdecorder.n_1_1) VAL='supply_v/2' FALL=1\n")
    the_file.write(".MEASURE TRAN meas_inv_columndecoder_1_trise TRIG V(Xdecorder.n_in) VAL='supply_v/2' FALL=1\n")
    the_file.write("+    TARG V(Xdecorder.n_1_1) VAL='supply_v/2' RISE=1\n\n")
    
    the_file.write("* inv_columndecoder_2 delay\n")
    the_file.write(".MEASURE TRAN meas_inv_columndecoder_2_tfall TRIG V(Xdecorder.n_in) VAL='supply_v/2' FALL=1\n")
    the_file.write("+    TARG V(Xdecorder.n_1_2) VAL='supply_v/2' FALL=1\n")
    the_file.write(".MEASURE TRAN meas_inv_columndecoder_2_trise TRIG V(Xdecorder.n_in) VAL='supply_v/2' RISE=1\n")
    the_file.write("+    TARG V(Xdecorder.n_1_2) VAL='supply_v/2' RISE=1\n\n")

    the_file.write("* inv_columndecoder_3 delay\n")
    the_file.write(".MEASURE TRAN meas_inv_columndecoder_3_tfall TRIG V(Xdecorder.n_in) VAL='supply_v/2' RISE=1\n")
    the_file.write("+    TARG V(n_1_"+str(numberoftgates+5)+") VAL='supply_v/2' FALL=1\n")
    the_file.write(".MEASURE TRAN meas_inv_columndecoder_3_trise TRIG V(Xdecorder.n_in) VAL='supply_v/2' FALL=1\n")
    the_file.write("+    TARG V(n_1_"+str(numberoftgates+5)+") VAL='supply_v/2' RISE=1\n\n")


    the_file.write("* Total delays\n")
    the_file.write(".MEASURE TRAN meas_total_tfall TRIG V(n_1_3) VAL='supply_v/2' FALL=1\n")
    the_file.write("+    TARG V(n_1_"+str(numberoftgates+5)+") VAL='supply_v/2' FALL=1\n")
    the_file.write(".MEASURE TRAN meas_total_trise TRIG V(n_1_3) VAL='supply_v/2' RISE=1\n")
    the_file.write("+    TARG V(n_1_"+str(numberoftgates+5)+") VAL='supply_v/2' RISE=1\n\n")

    the_file.write(".MEASURE TRAN meas_logic_low_voltage FIND V(n_in) AT=3n\n\n")

    the_file.write("* Measure the power required to propagate a rise and a fall transition through the subcircuit at 250MHz.\n")
    the_file.write(".MEASURE TRAN meas_current INTEGRAL I(V_col) FROM=0ns TO=4ns\n")
    the_file.write(".MEASURE TRAN meas_avg_power PARAM = '-(meas_current/4n)*supply_v'\n\n")
    
    the_file.write("********************************************************************************\n")
    the_file.write("** Circuit\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write("Xrouting_wire_load_1 n_in n_1_1 n_1_2 vsram vsram_n vdd gnd vdd vdd routing_wire_load\n")
    the_file.write("Xlocal_routing_wire_load_1 n_1_2 n_1_3 vsram vsram_n vdd gnd vdd RAM_local_routing_wire_load\n")
    the_file.write("Xinv_ff_output_driver n_1_3 n_1_4 vdd gnd inv Wn=inv_ff_output_driver_nmos Wp=inv_ff_output_driver_pmos\n")
    the_file.write("Xdecorder n_1_4 n_1_5 vdd_col gnd columndecoder\n")
    #A chain of wires and tgates go here:
    for i in range(5, numberoftgates+5,2):
        the_file.write("Xwire"+str(i)+" n_1_"+str(i)+" n_1_"+str(i+1)+" wire Rw=wire_memorycell_horizontal_res/"+str(numberoftgates)+" Cw=wire_memorycell_horizontal_cap/"+str(numberoftgates)+"\n")
        the_file.write("Xtgate"+str(i)+" gnd n_2_"+str(i)+" gnd n_1_"+str(i+1)+" vdd gnd RAM_tgate\n")
        the_file.write("Xwire"+str(i+1)+" n_1_"+str(i+1)+" n_1_"+str(i+2)+" wire Rw=wire_memorycell_horizontal_res/"+str(numberoftgates)+" Cw=wire_memorycell_horizontal_cap/"+str(numberoftgates)+"\n")
        the_file.write("Xtgate"+str(i+1)+" gnd n_2_"+str(i+1)+" n_1_"+str(i+2)+" gnd vdd gnd RAM_tgate\n")

    the_file.write(".END")
    the_file.close()

    # Come out of top-level directory
    os.chdir("../")

    return (name + "/" + name + ".sp")


# This is the top-level path for column decoder:
def generate_columndecoder_top_lp(name, numberoftgates, decsize):

    # Create directories
    if not os.path.exists(name):
        os.makedirs(name)  
    # Change to directory    
    os.chdir(name)

    filename = name + ".sp"
    the_file = open(filename, 'w')
    the_file.write(".TITLE RAM column decoder\n\n")



    the_file.write("********************************************************************************\n")
    the_file.write("** Include libraries, parameters and other\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".LIB \"../includes.l\" INCLUDES\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Setup and input\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".TRAN 1p 5n SWEEP DATA=sweep_data\n")
    the_file.write(".OPTIONS BRIEF=1\n\n")
    the_file.write("* Input signal\n")
    the_file.write("VIN n_in gnd PULSE (0 supply_v_lp 0 0 0 2n 4n)\n")
    the_file.write("* Power rail for the circuit under test.\n")
    the_file.write("* This allows us to measure power of a circuit under test without measuring the power of wave shaping and load circuitry.\n")
    the_file.write("V_col vdd_col gnd supply_v_lp\n\n")

    #fall time is meaningless in precharge circuitry. I'll keep the format to make things easier.

    the_file.write("********************************************************************************\n")
    the_file.write("** Measurement\n")
    the_file.write("********************************************************************************\n\n")

    the_file.write("* inv_columndecoder_1 delay\n")
    the_file.write(".MEASURE TRAN meas_inv_columndecoder_1_tfall TRIG V(Xdecorder.n_in) VAL='supply_v_lp/2' RISE=1\n")
    the_file.write("+    TARG V(Xdecorder.n_1_1) VAL='supply_v_lp/2' FALL=1\n")
    the_file.write(".MEASURE TRAN meas_inv_columndecoder_1_trise TRIG V(Xdecorder.n_in) VAL='supply_v_lp/2' FALL=1\n")
    the_file.write("+    TARG V(Xdecorder.n_1_1) VAL='supply_v_lp/2' RISE=1\n\n")
    
    the_file.write("* inv_columndecoder_2 delay\n")
    the_file.write(".MEASURE TRAN meas_inv_columndecoder_2_tfall TRIG V(Xdecorder.n_in) VAL='supply_v_lp/2' FALL=1\n")
    the_file.write("+    TARG V(Xdecorder.n_1_2) VAL='supply_v_lp/2' FALL=1\n")
    the_file.write(".MEASURE TRAN meas_inv_columndecoder_2_trise TRIG V(Xdecorder.n_in) VAL='supply_v_lp/2' RISE=1\n")
    the_file.write("+    TARG V(Xdecorder.n_1_2) VAL='supply_v_lp/2' RISE=1\n\n")

    the_file.write("* inv_columndecoder_3 delay\n")
    the_file.write(".MEASURE TRAN meas_inv_columndecoder_3_tfall TRIG V(Xdecorder.n_in) VAL='supply_v_lp/2' RISE=1\n")
    the_file.write("+    TARG V(n_1_"+str(numberoftgates+5)+") VAL='supply_v_lp/2' FALL=1\n")
    the_file.write(".MEASURE TRAN meas_inv_columndecoder_3_trise TRIG V(Xdecorder.n_in) VAL='supply_v_lp/2' FALL=1\n")
    the_file.write("+    TARG V(n_1_"+str(numberoftgates+5)+") VAL='supply_v_lp/2' RISE=1\n\n")


    the_file.write("* Total delays\n")
    the_file.write(".MEASURE TRAN meas_total_tfall TRIG V(n_1_3) VAL='supply_v_lp/2' FALL=1\n")
    the_file.write("+    TARG V(n_1_"+str(numberoftgates+5)+") VAL='supply_v_lp/2' FALL=1\n")
    the_file.write(".MEASURE TRAN meas_total_trise TRIG V(n_1_3) VAL='supply_v_lp/2' RISE=1\n")
    the_file.write("+    TARG V(n_1_"+str(numberoftgates+5)+") VAL='supply_v_lp/2' RISE=1\n\n")

    the_file.write(".MEASURE TRAN meas_logic_low_voltage FIND V(n_in) AT=3n\n\n")

    the_file.write("* Measure the power required to propagate a rise and a fall transition through the subcircuit at 250MHz.\n")
    the_file.write(".MEASURE TRAN meas_current INTEGRAL I(V_col) FROM=0ns TO=4ns\n")
    the_file.write(".MEASURE TRAN meas_avg_power PARAM = '-(meas_current/4n)*supply_v_lp'\n\n")
    
    the_file.write("********************************************************************************\n")
    the_file.write("** Circuit\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write("Xrouting_wire_load_1 n_in n_1_1 n_1_2 vsram vsram_n vdd gnd vdd vdd routing_wire_load\n")
    the_file.write("Xlocal_routing_wire_load_1 n_1_2 n_1_3 vsram vsram_n vdd gnd vdd RAM_local_routing_wire_load\n")
    the_file.write("Xinv_ff_output_driver n_1_3 n_1_4 vdd_lp gnd inv_lp Wn=inv_ff_output_driver_nmos Wp=inv_ff_output_driver_pmos\n")
    the_file.write("Xdecorder n_1_4 n_1_5 vdd_col gnd columndecoder\n")
    #A chain of wires and tgates go here:
    for i in range(5, numberoftgates+5,2):
        the_file.write("Xwire"+str(i)+" n_1_"+str(i)+" n_1_"+str(i+1)+" wire Rw=wire_memorycell_horizontal_res/"+str(numberoftgates)+" Cw=wire_memorycell_horizontal_cap/"+str(numberoftgates)+"\n")
        the_file.write("Xtgate"+str(i)+" gnd n_2_"+str(i)+" gnd n_1_"+str(i+1)+" vdd_lp gnd RAM_tgate\n")
        the_file.write("Xwire"+str(i+1)+" n_1_"+str(i+1)+" n_1_"+str(i+2)+" wire Rw=wire_memorycell_horizontal_res/"+str(numberoftgates)+" Cw=wire_memorycell_horizontal_cap/"+str(numberoftgates)+"\n")
        the_file.write("Xtgate"+str(i+1)+" gnd n_2_"+str(i+1)+" n_1_"+str(i+2)+" gnd vdd_lp gnd RAM_tgate\n")

    the_file.write(".END")
    the_file.close()

    # Come out of top-level directory
    os.chdir("../")

    return (name + "/" + name + ".sp")

def generate_writedriver_top(name, numberofsrams):

    # Create directories
    if not os.path.exists(name):
        os.makedirs(name)  
    # Change to directory    
    os.chdir(name)

    filename = name + ".sp"
    the_file = open(filename, 'w')
    the_file.write(".TITLE RAM write driver\n\n")


    the_file.write("********************************************************************************\n")
    the_file.write("** Include libraries, parameters and other\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".LIB \"../includes.l\" INCLUDES\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Setup and input\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".TRAN 1p 5n SWEEP DATA=sweep_data\n")
    the_file.write(".OPTIONS BRIEF=1\n\n")
    the_file.write("* Input signal\n")
    the_file.write("VIN n_in gnd PULSE (0 supply_v 0 0 0 2n 4n)\n")
    the_file.write("VIwe we gnd PULSE (0 supply_v 0 0 0 4n 8n)\n")
    the_file.write("* Power rail for the circuit under test.\n")
    the_file.write("* This allows us to measure power of a circuit under test without measuring the power of wave shaping and load circuitry.\n")
    the_file.write("V_write vdd_wr gnd supply_v\n\n")

    #fall time is meaningless in precharge circuitry. I'll keep the format to make things easier.

    the_file.write("********************************************************************************\n")
    the_file.write("** Measurement\n")
    the_file.write("********************************************************************************\n\n")

    the_file.write("* inv_writedriver_1 delay\n")
    the_file.write(".MEASURE TRAN meas_inv_writedriver_1_tfall TRIG V(xwrite.n_din) VAL='supply_v/2' RISE=1\n")
    the_file.write("+    TARG V(xwrite.n_dinb) VAL='supply_v/2' FALL=1\n")
    the_file.write(".MEASURE TRAN meas_inv_writedriver_1_trise TRIG V(xwrite.n_din) VAL='supply_v/2' FALL=1\n")
    the_file.write("+    TARG V(xwrite.n_dinb) VAL='supply_v/2' RISE=1\n\n")
    
    the_file.write("* inv_writedriver_2 delay\n")
    the_file.write(".MEASURE TRAN meas_inv_writedriver_2_tfall TRIG V(xwrite.n_we) VAL='supply_v/2' RISE=1\n")
    the_file.write("+    TARG V(xwrite.n_web) VAL='supply_v/2' FALL=1\n")
    the_file.write(".MEASURE TRAN meas_inv_writedriver_2_trise TRIG V(xwrite.n_we) VAL='supply_v/2' FALL=1\n")
    the_file.write("+    TARG V(xwrite.n_web) VAL='supply_v/2' RISE=1\n\n")

    the_file.write("* Total delays\n")
    the_file.write(".MEASURE TRAN meas_total_tfall TRIG V(n_in) VAL='supply_v/2' RISE=1\n")
    the_file.write("+    TARG V(Xsram1.n_1_2) VAL='supply_v/2' FALL=1\n")
    the_file.write(".MEASURE TRAN meas_total_trise TRIG V(n_in) VAL='supply_v/2' FALL=1\n")
    the_file.write("+    TARG V(Xsram1.n_1_2) VAL='supply_v/2' RISE=1\n\n")

    the_file.write(".MEASURE TRAN meas_logic_low_voltage FIND V(n_in) AT=3n\n\n")

    the_file.write("* Measure the power required to propagate a rise and a fall transition through the subcircuit at 250MHz.\n")
    the_file.write(".MEASURE TRAN meas_current INTEGRAL I(V_write) FROM=0ns TO=4ns\n")
    the_file.write(".MEASURE TRAN meas_avg_power PARAM = '-(meas_current/4n)*supply_v'\n\n")
    
    the_file.write("********************************************************************************\n")
    the_file.write("** Circuit\n")
    the_file.write("********************************************************************************\n\n")

    #shape the form of n_in and w_in before passing to the actual circuit:
    the_file.write("X_inv_shape_0 n_in n_in1 vdd gnd inv Wn=inv_writedriver_1_nmos Wp=inv_writedriver_1_pmos\n")
    the_file.write("X_inv_shape_1 n_in1 n_in_shaped vdd gnd inv Wn=inv_writedriver_1_nmos Wp=inv_writedriver_1_pmos\n")

    the_file.write("X_inv_shape_2 we n_we vdd gnd inv Wn=inv_writedriver_1_nmos Wp=inv_writedriver_1_pmos\n")
    the_file.write("X_inv_shape_3 n_we n_we_shaped vdd gnd inv Wn=inv_writedriver_1_nmos Wp=inv_writedriver_1_pmos\n")

    the_file.write("xprecharge vdd n_bl_0 n_br_0 vdd gnd precharge\n")
    #the_file.write("xwrite we n_in n_bl_0 n_br_0 vdd_wr gnd writedriver\n")
    for i in range(2, numberofsrams+1):
        the_file.write("Xwire"+str(i)+" n_bl_"+str(i-1)+" n_bl_"+str(i)+" wire Rw=wire_memorycell_vertical_res/"+str(numberofsrams)+" Cw=wire_memorycell_vertical_cap/"+str(numberofsrams)+"\n")
        the_file.write("Xwirer"+str(i)+" n_br_"+str(i-1)+" n_br_"+str(i)+" wire Rw=wire_memorycell_vertical_res/"+str(numberofsrams)+" Cw=wire_memorycell_vertical_cap/"+str(numberofsrams)+"\n")
        the_file.write("Xsram"+str(i)+" gnd gnd n_bl_"+str(i)+" gnd n_br_"+str(i)+" gnd vdd gnd memorycell\n")

    the_file.write("Xwire1 n_bl_0 n_bl_1 wire Rw=wire_memorycell_vertical_res/"+str(numberofsrams)+" Cw=wire_memorycell_vertical_cap/"+str(numberofsrams)+"\n")
    the_file.write("Xwirer1 n_br_0 n_br_1 wire Rw=wire_memorycell_vertical_res/"+str(numberofsrams)+" Cw=wire_memorycell_vertical_cap/"+str(numberofsrams)+"\n")
    the_file.write("Xsram1 vdd gnd n_bl_0 gnd n_br_0 gnd vdd gnd memorycell\n")

    the_file.write(".IC V(Xsram1.n_1_2) = 'supply_v'\n")
    the_file.write(".IC V(Xsram1.n_1_1) = 0\n")
    #we'll sense the left side of the sram

    #This part can actually be set to any value because it will be overwritten by the bl and br lines.
    the_file.write(".IC V(xsamp1.n_1_2) = 0\n")
    the_file.write(".IC V(xsamp1.n_1_1) = 'supply_v'\n")
    #tgates on path:
    the_file.write("xtgate1 n_bl_"+str(numberofsrams)+" tgate_l vdd gnd vdd gnd RAM_tgate\n")
    the_file.write("xtgater n_br_"+str(numberofsrams)+" tgate_r vdd gnd vdd gnd RAM_tgate\n")
    #samp and write driver:
    the_file.write("xwrite n_we_shaped n_in_shaped tgate_l tgate_r vdd_wr gnd writedriver\n")
    the_file.write("xsamp1 vdd tgate_l tgate_r n_hang_samp vdd gnd samp1\n")

    #bitline initial conditions
    the_file.write(".IC V(tgate_r) = 'supply_v'\n")
    the_file.write(".IC V(tgate_l) = 'supply_v'\n")
    for i in range(0, numberofsrams+1):
        the_file.write(".IC V(n_br_"+str(i-1)+") = 'supply_v'\n")
        the_file.write(".IC V(n_br_"+str(i-1)+") = 'supply_v'\n")  

    the_file.write(".END")
    the_file.close()

    # Come out of top-level directory
    os.chdir("../")

    return (name + "/" + name + ".sp")

# This is the write driver for SRAM-based BRAMs:
def generate_writedriver_top_lp(name, numberofsrams):

    # Create directories
    if not os.path.exists(name):
        os.makedirs(name)  
    # Change to directory    
    os.chdir(name)

    filename = name + ".sp"
    the_file = open(filename, 'w')
    the_file.write(".TITLE RAM write driver\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Include libraries, parameters and other\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".LIB \"../includes.l\" INCLUDES\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Setup and input\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".TRAN 1p 5n SWEEP DATA=sweep_data\n")
    the_file.write(".OPTIONS BRIEF=1\n\n")
    the_file.write("* Input signal\n")
    the_file.write("VIN n_in gnd PULSE (0 supply_v_lp 0 0 0 2n 4n)\n")
    the_file.write("VIwe we gnd PULSE (0 supply_v_lp 0 0 0 4n 8n)\n")
    the_file.write("* Power rail for the circuit under test.\n")
    the_file.write("* This allows us to measure power of a circuit under test without measuring the power of wave shaping and load circuitry.\n")
    the_file.write("V_write vdd_wr gnd supply_v_lp\n\n")

    #fall time is meaningless in precharge circuitry. I'll keep the format to make things easier.

    the_file.write("********************************************************************************\n")
    the_file.write("** Measurement\n")
    the_file.write("********************************************************************************\n\n")

    the_file.write("* inv_writedriver_1 delay\n")
    the_file.write(".MEASURE TRAN meas_inv_writedriver_1_tfall TRIG V(xwrite.n_din) VAL='supply_v_lp/2' RISE=1\n")
    the_file.write("+    TARG V(xwrite.n_dinb) VAL='supply_v_lp/2' FALL=1\n")
    the_file.write(".MEASURE TRAN meas_inv_writedriver_1_trise TRIG V(xwrite.n_din) VAL='supply_v_lp/2' FALL=1\n")
    the_file.write("+    TARG V(xwrite.n_dinb) VAL='supply_v_lp/2' RISE=1\n\n")
    
    the_file.write("* inv_writedriver_2 delay\n")
    the_file.write(".MEASURE TRAN meas_inv_writedriver_2_tfall TRIG V(xwrite.n_we) VAL='supply_v_lp/2' RISE=1\n")
    the_file.write("+    TARG V(xwrite.n_web) VAL='supply_v_lp/2' FALL=1\n")
    the_file.write(".MEASURE TRAN meas_inv_writedriver_2_trise TRIG V(xwrite.n_we) VAL='supply_v_lp/2' FALL=1\n")
    the_file.write("+    TARG V(xwrite.n_web) VAL='supply_v_lp/2' RISE=1\n\n")

    the_file.write("* Total delays\n")
    the_file.write(".MEASURE TRAN meas_total_tfall TRIG V(n_in) VAL='supply_v_lp/2' RISE=1\n")
    the_file.write("+    TARG V(Xsram1.n_1_2) VAL='supply_v_lp/2' FALL=1\n")
    the_file.write(".MEASURE TRAN meas_total_trise TRIG V(n_in) VAL='supply_v_lp/2' FALL=1\n")
    the_file.write("+    TARG V(Xsram1.n_1_2) VAL='supply_v_lp/2' RISE=1\n\n")

    the_file.write(".MEASURE TRAN meas_logic_low_voltage FIND V(n_in) AT=3n\n\n")
    the_file.write("* Measure the power required to propagate a rise and a fall transition through the subcircuit at 250MHz.\n")
    the_file.write(".MEASURE TRAN meas_current INTEGRAL I(V_write) FROM=0ns TO=4ns\n")
    the_file.write(".MEASURE TRAN meas_avg_power PARAM = '-(meas_current/4n)*supply_v_lp'\n\n")
    
    the_file.write("********************************************************************************\n")
    the_file.write("** Circuit\n")
    the_file.write("********************************************************************************\n\n")

    #shape the form of n_in and w_in before passing to the actual circuit:
    the_file.write("X_inv_shape_0 n_in n_in1 vdd_lp gnd inv Wn=90n Wp=90n\n")
    the_file.write("X_inv_shape_1 n_in1 n_in_shaped vdd_lp gnd inv Wn=90n Wp=90n\n")

    the_file.write("X_inv_shape_2 we n_we vdd_lp gnd inv Wn=90n Wp=90n\n")
    the_file.write("X_inv_shape_3 n_we n_we_shaped vdd_lp gnd inv Wn=90n Wp=90n\n")
    the_file.write("xprecharge vdd_lp n_bl_0 n_br_0 vdd_lp gnd precharge\n")
    #the_file.write("xwrite we n_in n_bl_0 n_br_0 vdd_wr gnd writedriver\n")
    for i in range(2, numberofsrams+1):
        the_file.write("Xwire"+str(i)+" n_bl_"+str(i-1)+" n_bl_"+str(i)+" wire Rw=wire_memorycell_vertical_res/"+str(numberofsrams)+" Cw=wire_memorycell_vertical_cap/"+str(numberofsrams)+"\n")
        the_file.write("Xwirer"+str(i)+" n_br_"+str(i-1)+" n_br_"+str(i)+" wire Rw=wire_memorycell_vertical_res/"+str(numberofsrams)+" Cw=wire_memorycell_vertical_cap/"+str(numberofsrams)+"\n")
        the_file.write("Xsram"+str(i)+" gnd gnd n_bl_"+str(i)+" gnd n_br_"+str(i)+" gnd vdd_lp gnd memorycell\n")

    the_file.write("Xwire1 n_bl_0 n_bl_1 wire Rw=wire_memorycell_vertical_res/"+str(numberofsrams)+" Cw=wire_memorycell_vertical_cap/"+str(numberofsrams)+"\n")
    the_file.write("Xwirer1 n_br_0 n_br_1 wire Rw=wire_memorycell_vertical_res/"+str(numberofsrams)+" Cw=wire_memorycell_vertical_cap/"+str(numberofsrams)+"\n")
    the_file.write("Xsram1 vdd_lp gnd n_bl_0 gnd n_br_0 gnd vdd_lp gnd memorycell\n")

    the_file.write(".IC V(Xsram1.n_1_2) = 'supply_v_lp'\n")
    the_file.write(".IC V(Xsram1.n_1_1) = 0\n")
    #we'll sense the left side of the sram

    #This part can actually be set to any value because it will be overwritten by the bl and br lines.
    the_file.write(".IC V(xsamp1.n_1_2) = 0\n")
    the_file.write(".IC V(xsamp1.n_1_1) = 'supply_v_lp'\n")
    #tgates on path:
    the_file.write("xtgate1 n_bl_"+str(numberofsrams)+" tgate_l vdd_lp gnd vdd_lp gnd RAM_tgate_lp\n")
    the_file.write("xtgater n_br_"+str(numberofsrams)+" tgate_r vdd_lp gnd vdd_lp gnd RAM_tgate_lp\n")
    #samp and write driver:
    #initial conditions for the bitline:
    the_file.write(".IC V(tgate_r) = 'supply_v_lp'\n")
    the_file.write(".IC V(tgate_l) = 'supply_v_lp'\n")
    for i in range(0, numberofsrams+1):
        the_file.write(".IC V(n_br_"+str(i-1)+") = 'supply_v_lp'\n")
        the_file.write(".IC V(n_br_"+str(i-1)+") = 'supply_v_lp'\n")     

    the_file.write("xwrite n_we_shaped n_in_shaped tgate_l tgate_r vdd_wr gnd writedriver\n")
    the_file.write("xsamp1 vdd_lp tgate_l tgate_r n_hang_samp vdd_lp gnd samp1\n")

    the_file.write(".END")
    the_file.close()

    # Come out of top-level directory
    os.chdir("../")

    return (name + "/" + name + ".sp")



# This is the sense amplifier for SRAM-based BRAMs:
def generate_samp_top_part2(name, numberofsrams, difference):

    # Create directories
    if not os.path.exists(name):
        os.makedirs(name)  
    # Change to directory    
    os.chdir(name)

    filename = name + ".sp"
    the_file = open(filename, 'w')
    the_file.write(".TITLE Sense amp\n\n")



    the_file.write("********************************************************************************\n")
    the_file.write("** Include libraries, parameters and other\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".LIB \"../includes.l\" INCLUDES\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Setup and input\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".TRAN 1p 4n SWEEP DATA=sweep_data\n")
    the_file.write(".OPTIONS BRIEF=1\n\n")
    the_file.write("* Input signal\n")
    the_file.write("VIN n_in gnd PULSE ( supply_v 0 0 0 0 4n 8n)\n")
    the_file.write("VIww wordline gnd PULSE (0 supply_v 0 0 0 4n 8n)\n")
    the_file.write("* Power rail for the circuit under test.\n")
    the_file.write("* This allows us to measure power of a circuit under test without measuring the power of wave shaping and load circuitry.\n")
    the_file.write("V_se vdd_se gnd supply_v\n\n")

    #fall time is meaningless in precharge circuitry. I'll keep the format to make things easier.

    the_file.write("********************************************************************************\n")
    the_file.write("** Measurement\n")
    the_file.write("********************************************************************************\n\n")


    the_file.write("* Total delays\n")
    the_file.write(".MEASURE TRAN meas_total_tfall TRIG V(n_in) VAL='sense_v' FALL=1\n")
    the_file.write("+    TARG V(xsamp1.n_1_1) VAL='sense_v' FALL=1\n")
    # the fall delay is actually 0 for this sense amp, but since the total delay is equal to rise delay, I'll just measure it as that so that ERF doesnt fail.
    the_file.write(".MEASURE TRAN meas_total_trise TRIG V(n_in) VAL='sense_v' FALL=1\n")
    the_file.write("+    TARG V(xsamp1.n_1_1) VAL='sense_v' FALL=1\n\n")

    #the_file.write(".MEASURE TRAN meas_logic_low_voltage FIND V(gnd) AT=1n\n\n")
    #the_file.write(".MEASURE TRAN meas_logic_low_voltage FIND V(gnd) AT=1n\n\n")
    the_file.write(".MEASURE TRAN meas_logic_low_voltage FIND V(gnd) AT=1n\n\n")
    the_file.write("* Measure the power required to propagate a rise and a fall transition through the subcircuit at 250MHz.\n")
    the_file.write(".MEASURE TRAN meas_current INTEGRAL I(V_se) FROM=0ns TO=4ns\n")

    the_file.write(".MEASURE TRAN meas_avg_power PARAM = '-(meas_current/4n)*supply_v'\n\n")


    the_file.write("********************************************************************************\n")
    the_file.write("** Circuit\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write("xprecharge vdd n_bl_0 n_br_0 vdd gnd precharge\n")
    for i in range(2, numberofsrams+1):
        the_file.write("Xwire"+str(i)+" n_bl_"+str(i-1)+" n_bl_"+str(i)+" wire Rw=wire_memorycell_vertical_res/"+str(numberofsrams)+" Cw=wire_memorycell_vertical_cap/"+str(numberofsrams)+"\n")
        the_file.write("Xwirer"+str(i)+" n_br_"+str(i-1)+" n_br_"+str(i)+" wire Rw=wire_memorycell_vertical_res/"+str(numberofsrams)+" Cw=wire_memorycell_vertical_cap/"+str(numberofsrams)+"\n")
        the_file.write("Xsram"+str(i)+" gnd gnd n_bl_"+str(i)+" gnd n_br_"+str(i)+" gnd vdd gnd memorycell\n")

    the_file.write("Xwire"+str(1)+" n_bl_"+str(0)+" n_bl_"+str(1)+" wire Rw=wire_memorycell_vertical_res/"+str(numberofsrams)+" Cw=wire_memorycell_vertical_cap/"+str(numberofsrams)+"\n")
    the_file.write("Xwirer"+str(1)+" n_br_"+str(0)+" n_br_"+str(1)+" wire Rw=wire_memorycell_vertical_res/"+str(numberofsrams)+" Cw=wire_memorycell_vertical_cap/"+str(numberofsrams)+"\n")

    the_file.write("Xsram"+str(1)+" gnd gnd n_bl_"+str(1)+" gnd n_br_"+str(1)+" gnd vdd gnd memorycell\n")
    the_file.write("Iread n_br_"+str(1)+" gnd PULSE(0 Rcurrent 0 0 0 4n 8n)\n")

    #left size of sram should produce vdd
    #uncomment the following to set to 0, but the delay will be 0 in that case.
    #the_file.write(".IC V(Xsram"+str(numberofsrams)+".n_1_2) = 0\n")
    #the_file.write(".IC V(Xsram"+str(numberofsrams)+".n_1_1) = 'supply_v'\n")
    #the_file.write(".IC V(Xsram"+str(numberofsrams)+".n_1_2) = 0\n")
    #the_file.write(".IC V(Xsram"+str(numberofsrams)+".n_1_1) = 'supply_v'\n")
    #we'll sense the left side of the sram
    #precharge bitlines
    the_file.write(".IC V(n_bl_"+str(numberofsrams)+") = 'supply_v'\n")
    the_file.write(".IC V(n_br_"+str(numberofsrams)+") = 'supply_v'\n")
    the_file.write(".IC V(tgate_l) = 'supply_v'\n")
    the_file.write(".IC V(tgate_r) = 'supply_v'\n")
    #samp produces the opposite value at the start
    #This part can actually be set to any value because it will be overwritten by the bl and br lines.
    the_file.write(".IC V(xsamp1.n_1_2) = 'supply_v'\n")
    the_file.write(".IC V(xsamp1.n_1_1) = 'supply_v'\n")
    #tgates on path:
    the_file.write("xtgate1 n_bl_"+str(numberofsrams)+" tgate_l vdd gnd vdd gnd RAM_tgate\n")
    the_file.write("xtgater n_br_"+str(numberofsrams)+" tgate_r vdd gnd vdd gnd RAM_tgate\n")
    #samp and column decoder:
    the_file.write("xwrite gnd gnd tgate_l tgate_r vdd gnd writedriver\n")
    the_file.write("xsamp1 n_in tgate_l tgate_r n_out vdd_se gnd samp1\n")

    the_file.write(".END")
    the_file.close()

    # Come out of top-level directory
    os.chdir("../")

    return (name + "/" + name + ".sp")



# This is the sense amplifier for SRAM-based BRAMs:
def generate_samp_top_part2_lp(name, numberofsrams, difference):

    # Create directories
    if not os.path.exists(name):
        os.makedirs(name)  
    # Change to directory    
    os.chdir(name)

    filename = name + ".sp"
    the_file = open(filename, 'w')
    the_file.write(".TITLE Sense amp\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Include libraries, parameters and other\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".LIB \"../includes.l\" INCLUDES\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Setup and input\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".TRAN 1p 4n SWEEP DATA=sweep_data\n")
    the_file.write(".OPTIONS BRIEF=1\n\n")
    the_file.write("* Input signal\n")
    the_file.write("VIN n_in gnd PULSE ( supply_v_lp 0 0 0 0 4n 8n)\n")
    the_file.write("VIww wordline gnd PULSE (0 supply_v_lp 0 0 0 4n 8n)\n")
    the_file.write("* Power rail for the circuit under test.\n")
    the_file.write("* This allows us to measure power of a circuit under test without measuring the power of wave shaping and load circuitry.\n")
    the_file.write("V_se vdd_se gnd supply_v_lp\n\n")

    #fall time is meaningless in precharge circuitry. I'll keep the format to make things easier.

    the_file.write("********************************************************************************\n")
    the_file.write("** Measurement\n")
    the_file.write("********************************************************************************\n\n")


    the_file.write("* Total delays\n")
    the_file.write(".MEASURE TRAN meas_total_tfall TRIG V(n_in) VAL='sense_v' FALL=1\n")
    the_file.write("+    TARG V(xsamp1.n_1_2) VAL='sense_v' FALL=1\n")
    # the fall delay is actually 0 for this sense amp, but since the total delay is equal to rise delay, I'll just measure it as that so that ERF doesnt fail.
    the_file.write(".MEASURE TRAN meas_total_trise TRIG V(n_in) VAL='sense_v' FALL=1\n")
    the_file.write("+    TARG V(xsamp1.n_1_2) VAL='sense_v' FALL=1\n\n")

    #the_file.write(".MEASURE TRAN meas_logic_low_voltage FIND V(gnd) AT=1n\n\n")
    #the_file.write(".MEASURE TRAN meas_logic_low_voltage FIND V(gnd) AT=1n\n\n")
    the_file.write(".MEASURE TRAN meas_logic_low_voltage FIND V(gnd) AT=1n\n\n")


    the_file.write("* Measure the power required to propagate a rise and a fall transition through the subcircuit at 250MHz.\n")
    the_file.write(".MEASURE TRAN meas_current INTEGRAL I(V_se) FROM=0ns TO=4ns\n")

    the_file.write(".MEASURE TRAN meas_avg_power PARAM = '-(meas_current/4n)*supply_v_lp'\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Circuit\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write("xprecharge vdd_lp n_bl_0 n_br_0 vdd_lp gnd precharge\n")
    for i in range(2, numberofsrams+1):
        #the_file.write("Xwire"+str(i)+" n_bl_"+str(i-1)+" n_bl_"+str(i)+" wire Rw=wire_memorycell_vertical_res/"+str(numberofsrams)+" Cw=wire_memorycell_vertical_cap/"+str(numberofsrams)+"\n")
        #the_file.write("Xwirer"+str(i)+" n_br_"+str(i-1)+" n_br_"+str(i)+" wire Rw=wire_memorycell_vertical_res/"+str(numberofsrams)+" Cw=wire_memorycell_vertical_cap/"+str(numberofsrams)+"\n")
        the_file.write("Xwire"+str(i)+" n_bl_"+str(i-1)+" n_bl_"+str(i)+" wire Rw=wire_memorycell_vertical_res/"+str(numberofsrams)+" Cw=wire_memorycell_vertical_cap/"+str(numberofsrams)+"\n")
        the_file.write("Xwirer"+str(i)+" n_br_"+str(i-1)+" n_br_"+str(i)+" wire Rw=wire_memorycell_vertical_res/"+str(numberofsrams)+" Cw= wire_memorycell_vertical_cap/"+str(numberofsrams)+"\n")
        the_file.write("Xsram"+str(i)+" gnd gnd n_bl_"+str(i)+" gnd n_br_"+str(i)+" gnd vdd_lp gnd memorycell\n")

    #the_file.write("Xwire"+str(1)+" n_bl_"+str(0)+" n_bl_"+str(1)+" wire Rw=wire_memorycell_vertical_res/"+str(numberofsrams)+" Cw=wire_memorycell_vertical_cap/"+str(numberofsrams)+"\n")
    #the_file.write("Xwirer"+str(1)+" n_br_"+str(0)+" n_br_"+str(1)+" wire Rw=wire_memorycell_vertical_res/"+str(numberofsrams)+" Cw=wire_memorycell_vertical_cap/"+str(numberofsrams)+"\n")
    the_file.write("Xwire"+str(1)+" n_bl_"+str(0)+" n_bl_"+str(1)+" wire Rw=wire_memorycell_vertical_res/"+str(numberofsrams)+" Cw=wire_memorycell_vertical_cap/"+str(numberofsrams)+"\n")
    the_file.write("Xwirer"+str(1)+" n_br_"+str(0)+" n_br_"+str(1)+" wire Rw=wire_memorycell_vertical_res/"+str(numberofsrams)+" Cw=wire_memorycell_vertical_cap/"+str(numberofsrams)+"\n")
    the_file.write("Xsram"+str(1)+" gnd gnd n_bl_"+str(1)+" gnd n_br_"+str(1)+" gnd vdd_lp gnd memorycell\n")
    the_file.write("Iread n_br_"+str(1)+" gnd PULSE(0 Rcurrent 0 0 0 4n 8n)\n")

    #left size of sram should produce vdd
    #uncomment the following to set to 0, but the delay will be 0 in that case.
    #the_file.write(".IC V(Xsram"+str(numberofsrams)+".n_1_2) = 0\n")
    #the_file.write(".IC V(Xsram"+str(numberofsrams)+".n_1_1) = 'supply_v'\n")
    #the_file.write(".IC V(Xsram"+str(numberofsrams)+".n_1_2) = 0\n")
    #the_file.write(".IC V(Xsram"+str(numberofsrams)+".n_1_1) = 'supply_v'\n")
    #we'll sense the left side of the sram
    #precharge bitlines
    the_file.write(".IC V(n_bl_"+str(numberofsrams)+") = 'supply_v_lp'\n")
    the_file.write(".IC V(n_br_"+str(numberofsrams)+") = 'supply_v_lp'\n")
    the_file.write(".IC V(tgate_l) = 'supply_v_lp'\n")
    the_file.write(".IC V(tgate_r) = 'supply_v_lp'\n")
    #samp produces the opposite value at the start
    #This part can actually be set to any value because it will be overwritten by the bl and br lines.
    the_file.write(".IC V(xsamp1.n_1_2) = 'supply_v_lp'\n")
    the_file.write(".IC V(xsamp1.n_1_1) = 'supply_v_lp'\n")
    #tgates on path:

    the_file.write("xtgate1 n_bl_"+str(numberofsrams)+" tgate_l vdd_lp gnd vdd_lp gnd RAM_tgate_lp\n")
    the_file.write("xtgater n_br_"+str(numberofsrams)+" tgate_r vdd_lp gnd vdd_lp gnd RAM_tgate_lp\n")
    #samp and column decoder:
    the_file.write("xwrite gnd gnd tgate_l tgate_r vdd_lp gnd writedriver\n")
    the_file.write("xsamp1 gnd tgate_l tgate_r n_out vdd_se gnd samp1\n")

    the_file.write(".END")
    the_file.close()

    # Come out of top-level directory
    os.chdir("../")

    return (name + "/" + name + ".sp")


# This is the sense amplifier for SRAM-based BRAMs:
def generate_samp_top_part1(name, numberofsrams, difference):

    # Create directories
    if not os.path.exists(name):
        os.makedirs(name)  
    # Change to directory    
    os.chdir(name)

    filename = name + ".sp"
    the_file = open(filename, 'w')
    the_file.write(".TITLE Sense amp\n\n")


    the_file.write("********************************************************************************\n")
    the_file.write("** Include libraries, parameters and other\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".LIB \"../includes.l\" INCLUDES\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Setup and input\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".TRAN 1p 4n SWEEP DATA=sweep_data\n")
    the_file.write(".OPTIONS BRIEF=1\n\n")
    the_file.write("* Input signal\n")
    the_file.write("VIN n_in gnd PULSE ( 0 supply_v 0 0 0 4n 8n)\n")
    the_file.write("VIww wordline gnd PULSE (0 supply_v 0 0 0 4n 8n)\n")
    the_file.write("* Power rail for the circuit under test.\n")
    the_file.write("* This allows us to measure power of a circuit under test without measuring the power of wave shaping and load circuitry.\n")
    the_file.write("V_se vdd_se gnd supply_v\n")
    the_file.write("V_left tgate_r gnd supply_v\n")
    the_file.write("V_right tgate_l gnd sense_v\n\n")
    #fall time is meaningless in precharge circuitry. I'll keep the format to make things easier.

    the_file.write("********************************************************************************\n")
    the_file.write("** Measurement\n")
    the_file.write("********************************************************************************\n\n")


    the_file.write("* Total delays\n")
    the_file.write(".MEASURE TRAN meas_total_tfall TRIG V(n_in) VAL='supply_v/2' RISE=1\n")
    the_file.write("+    TARG V(n_out) VAL='sense_v' RISE=1\n")
    # the fall delay is actually 0 for this sense amp, but since the total delay is equal to rise delay, I'll just measure it as that so that ERF doesnt fail.
    the_file.write(".MEASURE TRAN meas_total_trise TRIG V(n_in) VAL='supply_v/2' RISE=1\n")
    the_file.write("+    TARG V(n_out) VAL='sense_v' RISE=1\n\n")

    the_file.write(".MEASURE TRAN meas_logic_low_voltage FIND V(gnd) AT=1n\n\n")
    the_file.write("* Measure the power required to propagate a rise and a fall transition through the subcircuit at 250MHz.\n")
    the_file.write(".MEASURE TRAN meas_current INTEGRAL I(V_se) FROM=0ns TO=4ns\n")
    the_file.write(".MEASURE TRAN meas_avg_power PARAM = '-(meas_current/4n)*supply_v'\n\n")
    
    the_file.write("********************************************************************************\n")
    the_file.write("** Circuit\n")
    the_file.write("********************************************************************************\n\n")
    #samp produces the opposite value at the start
    #This part can actually be set to any value because it will be overwritten by the bl and br lines.
    the_file.write(".IC V(xsamp1.n_1_2) = 'sense_v'\n")
    the_file.write(".IC V(xsamp1.n_1_1) = 'supply_v'\n")

    the_file.write("xsamp1 n_in tgate_l tgate_r n_out vdd_se gnd samp1\n")

    the_file.write(".END")
    the_file.close()

    # Come out of top-level directory
    os.chdir("../")

    return (name + "/" + name + ".sp")




# This is the sense amplifier for SRAM-based BRAMs:
def generate_samp_top_part1_lp(name, numberofsrams, difference):

    # Create directories
    if not os.path.exists(name):
        os.makedirs(name)  
    # Change to directory    
    os.chdir(name)


    # Create the file spice file and fill it with the netlist:
    filename = name + ".sp"
    the_file = open(filename, 'w')
    the_file.write(".TITLE Sense amp\n\n")


    the_file.write("********************************************************************************\n")
    the_file.write("** Include libraries, parameters and other\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".LIB \"../includes.l\" INCLUDES\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Setup and input\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".TRAN 1p 4n SWEEP DATA=sweep_data\n")
    the_file.write(".OPTIONS BRIEF=1\n\n")
    the_file.write("* Input signal\n")
    the_file.write("VIN n_in gnd PULSE ( 0 supply_v_lp 0 0 0 4n 8n)\n")
    the_file.write("VIww wordline gnd PULSE (0 supply_v_lp 0 0 0 4n 8n)\n")
    the_file.write("* Power rail for the circuit under test.\n")
    the_file.write("* This allows us to measure power of a circuit under test without measuring the power of wave shaping and load circuitry.\n")
    the_file.write("V_se vdd_se gnd supply_v_lp\n")
    the_file.write("V_left tgate_r gnd supply_v_lp\n")
    the_file.write("V_right tgate_l gnd sense_v\n\n")
    #fall time is meaningless in precharge circuitry. I'll keep the format to make things easier.

    the_file.write("********************************************************************************\n")
    the_file.write("** Measurement\n")
    the_file.write("********************************************************************************\n\n")


    the_file.write("* Total delays\n")
    the_file.write(".MEASURE TRAN meas_total_tfall TRIG V(n_in) VAL='supply_v_lp/2' RISE=1\n")
    the_file.write("+    TARG V(n_out) VAL='sense_v' RISE=1\n")
    # the fall delay is actually 0 for this sense amp, but since the total delay is equal to rise delay, I'll just measure it as that so that ERF doesnt fail.
    the_file.write(".MEASURE TRAN meas_total_trise TRIG V(n_in) VAL='supply_v_lp/2' RISE=1\n")
    the_file.write("+    TARG V(n_out) VAL='sense_v' RISE=1\n\n")

    the_file.write(".MEASURE TRAN meas_logic_low_voltage FIND V(gnd) AT=1n\n\n")
    the_file.write("* Measure the power required to propagate a rise and a fall transition through the subcircuit at 250MHz.\n")
    the_file.write(".MEASURE TRAN meas_current INTEGRAL I(V_se) FROM=0ns TO=4ns\n")
    the_file.write(".MEASURE TRAN meas_avg_power PARAM = '-(meas_current/4n)*supply_v_lp'\n\n")
    
    the_file.write("********************************************************************************\n")
    the_file.write("** Circuit\n")
    the_file.write("********************************************************************************\n\n")
    #samp produces the opposite value at the start
    #This part can actually be set to any value because it will be overwritten by the bl and br lines.
    the_file.write(".IC V(xsamp1.n_1_2) = 'sense_v'\n")
    the_file.write(".IC V(xsamp1.n_1_1) = 'supply_v_lp'\n")

    the_file.write("xsamp1 n_in tgate_l tgate_r n_out vdd_se gnd samp1\n")

    the_file.write(".END")
    the_file.close()

    # Come out of top-level directory
    os.chdir("../")

    return (name + "/" + name + ".sp")



# This is the sense amplifier for SRAM-based BRAMs:
def generate_samp_top(name, numberofsrams):

    # Create directories
    if not os.path.exists(name):
        os.makedirs(name)  
    # Change to directory    
    os.chdir(name)



    # Create the file spice file and fill it with the netlist:
    filename = name + ".sp"
    the_file = open(filename, 'w')
    the_file.write(".TITLE Sense amp\n\n")



    the_file.write("********************************************************************************\n")
    the_file.write("** Include libraries, parameters and other\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".LIB \"../includes.l\" INCLUDES\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Setup and input\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".TRAN 1p 4n SWEEP DATA=sweep_data\n")
    the_file.write(".OPTIONS BRIEF=1\n\n")
    the_file.write("* Input signal\n")
    the_file.write("VIN n_in gnd PULSE ( 0 supply_v 400p 0 0 4n 8n)\n")
    the_file.write("VIww wordline gnd PULSE (0 supply_v 0 0 0 4n 8n)\n")
    the_file.write("* Power rail for the circuit under test.\n")
    the_file.write("* This allows us to measure power of a circuit under test without measuring the power of wave shaping and load circuitry.\n")
    the_file.write("V_se vdd_se gnd supply_v\n\n")

    #fall time is meaningless in precharge circuitry. I'll keep the format to make things easier.
    the_file.write("********************************************************************************\n")
    the_file.write("** Measurement\n")
    the_file.write("********************************************************************************\n\n")


    the_file.write("* Total delays\n")
    the_file.write(".MEASURE TRAN meas_total_tfall TRIG V(n_in) VAL='supply_v/2' RISE=1\n")
    the_file.write("+    TARG V(n_out) VAL='supply_v/2' RISE=1\n")
    # the fall delay is actually 0 for this sense amp, but since the total delay is equal to rise delay, I'll just measure it as that so that ERF doesnt fail.
    the_file.write(".MEASURE TRAN meas_total_trise TRIG V(n_in) VAL='supply_v/2' RISE=1\n")
    the_file.write("+    TARG V(n_out) VAL='supply_v/2' RISE=1\n\n")

    the_file.write(".MEASURE TRAN meas_logic_low_voltage FIND V(gnd) AT=1n\n\n")
    the_file.write("* Measure the power required to propagate a rise and a fall transition through the subcircuit at 250MHz.\n")
    the_file.write(".MEASURE TRAN meas_current INTEGRAL I(V_se) FROM=0ns TO=4ns\n")
    the_file.write(".MEASURE TRAN meas_avg_power PARAM = '-(meas_current/4n)*supply_v'\n\n")
    
    the_file.write("********************************************************************************\n")
    the_file.write("** Circuit\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write("xprecharge vdd n_bl_0 n_br_0 vdd gnd precharge\n")
    for i in range(2, numberofsrams+1):
        the_file.write("Xwire"+str(i)+" n_bl_"+str(i-1)+" n_bl_"+str(i)+" wire Rw=wire_memorycell_vertical_res/"+str(numberofsrams)+" Cw=wire_memorycell_vertical_cap/"+str(numberofsrams)+"\n")
        the_file.write("Xwirer"+str(i)+" n_br_"+str(i-1)+" n_br_"+str(i)+" wire Rw=wire_memorycell_vertical_res/"+str(numberofsrams)+" Cw=wire_memorycell_vertical_cap/"+str(numberofsrams)+"\n")
        the_file.write("Xsram"+str(i)+" gnd gnd n_bl_"+str(i)+" gnd n_br_"+str(i)+" gnd vdd gnd memorycell\n")

    the_file.write("Xwire"+str(1)+" n_bl_"+str(0)+" n_bl_"+str(1)+" wire Rw=wire_memorycell_vertical_res/"+str(numberofsrams)+" Cw=wire_memorycell_vertical_cap/"+str(numberofsrams)+"\n")
    the_file.write("Xwirer"+str(1)+" n_br_"+str(0)+" n_br_"+str(1)+" wire Rw=wire_memorycell_vertical_res/"+str(numberofsrams)+" Cw=wire_memorycell_vertical_cap/"+str(numberofsrams)+"\n")
    the_file.write("Xsram"+str(1)+" wordline gnd n_bl_"+str(1)+" gnd n_br_"+str(1)+" gnd vdd gnd memorycell\n")

    #left size of sram should produce vdd
    #uncomment the following to set to 0, but the delay will be 0 in that case.
    #the_file.write(".IC V(Xsram"+str(numberofsrams)+".n_1_2) = 0\n")
    #the_file.write(".IC V(Xsram"+str(numberofsrams)+".n_1_1) = 'supply_v'\n")
    the_file.write(".IC V(Xsram"+str(numberofsrams)+".n_1_2) = 0\n")
    the_file.write(".IC V(Xsram"+str(numberofsrams)+".n_1_1) = 'supply_v'\n")
    #we'll sense the left side of the sram
    #precharge bitlines
    the_file.write(".IC V(n_bl_"+str(numberofsrams)+") = 'supply_v'\n")
    the_file.write(".IC V(n_br_"+str(numberofsrams)+") = 'supply_v'\n")
    the_file.write(".IC V(tgate_l) = 'supply_v'\n")
    the_file.write(".IC V(tgate_r) = 'supply_v'\n")
    #samp produces the opposite value at the start
    #This part can actually be set to any value because it will be overwritten by the bl and br lines.
    the_file.write(".IC V(xsamp1.n_1_2) = 'supply_v'\n")
    the_file.write(".IC V(xsamp1.n_1_1) = 'supply_v'\n")
    #tgates on path:
    the_file.write("xtgate1 n_bl_"+str(numberofsrams)+" tgate_l vdd gnd vdd gnd RAM_tgate\n")
    the_file.write("xtgater n_br_"+str(numberofsrams)+" tgate_r vdd gnd vdd gnd RAM_tgate\n")
    #samp and column decoder:
    the_file.write("xwrite gnd gnd tgate_l tgate_r vdd gnd writedriver\n")
    the_file.write("xsamp1 n_in tgate_l tgate_r n_out vdd_se gnd samp1\n")

    the_file.write(".END")
    the_file.close()

    # Come out of top-level directory
    os.chdir("../")

    return (name + "/" + name + ".sp")


# This is the precharge top-level path for SRAM-based BRAMs
def generate_precharge_top(name, numberofsrams):

    # Create directories
    if not os.path.exists(name):
        os.makedirs(name)  
    # Change to directory    
    os.chdir(name)

    filename = name + ".sp"
    the_file = open(filename, 'w')
    the_file.write(".TITLE precharge and equalization\n\n")

    half = 0
    #if there are more than 256 SRAMs, we add an additional precharge at the bototm
    # This modeled by instanciating less SRAM cells
    if numberofsrams == 512:
        half = 1
        numberofsrams2 = 256
    else:
        numberofsrams2 = numberofsrams

    the_file.write("********************************************************************************\n")
    the_file.write("** Include libraries, parameters and other\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".LIB \"../includes.l\" INCLUDES\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Setup and input\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".TRAN 1p 4n SWEEP DATA=sweep_data\n")
    the_file.write(".OPTIONS BRIEF=1\n\n")
    the_file.write("* Input signal\n")
    the_file.write("VIN n_in gnd PULSE (0 supply_v 0 0 0 4n 8n)\n")
    the_file.write("* Power rail for the circuit under test.\n")
    the_file.write("* This allows us to measure power of a circuit under test without measuring the power of wave shaping and load circuitry.\n")
    the_file.write("V_eq vdd_eq gnd supply_v\n\n")

    #fall time is meaningless in precharge circuitry. I'll keep the format to make things easier.

    the_file.write("********************************************************************************\n")
    the_file.write("** Measurement\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write("* Total delays\n")
    the_file.write(".MEASURE TRAN meas_total_tfall TRIG V(v_precharge) VAL='supply_v/2' FALL=1\n")
    the_file.write("+    TARG V(n_bl_"+str(numberofsrams2)+") VAL='0.99*supply_v' RISE=1\n")
    the_file.write(".MEASURE TRAN meas_total_trise TRIG V(v_precharge) VAL='supply_v/2' FALL=1\n")
    the_file.write("+    TARG V(n_bl_"+str(numberofsrams2)+") VAL='0.99*supply_v' RISE=1\n\n")

    the_file.write(".MEASURE TRAN meas_logic_low_voltage FIND V(v_precharge) AT=3n\n\n")
    the_file.write("* Measure the power required to propagate a rise and a fall transition through the subcircuit at 250MHz.\n")
    the_file.write(".MEASURE TRAN meas_current INTEGRAL I(V_eq) FROM=0ns TO=4ns\n")
    if half ==0:
        the_file.write(".MEASURE TRAN meas_avg_power PARAM = '-(meas_current/4n)*supply_v'\n\n")
    else:
        the_file.write(".MEASURE TRAN meas_avg_power PARAM = '-(meas_current/2n)*supply_v'\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Circuit\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write("xinv n_in v_precharge vdd gnd inv l=gate_length w=2*gate_length\n")
    the_file.write("xprecharge v_precharge n_bl_0 n_br_0 vdd_eq gnd precharge\n")
    for i in range(1, numberofsrams2+1):
        the_file.write("Xwire"+str(i)+" n_bl_"+str(i-1)+" n_bl_"+str(i)+" wire Rw=wire_memorycell_vertical_res/"+str(numberofsrams)+" Cw=wire_memorycell_vertical_cap/"+str(numberofsrams)+"\n")
        the_file.write("Xwirer"+str(i)+" n_br_"+str(i-1)+" n_br_"+str(i)+" wire Rw=wire_memorycell_vertical_res/"+str(numberofsrams)+" Cw=wire_memorycell_vertical_cap/"+str(numberofsrams)+"\n")
        the_file.write("Xsram"+str(i)+" gnd gnd n_bl_"+str(i)+" gnd n_br_"+str(i)+" gnd vdd gnd memorycell\n")
    #tgates on path:
    the_file.write("xtgate1 n_bl_"+str(numberofsrams2)+" tgate_l vdd gnd vdd gnd RAM_tgate\n")
    the_file.write("xtgater n_br_"+str(numberofsrams2)+" tgate_r vdd gnd vdd gnd RAM_tgate\n")
    #samp and column decoder:
    the_file.write("xwrite gnd gnd tgate_l tgate_r vdd gnd writedriver\n")
    the_file.write("xsamp1 gnd tgate_l tgate_r n_samp_out vdd gnd samp1\n")

    the_file.write(".IC V(n_bl_0) = 0\n")
    the_file.write(".IC V(n_br_0) = 'supply_v'\n")
    the_file.write(".IC V(tgate_r) = 'supply_v'\n")
    the_file.write(".END")
    the_file.close()

    # Come out of top-level directory
    os.chdir("../")

    return (name + "/" + name + ".sp")


# This is the precharge top-level path for SRAM-based BRAMs
def generate_precharge_top_lp(name, numberofsrams):

    # Create directories
    if not os.path.exists(name):
        os.makedirs(name)  
    # Change to directory    
    os.chdir(name)

    filename = name + ".sp"
    the_file = open(filename, 'w')
    the_file.write(".TITLE precharge and equalization\n\n")

    half = 0
    # if there are more than 256 SRAMs, we add an additional precharge at the bottom
    # This modeled by instanciating less SRAM cells
    if numberofsrams == 512:
        half = 1
        numberofsrams2 = 256
    else:
        numberofsrams2 = numberofsrams


    the_file.write("********************************************************************************\n")
    the_file.write("** Include libraries, parameters and other\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".LIB \"../includes.l\" INCLUDES\n\n")

    the_file.write("********************************************************************************\n")
    the_file.write("** Setup and input\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write(".TRAN 1p 4n SWEEP DATA=sweep_data\n")
    the_file.write(".OPTIONS BRIEF=1\n\n")
    the_file.write("* Input signal\n")
    the_file.write("VIN n_in gnd PULSE (0 supply_v_lp 0 0 0 4n 8n)\n")
    the_file.write("* Power rail for the circuit under test.\n")
    the_file.write("* This allows us to measure power of a circuit under test without measuring the power of wave shaping and load circuitry.\n")
    the_file.write("V_eq vdd_eq gnd supply_v_lp\n\n")

    #fall time is meaningless in precharge circuitry. I'll keep the format to make things easier.

    the_file.write("********************************************************************************\n")
    the_file.write("** Measurement\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write("* Total delays\n")
    the_file.write(".MEASURE TRAN meas_total_tfall TRIG V(v_precharge) VAL='supply_v_lp/2' FALL=1\n")
    the_file.write("+    TARG V(n_bl_"+str(numberofsrams2)+") VAL='0.99*supply_v_lp' RISE=1\n")
    the_file.write(".MEASURE TRAN meas_total_trise TRIG V(v_precharge) VAL='supply_v_lp/2' FALL=1\n")
    the_file.write("+    TARG V(n_bl_"+str(numberofsrams2)+") VAL='0.99*supply_v_lp' RISE=1\n\n")

    the_file.write(".MEASURE TRAN meas_logic_low_voltage FIND V(v_precharge) AT=3n\n\n")
    the_file.write("* Measure the power required to propagate a rise and a fall transition through the subcircuit at 250MHz.\n")
    the_file.write(".MEASURE TRAN meas_current INTEGRAL I(V_eq) FROM=0ns TO=4ns\n")
    if half == 0:
        the_file.write(".MEASURE TRAN meas_avg_power PARAM = '-(meas_current/4n)*supply_v_lp'\n\n")
    else:
        the_file.write(".MEASURE TRAN meas_avg_power PARAM = '-(meas_current/2n)*supply_v_lp'\n\n")
    
    the_file.write("********************************************************************************\n")
    the_file.write("** Circuit\n")
    the_file.write("********************************************************************************\n\n")
    the_file.write("xinv n_in v_precharge vdd_lp gnd inv l=gate_length w=2*gate_length\n")
    the_file.write("xprecharge v_precharge n_bl_0 n_br_0 vdd_eq gnd precharge\n")
    for i in range(1, numberofsrams2+1):
        the_file.write("Xwire"+str(i)+" n_bl_"+str(i-1)+" n_bl_"+str(i)+" wire Rw=wire_memorycell_vertical_res/"+str(numberofsrams)+" Cw=wire_memorycell_vertical_cap/"+str(numberofsrams)+"\n")
        the_file.write("Xwirer"+str(i)+" n_br_"+str(i-1)+" n_br_"+str(i)+" wire Rw=wire_memorycell_vertical_res/"+str(numberofsrams)+" Cw=wire_memorycell_vertical_cap/"+str(numberofsrams)+"\n")
        the_file.write("Xsram"+str(i)+" gnd gnd n_bl_"+str(i)+" gnd n_br_"+str(i)+" gnd vdd gnd memorycell\n")
    #tgates on path:
    the_file.write("xtgate1 n_bl_"+str(numberofsrams2)+" tgate_l vdd_lp gnd vdd_lp gnd RAM_tgate_lp\n")
    the_file.write("xtgater n_br_"+str(numberofsrams2)+" tgate_r vdd_lp gnd vdd_lp gnd RAM_tgate_lp\n")
    #samp and column decoder:
    the_file.write("xwrite gnd gnd tgate_l tgate_r vdd_lp gnd writedriver\n")
    the_file.write("xsamp1 gnd tgate_l tgate_r n_samp_out vdd_lp gnd samp1\n")

    the_file.write(".IC V(n_bl_0) = 0\n")
    the_file.write(".IC V(n_br_0) = 'supply_v_lp'\n")
    the_file.write(".IC V(tgate_r) = 'supply_v_lp'\n")
    the_file.write(".END")
    the_file.close()

    # Come out of top-level directory
    os.chdir("../")

    return (name + "/" + name + ".sp")


def generate_HB_local_mux_top(mux_name, name):
    """ Generate the top level local mux SPICE file """    
    # Create directories
    if not os.path.exists(mux_name):
        os.makedirs(mux_name)  
    # Change to directory    
    os.chdir(mux_name)
    
    connection_block_filename = mux_name + ".sp"
    local_mux_file = open(connection_block_filename, 'w')
    local_mux_file.write(".TITLE RAM Local routing multiplexer\n\n") 
    
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
    
    local_mux_file.write("* Power rail for the circuit under test.\n")
    local_mux_file.write("* This allows us to measure power of a circuit under test without measuring the power of wave shaping and load circuitry.\n")
    local_mux_file.write("V_LOCAL_MUX vdd_local_mux gnd supply_v\n\n")

    local_mux_file.write("********************************************************************************\n")
    local_mux_file.write("** Measurement\n")
    local_mux_file.write("********************************************************************************\n\n")
    local_mux_file.write("* inv_RAM_local_mux_1 delay\n")
    local_mux_file.write(".MEASURE TRAN meas_inv_"+mux_name+"_1_tfall TRIG V(Xlocal_routing_wire_load_1.Xlocal_mux_on_1.n_in) VAL='supply_v/2' FALL=1\n")
    local_mux_file.write("+    TARG V(Xlocal_routing_wire_load_1.Xlocal_mux_on_1.n_1_1) VAL='supply_v/2' FALL=1\n")
    local_mux_file.write(".MEASURE TRAN meas_inv_"+mux_name+"_1_trise TRIG V(Xlocal_routing_wire_load_1.Xlocal_mux_on_1.n_in) VAL='supply_v/2' RISE=1\n")
    local_mux_file.write("+    TARG V(Xlocal_routing_wire_load_1.Xlocal_mux_on_1.n_1_1) VAL='supply_v/2' RISE=1\n\n")

    local_mux_file.write("* inv_RAM_local_mux_2 delay\n")
    local_mux_file.write(".MEASURE TRAN meas_inv_"+mux_name+"_2_tfall TRIG V(Xlocal_routing_wire_load_1.Xlocal_mux_on_1.n_in) VAL='supply_v/2' FALL=1\n")
    local_mux_file.write("+    TARG V(n_1_5) VAL='supply_v/2' FALL=1\n")
    local_mux_file.write(".MEASURE TRAN meas_inv_"+mux_name+"_2_trise TRIG V(Xlocal_routing_wire_load_1.Xlocal_mux_on_1.n_in) VAL='supply_v/2' RISE=1\n")
    local_mux_file.write("+    TARG V(n_1_5) VAL='supply_v/2' RISE=1\n\n")

    local_mux_file.write("* Total delays\n")
    local_mux_file.write(".MEASURE TRAN meas_total_tfall TRIG V(Xlocal_routing_wire_load_1.Xlocal_mux_on_1.n_in) VAL='supply_v/2' FALL=1\n")
    local_mux_file.write("+    TARG V(n_1_5) VAL='supply_v/2' FALL=1\n")
    local_mux_file.write(".MEASURE TRAN meas_total_trise TRIG V(Xlocal_routing_wire_load_1.Xlocal_mux_on_1.n_in) VAL='supply_v/2' RISE=1\n")
    local_mux_file.write("+    TARG V(n_1_5) VAL='supply_v/2' RISE=1\n\n")

    local_mux_file.write(".MEASURE TRAN meas_logic_low_voltage FIND V(n_in) AT=3n\n\n")#check

    local_mux_file.write("* Measure the power required to propagate a rise and a fall transition through the subcircuit at 250MHz.\n")
    local_mux_file.write(".MEASURE TRAN meas_current INTEGRAL I(V_LOCAL_MUX) FROM=0ns TO=4ns\n")
    local_mux_file.write(".MEASURE TRAN meas_avg_power PARAM = '-(meas_current/4n)*supply_v'\n\n")
    
    local_mux_file.write("********************************************************************************\n")
    local_mux_file.write("** Circuit\n")
    local_mux_file.write("********************************************************************************\n\n")
    local_mux_file.write("Xsb_mux_on_1 n_in n_1_1 vsram vsram_n vdd gnd sb_mux_on\n")
    local_mux_file.write("Xrouting_wire_load_1 n_1_1 n_1_2 n_1_3 vsram vsram_n vdd gnd vdd vdd routing_wire_load\n")
    local_mux_file.write("Xlocal_routing_wire_load_1 n_1_3 n_1_4 vsram vsram_n vdd gnd vdd_local_mux "+name+"_local_routing_wire_load\n")
    # the inputs have to be registered, but we don't know where EDI places them.
    # therefore, I'll add a considerably long wire here (calculated in fpga.py)
    local_mux_file.write("Xwirer_edi n_1_4 n_1_5 wire Rw=wire_"+name+"_1_res Cw=wire_"+name+"_1_cap \n")
    local_mux_file.write("Xff n_1_5 n_hang1 vsram vsram_n vdd gnd gnd vdd gnd vdd vdd gnd ff\n\n")
    local_mux_file.write(".END")
    local_mux_file.close()

    # Come out of top-level directory
    os.chdir("../")
    
    return (mux_name + "/" + mux_name + ".sp")





def generate_RAM_local_mux_top(mux_name):
    """ Generate the top level local mux SPICE file """
    
    # Create directories
    if not os.path.exists(mux_name):
        os.makedirs(mux_name)  
    # Change to directory    
    os.chdir(mux_name)
    
    connection_block_filename = mux_name + ".sp"
    local_mux_file = open(connection_block_filename, 'w')
    local_mux_file.write(".TITLE RAM Local routing multiplexer\n\n") 
    
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
    
    local_mux_file.write("* Power rail for the circuit under test.\n")
    local_mux_file.write("* This allows us to measure power of a circuit under test without measuring the power of wave shaping and load circuitry.\n")
    local_mux_file.write("V_LOCAL_MUX vdd_local_mux gnd supply_v\n\n")

    local_mux_file.write("********************************************************************************\n")
    local_mux_file.write("** Measurement\n")
    local_mux_file.write("********************************************************************************\n\n")
    local_mux_file.write("* inv_RAM_local_mux_1 delay\n")
    local_mux_file.write(".MEASURE TRAN meas_inv_RAM_local_mux_1_tfall TRIG V(Xlocal_routing_wire_load_1.XRAM_local_mux_on_1.n_in) VAL='supply_v/2' RISE=1\n")
    local_mux_file.write("+    TARG V(n_1_4) VAL='supply_v/2' FALL=1\n")
    local_mux_file.write(".MEASURE TRAN meas_inv_RAM_local_mux_1_trise TRIG V(Xlocal_routing_wire_load_1.XRAM_local_mux_on_1.n_in) VAL='supply_v/2' FALL=1\n")
    local_mux_file.write("+    TARG V(n_1_4) VAL='supply_v/2' RISE=1\n\n")
    local_mux_file.write("* Total delays\n")
    local_mux_file.write(".MEASURE TRAN meas_total_tfall TRIG V(Xlocal_routing_wire_load_1.XRAM_local_mux_on_1.n_in) VAL='supply_v/2' RISE=1\n")
    local_mux_file.write("+    TARG V(n_1_4) VAL='supply_v/2' FALL=1\n")
    local_mux_file.write(".MEASURE TRAN meas_total_trise TRIG V(Xlocal_routing_wire_load_1.XRAM_local_mux_on_1.n_in) VAL='supply_v/2' FALL=1\n")
    local_mux_file.write("+    TARG V(n_1_4) VAL='supply_v/2' RISE=1\n\n")

    local_mux_file.write(".MEASURE TRAN meas_logic_low_voltage FIND V(n_in) AT=3n\n\n")#check

    local_mux_file.write("* Measure the power required to propagate a rise and a fall transition through the subcircuit at 250MHz.\n")
    local_mux_file.write(".MEASURE TRAN meas_current INTEGRAL I(V_LOCAL_MUX) FROM=0ns TO=4ns\n")
    local_mux_file.write(".MEASURE TRAN meas_avg_power PARAM = '-(meas_current/4n)*supply_v'\n\n")
    
    local_mux_file.write("********************************************************************************\n")
    local_mux_file.write("** Circuit\n")
    local_mux_file.write("********************************************************************************\n\n")
    local_mux_file.write("Xsb_mux_on_1 n_in n_1_1 vsram vsram_n vdd gnd sb_mux_on\n")
    local_mux_file.write("Xrouting_wire_load_1 n_1_1 n_1_2 n_1_3 vsram vsram_n vdd gnd vdd vdd routing_wire_load\n")
    local_mux_file.write("Xlocal_routing_wire_load_1 n_1_3 n_1_4 vsram vsram_n vdd gnd vdd_local_mux RAM_local_routing_wire_load\n")
    local_mux_file.write("Xff n_1_4 n_hang1 vsram vsram_n vdd gnd gnd vdd gnd vdd vdd gnd ff\n\n")
    #im putting a flip flop here for now, if we are going to move it, this needs to change.
    local_mux_file.write(".END")
    local_mux_file.close()

    # Come out of top-level directory
    os.chdir("../")
    
    return (mux_name + "/" + mux_name + ".sp")



def generate_RAM_local_mux_top_lp(mux_name):
    """ Generate the top level local mux SPICE file """
    
    # Create directories
    if not os.path.exists(mux_name):
        os.makedirs(mux_name)  
    # Change to directory    
    os.chdir(mux_name)
    
    connection_block_filename = mux_name + ".sp"
    local_mux_file = open(connection_block_filename, 'w')
    local_mux_file.write(".TITLE RAM Local routing multiplexer\n\n") 
    
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
    
    local_mux_file.write("* Power rail for the circuit under test.\n")
    local_mux_file.write("* This allows us to measure power of a circuit under test without measuring the power of wave shaping and load circuitry.\n")
    local_mux_file.write("V_LOCAL_MUX vdd_local_mux gnd supply_v\n\n")

    local_mux_file.write("********************************************************************************\n")
    local_mux_file.write("** Measurement\n")
    local_mux_file.write("********************************************************************************\n\n")
    local_mux_file.write("* inv_RAM_local_mux_1 delay\n")
    local_mux_file.write(".MEASURE TRAN meas_inv_RAM_local_mux_1_tfall TRIG V(Xlocal_routing_wire_load_1.XRAM_local_mux_on_1.n_in) VAL='supply_v/2' RISE=1\n")
    local_mux_file.write("+    TARG V(n_1_4) VAL='supply_v/2' FALL=1\n")
    local_mux_file.write(".MEASURE TRAN meas_inv_RAM_local_mux_1_trise TRIG V(Xlocal_routing_wire_load_1.XRAM_local_mux_on_1.n_in) VAL='supply_v/2' FALL=1\n")
    local_mux_file.write("+    TARG V(n_1_4) VAL='supply_v/2' RISE=1\n\n")

    #local_mux_file.write(".MEASURE TRAN meas_inv_RAM_local_mux_2_tfall TRIG V(XCSVL.n_in) VAL='supply_v/2' RISE=1\n")
    #local_mux_file.write("+    TARG V(XCSVL.n_1_1) VAL='supply_v/2' FALL=1\n")
    #local_mux_file.write(".MEASURE TRAN meas_inv_RAM_local_mux_2_trise TRIG V(XCSVL.n_in) VAL='supply_v/2' FALL=1\n")
    #local_mux_file.write("+    TARG V(XCSVL.n_1_1) VAL='supply_v/2' RISE=1\n\n")

    #local_mux_file.write(".MEASURE TRAN meas_inv_RAM_local_mux_3_tfall TRIG V(Xlocal_routing_wire_load_1.XRAM_local_mux_on_1.n_in) VAL='supply_v/2' RISE=1\n")
    #local_mux_file.write("+    TARG V(XCSVL.n_out) VAL='supply_v/2' FALL=1\n")
    #local_mux_file.write(".MEASURE TRAN meas_inv_RAM_local_mux_3_trise TRIG V(Xlocal_routing_wire_load_1.XRAM_local_mux_on_1.n_in) VAL='supply_v/2' FALL=1\n")
    #local_mux_file.write("+    TARG V(XCSVL.n_out) VAL='supply_v/2' RISE=1\n\n")

    local_mux_file.write("* Total delays\n")
    local_mux_file.write(".MEASURE TRAN meas_total_tfall TRIG V(Xlocal_routing_wire_load_1.XRAM_local_mux_on_1.n_in) VAL='supply_v/2' RISE=1\n")
    local_mux_file.write("+    TARG V(n_1_5) VAL='supply_v_lp/2' FALL=1\n")
    local_mux_file.write(".MEASURE TRAN meas_total_trise TRIG V(Xlocal_routing_wire_load_1.XRAM_local_mux_on_1.n_in) VAL='supply_v/2' FALL=1\n")
    local_mux_file.write("+    TARG V(n_1_5) VAL='supply_v_lp/2' RISE=1\n\n")

    local_mux_file.write(".MEASURE TRAN meas_logic_low_voltage FIND V(n_in) AT=3n\n\n")#check
    local_mux_file.write(".MEASURE TRAN test1 FIND V(n_1_5) AT=1.99n\n\n")#check
    local_mux_file.write(".MEASURE TRAN test11 FIND V(XCSVL.n_in) AT=1.99n\n\n")#check
    local_mux_file.write(".MEASURE TRAN test12 FIND V(XCSVL.n_1_1) AT=1.99n\n\n")#check
    local_mux_file.write(".MEASURE TRAN test13 FIND V(XCSVL.n_out) AT=1.99n\n\n")#check
    local_mux_file.write(".MEASURE TRAN test14 FIND V(XCSVL.n_out_b) AT=1.99n\n\n")#check
    local_mux_file.write(".MEASURE TRAN test31 FIND V(n_1_5) AT=3.99n\n\n")#check
    local_mux_file.write(".MEASURE TRAN test15 FIND V(XCSVL.n_in) AT=3.99n\n\n")#check
    local_mux_file.write(".MEASURE TRAN test16 FIND V(XCSVL.n_1_1) AT=3.99n\n\n")#check
    local_mux_file.write(".MEASURE TRAN test17 FIND V(XCSVL.n_out) AT=3.99n\n\n")#check
    local_mux_file.write(".MEASURE TRAN test18 FIND V(XCSVL.n_out_b) AT=3.99n\n\n")#check
    local_mux_file.write("* Measure the power required to propagate a rise and a fall transition through the subcircuit at 250MHz.\n")
    local_mux_file.write(".MEASURE TRAN meas_current INTEGRAL I(V_LOCAL_MUX) FROM=0ns TO=4ns\n")
    local_mux_file.write(".MEASURE TRAN meas_avg_power PARAM = '-(meas_current/4n)*supply_v'\n\n")
    
    local_mux_file.write("********************************************************************************\n")
    local_mux_file.write("** Circuit\n")
    local_mux_file.write("********************************************************************************\n\n")
    local_mux_file.write("Xsb_mux_on_1 n_in n_1_1 vsram vsram_n vdd gnd sb_mux_on\n")
    local_mux_file.write("Xrouting_wire_load_1 n_1_1 n_1_2 n_1_3 vsram vsram_n vdd gnd vdd vdd routing_wire_load\n")
    local_mux_file.write("Xlocal_routing_wire_load_1 n_1_3 n_1_4 vsram vsram_n vdd gnd vdd_local_mux RAM_local_routing_wire_load\n")
    local_mux_file.write("XCSVL n_1_4 n_1_5 vdd vdd_lp gnd CSVL\n")
    local_mux_file.write("Xff n_1_5 n_hang1 vsram vsram_n vdd_lp gnd gnd vdd_lp gnd vdd_lp vdd gnd ff\n\n")
    #im putting a flip flop here for now, if we are going to move it, this needs to change.
    local_mux_file.write(".END")
    local_mux_file.close()

    # Come out of top-level directory
    os.chdir("../")
    
    return (mux_name + "/" + mux_name + ".sp")
    
def generate_lut6_top(lut_name, use_tgate):
    """ Generate the top level 6-LUT SPICE file """

    """
    TODO:
    - This should be modified for the case of FLUTs since the LUTs in this case are loaded differently
      they are loaded with a full adder and the input to the flut mux and not with the lut output load.
    """

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
	
    lut_file.write(".MEASURE TRAN info_node1_lut_tfall TRIG V(n_in) VAL='supply_v/2' FALL=1\n")
    lut_file.write("+    TARG V(Xlut.n_3_1) VAL='supply_v/2' FALL=1\n")
    lut_file.write(".MEASURE TRAN info_node1_lut_trise TRIG V(n_in) VAL='supply_v/2' RISE=1\n")
    lut_file.write("+    TARG V(Xlut.n_3_1) VAL='supply_v/2' RISE=1\n\n") 

    lut_file.write(".MEASURE TRAN info_node2_lut_tfall TRIG V(n_in) VAL='supply_v/2' FALL=1\n")
    lut_file.write("+    TARG V(Xlut.n_4_1) VAL='supply_v/2' FALL=1\n")
    lut_file.write(".MEASURE TRAN info_node2_lut_trise TRIG V(n_in) VAL='supply_v/2' RISE=1\n")
    lut_file.write("+    TARG V(Xlut.n_4_1) VAL='supply_v/2' RISE=1\n\n")     

    lut_file.write(".MEASURE TRAN info_node3_lut_tfall TRIG V(n_in) VAL='supply_v/2' FALL=1\n")
    lut_file.write("+    TARG V(Xlut.n_7_1) VAL='supply_v/2' FALL=1\n")
    lut_file.write(".MEASURE TRAN info_node3_lut_trise TRIG V(n_in) VAL='supply_v/2' RISE=1\n")
    lut_file.write("+    TARG V(Xlut.n_7_1) VAL='supply_v/2' RISE=1\n\n")   

    lut_file.write(".MEASURE TRAN info_node4_lut_tfall TRIG V(n_in) VAL='supply_v/2' FALL=1\n")
    lut_file.write("+    TARG V(Xlut.n_8_1) VAL='supply_v/2' FALL=1\n")
    lut_file.write(".MEASURE TRAN info_node4_lut_trise TRIG V(n_in) VAL='supply_v/2' RISE=1\n")
    lut_file.write("+    TARG V(Xlut.n_8_1) VAL='supply_v/2' RISE=1\n\n")   


    lut_file.write(".MEASURE TRAN info_node5_lut_tfall TRIG V(n_in) VAL='supply_v/2' FALL=1\n")
    lut_file.write("+    TARG V(Xlut.n_9_1) VAL='supply_v/2' FALL=1\n")
    lut_file.write(".MEASURE TRAN info_node5_lut_trise TRIG V(n_in) VAL='supply_v/2' RISE=1\n")
    lut_file.write("+    TARG V(Xlut.n_9_1) VAL='supply_v/2' RISE=1\n\n")   
    lut_file.write("********************************************************************************\n")
    lut_file.write("** Circuit\n")
    lut_file.write("********************************************************************************\n\n")

    if not use_tgate :
        lut_file.write("Xlut n_in n_out vdd vdd vdd vdd vdd vdd vdd gnd lut\n\n")
        lut_file.write("Xlut_output_load n_out n_local_out n_general_out vsram vsram_n vdd gnd vdd vdd lut_output_load\n\n")
    else :
        lut_file.write("Xlut n_in n_out vdd gnd vdd gnd vdd gnd vdd gnd vdd gnd vdd gnd vdd gnd lut\n\n")
        lut_file.write("Xlut_output_load n_out n_local_out n_general_out vsram vsram_n vdd gnd vdd vdd lut_output_load\n\n")
    
    lut_file.write(".END")
    lut_file.close()

    # Come out of lut directory
    os.chdir("../")
    
    return (lut_name + "/" + lut_name + ".sp")
 

def generate_lut5_top(lut_name, use_tgate):
    """ Generate the top level 5-LUT SPICE file """

    
    # TODO:
    # This should be modified for the case of FLUTs since the LUTs in this case are loaded differently
    # they are loaded with a full adder and the input to the flut mux and not with the lut output load.
    

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
    if not use_tgate :
        lut_file.write("Xlut n_in n_out vdd vdd vdd vdd vdd vdd vdd gnd lut\n\n")
        lut_file.write("Xlut_output_load n_out n_local_out n_general_out vsram vsram_n vdd gnd vdd vdd lut_output_load\n\n")
    else :
        lut_file.write("Xlut n_in n_out vdd gnd vdd gnd vdd gnd vdd gnd vdd gnd vdd gnd vdd gnd lut\n\n")
        lut_file.write("Xlut_output_load n_out n_local_out n_general_out vsram vsram_n vdd gnd vdd vdd lut_output_load\n\n")
    
    lut_file.write(".END")
    lut_file.close()

    # Come out of lut directory
    os.chdir("../")
    
    return (lut_name + "/" + lut_name + ".sp") 
 

def generate_lut4_top(lut_name, use_tgate):
    """ Generate the top level 4-LUT SPICE file """

    
    # TODO:
    # This should be modified for the case of FLUTs since the LUTs in this case are loaded differently
    # they are loaded with a full adder and the input to the flut mux and not with the lut output load.
    

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
    if not use_tgate :
        lut_file.write("Xlut n_in n_out vdd vdd vdd vdd vdd vdd vdd gnd lut\n\n")
        lut_file.write("Xlut_output_load n_out n_local_out n_general_out vsram vsram_n vdd gnd vdd vdd lut_output_load\n\n")
    else :
        lut_file.write("Xlut n_in n_out vdd gnd vdd gnd vdd gnd vdd gnd vdd gnd vdd gnd vdd gnd lut\n\n")
        lut_file.write("Xlut_output_load n_out n_local_out n_general_out vsram vsram_n vdd gnd vdd vdd lut_output_load\n\n")

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
    input_driver_file.write("* Power rail for the circuit under test.\n")
    input_driver_file.write("* This allows us to measure power of a circuit under test without measuring the power of wave shaping and load circuitry.\n")
    input_driver_file.write("V_LUT_DRIVER vdd_lut_driver gnd supply_v\n\n")

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

    input_driver_file.write(".MEASURE TRAN meas_logic_low_voltage FIND V(n_out) AT=3n\n\n")

    input_driver_file.write("* Measure the power required to propagate a rise and a fall transition through the lut driver at 250MHz.\n")
    input_driver_file.write(".MEASURE TRAN meas_current INTEGRAL I(V_LUT_DRIVER) FROM=0ns TO=4ns\n")
    input_driver_file.write(".MEASURE TRAN meas_avg_power PARAM = '-((meas_current)/4n)*supply_v'\n\n")

    input_driver_file.write("********************************************************************************\n")
    input_driver_file.write("** Circuit\n")
    input_driver_file.write("********************************************************************************\n\n")
    input_driver_file.write("Xcb_mux_on_1 n_in n_1_1 vsram vsram_n vdd gnd cb_mux_on\n")
    input_driver_file.write("Xlocal_routing_wire_load_1 n_1_1 n_1_2 vsram vsram_n vdd gnd vdd local_routing_wire_load\n")
    input_driver_file.write("X" + input_driver_name + "_1 n_1_2 n_out vsram vsram_n n_rsel n_2_1 vdd_lut_driver gnd " + input_driver_name + "\n")
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
    input_driver_file.write("* Power rail for the circuit under test.\n")
    input_driver_file.write("* This allows us to measure power of a circuit under test without measuring the power of wave shaping and load circuitry.\n")
    input_driver_file.write("V_LUT_DRIVER vdd_lut_driver gnd supply_v\n\n")
    
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

    input_driver_file.write(".MEASURE TRAN meas_logic_low_voltage FIND V(n_out) AT=3n\n\n")
    
    input_driver_file.write("* Measure the power required to propagate a rise and a fall transition through the lut driver at 250MHz.\n")
    input_driver_file.write(".MEASURE TRAN meas_current INTEGRAL I(V_LUT_DRIVER) FROM=0ns TO=4ns\n")
    input_driver_file.write(".MEASURE TRAN meas_avg_power PARAM = '-((meas_current)/4n)*supply_v'\n\n")

    input_driver_file.write("********************************************************************************\n")
    input_driver_file.write("** Circuit\n")
    input_driver_file.write("********************************************************************************\n\n")
    input_driver_file.write("Xcb_mux_on_1 n_in n_1_1 vsram vsram_n vdd gnd cb_mux_on\n")
    input_driver_file.write("Xlocal_routing_wire_load_1 n_1_1 n_1_2 vsram vsram_n vdd gnd vdd local_routing_wire_load\n")
    input_driver_file.write("X" + input_driver_name_no_not + "_1 n_1_2 n_out vsram vsram_n n_rsel n_2_1 vdd gnd " + input_driver_name_no_not + "\n")
    if input_driver_type == "default_rsel" or input_driver_type == "reg_fb_rsel":
        # Connect a load to n_rsel node
        input_driver_file.write("Xff n_rsel n_ff_out vsram vsram_n gnd vdd gnd vdd gnd vdd vdd gnd ff\n")
    input_driver_file.write("X" + input_driver_name + "_1 n_2_1 n_out_n vdd_lut_driver gnd " + input_driver_name + "\n")
    input_driver_file.write("X" + input_driver_name_no_not + "_load_1 n_out n_vdd n_gnd " + input_driver_name_no_not + "_load\n")
    input_driver_file.write("X" + input_driver_name_no_not + "_load_2 n_out_n n_vdd n_gnd " + input_driver_name_no_not + "_load\n\n")
    input_driver_file.write(".END")
    input_driver_file.close()

    # Come out of lut_driver directory
    os.chdir("../")
    
    return (input_driver_name_no_not + "/" + input_driver_name + ".sp")    
   
  
def generate_lut_and_driver_top(input_driver_name, input_driver_type, use_tgate, use_fluts):
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
    # spice_file.write(".OPTIONS POST=2\n\n")
    
    spice_file.write("********************************************************************************\n")
    spice_file.write("** Setup and input\n")
    spice_file.write("********************************************************************************\n\n")
    spice_file.write(".TRAN 1p 16n SWEEP DATA=sweep_data\n")
    spice_file.write(".OPTIONS BRIEF=1\n\n")
    spice_file.write("* Input signal\n")
    spice_file.write("VIN_SRAM n_in_sram gnd PULSE (0 supply_v 4n 0 0 4n 8n)\n")
    spice_file.write("VIN_GATE n_in_gate gnd PULSE (supply_v 0 3n 0 0 2n 4n)\n\n")
    spice_file.write("* Power rail for the circuit under test.\n")
    spice_file.write("* This allows us to measure power of a circuit under test without measuring the power of wave shaping and load circuitry.\n")
    spice_file.write("V_LUT vdd_lut gnd supply_v\n\n")

    spice_file.write("********************************************************************************\n")
    spice_file.write("** Measurement\n")
    spice_file.write("********************************************************************************\n\n")
    spice_file.write("* Total delays\n")
    spice_file.write(".MEASURE TRAN meas_total_tfall TRIG V(n_3_1) VAL='supply_v/2' RISE=2\n")
    spice_file.write("+    TARG V(n_out) VAL='supply_v/2' FALL=1\n")
    spice_file.write(".MEASURE TRAN meas_total_trise TRIG V(n_3_1) VAL='supply_v/2' RISE=1\n")
    spice_file.write("+    TARG V(n_out) VAL='supply_v/2' RISE=1\n\n")
    
    spice_file.write(".MEASURE TRAN meas_logic_low_voltage FIND V(n_out) AT=3n\n\n")

    spice_file.write("* Measure the power required to propagate a rise and a fall transition through the lut at 250MHz.\n")
    spice_file.write(".MEASURE TRAN meas_current1 INTEGRAL I(V_LUT) FROM=5ns TO=7ns\n")
    spice_file.write(".MEASURE TRAN meas_current2 INTEGRAL I(V_LUT) FROM=9ns TO=11ns\n")
    spice_file.write(".MEASURE TRAN meas_avg_power PARAM = '-((meas_current1 + meas_current2)/4n)*supply_v'\n\n")

    spice_file.write("********************************************************************************\n")
    spice_file.write("** Circuit\n")
    spice_file.write("********************************************************************************\n\n")    
    spice_file.write("Xcb_mux_on_1 n_in_gate n_1_1 vsram vsram_n vdd gnd cb_mux_on\n")
    spice_file.write("Xlocal_routing_wire_load_1 n_1_1 n_1_2 vsram vsram_n vdd gnd vdd local_routing_wire_load\n")
    spice_file.write("X" + input_driver_name + "_1 n_1_2 n_3_1 vsram vsram_n n_rsel n_2_1 vdd gnd " + input_driver_name + "\n")

    # Connect a load to n_rsel node
    if input_driver_type == "default_rsel" or input_driver_type == "reg_fb_rsel":
        spice_file.write("Xff n_rsel n_ff_out vsram vsram_n gnd vdd gnd vdd gnd vdd vdd gnd ff\n")
    spice_file.write("X" + input_driver_name + "_not_1 n_2_1 n_1_4 vdd gnd " + input_driver_name + "_not\n")

    # Connect the LUT driver to a different LUT input based on LUT driver name and connect the other inputs to vdd
    # pass- transistor ----> "Xlut n_in_sram n_out a b c d e f vdd_lut gnd lut"
    # transmission gate ---> "Xlut n_in_sram n_out a a_not b b_not c c_not d d_not e e_not f f_not vdd_lut gnd lut"
    lut_letter = input_driver_name.replace("_driver", "")
    lut_letter = lut_letter.replace("lut_", "")
    # string holding lut input connections depending on the driver letter
    lut_input_nodes = ""
    # loop over the letters a -> f
    for letter in range(97,103):
        # if this is the driver connect it to n_3_1 else connect it to vdd
        if chr(letter) == lut_letter:
            lut_input_nodes += "n_3_1 "
            # if tgate connect the complement input to n_1_4
            if use_tgate: lut_input_nodes += "n_1_4 "
        else:
            lut_input_nodes += "vdd "
            # if tgate connect the complement to gnd
            if use_tgate: lut_input_nodes += "gnd "

    spice_file.write("Xlut n_in_sram n_out " + lut_input_nodes + "vdd_lut gnd lut\n")
    
    if use_fluts:
        spice_file.write("Xwireflut n_out n_out2 wire Rw=wire_lut_to_flut_mux_res Cw=wire_lut_to_flut_mux_cap\n") 
        spice_file.write("Xthemux n_out2 n_out3 vdd gnd vdd gnd flut_mux\n") 
    else:
        spice_file.write("Xlut_output_load n_out n_local_out n_general_out vsram vsram_n vdd gnd vdd vdd lut_output_load\n\n")
    
    
    spice_file.write(".END")
    spice_file.close()

    # Come out of lut_driver directory
    os.chdir("../")  
  
    
def generate_local_ble_output_top(name, use_tgate):
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
    top_file.write("* Power rail for the circuit under test.\n")
    top_file.write("* This allows us to measure power of a circuit under test without measuring the power of wave shaping and load circuitry.\n")
    top_file.write("V_LOCAL_OUTPUT vdd_local_output gnd supply_v\n\n")

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

    top_file.write(".MEASURE TRAN meas_logic_low_voltage FIND V(n_local_out) AT=3n\n\n")

    top_file.write("* Measure the power required to propagate a rise and a fall transition through the subcircuit at 250MHz.\n")
    top_file.write(".MEASURE TRAN meas_current INTEGRAL I(V_LOCAL_OUTPUT) FROM=0ns TO=4ns\n")
    top_file.write(".MEASURE TRAN meas_avg_power PARAM = '-((meas_current)/4n)*supply_v'\n\n")

    top_file.write("********************************************************************************\n")
    top_file.write("** Circuit\n")
    top_file.write("********************************************************************************\n\n")
    if not use_tgate :
        top_file.write("Xlut n_in n_1_1 vdd vdd vdd vdd vdd vdd vdd gnd lut\n\n")
        top_file.write("Xlut_output_load n_1_1 n_local_out n_general_out vsram vsram_n vdd gnd vdd_local_output vdd lut_output_load\n\n")
    else :
        top_file.write("Xlut n_in n_1_1 vdd gnd vdd gnd vdd gnd vdd gnd vdd gnd vdd gnd vdd gnd lut\n\n")
        top_file.write("Xlut_output_load n_1_1 n_local_out n_general_out vsram vsram_n vdd gnd vdd_local_output vdd lut_output_load\n\n")

    top_file.write("Xlocal_ble_output_load n_local_out vsram vsram_n vdd gnd local_ble_output_load\n")
    top_file.write(".END")
    top_file.close()

    # Come out of top-level directory
    os.chdir("../")
    
    return (name + "/" + name + ".sp")
    
    
def generate_general_ble_output_top(name, use_tgate):
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
    top_file.write("* Power rail for the circuit under test.\n")
    top_file.write("* This allows us to measure power of a circuit under test without measuring the power of wave shaping and load circuitry.\n")
    top_file.write("V_GENERAL_OUTPUT vdd_general_output gnd supply_v\n\n")

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
    top_file.write("+    TARG V(Xgeneral_ble_output_load.n_meas_point) VAL='supply_v/2' FALL=1\n")
    top_file.write(".MEASURE TRAN meas_inv_general_ble_output_2_trise TRIG V(n_1_1) VAL='supply_v/2' RISE=1\n")
    top_file.write("+    TARG V(Xgeneral_ble_output_load.n_meas_point) VAL='supply_v/2' RISE=1\n\n")
    top_file.write("* Total delays\n")
    top_file.write(".MEASURE TRAN meas_total_tfall TRIG V(n_1_1) VAL='supply_v/2' FALL=1\n")
    top_file.write("+    TARG V(Xgeneral_ble_output_load.n_meas_point) VAL='supply_v/2' FALL=1\n")
    top_file.write(".MEASURE TRAN meas_total_trise TRIG V(n_1_1) VAL='supply_v/2' RISE=1\n")
    top_file.write("+    TARG V(Xgeneral_ble_output_load.n_meas_point) VAL='supply_v/2' RISE=1\n\n")

    top_file.write(".MEASURE TRAN meas_logic_low_voltage FIND V(n_general_out) AT=3n\n\n")

    top_file.write("* Measure the power required to propagate a rise and a fall transition through the subcircuit at 250MHz.\n")
    top_file.write(".MEASURE TRAN meas_current INTEGRAL I(V_GENERAL_OUTPUT) FROM=0ns TO=4ns\n")
    top_file.write(".MEASURE TRAN meas_avg_power PARAM = '-((meas_current)/4n)*supply_v'\n\n")

    top_file.write("********************************************************************************\n")
    top_file.write("** Circuit\n")
    top_file.write("********************************************************************************\n\n")
    if not use_tgate :
        top_file.write("Xlut n_in n_1_1 vdd vdd vdd vdd vdd vdd vdd gnd lut\n\n")
        top_file.write("Xlut_output_load n_1_1 n_local_out n_general_out vsram vsram_n vdd gnd vdd vdd_general_output lut_output_load\n\n")
    else :
        top_file.write("Xlut n_in n_1_1 vdd gnd vdd gnd vdd gnd vdd gnd vdd gnd vdd gnd vdd gnd lut\n\n")
        top_file.write("Xlut_output_load n_1_1 n_local_out n_general_out vsram vsram_n vdd gnd vdd vdd_general_output lut_output_load\n\n")

    top_file.write("Xgeneral_ble_output_load n_general_out n_hang1 vsram vsram_n vdd gnd general_ble_output_load\n")
    top_file.write(".END")
    top_file.close()

    # Come out of top-level directory
    os.chdir("../")
    
    return (name + "/" + name + ".sp")
    


def generate_flut_mux_top(name, use_tgate, enable_carry_chain):
    
    #TODO: 
    #- I think the general ble output load should be removed from this ciruit in case of an ALM
    #  with carry chain. Since, the load in this case is only the carry chain mux. 
    #- I also think that in both cases whether there is a carry chain mux or not the delay should 
    #  be measured between the n_1_1 and n_1_3 and not between n_1_1 and n_local_out.
    
    # Create directories
    if not os.path.exists(name):
        os.makedirs(name)  
    # Change to directory    
    os.chdir(name)  
    
    filename = name + ".sp"
    top_file = open(filename, 'w')
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
    top_file.write("* Power rail for the circuit under test.\n")
    top_file.write("* This allows us to measure power of a circuit under test without measuring the power of wave shaping and load circuitry.\n")
    top_file.write("V_FLUT vdd_f gnd supply_v\n\n")

    top_file.write("********************************************************************************\n")
    top_file.write("** Measurement\n")
    top_file.write("********************************************************************************\n\n")
    top_file.write("* inv_"+ name +"_1 delay\n")
    top_file.write(".MEASURE TRAN meas_inv_"+ name +"_1_tfall TRIG V(n_1_2) VAL='supply_v/2' RISE=1\n")
    top_file.write("+    TARG V(Xthemux.n_2_1) VAL='supply_v/2' FALL=1\n")
    top_file.write(".MEASURE TRAN meas_inv_"+ name +"_1_trise TRIG V(n_1_2) VAL='supply_v/2' FALL=1\n")
    top_file.write("+    TARG V(Xthemux.n_2_1) VAL='supply_v/2' RISE=1\n\n")
    top_file.write("* inv_"+ name +"_2 delays\n")
    top_file.write(".MEASURE TRAN meas_inv_"+ name +"_2_tfall TRIG V(n_1_2) VAL='supply_v/2' FALL=1\n")
    top_file.write("+    TARG V(n_local_out) VAL='supply_v/2' FALL=1\n")
    top_file.write(".MEASURE TRAN meas_inv_"+ name +"_2_trise TRIG V(n_1_2) VAL='supply_v/2' RISE=1\n")
    top_file.write("+    TARG V(n_local_out) VAL='supply_v/2' RISE=1\n\n")
    top_file.write("* Total delays\n")
    top_file.write(".MEASURE TRAN meas_total_tfall TRIG V(n_1_1) VAL='supply_v/2' FALL=1\n")
    #top_file.write("+    TARG V(n_1_3) VAL='supply_v/2' FALL=1\n")
    top_file.write("+    TARG V(n_local_out) VAL='supply_v/2' FALL=1\n")
    top_file.write(".MEASURE TRAN meas_total_trise TRIG V(n_1_1) VAL='supply_v/2' RISE=1\n")
    #top_file.write("+    TARG V(n_1_3) VAL='supply_v/2' RISE=1\n\n")
    top_file.write("+    TARG V(n_local_out) VAL='supply_v/2' RISE=1\n\n")
    top_file.write(".MEASURE TRAN meas_logic_low_voltage FIND V(n_general_out) AT=3n\n\n")

    top_file.write("* Measure the power required to propagate a rise and a fall transition through the subcircuit at 250MHz.\n")
    top_file.write(".MEASURE TRAN meas_current INTEGRAL I(V_FLUT) FROM=0ns TO=4ns\n")
    top_file.write(".MEASURE TRAN meas_avg_power PARAM = '-((meas_current)/4n)*supply_v'\n\n")

    top_file.write("********************************************************************************\n")
    top_file.write("** Circuit\n")
    top_file.write("********************************************************************************\n\n")
    # lut, wire from lut to the mux, the mux, and the load same output load as before
    if not use_tgate :
        top_file.write("Xlut n_in n_1_1 vdd vdd vdd vdd vdd vdd vdd gnd lut\n")
        top_file.write("Xwireflut n_1_1 n_1_2 wire Rw=wire_lut_to_flut_mux_res Cw=wire_lut_to_flut_mux_cap\n")  
        top_file.write("Xthemux n_1_2 n_1_3 vdd gnd vdd_f gnd flut_mux\n")       
        if enable_carry_chain == 1:
            top_file.write("Xwireovercc n_1_3 n_1_4 wire Rw=wire_carry_chain_5_res Cw=wire_carry_chain_5_cap\n")
            top_file.write("Xccmux n_1_4 n_local_out vdd gnd vdd gnd carry_chain_mux\n")   
        else:
            top_file.write("Xlut_output_load n_1_3 n_local_out n_general_out vsram vsram_n vdd gnd vdd vdd lut_output_load\n\n")
    else :
        top_file.write("Xlut n_in n_1_1 vdd gnd vdd gnd vdd gnd vdd gnd vdd gnd vdd gnd vdd gnd lut\n\n")
        top_file.write("Xwireflut n_1_1 n_1_2 wire Rw=wire_lut_to_flut_mux_res Cw=wire_lut_to_flut_mux_cap\n") 
        top_file.write("Xthemux n_1_2 n_1_3 vdd gnd vdd_f gnd flut_mux\n")  
        if enable_carry_chain == 1:
            top_file.write("Xwireovercc n_1_3 n_1_4 wire Rw=wire_carry_chain_5_res Cw=wire_carry_chain_5_cap\n") 
            top_file.write("Xccmux n_1_4 n_local_out vdd gnd vdd gnd carry_chain_mux\n")
        else:
            top_file.write("Xlut_output_load n_1_3 n_local_out n_general_out vsram vsram_n vdd gnd vdd vdd lut_output_load\n\n")

    top_file.write("Xgeneral_ble_output_load n_general_out n_hang1 vsram vsram_n vdd gnd general_ble_output_load\n")
    top_file.write(".END")
    top_file.close()

    # Come out of top-level directory
    os.chdir("../")
    
    return (name + "/" + name + ".sp")


def generate_cc_mux_top(name, use_tgate):
    """ Creating the SPICE netlist for calculating the delay of the carry chain mux"""
    
    # Create directories
    if not os.path.exists(name):
        os.makedirs(name)  
    # Change to directory    
    os.chdir(name)  
    
    filename = name + ".sp"
    top_file = open(filename, 'w')
    top_file.write(".TITLE Carry chain mux\n\n") 
    
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
    top_file.write("* Power rail for the circuit under test.\n")
    top_file.write("* This allows us to measure power of a circuit under test without measuring the power of wave shaping and load circuitry.\n")
    top_file.write("V_FLUT vdd_test gnd supply_v\n\n")

    top_file.write("********************************************************************************\n")
    top_file.write("** Measurement\n")
    top_file.write("********************************************************************************\n\n")
    top_file.write("* inv_"+ name +"_1 delay\n")
    top_file.write(".MEASURE TRAN meas_inv_"+ name +"_1_tfall TRIG V(n_1_4) VAL='supply_v/2' RISE=1\n")
    top_file.write("+    TARG V(Xthemux.n_2_1) VAL='supply_v/2' FALL=1\n")
    top_file.write(".MEASURE TRAN meas_inv_"+ name +"_1_trise TRIG V(n_1_4) VAL='supply_v/2' FALL=1\n")
    top_file.write("+    TARG V(Xthemux.n_2_1) VAL='supply_v/2' RISE=1\n\n")
    top_file.write("* inv_"+ name +"_2 delays\n")
    top_file.write(".MEASURE TRAN meas_inv_"+ name +"_2_tfall TRIG V(n_1_4) VAL='supply_v/2' FALL=1\n")
    top_file.write("+    TARG V(n_local_out) VAL='supply_v/2' FALL=1\n")
    top_file.write(".MEASURE TRAN meas_inv_"+ name +"_2_trise TRIG V(n_1_4) VAL='supply_v/2' RISE=1\n")
    top_file.write("+    TARG V(n_local_out) VAL='supply_v/2' RISE=1\n\n")
    top_file.write("* Total delays\n")
    top_file.write(".MEASURE TRAN meas_total_tfall TRIG V(n_1_4) VAL='supply_v/2' FALL=1\n")
    #top_file.write("+    TARG V(n_1_3) VAL='supply_v/2' FALL=1\n")
    top_file.write("+    TARG V(n_local_out) VAL='supply_v/2' FALL=1\n")
    top_file.write(".MEASURE TRAN meas_total_trise TRIG V(n_1_4) VAL='supply_v/2' RISE=1\n")
    #top_file.write("+    TARG V(n_1_3) VAL='supply_v/2' RISE=1\n\n")
    top_file.write("+    TARG V(n_local_out) VAL='supply_v/2' RISE=1\n\n")
    top_file.write(".MEASURE TRAN meas_logic_low_voltage FIND V(n_general_out) AT=3n\n\n")

    top_file.write("* Measure the power required to propagate a rise and a fall transition through the subcircuit at 250MHz.\n")
    top_file.write(".MEASURE TRAN meas_current INTEGRAL I(V_FLUT) FROM=0ns TO=4ns\n")
    top_file.write(".MEASURE TRAN meas_avg_power PARAM = '-((meas_current)/4n)*supply_v'\n\n")

    top_file.write("********************************************************************************\n")
    top_file.write("** Circuit\n")
    top_file.write("********************************************************************************\n\n")
    # lut, wire from lut to the mux, the mux, and the load same output load as before
    
    top_file.write("Xcarrychain_shape1 vdd gnd n_in n_1_1 n_hang n_p_1 vdd gnd FA_carry_chain\n")
    top_file.write("Xcarrychain_shape2 vdd gnd n_1_1 n_1_2 n_hang_2 n_p_2 vdd gnd FA_carry_chain\n")
    top_file.write("Xcarrychain_shape3 vdd gnd n_1_2 n_hang_3 n_1_3 n_p_3 vdd gnd FA_carry_chain\n")
    top_file.write("Xinv_shape n_1_3 n_1_4 vdd gnd carry_chain_perf\n")
    top_file.write("Xthemux n_1_4 n_1_5 vdd gnd vdd_test gnd carry_chain_mux\n")       
    top_file.write("Xlut_output_load n_1_5 n_local_out n_general_out vsram vsram_n vdd gnd vdd vdd lut_output_load\n\n")


    top_file.write("Xgeneral_ble_output_load n_general_out n_hang1 vsram vsram_n vdd gnd general_ble_output_load\n")
    top_file.write(".END")
    top_file.close()

    # Come out of top-level directory
    os.chdir("../")
    
    return (name + "/" + name + ".sp")


"""
def generate_carrychain_top(name, architecture):
    """ """
    
    # Create directories
    if not os.path.exists(name):
        os.makedirs(name)  
    # Change to directory    
    os.chdir(name)  
    
    filename = name + ".sp"
    top_file = open(filename, 'w')
    top_file.write(".TITLE Carry Chain\n\n") 
    
    top_file.write("********************************************************************************\n")
    top_file.write("** Include libraries, parameters and other\n")
    top_file.write("********************************************************************************\n\n")
    top_file.write(".LIB \"../includes.l\" INCLUDES\n\n")
    
    top_file.write("********************************************************************************\n")
    top_file.write("** Setup and input\n")
    top_file.write("********************************************************************************\n\n")
    top_file.write(".TRAN 1p 26n SWEEP DATA=sweep_data\n")
    top_file.write(".OPTIONS BRIEF=1\n\n")
    top_file.write("* Input signals\n")

    #top_file.write("VIN n_a gnd PWL (0 0 1.999n 0 2n 'supply_v' 3.999n 'supply_v' 4n 0 13.999n 0 14n 'supply_v' 23.999n 'supply_v' 24n 0)\n\n")
    #top_file.write("VIN2 n_b gnd PWL (0 0 5.999n 0 6n supply_v 7.999n supply_v 8n 0 17.999n 0 18n supply_v 19.999n supply_v 20n 0 21.999n 0 22n supply_v)\n\n")
    #top_file.write("VIN3 n_cin gnd PWL (0 0 9.999n 0 10n supply_v 11.999n supply_v 12n 0 13.999n 0 14n supply_v 15.999n supply_v 16n 0 )\n\n")
    top_file.write("VIN n_a gnd PWL (0 0 1.999n 0 2n 'supply_v' 3.999n 'supply_v' 4n 0 13.999n 0 14n 'supply_v' 23.999n 'supply_v' 24n 0)\n\n")
    top_file.write("VIN2 n_b gnd PWL (0 0 5.999n 0 6n supply_v 7.999n supply_v 8n 0 17.999n 0 18n supply_v 19.999n supply_v 20n 0 21.999n 0 22n supply_v)\n\n")
    top_file.write("VIN3 n_cin gnd PWL (0 0 9.999n 0 10n supply_v 11.999n supply_v 12n 0 13.999n 0 14n supply_v 15.999n supply_v 16n 0 )\n\n")

    top_file.write("* Power rail for the circuit under test.\n")
    top_file.write("* This allows us to measure power of a circuit under test without measuring the power of wave shaping and load circuitry.\n")
    top_file.write("V_test vdd_test gnd supply_v\n\n")

    top_file.write("********************************************************************************\n")
    top_file.write("** Measurement\n")
    top_file.write("********************************************************************************\n\n")
    top_file.write("* inv_carry_chain_1 delay\n")
    top_file.write(".MEASURE TRAN meas_inv_carry_chain_1_tfall TRIG V(n_a) VAL='supply_v/2' RISE=1\n")
    top_file.write("+    TARG V(Xcarrychain.n_a_in_bar) VAL='supply_v/2' FALL=1\n")
    top_file.write(".MEASURE TRAN meas_inv_carry_chain_1_trise TRIG V(n_a) VAL='supply_v/2' FALL=1\n")
    top_file.write("+    TARG V(Xcarrychain.n_a_in_bar) VAL='supply_v/2' RISE=1\n\n")

    top_file.write("* inv_carry_chain_2 delays\n")
    top_file.write(".MEASURE TRAN meas_inv_carry_chain_2_tfall TRIG V(Xcarrychain.n_sum_internal) VAL='supply_v/2' RISE=1\n")
    top_file.write("+    TARG V(n_sum_out) VAL='supply_v/2' FALL=1\n")
    top_file.write(".MEASURE TRAN meas_inv_carry_chain_2_trise TRIG V(Xcarrychain.n_sum_internal) VAL='supply_v/2' FALL=1\n")
    top_file.write("+    TARG V(n_sum_out) VAL='supply_v/2' RISE=1\n\n")
    top_file.write("* Total delays\n")

"""
"""
    top_file.write(".MEASURE TRAN meaz1_total_tfall TRIG V(n_a) VAL='supply_v/2' FALL=1\n")
    top_file.write("+    TARG V(Xcarrychain.n_sum_out) VAL='supply_v/2' FALL=1\n")
    top_file.write(".MEASURE TRAN meaz1_total_trise TRIG V(n_a) VAL='supply_v/2' RISE=1\n")
    top_file.write("+    TARG V(Xcarrychain.n_sum_out) VAL='supply_v/2' RISE=1\n\n")

    top_file.write(".MEASURE TRAN meaz2_total_tfall TRIG V(n_b) VAL='supply_v/2' FALL=1\n")
    top_file.write("+    TARG V(Xcarrychain.n_sum_out) VAL='supply_v/2' FALL=2\n")
    top_file.write(".MEASURE TRAN meaz2_total_trise TRIG V(n_b) VAL='supply_v/2' RISE=1\n")
    top_file.write("+    TARG V(Xcarrychain.n_sum_out) VAL='supply_v/2' RISE=2\n\n")

    top_file.write(".MEASURE TRAN meaz3_total_tfall TRIG V(n_cin) VAL='supply_v/2' FALL=1\n")
    top_file.write("+    TARG V(Xcarrychain.n_sum_out) VAL='supply_v/2' FALL=3\n")
    top_file.write(".MEASURE TRAN meaz3_total_trise TRIG V(n_cin) VAL='supply_v/2' RISE=1\n")
    top_file.write("+    TARG V(Xcarrychain.n_sum_out) VAL='supply_v/2' RISE=3\n\n")


    top_file.write(".MEASURE TRAN meaz1_total_tfall TRIG V(n_a) VAL='supply_v/2' RISE=3\n")
    top_file.write("+    TARG V(Xcarrychain.n_cout) VAL='supply_v/2' FALL=3\n")
    top_file.write(".MEASURE TRAN meaz1_total_trise TRIG V(n_a) VAL='supply_v/2' FALL=2\n")
    top_file.write("+    TARG V(Xcarrychain.n_cout) VAL='supply_v/2' RISE=3\n\n")

    top_file.write(".MEASURE TRAN meaz2_total_tfall TRIG V(n_b) VAL='supply_v/2' RISE=2\n")
    top_file.write("+    TARG V(Xcarrychain.n_cout) VAL='supply_v/2' FALL=2\n")
    top_file.write(".MEASURE TRAN meaz2_total_trise TRIG V(n_b) VAL='supply_v/2' FALL=2\n")
    top_file.write("+    TARG V(Xcarrychain.n_cout) VAL='supply_v/2' RISE=2\n\n")

    top_file.write(".MEASURE TRAN meaz3_total_tfall TRIG V(n_cin) VAL='supply_v/2' RISE=2\n")
    top_file.write("+    TARG V(Xcarrychain.n_cout) VAL='supply_v/2' FALL=1\n")
    top_file.write(".MEASURE TRAN meaz3_total_trise TRIG V(n_cin) VAL='supply_v/2' FALL=2\n")
    top_file.write("+    TARG V(Xcarrychain.n_cout) VAL='supply_v/2' RISE=1\n\n")
"""
"""
    top_file.write(".MEASURE TRAN meaz1_total_tfall TRIG V(n_a) VAL='supply_v/2' RISE=3\n")
    top_file.write("+    TARG V(Xcarrychain.n_cout) VAL='supply_v/2' FALL=3\n")
    top_file.write(".MEASURE TRAN meaz1_total_trise TRIG V(n_a) VAL='supply_v/2' FALL=2\n")
    top_file.write("+    TARG V(Xcarrychain.n_cout) VAL='supply_v/2' RISE=3\n\n")

    top_file.write(".MEASURE TRAN meaz2_total_tfall TRIG V(n_b) VAL='supply_v/2' RISE=2\n")
    top_file.write("+    TARG V(Xcarrychain.n_cout) VAL='supply_v/2' FALL=2\n")
    top_file.write(".MEASURE TRAN meaz2_total_trise TRIG V(n_b) VAL='supply_v/2' FALL=2\n")
    top_file.write("+    TARG V(Xcarrychain.n_cout) VAL='supply_v/2' RISE=2\n\n")

    top_file.write(".MEASURE TRAN meaz3_total_tfall TRIG V(n_cin) VAL='supply_v/2' RISE=2\n")
    top_file.write("+    TARG V(Xcarrychain.n_cout) VAL='supply_v/2' FALL=1\n")
    top_file.write(".MEASURE TRAN meaz3_total_trise TRIG V(n_cin) VAL='supply_v/2' FALL=2\n")
    top_file.write("+    TARG V(Xcarrychain.n_cout) VAL='supply_v/2' RISE=1\n\n")


    top_file.write(".MEASURE TRAN meas_logic_low_voltage FIND V(gnd) AT=3n\n\n")

    top_file.write("* Measure the power required to propagate a rise and a fall transition through the subcircuit at 250MHz.\n")
    top_file.write(".MEASURE TRAN meas_current INTEGRAL I(V_test) FROM=0ns TO=26ns\n")
    top_file.write(".MEASURE TRAN meas_avg_power PARAM = '-((meas_current)/26n)*supply_v'\n\n")

    top_file.write("********************************************************************************\n")
    top_file.write("** Circuit\n")
    top_file.write("********************************************************************************\n\n")

    # Generate Cin as part of wave-shaping circuitry:
    #top_file.write("Xcarrychain_shape vdd n_gnd n_cin n_cout n_sum_out vdd_test gnd FA_carry_chain\n")

    # Generate a_in and b_in as part of wave-shaping circuitry:
    #top_file.write("Xlut n_a n_b n_cin n_cout n_sum_out vdd_test gnd FA_carry_chain\n")
    #top_file.write("Xmux n_a n_b n_cin n_cout n_sum_out vdd_test gnd FA_carry_chain\n")

    top_file.write(".print tran V(n_cout) V(n_a) V(n_cin) V(n_b)  \n")   

    # cout typical load
    #top_file.write("Xcarrychain_shape vdd n_gnd n_cin n_cout n_sum_out vdd_test gnd FA_carry_chain\n")    
    # sum typical load
    #top_file.write("Xmux2 vdd n_gnd n_cin n_cout n_sum_out vdd_test gnd FA_carry_chain\n")
    top_file.write(".END")
    top_file.close()

    # Come out of top-level directory
    os.chdir("../")
    
    return (name + "/" + name + ".sp")
    """

def generate_carry_chain_ripple_top(name):

    # Create directories
    if not os.path.exists(name):
        os.makedirs(name)  
    # Change to directory    
    os.chdir(name)  
    
    filename = name + ".sp"
    top_file = open(filename, 'w')
    top_file.write(".TITLE Carry Chain\n\n") 
    
    top_file.write("********************************************************************************\n")
    top_file.write("** Include libraries, parameters and other\n")
    top_file.write("********************************************************************************\n\n")
    top_file.write(".LIB \"../includes.l\" INCLUDES\n\n")
    
    top_file.write("********************************************************************************\n")
    top_file.write("** Setup and input\n")
    top_file.write("********************************************************************************\n\n")
    top_file.write(".TRAN 1p 26n SWEEP DATA=sweep_data\n")
    top_file.write(".OPTIONS BRIEF=1\n\n")
    top_file.write("* Input signals\n")


    top_file.write("VIN n_in gnd PULSE (0 supply_v 0 0 0 2n 4n)\n\n")
    top_file.write("* Power rail for the circuit under test.\n")
    top_file.write("* This allows us to measure power of a circuit under test without measuring the power of wave shaping and load circuitry.\n")
    top_file.write("V_test vdd_test gnd supply_v\n\n")

    top_file.write("********************************************************************************\n")
    top_file.write("** Measurement\n")
    top_file.write("********************************************************************************\n\n")
    top_file.write("* inv_carry_chain_1 delay\n")
    top_file.write(".MEASURE TRAN meas_inv_carry_chain_perf_1_tfall TRIG V(n_1_2) VAL='supply_v/2' FALL=1\n")
    top_file.write("+    TARG V(n_out) VAL='supply_v/2' FALL=1\n")
    top_file.write(".MEASURE TRAN meas_inv_carry_chain_perf_1_trise TRIG V(n_1_2) VAL='supply_v/2' RISE=1\n")
    top_file.write("+    TARG V(n_out) VAL='supply_v/2' RISE=1\n\n")


    top_file.write(".MEASURE TRAN meas_total_tfall TRIG V(n_1_2) VAL='supply_v/2' FALL=1\n")
    top_file.write("+    TARG V(n_out) VAL='supply_v/2' FALL=1\n")
    top_file.write(".MEASURE TRAN meas_total_trise TRIG V(n_1_2) VAL='supply_v/2' RISE=1\n")
    top_file.write("+    TARG V(n_out) VAL='supply_v/2' RISE=1\n\n")

    top_file.write(".MEASURE TRAN meas_logic_low_voltage FIND V(gnd) AT=3n\n\n")

    top_file.write("* Measure the power required to propagate a rise and a fall transition through the subcircuit at 250MHz.\n")
    top_file.write(".MEASURE TRAN meas_current INTEGRAL I(V_test) FROM=0ns TO=26ns\n")
    top_file.write(".MEASURE TRAN meas_avg_power PARAM = '-((meas_current)/26n)*supply_v'\n\n")

    top_file.write("********************************************************************************\n")
    top_file.write("** Circuit\n")
    top_file.write("********************************************************************************\n\n")

    # Generate Cin as part of wave-shaping circuitry:
    top_file.write("Xcarrychain_shape1 vdd gnd n_in n_1_1 n_hang n_p_1 vdd gnd FA_carry_chain\n")
    top_file.write("Xcarrychain_shape2 vdd gnd n_1_1 n_1_2 n_hang_s n_p_2 vdd gnd FA_carry_chain\n")
    
    
    # Generate the uni under test:
    top_file.write("Xcarrychain_main vdd gnd n_1_2 n_hang_2 n_1_3 n_p_3 vdd gnd FA_carry_chain\n")
    top_file.write("Xinv n_1_3 n_out vdd_test gnd carry_chain_perf\n")
    
    # generate typical load
    top_file.write("Xthemux n_out n_out2 vdd gnd vdd gnd carry_chain_mux\n")  

    top_file.write(".END")
    top_file.close()

    # Come out of top-level directory
    os.chdir("../")
    
    return (name + "/" + name + ".sp")
    


def generate_carry_chain_skip_top(name, use_tgate):

    # Create directories
    if not os.path.exists(name):
        os.makedirs(name)  
    # Change to directory    
    os.chdir(name)  
    
    filename = name + ".sp"
    top_file = open(filename, 'w')
    top_file.write(".TITLE Carry Chain\n\n") 
    
    top_file.write("********************************************************************************\n")
    top_file.write("** Include libraries, parameters and other\n")
    top_file.write("********************************************************************************\n\n")
    top_file.write(".LIB \"../includes.l\" INCLUDES\n\n")
    
    top_file.write("********************************************************************************\n")
    top_file.write("** Setup and input\n")
    top_file.write("********************************************************************************\n\n")
    top_file.write(".TRAN 1p 26n SWEEP DATA=sweep_data\n")
    top_file.write(".OPTIONS BRIEF=1\n\n")
    top_file.write("* Input signals\n")


    top_file.write("VIN n_in gnd PULSE (0 supply_v 0 0 0 2n 4n)\n\n")
    top_file.write("* Power rail for the circuit under test.\n")
    top_file.write("* This allows us to measure power of a circuit under test without measuring the power of wave shaping and load circuitry.\n")
    top_file.write("V_test vdd_test gnd supply_v\n\n")

    top_file.write("********************************************************************************\n")
    top_file.write("** Measurement\n")
    top_file.write("********************************************************************************\n\n")
    top_file.write("* inv_carry_chain_1 delay\n")
    top_file.write(".MEASURE TRAN meas_inv_carry_chain_perf_1_tfall TRIG V(n_1_2) VAL='supply_v/2' FALL=1\n")
    top_file.write("+    TARG V(n_out) VAL='supply_v/2' FALL=1\n")
    top_file.write(".MEASURE TRAN meas_inv_carry_chain_perf_1_trise TRIG V(n_1_2) VAL='supply_v/2' RISE=1\n")
    top_file.write("+    TARG V(n_out) VAL='supply_v/2' RISE=1\n\n")


    top_file.write(".MEASURE TRAN meas_total_tfall TRIG V(n_1_2) VAL='supply_v/2' FALL=1\n")
    top_file.write("+    TARG V(n_out) VAL='supply_v/2' FALL=1\n")
    top_file.write(".MEASURE TRAN meas_total_trise TRIG V(n_1_2) VAL='supply_v/2' RISE=1\n")
    top_file.write("+    TARG V(n_out) VAL='supply_v/2' RISE=1\n\n")

    top_file.write(".MEASURE TRAN meas_logic_low_voltage FIND V(gnd) AT=3n\n\n")

    top_file.write("* Measure the power required to propagate a rise and a fall transition through the subcircuit at 250MHz.\n")
    top_file.write(".MEASURE TRAN meas_current INTEGRAL I(V_test) FROM=0ns TO=26ns\n")
    top_file.write(".MEASURE TRAN meas_avg_power PARAM = '-((meas_current)/26n)*supply_v'\n\n")

    top_file.write("********************************************************************************\n")
    top_file.write("** Circuit\n")
    top_file.write("********************************************************************************\n\n")

    # Generate Cin as part of wave-shaping circuitry:
    top_file.write("Xcarrychain_shape1 vdd gnd n_in n_1_1 n_hang n_p_1 vdd gnd FA_carry_chain\n")
    top_file.write("Xcarrychain_shape2 vdd gnd n_1_1 n_1_2 n_hang_s n_p_2 vdd gnd FA_carry_chain\n")
    
    
    # Generate the uni under test:
    top_file.write("Xcarrychain_main vdd gnd n_1_2 n_hang_2 n_1_3 n_p_3 vdd gnd FA_carry_chain\n")
    top_file.write("Xinv n_1_3 n_out vdd_test gnd carry_chain_perf\n")

    # generate typical load
    top_file.write("Xthemux n_out n_out2 vdd gnd vdd gnd carry_chain_mux\n")  

    top_file.write(".END")
    top_file.close()

    # Come out of top-level directory
    os.chdir("../")
    
    return (name + "/" + name + ".sp")



def generate_carrychain_top(name):
    """ """
    
    # Create directories
    if not os.path.exists(name):
        os.makedirs(name)  
    # Change to directory    
    os.chdir(name)  
    
    filename = name + ".sp"
    top_file = open(filename, 'w')
    top_file.write(".TITLE Carry Chain\n\n") 
    
    top_file.write("********************************************************************************\n")
    top_file.write("** Include libraries, parameters and other\n")
    top_file.write("********************************************************************************\n\n")
    top_file.write(".LIB \"../includes.l\" INCLUDES\n\n")
    
    top_file.write("********************************************************************************\n")
    top_file.write("** Setup and input\n")
    top_file.write("********************************************************************************\n\n")
    top_file.write(".TRAN 1p 26n SWEEP DATA=sweep_data\n")
    top_file.write(".OPTIONS BRIEF=1\n\n")
    top_file.write("* Input signals\n")

    #top_file.write("VIN n_a gnd PWL (0 0 1.999n 0 2n 'supply_v' 3.999n 'supply_v' 4n 0 13.999n 0 14n 'supply_v' 23.999n 'supply_v' 24n 0)\n\n")
    #top_file.write("VIN2 n_b gnd PWL (0 0 5.999n 0 6n supply_v 7.999n supply_v 8n 0 17.999n 0 18n supply_v 19.999n supply_v 20n 0 21.999n 0 22n supply_v)\n\n")
    #top_file.write("VIN3 n_cin gnd PWL (0 0 9.999n 0 10n supply_v 11.999n supply_v 12n 0 13.999n 0 14n supply_v 15.999n supply_v 16n 0 )\n\n")
    #top_file.write("VIN n_a gnd PWL (0 0 1.999n 0 2n 'supply_v' 3.999n 'supply_v' 4n 0 13.999n 0 14n 'supply_v' 23.999n 'supply_v' 24n 0)\n\n")
    #top_file.write("VIN2 n_b gnd PWL (0 0 5.999n 0 6n supply_v 7.999n supply_v 8n 0 17.999n 0 18n supply_v 19.999n supply_v 20n 0 21.999n 0 22n supply_v)\n\n")
    #top_file.write("VIN3 n_cin gnd PWL (0 0 9.999n 0 10n supply_v 11.999n supply_v 12n 0 13.999n 0 14n supply_v 15.999n supply_v 16n 0 )\n\n")
    
    top_file.write("VIN n_in gnd PULSE (0 supply_v 0 0 0 2n 4n)\n\n")
    top_file.write("* Power rail for the circuit under test.\n")
    top_file.write("* This allows us to measure power of a circuit under test without measuring the power of wave shaping and load circuitry.\n")
    top_file.write("V_test vdd_test gnd supply_v\n\n")

    top_file.write("********************************************************************************\n")
    top_file.write("** Measurement\n")
    top_file.write("********************************************************************************\n\n")
    top_file.write("* inv_carry_chain_1 delay\n")
    top_file.write(".MEASURE TRAN meas_inv_carry_chain_1_tfall TRIG V(n_1_1) VAL='supply_v/2' RISE=1\n")
    top_file.write("+    TARG V(Xcarrychain.n_cin_in_bar) VAL='supply_v/2' FALL=1\n")
    top_file.write(".MEASURE TRAN meas_inv_carry_chain_1_trise TRIG V(n_1_1) VAL='supply_v/2' FALL=1\n")
    top_file.write("+    TARG V(Xcarrychain.n_cin_in_bar) VAL='supply_v/2' RISE=1\n\n")

    top_file.write("* inv_carry_chain_2 delays\n")
    top_file.write(".MEASURE TRAN meas_inv_carry_chain_2_tfall TRIG V(n_1_1) VAL='supply_v/2' RISE=1\n")
    top_file.write("+    TARG V(n_sum_out) VAL='supply_v/2' FALL=1\n")
    top_file.write(".MEASURE TRAN meas_inv_carry_chain_2_trise TRIG V(n_1_1) VAL='supply_v/2' FALL=1\n")
    top_file.write("+    TARG V(n_sum_out) VAL='supply_v/2' RISE=1\n\n")
    top_file.write("* Total delays\n")


    top_file.write(".MEASURE TRAN meas_total_tfall TRIG V(n_1_1) VAL='supply_v/2' RISE=1\n")
    top_file.write("+    TARG V(n_1_2) VAL='supply_v/2' FALL=1\n")
    top_file.write(".MEASURE TRAN meas_total_trise TRIG V(n_1_1) VAL='supply_v/2' FALL=1\n")
    top_file.write("+    TARG V(n_1_2) VAL='supply_v/2' RISE=1\n\n")

    top_file.write(".MEASURE TRAN meas_logic_low_voltage FIND V(gnd) AT=3n\n\n")

    top_file.write("* Measure the power required to propagate a rise and a fall transition through the subcircuit at 250MHz.\n")
    top_file.write(".MEASURE TRAN meas_current INTEGRAL I(V_test) FROM=0ns TO=26ns\n")
    top_file.write(".MEASURE TRAN meas_avg_power PARAM = '-((meas_current)/26n)*supply_v'\n\n")

    top_file.write("********************************************************************************\n")
    top_file.write("** Circuit\n")
    top_file.write("********************************************************************************\n\n")

    # Generate Cin as part of wave-shaping circuitry:
    top_file.write("Xcarrychain_shape vdd gnd n_in n_0_1 n_hang n_p_1 vdd gnd FA_carry_chain\n")
    top_file.write("Xcarrychain_shape1 vdd gnd n_0_1 n_0_2 n_hangz n_p_0 vdd gnd FA_carry_chain\n")
    top_file.write("Xcarrychain_shape2 vdd gnd n_0_2 n_1_1 n_hangzz n_p_z vdd gnd FA_carry_chain\n")
    
    # Generate the adder under test:
    top_file.write("Xcarrychain vdd gnd n_1_1 n_1_2 n_sum_out n_p_2 vdd_test gnd FA_carry_chain\n")
    
    # cout typical load
    top_file.write("Xcarrychain_load vdd gnd n_1_2 n_1_3 n_sum_out2 n_p_3 vdd gnd FA_carry_chain\n")      

    top_file.write(".END")
    top_file.close()

    # Come out of top-level directory
    os.chdir("../")
    
    return (name + "/" + name + ".sp")
    

def generate_carry_inter_top(name):

    # Create directories
    if not os.path.exists(name):
        os.makedirs(name)  
    # Change to directory    
    os.chdir(name)  
    
    filename = name + ".sp"
    top_file = open(filename, 'w')
    top_file.write(".TITLE Carry Chain\n\n") 
    
    top_file.write("********************************************************************************\n")
    top_file.write("** Include libraries, parameters and other\n")
    top_file.write("********************************************************************************\n\n")
    top_file.write(".LIB \"../includes.l\" INCLUDES\n\n")
    
    top_file.write("********************************************************************************\n")
    top_file.write("** Setup and input\n")
    top_file.write("********************************************************************************\n\n")
    top_file.write(".TRAN 1p 26n SWEEP DATA=sweep_data\n")
    top_file.write(".OPTIONS BRIEF=1\n\n")
    top_file.write("* Input signals\n")

    top_file.write("VIN n_in gnd PULSE (0 supply_v 0 0 0 2n 4n)\n\n")
    top_file.write("* Power rail for the circuit under test.\n")
    top_file.write("* This allows us to measure power of a circuit under test without measuring the power of wave shaping and load circuitry.\n")
    top_file.write("V_test vdd_test gnd supply_v\n\n")

    top_file.write("********************************************************************************\n")
    top_file.write("** Measurement\n")
    top_file.write("********************************************************************************\n\n")
    top_file.write("* inv_nand"+name+"_1 delay\n")
    top_file.write(".MEASURE TRAN meas_inv_"+name+"_1_tfall TRIG V(n_1_2) VAL='supply_v/2' RISE=1\n")
    top_file.write("+    TARG V(Xdrivers.n_1_1) VAL='supply_v/2' FALL=1\n")
    top_file.write(".MEASURE TRAN meas_inv_"+name+"_1_trise TRIG V(n_1_2) VAL='supply_v/2' FALL=1\n")
    top_file.write("+    TARG V(Xdrivers.n_1_1) VAL='supply_v/2' RISE=1\n\n")

    top_file.write("* inv_"+name+"_2 delays\n")
    top_file.write(".MEASURE TRAN meas_inv_"+name+"_2_tfall TRIG V(n_1_2) VAL='supply_v/2' FALL=1\n")
    top_file.write("+    TARG V(n_1_3) VAL='supply_v/2' FALL=1\n")
    top_file.write(".MEASURE TRAN meas_inv_"+name+"_2_trise TRIG V(n_1_2) VAL='supply_v/2' RISE=1\n")
    top_file.write("+    TARG V(n_1_3) VAL='supply_v/2' RISE=1\n\n")
    top_file.write("* Total delays\n")

    top_file.write(".MEASURE TRAN meas_total_tfall TRIG V(n_1_2) VAL='supply_v/2' FALL=1\n")
    top_file.write("+    TARG V(n_1_3) VAL='supply_v/2' FALL=1\n")
    top_file.write(".MEASURE TRAN meas_total_trise TRIG V(n_1_2) VAL='supply_v/2' RISE=1\n")
    top_file.write("+    TARG V(n_1_3) VAL='supply_v/2' RISE=1\n\n")

    top_file.write(".MEASURE TRAN meas_logic_low_voltage FIND V(gnd) AT=3n\n\n")

    top_file.write("* Measure the power required to propagate a rise and a fall transition through the subcircuit at 250MHz.\n")
    top_file.write(".MEASURE TRAN meas_current INTEGRAL I(V_test) FROM=0ns TO=26ns\n")
    top_file.write(".MEASURE TRAN meas_avg_power PARAM = '-((meas_current)/26n)*supply_v'\n\n")

    top_file.write("********************************************************************************\n")
    top_file.write("** Circuit\n")
    top_file.write("********************************************************************************\n\n")

    # Generate Cin as part of wave-shaping circuitry:
    top_file.write("Xcarrychain_0 vdd gnd n_in n_1_1 n_sum_out n_1p vdd gnd FA_carry_chain\n")   
    top_file.write("Xcarrychain vdd gnd n_1_1 n_1_2 n_sum_out2 n_2p vdd gnd FA_carry_chain\n")

    # Generate the unit under test:
    top_file.write("Xdrivers n_1_2 n_1_3 vdd_test gnd carry_chain_inter\n")
    # typical load (next carry chain)
    top_file.write("Xcarrychain_l n_1_3 vdd gnd n_hangl n_sum_out3 n_3p vdd gnd FA_carry_chain\n")   
    

    top_file.write(".END")
    top_file.close()

    # Come out of top-level directory
    os.chdir("../")
    
    return (name + "/" + name + ".sp")



def generate_carrychainand_top(name, use_tgate, nand1_size, nand2_size):
    # Create directories
    if not os.path.exists(name):
        os.makedirs(name)  
    # Change to directory    
    os.chdir(name)  
    
    filename = name + ".sp"
    top_file = open(filename, 'w')
    top_file.write(".TITLE Carry Chain\n\n") 
    
    top_file.write("********************************************************************************\n")
    top_file.write("** Include libraries, parameters and other\n")
    top_file.write("********************************************************************************\n\n")
    top_file.write(".LIB \"../includes.l\" INCLUDES\n\n")
    
    top_file.write("********************************************************************************\n")
    top_file.write("** Setup and input\n")
    top_file.write("********************************************************************************\n\n")
    top_file.write(".TRAN 1p 26n SWEEP DATA=sweep_data\n")
    top_file.write(".OPTIONS BRIEF=1\n\n")
    top_file.write("* Input signals\n")

    top_file.write("VIN n_in gnd PULSE (0 supply_v 0 0 0 2n 4n)\n\n")
    top_file.write("* Power rail for the circuit under test.\n")
    top_file.write("* This allows us to measure power of a circuit under test without measuring the power of wave shaping and load circuitry.\n")
    top_file.write("V_test vdd_test gnd supply_v\n\n")

    top_file.write("********************************************************************************\n")
    top_file.write("** Measurement\n")
    top_file.write("********************************************************************************\n\n")
    top_file.write("* inv_nand"+name+"_1 delay\n")
    top_file.write(".MEASURE TRAN meas_inv_nand"+str(nand1_size)+"_"+name+"_1_tfall TRIG V(n_1_2) VAL='supply_v/2' RISE=1\n")
    top_file.write("+    TARG V(Xandtree.n_1_2) VAL='supply_v/2' FALL=1\n")
    top_file.write(".MEASURE TRAN meas_inv_nand"+str(nand1_size)+"_"+name+"_1_trise TRIG V(n_1_2) VAL='supply_v/2' FALL=1\n")
    top_file.write("+    TARG V(Xandtree.n_1_2) VAL='supply_v/2' RISE=1\n\n")

    top_file.write("* inv_"+name+"_2 delays\n")
    top_file.write(".MEASURE TRAN meas_inv_"+name+"_2_tfall TRIG V(n_1_2) VAL='supply_v/2' FALL=1\n")
    top_file.write("+    TARG V(Xandtree.n_1_3) VAL='supply_v/2' FALL=1\n")
    top_file.write(".MEASURE TRAN meas_inv_"+name+"_2_trise TRIG V(n_1_2) VAL='supply_v/2' RISE=1\n")
    top_file.write("+    TARG V(Xandtree.n_1_3) VAL='supply_v/2' RISE=1\n\n")
    top_file.write("* Total delays\n")


    top_file.write("* inv_nand"+name+"_3 delay\n")
    top_file.write(".MEASURE TRAN meas_inv_nand"+str(nand2_size)+"_"+name+"_3_tfall TRIG V(n_1_2) VAL='supply_v/2' RISE=1\n")
    top_file.write("+    TARG V(Xandtree.n_1_5) VAL='supply_v/2' FALL=1\n")
    top_file.write(".MEASURE TRAN meas_inv_nand"+str(nand2_size)+"_"+name+"_3_trise TRIG V(n_1_2) VAL='supply_v/2' FALL=1\n")
    top_file.write("+    TARG V(Xandtree.n_1_5) VAL='supply_v/2' RISE=1\n\n")

    top_file.write("* inv_"+name+"_4 delays\n")
    top_file.write(".MEASURE TRAN meas_inv_"+name+"_4_tfall TRIG V(n_1_2) VAL='supply_v/2' FALL=1\n")
    top_file.write("+    TARG V(n_1_3) VAL='supply_v/2' FALL=1\n")
    top_file.write(".MEASURE TRAN meas_inv_"+name+"_4_trise TRIG V(n_1_2) VAL='supply_v/2' RISE=1\n")
    top_file.write("+    TARG V(n_1_3) VAL='supply_v/2' RISE=1\n\n")
    top_file.write("* Total delays\n")

    top_file.write(".MEASURE TRAN meas_total_tfall TRIG V(n_1_2) VAL='supply_v/2' FALL=1\n")
    top_file.write("+    TARG V(n_1_3) VAL='supply_v/2' FALL=1\n")
    top_file.write(".MEASURE TRAN meas_total_trise TRIG V(n_1_2) VAL='supply_v/2' RISE=1\n")
    top_file.write("+    TARG V(n_1_3) VAL='supply_v/2' RISE=1\n\n")

    top_file.write(".MEASURE TRAN meas_logic_low_voltage FIND V(gnd) AT=3n\n\n")

    top_file.write("* Measure the power required to propagate a rise and a fall transition through the subcircuit at 250MHz.\n")
    top_file.write(".MEASURE TRAN meas_current INTEGRAL I(V_test) FROM=0ns TO=26ns\n")
    top_file.write(".MEASURE TRAN meas_avg_power PARAM = '-((meas_current)/26n)*supply_v'\n\n")

    top_file.write("********************************************************************************\n")
    top_file.write("** Circuit\n")
    top_file.write("********************************************************************************\n\n")

    # Generate Cin as part of wave-shaping circuitry:
    if not use_tgate:
        top_file.write("Xlut n_in n_1_1 vdd vdd vdd vdd vdd vdd vdd gnd lut\n")
    else :
        top_file.write("Xlut n_in n_1_1 vdd gnd vdd gnd vdd gnd vdd gnd vdd gnd vdd gnd vdd gnd lut\n\n")
    
    top_file.write("Xcarrychain n_1_1 vdd gnd n_hang n_sum_out n_1_2 vdd gnd FA_carry_chain\n")
    # Generate the unit under test:
    top_file.write("Xandtree n_1_2 n_1_3 vdd_test gnd xcarry_chain_and\n")
    # typical load
    top_file.write("Xcarrychainskip_mux n_1_3 n_1_4 vdd gnd vdd gnd xcarry_chain_mux\n")   
    top_file.write("Xcarrychain_mux n_1_4 n_1_5 vdd gnd vdd gnd carry_chain_mux\n")     

    top_file.write(".END")
    top_file.close()

    # Come out of top-level directory
    os.chdir("../")
    
    return (name + "/" + name + ".sp")
    

def generate_skip_mux_top(name, use_tgate):
    # Create directories
    if not os.path.exists(name):
        os.makedirs(name)  
    # Change to directory    
    os.chdir(name)  
    
    filename = name + ".sp"
    top_file = open(filename, 'w')
    top_file.write(".TITLE Carry Chain\n\n")


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
    top_file.write("* Power rail for the circuit under test.\n")
    top_file.write("* This allows us to measure power of a circuit under test without measuring the power of wave shaping and load circuitry.\n")
    top_file.write("V_FLUT vdd_test gnd supply_v\n\n")

    top_file.write("********************************************************************************\n")
    top_file.write("** Measurement\n")
    top_file.write("********************************************************************************\n\n")
    top_file.write("* inv_"+ name +"_1 delay\n")
    top_file.write(".MEASURE TRAN meas_inv_"+ name +"_1_tfall TRIG V(n_1_3) VAL='supply_v/2' RISE=1\n")
    top_file.write("+    TARG V(Xcarrychainskip_mux.n_2_1) VAL='supply_v/2' FALL=1\n")
    top_file.write(".MEASURE TRAN meas_inv_"+ name +"_1_trise TRIG V(n_1_3) VAL='supply_v/2' FALL=1\n")
    top_file.write("+    TARG V(Xcarrychainskip_mux.n_2_1) VAL='supply_v/2' RISE=1\n\n")
    top_file.write("* inv_"+ name +"_2 delays\n")
    top_file.write(".MEASURE TRAN meas_inv_"+ name +"_2_tfall TRIG V(n_1_3) VAL='supply_v/2' FALL=1\n")
    top_file.write("+    TARG V(n_1_4) VAL='supply_v/2' FALL=1\n")
    top_file.write(".MEASURE TRAN meas_inv_"+ name +"_2_trise TRIG V(n_1_3) VAL='supply_v/2' RISE=1\n")
    top_file.write("+    TARG V(n_1_4) VAL='supply_v/2' RISE=1\n\n")
    top_file.write("* Total delays\n")
    top_file.write(".MEASURE TRAN meas_total_tfall TRIG V(n_1_3) VAL='supply_v/2' FALL=1\n")
    #top_file.write("+    TARG V(n_1_3) VAL='supply_v/2' FALL=1\n")
    top_file.write("+    TARG V(n_1_4) VAL='supply_v/2' FALL=1\n")
    top_file.write(".MEASURE TRAN meas_total_trise TRIG V(n_1_3) VAL='supply_v/2' RISE=1\n")
    #top_file.write("+    TARG V(n_1_3) VAL='supply_v/2' RISE=1\n\n")
    top_file.write("+    TARG V(n_1_4) VAL='supply_v/2' RISE=1\n\n")
    top_file.write(".MEASURE TRAN meas_logic_low_voltage FIND V(n_general_out) AT=3n\n\n")

    top_file.write("* Measure the power required to propagate a rise and a fall transition through the subcircuit at 250MHz.\n")
    top_file.write(".MEASURE TRAN meas_current INTEGRAL I(V_FLUT) FROM=0ns TO=4ns\n")
    top_file.write(".MEASURE TRAN meas_avg_power PARAM = '-((meas_current)/4n)*supply_v'\n\n")


    top_file.write("********************************************************************************\n")
    top_file.write("** Circuit\n")
    top_file.write("********************************************************************************\n\n")

    # Generate Cin as part of wave-shaping circuitry:
    if not use_tgate:
        top_file.write("Xlut n_in n_1_1 vdd vdd vdd vdd vdd vdd vdd gnd lut\n")
    else :
        top_file.write("Xlut n_in n_1_1 vdd gnd vdd gnd vdd gnd vdd gnd vdd gnd vdd gnd vdd gnd lut\n\n")
    
    top_file.write("Xcarrychain n_1_1 vdd gnd n_hang n_sum_out n_1_2 vdd gnd FA_carry_chain\n")
    
    top_file.write("Xandtree n_1_2 n_1_3 vdd gnd xcarry_chain_and\n")
    # Generate the unit under test:
    top_file.write("Xcarrychainskip_mux n_1_3 n_1_4 vdd gnd vdd_test gnd xcarry_chain_mux\n")   
    # typical load
    top_file.write("Xcarrychain_mux n_1_4 n_1_5 vdd gnd vdd gnd carry_chain_mux\n")     

    top_file.write(".END")
    top_file.close()

    # Come out of top-level directory
    os.chdir("../")
    return (name + "/" + name + ".sp")


def generate_dedicated_driver_top (name, top_name, num_bufs):

    # Create directories
    if not os.path.exists(name):
        os.makedirs(name)  
    # Change to directory    
    os.chdir(name)  
    
    filename = name + ".sp"
    top_file = open(filename, 'w')
    top_file.write(".TITLE Dedicated Routing Driver\n\n")


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
    top_file.write("* Power rail for the circuit under test.\n")
    top_file.write("* This allows us to measure power of a circuit under test without measuring the power of wave shaping and load circuitry.\n")
    top_file.write("V_TEST vdd_test gnd supply_v\n\n")

    top_file.write("********************************************************************************\n")
    top_file.write("** Measurement\n")
    top_file.write("********************************************************************************\n\n")
    for i in range(1, num_bufs * 2 + 1, 2):
        top_file.write("* inv_"+ name +"_"+str(i)+" delay\n")
        top_file.write(".MEASURE TRAN meas_inv_"+ name +"_"+str(i)+"_tfall TRIG V(n_1_1) VAL='supply_v/2' RISE=1\n")
        top_file.write("+    TARG V(Xdriver.n_1_"+str(2 * i)+") VAL='supply_v/2' FALL=1\n")
        top_file.write(".MEASURE TRAN meas_inv_"+ name +"_"+str(i)+"_trise TRIG V(n_1_1) VAL='supply_v/2' FALL=1\n")
        top_file.write("+    TARG V(Xdriver.n_1_"+str(2 * i)+") VAL='supply_v/2' RISE=1\n\n")
        if i + 1 == num_bufs * 2:
            top_file.write("* inv_"+ name +"_"+str(i+1)+" delays\n")
            top_file.write(".MEASURE TRAN meas_inv_"+ name +"_"+str(i+1)+"_tfall TRIG V(n_1_1) VAL='supply_v/2' FALL=1\n")
            top_file.write("+    TARG V(Xdriver.n_out) VAL='supply_v/2' FALL=1\n")
            top_file.write(".MEASURE TRAN meas_inv_"+ name +"_"+str(i+1)+"_trise TRIG V(n_1_1) VAL='supply_v/2' RISE=1\n")
            top_file.write("+    TARG V(Xdriver.n_out) VAL='supply_v/2' RISE=1\n\n")
        else:
            top_file.write("* inv_"+ name +"_"+str(i+1)+" delays\n")
            top_file.write(".MEASURE TRAN meas_inv_"+ name +"_"+str(i+1)+"_tfall TRIG V(n_1_1) VAL='supply_v/2' FALL=1\n")
            top_file.write("+    TARG V(Xdriver.n_1_"+str(2 * i + 2)+") VAL='supply_v/2' FALL=1\n")
            top_file.write(".MEASURE TRAN meas_inv_"+ name +"_"+str(i+1)+"_trise TRIG V(n_1_1) VAL='supply_v/2' RISE=1\n")
            top_file.write("+    TARG V(Xdriver.n_1_"+str(2 * i + 2)+") VAL='supply_v/2' RISE=1\n\n")

    top_file.write("* Total delays\n")
    top_file.write(".MEASURE TRAN meas_total_tfall TRIG V(n_1_1) VAL='supply_v/2' FALL=1\n")
    top_file.write("+    TARG V(n_1_3) VAL='supply_v/2' FALL=1\n")
    top_file.write(".MEASURE TRAN meas_total_trise TRIG V(n_1_1) VAL='supply_v/2' RISE=1\n")
    top_file.write("+    TARG V(n_1_3) VAL='supply_v/2' RISE=1\n\n")

    top_file.write(".MEASURE TRAN meas_logic_low_voltage FIND V(gnd) AT=3n\n\n")

    top_file.write("* Measure the power required to propagate a rise and a fall transition through the subcircuit at 250MHz.\n")
    top_file.write(".MEASURE TRAN meas_current INTEGRAL I(V_TEST) FROM=0ns TO=4ns\n")
    top_file.write(".MEASURE TRAN meas_avg_power PARAM = '-((meas_current)/4n)*supply_v'\n\n")


    top_file.write("********************************************************************************\n")
    top_file.write("** Circuit\n")
    top_file.write("********************************************************************************\n\n")

    top_file.write("Xinv_ff_output_driver_0 n_in n_1_0 vdd gnd inv Wn=inv_ff_output_driver_nmos Wp=inv_ff_output_driver_pmos\n")
    top_file.write("Xinv_ff_output_driver n_1_0 n_1_1 vdd gnd inv Wn=inv_ff_output_driver_nmos Wp=inv_ff_output_driver_pmos\n")

    top_file.write("Xdriver n_1_1 n_1_2 vdd_test gnd "+name+"\n")   
    # typical load
    top_file.write("Xwirer_edi n_1_2 n_1_3 wire Rw=wire_"+top_name+"_2_res Cw=wire_"+top_name+"_2_cap \n")
    top_file.write("Xff n_1_3 n_hang2 vdd gnd vdd nnd gnd vdd gnd vdd vdd gnd ff\n")
   
    top_file.write(".END")
    top_file.close()

    # Come out of top-level directory
    os.chdir("../")
    return (name + "/" + name + ".sp")
