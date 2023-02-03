def general_routing_load_generate(spice_filename, wire_length, tile_sb_on, tile_sb_partial, tile_sb_off, tile_cb_on, tile_cb_partial, tile_cb_off):
    """ Generates a routing wire load SPICE deck  """
    
    # Open SPICE file for appending
    spice_file = open(spice_filename, 'a')
    
    ###############################################################
    ## ROUTING WIRE LOAD
    ###############################################################

    # First we write the individual tile loads
    # Tiles are generated such that if you drive a wire from the left you get
    #   driver -> tile 4 -> tile 3 -> tile 2 -> tile 1 (driver) -> tile 4 -> etc.
    for i in range(wire_length):
        spice_file.write("******************************************************************************************\n")
        spice_file.write("* Routing wire load tile " + str(i+1) + "\n")
        spice_file.write("******************************************************************************************\n")
        # If this is Tile 1, we need to add a nodes to which we can connect the ON sb_mux and cb_mux so that we can measure power.
        if i == 0:
            spice_file.write(".SUBCKT routing_wire_load_tile_" + str(i+1) + " n_in n_out n_cb_out n_gate n_gate_n n_vdd n_gnd n_vdd_sb_mux_on n_vdd_cb_mux_on\n")
        else:
            spice_file.write(".SUBCKT routing_wire_load_tile_" + str(i+1) + " n_in n_out n_cb_out n_gate n_gate_n n_vdd n_gnd\n")
        spice_file.write("Xwire_gen_routing_1 n_in n_1_1 wire Rw='wire_gen_routing_res/" + str(2*wire_length) + "' Cw='wire_gen_routing_cap/" + str(2*wire_length) + "'\n\n")
        
        # SWITCH BLOCK LOAD
        # Write the ON switch block loads 
        for sb_on in range(tile_sb_on[i]):
            # Tile 1 is terminated by a on SB, if this is tile 1 and sb_on 1, we ignore it because we put that one at the end.
            if i == 0:
                if sb_on != 0:
                    spice_file.write("Xwire_sb_load_on_" + str(sb_on+1) + " n_1_1 n_1_sb_on_" + str(sb_on+1) + " wire Rw=wire_sb_load_on_res Cw=wire_sb_load_on_cap\n")
                    spice_file.write("Xsb_load_on_" + str(sb_on+1) + " n_1_sb_on_" + str(sb_on+1) + " n_sb_mux_on_" + str(sb_on+1) + "_hang n_gate n_gate_n n_vdd n_gnd sb_mux_on\n\n")
            else:
                spice_file.write("Xwire_sb_load_on_" + str(sb_on+1) + " n_1_1 n_1_sb_on_" + str(sb_on+1) + " wire Rw=wire_sb_load_on_res Cw=wire_sb_load_on_cap\n")
                spice_file.write("Xsb_load_on_" + str(sb_on+1) + " n_1_sb_on_" + str(sb_on+1) + " n_sb_mux_on_" + str(sb_on+1) + "_hang n_gate n_gate_n n_vdd n_gnd sb_mux_on\n\n")
        # Write partially on switch block loads
        for sb_partial in range(tile_sb_partial[i]):
            spice_file.write("Xwire_sb_load_partial_" + str(sb_partial+1) + " n_1_1 n_1_sb_partial_" + str(sb_partial+1) + " wire Rw=wire_sb_load_partial_res Cw=wire_sb_load_partial_cap\n")
            spice_file.write("Xsb_load_partial_" + str(sb_partial+1) + " n_1_sb_partial_" + str(sb_partial+1) + " n_gate n_gate_n n_vdd n_gnd sb_mux_partial\n\n")
        # Write off switch block loads
        for sb_off in range(tile_sb_off[i]):
            spice_file.write("Xwire_sb_load_off_" + str(sb_off+1) + " n_1_1 n_1_sb_off_" + str(sb_off+1) + " wire Rw=wire_sb_load_off_res Cw=wire_sb_load_off_cap\n")
            spice_file.write("Xsb_load_off_" + str(sb_off+1) + " n_1_sb_off_" + str(sb_off+1) + " n_gate n_gate_n n_vdd n_gnd sb_mux_off\n\n")
        
        # CONNECTION BLOCK LOAD
        # Write the ON connection block load
        for cb_on in range(tile_cb_on[i]):
            # If this is tile 1, we need to connect the connection block to the n_cb_out net
            if i == 0:
                # We only connect one of them, so the first one in this case.
                # This cb_mux is connected to a different power rail so that we can measure power.
                if cb_on == 0:
                    spice_file.write("Xwire_cb_load_on_" + str(cb_on+1) + " n_1_1 n_1_cb_on_" + str(cb_on+1) + " wire Rw=wire_cb_load_on_res Cw=wire_cb_load_on_cap\n")
                    spice_file.write("Xcb_load_on_" + str(cb_on+1) + " n_1_cb_on_" + str(cb_on+1) + " n_cb_out n_gate n_gate_n n_vdd_cb_mux_on n_gnd cb_mux_on\n\n")
            else:
                spice_file.write("Xwire_cb_load_on_" + str(cb_on+1) + " n_1_1 n_1_cb_on_" + str(cb_on+1) + " wire Rw=wire_cb_load_on_res Cw=wire_cb_load_on_cap\n")
                spice_file.write("Xcb_load_on_" + str(cb_on+1) + " n_1_cb_on_" + str(cb_on+1) + " n_cb_mux_on_" + str(cb_on+1) + "_hang n_gate n_gate_n n_vdd n_gnd cb_mux_on\n\n")
        # Write partially on connection block loads
        for cb_partial in range(tile_cb_partial[i]):
            spice_file.write("Xwire_cb_load_partial_" + str(cb_partial+1) + " n_1_1 n_1_cb_partial_" + str(cb_partial+1) + " wire Rw=wire_cb_load_partial_res Cw=wire_cb_load_partial_cap\n")
            spice_file.write("Xcb_load_partial_" + str(cb_partial+1) + " n_1_cb_partial_" + str(cb_partial+1) + " n_gate n_gate_n n_vdd n_gnd cb_mux_partial\n\n")
        # Write off connection block loads
        for cb_off in range(tile_cb_off[i]):
            spice_file.write("Xwire_cb_load_off_" + str(cb_off+1) + " n_1_1 n_1_cb_off_" + str(cb_off+1) + " wire Rw=wire_cb_load_off_res Cw=wire_cb_load_off_cap\n")
            spice_file.write("Xcb_load_off_" + str(cb_off+1) + " n_1_cb_off_" + str(cb_off+1) + " n_gate n_gate_n n_vdd n_gnd cb_mux_off\n\n")
        
        # Tile 1 is terminated by a on switch block, other tiles just connect the wire to the output
        # Tile 1's sb_mux is connected to a different power rail so that we can measure dynamic power.
        if i == 0:
            spice_file.write("Xwire_gen_routing_2 n_1_1 n_1_2 wire Rw='wire_gen_routing_res/" + str(2*wire_length) + "' Cw='wire_gen_routing_cap/" + str(2*wire_length) + "'\n")
            spice_file.write("Xsb_mux_on_out n_1_2 n_out n_gate n_gate_n n_vdd_sb_mux_on n_gnd sb_mux_on\n")
        else:
            spice_file.write("Xwire_gen_routing_2 n_1_1 n_out wire Rw='wire_gen_routing_res/" + str(2*wire_length) + "' Cw='wire_gen_routing_cap/" + str(2*wire_length) + "'\n")
    
        spice_file.write(".ENDS\n\n\n")
    
    
    # Now write a subcircuit for the complete routing wire
    spice_file.write("******************************************************************************************\n")
    spice_file.write("* Routing wire load tile " + str(i+1) + "\n")
    spice_file.write("******************************************************************************************\n")
    spice_file.write(".SUBCKT routing_wire_load n_in n_out n_cb_out n_gate n_gate_n n_vdd n_gnd n_vdd_sb_mux_on n_vdd_cb_mux_on\n")
    # Iterate through tiles backwards
    in_node = "n_in"
    for tile in range(wire_length,1,-1):
        out_node = "n_" + str(tile)
        spice_file.write("Xrouting_wire_load_tile_" + str(tile) + " " + in_node + " " + out_node + " n_hang_" + str(tile) + " n_gate n_gate_n n_vdd n_gnd routing_wire_load_tile_"  + str(tile) + "\n")
        in_node = out_node
    # Write tile 1
    spice_file.write("Xrouting_wire_load_tile_1 " + in_node + " n_out n_cb_out n_gate n_gate_n n_vdd n_gnd n_vdd_sb_mux_on n_vdd_cb_mux_on routing_wire_load_tile_1\n")
    spice_file.write(".ENDS\n\n\n")
    
    spice_file.close()

    
    # Create a list of all wires used in this subcircuit
    wire_names_list = []
    wire_names_list.append("wire_gen_routing")
    wire_names_list.append("wire_sb_load_on")
    wire_names_list.append("wire_sb_load_partial")
    wire_names_list.append("wire_sb_load_off")
    wire_names_list.append("wire_cb_load_on")
    wire_names_list.append("wire_cb_load_partial")
    wire_names_list.append("wire_cb_load_off")
    
    return wire_names_list
    
    
