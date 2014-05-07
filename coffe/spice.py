# Python scripts for interfacing to HSPICE
#
# 

import os
import subprocess
from itertools import product

# Global variable for minimum transistor width (45nm)
#min_tran_width = 45

# This global variable tells us how much variation we are willing to tolerate in ERF (in percentage, 0.01 = 1%)
global_erf_tolerance = 0.01

erf_monitor_verbose = True

def expand_ranges(sizing_ranges):
    """ The input to this function is a dictionary that describes the SPICE sweep
        ranges. dict = {"name": (start_value, stop_value, increment)}
        To make it easy to run all the described SPICE simulations, this function
        creates a list of all possible combinations in the ranges.
        It also produces a 'name' list that matches the order of 
        the parameters for each combination."""
    
    # Use a copy of sizing ranges
    sizing_ranges_copy = sizing_ranges.copy()
    
    # Expand the ranges into full list of values    
    for key, values in sizing_ranges_copy.items():
        # Initialization
        start_value = values[0]
        end_value = values[1]
        increment = values[2]
        current_value = start_value
        value_list = []
        # Loop till current values is larger than end value
        while current_value <= end_value:
            value_list.append(current_value)
            current_value = current_value + increment
        # Replace the range with a list
        sizing_ranges_copy[key] = value_list
                                     
    # Now we want to make a list of all possible combinations
    sizing_combinations = [] 
    for combination in product(*[sizing_ranges_copy[i] for i in sorted(sizing_ranges_copy.keys())]):
        sizing_combinations.append(combination)

    # Make a list of sorted parameter names to go with the list of
    # combinations. The sorted list of names will match the order of 
    # items in each combinations of the list. 
    parameter_names = sorted(sizing_ranges_copy.keys())

    return parameter_names, sizing_combinations

    
def get_middle_value_config(param_names, spice_ranges):
    """ """
    
    # Initialize config as a tuple
    config = ()

    # For each parameter, find the mid value and create a config tuple
    for name in param_names:
        # Replaced code with unexpdanded.
        #range_len = len(spice_expanded_ranges[name])
        #mid_val = spice_expanded_ranges[name][range_len/2]
        #config = config + (mid_val,)
        range = spice_ranges[name]
        min = range[0]
        max = range[1]
        mid = (max-min)/2 + min
        config = config + (mid,)
        
    return config

    
def initialize_transistor_file(tran_size_filename, param_names, combo, min_tran_width):
    """ Initializes the transistor sizes file to the values in combo. 
        It does not use any ERF ratios, so all inverters have equal
        NMOS and PMOS sizes. """
    
    spice_params_write = {}
    
    # Create spice params dictionary with the combo
    for i in range(len(param_names)):
        if param_names[i].startswith("inv_"):
            spice_params_write[param_names[i] + "_nmos"] = str(
                                combo[i]*min_tran_width) + "n"
            spice_params_write[param_names[i] + "_pmos"] = str(
                                combo[i]*min_tran_width) + "n" 
        elif param_names[i].startswith("ptran_"):
            spice_params_write[param_names[i] + "_nmos"] = str(
                                combo[i]*min_tran_width) + "n"
        elif param_names[i].startswith("rest_"):
            spice_params_write[param_names[i] + "_pmos"] = str(
                                combo[i]*min_tran_width) + "n"        
      
    # Change parameters transistor library
    spice_params_read = change_params(tran_size_filename, spice_params_write) 
  
    return spice_params_read    
    
    
def make_data_block(element_names, sizing_combos, inv_ratios, wire_rc, min_tran_width):
    """ """

    # Get the wire names
    wire_rc_names = wire_rc[0].keys()
    
    # Make the sweep parameters string needed for .DATA block
    sweep_param_names = ""
    for element_name in element_names:
        if "ptran_" in element_name:
            sweep_param_names += element_name + "_nmos "
        elif "rest_" in element_name:
            sweep_param_names += element_name + "_pmos "
        elif "inv_" in element_name:
            sweep_param_names += element_name + "_nmos "
            sweep_param_names += element_name + "_pmos "
    # Add the wire_rc names for both resistance and capacitance
    for wire_rc_name in wire_rc_names:
        sweep_param_names += wire_rc_name + "_res "
        sweep_param_names += wire_rc_name + "_cap "
     

    data_filename = "sweep_data.l"
    data_file = open(data_filename, 'w')
    data_file.write(".DATA sweep_data " + sweep_param_names + "\n")
    for i in range(len(sizing_combos)):
        combo = sizing_combos[i]
        for i in range(len(combo)):
            element_name = element_names[i]
            # If it is ptran, just write one value (only 1 NMOS)
            if "ptran_" in element_name:
                data_file.write(str(combo[i]*min_tran_width) + "n ")
            # If it is rest, just write one value (only 1 PMOS)
            if "rest_" in element_name:
                data_file.write(str(combo[i]*min_tran_width) + "n ")
            # If element is an inverter, we have to place a NMOS as well as a PMOS value
            elif "inv_" in element_name:
                # If the NMOS is bigger than the PMOS
                if inv_ratios[element_name] < 1:
                    data_file.write(str(int(combo[i]*min_tran_width/inv_ratios[element_name])) + "n ")
                    data_file.write(str(combo[i]*min_tran_width) + "n ")
                # If the PMOS is bigger than the NMOS
                else:
                    data_file.write(str(combo[i]*min_tran_width) + "n ") 
                    data_file.write(str(int(combo[i]*min_tran_width*inv_ratios[element_name])) + "n ")
        # Get wire RC data for this combo
        wire_rc_combo = wire_rc[i]
        # Add wire R and C
        for wire_name in wire_rc_names:
            data_file.write(str(wire_rc_combo[wire_name][0]) + " " + str(wire_rc_combo[wire_name][1]) + "f ")
        data_file.write("\n")
        
    data_file.write(".ENDDATA")
    data_file.close()


