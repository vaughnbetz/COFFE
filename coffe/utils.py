import sys
import os


def compare_tfall_trise(tfall, trise):
    """ Compare tfall and trise and returns largest value or -1.0
        -1.0 is return if something went wrong in SPICE """
    
    # Initialize output delay
    delay = -1.0
    
    # Compare tfall and trise
    if (tfall == 0.0) or (trise == 0.0):
        # Couldn't find one of the values in output
        # This is an error because maybe SPICE failed
        delay = -1.0
    elif tfall > trise:
        if tfall > 0.0:
            # tfall is positive and bigger than the trise, this is a valid result
            delay = tfall
        else:
            # Both tfall and trise are negative, this is an invalid result
            delay = -1.0
    elif trise >= tfall:
        if trise > 0.0:
            # trise is positive and larger or equal to tfall, this is value result
            delay = trise
        else:
            delay = -1.0
    else:
        delay = -1.0
        
    return delay
   
    
def print_area_and_delay(fpga_inst):
    """ Print area and delay per subcircuit """
    
    print "  SUBCIRCUIT AREA & DELAY"
    print "  -----------------------"
    
    area_dict = fpga_inst.area_dict

    # I'm using 'ljust' to create neat columns for printing this data. 
    # If subcircuit names are changed, it might make this printing function 
    # not work as well. The 'ljust' constants would have to be adjusted accordingly.
    
    # Print the header
    print "  Subcircuit".ljust(24) + "Area (um^2)".ljust(13) + "Delay (ps)".ljust(13) + "trise (ps)".ljust(13) + "tfall (ps)".ljust(13)
    
    # Switch block mux
    print "  " + fpga_inst.sb_mux.name.ljust(22) + str(round(area_dict[fpga_inst.sb_mux.name]/1e6,3)).ljust(13) + str(round(fpga_inst.sb_mux.delay/1e-12,4)).ljust(13) + str(round(fpga_inst.sb_mux.tfall/1e-12,4)).ljust(13) + str(round(fpga_inst.sb_mux.trise/1e-12,4)).ljust(13)
    
    # Connection block mux
    print "  " + fpga_inst.cb_mux.name.ljust(22) + str(round(area_dict[fpga_inst.cb_mux.name]/1e6,3)).ljust(13) + str(round(fpga_inst.cb_mux.delay/1e-12,4)).ljust(13) + str(round(fpga_inst.cb_mux.tfall/1e-12,4)).ljust(13) + str(round(fpga_inst.cb_mux.trise/1e-12,4)).ljust(13)
    
    # Local mux
    print "  " + fpga_inst.logic_cluster.local_mux.name.ljust(22) + str(round(area_dict[fpga_inst.logic_cluster.local_mux.name]/1e6,3)).ljust(13) + str(round(fpga_inst.logic_cluster.local_mux.delay/1e-12,4)).ljust(13) + str(round(fpga_inst.logic_cluster.local_mux.tfall/1e-12,4)).ljust(13) + str(round(fpga_inst.logic_cluster.local_mux.trise/1e-12,4)).ljust(13)
    
    # Local BLE output
    print "  " + fpga_inst.logic_cluster.ble.local_output.name.ljust(22) + str(round(area_dict[fpga_inst.logic_cluster.ble.local_output.name]/1e6,3)).ljust(13) + str(round(fpga_inst.logic_cluster.ble.local_output.delay/1e-12,4)).ljust(13) + str(round(fpga_inst.logic_cluster.ble.local_output.tfall/1e-12,4)).ljust(13) + str(round(fpga_inst.logic_cluster.ble.local_output.trise/1e-12,4)).ljust(13)
    
    # General BLE output
    print "  " + fpga_inst.logic_cluster.ble.general_output.name.ljust(22) + str(round(area_dict[fpga_inst.logic_cluster.ble.general_output.name]/1e6,3)).ljust(13) + str(round(fpga_inst.logic_cluster.ble.general_output.delay/1e-12,4)).ljust(13) + str(round(fpga_inst.logic_cluster.ble.general_output.tfall/1e-12,4)).ljust(13) + str(round(fpga_inst.logic_cluster.ble.general_output.trise/1e-12,4)).ljust(13)
    
    # LUT
    print "  " + fpga_inst.logic_cluster.ble.lut.name.ljust(22) + str(round(area_dict[fpga_inst.logic_cluster.ble.lut.name]/1e6,3)).ljust(13) + str(round(fpga_inst.logic_cluster.ble.lut.delay/1e-12,4)).ljust(13) + str(round(fpga_inst.logic_cluster.ble.lut.tfall/1e-12,4)).ljust(13) + str(round(fpga_inst.logic_cluster.ble.lut.trise/1e-12,4)).ljust(13)
    
    # Get LUT input names so that we can print inputs in sorted order
    lut_input_names = fpga_inst.logic_cluster.ble.lut.input_drivers.keys()
    lut_input_names.sort()
      
    # LUT input drivers
    for input_name in lut_input_names:
        driver = fpga_inst.logic_cluster.ble.lut.input_drivers[input_name].driver
        not_driver = fpga_inst.logic_cluster.ble.lut.input_drivers[input_name].not_driver
        print "  " + driver.name.ljust(22) + str(round(area_dict[driver.name]/1e6,3)).ljust(13) + str(round(driver.delay/1e-12,4)).ljust(13) + str(round(driver.tfall/1e-12,4)).ljust(13) + str(round(driver.trise/1e-12,4)).ljust(13)
        print "  " + not_driver.name.ljust(22) + str(round(area_dict[not_driver.name]/1e6,3)).ljust(13) + str(round(not_driver.delay/1e-12,4)).ljust(13) + str(round(not_driver.tfall/1e-12,4)).ljust(13) + str(round(not_driver.trise/1e-12,4)).ljust(13)
    
    print ""

    
