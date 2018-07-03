### COFFE: CIRCUIT OPTIMIZATION FOR FPGA EXPLORATION
# Created by: Charles Chiasson (charles.chiasson@gmail.com)
#         at: University of Toronto
#         in: 2013        
      
# BRAM simulation added by Sadegh Yazdanshenas in 2016
# MTJ and SRAM designs by Kosuke Tatsumura
# COFFE 2.0 by Sadegh Yazdanshenas 2015-2018     

# The big picture:
#
# COFFE will size the transistors of an FPGA based on some input architecture 
# parameters. COFFE will produce area and delay results that can be used to
# create VPR architecture files for architecture exploration. By changing how
# COFFE designs circuitry, one could also use COFFE to explore different FPGA
# circuit designs.
#
# How it works (in a nutshell):
#
# We start off by creating an 'FPGA' object with the input architecture parameters.
# This FPGA object contains other objects that each represent part of the FPGA
# circuitry (like switch block, LUT, etc.).
# We use the FPGA object to generate SPICE netlists of the circuitry
# We also use it to calculate area and wire loads
# 
# Once the FPGA object is created and the SPICE netlists are generated,
# we pass the FPGA object to COFFE's transistor sizing engine. The following paper 
# explains COFFE's transistor sizing algorithm in detail.
#
# [1] C. Chiasson and V. Betz, "COFFE: Fully-Automated Transistor Sizing for FPGAs", FPT2013
#
 

import os
import sys
#import shutil
import argparse
import time
import coffe.fpga as fpga
import coffe.spice as spice
import coffe.tran_sizing as tran_sizing
import coffe.utils as utils
import coffe.vpr
import datetime
import math

print "\nCOFFE 2.0\n"
print "Man is a tool-using animal."
print "Without tools he is nothing, with tools he is all."
print "                           - Thomas Carlyle\n\n"

# TODO: see the effect on disabling floorplanning on results and runtime
# if it is worth it we could add an argument which could disable 
# floorplanning for a quicker run

# Parse the input arguments with argparse
parser = argparse.ArgumentParser()
parser.add_argument('arch_description')
parser.add_argument('-n', '--no_sizing', help="don't perform transistor sizing", action='store_true')
parser.add_argument('-o', '--opt_type', type=str, choices=["global", "local"], default="global", help="choose optimization type")
parser.add_argument('-s', '--initial_sizes', type=str, default="default", help="path to initial transistor sizes")
parser.add_argument('-m', '--re_erf', type=int, default=1, help="choose how many sizing combos to re-erf")
parser.add_argument('-a', '--area_opt_weight', type=int, default=1, help="area optimization weight")
parser.add_argument('-d', '--delay_opt_weight', type=int, default=1, help="delay optimization weight")
parser.add_argument('-i', '--max_iterations', type=int, default=6, help="max FPGA sizing iterations")

# quick mode is disabled by default. Try passing -q 0.03 for 3% minimum improvement
parser.add_argument('-q', '--quick_mode', type=float, default=-1.0, help="minimum cost function improvement for resizing")


args = parser.parse_args()

#TODO: remove this and use the args object no need to replicate code
arch_description_filename = args.arch_description
is_size_transistors = not args.no_sizing
opt_type = args.opt_type
re_erf = args.re_erf
area_opt_weight = args.area_opt_weight
delay_opt_weight = args.delay_opt_weight
max_iterations = args.max_iterations
initial_sizes = args.initial_sizes
quick_mode_threshold = args.quick_mode


# Make the top-level spice folder if it doesn't already exist
# if it's already there delete its content
arch_folder = utils.create_output_dir(args.arch_description)

# Load the input architecture description file
arch_params_dict = utils.load_arch_params(arch_description_filename)

# Print the options to both terminal and report file
report_file_path = os.path.join(arch_folder, "report.txt") 
utils.print_run_options(args, report_file_path)

# Print architecture and process details to terminal and report file
utils.print_architecture_params(arch_params_dict, report_file_path)


# TODO: Remove this and pass the dictionary to the FPGA instance and 
# handel this there