def local_routing_load_generate(spice_filename, num_on, num_partial, num_off):
    """ """
    
    # The first thing we want to figure out is the interval between each on load and each partially on load
    # Number of partially on muxes between each on mux
    interval_partial = int(num_partial/num_on)
    # Number of off muxes between each partially on mux
    interval_off = int(num_off/num_partial)

    # Open SPICE file for appending
    spice_file = open(spice_filename, 'a')
    
    spice_file.write("******************************************************************************************\n")
    spice_file.write("* Local routing wire load\n")
    spice_file.write("******************************************************************************************\n")
    spice_file.write(".SUBCKT local_routing_wire_load n_in n_out n_gate n_gate_n n_vdd n_gnd n_vdd_local_mux_on\n")
    
    num_total = int(num_on + num_partial + num_off)
    interval_counter_partial = 0
    interval_counter_off = 0
    on_counter = 0
    partial_counter = 0
    off_counter = 0
    
    # Initialize nodes
    current_node = "n_in"
    next_node = "n_1"
    
    # Write SPICE file while keeping correct intervals between partial and on muxes
    for i in range(num_total):
        if interval_counter_partial == interval_partial and on_counter < num_on:
                # Add an on mux
                interval_counter_partial = 0
                on_counter = on_counter + 1
                if on_counter == num_on:
                    spice_file.write("Xwire_local_routing_" + str(i+1) + " " + current_node + " " + next_node + " wire Rw='wire_local_routing_res/" + str(num_total) + "' Cw='wire_local_routing_cap/" + str(num_total) + "'\n")
                    spice_file.write("Xlocal_mux_on_" + str(on_counter) + " " + next_node + " n_out n_gate n_gate_n n_vdd_local_mux_on n_gnd local_mux_on\n")
                else:
                    spice_file.write("Xwire_local_routing_" + str(i+1) + " " + current_node + " " + next_node + " wire Rw='wire_local_routing_res/" + str(num_total) + "' Cw='wire_local_routing_cap/" + str(num_total) + "'\n")
                    spice_file.write("Xlocal_mux_on_" + str(on_counter) + " " + next_node + " n_hang_" + str(on_counter) + " n_gate n_gate_n n_vdd n_gnd local_mux_on\n")    
        else:
            if interval_counter_off == interval_off and partial_counter < num_partial:
                # Add a partially on mux
                interval_counter_off = 0
                interval_counter_partial = interval_counter_partial + 1
                partial_counter = partial_counter + 1
                spice_file.write("Xwire_local_routing_" + str(i+1) + " " + current_node + " " + next_node + " wire Rw='wire_local_routing_res/" + str(num_total) + "' Cw='wire_local_routing_cap/" + str(num_total) + "'\n")
                spice_file.write("Xlocal_mux_partial_" + str(partial_counter) + " " + next_node + " n_gate n_gate_n n_vdd n_gnd local_mux_partial\n")
            else:
                # Add an off mux
                interval_counter_off = interval_counter_off + 1
                off_counter = off_counter + 1
                spice_file.write("Xwire_local_routing_" + str(i+1) + " " + current_node + " " + next_node + " wire Rw='wire_local_routing_res/" + str(num_total) + "' Cw='wire_local_routing_cap/" + str(num_total) + "'\n")
                spice_file.write("Xlocal_mux_off_" + str(off_counter) + " " + next_node + " n_gate n_gate_n n_vdd n_gnd local_mux_off\n")
        # Update current and next nodes        
        current_node = next_node
        next_node = "n_" + str(i+2)
    spice_file.write(".ENDS\n\n\n")

    spice_file.close()
    
    
    # Create a list of all wires used in this subcircuit
    wire_names_list = []
    wire_names_list.append("wire_local_routing")
    
    return wire_names_list