def print_block_area(fpga_inst):
        """ Print physical area of important blocks (like SB, CB, LUT, etc.) in um^2 """
        
        tile = fpga_inst.area_dict["tile"]/1000000
        lut = fpga_inst.area_dict["lut_total"]/1000000
        ff = fpga_inst.area_dict["ff_total"]/1000000
        ble_output = fpga_inst.area_dict["ble_output_total"]/1000000
        local_mux = fpga_inst.area_dict["local_mux_total"]/1000000
        cb = fpga_inst.area_dict["cb_total"]/1000000
        sb = fpga_inst.area_dict["sb_total"]/1000000
        sanity_check = lut+ff+ble_output+local_mux+cb+sb
        
        print "  TILE AREA CONTRIBUTIONS"
        print "  -----------------------"
        print "  Block".ljust(20) + "Total Area (um^2)".ljust(20) + "Fraction of total tile area"
        print "  Tile".ljust(20) + str(round(tile,3)).ljust(20) + "100%"
        print "  LUT".ljust(20) + str(round(lut,3)).ljust(20) + str(round(lut/tile*100,3)) + "%"
        print "  FF".ljust(20) + str(round(ff,3)).ljust(20) + str(round(ff/tile*100,3)) + "%"
        print "  BLE output".ljust(20) + str(round(ble_output,3)).ljust(20) + str(round(ble_output/tile*100,3)) + "%"
        print "  Local mux".ljust(20) + str(round(local_mux,3)).ljust(20) + str(round(local_mux/tile*100,3)) + "%"
        print "  Connection block".ljust(20) + str(round(cb,3)).ljust(20) + str(round(cb/tile*100,3)) + "%"
        print "  Switch block".ljust(20) + str(round(sb,3)).ljust(20) + str(round(sb/tile*100,3)) + "%"
        print ""    
  
  
def print_vpr_delays(fpga_inst):

    print "  VPR DELAYS"
    print "  ----------"
    print "  Path".ljust(50) + "Delay (ps)"
    print "  Tdel (routing switch)".ljust(50) + str(fpga_inst.sb_mux.delay)
    print "  T_ipin_cblock (connection block mux)".ljust(50) + str(fpga_inst.cb_mux.delay)
    print "  CLB input -> BLE input (local CLB routing)".ljust(50) + str(fpga_inst.logic_cluster.local_mux.delay)
    print "  LUT output -> BLE input (local feedback)".ljust(50) + str(fpga_inst.logic_cluster.ble.local_output.delay)
    print "  LUT output -> CLB output (logic block output)".ljust(50) + str(fpga_inst.logic_cluster.ble.general_output.delay)
    
    # Figure out LUT delays
    lut_input_names = fpga_inst.logic_cluster.ble.lut.input_drivers.keys()
    lut_input_names.sort()
    for input_name in lut_input_names:
        lut_input = fpga_inst.logic_cluster.ble.lut.input_drivers[input_name]
        driver_delay = max(lut_input.driver.delay, lut_input.not_driver.delay)
        path_delay = lut_input.delay
        print ("  lut_" + input_name).ljust(50) + str(driver_delay+path_delay)
    
    print ""
 

def print_vpr_areas(fpga_inst):

    print "  VPR AREAS"
    print "  ----------"
    print "  grid_logic_tile_area".ljust(50) + str(fpga_inst.area_dict["logic_cluster"]/fpga_inst.specs.min_width_tran_area)
    print "  ipin_mux_trans_size (connection block mux)".ljust(50) + str(fpga_inst.area_dict["ipin_mux_trans_size"]/fpga_inst.specs.min_width_tran_area)
    print "  mux_trans_size (routing switch)".ljust(50) + str(fpga_inst.area_dict["switch_mux_trans_size"]/fpga_inst.specs.min_width_tran_area)
    print "  buf_size (routing switch)".ljust(50) + str(fpga_inst.area_dict["switch_buf_size"]/fpga_inst.specs.min_width_tran_area)
    print ""

    
