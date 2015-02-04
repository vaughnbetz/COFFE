### COFFE: CIRCUIT OPTIMIZATION FOR FPGA EXPLORATION
# Created by: Charles Chiasson (charles.chiasson@gmail.com)
#         at: University of Toronto
#         in: 2013        
           
#
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
import shutil
import argparse
import time
import coffe.fpga as fpga
import coffe.spice as spice
import coffe.tran_sizing as tran_sizing
import coffe.utils
import coffe.vpr
import datetime

print "\nCOFFE 1.1\n"
print "Man is a tool-using animal."
print "Without tools he is nothing, with tools he is all."
print "                           - Thomas Carlyle\n\n"

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

args = parser.parse_args()
arch_description_filename = args.arch_description
is_size_transistors = not args.no_sizing
opt_type = args.opt_type
re_erf = args.re_erf
area_opt_weight = args.area_opt_weight
delay_opt_weight = args.delay_opt_weight
max_iterations = args.max_iterations
initial_sizes = args.initial_sizes

# Make the top-level spice folder if it doesn't already exist
arch_desc_words = arch_description_filename.split('.')
arch_folder = arch_desc_words[0]
if not os.path.exists(arch_folder):
    os.mkdir(arch_folder)
else:
    # Delete contents of sub-directories
    # COFFE generates several 'intermediate results' files during sizing
    # so we delete them to avoid from having them pile up if we run COFFE
    # more than once.
    dir_contents = os.listdir(arch_folder)
    for content in dir_contents:
        if os.path.isdir(arch_folder + "/" + content):
            shutil.rmtree(arch_folder + "/" + content)

# Print the options to both terminal and report file
report_file_path = os.path.join(arch_folder, "report.txt") 
report_file = open(report_file_path, 'w')
report_file.write("Created " + str(datetime.datetime.now()) + "\n\n")
print "RUN OPTIONS:"
report_file.write("RUN OPTIONS:\n")
if is_size_transistors:
    print "Transistor sizing: on"
    report_file.write("Transistor sizing: on\n")
else:
    print "Transistor sizing: off"
    report_file.write("Transistor sizing: off\n")
if opt_type == "global":
    print "Optimization type: global"
    report_file.write("Optimization type: global\n")
else:
    print "Optimization type: local"
    report_file.write("Optimization type: local\n")
print "Number of top combos to re-ERF: " + str(re_erf)
print "Area optimization weight: " + str(area_opt_weight)
print "Delay optimization weight: " + str(delay_opt_weight)
print "Maximum number of sizing iterations: " + str(max_iterations)
print ""
report_file.write("Number of top combos to re-ERF: " + str(re_erf) + "\n")
report_file.write("Area optimization weight: " + str(area_opt_weight) + "\n")
report_file.write("Delay optimization weight: " + str(delay_opt_weight) + "\n")
report_file.write("Maximum number of sizing iterations: " + str(max_iterations) + "\n")
report_file.write("\n")
report_file.close()

# Load the input architecture description file
arch_params_dict = coffe.utils.load_arch_params(arch_description_filename)

# Print architecture and process details to terminal and report file
coffe.utils.print_architecture_params(arch_params_dict, report_file_path)

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

use_tgate = False
use_finfet = False

if arch_params_dict['transistor_type'] == "finfet":
    use_finfet = True
if arch_params_dict['switch_type'] == "transmission_gate":
    use_tgate = True

# Default_dir is the dir you ran COFFE from. COFFE will be switching directories 
# while running HSPICE, this variable is so that we can get back to our starting point
default_dir = os.getcwd()


# Record start time
total_start_time = time.time()

# Create an FPGA instance
if not use_finfet :
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
                          rest_length_factor)
else :
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
                          rest_length_factor)



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
    initial_tran_size = coffe.utils.extract_initial_tran_size(initial_sizes, use_tgate)

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
# Create an HSPICE interface
spice_interface = spice.SpiceInterface()

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
    
# Update subcircuit delays (these are the final values)
fpga_inst.update_delays(spice_interface)

# Go back to the base directory
os.chdir(default_dir)

print "|------------------------------------------------------------------------------|"
print "|    Area and Delay Report                                                     |"
print "|------------------------------------------------------------------------------|"
print ""

# Print out final COFFE report to file
report_file = open(arch_folder + "/report.txt", 'a')
report_file.write("\n")
report_file.write("|------------------------------------------------------------------------------|\n")
report_file.write("|    Area and Delay Report                                                     |\n")
report_file.write("|------------------------------------------------------------------------------|\n")
report_file.write("\n")

# Print area and delay per subcircuit
coffe.utils.print_area_and_delay(report_file, fpga_inst)

# Print power per subcircuit
coffe.utils.print_power(report_file, fpga_inst)

# Print block areas
coffe.utils.print_block_area(report_file, fpga_inst)

# Print VPR delays (to be used to make architecture file)
coffe.utils.print_vpr_delays(report_file, fpga_inst)

# Print VPR areas (to be used to make architecture file)
coffe.utils.print_vpr_areas(report_file, fpga_inst)
      
# Print area and delay summary
final_cost = fpga_inst.area_dict["tile"]*fpga_inst.delay_dict["rep_crit_path"]
print "  SUMMARY"
print "  -------"
print "  Tile Area                            " + str(round(fpga_inst.area_dict["tile"]/1e6,2)) + " um^2"
print "  Representative Critical Path Delay   " + str(round(fpga_inst.delay_dict["rep_crit_path"]*1e12,2)) + " ps"
print ("  Cost (area^" + str(area_opt_weight) + " x delay^" + str(delay_opt_weight) + ")              " 
       + str(round(final_cost,5)))

print ""
print "|------------------------------------------------------------------------------|"
print ""

report_file.write("  SUMMARY\n")
report_file.write("  -------\n")
report_file.write("  Tile Area                            " + str(round(fpga_inst.area_dict["tile"]/1e6,2)) + " um^2\n")
report_file.write("  Representative Critical Path Delay   " + str(round(fpga_inst.delay_dict["rep_crit_path"]*1e12,2)) + " ps\n")
report_file.write("  Cost (area^" + str(area_opt_weight) + " x delay^" + str(delay_opt_weight) + ")              " 
       + str(round(final_cost,5)) + "\n")

report_file.write("\n")
report_file.write("|------------------------------------------------------------------------------|\n")
report_file.write("\n")

# Record end time
total_end_time = time.time()
total_time_elapsed = total_end_time - total_start_time
total_hours_elapsed = int(total_time_elapsed/3600)
total_minutes_elapsed = int((total_time_elapsed-3600*total_hours_elapsed)/60)
total_seconds_elapsed = int(total_time_elapsed - 3600*total_hours_elapsed - 60*total_minutes_elapsed)

print "Number of HSPICE simulations performed: " + str(spice_interface.get_num_simulations_performed())
print "Total time elapsed: " + str(total_hours_elapsed) + " hours " + str(total_minutes_elapsed) + " minutes " + str(total_seconds_elapsed) + " seconds\n" 

report_file.write( "Number of HSPICE simulations performed: " + str(spice_interface.get_num_simulations_performed()) + "\n")
report_file.write( "Total time elapsed: " + str(total_hours_elapsed) + " hours " + str(total_minutes_elapsed) + " minutes " + str(total_seconds_elapsed) + " seconds\n" )
report_file.write( "\n")

report_file.close()

vpr_file = open(arch_desc_words[0] + ".xml", 'w')
coffe.vpr.print_vpr_file(vpr_file, fpga_inst)
vpr_file.close()