def hb_local_routing_load_generate(spice_filename, num_on, num_partial, num_off, hb_name, mux_name):
    """ """
    
    # The first thing we want to figure out is the interval between each on load and each partially on load
    # Number of partially on muxes between each on mux
    interval_partial = int(num_partial/num_on)
    # Number of off muxes between each partially on mux
    interval_off = int(num_off/num_partial)

    # Open SPICE file for appending
    spice_file = open(spice_filename, 'a')
    
    spice_file.write("******************************************************************************************\n")
    spice_file.write("* Local routing wire load\n")
    spice_file.write("******************************************************************************************\n")
    spice_file.write(".SUBCKT "+hb_name+" n_in n_out n_gate n_gate_n n_vdd n_gnd n_vdd_local_mux_on\n")
    
    num_total = num_on + num_partial + num_off
    interval_counter_partial = 0
    interval_counter_off = 0
    on_counter = 0
    partial_counter = 0
    off_counter = 0
    
    # Initialize nodes
    current_node = "n_in"
    next_node = "n_1"
    
    # Write SPICE file while keeping correct intervals between partial and on muxes
    for i in range(num_total):
        if interval_counter_partial == interval_partial and on_counter < num_on:
                # Add an on mux
                interval_counter_partial = 0
                on_counter = on_counter + 1
                if on_counter == num_on:
                    spice_file.write("Xwire_local_routing_" + str(i+1) + " " + current_node + " " + next_node + " wire Rw='wire_"+hb_name+"_res/" + str(num_total) + "' Cw='wire_"+hb_name+"_cap/" + str(num_total) + "'\n")
                    spice_file.write("Xlocal_mux_on_" + str(on_counter) + " " + next_node + " n_out n_gate n_gate_n n_vdd_local_mux_on n_gnd "+mux_name+"_on\n")
                else:
                    spice_file.write("Xwire_local_routing_" + str(i+1) + " " + current_node + " " + next_node + " wire Rw='wire_"+hb_name+"_res/" + str(num_total) + "' Cw='wire_"+hb_name+"_cap/" + str(num_total) + "'\n")
                    spice_file.write("Xlocal_mux_on_" + str(on_counter) + " " + next_node + " n_hang_" + str(on_counter) + " n_gate n_gate_n n_vdd n_gnd "+mux_name+"_on\n")    
        else:
            if interval_counter_off == interval_off and partial_counter < num_partial:
                # Add a partially on mux
                interval_counter_off = 0
                interval_counter_partial = interval_counter_partial + 1
                partial_counter = partial_counter + 1
                spice_file.write("Xwire_local_routing_" + str(i+1) + " " + current_node + " " + next_node + " wire Rw='wire_"+hb_name+"_res/" + str(num_total) + "' Cw='wire_"+hb_name+"_cap/" + str(num_total) + "'\n")
                spice_file.write("Xlocal_mux_partial_" + str(partial_counter) + " " + next_node + " n_gate n_gate_n n_vdd n_gnd "+mux_name+"_partial\n")
            else:
                # Add an off mux
                interval_counter_off = interval_counter_off + 1
                off_counter = off_counter + 1
                spice_file.write("Xwire_local_routing_" + str(i+1) + " " + current_node + " " + next_node + " wire Rw='wire_"+hb_name+"_res/" + str(num_total) + "' Cw='wire_"+hb_name+"_cap/" + str(num_total) + "'\n")
                spice_file.write("Xlocal_mux_off_" + str(off_counter) + " " + next_node + " n_gate n_gate_n n_vdd n_gnd "+mux_name+"_off\n")
        # Update current and next nodes        
        current_node = next_node
        next_node = "n_" + str(i+2)
    spice_file.write(".ENDS\n\n\n")

    spice_file.close()
    
    
    # Create a list of all wires used in this subcircuit
    wire_names_list = []
    wire_names_list.append("wire_"+hb_name+"local_routing")
    
    return wire_names_list