def load_arch_params(filename):
    """ Parse the architecture description file and load values into dictionary. 
        Returns this dictionary.
        Will print error message and terminate program if an invalid parameter is found
        or if a parameter is missing.
        """
    
    # This is the dictionary of parameters we expect to find
    arch_params = {
        'W': -1,
        'L': -1,
        'Fs': -1,
        'N': -1,
        'K': -1,
        'I': -1,
        'Fcin': -1.0,
        'Fcout': -1.0,
        'Or': -1,
        'Ofb': -1,
        'Fclocal': -1.0,
        'Rsel': "",
        'Rfb': "",
        'vdd': -1,
        'vsram': -1,
        'vsram_n': -1,
        'gate_length': -1,
        'min_tran_width': -1,
        'min_width_tran_area': -1,
        'sram_cell_area': -1,
        'model_path': "",
        'model_library': "",
        'metal' : []
    }

    params_file = open(filename, 'r')
    for line in params_file:
    
        # Ignore comment lines
        if line.startswith('#'):
            continue
        
        # Remove line feeds and spaces
        line = line.replace('\n', '')
        line = line.replace('\r', '')
        line = line.replace('\t', '')
        line = line.replace(' ', '')
        
        # Ignore empty lines
        if line == "":
            continue
        
        # Split lines at '='
        words = line.split('=')
        if words[0] not in arch_params.keys():
            print "ERROR: Found invalid architecture parameter (" + words[0] + ") in " + filename
            sys.exit()
         
        param = words[0]
        value = words[1]
             
        if param == 'W':
            arch_params['W'] = int(value)
        elif param == 'L':
            arch_params['L'] = int(value)
        elif param == 'Fs':
            arch_params['Fs'] = int(value)
        elif param == 'N':
            arch_params['N'] = int(value)
        elif param == 'K':
            arch_params['K'] = int(value)
        elif param == 'I':
            arch_params['I'] = int(value)
        elif param == 'Fcin':
            arch_params['Fcin'] = float(value)
        elif param == 'Fcout':
            arch_params['Fcout'] = float(value) 
        elif param == 'Or':
            arch_params['Or'] = int(value)
        elif param == 'Ofb':
            arch_params['Ofb'] = int(value)
        elif param == 'Fclocal':
            arch_params['Fclocal'] = float(value)
        elif param == 'Rsel':
            # Check if this is a valid value for Rsel
            if value != 'z' and (value < 'a' or value > chr(arch_params['K']+96)):
                print "ERROR: Invalid value (" + str(value) + ") for Rsel in " + filename
                sys.exit()
            arch_params['Rsel'] = value
        elif param == 'Rfb':
            # Check if this is a valid value for Rfb
            # If the value is only Z, there are no register feedback muxes, that's valid
            if value == 'z':
                arch_params['Rfb'] = value
            elif len(value) > arch_params['K']:
                print "ERROR: Invalid value (" + str(value) + ") for Rfb in " + filename + " (string too long)"
                sys.exit()
            else:
                # Now, let's make sure all these characters are valid characters
                for character in value:
                    # The character has to be a valid LUT input
                    if (character < 'a' or character > chr(arch_params['K']+96)):
                        print "ERROR: Invalid value (" + str(value) + ") for Rfb in " + filename + " (" + character + " is not valid)"
                        sys.exit()
                    # The character should not appear twice
                    elif value.count(character) > 1:
                        print "ERROR: Invalid value (" + str(value) + ") for Rfb in " + filename + " (" + character + " appears more than once)"
                        sys.exit()
                arch_params['Rfb'] = value
        elif param == 'vdd':
            arch_params['vdd'] = float(value)
        elif param == 'vsram':
            arch_params['vsram'] = float(value)
        elif param == 'vsram_n':
            arch_params['vsram_n'] = float(value)
        elif param == 'gate_length':
            arch_params['gate_length'] = int(value)
        elif param == 'min_tran_width':
            arch_params['min_tran_width'] = int(value)
        elif param == 'min_width_tran_area':
            arch_params['min_width_tran_area'] = int(value)
        elif param == 'sram_cell_area':
            arch_params['sram_cell_area'] = float(value)
        elif param == 'model_path':
            arch_params['model_path'] = os.path.abspath(value)
        elif param == 'model_library':
            arch_params['model_library'] = value
        elif param == 'metal':
            value_words = value.split(',')
            r = value_words[0].replace(' ', '')
            r = r.replace(' ', '')
            r = r.replace('\n', '')
            r = r.replace('\r', '')
            r = r.replace('\t', '')
            c = value_words[1].replace(' ', '')
            c = c.replace(' ', '')
            c = c.replace('\n', '')
            c = c.replace('\r', '')
            c = c.replace('\t', '')
            arch_params['metal'].append((float(r),float(c)))
    
    params_file.close()
    
    # Check that we read everything
    for param, value in arch_params.iteritems():
        if value == -1 or value == "":
            print "ERROR: Did not find architecture parameter " + param + " in " + filename
            sys.exit()
    
    return arch_params 