def change_params(tran_size_filename, write_params):
    """Set/read parameters in parameter library file.
       write_params is a dictionary {'param name', 'value to write'}
       Returns a dictionary of ALL params and their current value"""
    
    # What we want to do is go through a file line by line and change certain values
    # To do this, we will open two files, the original and a temp file.
    # We copy the contents of the original file to the temp file but with the appropriate
    # changes. When this is complete, we delete the original and rename the temp.
    # We also read all other parameters that don't need to be written.
    
    # Open original file for reading
    original_file = open(tran_size_filename, "r")
    # Open new file for writing
    new_file = open(tran_size_filename + ".tmp", "w")
    
    # Initialize the params_read dictionary
    params_read = {}
    
    # Now we will go through the file line by line.
    # If the line is not a parameter line, just write it to the new file
    # If the line is a parameter line, change the value if required and write to new file
    for line in original_file:
        if ".PARAM" in line:
            words = line.split()
            if words[1] in write_params:
                # Write line to file but with new value
                new_file.write(words[0] + " " + words[1] + " " + words[2] + " " +
                                 write_params[words[1]] + "\n")
                # Add the parameters to the read list
                params_read[words[1]] = write_params[words[1]]
            else:
                # Write it to file
                new_file.write(line)
                # Add the parameters to the read list
                params_read[words[1]] = words[3]    
        else:
            new_file.write(line)
    
    # Close the files
    original_file.close()
    new_file.close()
    
    # Delete the original file and rename new file
    os.remove(tran_size_filename)
    os.rename(tran_size_filename + ".tmp", tran_size_filename)
    
    # Return a dictionary of all the parameters (read and written)
    return params_read


def sweep_setup(filename, tran_size_filename, sweep_settings):
    """Setup a sweep analysis in SPICE file
       sweet_settings is a tuple of the form ("name", "start", "stop", "inc")
       filename is the name of the spice file to modify"""
         
    # What we want to do is go through a file line by line and change certain values
    # To do this, we will open two files, the original and a temp file.
    # We copy the contents of the original file to the temp file but with the appropriate
    # changes. When this is complete, we delete the original and rename the temp.
    
    # Open original spice file for reading
    original_file = open(filename, "r")
    # Open new spice file for writing
    new_file = open(filename + ".tmp", "w")
    
    # Create the sweep string to be added to SPICE file
    sweep_str = (" SWEEP " + sweep_settings[0] + " " + sweep_settings[1] + " "
                     + sweep_settings[2] + " " + sweep_settings[3])
        
    # Now we will go through the file line by line.
    # If the line is not the .TRAN line, just write it to the new file
    # If the line is the .TRAN line, add the SWEEP and write to new file
    
    for line in original_file:
        # If .TRAN statement, modify it
        if ".TRAN" in line:
            line = line.strip() + sweep_str + "\n"
        # Write the line back to new file
        new_file.write(line)
        
    
    # Close the files
    original_file.close()
    new_file.close()
    
    # Delete the original file and rename new file
    os.remove(filename)
    os.rename(filename + ".tmp", filename)
    
    # Read all spice params in a dictionary
    params_read = change_params(tran_size_filename, {})
    
    # Return a dictionary of all the parameters read
    return params_read
    
    
def sweep_data_setup(filename):
    """Setup a sweep analysis for .DATA block in SPICE file
       The name of the .DATA block is assumed to be "sweep_data"
       filename is the name of the spice file to modify"""
         
    # What we want to do is go through a file line by line and change certain values
    # To do this, we will open two files, the original and a temp file.
    # We copy the contents of the original file to the temp file but with the appropriate
    # changes. When this is complete, we delete the original and rename the temp.
    
    # Open original spice file for reading
    original_file = open(filename, "r")
    # Open new spice file for writing
    new_file = open(filename + ".tmp", "w")
    
    # Create the sweep string to be added to SPICE file
    sweep_str = " SWEEP DATA=sweep_data"
        
    # Now we will go through the file line by line.
    # If the line is not the .TRAN line, just write it to the new file
    # If the line is the .TRAN line, add the SWEEP and write to new file
    
    for line in original_file:
        # If .TRAN statement, modify it
        if ".TRAN" in line:
            line = line.strip() + sweep_str + "\n"
        # Write the line back to new file
        new_file.write(line)
        
    
    # Close the files
    original_file.close()
    new_file.close()
    
    # Delete the original file and rename new file
    os.remove(filename)
    os.rename(filename + ".tmp", filename)