def RAM_local_routing_load_generate(spice_filename, num_on, num_partial, num_off):
    """ """
    
    # The first thing we want to figure out is the interval between each on load and each partially on load
    # Number of partially on muxes between each on mux
    interval_partial = int(num_partial/num_on)
    # Number of off muxes between each partially on mux
    interval_off = int(num_off/num_partial)

    # Open SPICE file for appending
    spice_file = open(spice_filename, 'a')
    
    spice_file.write("******************************************************************************************\n")
    spice_file.write("* RAM local routing wire load\n")
    spice_file.write("******************************************************************************************\n")
    spice_file.write(".SUBCKT RAM_local_routing_wire_load n_in n_out n_gate n_gate_n n_vdd n_gnd n_vdd_RAM_local_mux_on\n")
    
    num_total = num_on + num_partial + num_off
    interval_counter_partial = 0
    interval_counter_off = 0
    on_counter = 0
    partial_counter = 0
    off_counter = 0
    
    # Initialize nodes
    current_node = "n_in"
    next_node = "n_1"
    
    # Write SPICE file while keeping correct intervals between partial and on muxes
    for i in range(num_total):
        if interval_counter_partial == interval_partial and on_counter < num_on:
                # Add an on mux
                interval_counter_partial = 0
                on_counter = on_counter + 1
                if on_counter == num_on:
                    spice_file.write("Xwire_RAM_local_routing_" + str(i+1) + " " + current_node + " " + next_node + " wire Rw='wire_RAM_local_routing_res/" + str(num_total) + "' Cw='wire_RAM_local_routing_cap/" + str(num_total) + "'\n")
                    spice_file.write("XRAM_local_mux_on_" + str(on_counter) + " " + next_node + " n_out n_gate n_gate_n n_vdd_RAM_local_mux_on n_gnd RAM_local_mux_on\n")
                else:
                    spice_file.write("Xwire_RAM_local_routing_" + str(i+1) + " " + current_node + " " + next_node + " wire Rw='wire_RAM_local_routing_res/" + str(num_total) + "' Cw='wire_RAM_local_routing_cap/" + str(num_total) + "'\n")
                    spice_file.write("XRAM_local_mux_on_" + str(on_counter) + " " + next_node + " n_hang_" + str(on_counter) + " n_gate n_gate_n n_vdd n_gnd RAM_local_mux_on\n")    
        else:
            if interval_counter_off == interval_off and partial_counter < num_partial:
                # Add a partially on mux
                interval_counter_off = 0
                interval_counter_partial = interval_counter_partial + 1
                partial_counter = partial_counter + 1
                spice_file.write("Xwire_RAM_local_routing_" + str(i+1) + " " + current_node + " " + next_node + " wire Rw='wire_RAM_local_routing_res/" + str(num_total) + "' Cw='wire_RAM_local_routing_cap/" + str(num_total) + "'\n")
                spice_file.write("XRAM_local_mux_partial_" + str(partial_counter) + " " + next_node + " n_gate n_gate_n n_vdd n_gnd RAM_local_mux_partial\n")
            else:
                # Add an off mux
                interval_counter_off = interval_counter_off + 1
                off_counter = off_counter + 1
                spice_file.write("Xwire_RAM_local_routing_" + str(i+1) + " " + current_node + " " + next_node + " wire Rw='wire_RAM_local_routing_res/" + str(num_total) + "' Cw='wire_RAM_local_routing_cap/" + str(num_total) + "'\n")
                spice_file.write("XRAM_local_mux_off_" + str(off_counter) + " " + next_node + " n_gate n_gate_n n_vdd n_gnd RAM_local_mux_off\n")
        # Update current and next nodes        
        current_node = next_node
        next_node = "n_" + str(i+2)
    spice_file.write(".ENDS\n\n\n")

    spice_file.close()
    
    
    # Create a list of all wires used in this subcircuit
    wire_names_list = []
    wire_names_list.append("wire_RAM_local_routing")
    
    return wire_names_list   
 
 