# Create some local variables
N = arch_params_dict['N']
K = arch_params_dict['K']
W = arch_params_dict['W']
L = arch_params_dict['L']
I = arch_params_dict['I']
Fs = arch_params_dict['Fs']
Fcin = arch_params_dict['Fcin']
Fcout = arch_params_dict['Fcout']
Or = arch_params_dict['Or']
Ofb = arch_params_dict['Ofb']
Rsel = arch_params_dict['Rsel']
Rfb = arch_params_dict['Rfb']
Fclocal = arch_params_dict['Fclocal']
vdd = arch_params_dict['vdd']
vsram = arch_params_dict['vsram']
vsram_n = arch_params_dict['vsram_n']
gate_length = arch_params_dict['gate_length']
rest_length_factor = arch_params_dict['rest_length_factor']
min_tran_width = arch_params_dict['min_tran_width']
min_width_tran_area = arch_params_dict['min_width_tran_area']
sram_cell_area = arch_params_dict['sram_cell_area']
trans_diffusion_length = arch_params_dict['trans_diffusion_length']
model_path = arch_params_dict['model_path']
model_library = arch_params_dict['model_library']
metal_stack = arch_params_dict['metal']
row_decoder_bits = arch_params_dict['row_decoder_bits']
col_decoder_bits = arch_params_dict['col_decoder_bits']
conf_decoder_bits = arch_params_dict['conf_decoder_bits']
sense_dv = arch_params_dict['sense_dv']
worst_read_current = arch_params_dict['worst_read_current']

vdd_low_power = arch_params_dict['vdd_low_power']
number_of_banks = arch_params_dict['number_of_banks']
memory_technology = arch_params_dict['memory_technology']
SRAM_nominal_current = arch_params_dict['SRAM_nominal_current']
MTJ_Rlow_nominal = arch_params_dict['MTJ_Rlow_nominal']
MTJ_Rhigh_nominal = arch_params_dict['MTJ_Rhigh_nominal']
MTJ_Rlow_worstcase = arch_params_dict['MTJ_Rlow_worstcase']
MTJ_Rhigh_worstcase = arch_params_dict['MTJ_Rhigh_worstcase']

vref = arch_params_dict['vref']
vclmp = arch_params_dict['vclmp']
enable_bram_module = arch_params_dict['enable_bram_module']
read_to_write_ratio = arch_params_dict['read_to_write_ratio']
ram_local_mux_size = arch_params_dict['ram_local_mux_size']
use_tgate = False
use_finfet = False
use_fluts = False
independent_inputs = arch_params_dict['independent_inputs']
use_fluts = arch_params_dict['use_fluts']

enable_carry_chain = arch_params_dict['enable_carry_chain']
carry_chain_type = arch_params_dict['carry_chain_type']
FAs_per_flut = arch_params_dict['FAs_per_flut']

hb_files = arch_params_dict['hb_files']

if arch_params_dict['transistor_type'] == "finfet":
    use_finfet = True
    if enable_bram_module == 1:
      print "finfet and BRAM simulations are not compatible"
      sys.exit()
if arch_params_dict['switch_type'] == "transmission_gate":
    use_tgate = True

# Default_dir is the dir you ran COFFE from. COFFE will be switching directories 
# while running HSPICE, this variable is so that we can get back to our starting point
default_dir = os.getcwd()

# Create an HSPICE interface
spice_interface = spice.SpiceInterface()


# Record start time
total_start_time = time.time()

# Create an FPGA instance
fpga_inst = fpga.FPGA(N, K, W, L, I, Fs, Fcin, Fcout, Fclocal, Or, Ofb, Rsel, Rfb,
                      vdd, vsram, vsram_n, 
                      gate_length, 
                      min_tran_width, 
                      min_width_tran_area, 
                      sram_cell_area,
                      trans_diffusion_length,
                      model_path, 
                      model_library, 
                      metal_stack,
                      use_tgate,
                      use_finfet,
                      rest_length_factor, row_decoder_bits, col_decoder_bits, conf_decoder_bits, sense_dv, worst_read_current, vdd_low_power, vref, number_of_banks,
                      memory_technology, SRAM_nominal_current, MTJ_Rlow_nominal, MTJ_Rhigh_nominal, MTJ_Rlow_worstcase, MTJ_Rhigh_worstcase, vclmp, 
                      read_to_write_ratio, enable_bram_module, ram_local_mux_size, quick_mode_threshold, use_fluts, independent_inputs, enable_carry_chain, carry_chain_type, FAs_per_flut,
                      hb_files, area_opt_weight, delay_opt_weight,
                      spice_interface)