def sweep_remove(filename):
    """Remove SWEEP analysis from SPICE file
       filename is the name of the spice file to modify"""
         
    # What we want to do is go through a file line by line and change certain values
    # To do this, we will open two files, the original and a temp file.
    # We copy the contents of the original file to the temp file but with the appropriate
    # changes. When this is complete, we delete the original and rename the temp.
    
    # Open original spice file for reading
    original_file = open(filename, "r")
    # Open new spice file for writing
    new_file = open(filename + ".tmp", "w")
        
    # Now we will go through the file line by line.
    # If the line is not a the .TRAN line, just write it to the new file
    # If the line is a parameter line, add the SWEEP and write to new file
    for line in original_file:
        if ".TRAN" in line:
            words = line.split()
            line = words[0] + " " + words[1] + " " + words[2] + "\n"
        new_file.write(line)
    
    # Close the files
    original_file.close()
    new_file.close()
    
    # Delete the original file and rename new file
    os.remove(filename)
    os.rename(filename + ".tmp", filename)
    

def read_output(filename):
    """Reads the measurements from SPICE output file.
       filename is the name of the SPICE output file
       Returns a dictionary of all measurements found.
       Measurements must start with 'meas_'"""
    
    # Open the file for reading
    output_file = open(filename, "r")
    
    # Initialize the meas_read dictionary 
    meas_read = {}
    
    # Look for measurements and save to dictionary
    for line in output_file:
        if "meas_" in line:
            if "failed" in line:
                # Signal that SPICE failed
                meas_read["failed"] = "failed"
                break
            else:
                split1 = line.split("=")
                measurement_name = split1[0].strip()
                split2 = split1[1].split()
                measurement_value = split2[0]
                # Save the measured value
                meas_read[measurement_name] = convert_num(measurement_value)
    # Close the file
    output_file.close()
    
    return meas_read
 
    
def read_sweep_output(filename, param_name):
    """Reads the measurements from SPICE output file.
       filename is the name of the SPICE output file
       param_name is the parameter name
       Returns a list of all measurements found (abs_diff, sweep_value, tfall, trise)"""
    
    # Open the file for reading
    output_file = open(filename, "r")
    
    # Remove _pmos or _nmos from the parameter name (need to do this to read measurement)
    if param_name.endswith("_pmos"):
        param_name = param_name.replace("_pmos", "")
    elif param_name.endswith("_nmos"):
        param_name = param_name.replace("_nmos", "")
    
    # Initialize the list 
    sweep_erf_list = []
    
    # Initialize the dictionary of all sweep results   
    sweep_meas = {}
    meas_read = {}
           
    # Look for measurements and save to list
    # Works by recognizing sweep parameter value and rise and fall measurements in sequence
    # Remembers values and when trise is found, this completes one list entry so we add
    # it to the list
    sweep_value = -1
    tfall = -1
    trise = -1
    for line in output_file:
        # Initialize the dictionary of measurements
        if ("parameter " + param_name) in line:
            words = line.split()
            sweep_value = float(words[4])
        elif "meas_" in line:
            if "meas_variable" in line:
                # Hack to make work with other HSPICE versions
                continue
            elif "failed" in line:
                # Signal that SPICE failed
                meas_read["failed"] = "failed"
                break
            else:
                # Add the measurement to dictionary
                split1 = line.split("=")
                measurement_name = split1[0].strip()
                split2 = split1[1].split()
                measurement_value = split2[0]
                meas_read[measurement_name] = convert_num(measurement_value)
                # Check if its the sweep results
                if measurement_name == ("meas_" + param_name + "_tfall"):
                    tfall = convert_num(measurement_value)
                elif measurement_name == ("meas_" + param_name + "_trise"):
                    trise = convert_num(measurement_value)
        elif "***** job concluded" in line:
            sweep_erf_list.append((abs(tfall-trise), sweep_value, tfall, trise))
            sweep_meas[sweep_value] = meas_read
            # Create new dictionary
            meas_read = dict()
            
    # Close the file
    output_file.close()
    
    return sweep_erf_list, sweep_meas
    
    
def read_sweep_data_output(filename):
    """Reads the measurements from SPICE output file.
       filename is the name of the SPICE output file
       It reads "meas_total" for tfall and trise
       Returns list of (tfall, trise)"""
    
    # Open the file for reading
    output_file = open(filename, "r")
    
    # Initialize the list 
    sweep_list = []
           
    # Look for measurements and save to list
    # Works by recognizing rise and fall measurements in sequence
    # Remembers values and adds them as a tuple to the sweep list
    tfall = 1
    trise = 1
    for line in output_file:
        if "meas_total" in line:
            if "meas_variable" in line:
                # Hack to make work with other HSPICE versions
                continue
            if "failed" in line:
                # If HSPICE simulation failed, set delay to 1s (huge delay)
                tfall = 1
                trise = 1
            else:
                # Add the measurement to dictionary
                split1 = line.split("=")
                measurement_name = split1[0].strip()
                split2 = split1[1].split()
                measurement_value = split2[0]
                if measurement_value[0] == "-":
                    tfall = 1
                    trise = 1
                elif "_tfall" in line:
                    tfall = convert_num(measurement_value)
                elif "_trise" in line:
                    trise = convert_num(measurement_value)     
        elif "***** job concluded" in line:
            sweep_list.append((tfall, trise))
            
    # Close the file
    output_file.close()
    
    return sweep_list
   
    
def convert_num(spice_number):
    """ Convert a numbers from SPICE output of the form 4.3423p to a float """
    
    # Make dictionary of exponent values
    exponent_values = {"m" : float(1e-3),
                       "u" : float(1e-6),
                       "n" : float(1e-9),
                       "p" : float(1e-12),
                       "f" : float(1e-15),
                       "a" : float(1e-18)}
    
    # The number format depends on the HSPICE version. Some versions use scientific notation,
    # other use letters (e.g. 4.342n)
    
    if spice_number[len(spice_number)-1].isalpha():
        # The coefficient is everything but the last character
        coefficient = float(spice_number[0:len(spice_number)-1])
        # The exponent is the last char (convert to num with dict)
        exponent = exponent_values[spice_number[len(spice_number)-1]]
        number = coefficient*exponent
    else:
        number = float(spice_number)

    return number