def generate_ble_outputs(spice_filename, num_local_out, num_gen_out):
    """ Create the BLE outputs block. Contains 'num_local_out' local outputs and 'num_gen_out' general outputs. """
    
    #TODO: The order of the wires is weird in this netlist, have a look at it later.
    # Total number of BLE outputs
    total_outputs = num_local_out + num_gen_out
    
    # Open SPICE file for appending
    spice_file = open(spice_filename, 'a')
    
    spice_file.write("******************************************************************************************\n")
    spice_file.write("* BLE outputs\n")
    spice_file.write("******************************************************************************************\n")
    spice_file.write(".SUBCKT ble_outputs n_1_" + str(int((total_outputs + 1)/2)+1) + " n_local_out n_general_out n_gate n_gate_n n_vdd n_gnd n_vdd_local_output_on n_vdd_general_output_on\n")
    # Create the BLE output bar
    current_node = 2
    for i in range(num_local_out):
        #if it is the first 2:1 local ble feedback mux then attach the n_local_out signal to its output else assign a random signal to it
        if i == 0:
            spice_file.write("Xlocal_ble_output_" + str(i+1) + " n_1_" + str(current_node) + " n_local_out n_gate n_gate_n n_vdd_local_output_on n_gnd local_ble_output\n")
        else:
            spice_file.write("Xlocal_ble_output_" + str(i+1) + " n_1_" + str(current_node) + " n_hang_" + str(current_node) + " n_gate n_gate_n n_vdd n_gnd local_ble_output\n")
        spice_file.write("Xwire_ble_outputs_" + str(i+1) + " n_1_" + str(current_node) + " n_1_" + str(current_node + 1) + " wire Rw='wire_ble_outputs_res/" + str(total_outputs-1) + "' Cw='wire_ble_outputs_cap/" + str(total_outputs-1) + "'\n")
        current_node = current_node + 1
    for i in range(num_gen_out):
        #if it is the first 2:1 general ble output mux then attach the n_general_out signal to its output else assign a random signal to it
        if i == 0:
            spice_file.write("Xgeneral_ble_output_" + str(i+1) + " n_1_" + str(current_node) + " n_general_out n_gate n_gate_n n_vdd_general_output_on n_gnd general_ble_output\n")
        else:
            spice_file.write("Xgeneral_ble_output_" + str(i+1) + " n_1_" + str(current_node) + " n_hang_" + str(current_node) + " n_gate n_gate_n n_vdd n_gnd general_ble_output\n")
        # Only add wire if this is not the last ble output.
        if (i+1) != num_gen_out:
            spice_file.write("Xwire_ble_outputs_" + str(num_local_out+i+1) + " n_1_" + str(current_node) + " n_1_" + str(current_node + 1) + " wire Rw='wire_ble_outputs_res/" + str(total_outputs-1) + "' Cw='wire_ble_outputs_cap/" + str(total_outputs-1) + "'\n")
        current_node = current_node + 1
    spice_file.write(".ENDS\n\n\n")

    spice_file.close()
    
    # Create a list of all wires used in this subcircuit
    wire_names_list = []
    wire_names_list.append("wire_ble_outputs")
    
    return wire_names_list
    
    