###############################################################
## GENERATE FILES
###############################################################


# Change to the architecture directory
os.chdir(arch_folder)  

# Generate FPGA and associated SPICE files
fpga_inst.generate(is_size_transistors) 

# Go back to the base directory
os.chdir(default_dir)

# Extract initial transistor sizes from file if this option was used.
if initial_sizes != "default" :
    print "Extracting initial transistor sizes from: " + initial_sizes
    initial_tran_size = utils.extract_initial_tran_size(initial_sizes, use_tgate)

# over writes default initial sizes if initial sizes are specified
if initial_sizes != "default" :
    print "Setting transistor sizes to extracted values"
    tran_sizing.override_transistor_sizes(fpga_inst, initial_tran_size)
    for tran in initial_tran_size :
        fpga_inst.transistor_sizes[tran] = initial_tran_size[tran]
    
    print "Re-calculating area..."
    fpga_inst.update_area()
    print "Re-calculating wire lengths..."
    fpga_inst.update_wires()
    print "Re-calculating resistance and capacitance..."
    fpga_inst.update_wire_rc()
    print ""

# Print FPGA implementation details
report_file = open(report_file_path, 'a')
fpga_inst.print_details(report_file)  
report_file.close()


# Go to architecture directory
os.chdir(arch_folder)

###############################################################
## TRANSISTOR SIZING
###############################################################


sys.stdout.flush()
# Size FPGA transistors
if is_size_transistors:
    tran_sizing.size_fpga_transistors(fpga_inst, 
                                      opt_type, 
                                      re_erf, 
                                      max_iterations, 
                                      area_opt_weight, 
                                      delay_opt_weight, 
                                      spice_interface)    
else:
  # in case of disabeling floorplanning there is no need to 
  # update delays before updating area. Tried both ways and 
  # they give exactly the same results
  #fpga_inst.update_delays(spice_interface)

  # same thing here no need to update area before calculating 
  # the lb_height value. Also tested and gave same results
  #fpga_inst.update_area()
  fpga_inst.lb_height = math.sqrt(fpga_inst.area_dict["tile"])
  fpga_inst.update_area()
  fpga_inst.compute_distance()
  fpga_inst.update_wires()
  fpga_inst.update_wire_rc()

  # commented this part to avoid doing floorplannig for
  # a non-sizing run
  #fpga_inst.determine_height()

  fpga_inst.update_delays(spice_interface)

# Obtain Memory core power
if enable_bram_module == 1:
  fpga_inst.update_power(spice_interface)


#print str(fpga_inst.dict_real_widths["sb_sram"])
#print str(fpga_inst.dict_real_widths["sb"])
#print str(fpga_inst.dict_real_widths["cb_sram"])
#print str(fpga_inst.dict_real_widths["cb"])
#print str(fpga_inst.dict_real_widths["ic_sram"])
#print str(fpga_inst.dict_real_widths["ic"])
#print str(fpga_inst.dict_real_widths["lut_sram"])
#print str(fpga_inst.dict_real_widths["lut"])
#print str(fpga_inst.dict_real_widths["cc"])
#print str(fpga_inst.dict_real_widths["ffble"])
#print str(fpga_inst.lb_height)


# Go back to the base directory
os.chdir(default_dir)


# Print out final COFFE report to file
utils.print_summary(arch_folder, fpga_inst, total_start_time)



vpr_file = open(arch_folder + ".xml", 'w')

if enable_bram_module == 1:
  coffe.vpr.print_vpr_file_memory(vpr_file, fpga_inst)
else:
  coffe.vpr.print_vpr_file_flut_hard(vpr_file, fpga_inst)

vpr_file.close()