def set_parameters(tran_size_filename, param_names, config, inv_ratios, min_tran_width):
    """ The input to this function is the transistor sizes we wish to set.
        But, they aren't necessarily in the format required by the SPICE file.
        (i.e. inv NMOS and PMOS don't have distinct sizes yet, just one size for both,
        and sizes are not in nanometer format, they are in xMin width format)
        This function does this transistor size formating, and then calls
        the change_params to change the parameters in the SPICE file. """
    
    spice_params_write = {}

    # Create spice params dictionary with config
    for i in range(len(param_names)):
        if param_names[i].startswith("inv_"):
            # If NMOS is bigger
            if inv_ratios[param_names[i]] < 1:
                spice_params_write[param_names[i] + "_nmos"] = str(
                    int(config[i]*min_tran_width/inv_ratios[param_names[i]])) + "n"
                spice_params_write[param_names[i] + "_pmos"] = str(
                    config[i]*min_tran_width) + "n" 
            # If PMOS is bigger        
            else:
                spice_params_write[param_names[i] + "_nmos"] = str(
                    config[i]*min_tran_width) + "n"  
                spice_params_write[param_names[i] + "_pmos"] = str(
                    int(config[i]*min_tran_width*inv_ratios[param_names[i]])) + "n"
        elif param_names[i].startswith("ptran_"):
            spice_params_write[param_names[i] + "_nmos"] = str(
                               config[i]*min_tran_width) + "n"
        elif param_names[i].startswith("tgate_"):
            spice_params_write[param_names[i] + "_nmos"] = str(
                                config[i]*min_tran_width) + "n"
            spice_params_write[param_names[i] + "_pmos"] = str(
                                config[i]*min_tran_width) + "n" 
        elif param_names[i].startswith("rest_"):
            spice_params_write[param_names[i] + "_pmos"] = str(
                               config[i]*min_tran_width) + "n" 
    
    # Change parameters in spice file
    spice_params_read = change_params(tran_size_filename, spice_params_write) 
  
    return spice_params_read 
 
# TODO: I think we could merge these two functions 
def set_all_parameters(tran_size_filename, transistor_sizes, min_tran_width):
    """ The input to this function is the transistor sizes we wish to set.
        But, they aren't necessarily in the format required by the SPICE file.
        (i.e. sizes are not in nanometer format, they are in xMin width format)
        This function does this transistor size formating, and then calls
        the change_params to change the parameters in the SPICE file. """
    
    spice_params_write = {}
     
    # Create spice params dictionary with config
    for tran_name, tran_size in transistor_sizes.iteritems():
        spice_params_write[tran_name] = str(tran_size*min_tran_width) + "n" 
    
    # Change parameters in spice file
    spice_params_read = change_params(tran_size_filename, spice_params_write) 
  
    return spice_params_read
 

def run(spice_filedir, spice_filename):
    """ This function simply runs HSPICE on 'spice_filename'. 
        The function does not change any SPICE parameters (transistor sizes, etc.),
        this has to be done before calling this function.
        Returns a dictionary containing all the SPICE measurements. """
    
    # Change working directory so that SPICE output files are created in circuit subdirectory
    saved_cwd = os.getcwd()
    os.chdir(spice_filedir)

    # Run the SPICE simulation and capture console output
    spice_output_filename = spice_filename.rstrip(".sp") + ".output"
    output = open(spice_output_filename, "w")
    subprocess.call(["hspice", spice_filename], stdout=output, stderr=output)
    output.close()
    
    # Read spice measurements    
    spice_measurements = read_output(spice_output_filename)

    # TODO: I just put this here for now, should figure out what is the best way to do this.
    if "meas_logic_low_voltage" in spice_measurements:
        logic_low_voltage = spice_measurements["meas_logic_low_voltage"]
        if logic_low_voltage > 0.01: 
            print "ERROR!!! Logic-low voltage not low enough: " + str(logic_low_voltage)
            spice_measurements["failed"] = "failed"

    # Return to saved cwd
    os.chdir(saved_cwd)
        
    return spice_measurements  
    
    
def spice_inverter(spice_filedir, spice_filename, tran_size_filename, param_name, nmos_size, pmos_size):
    """ Run SPICE to get rise and fall measurements for an inverter.
        spice_filename is the name of the SPICE file to use.
        param_name is the inverter name.
        nmos_size and pmos_size are integer values for nmos and pmos size
        return (trise, tfall, all_read_spice_params)"""
        
    # Make a spice param dictionary
    spice_params_write = {param_name + "_nmos": str(nmos_size) + "n",
                          param_name + "_pmos": str(pmos_size) + "n"}
            
    # Change parameters in transistor library file
    spice_params_read = change_params(tran_size_filename, spice_params_write)
     
    # Change working directory so that SPICE output files are created in circuit subdirectory
    saved_cwd = os.getcwd()
    os.chdir(spice_filedir)
     
    # Run the SPICE simulation and capture console output
    spice_output_filename = spice_filename.rstrip(".sp") + ".output"
    output = open(spice_output_filename, "w")
    subprocess.call(["hspice", spice_filename], stdout=output, stderr=output)
    output.close()
            
    # Read spice measurements    
    spice_measurements = read_output(spice_output_filename)     
    
    # Return to saved cwd
    os.chdir(saved_cwd)
        
    return spice_params_read, spice_measurements
    
    