def generate_lut_output_load(spice_filename, num_local_out, num_gen_out):
    """ Create the LUT output load subcircuit. It consists of a FF which 
        has the register select mux at its input and all BLE outputs which 
        include the output routing mux (Or) and the output feedback mux (Ofb) """

    # Total number of BLE outputs
    total_outputs = num_local_out + num_gen_out

    # Open SPICE file for appending
    spice_file = open(spice_filename, 'a')
    
    spice_file.write("******************************************************************************************\n")
    spice_file.write("* LUT output load\n")
    spice_file.write("******************************************************************************************\n")
    spice_file.write(".SUBCKT lut_output_load n_in n_local_out n_general_out n_gate n_gate_n n_vdd n_gnd n_vdd_local_output_on n_vdd_general_output_on\n")
    spice_file.write("Xwire_lut_output_load_1 n_in n_1_1 wire Rw='wire_lut_output_load_1_res' Cw='wire_lut_output_load_1_cap'\n")
    spice_file.write("Xff n_1_1 n_hang1 n_gate n_gate_n n_vdd n_gnd n_gnd n_vdd n_gnd n_vdd n_vdd n_gnd ff\n")
    spice_file.write("Xwire_lut_output_load_2 n_1_1 n_1_2 wire Rw='wire_lut_output_load_2_res' Cw='wire_lut_output_load_2_cap'\n")
    spice_file.write("Xble_outputs n_1_2 n_local_out n_general_out n_gate n_gate_n n_vdd n_gnd n_vdd_local_output_on n_vdd_general_output_on ble_outputs\n")
    spice_file.write(".ENDS\n\n\n")

    spice_file.close()
    
    # Create a list of all wires used in this subcircuit
    wire_names_list = []
    wire_names_list.append("wire_lut_output_load_1")
    wire_names_list.append("wire_lut_output_load_2")
    
    return wire_names_list
    

