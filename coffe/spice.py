# This file defines an HSPICE interface class. An object if this class is can be used to 
# run HSPICE jobs and parse the output of those jobs.

import os
import subprocess
import coffe.utils as utils

# All .sp files should be created to use sweep_data.l to set parameters.
HSPICE_DATA_SWEEP_PATH = "sweep_data.l"

# The contents of 
DATA_SWEEP_PATH = "data.txt"


class SpiceInterface(object):
    """
    Defines an HSPICE interface class. 
    An object of this class can be used to run HSPICE jobs and parse the output of those jobs.
    """

    def __init__(self):

        # This simulation counter keeps track of number of HSPICE sims performed.
        self.simulation_counter = 0

        return


    def get_num_simulations_performed(self):
        """
        Returns the total number of HSPICE sims performed by this SpiceInterface object.
        """

        return self.simulation_counter


    def _setup_data_sweep_file(self, parameter_dict):
        """
        Create an HSPICE .DATA statement with the data from parameter_dict.
        The .DATA file is hard to read. So, we also write out the parameters to a text file
        in an easy to read format. This makes it easier to debug.
        """
        
        max_items_per_line = 4

        # Get a list of parameter names
        param_list = parameter_dict.keys()

        # Write out parameters to a "easy to read format" file (this just helps for debug) 
        data_file = open(DATA_SWEEP_PATH, 'w')
        data_file.write("param            value\n")
        data_file.write("----------------------\n")
        for param in param_list :
            data_file.write( param )
            for i in range(len(parameter_dict[param])) :
                data_file.write( "    " + str(parameter_dict[param][i]))

            data_file.write("\n")
        data_file.close()

        # Write the .DATA HPSICE file. This first part writes out the header.
        hspice_data_file = open(HSPICE_DATA_SWEEP_PATH, 'w')
        hspice_data_file.write(".DATA sweep_data")
        item_counter = 0
        for param_name in param_list:
            if item_counter >= max_items_per_line:
                hspice_data_file.write("\n" + param_name)
                item_counter = 0
            else:
                hspice_data_file.write(" " + param_name)
            item_counter += 1
        hspice_data_file.write("\n")
    
        # Add data for each elements in the lists.
        num_settings = len(parameter_dict[param_list[0]])
        for i in xrange(num_settings):
            item_counter = 0
            for param_name in param_list:
                if item_counter >= max_items_per_line:
                    hspice_data_file.write(str(parameter_dict[param_name][i]) + "\n")
                    item_counter = 0
                else:
                    hspice_data_file.write(str(parameter_dict[param_name][i]) + " ")
                item_counter += 1
            hspice_data_file.write ("\n")
    
        # Add the footer
        hspice_data_file.write(".ENDDATA")
    
        hspice_data_file.close()
    
        return
    

    def run(self, sp_path, parameter_dict):    
        """
        This function runs HSPICE on the .sp file at 'sp_path' and returns a dictionary that 
        contains the HSPICE measurements.

        'parameter_dict' is a dictionary that contains the sizes of transistors and wire RC. 
        It has the following format:
        parameter_dict = {param1_name: [val1, val2, etc...],
                          param2_name: [val1, val2, etc...],
                          etc...}

        You need to make sure that 'parameter_dict' has a key-value pair for each parameter
        in your HSPICE netlists. Otherwise, the simulation will fail because of missing 
        parameters. That is, only the parameters found in 'parameter_dict' will be given a
        value. 
        
        This is important when we consider the fact that, the 'value' in the key value 
        pair is a list of different parameter values that you want to run HSPICE on.
        The lists must be of the same length for all params in 'parameter_dict' (param1_name's
        list has the same number of elements as param2_name). Here's what is going to happen:
        We will start by setting all the parameters to their 'val1' and we'll run HSPICE. 
        Then, we'll set all the params to 'val2' and we'll run HSPICE. And so on (that's 
        actually not exactly what happens, but you get the idea). So, you can run HSPICE on 
        different transistor size conbinations by adding elements to these lists. Transistor 
        sizing combination i is ALL the vali in the parameter_dict. So, even if you never 
        want to change param1_name, you still need a list (who's elements will all be the 
        same in this case).
        If you only want to run HSPICE for one transistor sizing combination, your lists will
        only have one element (but it still needs to be a list).

        Ok, so 'parameter_dict' contains a key-value pair for each transistor where the 'value'
        is a list of transistor sizes to use. A transistor sizing combination consists of all 
        the elements at a particular index in these lists. You also need to provide a key-value
        (or key-list we could say) for all your wire RC parameters. The wire RC data in the 
        lists corresponds to each transistor sizing combination. You'll need to calculate what
        the wire RC is for a particular transistor sizing combination outside this function 
        though. Here, we'll only set the paramters to the appropriate values. 

        Finally, what we'll return is a dictionary similar to 'parameter_dict' but containing
        all of the of the SPICE measurements. The return value will have this format: 

        measurements = {meas_name1: [value1, value2, value3, etc...], 
                        meas_name2: [value1, value2, value3, etc...],
                        etc...}
        """

        sp_dir = os.path.dirname(sp_path)
        sp_filename = os.path.basename(sp_path)
  
        # Setup the .DATA sweep file with parameters in 'parameter_dict' 
        self._setup_data_sweep_file(parameter_dict)
 
        # Change working dir so that SPICE output files are created in circuit subdirectory
        saved_cwd = os.getcwd()
        os.chdir(sp_dir)
         
        # Run the SPICE simulation and capture output
        output_filename = sp_filename.rstrip(".sp") + ".lis"
        output_file = open(output_filename, "w")

        hspice_success = False
        hspice_runs = 0

        # there are many cases when then hspice similation will fail
        # most often, it is because the input file is incorrect (which would be a bug with in COFFE)
        # or hpice fails to checheck out the license, assuming the license exists, it is likely due
        # to many instances checking out the license at the same time. In this case, we check if the
        # ".mt0" exists, if not, we run hspice again. After we read the results, we delete it to make
        # sure we are not reading previous results
        while ( not hspice_success) :
            utils.check_for_time()
            subprocess.call(["hspice", sp_filename], stdout=output_file, stderr=output_file)
            output_file.close()
             
            # Read spice measurements
            mt0_path = output_filename.replace(".lis", ".mt0")
            # check that the ".mt0" file is there
            if os.path.isfile(mt0_path) :
                spice_measurements = self.parse_mt0(mt0_path)
                os.remove(mt0_path)
                hspice_success = True
            # something else is likely to be the problem
            else :
                hspice_runs = hspice_runs + 1
                if hspice_runs > 10 :
                    print "***hspice failed to run***"
                    exit(2)
  
        # Update simulation counter
        self.simulation_counter += len(parameter_dict.itervalues().next())

        # Return to saved cwd
        os.chdir(saved_cwd)
           
        return spice_measurements


    def parse_mt0(self, filepath):
        """
        Parse a HSPICE .mt0 file to collect measurements. 
        This function works on .mt0 files generated from single HSPICE runs,
        .sweep runs or .data runs. 
        
        Returns a dictionary that maps measurement names to a list of values.
        If this was a single HSPICE run, the list will only have one element.
        But, if this was a HSPICE sweep, the list will have multiple elements,
        one for each sweep setting. The same goes for .data sweeps.
    
        measurements = {meas_name1: [value1, value2, value3, etc...], 
                        meas_name2: [value1, value2, value3, etc...],
                        etc...}
        """
    
        # The measurements data structure is what we will be building.
        # It's a dictionary that maps measurement names to a list of values. 
        # If this was a simple HSPICE run, the list will only have one element. 
        # But, if this was a HSPICE sweep, the list will have multiple elements,
        # one for each sweep setting.
        # measurements = {meas_name1: [value1, value2, value3, etc...], 
        #                 meas_name2: [value1, value2, value3, etc...],
        #                 etc...}
        measurements = {}
        meas_names = []

        #parse should be changed for ram block
        meaz1_names = []
        meaz2_names = []
        meaz1counter = 0
        meaz2counter = 0

        #I'll need an aittional 4 to test carry chains:
        meaz3_names = []
        meaz4_names = []
        meaz5_names = []
        meaz6_names = []
        meaz3counter = 0
        meaz4counter = 0
        meaz5counter = 0
        meaz6counter = 0
    
        # Open the file for reading
        mt0_file = open(filepath, 'r')
    
        # The first thing we expect to find is the measurement names.
        # We use the 'parsing_names' flag to show that we are parsing the names.
        # Once we find 'alter#' we are done parsing the measurement names. 
        # Then, we start parsing the values themselves.
        parsing_names = True
        for line in mt0_file:
            # Ignore these lines
            if line.startswith("$"):
                continue
            if line.startswith("."):
                continue
    
            if parsing_names:
                words = line.split()
                for meas_name in words:
                    meas_names.append(meas_name)
                    measurements[meas_name] = []
                    if "meaz1" in meas_name:
                        meaz1counter += 1
                        meaz1_names.append(meas_name)
                    if "meaz2" in meas_name:
                        meaz2counter += 1
                        meaz2_names.append(meas_name)
                    if "meaz3" in meas_name:
                        meaz3counter += 1
                        meaz3_names.append(meas_name)
                    if "meaz4" in meas_name:
                        meaz4counter += 1
                        meaz4_names.append(meas_name)
                    if "meaz5" in meas_name:
                        meaz5counter += 1
                        meaz5_names.append(meas_name)
                    if "meaz6" in meas_name:
                        meaz6counter += 1
                        meaz6_names.append(meas_name)
                    # When we find 'alter#' we are done parsing measurement names.
                    if meas_name.startswith("alter#"):
                        num_measurements = len(meas_names)
                        current_meas = 0
                        parsing_names = False
            else:
                line = line.replace("\n", "")
                words = line.split()
                for meas in words:
                    # Append each measurement value to the right list.
                    # We use current_meas and meas_names to keep track of where we 
                    # need to add the measurement value.
                    measurements[meas_names[current_meas]].append(meas)
                    current_meas += 1
                    if current_meas == num_measurements:
                        current_meas = 0


        
        mt0_file.close()

        # This part is added to support having tow different fanins (e.g. ram rowdecoder)
        # If this happens to any other circuit, you should name the delays with mez1 and meaz2
        # the rest is simply the same.
        if meaz3counter != 0:
            for x in range(0,len(meaz1_names)):
                newname = meaz3_names[x].replace("meaz3_", "meas_")
                measurements[newname] = max(measurements[meaz1_names[x]],measurements[meaz2_names[x]],measurements[meaz3_names[x]])
            return measurements             
        if len(meaz1_names) !=0 and len(meaz2_names) != 0:
            if len(meaz1_names) != len(meaz2_names):
                    sys.exit(-1)
            for x in range(0,len(meaz1_names)):
                newname = meaz1_names[x].replace("meaz1_", "meas_")
                measurements[newname] = max(measurements[meaz1_names[x]],measurements[meaz2_names[x]])
        elif len(meaz1_names) !=0:
            for x in range(0,len(meaz1_names)):
                newname = meaz1_names[x].replace("meaz1_", "meas_")
                measurements[newname] = measurements[meaz1_names[x]]
        elif len(meaz2_names) !=0:
            for x in range(0,len(meaz2_names)):
                newname = meaz2_names[x].replace("meaz2_", "meas_")
                measurements[newname] = measurements[meaz2_names[x]]

        return measurements         