def sweep(spice_filedir, spice_filename, tran_size_filename, param_name, sweep_values):
    """ Perform a SWEEP analysis with HSPICE. """
        
    # Make sweep settings
    sweep_settings = (param_name, (str(sweep_values[0]) + "n"),
                             (str(sweep_values[1]) + "n"), (str(sweep_values[2]) + "n"))
 
    # Add SWEEP analysis in SPICE file and read all SPICE params
    spice_params_read = sweep_setup(spice_filedir + spice_filename, tran_size_filename, sweep_settings)

    # Change working directory so that SPICE output files are created in circuit subdirectory
    saved_cwd = os.getcwd()
    os.chdir(spice_filedir)
     
    # Run the SPICE simulation and capture console output
    spice_output_filename = spice_filename.rstrip(".sp") + ".output"
    output = open(spice_output_filename, "w")
    subprocess.call(["hspice", spice_filename], stdout=output, stderr=output)
    output.close()
    
    # Read the sweep results        
    sweep_erf, sweep_results = read_sweep_output(spice_output_filename, param_name)
    
    # Return to saved cwd
    os.chdir(saved_cwd)
        
    # Remove the SWEEP analysis from the SPICE file
    sweep_remove(spice_filedir + spice_filename)    
        
    return spice_params_read, sweep_results, sweep_erf
    
    
def sweep_data(spice_filedir, spice_filename):
    """ Perform a SWEEP .DATA analysis with HSPICE. """
        
   
    # Add SWEEP .DATA analysis in SPICE file
    sweep_data_setup(spice_filedir + spice_filename)
     
    # Change working directory so that SPICE output files are created in circuit subdirectory
    saved_cwd = os.getcwd()
    os.chdir(spice_filedir)
     
    # Run the SPICE simulation and capture console output
    spice_output_filename = spice_filename.rstrip(".sp") + ".output"
    output = open(spice_output_filename, "w")
    subprocess.call(["hspice", spice_filename], stdout=output, stderr=output)
    output.close()
    
    # Read the sweep results        
    sweep_results = read_sweep_data_output(spice_output_filename)
        
    # Return to saved cwd
    os.chdir(saved_cwd)
        
    # Remove the SWEEP analysis from the SPICE file
    sweep_remove(spice_filedir + spice_filename)    
        
    return sweep_results

    
def get_total_tfall_trise(name, spice_path):
    """ Run HSPICE on SPICE decks and parse output 
        Returns this tuple: (tfall, trise) """
        
    print 'Updating delay for ' + name
    
    # We are going to change the working directory to the SPICE deck directory so that files generated by SPICE area created there
    saved_cwd = os.getcwd()
    new_cwd = ""
    spice_filename_nodir = ""
    if "/" in spice_path:
        words = spice_path.split("/")
        for i in range(len(words)-1):
            new_cwd = new_cwd + words[i] + "/"
        os.chdir(new_cwd)
        spice_filename_nodir = words[len(words)-1]

    # Run the SPICE simulation and capture console output
    spice_output_filename = spice_filename_nodir.rstrip(".sp") + ".output"
    output = open(spice_output_filename, "w")
    subprocess.call(["hspice", spice_filename_nodir], stdout=output, stderr=output)
    output.close()

    # Return to saved cwd
    os.chdir(saved_cwd)

    # Parse output files
    spice_output = open(spice_path.rstrip(".sp") + ".output", 'r')
    tfall = 0.0
    trise = 0.0
    avg_power = 0.0
    for line in spice_output:
        if 'meas_total_tfall' in line:
            split1 = line.split("=")
            split2 = split1[1].split()
            delay_str = split2[0]
            tfall = convert_num(delay_str)
        elif 'meas_total_trise' in line:
            split1 = line.split("=")
            split2 = split1[1].split()
            delay_str = split2[0]
            trise = convert_num(delay_str)
        elif 'avg_power_gen_routing' in line:
            split1 = line.split("=")
            split2 = split1[1].split()
            power_str = split2[0]
            avg_power = convert_num(power_str)
    spice_output.close()

    return (tfall, trise)
    

def get_inverter_ratios(param_names, spice_params):
    """ """
    
    # Dictionary in which we will store the inverter ratios    
    inv_ratios = {}
    # For each parameter, check if inverter, get inverter ratio PMOS/NMOS
    for name in param_names:
        if "inv_" in name:
            pmos_size = int(spice_params[name + "_pmos"].replace("n", ""))
            nmos_size = int(spice_params[name + "_nmos"].replace("n", ""))
            ratio = float(pmos_size)/nmos_size
            inv_ratios[name] = ratio  

    return inv_ratios  
  
      