def generate_local_ble_output_load(spice_filename):

    # Open SPICE file for appending
    spice_file = open(spice_filename, 'a')
    
    spice_file.write("******************************************************************************************\n")
    spice_file.write("* Local BLE output load\n")
    spice_file.write("******************************************************************************************\n")
    spice_file.write(".SUBCKT local_ble_output_load n_in n_gate n_gate_n n_vdd n_gnd\n")
    spice_file.write("Xwire_local_ble_output_feedback n_in n_1_1 wire Rw='wire_local_ble_output_feedback_res' Cw='wire_local_ble_output_feedback_cap'\n")
    spice_file.write("Xlocal_routing_wire_load_1 n_1_1 n_1_2 n_gate n_gate_n n_vdd n_gnd n_vdd local_routing_wire_load\n")
    spice_file.write("Xlut_a_driver_1 n_1_2 n_hang1 vsram vsram_n n_hang2 n_hang3 n_vdd n_gnd lut_a_driver\n\n")
    spice_file.write(".ENDS\n\n\n")
    
    spice_file.close()
    
    # Create a list of all wires used in this subcircuit
    wire_names_list = []
    wire_names_list.append("wire_local_ble_output_feedback")
    
    return wire_names_list
    
    
def generate_general_ble_output_load(spice_filename, num_sb_mux_off, num_sb_mux_partial, num_sb_mux_on):
    """ Create the cluster output load SPICE deck. We assume 2-level muxes. The load is distributed as
        off, then partial, then on. 
        Inputs are SPICE file, number of SB muxes that are off, then partially on, then on.
        Returns wire names used in this SPICE circuit."""
    
    # Total number of sb muxes connected to this logic cluster output
    sb_mux_total = num_sb_mux_off + num_sb_mux_partial + num_sb_mux_on
    
    # Open SPICE file for appending
    spice_file = open(spice_filename, 'a')
    
    spice_file.write("******************************************************************************************\n")
    spice_file.write("* General BLE output load\n")
    spice_file.write("******************************************************************************************\n")
    spice_file.write(".SUBCKT general_ble_output_load n_1_1 n_out n_gate n_gate_n n_vdd n_gnd\n")
    current_node = "n_1_1"
    next_node = "n_1_2"
    for i in range(num_sb_mux_off):
        spice_file.write("Xwire_general_ble_output_" + str(i+1) + " " + current_node + " " + next_node + " wire Rw='wire_general_ble_output_res/" + str(sb_mux_total) + "' Cw='wire_general_ble_output_cap/" + str(sb_mux_total) + "'\n")
        spice_file.write("Xsb_mux_off_" + str(i+1) + " " + next_node + " n_gate n_gate_n n_vdd n_gnd sb_mux_off\n")
        current_node = next_node
        next_node = "n_1_" + str(i+3)
    for i in range(num_sb_mux_partial):
        spice_file.write("Xwire_general_ble_output_" + str(i+num_sb_mux_off+1) + " " + current_node + " " + next_node + " wire Rw='wire_general_ble_output_res/" + str(sb_mux_total) + "' Cw='wire_general_ble_output_cap/" + str(sb_mux_total) + "'\n")
        spice_file.write("Xsb_mux_partial_" + str(i+1) + " " + next_node + " n_gate n_gate_n n_vdd n_gnd sb_mux_partial\n")
        current_node = next_node
        next_node = "n_1_" + str(i+num_sb_mux_off+3)
    for i in range(num_sb_mux_on):
        
        # The last 'on' sb_mux needs to have special node names to be able to connect it to the output and also for measurements.
        if i == (num_sb_mux_on-1):
            spice_file.write("Xwire_general_ble_output_" + str(i+num_sb_mux_off+num_sb_mux_partial+1) + " " + current_node + " n_meas_point" 
                             + " wire Rw='wire_general_ble_output_res/" + str(sb_mux_total) + "' Cw='wire_general_ble_output_cap/" + str(sb_mux_total) + "'\n")
            spice_file.write("Xsb_mux_on_" + str(i+1) + " n_meas_point n_out n_gate n_gate_n n_vdd n_gnd sb_mux_on\n")
        else:
            spice_file.write("Xwire_general_ble_output_" + str(i+num_sb_mux_off+num_sb_mux_partial+1) + " " + current_node + " " + next_node 
                             + " wire Rw='wire_general_ble_output_res/" + str(sb_mux_total) + "' Cw='wire_general_ble_output_cap/" + str(sb_mux_total) + "'\n")
            spice_file.write("Xsb_mux_on_" + str(i+1) + " " + next_node + " n_hang_" + str(i) + " n_gate n_gate_n n_vdd n_gnd sb_mux_on\n")
        current_node = next_node
        next_node = "n_1_" + str(i+num_sb_mux_off+num_sb_mux_partial+3)

    spice_file.write(".ENDS\n\n\n")
    
    spice_file.close()
    
    # Create a list of all wires used in this subcircuit
    wire_names_list = []
    wire_names_list.append("wire_general_ble_output")
    
    return wire_names_list