def size_inverter_erf(spice_filedir, spice_filename, tran_size_filename, param_name, param_value, min_tran_width, num_hspice_sims):
    """ Sizes an inverter for equal rise and fall
        spice_filedir is the directory where the SPICE file is
        spice_filename is the name of the SPICE file to use
        param_name is the name of the inverter
        param_value is the inverter size
        The function will figure out whether it is nmos or pmos that has the
        param_value size. It will then size the other to achieve equal rise
        and fall."""        
    
    if erf_monitor_verbose:
        print "ERF MONITOR: " + param_name 
     
    # param_size is the true transistor width in nanometers
    param_size = param_value*min_tran_width
    nmos_size = param_size
    pmos_size = param_size
    
    # Run SPICE on inverter for given size, get measurements
    spice_params, spice_meas = spice_inverter(spice_filedir, spice_filename, tran_size_filename, param_name,
                                                nmos_size, pmos_size)
    num_hspice_sims += 1
                                                
    # Check if SPICE failed
    if "failed" in spice_meas:
        print "SPICE failed on first ERF run"
        return spice_params, spice_meas
                                                    
    # Get trise and tfall measurements for this inverter    
    inv_tfall = spice_meas["meas_" + param_name + "_tfall"]
    inv_trise = spice_meas["meas_" + param_name + "_trise"]

    # The first step in sizing for equal rise and fall is to find out which
    # transistor needs to be larger, the nmos or the pmos. To do this, we
    # make them both of equal size (size=param_value) and compare the rise
    # and fall times. If the rise time is faster, nmos must be made bigger.
    # If the fall time is faster, pmos must be made bigger. 
    if inv_trise > inv_tfall:
        # PMOS must be larger than NMOS
        
        # The first thing we want to do is increase the PMOS size in fixed increments
        # to get an upper bound on the PMOS size.
        # We also monitor trise. We expect that increasing the PMOS size will decrease
        # the rise time and increase the fall time. If at any time, we see that increasing the PMOS is increasing 
        # the rise time, we should stop increasing the PMOS size. This means we might be self-loading the inverter.
        upper_bound_not_found = True
        nmos_size = param_size
        mult = 2
        previous_trise = 1
        self_loading = False
        if erf_monitor_verbose:
            print "Looking for PMOS size upper bound"
        while upper_bound_not_found and not self_loading:
            pmos_size = mult*nmos_size
            sizing_bounds_str = "NMOS=" + str(nmos_size) + "  PMOS=" + str(pmos_size)
            spice_params, spice_meas = spice_inverter(spice_filedir, spice_filename, tran_size_filename, param_name, nmos_size, pmos_size)
            num_hspice_sims += 1
            # Get trise and tfall measurements for this inverter    
            tfall = spice_meas["meas_" + param_name + "_tfall"]
            trise = spice_meas["meas_" + param_name + "_trise"]
            if erf_monitor_verbose:
                print sizing_bounds_str + ": tfall=" + str(tfall) + " trise=" + str(trise) + " diff=" + str(tfall-trise)
            # If fall time becomes bigger, we have found the upper bound
            if tfall > trise:
                upper_bound_not_found = False
                if erf_monitor_verbose:
                    print "Upper bound found, PMOS=" + str(pmos_size)
            else:
                # Check if trise is increasing or decreasing
                if previous_trise != 1:
                    if trise > previous_trise:
                        self_loading = True
                        if erf_monitor_verbose:
                            print "Increasing PMOS is no longer decreasing trise, using PMOS=" + str(pmos_size)
                previous_trise = trise    
            
            mult = mult+1

        # If not self-loading, find the ERF size, if self loaded, just use current PMOS size
        if not self_loading:      
            # Now, we know that the equality occurs somewhere in [pmos_size-nmos_size, pmos_size]
            # We are going to search this range in intervals of min transistor width
            if erf_monitor_verbose:
                print "Running HSPICE sweep..."
            incr = min_tran_width
            spice_values = (pmos_size-nmos_size, pmos_size, incr)
            spice_params, sweep_results, sweep_erf = sweep(spice_filedir, spice_filename, tran_size_filename,
                                                        (param_name + "_pmos"), spice_values)
            num_hspice_sims += int(nmos_size/incr)
    
            # Find the interval that contains the ERF
            imin = 0
            imax = 0
            for i in range(len(sweep_erf)):
                # If tfall > trise
                if sweep_erf[i][2] > sweep_erf[i][3]:
                    imax = i
                    imin = i-1
                    break     

            if imin == imax:
                if erf_monitor_verbose:
                    print "Cannot skew P/N ratio enough for ERF on " + param_name

            # Min & Max PMOS sizes
            pmos_min = sweep_erf[imin][1]
            pmos_max = sweep_erf[imax][1]
            if erf_monitor_verbose:
                print "ERF PMOS size in range: [" + str(int(pmos_min/1e-9)) + ", " + str(int(pmos_max/1e-9)) + "]"
            
            # Now we know that ERF is in PMOS = [pmos_min, pmos_max]
            # We will sweep this for every single value in the range
            if erf_monitor_verbose:
                print "Running HSPICE sweep..."
            spice_values = (pmos_min, pmos_max, 1)
            spice_params, sweep_results, sweep_erf = sweep(spice_filedir, spice_filename, tran_size_filename,
                                                          (param_name + "_pmos"), spice_values)
            num_hspice_sims += int((pmos_max-pmos_min)/incr)

            # Sort list based on diff (first element of tuple)
            sweep_erf.sort()
            
            # Get pmos_size from sorted results (in nm)
            pmos_size = int(round(sweep_erf[0][1]/1e-9))
            
            if erf_monitor_verbose:
                print "ERF PMOS size is " + str(pmos_size) + "\n"
            
            # Get the SPICE measurements for this pmos size
            spice_meas = sweep_results[sweep_erf[0][1]]
        
        # Change the spice_params to match this PMOS size
        spice_params[param_name + "_pmos"] = str(pmos_size) + "n"

        # Write the SPICE params to the SPICE file such that we have an inverter sized for ERF
        spice_params = change_params(tran_size_filename, spice_params)

                                                                    
    else:
        # NMOS must be larger than PMOS
        # The first thing we want to do is increase the NMOS size in fixed increments
        # to get an upper bound on the PNOS size.
        # We also monitor tfall. We expect that increasing the NMOS size will decrease
        # the fall time and increase the rise time. If at any time, we see that increasing the NMOS is increasing 
        # the fall time, we should stop increasing the NMOS size. This means we might be self-loading the inverter.
        upper_bound_not_found = True
        pmos_size = param_size
        mult = 2
        previous_tfall = 1
        self_loading = False
        if erf_monitor_verbose:
            print "Looking for NMOS size upper bound"
        while upper_bound_not_found:
            nmos_size = mult*pmos_size
            sizing_bounds_str = "NMOS=" + str(nmos_size) + "  PMOS=" + str(pmos_size)            
            spice_params, spice_meas = spice_inverter(spice_filedir, spice_filename, tran_size_filename, param_name, nmos_size, pmos_size)
            num_hspice_sims += 1
            # Get trise and tfall measurements for this inverter    
            tfall = spice_meas["meas_" + param_name + "_tfall"]
            trise = spice_meas["meas_" + param_name + "_trise"]
            if erf_monitor_verbose:
                print sizing_bounds_str + ": tfall=" + str(tfall) + " trise=" + str(trise) + " diff=" + str(tfall-trise)
            # If rise time becomes bigger, we have found the upper bound
            if trise > tfall:
                upper_bound_not_found = False
                if erf_monitor_verbose:
                    print "Upper bound found, NMOS=" + str(nmos_size)
            else:
                # Check if tfall is increasing or decreasing
                if previous_tfall != 1:
                    if tfall > previous_tfall:
                        self_loading = True
                        if erf_monitor_verbose:
                            print "Increasing NMOS is no longer decreasing tfall, using PMOS=" + str(nmos_size)
                previous_trise = trise
            
            mult = mult+1
        
        # If not self-loading, find the ERF size, if self loaded, just use current PMOS size
        if not self_loading:  
            # Now, we know that the equality occurs somewhere in [nmos_size-pmos_size, nmos_size]
            # We are going to search this range in intervals of min transistor width
            if erf_monitor_verbose:
                print "Running HSPICE sweep..."
            incr = min_tran_width
            spice_values = (nmos_size-pmos_size, nmos_size, incr)
            spice_params, sweep_results, sweep_erf = sweep(spice_filedir, spice_filename, tran_size_filename,
                                                        (param_name + "_nmos"), spice_values)
            num_hspice_sims += int(pmos_size/incr)
            
            # Find the interval that contains the ERF
            imin = 0
            imax = 0
            for i in range(len(sweep_erf)):
                # If tfall < trise
                if sweep_erf[i][2] < sweep_erf[i][3]:
                    imax = i
                    imin = i-1
                    break     
            
            if imin == imax:
                if erf_monitor_verbose:
                    print "Cannot skew P/N ratio enough for ERF on " + param_name
                
            # Min & Max NMOS sizes
            nmos_min = sweep_erf[imin][1]
            nmos_max = sweep_erf[imax][1]
            if erf_monitor_verbose:
                print "ERF NMOS size in range: [" + str(int(nmos_min/1e-9)) + ", " + str(int(nmos_max/1e-9)) + "]"
            
            # Now we know that ERF is in NMOS = [nmos_min, nmos_max]
            # We will sweep this for every single value in the range
            if erf_monitor_verbose:
                print "Running HSPICE sweep..."
            spice_values = (nmos_min, nmos_max, 1)
            spice_params, sweep_results, sweep_erf = sweep(spice_filedir, spice_filename, tran_size_filename,
                                                          (param_name + "_nmos"), spice_values)
            num_hspice_sims += int(nmos_max-nmos_min)
            
            # Sort list based on diff (first element of tuple)
            sweep_erf.sort()
            
            # Get nmos_size from sorted results (in nm)
            nmos_size = int(round(sweep_erf[0][1]/1e-9))
            
            if erf_monitor_verbose:
                print "ERF NMOS size is " + str(nmos_size) + "\n"
        
        # Change the spice_params to match this NMOS size
        spice_params[param_name + "_nmos"] = str(nmos_size) + "n"
        
        # Get the SPICE measurements for this nmos size
        spice_meas = sweep_results[sweep_erf[0][1]]
        
        # Write the SPICE params to the SPICE file such that we have an inverter sized for ERF
        spice_params = change_params(tran_size_filename, spice_params)
    
    return spice_params, spice_meas, num_hspice_sims 
    
    
def erf(spice_filedir, spice_filename, tran_size_filename, param_names, config, min_tran_width, num_hspice_sims):
    """ Equalize rise and fall times of all inverters listed in 'params_names' for this 'config'.
        Returns the inverter ratios that give equal rise and fall. """

    # This function will equalize rise and fall times on all inverters in the input 'param_names'
    # It iteratively finds P/N ratios that equalize the rise and fall times of each inverter.
    # Iteration stops if we find the same P/N ratios more than once, or if all rise and fall times are
    # found to be sufficiently equal.
   
    # Dictionary {'inv_name': (nmos_list, pmos_list)}, for each inverter, it holds an NMOS list and PMOS list. 
    # nmos_list[i] and pmos_list[i] give balanced rise and fall. Each ERF iteration adds a transistor size to these lists
    inverter_sizes = {}
    
    # This list holds a string that we can print
    iteration_str_list = []
    
    # Size each inverter for equal rise and fall. 
    # Save inverter NMOS and PMOS sizes in a list.
    # Assume inverter sizing will be stable after one iteration
    inverter_sizing_stable = True
    sizing_str_list = []
    for i in range(len(param_names)):
        # Is the parameter an inverter?
        if param_names[i].startswith("inv_"):
            # Size the inverter for equal rise and fall
            spice_params, spice_meas, num_hspice_sims = size_inverter_erf(spice_filedir, 
                                                                          spice_filename, 
                                                                          tran_size_filename, 
                                                                          param_names[i], 
                                                                          config[i], 
                                                                          min_tran_width, 
                                                                          num_hspice_sims)
                                                 
            # Check to see if SPICE failed
            if "failed" in spice_meas:
                print "SPICE failed!"
                return spice_params, spice_meas
                 
            # Get NMOS and PMOS sizes for this inverter
            nmos_size = str(spice_params[param_names[i] + "_nmos"].rstrip("n"))
            pmos_size = str(spice_params[param_names[i] + "_pmos"].rstrip("n"))
            nmos_list = []
            pmos_list = [] 
            nmos_list.append(nmos_size)
            pmos_list.append(pmos_size)    
            inverter_sizes[param_names[i]] = (nmos_list, pmos_list)  
            tfall = spice_meas["meas_" + param_names[i] + "_tfall"]
            trise = spice_meas["meas_" + param_names[i] + "_trise"]    
            # Make output strings
            sizing_str_list.append(param_names[i] + "(N=" + str(nmos_size) + " P=" + str(pmos_size) + ", Fall=" + str(tfall) + ", Rise=" +str(trise) + ")")
            
            # Check to see if ERF meets tolerance constraint
            erf_error = abs(tfall-trise)/tfall
            if erf_error > global_erf_tolerance:
                # ERF tolerance not met, sizing is not stable, need more iterations
                inverter_sizing_stable = False
    
    # Print initial sizing results
    if erf_monitor_verbose:
        print "ERF Sizing Summary:"
        print "Iteration 1"
        for sizing_str in sizing_str_list:
            print sizing_str
        if inverter_sizing_stable:
            print "ERF sizing complete"
        else:
            print "ERF results not satisfactory, doing it again."
        print ""
    iteration_str_list.append(sizing_str_list)

    # If sizing is not stable:
    # Iteratively size inverters for equal rise and fall until inverter sizes stable
    # We consider inverter sizes are stable as soon as we obtain the same inverter
    # sizing twice or the sizing meets the ERF tolerance
    while not inverter_sizing_stable:
        sizing_str_list = []    
        # Assume that inverter sizings are stable
        inverter_sizing_stable = True
        # For each inverter, size for ERF again and compare to previous sizes
        for i in range(len(param_names)):
            # Is the parameter an inverter?
            if param_names[i].startswith("inv_"):
                # Size the inverter for equal rise and fall
                spice_params, spice_meas, num_hspice_sims = size_inverter_erf(spice_filedir, 
                                                                              spice_filename, 
                                                                              tran_size_filename, 
                                                                              param_names[i], 
                                                                              config[i], 
                                                                              min_tran_width, 
                                                                              num_hspice_sims)
                
                # Get NMOS and PMOS sizes for this inverter                       
                nmos_size = str(spice_params[param_names[i] + "_nmos"].rstrip("n"))
                pmos_size = str(spice_params[param_names[i] + "_pmos"].rstrip("n"))
                
                # Get the measurements
                tfall = spice_meas["meas_" + param_names[i] + "_tfall"]
                trise = spice_meas["meas_" + param_names[i] + "_trise"]
                
                # Check if this sizing has been obtained before
                if (nmos_size not in inverter_sizes[param_names[i]][0]) or (
                         pmos_size not in inverter_sizes[param_names[i]][1]):
                    # Inverter sizing has not been obtained before
                    # So, we can only exit loop if ERF tolerance is met
                    erf_error = abs(tfall - trise)/tfall
                    if erf_error > global_erf_tolerance:
                        # ERF tolerance not met, sizing is not stable, need more iterations
                        inverter_sizing_stable = False
                
                # Remember new transistor sizes
                inverter_sizes[param_names[i]][0].append(nmos_size)
                inverter_sizes[param_names[i]][1].append(pmos_size)

                # Add to output string
                sizing_str_list.append(param_names[i] + "(N=" + str(nmos_size) + " P=" + str(pmos_size) + ", Fall=" + str(tfall) + ", Rise=" +str(trise)  + ")")   
         
        iteration_str_list.append(sizing_str_list) 
        
        # Print status messages
        if erf_monitor_verbose:
            print "ERF Sizing Summary:"
            for i in range(len(iteration_str_list)):
                sizing_str_list = iteration_str_list[i]
                print "Iteration " + str(i+1)
                for sizing_str in sizing_str_list:
                    print sizing_str
            if inverter_sizing_stable:
                print "ERF sizing complete"
            else:
                print "ERF results not satisfactory, doing it again."    
            print ""

    # Get the ERF ratios
    erf_ratios = get_inverter_ratios(param_names, spice_params)
                         
    return erf_ratios, num_hspice_sims
                  
